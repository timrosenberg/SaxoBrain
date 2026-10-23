"""Verify body-authored article cards with real Hugo rendering."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_content_authoring import Document, ROOT


class ArticleCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        (root / 'content/_index.md').write_text('---\ntitle: Test\n---\n')
        (root / 'content/Reading Source.md').write_text(
            '---\ntitle: Reading Source\nslug: reading-source\n---\n')
        (root / 'content/cards.md').write_text('''---
title: Cards
---
## Editable topic

> [!articles]
>
> > [!article] [[Reading Source|Editable article title]]
> >
> > > [!byline] An editable author
> >
> > An editable description with **emphasis** and a [source](https://example.org/source).
> >
> > > [!label] [Assigned term](/curriculum/second-year/#reading)
>
> > [!article] [Another reading](/reading/another/)
> >
> > A description without an author or label.

> [!article] Unlinked article title
>
> Preserve this fallback description.
''')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts'),
             '--baseURL', 'https://example.org/SaxoBrain/'], text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.source = (root / 'public/cards/index.html').read_text()
        cls.doc = Document(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_cards_preserve_body_copy_and_independent_links(self):
        self.assertEqual(len(self.doc.matching('div', 'article-cards')), 1)
        self.assertEqual(len(self.doc.matching('article', 'article-card')), 2)
        self.assertEqual(len(self.doc.matching('h3', 'article-card-title')), 2)
        self.assertIn('Editable article title', self.source)
        self.assertIn('An editable author', self.source)
        self.assertIn('An editable description with <strong>emphasis</strong>', self.source)
        self.assertIn('https://example.org/source', self.source)
        self.assertIn('/SaxoBrain/reading-source/', self.source)
        self.assertIn('/SaxoBrain/curriculum/second-year/#reading', self.source)
        self.assertEqual(self.doc.max_anchor_depth, 1)

    def test_optional_byline_label_and_unlinked_fallback(self):
        self.assertEqual(len(self.doc.matching('div', 'article-byline')), 1)
        self.assertEqual(len(self.doc.matching('div', 'article-label')), 1)
        self.assertEqual(self.source.count('Unlinked article title'), 1)
        self.assertIn('Preserve this fallback description.', self.source)
        self.assertNotIn('[!article]', self.source)


if __name__ == '__main__':
    unittest.main()
