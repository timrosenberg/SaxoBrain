#!/usr/bin/env python3
"""Check generated internal links, local assets and private-content exclusions."""
import argparse
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and key in {'href', 'src', 'poster', 'data-pdf-url'}:
                self.links.append(value)


def validate_site(root, base_url):
    root = Path(root).resolve()
    base = urlsplit(base_url)
    prefix = base.path.rstrip('/')
    problems = []
    if not (root / 'index.html').is_file():
        return ['Missing rendered index.html; refusing an empty artifact']
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if any(p in {'project-reference', '📁 project-reference', '.obsidian'} for p in path.relative_to(root).parts) or path.suffix == '.base':
            problems.append(f'{relative}: private vault file in public output')
        if path.suffix != '.html':
            continue
        html = path.read_text(encoding='utf-8')
        if re.search(r'!\[\[[^\]]+\.base(?:[|#][^\]]*)?\]\]', unescape(html)):
            problems.append(f'{relative}: vault-only Base embed leaked')
        if 'research-notes-private' in html:
            problems.append(f'{relative}: private research section leaked')
        parser = References()
        parser.feed(html)
        page_url = urljoin(base_url, relative[:-10] if relative.endswith('index.html') else relative)
        for link in parser.links:
            if link.startswith(('#', 'mailto:', 'tel:', 'data:', 'blob:')):
                continue
            target = urlsplit(urljoin(page_url, link))
            if target.scheme not in {'http', 'https'} or target.netloc != base.netloc:
                continue
            public_path = unquote(target.path)
            if prefix and (public_path == prefix or public_path.startswith(prefix + '/')):
                public_path = public_path[len(prefix):]
            elif prefix:
                problems.append(f'{relative}: internal target outside the hosting prefix: {link}')
                continue
            file = (root / public_path.lstrip('/')).resolve()
            if not file.is_relative_to(root):
                problems.append(f'{relative}: path escapes public output: {link}')
            elif not file.is_file() and not (file / 'index.html').is_file():
                problems.append(f'{relative}: missing internal target: {link}')
    return problems


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('base_url')
    args = parser.parse_args()
    errors = validate_site(args.root, args.base_url)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    print('Rendered site validation passed.')
