"""Exercise body components through Hugo, including ordinary Obsidian Markdown."""
import html
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.text = []
        self.anchor_depth = 0
        self.max_anchor_depth = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == 'a':
            self.anchor_depth += 1
            self.max_anchor_depth = max(self.max_anchor_depth, self.anchor_depth)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor_depth -= 1

    def handle_data(self, data):
        self.text.append(data)

    def matching(self, tag, cls):
        return [attrs for t, attrs in self.tags
                if t == tag and cls in attrs.get('class', '').split()]


class BodyComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.root = root
        (root / 'content').mkdir()
        shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
        shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
        (root / 'content/_index.md').write_text('---\ntitle: Test\n---\n')
        (root / 'content/resources/equipment').mkdir(parents=True)
        (root / 'content/resources/equipment/_index.md').write_text(
            '---\ntitle: Equipment\ntype: equipment\n---\n')
        (root / 'content/Included Note.md').write_text(
            '---\ntitle: Included Note\n---\n\nText edited in the source note.\n'
            '\n## Research notes (private)\n\nPrivate fixture research.\n\n![[Included Note]]\n')
        (root / 'content/Source With Heading.md').write_text(
            '---\ntitle: Source With Heading\n---\n\n## First method\n\nEmbedded instructions.\n\n[Jump](#first-method)\n\n### Nested details\n\nNested instructions.\n')
        (root / 'content/method.md').write_text(
            '---\ntitle: Method\ntype: equipment\nequipment-format: methods\n---\n\n'
            '## First method\n\n![[Source With Heading]]\n\n## Second method\n\n![[Source With Heading]]\n\nOther instructions.\n')
        (root / 'content/product.md').write_text(
            (root / 'content/method.md').read_text().replace('equipment-format: methods', 'equipment-format: products'))
        (root / 'content/instruments.md').write_text(
            '---\ntitle: Instruments\ntype: equipment\nequipment-format: saxophones\n---\n\n'
            'See [[Included Note]].\n\n![[Included Note]]\n\n'
            '## Altos [[Included Note|guide]]\n\n### First method\n\n![[Source With Heading]]\n\n'
            '## Tenors\n\n### Another product\n\n![[Source With Heading]]\n')
        (root / 'content/fixture.md').write_text('''---
title: Fixture
pdf-viewer: true
image-viewer: true
---

> [!resource] [Guide](/media/example.pdf)
>
> Any editable description, with **emphasis** and a [credit](https://example.org/credit).
>
> A second paragraph can wrap
> across lines.

> [!resource] [Picture](/media/chart.jpeg)

> [!resource] [[Included Note|Article]]
> Optional article description.

> [!topics]
> > [!topic] [An editable topic](#section-id)
> > An editable card description with a [source](https://example.org/topic-source).

> [!products]
> > [!product] [A strap](https://example.org/strap)
> >
> > ![A complete strap](/media/strap.jpg)
> >
> > An editable product note with a [tall size](https://example.org/strap-tall).
>
> > [!product] [Another strap](https://example.org/another-strap)
> > A product can have notes without a photo.

> [!section] [An editable heading](#section-id)
>
> ![[Included Note]]

> [!unknown] Unknown but editable
> Keep this fallback text.

> An ordinary quotation.

`![[Not An Embed]]`
''')
        result = subprocess.run(
            ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
            text=True, capture_output=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.source = (root / 'public/fixture/index.html').read_text()
        cls.doc = Document(cls.source)
        cls.methods = Document((root / 'public/method/index.html').read_text())
        cls.products = Document((root / 'public/product/index.html').read_text())
        cls.instruments = Document((root / 'public/instruments/index.html').read_text())
        cls.instruments_source = (root / 'public/instruments/index.html').read_text()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_resources_use_explicit_body_blocks(self):
        self.assertEqual(len(self.doc.matching('div', 'pdf-resource')), 3)
        self.assertIn('Any editable description', self.source)
        self.assertIn('<strong>emphasis</strong>', self.source)
        self.assertIn('https://example.org/credit', self.source)
        self.assertIn('data-pdf-view', self.source)
        self.assertIn('data-image-view', self.source)

    def test_article_and_creditless_file_keep_ordinary_links(self):
        links = [a for t, a in self.doc.tags if t == 'a']
        self.assertTrue(any(a.get('href') == '/included-note/' for a in links))
        self.assertTrue(any(a.get('href') == '/media/chart.jpeg' and 'download' in a
                            for a in links))

    def test_topic_and_section_text_come_from_body(self):
        self.assertEqual(sum('equipment-topic' in a.get('class', '').split()
                             for _, a in self.doc.tags), 1)
        self.assertTrue(any(a.get('id') == 'section-id' for t, a in self.doc.tags))
        self.assertIn('An editable card description', self.source)

    def test_obsidian_embed_renders_source_text(self):
        self.assertIn('Text edited in the source note.', self.source)
        self.assertNotIn('![[Included Note]]', self.source)
        self.assertNotIn('Private fixture research.', self.source)

    def test_product_blocks_keep_photos_notes_and_independent_links(self):
        self.assertEqual(len(self.doc.matching('div', 'equipment-products-cards')), 1)
        self.assertEqual(len(self.doc.matching('section', 'equipment-product')), 2)
        images = [a for t, a in self.doc.tags if t == 'img']
        self.assertEqual(sum(a.get('src') == '/media/strap.jpg' for a in images), 1)
        self.assertTrue(any(a.get('alt') == 'A complete strap' for a in images))
        links = {a.get('href') for t, a in self.doc.tags if t == 'a'}
        self.assertTrue({'https://example.org/strap', 'https://example.org/strap-tall',
                         'https://example.org/another-strap'} <= links)
        self.assertIn('An editable product note', ''.join(self.doc.text))
        self.assertIn('A product can have notes without a photo.', ''.join(self.doc.text))
        self.assertEqual(self.doc.max_anchor_depth, 1)

    def test_unknown_blocks_and_quotes_keep_their_text(self):
        self.assertIn('Unknown but editable', self.source)
        self.assertIn('Keep this fallback text.', self.source)
        self.assertIn('An ordinary quotation.', self.source)
        self.assertIn('![[Not An Embed]]', ''.join(self.doc.text))

    def test_embedded_headings_do_not_create_extra_method_controls(self):
        self.assertEqual(len(self.methods.matching('details', 'equipment-method')), 2)
        self.assertIn('Embedded instructions.', ''.join(self.methods.text))
        ids = [a['id'] for _, a in self.methods.tags if 'id' in a]
        self.assertEqual(len(ids), len(set(ids)))
        fragments = [a['href'][1:] for t, a in self.methods.tags
                     if t == 'a' and a.get('href', '').startswith('#embed-')]
        self.assertEqual(len(fragments), 2)
        self.assertTrue(all(fragment in ids for fragment in fragments))

    def test_links_inside_topic_descriptions_are_independent(self):
        self.assertEqual(self.doc.max_anchor_depth, 1)
        self.assertIn('https://example.org/topic-source', self.source)

    def test_embedded_headings_do_not_create_extra_products(self):
        self.assertEqual(len(self.products.matching('section', 'equipment-product')), 2)
        self.assertEqual(len(self.instruments.matching('section', 'equipment-product')), 2)
        for doc in [self.products, self.instruments]:
            ids = [a['id'] for _, a in doc.tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))

    def test_circular_embeds_fail_with_a_clear_error(self):
        paths = [self.root / 'content/Cycle A.md', self.root / 'content/Cycle B.md']
        paths[0].write_text('---\ntitle: Cycle A\n---\n\n![[Cycle B]]\n')
        paths[1].write_text('---\ntitle: Cycle B\n---\n\n![[Cycle A]]\n')
        try:
            result = subprocess.run(
                ['hugo', '--source', str(self.root), '--layoutDir', str(ROOT / 'layouts')],
                text=True, capture_output=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Circular note embed', result.stdout + result.stderr)
        finally:
            for path in paths:
                path.unlink()

    def test_deferred_introduction_keeps_links_and_embeds(self):
        self.assertNotIn('[[Included Note', self.instruments_source)
        self.assertIn('Text edited in the source note.', ''.join(self.instruments.text))


if __name__ == '__main__':
    unittest.main()
