#!/usr/bin/env python3
"""Validate the editable vault without contacting outside services."""
import argparse
import datetime
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml


class UniqueLoader(yaml.CSafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError('property names must be strings')
        if key in result:
            raise ValueError('duplicate key: ' + key)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
FRONTMATTER = re.compile(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', re.S)
WIKI = re.compile(r'\[\[([^\]]+)\]\]')
LEVELS = {'Pre-college', 'First Year', 'Second Year', 'Third Year', 'Fourth Year', 'Advanced'}
COMMON = {'title', 'slug', 'aliases', 'notion-id', 'third-party', 'third-party-files',
          'pdf-viewer', 'embed-youtube', 'image-viewer', 'list-children', 'original-url',
          'wayback-url'}
FIELDS = {
    'works': COMMON | set('composer instruments composed year-of-study streaming purchase want-to-play added publisher research arranger-edition duration multi-instruments library-recording studied-performed tags download library-score website'.split()),
    'composers': COMMON | set('nationality gender race born died wikidata photo photo-source website photo-credit sort-name pronouns'.split()),
    'recordings': COMMON | set('saxophonists works streaming youtube spotify apple-music amazon-music tidal tracks year-released cover publisher out-of-print soundcloud'.split()),
}
BOOLS = {'third-party', 'third-party-files', 'pdf-viewer', 'embed-youtube', 'image-viewer',
         'list-children', 'want-to-play', 'studied-performed', 'out-of-print'}
LISTS = {'aliases', 'composer', 'instruments', 'nationality', 'race', 'works', 'tracks',
         'tags', 'research', 'purchase', 'download', 'library-score', 'library-recording'}
TEXT = {'title', 'slug', 'year-of-study', 'gender', 'wikidata', 'photo', 'photo-source',
        'website', 'cover', 'saxophonists', 'multi-instruments', 'sort-name', 'pronouns'}
LINKS = {'purchase', 'download', 'library-score', 'library-recording', 'streaming', 'website',
         'youtube', 'spotify', 'apple-music', 'amazon-music', 'tidal', 'soundcloud', 'photo',
         'cover', 'original-url', 'wayback-url'}


def read_note(path):
    text = path.read_text(encoding='utf-8')
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError('expected YAML frontmatter between --- lines')
    fields = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(fields, dict):
        raise ValueError('frontmatter must be a property mapping')
    return fields, text[match.end():]


def page_key(name):
    return name.replace('’', "'").replace('‘', "'").replace('\xa0', ' ').casefold()


def site_text(root):
    values, errors = {}, []
    for path in sorted((root / 'content/Site Text').glob('*.md')):
        active = False
        for row in path.read_text(encoding='utf-8').splitlines():
            row = row.strip()
            if re.fullmatch(r'\|?\s*Setting\s*\|\s*Text\s*\|?', row):
                active = True
                continue
            if not row:
                active = False
            if not active or re.fullmatch(r'\|?\s*:?-+:?\s*\|\s*:?-+:?\s*\|?', row):
                continue
            match = re.fullmatch(r'\|?\s*([a-z][a-z0-9-]*)\s*\|\s*((?:\\\||[^|])*)\|?', row)
            if not match or not match[2].strip():
                errors.append(f'{path.relative_to(root)}: invalid Site Text row: {row}')
                continue
            key, value = match[1], match[2].strip()
            if key in values:
                errors.append(f'{path.relative_to(root)}: duplicate Site Text setting {key}')
            values[key] = value
    return values, errors


def placeholders(value):
    return sorted(re.findall(r'\{[a-z][a-z0-9-]*\}', value))


def link_error(root, value, field):
    url = re.split(r'\s+·\s+', value.strip())[-1]
    try:
        parts = urlsplit(url)
        if any(c.isspace() for c in url) or any(ord(c) < 32 for c in url):
            return 'invalid link'
        if parts.scheme in {'http', 'https'} and parts.hostname:
            return None
        if parts.scheme == 'mailto' and field == 'purchase' and '@' in parts.path:
            return None
        # Historical Notion attachments remain metadata until a separate cleanup.
        if parts.scheme == 'attachment' and field == 'download':
            return None
        if url.startswith('/media/'):
            asset = (root / 'static' / unquote(parts.path).lstrip('/')).resolve()
            if not asset.is_relative_to((root / 'static/media').resolve()):
                return 'invalid local asset path'
            return None if asset.is_file() else 'missing local asset'
    except ValueError:
        pass
    return 'invalid link'


def validate(root, baseline=None):
    root = Path(root).resolve()
    errors, notes, pages = [], {}, {}
    for path in sorted((root / 'content').rglob('*.md')):
        name = str(path.relative_to(root))
        if path.is_symlink():
            errors.append(f'{name}: symbolic links are not allowed')
            continue
        try:
            data, body = read_note(path)
        except (ValueError, yaml.YAMLError) as exc:
            errors.append(f'{name}: YAML: {exc}')
            continue
        notes[path] = (data, body)
        if path.stem != '_index':
            key = page_key(path.stem)
            if key in pages:
                errors.append(f'{name}: ambiguous page name also used by {pages[key]}')
            pages[key] = name
        section = path.relative_to(root / 'content').parts[0]
        for field in ['title'] + (['slug'] if section in FIELDS and path.stem != '_index' else []):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f'{name}: {field}: expected nonempty text')
        if section in FIELDS and path.stem != '_index':
            for field in data.keys() - FIELDS[section]:
                errors.append(f'{name}: {field}: unsupported property; schema changes require a structural PR')
        if section == 'works' and path.stem != '_index':
            for field in ['composer', 'instruments']:
                value = data.get(field)
                if not isinstance(value, list) or (field == 'instruments' and not value):
                    errors.append(f'{name}: {field}: expected a nonempty list')
        for field, value in data.items():
            if value is None or value == '':
                continue
            if field in {'composed', 'born', 'died', 'year'} and type(value) is not int:
                errors.append(f'{name}: {field}: expected an integer or an empty value')
            if field in BOOLS and type(value) is not bool:
                errors.append(f'{name}: {field}: expected true or false')
            if field in LISTS and (not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value)):
                errors.append(f'{name}: {field}: expected a list of nonempty text values')
            if field in TEXT and not isinstance(value, str):
                errors.append(f'{name}: {field}: expected text')
            if field == 'year-of-study' and isinstance(value, str) and value not in LEVELS:
                errors.append(f'{name}: {field}: unrecognized value {value!r}')
            if field in {'publisher', 'arranger-edition', 'streaming'} and not isinstance(value, (str, list)):
                errors.append(f'{name}: {field}: expected text or a list')
            if field == 'duration' and (type(value) not in {str, int, float}):
                errors.append(f'{name}: duration: expected text or a number')
            if field == 'added':
                try:
                    datetime.date.fromisoformat(str(value))
                except ValueError:
                    errors.append(f'{name}: added: expected YYYY-MM-DD')
            if field == 'aliases' and isinstance(value, list):
                for alias in value:
                    if not isinstance(alias, str) or not alias.startswith('/') or alias.startswith('//') or any(c in alias for c in '?#'):
                        errors.append(f'{name}: aliases: expected absolute site paths')
            if field in LINKS:
                for entry in value if isinstance(value, list) else [value]:
                    problem = link_error(root, entry, field) if isinstance(entry, str) else 'invalid link'
                    if problem:
                        errors.append(f'{name}: {field}: {problem}: {entry}')
    for path, (data, body) in notes.items():
        name = str(path.relative_to(root))
        for field, section in [('composer', 'composers'), ('works', 'works')]:
            entries = data.get(field) or []
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, str):
                    continue
                match = WIKI.fullmatch(entry)
                target = page_key(match[1].split('|')[0]) if match else ''
                actual = pages.get(target, '')
                if not actual.startswith(f'content/{section}/'):
                    errors.append(f'{name}: {field}: unresolved {"composer" if field == "composer" else "work"} {entry}')
    values, table_errors = site_text(root)
    errors.extend(table_errors)
    if baseline:
        previous, previous_errors = site_text(Path(baseline))
        errors.extend(previous_errors)
        for key, value in previous.items():
            if key not in values:
                errors.append(f'Site Text: missing setting {key}')
            elif placeholders(value) != placeholders(values[key]):
                errors.append(f'Site Text: {key}: placeholders changed')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    problems = validate(args.root, args.baseline)
    if problems:
        print('\n'.join(problems))
        raise SystemExit(1)
    print('Content validation passed.')
