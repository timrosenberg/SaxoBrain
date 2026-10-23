# Repertoire Planner Prototype

The planner is an unfinished future project. Its specification remains in Tim's personal vault note "SaxoBrain - Repertoire Planner". This folder is excluded from the public Hugo site.

- `planner-prototype.html`: standalone browser prototype.
- `template-planner.html`: editable prototype source.
- `data2.json`: generated curriculum and catalog data from the original prototype cycle.
- `build_data.py` and `build_v2.py`: data preparation dependencies.
- `build_planner.py`: embeds the data into the planner template.

The original prototype data is dated. Regenerate it before using the prototype for current catalog choices.

```sh
python3 build_v2.py /Users/trosenberg/Documents/GitHub/SaxoBrain
python3 build_planner.py
```

Completed curriculum mockups, earlier template rounds and the replaced Notion-era curriculum pages are preserved in the external cleanup archive identified in the repository's CLAUDE.md.
