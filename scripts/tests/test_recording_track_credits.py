"""Verify album credits without requiring composer stub pages."""
from pathlib import Path
import html
import re
import shutil
import subprocess
import tempfile
import unittest

from test_content_authoring import Document, ROOT


class RecordingTrackCredits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        for section in ['recordings', 'composers', 'works']:
            (root / 'content' / section).mkdir()
        for name in ['Known Composer', 'Other Composer']:
            (root / 'content/composers' / f'{name}.md').write_text(
                f'---\ntitle: {name}\n---\n')
        (root / 'content/works/Known Composer - Sonata.md').write_text('''---
title: Sonata
slug: sonata
composer:
  - "[[Known Composer]]"
instruments: [Alto Saxophone, Piano]
---
''')
        (root / 'content/recordings/Credits.md').write_text('''---
title: Credits
slug: credits
youtube: https://www.youtube.com/playlist?list=fixture
tracks:
  - "Obsidian Butterfly · 9:59 · John Leszczyński"
  - "Suite: I. Opening · 1:00 · Claudio Gabriele"
  - "Suite: II. Closing · 2:00 · Claudio Gabriele"
  - "Catalog composer · 3:00 · [[Known Composer]]"
  - "Sonata: I. Opening · 4:00 · [[Known Composer - Sonata]]"
  - "Sonata: II. Closing · 5:00 · [[Known Composer - Sonata]]"
  - "No credit · 6:00"
  - "Joint work · 7:00 · [[Known Composer]], [[Other Composer]]"
---
''')
        (root / 'content/recordings/Nested.md').write_text('''---
title: Nested
slug: nested
youtube: https://www.youtube.com/playlist?list=fixture
tracks:
  - "Sonata: I. This Black Cat · 4:49 · Carter Pann"
  - "Sonata: II. Three Songs Without Words: 1. Reverie · 3:54 · Carter Pann"
  - "Sonata: II. Three Songs Without Words: 2. Soaring · 3:14 · Carter Pann"
  - "Sonata: II. Three Songs Without Words: 3. Consolation · 6:09 · Carter Pann"
  - "Sonata: III. Cuppa Joe · 1:51 · Carter Pann"
  - "Sonata: IV. Epilogue: Lacrimosa · 4:39 · Carter Pann"
---
''')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
            text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.source = (root / 'public/recordings/credits/index.html').read_text()
        cls.nested_source = (root / 'public/recordings/nested/index.html').read_text()
        cls.doc = Document(cls.source)
        cls.credits = [html.unescape(s) for s in re.findall(
            r'<span class="by">([^<]+)</span>', cls.source)]
        cls.composer_pages = list((root / 'public/composers').glob('*/index.html'))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_plain_name_appears_as_a_credit_without_a_composer_page(self):
        self.assertIn('John Leszczyński', self.credits)
        self.assertEqual(len(self.composer_pages), 2)
        self.assertNotIn('john-leszczyński', self.source)

    def test_plain_name_is_shared_by_grouped_movements(self):
        self.assertEqual(self.credits.count('Claudio Gabriele'), 1)
        self.assertRegex(self.source,
                         r'<li class="tgroup">Suite\s*<span class="by">Claudio Gabriele</span>')

    def test_existing_links_and_playlist_positions_remain_intact(self):
        self.assertEqual(self.credits.count('Known Composer'), 2)
        self.assertIn('Known Composer, Other Composer', self.credits)
        self.assertTrue(any(tag == 'a' and attrs.get('href') == '/works/sonata/'
                            for tag, attrs in self.doc.tags))
        rows = self.doc.matching('button', 'track')
        self.assertEqual([row['data-i'] for row in rows],
                         ['0', '1', '2', '3', '4', '5', '6', '7'])
        self.assertIn('<span class="td">9:59</span>', self.source)
        self.assertNotIn('Obsidian Butterfly ·', ''.join(self.doc.text))

    def test_subdivided_movement_stays_under_one_piece_heading(self):
        headings = re.findall(r'<li class="tgroup">(.*?)</li>', self.nested_source)
        self.assertEqual(len(headings), 1)
        self.assertIn('Sonata', headings[0])
        self.assertEqual(self.nested_source.count('Carter Pann'), 1)
        for name in ['1. Reverie', '2. Soaring', '3. Consolation']:
            self.assertIn(f'II. Three Songs Without Words: {name}', self.nested_source)
        self.assertIn('IV. Epilogue: Lacrimosa', self.nested_source)
        rows = Document(self.nested_source).matching('button', 'track')
        self.assertEqual([row['data-i'] for row in rows], list(map(str, range(6))))


if __name__ == '__main__':
    unittest.main()
