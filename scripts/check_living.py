#!/usr/bin/env python3
"""Check whether composers we list as living have died, according to Wikidata.

Looks at every composer with a `wikidata:` ID and an empty `died:` field. Prints a Markdown report of anyone
Wikidata now gives a date of death, and a count of composers it cannot check (no Wikidata ID).
Exit code 1 when someone needs attention, so a scheduled job can open an issue.

Nothing is changed: a person confirms the death and fills in `died:` by hand.

Usage: python3 scripts/check_living.py [report.md]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import wikidata_composers as w


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    living, unchecked = {}, []
    for c in w.read_composers():
        if c["died"]:
            continue
        if c["wikidata"].startswith("Q"):
            living[c["wikidata"]] = c
        else:
            unchecked.append(c)
    ents = w.entities(list(living), "claims")
    died = []
    for q, c in living.items():
        y = w.year(ents.get(q, {}), "P570")
        if y:
            died.append((c, q, y))

    lines = []
    if died:
        lines += ["Wikidata now lists a date of death for these composers. Please confirm (for example in an obituary) "
                  "and fill in `died:` in their file.", ""]
        lines += [f"- **{c['title']}** (`content/composers/{c['file'].name}`): died {y}, "
                  f"per [Wikidata {q}](https://www.wikidata.org/wiki/{q})" for c, q, y in sorted(died, key=lambda x: x[0]["title"])]
        lines.append("")
    lines.append(f"Checked {len(living)} composers with no death year. "
                 f"{len(unchecked)} composers with no death year have no Wikidata ID, so they cannot be checked automatically.")
    report = "\n".join(lines) + "\n"
    print(report)
    if out:
        out.write_text(report)
    return 1 if died else 0


if __name__ == "__main__":
    sys.exit(main())
