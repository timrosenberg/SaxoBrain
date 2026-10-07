"""Round 2: numbered years, alto and tenor merged (alto first), no jazz, full catalog for the planner."""
import json, sys, re, glob, os
sys.argv = [sys.argv[0], sys.argv[1], "/dev/null"]
ROOT = sys.argv[1]
import importlib.util
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "build_data.py"), encoding="utf-8").read()
src = src[: src.index("json.dump(")]  # reuse parsing, skip writing
ns = {"__name__": "bd"}
exec(compile(src, "build_data.py", "exec"), ns)
years = ns["years"]
work = ns["work"]
works = ns["works"]
split_fm, field = ns["split_fm"], ns["field"]

NAMES = {1: ("first-year", "First Year"), 2: ("second-year", "Second Year"), 3: ("third-year", "Third Year"), 4: ("fourth-year", "Fourth Year")}
LV = {"Pre-college": "pre", "First Year": "1", "Second-Year": "2", "Third Year": "3", "Fourth Year": "4", "Advanced": "adv"}
key = lambda p: p["url"] + "#" + p["title"]
slug_of = lambda u: u.rstrip("/").split("/")[-1]

out = []
for y in years:
    y["id"], y["name"] = NAMES[y["n"]]
    y.pop("jazz", None)
    y["listening"] = [g for g in y["listening"] if "jazz" not in g["group"].lower()]
    alto, tenor = y["rep"]["alto"], y["rep"]["tenor"]
    tenor_keys = {key(p) for c in tenor["categories"] for p in c["pieces"]}
    alto_keys = {key(p) for c in alto["categories"] for p in c["pieces"]}
    cats = []
    for c in alto["categories"]:
        cats.append({"name": c["name"], "alto": [dict(p, both=key(p) in tenor_keys) for p in c["pieces"]], "tenor": []})
    for c in tenor["categories"]:
        target = next((x for x in cats if x["name"] == c["name"]), None)
        if not target:
            target = {"name": c["name"], "alto": [], "tenor": []}
            cats.append(target)
        target["tenor"] += [p for p in c["pieces"] if key(p) not in alto_keys]
    for c in cats:
        for p in c["alto"] + c["tenor"]:
            p["s"] = slug_of(p["url"])
            p["l"] = LV.get(p.pop("level", ""), "")
            p.pop("parts", None)
    y["intro"] = alto["intro"]
    y["cats"] = cats
    y.pop("rep")
    y["more"]["adv"] = y.pop("moreAdv")
    out.append(y)

# whole catalog, compact, for the planner search
SAXES = [("Soprano", "S"), ("Alto", "A"), ("Tenor", "T"), ("Baritone", "B"), ("Bass", "Bs"), ("Any", "Any")]
catalog = []
for name in sorted(works):
    wf, _ = split_fm(works[name])
    inst = field(wf, "instruments") or []
    w = work(name)
    catalog.append({
        "s": field(wf, "slug"), "t": w["title"], "c": w["composer"], "l": LV.get(w["level"], ""),
        "i": [code for s, code in SAXES if f"{s} Saxophone" in inst], "li": w["listen"], "b": w["buy"],
    })
json.dump({"site": ns["SITE"], "years": out, "catalog": catalog}, open(os.path.join(here, "data2.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(catalog), "works;", [(y["name"], [(c["name"], len(c["alto"]), len(c["tenor"])) for c in y["cats"]]) for y in out])
