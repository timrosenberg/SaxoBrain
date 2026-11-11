#!/usr/bin/env python3
"""Build and validate a revision before creating a deployable artifact."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from validate_content import validate
from validate_site import validate_site


def run(command, cwd=None):
    print('+ ' + ' '.join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)


def require_fresh_output(path):
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise ValueError(f'Use a fresh output directory; existing files were preserved: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--allow-contract-changes', action='store_true')
    parser.add_argument('--live-addresses', action='append', default=[])
    args = parser.parse_args()
    source, baseline, output = (p.resolve() for p in [args.source, args.baseline, args.output])
    if not re.fullmatch('[a-f0-9]{40}', args.revision):
        raise ValueError('Revision must be a full commit SHA')
    previous = output.parent / (output.name + '-baseline')
    require_fresh_output(output)
    require_fresh_output(previous)
    errors = validate(source, None if args.allow_contract_changes else baseline)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts/tests', '-p', 'test_*.py'], source)
    run(['hugo', '--source', baseline, '--minify', '--baseURL', args.base_url, '--destination', previous])
    if not (previous / 'addresses.txt').is_file():
        raise ValueError('Baseline build produced no addresses.txt')
    run(['hugo', '--source', source, '--minify', '--baseURL', args.base_url, '--destination', output])
    run([sys.executable, source / 'scripts/check_addresses.py', output / 'addresses.txt', args.base_url,
         (previous / 'addresses.txt').as_uri(), *args.live_addresses])
    errors = validate_site(output, args.base_url)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    (output / 'release.json').write_text(json.dumps({'revision': args.revision}) + '\n')
    print('All publishing checks passed for ' + args.revision)


if __name__ == '__main__':
    main()
