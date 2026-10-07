"""Build curriculum mockup data (JSON) from the SaxoBrain content files.
Solo repertoire is parsed from content/curriculum/*; everything that lives on the
Notion-era index page (technique, etudes, jazz, reading, listening) is transcribed here."""
import re, glob, os, sys, json

ROOT = sys.argv[1]
OUT = sys.argv[2]
SITE = "https://timrosenberg.github.io/SaxoBrain"


def split_fm(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", t, re.S)
    return m.group(1), m.group(2)


def field(f, k):
    m = re.search(r"^%s:[ ]*(.*)$" % re.escape(k), f, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v and v != "[]":
        return v.strip('"')
    out = []
    for line in f[m.end():].split("\n")[1:]:
        if line.startswith("  - "):
            out.append(line[4:].strip().strip('"'))
        else:
            break
    return out or None


works = {os.path.basename(p)[:-3]: p for p in glob.glob(ROOT + "/content/works/*.md")}
comps = {os.path.basename(p)[:-3]: p for p in glob.glob(ROOT + "/content/composers/*.md")}


def composer_name(wf):
    c = field(wf, "composer") or []
    if not c:
        return ""
    names = []
    for x in c:
        x = x.strip("[]")
        file, _, disp = x.partition("|")
        if file in comps:
            cf, _ = split_fm(comps[file])
            names.append(field(cf, "title") or file)
        else:
            names.append(disp or file)
    return ", ".join(names)


def work(name):
    wf, body = split_fm(works[name])
    inst = field(wf, "instruments") or []
    purchase = field(wf, "purchase") or []
    download = field(wf, "download") or []
    return {
        "title": field(wf, "title"),
        "composer": composer_name(wf),
        "url": f"{SITE}/works/{field(wf, 'slug')}/",
        "listen": field(wf, "streaming") or "",
        "buy": purchase[0] if purchase else "",
        "free": download[0] if download else "",
        "solo": "Unaccompanied" in inst,
        "level": field(wf, "year-of-study") or "",
    }


# Excerpts from collections: written by hand from the curriculum pages.
TEAL = "Unknown - Solos for the Alto Saxophone Player"
BACH = "Johann Sebastian Bach - Bach for the Saxophone"
EXCERPTS = {
    "Rondo in D": dict(composer="Mozart", src=TEAL, srcnote="Teal, No. 11", listen="https://song.link/i/1452241276"),
    "Nocturne": dict(composer="Frédéric Chopin", src=TEAL, srcnote="Teal, No. 3", note="a.k.a. Nocturne No. 20 in C-sharp minor", listen="https://song.link/i/1452229840"),
    "Intermezzo": dict(composer="Granados", src=TEAL, srcnote="Teal, No. 6", listen="https://song.link/us/i/330153235"),
}
BACH_ITEMS = [
    ("Partita No. 1 in B minor for violin", "3–8"),
    ("Sonata No. 2 in A minor for violin: Allegro", "10"),
    ("Partita No. 2 in D minor for violin: Allemande and Corrente", "11 and 12"),
    ("Sonata No. 3 in C for violin: Allegro assai", "16"),
    ("Suite No. 1 in G for cello", "21–26"),
    ("Suite No. 2 in D minor for cello", "27–32"),
]


def excerpt(title, composer, src, srcnote, note="", listen=""):
    w = work(src)
    return {
        "title": title, "composer": composer, "url": w["url"], "listen": listen,
        "buy": w["buy"], "free": "", "solo": w["solo"], "note": note,
        "from": {"title": w["title"], "url": w["url"], "where": srcnote},
    }


def parse_rep(fname):
    fm, body = split_fm(f"{ROOT}/content/curriculum/{fname}.md")
    intro = []
    cats = []
    for line in body.split("\n"):
        h = re.match(r"^# (.*)", line)
        if h:
            cats.append({"name": h.group(1).strip(), "pieces": []})
            continue
        if not cats:
            s = line.strip()
            if s and s != "---":
                intro.append(s)
            continue
        if not line.startswith("- "):
            continue
        links = [l.split("|")[0] for l in re.findall(r"\[\[([^\]]+)\]\]", line)]
        wl = [l for l in links if l in works]
        if TEAL in wl:
            key = re.search(r"\*\*\*(.+?)\*\*\*", line).group(1)
            cats[-1]["pieces"].append(excerpt(key, src=TEAL, **{k: v for k, v in EXCERPTS[key].items() if k != "src"}))
            continue
        if BACH in wl and "Six Suites" not in line:
            t = re.search(r"\*([^*\[]+)\*", line).group(1).replace("\xa0", " ")
            for title, nums in BACH_ITEMS:
                if title.split(":")[0].split(" for ")[0].replace("Sonanta", "Sonata") in t.replace("Sonanta", "Sonata"):
                    cats[-1]["pieces"].append(excerpt(title, "Johann Sebastian Bach", BACH, f"Caravan, {nums}"))
                    break
            continue
        ws = [work(w) for w in wl]
        p = dict(ws[0])
        if len(ws) > 1:
            p["title"] = " & ".join(w["title"] for w in ws)
            p["parts"] = ws
            p["listen"] = next((w["listen"] for w in ws if w["listen"]), "")
        tail = line[line.rfind("]]") + 2:]
        m = re.search(r"\(([^)]*)\)", tail)
        p["note"] = m.group(1).replace(", and", " and") if m else ""
        cats[-1]["pieces"].append(p)
    return {"intro": intro, "categories": cats}


def etude(name, extra=None):
    w = work(name)
    d = {"title": w["title"], "composer": w["composer"], "url": w["url"], "buy": w["buy"]}
    if extra:
        d.update(extra)
    return d


R = lambda slug: f"{SITE}/reading/{slug}/"
REC = lambda slug: f"{SITE}/recordings/{slug}/"
PDF = lambda f: f"{SITE}/media/curriculum/{f}"
SCALES = f"{SITE}/resources/the-scale-series/"
CC = "The Cambridge Companion to the Saxophone"

years = [
    {
        "id": "first-year", "n": 1, "name": "First Year", "lv": "1", "catalog": "First Year",
        "technique": [
            {"text": "The Scale Series", "url": SCALES, "detail": "Memorized up to 4 sharps and 4 flats by the end of the year"},
        ],
        "etudes": [etude("David Hite - Melodious and Progressive Studies Book 1")],
        "rep": {"alto": parse_rep("First Year Alto Saxophone"), "tenor": parse_rep("First Year Tenor Saxophone")},
        "jazz": {
            "scales": [{"name": "Blues"}, {"name": "Pentatonic"}, {"name": "Whole tone"}, {"name": "Diminished"}],
            "scalesNote": "From The Scale Series",
            "books": [{"title": "Jazz Conception", "composer": "Jim Snidero", "tunes": ["Groove Blues", "Amen", "A Doll", "Grease", "Joe’s Thing"]}],
        },
        "reading": [
            {"term": "Fall", "title": "Teaching Students How to Practice", "by": "Steven Mauk", "url": R("teaching-students-how-to-practice"), "kind": "Article"},
            {"term": "Fall", "title": "8 Practice Hacks", "by": "Noa Kageyama", "url": R("8-practice-hacks"), "kind": "Article"},
            {"term": "Spring", "title": "A Jazz Guide to Practicing", "by": "Brent Vaartstra", "url": R("jazz-practicing-guide"), "kind": "PDF", "note": "Not just for jazz students. The guide is great for practicing any kind of music."},
            {"term": "Spring", "title": "Quality Practice: A Musician’s Guide", "by": "Susan Williams", "url": R("quality-practice"), "kind": "PDF"},
        ],
        "readingTheme": "How to practice",
        "listening": [
            {"group": "Intro to classical saxophone", "albums": [
                {"t": "Saxophone and Piano", "a": "Arno Bornkamp", "u": "https://album.link/i/1118489646"},
                {"t": "The Historic Saxophone", "a": "Claude Delangle", "u": "https://album.link/us/i/330892843", "page": REC("the-historic-saxophone-music-written-for-and-published-by-adolphe-sax")},
                {"t": "Recital", "a": "Otis Murphy", "u": ""},
                {"t": "Maslanka: Concertos", "a": "Joseph Lulloff", "u": "https://album.link/us/i/195157616"},
                {"t": "An Exhibition of Saxophone", "a": "Nobuya Sugawa", "u": "https://album.link/us/i/1493753584", "page": REC("exhibition-of-saxophone")},
                {"t": "Saxophone Classics", "a": "Diastema Saxophone Quartet", "u": "https://album.link/us/i/363166027"},
            ]},
            {"group": "Intro to jazz saxophone", "albums": [
                {"t": "Stitt Plays Bird", "a": "Sonny Stitt", "u": "https://album.link/us/i/1488827497"},
                {"t": "Cannonball Takes Charge", "a": "Cannonball Adderley", "u": "https://album.link/us/i/724424981"},
                {"t": "Saxophone Colossus", "a": "Sonny Rollins", "u": "https://album.link/us/i/1440952935"},
                {"t": "Dexter Calling", "a": "Dexter Gordon", "u": "https://album.link/us/i/724840234"},
                {"t": "Inspiration", "a": "Max Ionata", "u": "https://album.link/i/863872574"},
                {"t": "The Inside of the Outside", "a": "Jeff Coffin", "u": "https://album.link/i/1187384687"},
            ]},
        ],
    },
    {
        "id": "second-year", "n": 2, "name": "Second Year", "lv": "2", "catalog": "Second-Year",
        "technique": [
            {"text": "The Scale Series", "url": SCALES, "detail": "Completely memorized by the end of the first semester"},
            {"text": "Beginning altissimo"},
        ],
        "etudes": [
            etude("J. L. Small - 27 Melodious and Rhythmical Exercises"),
            etude("Jean-Marie Londiex - Exercices d’intonation"),
        ],
        "rep": {"alto": parse_rep("Second Year Alto Saxophone"), "tenor": parse_rep("Second Year Tenor Saxophone")},
        "jazz": {
            "scalesTitle": "Jazz scales, memorized",
            "scales": [
                {"name": "Blues"}, {"name": "Pentatonic"}, {"name": "Whole tone"}, {"name": "Diminished"},
                {"name": "Melodic minor", "f": "1 2 ♭3 4 5 6 7", "note": "Ascending form, all keys"},
                {"name": "Dorian", "f": "1 2 ♭3 4 5 6 ♭7", "note": "All keys"},
                {"name": "Lydian", "f": "1 2 3 ♯4 5 6 7", "note": "All keys"},
                {"name": "Mixolydian", "f": "1 2 3 4 5 6 ♭7", "note": "All keys. a.k.a. “The Bebop Scale”"},
                {"name": "Lydian bebop", "f": "1 2 3 ♯4 5 6 ♭7", "note": "A combination of the Lydian and Mixolydian modes"},
                {"name": "Whole-step triad combination", "f": "1 2 3 ♯4 5 6", "note": "Two major triads a whole step apart (C + D = C D E F♯ G A). Also: a pentatonic scale with a ♯4, or Lydian without a 7."},
            ],
            "theory": [
                "Spell all major, minor, augmented and diminished seventh chords",
                "Identify every scale degree in all major and minor keys (What is the 6th scale degree of F minor?)",
                "Chord and scale combinations (Which scales can be used on a G7 chord?)",
            ],
            "tunes": [
                {"group": "Major blues", "items": [
                    {"t": "Blues in the Closet", "c": "Oscar Pettiford"}, {"t": "Bessie’s Blues", "c": "John Coltrane"},
                    {"t": "Tenor Madness", "c": "Sonny Rollins"}, {"t": "C Jam Blues", "c": "Duke Ellington"},
                    {"t": "Straight, No Chaser", "c": "Thelonious Monk"}, {"t": "The Blues Walk", "c": "Clifford Brown"},
                    {"t": "Now’s the Time", "c": "Charlie Parker"}]},
                {"group": "Minor blues", "items": [
                    {"t": "Mr. P.C.", "c": "John Coltrane", "bb": "https://drive.google.com/open?id=15D4_NEhz9NIZ6DSC7wQeqv3DCZ_iqlbr", "pa": "https://www.youtube.com/watch?v=rVMuifNRY1A", "rec": "https://song.link/i/962195365"},
                    {"t": "Equinox", "c": "John Coltrane", "rec": "https://song.link/us/i/962199387"}]},
                {"group": "Modal blues", "items": [
                    {"t": "All Blues", "c": "Miles Davis", "rec": "https://song.link/us/i/268443200"},
                    {"t": "Footprints", "c": "Wayne Shorter", "rec": "https://song.link/us/i/186373848"}]},
                {"group": "Modal tunes", "items": [
                    {"t": "Impressions", "c": "John Coltrane", "rec": "https://song.link/us/i/1440912144"},
                    {"t": "So What", "c": "Miles Davis", "rec": "https://song.link/us/i/268443097"},
                    {"t": "Cantaloupe Island", "c": "Herbie Hancock", "rec": "https://song.link/us/i/724380029"},
                    {"t": "Little Sunflower", "c": "Freddie Hubbard", "rec": "https://song.link/us/i/76147149"}]},
            ],
            "books": [{"title": "Jazz Conception", "composer": "Jim Snidero", "tunes": ["Total Blues", "Miles", "Two Plus Two", "Blue Minor", "Bird Blues"]}],
        },
        "reading": [
            {"term": "Fall", "title": "Ch. 1: “Invention and Development”", "in": CC, "by": "Thomas Liley", "url": PDF("Liley-The-Cambridge-Companion-to-the-Saxophone-Ch.-1.pdf"), "kind": "PDF"},
            {"term": "Spring", "title": "Ch. 2: “In the Twentieth Century”", "in": CC, "by": "Don Ashton", "url": PDF("Ashton-The-Cambridge-Companion-to-the-Saxophone-Ch.-2.pdf"), "kind": "PDF"},
        ],
        "readingTheme": "The instrument’s history",
        "listening": [
            {"group": "Next steps: classical saxophone", "albums": [
                {"t": "Sonatas", "a": "Arno Bornkamp", "u": "https://album.link/us/i/979557388"},
                {"t": "Hybrid", "a": "Robert Young", "u": "https://album.link/us/i/1348879058"},
                {"t": "Notturno", "a": "Timothy McAllister", "u": "https://album.link/us/i/1520663218"},
                {"t": "A la Française", "a": "Claude Delangle", "u": "https://album.link/us/i/331278809", "page": REC("a-la-francaise"), "note": "Also listed as Koechlin: Etudes for Alto Saxophone and Piano"},
                {"t": "Grieg, Glazunov, Dvořák", "a": "Quatuor Habanera", "u": "https://album.link/i/1255924858"},
            ]},
            {"group": "Next steps: jazz saxophone", "albums": [
                {"t": "Blue Train", "a": "John Coltrane", "u": "https://album.link/us/i/1468202477"},
                {"t": "Kind of Blue", "a": "Miles Davis", "u": "https://album.link/us/i/268443092"},
                {"t": "Wish", "a": "Joshua Redman", "u": "https://album.link/us/i/305687509"},
                {"t": "The Magnificent Charlie Parker", "a": "Charlie Parker", "u": "https://album.link/us/i/1518148384"},
                {"t": "Two of a Mind", "a": "Paul Desmond and Gerry Mulligan", "u": "https://album.link/us/i/525523977"},
            ]},
        ],
    },
    {
        "id": "junior-year", "n": 3, "name": "Junior Year", "lv": "3", "catalog": "Third Year",
        "technique": [
            {"text": "Scales in 4ths"},
            {"text": "Advanced altissimo"},
            {"text": "Beginning extended techniques", "list": ["Growl", "Flutter", "Multiphonics", "Circular breathing", "Double tonguing"]},
        ],
        "etudes": [
            etude("Franz Wilhelm Ferling - 48 Famous Studies", {"also": {"t": "The Ferling Project", "u": f"{SITE}/resources/the-ferling-project/"}}),
            etude("Noël Samyn - 9 Études Transcendantes"),
        ],
        "rep": {"alto": parse_rep("Junior Year Alto Saxophone"), "tenor": parse_rep("Junior Year Tenor Saxophone")},
        "jazz": {
            "etudes": [{"title": "Jazz Saxophone Etudes, Vol. 1", "composer": "Greg Fishman"}, {"title": "14 Jazz and Funk Etudes", "composer": "Bob Mintzer"}],
            "tunes": [
                {"group": "AABA form", "items": [{"t": "My Little Suede Shoes"}, {"t": "Take the A Train"}, {"t": "The Preacher"}]},
                {"group": "Minor tunes", "items": [{"t": "Autumn Leaves"}, {"t": "Summertime"}, {"t": "Blue Bossa"}, {"t": "In a Mellow Tone"}]},
                {"group": "Rhythm changes", "items": [{"t": "Oleo"}, {"t": "Doxy"}]},
                {"group": "Other interesting harmonies", "items": [{"t": "Green Dolphin Street"}]},
            ],
        },
        "reading": [
            {"term": "Fall", "title": "Ch. 4: “Repertoire Heritage”", "in": CC, "by": "Thomas Liley", "url": PDF("Liley-The-Cambridge-companion-to-the-saxophone-Ch.-4.pdf"), "kind": "PDF"},
            {"term": "Spring", "title": "Ch. 14: “The Saxophone Today”", "in": CC, "by": "Delangle and Michat", "url": PDF("Delangle-and-Michat-The-Cambridge-companion-to-the-saxophone-Ch.-14.pdf"), "kind": "PDF"},
        ],
        "readingTheme": "Repertoire, then and now",
        "listening": [
            {"group": "Advanced classical saxophone", "albums": [
                {"t": "The Solitary Saxophone", "a": "Claude Delangle", "u": "https://album.link/us/i/1727130438", "page": REC("the-solitary-saxophone")},
                {"t": "Hot Sonate", "a": "Arno Bornkamp", "u": "https://www.arnobornkamp.nl/HotSonate.zip", "free": True},
                {"t": "The Snell Sessions", "a": "Christopher Creviston", "u": "https://album.link/us/i/458218946", "page": REC("the-snell-sessions")},
                {"t": "Le Merle noir", "a": "Idit Shner", "u": "https://album.link/us/i/686311432"},
                {"t": "Made in Japan", "a": "Nobuya Sugawa", "u": "https://album.link/us/i/1492024589"},
                {"t": "Mysterious Morning", "a": "Quatuor Habanera", "u": "https://album.link/us/i/1572107100"},
            ]},
            {"group": "Gettin’ weird: jazz saxophone", "albums": [
                {"t": "Giant Steps", "a": "John Coltrane", "u": "https://album.link/us/i/1502751229"},
                {"t": "Inner Urge", "a": "Joe Henderson", "u": "https://album.link/us/i/724519387"},
                {"t": "The Shape of Jazz to Come", "a": "Ornette Coleman", "u": "https://album.link/us/i/921051612"},
                {"t": "Out to Lunch", "a": "Eric Dolphy", "u": "https://album.link/us/i/1455686798"},
                {"t": "Looking Forward", "a": "Miguel Zenón", "u": "https://album.link/us/i/271250277"},
            ]},
        ],
    },
    {
        "id": "senior-year", "n": 4, "name": "Senior Year", "lv": "4", "catalog": "Fourth Year",
        "technique": [{"text": "Overtone exercises"}],
        "etudes": [etude("Guy Lacour - 28 Etudes sur les Modes a Transpositions Limitees d'Olivier Messiaen")],
        "rep": {"alto": parse_rep("Senior Year Alto Saxophone"), "tenor": parse_rep("Senior Year Tenor Saxophone")},
        "jazz": {
            "etudes": [{"title": "Jazz Saxophone Etudes, Book 2", "composer": "Greg Fishman"}],
            "tunes": [{"group": "Standards", "items": [{"t": t} for t in [
                "All the Things You Are", "Blue in Green", "Bye Bye Blackbird", "Cherokee", "Countdown", "Desafinado",
                "Donna Lee", "Eternal Triangle", "Freedom Jazz Dance", "Giant Steps", "It’s Only a Paper Moon",
                "Lucky Southern", "Lush Life", "Mack the Knife", "Moment’s Notice", "Ornithology", "Stella by Starlight",
                "Stolen Moments", "There Will Never Be Another You", "Wave", "The Way You Look Tonight", "Work Song", "Yesterdays"]]}],
        },
        "reading": [
            {"term": "Fall", "title": "Ch. 11: “Teaching the Saxophone”", "in": CC, "by": "Horch", "url": PDF("Horch-The-Cambridge-companion-to-the-saxophone-Ch.-11.pdf"), "kind": "PDF"},
            {"term": "Spring", "title": "Common Problems (and Solutions) for Developing Saxophonists", "by": "Blackwell", "url": PDF("Blackwell-Common-Problems-and-Solutions.pdf"), "kind": "PDF"},
        ],
        "readingTheme": "Teaching",
        "listening": [
            {"group": "Classical saxophone", "albums": [
                {"t": "Hard", "a": "Richard Ducros", "u": "https://album.link/i/393391585"},
                {"t": "Flows", "a": "Vincent David", "u": "https://album.link/us/i/1440143569"},
                {"t": "Boulez/Berio", "a": "Vincent David", "u": "https://album.link/i/1571966136"},
                {"t": "Differential Moods", "a": "Jeffrey Loeffert", "u": "https://album.link/us/i/1009784984"},
                {"t": "In Lights Starkly Different", "a": "Drew Whiting", "u": "https://album.link/us/i/1500502248"},
                {"t": "This is ~Nois", "a": "~Nois", "u": "https://album.link/us/i/1517756296"},
            ]},
            {"group": "Jazz saxophone", "albums": [
                {"t": "Directions in Music", "a": "Herbie Hancock, Michael Brecker and Roy Hargrove", "u": "https://album.link/us/i/1442924685"},
                {"t": "Gratitude", "a": "Chris Potter", "u": "https://album.link/us/i/1445880992"},
                {"t": "Gratitude", "a": "Dick Oatts", "u": "https://album.link/us/i/286049991"},
                {"t": "Live at the Village Vanguard Vol. 1 (The Embedded Sets)", "a": "Steve Coleman", "u": "https://album.link/us/i/1406547481"},
            ]},
        ],
    },
]

# How many catalog works sit at each year for each instrument (for the "keep exploring" link).
counts = {}
for p in works.values():
    wf, _ = split_fm(p)
    lv = field(wf, "year-of-study")
    inst = field(wf, "instruments") or []
    for sax in ("Alto", "Tenor"):
        if lv and f"{sax} Saxophone" in inst:
            counts[(lv, sax)] = counts.get((lv, sax), 0) + 1
for y in years:
    y["more"] = {s.lower(): counts.get((y["catalog"], s), 0) for s in ("Alto", "Tenor")}
    y["moreAdv"] = {s.lower(): counts.get(("Advanced", s), 0) for s in ("Alto", "Tenor")}
    # flag pieces whose catalog year differs from the curriculum year (reported to Tim, not shown)
    for sax in ("alto", "tenor"):
        for c in y["rep"][sax]["categories"]:
            for pc in c["pieces"]:
                if pc.get("level") and pc["level"] != y["catalog"] and "from" not in pc:
                    print(f"MISMATCH {y['name']} {sax}: {pc['composer']} - {pc['title']} is '{pc['level']}' in catalog", file=sys.stderr)

json.dump({"site": SITE, "years": years}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ok", sum(len(c["pieces"]) for y in years for s in ("alto", "tenor") for c in y["rep"][s]["categories"]), "pieces")
