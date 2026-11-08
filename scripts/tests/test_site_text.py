"""Exercise editable Site Text tables through Hugo's real label loader."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class SiteTextTables(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'layouts/_partials').mkdir(parents=True)
        (self.root / 'content/Site Text').mkdir(parents=True)
        (self.root / 'hugo.toml').write_text(
            'baseURL = "https://example.org/"\n'
            'disableKinds = ["taxonomy", "term", "rss", "sitemap"]\n')
        for name in ['site-text.html', 't.html']:
            shutil.copy(ROOT / 'layouts/_partials' / name,
                        self.root / 'layouts/_partials' / name)
        shutil.copy(ROOT / 'content/Site Text/_index.md',
                    self.root / 'content/Site Text/_index.md')
        (self.root / 'layouts/index.html').write_text(
            '{{ partial "site-text.html" . | jsonify | safeHTML }}')
        (self.root / 'layouts/page.html').write_text('SHOULD NOT PUBLISH {{ .Content }}')
        (self.root / 'layouts/section.html').write_text('SHOULD NOT PUBLISH {{ .Content }}')

    def note(self, name, body):
        (self.root / 'content/Site Text' / name).write_text(
            '---\ntitle: Labels\n---\n\n' + body)

    def build(self):
        return subprocess.run(['hugo', '--source', str(self.root)],
                              text=True, capture_output=True)

    def values(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads((self.root / 'public/index.html').read_text())

    def test_table_text_is_literal_and_editable_without_properties(self):
        self.note('Labels.md', r'''Introductory prose is not a setting.

| Setting | Text |
| :--- | ---: |
| composer-website | Composer's "website" & recordings |
| js-label | {count} of {total} works… |
| pipe-label | A \| B |
| path-label | C:\scores |
| number-label | 2026 |
| boolean-label | false |
''')
        expected = {
            'composer-website': 'Composer\'s "website" & recordings',
            'js-label': '{count} of {total} works…',
            'pipe-label': 'A | B',
            'path-label': r'C:\scores',
            'number-label': '2026',
            'boolean-label': 'false',
        }
        self.assertEqual(self.values(), expected)
        p = self.root / 'content/Site Text/Labels.md'
        p.write_text(p.read_text().replace('2026', '2027'))
        expected['number-label'] = '2027'
        self.assertEqual(self.values(), expected)

    def test_duplicate_setting_reports_both_notes(self):
        self.note('First.md', '| Setting | Text |\n| --- | --- |\n| label | First |\n')
        self.note('Second.md', '| Setting | Text |\n| --- | --- |\n| label | Second |\n')
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        for text in ['duplicate', 'label', 'First.md', 'Second.md']:
            self.assertIn(text, output)

    def test_optional_outer_pipes_do_not_drop_javascript_labels(self):
        for header, separator, row in [
            ('Setting | Text', '--- | ---', 'js-pdf-loading | New message'),
            ('| Setting | Text |', '| --- | --- |', 'js-pdf-loading | New message |'),
            ('| Setting | Text |', '| --- | --- |', '| js-pdf-loading | New message'),
        ]:
            with self.subTest(row=row):
                self.note('Labels.md', '\n'.join([header, separator, row]) + '\n')
                self.assertEqual(self.values(), {'js-pdf-loading': 'New message'})

    def test_malformed_javascript_row_fails_instead_of_disappearing(self):
        self.note('Broken.md', 'Setting | Text\n--- | ---\njs-pdf-loading New message\n')
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Broken.md', result.stdout + result.stderr)

    def test_literal_backslash_before_escaped_pipe(self):
        self.note('Labels.md', 'Setting | Text\n--- | ---\n'
                  + r'pipe-label | A\\| B' + '\n')
        self.assertEqual(self.values(), {'pipe-label': r'A\| B'})

    def test_bad_table_rows_fail_with_the_note_name(self):
        for row in ['| label | A | B |', '| label |   |', '| invalid key | Text |']:
            with self.subTest(row=row):
                self.note('Broken.md', '| Setting | Text |\n| --- | --- |\n' + row + '\n')
                result = self.build()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Broken.md', result.stdout + result.stderr)

    def test_site_text_pages_remain_unpublished(self):
        self.note('Hidden.md', '| Setting | Text |\n| --- | --- |\n| private-label | Text |\n')
        self.assertEqual(self.values(), {'private-label': 'Text'})
        self.assertFalse((self.root / 'public/site-text').exists())


if __name__ == '__main__':
    unittest.main()
