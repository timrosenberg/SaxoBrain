"""Import the non-catalog Notion pages (curriculum, reading, recordings, lists, resources) as Hugo pages.

Usage: python3 -I scripts/import_pages_from_export.py <export folder> <export zip> [--dry-run] [--force]

Reads scripts/migration/page-map.csv (rows with status "import") and writes
content/<section>/<Title>.md. Each page gets a `notion-id:` so a rerun never overwrites a page
unless --force is given. Attached files are copied from the zip into static/media/<address>/.

- <aside> callouts become blockquotes. Notion's own "Status: Imported" notes are dropped.
- Links to works, composers and other imported pages become [[File Name]] links. Links to private
  pages, database views and files that were not copied become plain text and are listed in the report.
- Pages that reproduce other people's writing get `third-party: true`; pages that host copied files get
  `third-party-files: true`. The layouts print a notice that these are outside Tim's CC BY-SA license.
"""
import csv
import json
import os
import posixpath
import re
import shutil
import sys
import unicodedata
import urllib.parse
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
STATIC = os.path.join(ROOT, "static", "media")
IDS = json.load(open(os.path.join(ROOT, "scripts", "migration", "notion-ids.json"), encoding="utf-8"))
WORK_BY_HEX = {k.replace("-", ""): v["file"] for k, v in IDS["works"].items()}
COMPOSER_BY_HEX = {k.replace("-", ""): v for k, v in IDS["composers"].items()}
MAX_COPY = 30 * 1024 * 1024  # larger files are left for separate hosting
LINK = re.compile(r"(!?)\[([^\]]*)\]\(((?:[^()]|\([^()]*\))*)\)")
HEX_IN = re.compile(r"([0-9a-f]{32})(?:\.md)?$")
PLACEHOLDER = "Moving over from Notion."
MENTION = re.compile(r"[ \t]*[-–][ \t]*\[‣\]\([^)]*\)|\[‣\]\([^)]*\)")

# Section pages that do not come from a Notion page get a title only
SECTION_STUBS = {
    "lists/competitions": "Competition Repertoire Lists",
    "lists/colleges": "College Repertoire Lists",
    "lists/programs": "Collected Recital Programs",
    "resources/equipment": "Saxophone Equipment",
}
# Pages whose source note does not say they are by someone else, but are
THIRD_PARTY_EXTRA = {"Jaw Vibrato Exercises", "The Alexander Method", "Summary of Dr. Young's Method"}
# Pages whose first external link is the original article (the URL matches the title)
ORIGINAL_IS_FIRST_LINK = {"Why Good Reeds Go Bad by Pete Spitzer", "A Method for Evaluating Reed Cane by Pete Spitzer",
                          "Stop Wasting Money on Reeds: tips for new saxophone reeds by Joshua Mlodzianowski"}
WAYBACK = os.path.join(ROOT, "scripts", "migration", "wayback.json")  # original URL -> verified snapshot URL
THIRD_PARTY_NOTE = re.compile(r"posted on facebook by|originally published on|appeared in|the following (article|was)|"
                              r"written by|printed here with", re.I)


def nfc(s):
    return unicodedata.normalize("NFC", s)


def hugo_key(name):
    return re.sub(r"[\s\-_]+", "", nfc(name)).lower()


def file_stem(title):
    s = re.sub(r"[*\"\\/<>:|?]+", " ", title.replace("’", "'"))
    return re.sub(r"\s+", " ", s).strip(" .")


def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def strip_emoji(text):
    while text and (unicodedata.category(text[0]) in ("So", "Sk") or text[0] in "️‍" or text[0].isspace()):
        text = text[1:]
    return text


class Importer:
    def __init__(self, export, zpath, dry):
        self.export, self.dry = export, dry
        self.zip = zipfile.ZipFile(zpath)
        self.members = {}
        for i in self.zip.infolist():
            self.members[nfc(i.filename).lower()] = i
        self.top = self.zip.namelist()[0].split("/")[0]
        rows = list(csv.DictReader(open(os.path.join(ROOT, "scripts", "migration", "page-map.csv"), encoding="utf-8")))
        self.rows = rows
        self.by_hex = {r["notion_id"]: r for r in rows if r["notion_id"]}
        self.stems = {}
        for r in rows:
            if r["status"] == "import":
                r["stem"] = "_index" if r["slug"] == "" else file_stem(r["title"])
                r["dir"] = r["target"].strip("/") if r["slug"] == "" else r["target"].strip("/").rsplit("/", 1)[0]
        self.report = {"unresolved": [], "copied": [], "skipped_big": [], "flagged": [], "written": 0, "skipped_existing": []}
        existing = {hugo_key(f[:-3]) for d in ("works", "composers") for f in os.listdir(os.path.join(CONTENT, d))}
        for r in rows:
            if r["status"] == "import" and r["stem"] != "_index":
                k = hugo_key(r["stem"])
                if k in existing:
                    raise SystemExit(f"File name {r['stem']!r} collides with an existing page under Hugo's naming rule")
                existing.add(k)

    # ---- links and files
    def copy_asset(self, page, rel_target):
        base = posixpath.dirname(page["source"])
        member = nfc(posixpath.normpath(posixpath.join(self.top, base, urllib.parse.unquote(rel_target)))).lower()
        info = self.members.get(member)
        if info is None:
            return None, "file not found in zip"
        if info.file_size > MAX_COPY:
            return None, f"{info.file_size // 1_000_000} MB, needs separate hosting"
        name = re.sub(r"[^\w.()\-]+", "_", posixpath.basename(info.filename))
        dest_rel = f"{page['target'].strip('/') or page['dir']}/{name}"
        if page["slug"] == "":
            dest_rel = f"{page['dir']}/{name}"
        dest = os.path.join(STATIC, dest_rel)
        if not self.dry:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with self.zip.open(info) as s, open(dest, "wb") as d:
                shutil.copyfileobj(s, d)
        self.report["copied"].append((page["title"], dest_rel, info.file_size))
        return "/media/" + urllib.parse.quote(dest_rel), None

    def resolve(self, page, is_img, label, target, state):
        target = target.strip()
        if re.match(r"(https?:|mailto:)", target):
            m = re.match(r"https?://app\.notion\.com/p/(?:[^/]*-)?([0-9a-f]{32})", target)
            if m:
                return self.internal(page, m.group(1), label)
            return f"![{label}]({target})" if is_img else f"[{label}]({target})"
        path = urllib.parse.unquote(target)
        h = HEX_IN.search(path.split("?")[0]) if path.endswith(".md") else None
        if h:
            return self.internal(page, h.group(1), label)
        url, why = self.copy_asset(page, target)
        if url is None:
            self.report["skipped_big" if why and "MB" in why else "unresolved"].append((page["title"], label, why))
            return "" if is_img else label
        if not is_img and not path.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            state["files"] = True
        return f"![{label}]({url})" if is_img else f"[{label}]({url})"

    def internal(self, page, h, label):
        label = label.replace("|", "-")
        if h in WORK_BY_HEX:
            return f"[[{nfc(WORK_BY_HEX[h])}|{label}]]"
        if h in COMPOSER_BY_HEX:
            return f"[[{nfc(COMPOSER_BY_HEX[h])}|{label}]]"
        r = self.by_hex.get(h)
        if r and r["status"] == "import":
            if r["slug"] == "":
                return f"[{label}]({r['target']})"
            return f"[[{nfc(r['stem'])}|{label}]]"
        why = {"view": "database view, not a page", "private": "private page", "ask": "page kept private"}.get(
            r["status"] if r else "", "target not in the export")
        self.report["unresolved"].append((page["title"], label, why))
        return label

    # ---- body conversion
    def convert(self, page, text):
        lines = text.split("\n")
        body = "\n".join(lines[1:]).strip("\n")
        props = {}
        if page["kind"] in ("album", "etude list"):
            plines = body.split("\n")
            i = 0
            while i < len(plines) and plines[i].strip() == "":
                i += 1
            j = i
            while j < len(plines) and re.match(r"^[A-Z][^:\n]{0,40}: ", plines[j]):
                k, v = plines[j].split(": ", 1)
                props[k] = v
                j += 1
            body = "\n".join(plines[j:]).strip("\n")
        state = {"files": False}
        # callouts
        notes = []

        def aside(m):
            inner = m.group(1).strip()
            if re.search(r"Status: Imported", inner):
                return ""
            first = inner
            notes.append(first)
            inner = strip_emoji(inner.replace("\n", "\n"))
            return "\n".join("> " + ln if ln.strip() else ">" for ln in inner.split("\n")) + "\n"
        body = re.sub(r"^[ \t]*(?:[-*][ \t]+)?(?:\*\*)?Table of Contents(?:\*\*)?[ \t]*\n", "", body, flags=re.M)  # Notion TOC placeholder
        body = MENTION.sub("", body)  # Notion's "‣" mention markers point back to Notion
        body = re.sub(r"<aside>\s*(.*?)\s*</aside>", aside, body, flags=re.S)
        body = LINK.sub(lambda m: self.resolve(page, m.group(1) == "!", m.group(2), m.group(3), state), body)
        body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
        return body, props, notes, state

    def front(self, page, props, notes, state, body):
        fm = [f"title: {yq(page['title'])}"]
        if page["slug"]:
            fm.append(f"slug: {page['slug']}")
        tp = (page["title"] in THIRD_PARTY_EXTRA or
              (page["kind"] != "etude list" and re.search(r"\sby\s+[A-Z]", page["title"]) and "Rosenberg" not in page["title"]) or
              any((THIRD_PARTY_NOTE.search(n) or n.lstrip().startswith("🔗")) and "my now defunct blog" not in n for n in notes))
        if tp:
            fm.append("third-party: true")
            url = next((re.search(r"https?://[^\s\]\)]+", n).group(0) for n in notes if re.search(r"https?://", n)), "")
            if not url and page["title"] in ORIGINAL_IS_FIRST_LINK:
                url = re.search(r"\]\((https?://[^)\s]+)", body).group(1)
            if "facebook.com" in url:
                url = ""  # a profile page, not the article
            if url:
                url = url.rstrip(".,")
                fm.append(f"original-url: {yq(url)}")
                snap = (json.load(open(WAYBACK, encoding="utf-8")) if os.path.exists(WAYBACK) else {}).get(url)
                if snap:
                    fm.append(f"wayback-url: {yq(snap)}")
            self.report["flagged"].append((page["title"], url))
        if state["files"] and not tp and page["title"] not in ("The Scale Series",):
            fm.append("third-party-files: true")
            self.report["flagged"].append((page["title"], "(hosts copied files)"))
        elif state["files"] and tp:
            pass
        for k, v in props.items():
            key = re.sub(r"[^a-z0-9]+", "-", k.lower()).strip("-")
            key = {"saxophonist-s": "saxophonists"}.get(key, key)
            if key == "works-performed":
                ws = []
                # a relation property reads "Title (path.md), Title (path.md)"; the page ID is what matters
                for h in re.findall(r"([0-9a-f]{32})\.md", urllib.parse.unquote(v)):
                    if h in WORK_BY_HEX:
                        ws.append(nfc(WORK_BY_HEX[h]))
                    else:
                        self.report["unresolved"].append((page["title"], h, "work not found"))
                fm.append("works:\n" + "\n".join(f"  - {yq('[[' + w + ']]')}" for w in ws))
            elif key == "composers-performed":
                continue
            elif key in ("album-cover", "pdf"):
                if v.startswith("http"):
                    url, why = v, None  # remote cover art stays a web link
                else:
                    url, why = self.copy_asset(page, v) if v else (None, None)
                if url:
                    fm.append(f"{'cover' if key == 'album-cover' else 'pdf'}: {yq(url)}")
                    if key == "pdf":
                        fm.append("third-party-files: true")
                elif why:
                    self.report["unresolved"].append((page["title"], key, why))
            else:
                fm.append(f"{key}: {yq(v)}")
        fm.append(f"notion-id: {page['notion_id']}")
        return "---\n" + "\n".join(fm) + "\n---\n\n"

    def refresh_work_notes(self):
        """Re-run the piece notes that link attached files, now that files are published.

        Only replaces a body that is still exactly what import_notes_from_export.py wrote, so edits made
        in Obsidian are never overwritten. Adds third-party-files: true to the work."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("old", os.path.join(ROOT, "scripts", "import_notes_from_export.py"))
        old = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old)
        changed, kept = [], []
        pages = [p for p in __import__("glob").glob(os.path.join(self.export, "Home", "Saxophone R*pertoire Database", "*.md"))]
        for src in sorted(pages):
            h = re.search(r"([0-9a-f]{32})\.md$", src)
            name = WORK_BY_HEX.get(h.group(1)) if h else None
            text = open(src, encoding="utf-8").read()
            raw = old.split_page(text)
            if not name or not raw or not any(
                    not re.match(r"(https?:|mailto:)", urllib.parse.unquote(m.group(3))) and not urllib.parse.unquote(m.group(3)).endswith(".md")
                    for m in LINK.finditer(raw)):
                continue
            path = os.path.join(CONTENT, "works", name + ".md")
            cur = open(path, encoding="utf-8").read()
            fm_end = cur.find("\n---", 4) + 4
            body_now = cur[fm_end:].strip()
            expected = old.convert_links(raw, [], name).strip()
            # also repair the first version of this mode, which left Notion's property lines in the body
            if body_now != expected and not (body_now.startswith("Composer:") and "Created time:" in body_now):
                kept.append(name)
                continue
            slug = re.search(r"^slug: (.+)$", cur, re.M).group(1)
            page = {"title": name, "source": os.path.relpath(src, self.export), "target": f"/works/{slug}/", "slug": slug,
                    "dir": "works", "kind": "work", "notion_id": h.group(1), "status": "import"}
            body, _, _, state = self.convert(page, "# " + name + "\n\n" + raw)  # raw has no property block
            fm = cur[:fm_end - 4].rstrip("\n")
            if state["files"] and "third-party-files" not in fm:
                fm += "\nthird-party-files: true"
            if not self.dry:
                open(path, "w", encoding="utf-8").write(fm + "\n---\n\n" + body)
            changed.append(name)
        return changed, kept

    def run(self, force):
        for r in self.rows:
            if r["status"] != "import":
                continue
            out_dir = os.path.join(CONTENT, r["dir"])
            out = os.path.join(out_dir, r["stem"] + ".md")
            if os.path.exists(out):
                cur = open(out, encoding="utf-8").read()
                ok = force and "notion-id:" in cur or PLACEHOLDER in cur
                if not ok:
                    self.report["skipped_existing"].append(out)
                    continue
            text = open(os.path.join(self.export, r["source"]), encoding="utf-8").read()
            body, props, notes, state = self.convert(r, text)
            content = self.front(r, props, notes, state, body) + body
            if not self.dry:
                os.makedirs(out_dir, exist_ok=True)
                open(out, "w", encoding="utf-8").write(content)
            self.report["written"] += 1
        for d, title in SECTION_STUBS.items():
            p = os.path.join(CONTENT, d, "_index.md")
            if not os.path.exists(p) and not self.dry:
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w", encoding="utf-8").write(f"---\ntitle: {yq(title)}\n---\n")
        return self.report


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    imp = Importer(args[0].rstrip("/"), args[1], "--dry-run" in sys.argv)
    if "--work-attachments" in sys.argv:
        changed, kept = imp.refresh_work_notes()
        print(f"Updated {len(changed)} work notes; left {len(kept)} that were edited since import: {kept}")
        for t in imp.report["skipped_big"] + imp.report["unresolved"]:
            print("  not linked:", *t)
        print(f"Copied {len(imp.report['copied'])} files, {sum(x[2] for x in imp.report['copied']) / 1e6:.1f} MB")
        return
    rep = imp.run("--force" in sys.argv)
    print(f"{'Would write' if '--dry-run' in sys.argv else 'Wrote'} {rep['written']} pages; skipped existing {len(rep['skipped_existing'])}")
    mb = sum(s for _, _, s in rep["copied"]) / 1e6
    print(f"Copied {len(rep['copied'])} files, {mb:.1f} MB")
    print(f"\nNot copied, too large ({len(rep['skipped_big'])}):")
    for t in rep["skipped_big"]:
        print("  ", *t)
    print(f"\nFlagged as outside CC BY-SA ({len(rep['flagged'])}):")
    for t in rep["flagged"]:
        print("  ", *t)
    print(f"\nLinks left as plain text ({len(rep['unresolved'])}):")
    for t in rep["unresolved"]:
        print("  ", *t)


if __name__ == "__main__":
    main()
