"""Copy piece notes from Tim's official Notion export (Markdown & CSV) into content/works.

Usage: python3 -I scripts/import_notes_from_export.py <export folder> [--dry-run]

- Matches each export page to a work file through the Notion page ID in notion-ids.json.
- Only fills work files that have no body yet, so it never overwrites edits made in Obsidian.
- Links to other works or composers become [[File Name]] links. Links to attached files and
  to pages that are not imported yet become plain text and are listed in the report.
"""
import glob
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
IDS = json.load(open(os.path.join(ROOT, "scripts", "migration", "notion-ids.json"), encoding="utf-8"))
WORK_BY_HEX = {k.replace("-", ""): v["file"] for k, v in IDS["works"].items()}
COMPOSER_BY_HEX = {k.replace("-", ""): v for k, v in IDS["composers"].items()}
HEX = re.compile(r"([0-9a-f]{32})\.md$")
LINK = re.compile(r"\[([^\]]*)\]\(((?:[^()]|\([^()]*\))*)\)")


def split_page(text):
    """Return the page body: everything after the title and the property block."""
    lines = text.split("\n")
    j = 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    while j < len(lines) and lines[j].strip():
        j += 1
    return "\n".join(lines[j:]).strip()


MENTION = re.compile(r"[ \t]*[-–][ \t]*\[‣\]\([^)]*\)|\[‣\]\([^)]*\)")


def convert_links(body, report, who):
    body = MENTION.sub("", body)  # Notion's "‣" mention markers point back to Notion
    def sub(m):
        label, target = m.group(1), urllib.parse.unquote(m.group(2))
        if re.match(r"(https?:|mailto:)", target):
            return m.group(0)
        h = HEX.search(target)
        if h and "Composers Database" in target and h.group(1) in COMPOSER_BY_HEX:
            return f"[[{COMPOSER_BY_HEX[h.group(1)]}|{label}]]" if label != COMPOSER_BY_HEX[h.group(1)] else f"[[{label}]]"
        if h and h.group(1) in WORK_BY_HEX:
            name = WORK_BY_HEX[h.group(1)]
            return f"[[{name}|{label}]]"
        kind = "page not imported yet" if h else "attached file"
        report.append((who, kind, label, target))
        return label
    return LINK.sub(sub, body)


def main(export, dry):
    pages = glob.glob(os.path.join(export, "Home", "Saxophone R*pertoire Database", "*.md"))
    report, written, skipped, empty = [], 0, [], 0
    for p in sorted(pages):
        h = HEX.search(p)
        body = split_page(open(p, encoding="utf-8").read())
        if not body:
            empty += 1
            continue
        name = WORK_BY_HEX.get(h.group(1)) if h else None
        target = os.path.join(CONTENT, "works", f"{name}.md") if name else None
        if not target or not os.path.exists(target):
            skipped.append((os.path.basename(p), "no matching work file"))
            continue
        current = open(target, encoding="utf-8").read()
        fm_end = current.find("\n---", 4)
        if current[fm_end + 4:].strip():
            skipped.append((name, "already has a body"))
            continue
        body = convert_links(body, report, name)
        if not dry:
            with open(target, "w", encoding="utf-8") as f:
                f.write(current[:fm_end + 4].rstrip("\n") + "\n\n" + body + "\n")
        written += 1
    print(f"{'Would write' if dry else 'Wrote'} {written} notes. {empty} pages have no notes. Skipped {len(skipped)}.")
    for s in skipped:
        print("  skipped:", *s)
    print(f"\nLinks that became plain text ({len(report)}):")
    for who, kind, label, target in report:
        print(f"  [{kind}] {who}: {label} -> {target}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], "--dry-run" in sys.argv)
