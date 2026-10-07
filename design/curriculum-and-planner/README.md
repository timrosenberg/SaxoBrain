# Curriculum redesign and repertoire planner prototypes

Design prototypes from 2026-10-07. Hugo ignores this folder; nothing here is published.

- `curriculum-mockup.html`: curriculum redesign, round 3 (current). Published as https://claude.ai/artifact/6h7NbqJr9bxNbfWtMJFbSy.
- `planner-prototype.html`: repertoire planner, split out for its own dev cycle. Published as https://claude.ai/artifact/MyNTq757LaApCain9TbHmH. Spec and open questions: Tim's vault note "SaxoBrain - Repertoire Planner".
- `template-round1.html`, `template-round2.html`: earlier rounds (round 1 had separate alto/tenor lists and jazz; round 2 added the planner).

- `notion-era-curriculum/`: the 12 curriculum pages the redesign replaced (index, alto and tenor lists per year, three jazz pages), moved here on 2026-10-07 when the redesign was built. Kept for reference; nothing links to them.

Both HTML files open directly in a browser.

## Rebuilding

```
python3 build_v2.py ~/Documents/GitHub/SaxoBrain   # reads content/, writes data2.json (curriculum + whole catalog)
python3 build_v3.py                                # template-round3.html -> curriculum-mockup.html
python3 build_planner.py                           # template-planner.html -> planner-prototype.html
```

`build_v2.py` reuses the parsing in `build_data.py` (round 1). The curriculum's technique, études, reading and listening are transcribed by hand in `build_data.py`; solo repertoire is parsed from `content/curriculum/`.
