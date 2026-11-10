"""Exercise the catalog's actual JavaScript instrumentation formatter."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CatalogInstrumentation(unittest.TestCase):
    def test_ensemble_sizes_and_accompaniments_use_distinct_wording(self):
        cases = [
            # William Albright's Doo-Dah uses these two instrument tags.
            (["Alto Saxophone", "Trio"], "Alto Saxophone Trio"),
            (["Trio", "Alto Saxophone"], "Alto Saxophone Trio"),
            (["Soprano Saxophone", "Alto Saxophone", "Tenor Saxophone", "Trio"],
             "Soprano and Alto and Tenor Saxophone Trio"),
            (["Soprano Saxophone", "Tenor Saxophone", "Piano", "Trio"],
             "Soprano and Tenor saxophone with piano (trio)"),
            (["Alto Saxophone", "Trumpet", "Piano", "Trio"],
             "Alto saxophone with trumpet, piano (trio)"),
            (["Alto Saxophone", "Duo"], "Alto Saxophone Duo"),
            (["Duo", "Alto Saxophone"], "Alto Saxophone Duo"),
            (["Soprano Saxophone", "Baritone Saxophone", "Duo"],
             "Soprano and Baritone Saxophone Duo"),
            (["Alto Saxophone", "Duo", "Orchestra"],
             "Alto Saxophone Duo with orchestra"),
            (["Alto Saxophone", "Piano"], "Alto saxophone with piano"),
            (["Soprano Saxophone", "Alto Saxophone", "Piano"],
             "Soprano or Alto saxophone with piano"),
            (["Alto Saxophone", "Unaccompanied"], "Alto saxophone, unaccompanied"),
            (["Saxophone Quartet (SATB)", "Unaccompanied"], "Saxophone Quartet (SATB)"),
        ]
        # Load the real editable labels, including any labels introduced by the fix.
        labels = {}
        for note in (ROOT / "content/Site Text").glob("*.md"):
            for line in note.read_text().splitlines():
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                if len(cells) == 2:
                    labels[cells[0]] = cells[1]
        script = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const input = JSON.parse(fs.readFileSync(0, "utf8"));
const source = fs.readFileSync("static/js/catalog.js", "utf8");
// Stop before UI setup; execute the production formatter and its dependencies.
const context = { document: { getElementById: () => ({ textContent: JSON.stringify(input.labels) }) } };
vm.createContext(context);
vm.runInContext(source.slice(0, source.indexOf("  function render()"))
  + "globalThis.format = instLine; })();", context);
process.stdout.write(JSON.stringify(input.cases.map(i => context.format({ i }))));
'''
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, text=True, capture_output=True,
            input=json.dumps({"labels": labels, "cases": [tags for tags, _ in cases]}))
        self.assertEqual(result.returncode, 0, result.stderr)
        for (tags, expected), actual in zip(cases, json.loads(result.stdout)):
            with self.subTest(tags=tags):
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
