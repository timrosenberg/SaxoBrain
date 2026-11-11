#!/usr/bin/env python3
"""Content/structure checks for the normal publishing path on main."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.request import Request, urlopen

from validate_content import COMMON, FIELDS, FRONTMATTER, UniqueLoader, placeholders
import yaml

PUBLISHER = '.github/workflows/publish.yml'
CHECK = 'Validate site'
ATTESTATIONS = ('Worktree:', 'Automated checks', 'Rendered checks', 'Acceptance criteria')
ISSUE_REF = re.compile(r'(?im)\b(?:closes?|fix(?:es)?|resolves?|issue)\s*:?\s*#(\d+)')
MEDIA = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif', '.pdf', '.mp3', '.m4a', '.wav', '.ogg', '.ico'}
EDITORIAL = COMMON | set('year equipment-title equipment-format equipment-table-anchors equipment-fragment-aliases equipment-parent display-title list-in-parent'.split())
PROTECTED_PROPERTIES = {'build', '_build', 'cascade', 'type', 'layout', 'outputs', 'url', 'headless', 'markup', 'render', 'draft'}


def git(root, *args, binary=False):
    return subprocess.check_output(['git', '-C', str(root), *args], text=not binary)


def note_at(root, ref, path):
    found = git(root, 'ls-tree', ref, '--', path)
    if not found:
        return None
    if not found.startswith('100644 ') and not found.startswith('100755 '):
        raise ValueError('symlink or unsupported file mode')
    return git(root, 'show', f'{ref}:{path}')


def properties(text):
    if text is None:
        return {}
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError('missing frontmatter')
    result = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(result, dict):
        raise ValueError('invalid properties')
    return result


def text_contract(text):
    result = {}
    for line in (text or '').splitlines():
        match = re.fullmatch(r'\|?\s*([a-z][a-z0-9-]*)\s*\|\s*((?:\\\||[^|])*)\|?', line.strip())
        if match:
            result[match[1]] = placeholders(match[2])
    return result


def previous_valid_note(root, ref, path):
    for commit in git(root, 'rev-list', '--first-parent', ref, '--', path).splitlines():
        text = note_at(root, commit, path)
        try:
            properties(text)
            return text
        except (ValueError, yaml.YAMLError):
            continue
    return None


def structural_changes(root, base, head):
    paths = git(root, 'diff', '--name-only', '-z', '--no-renames', base, head).split('\0')
    structural = []
    for name in filter(None, paths):
        path = Path(name)
        try:
            # Check mode even for content media and vault files.
            tree = git(root, 'ls-tree', head, '--', name)
            if tree and not tree.startswith(('100644 ', '100755 ')):
                raise ValueError('unsupported mode')
            if name.startswith('static/media/') and path.suffix.lower() in MEDIA:
                continue
            if name.startswith('📁 project-reference/') and path.suffix == '.md':
                continue
            if name.startswith('content/') and path.suffix == '.base':
                continue
            if not name.startswith('content/') or path.suffix != '.md' or any(p.startswith('.') for p in path.parts):
                raise ValueError('structural path')
            old, new = note_at(root, base, name), note_at(root, head, name)
            try:
                before = properties(old)
            except (ValueError, yaml.YAMLError):
                old = previous_valid_note(root, base, name)
                before = properties(old)
            try:
                after = properties(new)
            except (ValueError, yaml.YAMLError):
                # Invalid note syntax cannot pass data validation or publish.
                # A correction is compared with the nearest valid contract.
                continue
            for key in PROTECTED_PROPERTIES:
                if before.get(key) != after.get(key):
                    raise ValueError('rendering contract changed')
            section = path.parts[1]
            permitted = FIELDS.get(section, EDITORIAL)
            changed_keys = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
            if changed_keys - permitted:
                raise ValueError('metadata contract changed')
            if section == 'Site Text' and text_contract(old) != text_contract(new):
                raise ValueError('Site Text contract changed')
            if section == 'curriculum' and re.findall(r'\]\(#[^)]+\)', old or '') != re.findall(r'\]\(#[^)]+\)', new or ''):
                raise ValueError('curriculum navigation changed')
            for key in ('equipment-table-anchors', 'equipment-fragment-aliases', 'equipment-parent'):
                if before.get(key) != after.get(key):
                    raise ValueError('equipment structure changed')
        except (ValueError, yaml.YAMLError):
            structural.append(name)
    return structural


def verify_history(root, baseline, head, review, recovery_claims=None):
    try:
        subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', baseline, head],
                       check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        raise ValueError('Trusted release baseline is not an ancestor of this revision') from exc
    problems = []
    commits = git(root, 'rev-list', '--first-parent', '--reverse', f'{baseline}..{head}').splitlines()
    for index, commit in enumerate(commits):
        parent = git(root, 'rev-parse', commit + '^').strip()
        changes = structural_changes(root, parent, commit)
        if changes:
            errors = review(commit)
            if errors and recovery_claims:
                for later in commits[index + 1:]:
                    if commit in recovery_claims(later) and not review(later):
                        errors = []
                        break
            problems.extend(f'{commit[:12]}: {error} ({", ".join(changes)})' for error in errors)
    return problems


def review_errors(pr, issue, merged):
    errors = []
    body = pr.get('body') or ''
    if pr.get('base', {}).get('ref') != 'main':
        errors.append('Structural PR must target main')
    if merged and (not pr.get('merged') or pr.get('merged_by', {}).get('login') != 'timrosenberg'):
        errors.append('Tim must merge the structural PR after accepting it')
    for label in ATTESTATIONS:
        if not re.search(r'(?im)^\s*- \[x\]\s+' + re.escape(label) + r'\S*', body):
            errors.append(f'Structural PR needs completed attestation: {label}')
    if not re.search(r'(?im)^\s*- \[x\]\s+Worktree:\s+\S+', body):
        errors.append('Record the isolated worktree path')
    issue_body = (issue or {}).get('body') or ''
    if not ISSUE_REF.search(body) or not issue or issue.get('pull_request'):
        errors.append('Link a complete structural issue with Closes #N or Issue: #N')
    elif len(issue_body.strip()) < 500 or any(word not in issue_body.casefold() for word in ['scope', 'acceptance', 'verif', 'rollback', 'approach']):
        errors.append('Issue needs problem, scope, approach, acceptance, verification and rollback details')
    return errors


def healthy_baseline(runs, bootstrap):
    for run in runs:
        match = re.fullmatch(r'Publish ([a-f0-9]{40})', run.get('display_title', ''))
        if (match and run.get('event') in {'push', 'workflow_dispatch'} and run.get('head_branch') == 'main'
                and run.get('head_sha') == match[1] and run.get('conclusion') == 'success'
                and run.get('path') == PUBLISHER):
            return match[1]
    if not re.fullmatch('[a-f0-9]{40}', bootstrap):
        raise ValueError('Missing trusted bootstrap revision')
    return bootstrap


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('Invalid repository')
        self.repository = repository

    def get(self, path):
        request = Request('https://api.github.com/repos/' + self.repository + '/' + path,
                          headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                                   'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    def list(self, path, key=None):
        result = []
        for page in range(1, 101):
            data = self.get(path + ('&' if '?' in path else '?') + f'per_page=100&page={page}')
            rows = data[key] if key else data
            result.extend(rows)
            if len(rows) < 100:
                return result
        raise ValueError('Too many API pages; refusing an incomplete policy check')

    def review(self, number, merged=False):
        pr = self.get(f'pulls/{number}')
        match = ISSUE_REF.search(pr.get('body') or '')
        issue = self.get('issues/' + match[1]) if match else None
        errors = review_errors(pr, issue, merged)
        if merged:
            runs = self.list('actions/workflows/publish.yml/runs?event=pull_request&head_sha=' + pr['head']['sha'], 'workflow_runs')
            if not any(r.get('conclusion') == 'success' and r.get('path') == PUBLISHER for r in runs):
                errors.append('Structural PR needs a successful validation workflow for its final head')
        return errors

    def reviewed_commit(self, commit):
        candidates = self.list(f'commits/{commit}/pulls')
        for pr in candidates:
            if pr.get('merge_commit_sha') == commit and pr.get('base', {}).get('ref') == 'main':
                return self.review(pr['number'], merged=True)
        return ['Structural change has no merged main PR']

    def recovery_claims(self, commit):
        for pr in self.list(f'commits/{commit}/pulls'):
            if pr.get('merge_commit_sha') == commit and pr.get('base', {}).get('ref') == 'main':
                body = self.get(f'pulls/{pr["number"]}').get('body') or ''
                lines = re.findall(r'(?im)^Reviewed prior commits:\s*([^\n]+)', body)
                return re.findall(r'\b[a-f0-9]{40}\b', ' '.join(lines))
        return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--head', required=True)
    parser.add_argument('--base')
    parser.add_argument('--pr', type=int)
    parser.add_argument('--repository', default='timrosenberg/SaxoBrain')
    parser.add_argument('--bootstrap', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--baseline-only', action='store_true')
    args = parser.parse_args()
    api = GitHub(args.repository)
    if not re.fullmatch('[a-f0-9]{40}', args.head):
        raise ValueError('Expected a full commit SHA')
    if args.pr and not args.baseline_only:
        problems = api.review(args.pr) if structural_changes(args.root, args.base, args.head) else []
    else:
        bootstrap = json.loads(args.bootstrap.read_text())['sha']
        baseline = healthy_baseline(api.list('actions/workflows/publish.yml/runs?branch=main&status=success', 'workflow_runs'), bootstrap)
        if args.output:
            args.output.write_text(baseline + '\n')
        if args.baseline_only:
            print('Healthy baseline: ' + baseline)
            return
        if os.environ.get('GITHUB_REF') != 'refs/heads/main' or os.environ.get('GITHUB_EVENT_NAME') not in {'push', 'workflow_dispatch'}:
            raise ValueError('Production requires a push or dispatch on main')
        if api.get('branches/main')['commit']['sha'] != args.head:
            raise ValueError('Only the current main revision can publish; request a new run')
        problems = verify_history(args.root, baseline, args.head, api.reviewed_commit, api.recovery_claims)
    if problems:
        print('\n'.join(problems))
        raise SystemExit(1)
    print('Publishing policy passed.')


if __name__ == '__main__':
    main()
