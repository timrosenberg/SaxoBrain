"""Exercise body-authored editorial content through the real Hugo layouts."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_content_authoring import Document, ROOT


class RemainingAuthoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        pages = {
            '_index.md': '''---
title: Test
---
> [!starts] Editable entry heading
>
> > [!start] [Destination category](/curriculum/)
> > ### An editable card title
> > Description with a [separate source](https://example.org/source).
''',
            'curriculum/_index.md': '''---
title: Curriculum
---
Intro stays before the matrix.

> [!strands]
> - [Changed technique](#technique)
> - [Changed studies](#etudes)
> - [Changed repertoire](#repertoire)
> - [Changed reading](#reading)
> - [Changed listening](#listening)

> [!columns]
> > [!column] Editable explanation
> > A [linked explanation](https://example.org/explanation).
''',
            'curriculum/First Year.md': '''---
title: First Year
slug: first-year
year: 1
---
## [Changed technique](#technique)
- Practice slowly
## [Changed studies](#etudes)
- [[Sample Work]]
## [Changed repertoire](#repertoire)
Choose a work.
### Category
- [[Sample Work]]
> [!catalog] First Year
> There are **{count}** choices and **{advanced-count}** advanced choices.
>
> [Browse these choices](/?lvl=First+Year)
## [Changed reading](#reading)
> [!focus] A changed focus label:
> **An editable reading focus** with a [source](https://example.org/focus)
### Fall
- A reading assignment
## [Changed listening](#listening)
### Listening group
- [[Album]]
''',
            'works/Sample Work.md': '---\ntitle: Sample Work\nslug: sample-work\nyear-of-study: First Year\ninstruments: [Alto Saxophone]\n---\n',
            'recordings/Album.md': '---\ntitle: Album\nslug: album\n---\n',
            'composers/Example.md': '''---
title: Example
slug: example
photo: /media/example.jpg
---
> [!caption]
> Photo: [An editable **credit**](https://example.org/photo)

An editable biography.
''',
            'reading/explicit.md': '''---
title: Explicit PDF
---
> [!pdf] [An editable file label](/media/example.pdf)

A paragraph after the file.
''',
            'reading/ordinary.md': '---\ntitle: Ordinary link\n---\n[Just a link](/media/example.pdf)\n',
        }
        for name, source in pages.items():
            p = root / 'content' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(source)
        result = subprocess.run(['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts'),
                                 '--baseURL', 'https://example.org/SaxoBrain/'],
                                text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.pages = {name: (root / 'public' / name).read_text() for name in [
            'index.html', 'curriculum/index.html', 'curriculum/first-year/index.html',
            'composers/example/index.html', 'reading/explicit/index.html', 'reading/ordinary/index.html']}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_home_cards_follow_note_body_and_keep_independent_links(self):
        source = self.pages['index.html']
        doc = Document(source)
        self.assertEqual(len(doc.matching('div', 'starts')), 1)
        self.assertEqual(len(doc.matching('div', 'start')), 1)
        self.assertEqual(doc.max_anchor_depth, 1)
        self.assertIn('Editable entry heading', source)
        self.assertIn('An editable card title', source)
        self.assertIn('/SaxoBrain/curriculum/', source)
        self.assertIn('https://example.org/source', source)
        self.assertNotIn('Follow the curriculum', source)

    def test_curriculum_explanations_follow_overview_body(self):
        source = self.pages['curriculum/index.html']
        self.assertIn('Editable explanation', source)
        self.assertIn('https://example.org/explanation', source)
        self.assertIn('Changed technique', source)
        self.assertIn('<span class="line theme">An editable reading focus with a source</span>', source)
        self.assertEqual(Document(source).max_anchor_depth, 1)
        self.assertLess(source.index('Intro stays'), source.index('class="matrix"'))
        self.assertGreater(source.index('Editable explanation'), source.index('class="matrix"'))

    def test_year_headings_focus_and_counts_follow_body(self):
        source = self.pages['curriculum/first-year/index.html']
        self.assertIn('Changed technique', source)
        self.assertIn('Practice slowly', source)
        self.assertIn('A changed focus label:', source)
        self.assertIn('An editable reading focus', source)
        self.assertIn('There are <b>1</b> choices and <b>0</b> advanced choices.', source)
        self.assertIn('Browse these choices', source)
        self.assertIn('/SaxoBrain/?lvl=First', source)
        self.assertNotIn('[!focus]', source)
        self.assertNotIn('{count}', source[source.index('<main'):source.index('</main>')])
        doc = Document(source)
        ids = [a['id'] for _, a in doc.tags if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('repertoire', ids)

    def test_caption_is_in_portrait_and_not_duplicated_in_biography(self):
        source = self.pages['composers/example/index.html']
        self.assertIn('<figcaption>Photo:', source)
        self.assertEqual(source.count('An editable <strong>credit</strong>'), 1)
        self.assertLess(source.index('An editable <strong>credit</strong>'), source.index('</figure>'))
        self.assertIn('An editable biography.', source)

    def test_inline_pdf_is_explicit_and_preserves_fallback_link(self):
        source = self.pages['reading/explicit/index.html']
        self.assertIn('<div class="pdf"><iframe', source)
        self.assertIn('/SaxoBrain/media/example.pdf#view=FitH', source)
        self.assertIn('href="/SaxoBrain/media/example.pdf"', source)
        self.assertIn('A paragraph after the file.', source)
        self.assertNotIn('<iframe', self.pages['reading/ordinary/index.html'])

class PhotoCaptionMaintenance(unittest.TestCase):
    def test_photo_updates_write_body_credit_and_keep_editorial_caption(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('composer_photos', ROOT / 'scripts/composer_photos.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Composer.md'
            path.write_text('---\ntitle: Composer\nphoto: \nphoto-source: \nphoto-credit: \naliases: []\n---\n\nBiography.\n')
            module.set_fields(path, {'photo': '/media/example.jpg', 'photo-credit': 'A photographer',
                                     'photo-source': 'https://example.org/photo'})
            source = path.read_text()
            self.assertIn('> [!caption]\n> Photo: [A photographer](https://example.org/photo)', source)
            self.assertNotIn('photo-credit:', source)
            source = source.replace('A photographer', 'An edited photographer credit').replace('[!caption]', '[!CAPTION]')
            path.write_text(source)
            module.set_fields(path, {'photo': '/media/new.jpg', 'photo-credit': 'Automatic credit'})
            self.assertIn('An edited photographer credit', path.read_text())
            self.assertNotIn('Automatic credit', path.read_text())


if __name__ == '__main__':
    unittest.main()
