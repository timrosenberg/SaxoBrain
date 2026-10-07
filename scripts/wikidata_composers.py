#!/usr/bin/env python3
"""Find each composer on Wikidata and fill in `wikidata`, `born` and `died`.

Only composers whose `wikidata:` field is empty are looked up. A match is applied only when exactly one
Wikidata person has the composer's exact name (ignoring accents), works in music, and (when we record a
nationality) holds a matching citizenship. Everything else is written to scripts/migration/wikidata-review.json
for a person to decide; their choices go in scripts/migration/wikidata-overrides.json. Existing `born`/`died` values are never overwritten.

Usage: python3 scripts/wikidata_composers.py [--dry-run]
"""
import json, re, sys, time, unicodedata, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "scripts/migration/wikidata-review.json"
# Choices a person made after reviewing: composer title -> Wikidata ID, applied as is; null = no match (ruled out).
OVERRIDES = ROOT / "scripts/migration/wikidata-overrides.json"
API = "https://www.wikidata.org/w/api.php"
UA = "SaxoBrain composer dates (https://github.com/timrosenberg/SaxoBrain)"
MUSIC = re.compile(r"compos|music|saxophon|pianist|conduct|organist|violin|viol|clarinet|flaut|flut|trumpet|trombon|"
                   r"guitar|songwriter|arranger|bandleader|cellist|singer|percussion|bassist|horn|obo|bassoon|harp|"
                   r"lutenist|harpsichord|tubist|euphonium|drummer|vocalist|jazz", re.I)


def fold(s):
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if not unicodedata.combining(c)).lower().replace("-", " ")).strip()


def get(params):
    params = {**params, "format": "json", "formatversion": "2"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            time.sleep(2 + attempt * 3)
    raise RuntimeError("Wikidata did not answer: " + str(params))


def entities(ids, props="labels|aliases|claims", languages="en"):
    out = {}
    ids = list(dict.fromkeys(ids))
    for n in range(0, len(ids), 50):
        params = {"action": "wbgetentities", "ids": "|".join(ids[n:n + 50]), "props": props}
        if languages:
            params["languages"] = languages
        out.update(get(params)["entities"])
    return out


def claim_ids(e, p):
    return [c["mainsnak"]["datavalue"]["value"]["id"] for c in e.get("claims", {}).get(p, [])
            if c["mainsnak"].get("datavalue") and c.get("rank") != "deprecated"]


def year(e, p):
    """Year from a date claim, if Wikidata knows it to the year or better. Preferred rank wins."""
    cs = [c for c in e.get("claims", {}).get(p, []) if c["mainsnak"].get("datavalue") and c.get("rank") != "deprecated"]
    cs.sort(key=lambda c: c.get("rank") != "preferred")
    for c in cs:
        v = c["mainsnak"]["datavalue"]["value"]
        if v.get("precision", 0) >= 9:
            m = re.match(r"([+-])(\d+)-", v["time"])
            if m and m.group(1) == "+":
                return int(m.group(2))
    return None


def names(e):
    """Every label and alias in every language: many composers have only a French or German label."""
    out = {l["value"] for l in e.get("labels", {}).values()}
    out.update(a["value"] for al in e.get("aliases", {}).values() for a in al)
    return {fold(n) for n in out}


def read_composers():
    rows = []
    for f in sorted((ROOT / "content/composers").glob("*.md")):
        if f.name == "_index.md":
            continue
        s = f.read_text()
        fm = s[3:s.index("\n---", 3)]
        val = lambda k: (re.search(rf"^{k}:[ \t]*(.*)$", fm, re.M) or [None, ""])[1].strip().strip('"')
        nat = re.search(r"^nationality:\n((?:  - .*\n?)*)", fm, re.M)
        nats = [re.sub(r"^[^A-Za-z]+", "", x.strip()[2:].strip('"')) for x in nat.group(1).splitlines()] if nat else []
        rows.append({"file": f, "title": val("title"), "nat": nats, "born": val("born"), "died": val("died"), "wikidata": val("wikidata")})
    return rows


def set_fields(path, fields):
    s = path.read_text()
    end = s.index("\n---", 3)
    fm = s[:end]
    for k, v in fields.items():
        fm, n = re.subn(rf"^{k}:[ \t]*$", f"{k}: {v}", fm, count=1, flags=re.M)
        assert n == 1, (path, k)
    path.write_text(fm + s[end:])


def main():
    dry = "--dry-run" in sys.argv
    todo = [c for c in read_composers() if not c["wikidata"]]
    print(f"{len(todo)} composers without a Wikidata ID")

    overrides = json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    cands = {}
    for i, c in enumerate(todo):
        if c["title"] in overrides:
            cands[c["title"]] = [overrides[c["title"]]] if overrides[c["title"]] else []
            continue
        r = get({"action": "wbsearchentities", "search": c["title"], "language": "en", "type": "item", "limit": 15})
        cands[c["title"]] = [x["id"] for x in r.get("search", [])]
        if i % 100 == 99:
            print(f"  searched {i + 1}")
    ents = entities([q for ids in cands.values() for q in ids], languages=None)
    occ = entities({o for e in ents.values() for o in claim_ids(e, "P106")}, "labels")
    countries = entities({o for e in ents.values() for o in claim_ids(e, "P27")}, "labels|claims")
    occ_label = {k: v.get("labels", {}).get("en", {}).get("value", "") for k, v in occ.items()}

    def nat_words(q):
        e = countries.get(q, {})
        words = {fold(e.get("labels", {}).get("en", {}).get("value", ""))}
        words.update(fold(c["mainsnak"]["datavalue"]["value"]["text"]) for c in e.get("claims", {}).get("P1549", [])
                     if c["mainsnak"].get("datavalue") and c["mainsnak"]["datavalue"]["value"].get("language") == "en")
        return words

    applied, review = [], []
    for c in todo:
        want = fold(c["title"])
        people = []
        for q in cands[c["title"]]:
            e = ents.get(q, {})
            if "Q5" not in claim_ids(e, "P31") or want not in names(e):
                continue
            jobs = [occ_label.get(o, "") for o in claim_ids(e, "P106")]
            if not any(MUSIC.search(j) for j in jobs):
                continue
            citizen = set().union(*[nat_words(x) for x in claim_ids(e, "P27")]) if claim_ids(e, "P27") else set()
            people.append({"qid": q, "born": year(e, "P569"), "died": year(e, "P570"), "jobs": jobs[:4],
                           "nat_ok": (not c["nat"]) or any(fold(n) in citizen for n in c["nat"]) if citizen else None})
        entry = {"composer": c["title"], "nationality": c["nat"], "candidates": people}
        good = [p for p in people if p["nat_ok"] is not False]
        if c["title"] in overrides and not overrides[c["title"]]:
            continue
        if c["title"] in overrides:
            e = ents[overrides[c["title"]]]
            people = [{"qid": overrides[c["title"]], "born": year(e, "P569"), "died": year(e, "P570")}]
        if c["title"] in overrides or (len(people) == 1 and people[0]["nat_ok"] is True):
            p = people[0]
            fields = {"wikidata": p["qid"]}
            if p["born"] and not c["born"]:
                fields["born"] = p["born"]
            if p["died"] and not c["died"]:
                fields["died"] = p["died"]
            if not dry:
                set_fields(c["file"], fields)
            applied.append({"composer": c["title"], **fields})
        else:
            entry["why"] = ("no musician with this exact name" if not people else
                            "several possible people" if len(good) > 1 else
                            "nationality does not match" if not good else "no citizenship recorded to confirm")
            review.append(entry)

    if not dry:
        REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=1) + "\n")
    print(f"applied {len(applied)}; {len(review)} for review"
          f" ({', '.join(f'{k}: {v}' for k, v in sorted(__import__('collections').Counter(r['why'] for r in review).items()))})")
    return applied, review


if __name__ == "__main__":
    main()
