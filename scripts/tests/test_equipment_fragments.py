"""Equipment fragments survive presentation edits in Markdown tables."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class EquipmentFragments(unittest.TestCase):
    def render(self, cell):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
            shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
            (root / 'content/resources/equipment').mkdir(parents=True)
            (root / 'content/resources/equipment/_index.md').write_text(
                '---\ntitle: Equipment\n---\n')
            (root / 'content/equipment').mkdir()
            (root / 'content/equipment/comparisons.md').write_text('''---
title: Comparisons
equipment-table-anchors:
  - text: "Lars **Mlekusch (LM)** / LM1"
    id: lars-mlekusch-lm
---
| Model | Tip opening |
| --- | --- |
| ''' + cell + ''' | 1.60 |
''')
            result = subprocess.run(
                ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
                text=True, capture_output=True)
            page = root / 'public/equipment/comparisons/index.html'
            return result, page.read_text() if page.exists() else ''

    def test_fragment_survives_changed_emphasis_and_preserves_cell_formatting(self):
        for cell, rendered in [
            ('Lars Mlekusch (LM) / LM1', 'Lars Mlekusch (LM) / LM1'),
            ('Lars *Mlekusch (LM)* / LM1', 'Lars <em>Mlekusch (LM)</em> / LM1'),
            ('Lars **Mlekusch (LM)** / LM1', 'Lars <strong>Mlekusch (LM)</strong> / LM1'),
        ]:
            with self.subTest(cell=cell):
                result, html = self.render(cell)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('<td id="lars-mlekusch-lm">' + rendered + '</td>', html)
                self.assertEqual(html.count('id="lars-mlekusch-lm"'), 1)

    def test_missing_cell_still_fails_the_build(self):
        result, _ = self.render('Different model')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('has no cell for fragment "lars-mlekusch-lm"',
                      result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
