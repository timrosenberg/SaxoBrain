#!/usr/bin/env python3
"""Verify the deployed revision and representative files match the tested artifact."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen


def fetch(base_url, path, revision):
    url = urljoin(base_url.rstrip('/') + '/', quote(path, safe='/'))
    request = Request(url + '?saxobrain_release=' + revision, headers={'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=20) as response:
        return response.read()


def sample_files(root):
    files = ['index.html', 'index.json', 'addresses.txt', 'composers/index.html',
             'recordings/index.html', 'curriculum/index.html', 'css/site.css']
    files.extend(str(p.relative_to(root)) for p in sorted((root / 'js').glob('*.js')))
    for section in ['works', 'composers', 'recordings']:
        sample = next(iter(sorted((root / section).glob('*/index.html'))), None)
        if sample:
            files.append(str(sample.relative_to(root)))
    return files


def smoke(base_url, artifact, revision, files=None):
    artifact = Path(artifact)
    errors = []
    try:
        live = json.loads(fetch(base_url, 'release.json', revision))
        if live.get('revision') != revision:
            return ['Production revision does not match the tested commit']
    except (URLError, ValueError, OSError) as exc:
        return [f'Production release marker unavailable: {exc}']
    for path in sample_files(artifact) if files is None else files:
        try:
            expected = (artifact / path).read_bytes()
            actual = fetch(base_url, path, revision)
            if hashlib.sha256(actual).digest() != hashlib.sha256(expected).digest():
                errors.append(f'Production differs from tested artifact: {path}')
        except (URLError, OSError) as exc:
            errors.append(f'Production check failed for {path}: {exc}')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('base_url')
    parser.add_argument('artifact', type=Path)
    parser.add_argument('revision')
    parser.add_argument('--attempts', type=int, default=6)
    args = parser.parse_args()
    for attempt in range(args.attempts):
        errors = smoke(args.base_url, args.artifact, args.revision)
        if not errors:
            print(f'Production smoke checks passed for {args.revision}.')
            break
        print('\n'.join(errors), flush=True)
        if attempt + 1 == args.attempts:
            raise SystemExit(1)
        time.sleep(10)
