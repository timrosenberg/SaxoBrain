# CLAUDE.md

SaxoBrain: Tim Rosenberg's public saxophone knowledge base, migrating from Notion (saxobrain.notion.site) to Hugo on GitHub Pages. Planning record lives in Tim's vault: [SaxoBrain Improvement Brainstorm](obsidian://open?vault=The%20Vault&file=Notes%2FSaxoBrain%20Improvement%20Brainstorm) (`~/Vaults/The Vault/Notes/SaxoBrain Improvement Brainstorm.md`). Read it before planning work here; update its Migration Status section after milestones.

## Division of labor

- Tim edits content in Obsidian (`content/` is the vault root). He does not want to deal with Hugo; templates, config, workflow and scripts are Claude's area.
- Never commit or push without Tim's explicit go-ahead.
- Human-facing text (README, page copy): no em dashes, no "not X but Y" framing.

## Data model

- `content/works/*.md`: one per piece. Fields: `title`, `slug`, `composer` (list of `[[File Name]]` or `[[File Name|Display]]`), `instruments` (list), `year-of-study`, `arranger-edition`, `publisher`, `streaming`, `purchase` (list), `download` (list), `library-recording` (Alexander Street links, not shown publicly), `studied-performed`, `want-to-play` (Tim's personal flags, never shown publicly), `added`, `aliases`.
- `content/composers/*.md`: `title`, `slug`, `nationality`, `gender`, `race`, `aliases`. Body = bio.
- Year of Study is Tim's pedagogical call. Never assign or propose levels.
- Titles never repeat the composer in parentheses (Notion-era hack, stripped from 414 titles 2026-10-06 at Tim's request). Two versions of a piece are distinguished by voice, e.g. "Ballade (Alto)" / "Ballade (Tenor)". Original Notion titles are kept in `scripts/migration/notion-ids.json`.

## Addresses (permanent)

- URL = `/works/:slug/`, `/composers/:slug/` from the `slug:` field, never from the file name.
- Changing an address requires adding the old path to `aliases:` (absolute path, leading slash).
- `scripts/check_addresses.py` runs in the publish workflow: compares `public/addresses.txt` with the live site's copy and fails if any live address disappears or two pages share one.
- `layouts/_partials/composers-of.html` fails the build on any composer link without a matching file.
- Hugo treats file names that differ only in case, spaces or hyphens as the same page. File names must stay distinct under that rule (see `hugo_key` in the importer).

## Scripts

- `scripts/import_from_notion.py`: pre-launch import from the public Notion API. Overwrites `content/works` and `content/composers`. Do not run after launch.
- `scripts/migration/notion-ids.json`: Notion page ID → file name map, plus each work's Recordings relation IDs (recordings not yet imported).

## Build

`hugo --minify` locally. Publishing: `.github/workflows/publish.yml` on push to `main`.

## Known data issues (fix in content, then delete from this list)

- Duplicate composers to merge: Pierre-Max DuBois / Pierre Max Dubois 2; Niccolò Paganini / Niccolo Paganini; J. B. Faulx / J.B. Faulx; Srul Irving Glick / Srul Irving Glick 2.
- 8 works have no composer.
- Bodies of 226 work pages (notes) not imported yet: take them from Tim's official Notion export.
