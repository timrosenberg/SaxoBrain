"""One-time import of the SaxoBrain catalog from the public Notion site.

Reads the Saxophone Répertoire and Composers databases through the public
saxobrain.notion.site page API and writes one Markdown file per work and per
composer into content/. Safe to rerun before launch: it overwrites generated
files. After launch, do not rerun; slugs become permanent.

Usage: python3 scripts/import_from_notion.py
"""
import collections
import difflib
import json
import re
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
API = "https://saxobrain.notion.site/api/v3/"
HDRS = {"Content-Type": "application/json", "User-Agent": "curl/8.7.1"}
SPACE = "1c3d2867-c641-49dc-8691-b7d9666a018f"
WORKS_COLL, WORKS_VIEW = "647992f2-51d5-45ab-9c06-da2cdf5aa2d8", "157a51fb-eeb2-4c78-bf18-34c27b42dc7d"
COMP_COLL, COMP_VIEW = "39478210-f6d0-4929-8fdb-31cd47a90b6c", "0e298d67-df15-4ce4-aef6-bc056750f9b2"

# Lowercase duplicate tags in Notion, merged into the capitalized option
CANON_TAGS = {"piano": "Piano", "alto saxophone": "Alto Saxophone", "soprano saxophone": "Soprano Saxophone",
              "tenor saxophone": "Tenor Saxophone", "baritone saxophone": "Baritone Saxophone"}


def post(endpoint, body):
    req = urllib.request.Request(API + endpoint, data=json.dumps(body).encode(), headers=HDRS)
    return json.load(urllib.request.urlopen(req, timeout=180))


def unwrap(rec):
    v = rec["value"]
    return v.get("value", v)


def fetch_blocks(ids, table="block"):
    out = {}
    for n in range(0, len(ids), 100):
        reqs = [{"pointer": {"table": table, "id": i, "spaceId": SPACE}, "version": -1} for i in ids[n:n + 100]]
        out.update(post("syncRecordValuesMain", {"requests": reqs})["recordMap"].get(table, {}))
    return out


def query(coll, view):
    body = {"collection": {"id": coll}, "collectionView": {"id": view},
            "loader": {"type": "reducer", "reducers": {"collection_group_results": {"type": "results", "limit": 5000}},
                       "searchQuery": "", "userTimeZone": "America/New_York"}}
    d = post("queryCollection", body)
    ids = d["result"]["reducerResults"]["collection_group_results"]["blockIds"]
    blocks = d["recordMap"].get("block", {})
    blocks.update(fetch_blocks([i for i in ids if i not in blocks]))
    schema = unwrap(fetch_blocks([coll], "collection")[coll])["schema"]
    names = {k: p["name"] for k, p in schema.items()}
    rows = []
    for i in ids:
        b = unwrap(blocks[i])
        rows.append((i, b, {names.get(k, k): v for k, v in b.get("properties", {}).items()}))
    return rows


def text(prop):
    return "".join(seg[0] for seg in (prop or []) if seg and isinstance(seg[0], str)).replace("\xa0", " ").strip()


def formats(prop, kind):
    out = []
    for seg in prop or []:
        for f in (seg[1] if len(seg) > 1 else []):
            if f[0] == kind and len(f) > 1:
                out.append(f[1])
    return out


def split_list(prop):
    return [x.strip() for x in text(prop).split(",") if x.strip()]


def fold(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if not unicodedata.combining(ch)).lower()


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", fold(s)).strip("-") or "untitled"


def safe_filename(s):
    s = s.replace(":", " -").replace("/", "-").replace("\\", "-")
    s = re.sub(r'[*"<>|?#^\[\]]', "", s)
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s[:150] or "Untitled"


def hugo_key(name):
    """Hugo treats file names as equal when they differ only in case, spaces or hyphens."""
    return re.sub(r"[\s-]+", "-", name.lower())


def unique_names(items, display):
    """File names that stay distinct for macOS and Hugo; collisions get ' 2', ' 3'."""
    seen, out = collections.Counter(), {}
    for it in items:
        base = safe_filename(display(it))
        seen[hugo_key(base)] += 1
        n = seen[hugo_key(base)]
        out[it] = base if n == 1 else f"{base} {n}"
    return out


def unique(items, key):
    seen, out = collections.Counter(), {}
    for it in items:
        k = key(it)
        seen[k] += 1
        out[it] = k if seen[k] == 1 else f"{k}-{seen[k]}"
    return out


def yq(s):
    """YAML double-quoted scalar."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_list(key, values):
    if not values:
        return [f"{key}: []"]
    return [f"{key}:"] + [f"  - {yq(v)}" for v in values]


def main():
    print("Fetching composers...")
    comp_rows = query(COMP_COLL, COMP_VIEW)
    composers = {}
    for cid, _b, pr in comp_rows:
        name = text(pr.get("Composer Name"))
        if name:
            composers[cid] = {"name": name, "nationality": split_list(pr.get("Nationality")),
                              "gender": text(pr.get("Gender")), "race": split_list(pr.get("Race"))}

    print("Fetching works...")
    work_rows = query(WORKS_COLL, WORKS_VIEW)
    works = []
    for wid, b, pr in work_rows:
        tags = []
        for t in split_list(pr.get("Instruments")):
            t = CANON_TAGS.get(t, t)
            if t not in tags:
                tags.append(t)
        purchase = formats(pr.get("Purchase"), "a")
        works.append({
            "id": wid,
            "title": text(pr.get("Title")) or "Untitled",
            "composers": [c for c in formats(pr.get("Composer"), "p") if c in composers],
            "instruments": tags,
            "year": text(pr.get("Year of Study")),
            "arranger": split_list(pr.get("Arranger / Edition")),
            "publisher": split_list(pr.get("Publisher")),
            "streaming": text(pr.get("Streaming")),
            "purchase": [u for u in purchase if "alexanderstreet" not in u],
            "library": [u for u in purchase if "alexanderstreet" in u],
            "download": formats(pr.get("Download"), "a"),
            "records": formats(pr.get("Records"), "p"),
            "studied": text(pr.get("Studied/Performed")) == "Yes",
            "want": text(pr.get("Want to Play (again)")) == "Yes",
            "added": datetime.fromtimestamp(b.get("created_time", 0) / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
        })

    # When two composer records share a name, the one with more works keeps the plain file name and address
    work_count = collections.Counter(c for w in works for c in w["composers"])
    comp_ids = sorted(composers, key=lambda c: (-work_count[c], c))
    comp_file = unique_names(comp_ids, lambda c: composers[c]["name"])
    comp_slug = unique(comp_ids, lambda c: slugify(composers[c]["name"]))

    def lead_name(w):
        return composers[w["composers"][0]]["name"] if w["composers"] else "Unknown"

    VOICES = {"ss": "Soprano", "as": "Alto", "ts": "Tenor", "bs": "Baritone"}

    def strip_composer(w):
        """Drop a trailing '(Composer)' disambiguator, a Notion-era convention.
        '(Martin, As)' becomes '(Alto)'; '(Challan, H.)' and misspellings like '(Selmer-Collery)'
        are dropped. Anything else in parentheses, like '(after Chopin)', is kept."""
        m = re.search(r"\s*\(([^()]+)\)\s*$", w["title"])
        if not m:
            return w["title"]
        name_words = set()
        for c in w["composers"]:
            name_words.update(fold(composers[c]["name"]).replace("-", " ").replace(".", " ").split())
        parts = [x.strip() for x in m.group(1).split(",")]
        words = [x for x in fold(parts[0]).replace("-", " ").replace(".", " ").split() if len(x) > 2]
        close = lambda x: any(difflib.SequenceMatcher(None, x, n).ratio() >= 0.8 for n in name_words)
        if not words or not all(close(x) for x in words):
            return w["title"]
        voices = []
        for extra in parts[1:]:
            if re.fullmatch(r"[A-Z]\.?", extra):
                continue
            keys = [k.strip().lower() for k in extra.split("/")]
            if not all(k in VOICES for k in keys):
                return w["title"]
            voices.append("/".join(VOICES[k] for k in keys))
        base = w["title"][:m.start()].rstrip()
        return f"{base} ({', '.join(voices)})" if voices else base

    stripped = 0
    for w in works:
        new_title = strip_composer(w)
        if new_title != w["title"]:
            w["notion_title"], w["title"] = w["title"], new_title
            stripped += 1
    print(f"Removed the composer-in-parentheses from {stripped} titles.")

    idx = list(range(len(works)))
    work_file = unique_names(idx, lambda i: f"{lead_name(works[i])} - {works[i]['title']}")
    work_slug = unique(idx, lambda i: slugify(f"{lead_name(works[i])} {works[i]['title']}"))

    for d in ("works", "composers"):
        (CONTENT / d).mkdir(parents=True, exist_ok=True)
        for f in (CONTENT / d).glob("*.md"):
            if f.name != "_index.md":
                f.unlink()

    comp_names_on_disk = comp_file

    def link_for(cid):
        target, disp = comp_names_on_disk[cid], composers[cid]["name"]
        return f"[[{target}]]" if target == disp else f"[[{target}|{disp}]]"

    for cid in comp_ids:
        c = composers[cid]
        lines = ["---", f"title: {yq(c['name'])}", f"slug: {comp_slug[cid]}"]
        lines += yaml_list("nationality", c["nationality"])
        lines.append(f"gender: {yq(c['gender'])}" if c["gender"] else "gender: ")
        lines += yaml_list("race", c["race"])
        lines += ["aliases: []", "---", ""]
        (CONTENT / "composers" / f"{comp_names_on_disk[cid]}.md").write_text("\n".join(lines), encoding="utf-8")

    id_map = {"works": {}, "composers": {cid: comp_names_on_disk[cid] for cid in comp_ids}}
    for i, w in enumerate(works):
        fname = work_file[i]
        lines = ["---", f"title: {yq(w['title'])}", f"slug: {work_slug[i]}"]
        lines += yaml_list("composer", [link_for(c) for c in w["composers"]])
        lines += yaml_list("instruments", w["instruments"])
        lines.append(f"year-of-study: {yq(w['year'])}" if w["year"] else "year-of-study: ")
        if w["arranger"]:
            lines += yaml_list("arranger-edition", w["arranger"])
        if w["publisher"]:
            lines += yaml_list("publisher", w["publisher"])
        lines.append(f"streaming: {yq(w['streaming'])}" if w["streaming"] else "streaming: ")
        lines += yaml_list("purchase", w["purchase"])
        if w["download"]:
            lines += yaml_list("download", w["download"])
        if w["library"]:
            lines += yaml_list("library-recording", w["library"])
        if w["studied"]:
            lines.append("studied-performed: true")
        if w["want"]:
            lines.append("want-to-play: true")
        lines += [f"added: {w['added']}", "aliases: []", "---", ""]
        (CONTENT / "works" / f"{fname}.md").write_text("\n".join(lines), encoding="utf-8")
        id_map["works"][w["id"]] = {"file": fname, "records": w["records"], **({"notion_title": w["notion_title"]} if "notion_title" in w else {})}

    (ROOT / "scripts" / "migration" / "notion-ids.json").write_text(
        json.dumps(id_map, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {len(works)} works and {len(comp_ids)} composers.")
    print("Works without a composer:", sum(1 for w in works if not w["composers"]))


if __name__ == "__main__":
    main()
