#!/usr/bin/env python3
"""Inspect publishing protections. --apply activates the reviewed configuration."""
import argparse
import json
import subprocess


def rules():
    def rule(name, branch, extra):
        return {'name': name, 'target': 'branch', 'enforcement': 'active', 'bypass_actors': [],
                'conditions': {'ref_name': {'include': ['refs/heads/' + branch], 'exclude': []}},
                'rules': [{'type': 'non_fast_forward'}, {'type': 'deletion'}, *extra]}
    main = rule('SaxoBrain main safety', 'main', [])
    return [main]


def contains(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and contains(actual[k], v) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(any(contains(item, value) for item in actual) for value in expected)
    return actual == expected


def settings_errors(current_rules, policies):
    errors = []
    for expected in rules():
        actual = next((r for r in current_rules if r.get('name') == expected['name']), None)
        if not actual or not contains(actual, expected):
            errors.append('Missing or incorrect ruleset: ' + expected['name'])
    if not contains(policies, [{'name': 'main', 'type': 'branch'}]):
        errors.append('The normal Pages environment must allow only main')
    return errors


def api(repo, path, method='GET', payload=None):
    command = ['gh', 'api', 'repos/' + repo + '/' + path, '--method', method]
    if payload is not None:
        command.extend(['--input', '-'])
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def inspect(repo):
    summaries = api(repo, 'rulesets')
    current = [api(repo, f'rulesets/{r["id"]}') for r in summaries]
    env = api(repo, 'environments/github-pages')
    policies = api(repo, 'environments/github-pages/deployment-branch-policies')['branch_policies']
    errors = settings_errors(current, policies)
    if env.get('deployment_branch_policy') != {'protected_branches': False, 'custom_branch_policies': True}:
        errors.append('Pages must use explicit custom deployment branch policies')
    return current, env, policies, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', default='timrosenberg/SaxoBrain')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--implementation-pr', type=int, help='Reviewed and merged implementation PR required for activation')
    args = parser.parse_args()
    current, env, policies, errors = inspect(args.repo)
    if args.apply:
        if not args.implementation_pr:
            raise ValueError('--apply requires --implementation-pr with the reviewed PR number')
        pr = api(args.repo, 'pulls/' + str(args.implementation_pr))
        if not pr.get('merged') or pr.get('base', {}).get('ref') != 'main' or pr.get('merged_by', {}).get('login') != 'timrosenberg':
            raise ValueError('Tim must merge the reviewed implementation into main')
        comparison = api(args.repo, 'compare/' + pr['merge_commit_sha'] + '...main')
        if comparison['status'] not in {'ahead', 'identical'}:
            raise ValueError('Implementation must be in current main history')
        runs = api(args.repo, 'actions/workflows/publish.yml/runs?event=pull_request&head_sha=' + pr['head']['sha'])['workflow_runs']
        if not any(r['conclusion'] == 'success' for r in runs):
            raise ValueError('Implementation PR validation must pass before activation')
        if any(r['type'] != 'branch_policy' for r in env.get('protection_rules', [])):
            raise ValueError('Existing environment protections require manual review before modification')
        if len(policies) != 1 or policies[0].get('name') != 'main':
            raise ValueError('Unexpected environment branch policies; inspect before changing them')
        for expected in rules():
            existing = next((r for r in current if r.get('name') == expected['name']), None)
            path = 'rulesets' + ('/' + str(existing['id']) if existing else '')
            api(args.repo, path, 'PUT' if existing else 'POST', expected)
        api(args.repo, 'environments/github-pages', 'PUT', {'deployment_branch_policy': {'protected_branches': False, 'custom_branch_policies': True}})
        _, _, _, errors = inspect(args.repo)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('Publishing protections verified. Direct content pushes to main remain allowed.')


if __name__ == '__main__':
    main()
