"""Draft the mapping from every non-catalog Notion page to its place on the new site.

Usage: python3 -I scripts/migration/build_page_map.py <export folder>
Writes scripts/migration/page-map.csv. Edit the CSV (target, slug, status) before importing.

Status values:
  import   public page, goes to the target address
  view     a Notion database view; Hugo builds it from the catalog, nothing to import
  private  personal material, never published
  ask      not linked from the public Home page; Tim decides
"""
import csv
import glob
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "page-map.csv")
HEX = re.compile(r"\s([0-9a-f]{32})\.md$")


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:70].rstrip("-")


# Pages Tim listed on the Home page under each heading (title -> section)
COMPETITIONS = re.compile(r"^(19|20)\d\d .*(Competition|Gaudeamus)")
COLLEGES = {"UNCG Alto Saxophone Repertoire", "UNCG Tenor Saxophone Repertoire", "UCF Repertoire Lists",
            "Ohio University Saxophone Repertoire", "Ithaca College Selected Repertoire (Mauk)"}
PROGRAMS = {"2021 Interlochen Saxophone Recital Program", "2020 NASA Sessions"}
VIEWS = re.compile(r"^(Pre-College|First-Year|Second-Year|Third-Year|Fourth-Year|Advanced) Répertoire$|"
                   r"^(Soprano|Alto|Tenor|Baritone) Saxophone Répertoire$|^Composers Database$|"
                   r"^Saxophone Répertoire Database$|^Saxophone Recordings$|^Home views$|^Home$|^Works Published Adolphe Sax$")
PRIVATE_TOP = {"People", "Saxophone Job Applications", "Untitled", "My Tasks", "Pieces I Know",
               "Pieces from Saxophone Database to Play", "Library", "New Pieces to Play"}
RECORDINGS_EXTRA = {"Listening List 2019": "recordings", "Required Listening for Saxophone Students": "recordings"}
ARTICLES = {  # linked from Home under Articles
    "Scales: French Style by Joel Diegert", "What to buy? A Guide for the Beginning College Saxophonist",
    "How to Become a Better Teacher to Yourself by Noa Kageyama", "Tuning for Variable Pitch Instruments",
    "Jaw Vibrato Exercises", "How to Put Yourself on the Path to Bulletproof Intonation",
    "Altissimo Crash Course: Beginner through Advanced", "Introduction to Saxophone Acoustics",
    "Building a Saxophone Quartet Library by Heidi Radtke",
    "Saxophone Materials and Finishes: How Each Effects the Sound", "How To Fix Green & Old Rubber Mouthpieces",
    "Teaching Students How to Practice by Steven Mauk",
    "Teaching Students Attention to Details by Steven Mauk", "Four Steps to Musical Maturity by Steven Mauk",
    "8 Practice Hacks by Noa Kageyama", "Jazz Practicing Guide by Brent Vaartstra", "Quality Practice by Susan Williams",
}
ASK_TOP = {"Bauzin Works for Saxophone", "Every Sax Case Needs", "Jazz Standards", "Jazz Tunes",
           "Program Notes for Hamiltonian Cycle: Saxophone by Robert Mor", "Rosenberg's Required Saxophone Repertoire",
           "Steve Neff’s Real Book", "Vibrato Examples", "Resources", "My Saxophone Links",
           "Saxophone Case Materials Shopping List"}


SECTION_INDEX = {"Saxophone Curriculum", "Saxophone Reeds", "Saxophone Mouthpieces",
                 "Etudes & Studies for Teaching", "Altissimo Fingering Charts", "Required Reading for Saxophone Students",
                 "Required Listening for Saxophone Students"}


def place(rel, title):
    """Return (status, target section path, kind)."""
    top = rel.split(os.sep)[0] if rel != "." else ""
    if VIEWS.match(title):
        return "view", "", "database view"
    if rel.startswith("Saxophone Job Applications") or top in PRIVATE_TOP or title in PRIVATE_TOP:
        return "private", "", "personal"
    if rel.startswith("Home/Saxophone Curriculum") or title == "Saxophone Curriculum":
        return "import", "curriculum", "curriculum"
    if rel.startswith("Home/Saxophone Recordings"):
        return "import", "recordings", "album"
    if title in RECORDINGS_EXTRA:
        return "import", "recordings", "listening list"
    if title == "Required Reading for Saxophone Students":
        return "import", "reading", "reading list"
    if title in ARTICLES:
        return "import", "reading", "article (check author)"
    if COMPETITIONS.match(title):
        return "import", "lists/competitions", "competition list"
    if title in COLLEGES:
        return "import", "lists/colleges", "college list"
    if title in PROGRAMS:
        return "import", "lists/programs", "recital program"
    if rel.startswith("Home/Saxophone Reeds") or title == "Saxophone Reeds":
        return "import", "resources/equipment/reeds", "equipment"
    if rel.startswith("Home/Saxophone Mouthpieces") or title == "Saxophone Mouthpieces":
        return "import", "resources/equipment/mouthpieces", "equipment"
    if title in ("Saxophone Brands and Models", "Saxophone Ligatures", "Saxophone Neck Straps & Harnesses"):
        return "import", "resources/equipment", "equipment"
    if rel.startswith("Home/Etudes") or title == "Etudes & Studies for Teaching":
        return "import", "resources/etudes", "etude list"
    if rel.startswith("Home/Altissimo") or title in ("Altissimo Fingering Charts", "Steve Lacy’s Soprano Altissimo Fingerings"):
        return "import", "resources/altissimo", "fingering chart"
    if title in ("The Scale Series", "The Ferling Project", "Saxophone Music Publishers"):
        return "import", "resources", "resource"
    if title in ASK_TOP or top in ASK_TOP:
        return "ask", "", "not linked from Home"
    return "ask", "", "unclassified"


def main(export):
    skip = ("Répertoire Database", "Composers Database")
    rows, used = [], set()
    for dp, _, fns in os.walk(export):
        rel = os.path.relpath(dp, export)
        if any(x in rel for x in skip):
            continue
        for f in sorted(fns):
            if not f.endswith(".md"):
                continue
            text = open(os.path.join(dp, f), encoding="utf-8").read()
            title = text.split("\n", 1)[0].lstrip("# ").strip()
            m = HEX.search(f)
            status, sect, kind = place(rel, title)
            slug, target = "", ""
            if status == "import":
                slug = slugify(re.sub(r"\s+by\s+[A-Z].*$", "", title)) or slugify(title)
                if f"{sect}/{slug}" in used:
                    slug = slugify(title)
                used.add(f"{sect}/{slug}")
                target = f"/{sect}/{slug}/"
                if title in SECTION_INDEX:  # the page that introduces a whole section
                    slug, target = "", f"/{sect}/"
            ext = re.findall(r"\]\((https?://[^)\s]+)", text)
            rows.append({
                "status": status, "target": target, "slug": slug, "title": title, "kind": kind,
                "notion_id": m.group(1) if m else "", "source": os.path.join(rel, f),
                "chars": len(text), "images": text.count("!["), "external_links": len(ext),
                "first_link": ext[0] if ext else "",
            })
    rows.sort(key=lambda r: (r["status"], r["target"], r["title"]))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    c = Counter((r["status"], r["target"].rsplit("/", 2)[0] if r["target"] else "") for r in rows)
    for k, v in sorted(c.items()):
        print(f"{k[0]:8} {k[1]:35} {v}")
    print(len(rows), "pages ->", OUT)


if __name__ == "__main__":
    main(glob.glob(os.path.join(sys.argv[1], ""))[0].rstrip("/"))
