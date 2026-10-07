#!/usr/bin/env python3
"""Collect composer photos into static/media/composers/ so the site never hotlinks (no link rot).

Sources, in order, for composers whose `photo:` field is empty:
  1. the photo Tim set on the composer's Notion page (page icon, else the first image in the page);
  2. the Wikidata portrait (P18) from Wikimedia Commons, with the photographer and license as `photo-credit`.
A photo given by hand wins over both:  --add "Composer File Name" URL [--credit "Text"]

Each photo is resized to at most 600 px and saved as /media/composers/<slug>.jpg. `photo-source` keeps the
original address so the photo can be traced or replaced. Existing photos are never replaced.

Usage: python3 scripts/composer_photos.py [--notion] [--wikidata] [--credits] [--add NAME URL [--credit TEXT]]
"""
import html, json, re, subprocess, sys, tempfile, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "static/media/composers"
UA = "SaxoBrain composer photos (https://github.com/timrosenberg/SaxoBrain)"
FIELDS = ("photo", "photo-credit", "photo-source")


def front(path):
    s = path.read_text()
    return s, s.index("\n---", 3)


def field(path, k):
    s, end = front(path)
    m = re.search(rf"^{k}:[ \t]*(.*)$", s[:end], re.M)
    return m.group(1).strip().strip('"') if m else None


def ensure_fields(path):
    """Add empty photo fields before `aliases:` if the file does not have them yet."""
    s, end = front(path)
    fm = s[:end]
    missing = [k for k in FIELDS if not re.search(rf"^{k}:", fm, re.M)]
    if missing:
        fm = fm.replace("\naliases:", "".join(f"\n{k}: " for k in missing) + "\naliases:", 1)
        path.write_text(fm + s[end:])


def set_fields(path, values):
    s, end = front(path)
    fm = s[:end]
    for k, v in values.items():
        v = json.dumps(v, ensure_ascii=False) if isinstance(v, str) else v
        fm, n = re.subn(rf"^{k}:[ \t]*.*$", lambda m: f"{k}: {v}", fm, count=1, flags=re.M)
        assert n == 1, (path, k)
    path.write_text(fm + s[end:])


def download(url, slug):
    """Fetch an image, convert it to a JPEG at most 600 px on the long side. Returns the site path or None."""
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{slug}.jpg"
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@~!$'()*[]")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            data = r.read()
    except Exception as e:
        print(f"  could not download for {slug}: {e}")
        return None
    with tempfile.NamedTemporaryFile(suffix=Path(urllib.parse.urlparse(url).path).suffix or ".img") as t:
        t.write(data)
        t.flush()
        ok = subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", "600", t.name, "--out", str(dest)],
                            capture_output=True).returncode == 0
        if not ok and data[:4] == b"RIFF":  # WebP that sips cannot read
            ok = subprocess.run(["dwebp", t.name, "-o", str(dest) + ".png"], capture_output=True).returncode == 0 and \
                 subprocess.run(["sips", "-s", "format", "jpeg", "-Z", "600", str(dest) + ".png", "--out", str(dest)],
                                capture_output=True).returncode == 0
            Path(str(dest) + ".png").unlink(missing_ok=True)
    if not ok or not dest.exists():
        print(f"  not an image I can read for {slug}: {url[:80]}")
        dest.unlink(missing_ok=True)
        return None
    return f"/media/composers/{slug}.jpg"


def composers():
    """Composer files, minus those whose photo a person has ruled out (scripts/migration/photo-skip.json)."""
    skip = set(json.loads((ROOT / "scripts/migration/photo-skip.json").read_text())["composers"])
    out = {}
    for f in sorted((ROOT / "content/composers").glob("*.md")):
        if f.name != "_index.md" and f.stem not in skip:
            ensure_fields(f)
            out[f.stem] = f
    return out


def from_notion(files):
    import import_from_notion as n
    ids = json.loads((ROOT / "scripts/migration/notion-ids.json").read_text())["composers"]
    rows = n.query(n.COMP_COLL, n.COMP_VIEW)
    picks = {}
    child_ids = [c for _, b, _ in rows for c in b.get("content", [])]
    blocks = n.fetch_blocks(child_ids)
    for pid, b, _ in rows:
        name = ids.get(pid)
        name = name.get("file") if isinstance(name, dict) else name
        if not name or name not in files:
            continue
        icon = b.get("format", {}).get("page_icon", "")
        if icon.startswith("http"):
            picks[name] = (icon, pid)
            continue
        for c in b.get("content", []):
            bb = n.unwrap(blocks[c]) if c in blocks else {}
            if bb.get("type") == "image":
                src = (bb.get("properties", {}).get("source") or [[""]])[0][0] or bb.get("format", {}).get("display_source", "")
                if src:
                    picks[name] = (src, c)
                    break
    done = 0
    for name, (src, block) in sorted(picks.items()):
        f = files[name]
        if field(f, "photo"):
            continue
        url = src
        if "prod-files-secure" in src or "secure.notion-static" in src or src.startswith("attachment:"):
            r = n.post("getSignedFileUrls", {"urls": [{"url": src, "permissionRecord": {"table": "block", "id": block, "spaceId": n.SPACE}}]})
            url = (r.get("signedUrls") or [None])[0]
            src = "Notion upload"
            if not url:
                print(f"  no signed address for {name}")
                continue
        path = download(url, field(f, "slug"))
        if path:
            set_fields(f, {"photo": path, "photo-source": src})
            done += 1
    print(f"Notion: {len(picks)} composers had a photo; saved {done} new")


def commons_info(fname):
    """Photographer and license of a Wikimedia Commons file, plus its thumbnail and description page."""
    info = json.load(urllib.request.urlopen(urllib.request.Request(
        "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": "File:" + fname, "prop": "imageinfo", "iiprop": "url|extmetadata",
            "iiurlwidth": 600, "format": "json", "formatversion": 2}), headers={"User-Agent": UA}), timeout=40))
    ii = info["query"]["pages"][0].get("imageinfo", [{}])[0]
    meta = ii.get("extmetadata", {})
    strip = lambda k: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", meta.get(k, {}).get("value", "")))).strip()
    credit = ", ".join(x for x in (artist_name(strip("Artist")), strip("LicenseShortName")) if x)
    return ii, (credit + ", via Wikimedia Commons") if credit else ""


def artist_name(a):
    """Commons artist fields often repeat themselves ("Unknown authorUnknown author") or say nobody is known."""
    if re.search(r"unknown|anonym|unattributed", a, re.I):
        return "Unknown photographer"
    half = len(a) // 2
    if len(a) % 2 == 0 and a[:half] == a[half:]:
        a = a[:half]
    return a[:120]


def credit_commons(files):
    """Credit photos that came from Wikimedia (e.g. Tim's Notion links to upload.wikimedia.org)."""
    done = 0
    for name, f in sorted(files.items()):
        src = field(f, "photo-source") or ""
        if field(f, "photo-credit") or "upload.wikimedia.org" not in src:
            continue
        parts = urllib.parse.unquote(urllib.parse.urlparse(src).path).split("/")
        fname = parts[-2] if "/thumb/" in src else parts[-1]
        ii, credit = commons_info(fname)
        if credit:
            set_fields(f, {"photo-credit": credit, "photo-source": ii.get("descriptionurl", src)})
            done += 1
        else:
            print(f"  no Commons record for {name}: {fname}")
    print(f"Commons credits added: {done}")


def from_wikidata(files):
    import wikidata_composers as w
    todo = {name: f for name, f in files.items() if not field(f, "photo") and (field(f, "wikidata") or "").startswith("Q")}
    ents = w.entities([field(f, "wikidata") for f in todo.values()], "claims")
    done = 0
    for name, f in sorted(todo.items()):
        claims = ents.get(field(f, "wikidata"), {}).get("claims", {}).get("P18", [])
        claims = [c for c in claims if c["mainsnak"].get("datavalue") and c.get("rank") != "deprecated"]
        if not claims:
            continue
        claims.sort(key=lambda c: c.get("rank") != "preferred")
        ii, credit = commons_info(claims[0]["mainsnak"]["datavalue"]["value"])
        path = download(ii.get("thumburl") or ii.get("url"), field(f, "slug"))
        if path:
            set_fields(f, {"photo": path, "photo-credit": credit, "photo-source": ii.get("descriptionurl", "")})
            done += 1
    print(f"Wikidata: {len(todo)} linked composers without a photo; saved {done}")


def main():
    files = composers()
    args = sys.argv[1:]
    if "--add" in args:
        i = args.index("--add")
        name, url = args[i + 1], args[i + 2]
        credit = args[args.index("--credit") + 1] if "--credit" in args else ""
        f = files[name]
        path = download(url, field(f, "slug"))
        if path:
            set_fields(f, {"photo": path, "photo-credit": credit, "photo-source": url})
            print(f"saved {path}")
    if "--notion" in args:
        from_notion(files)
    if "--wikidata" in args:
        from_wikidata(files)
    if "--credits" in args or "--notion" in args:
        credit_commons(files)


if __name__ == "__main__":
    main()
