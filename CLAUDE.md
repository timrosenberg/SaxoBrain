# CLAUDE.md

SaxoBrain: Tim Rosenberg's public saxophone knowledge base, migrating from Notion (saxobrain.notion.site) to Hugo on GitHub Pages. Planning record lives in Tim's vault: [SaxoBrain Improvement Brainstorm](obsidian://open?vault=The%20Vault&file=Notes%2FSaxoBrain%20Improvement%20Brainstorm) (`~/Vaults/The Vault/Notes/SaxoBrain Improvement Brainstorm.md`). Read it before planning work here; update its Migration Status section after milestones.

## Division of labor

- Tim edits content in Obsidian (`content/` is the vault root). He does not want to deal with Hugo; templates, config, workflow and scripts are Claude's area.
- Never commit or push without Tim's explicit go-ahead.
- Human-facing text (README, page copy): no em dashes, no "not X but Y" framing.

## Data model

- `content/works/*.md`: one per piece. Fields: `title`, `slug`, `composer` (list of `[[File Name]]` or `[[File Name|Display]]`), `instruments` (list), `composed` (year of composition, of the original work for arrangements), `year-of-study`, `arranger-edition`, `publisher`, `streaming`, `purchase` (list), `download` (list), `library-recording` (Alexander Street links, not shown publicly), `studied-performed`, `want-to-play` (Tim's personal flags, never shown publicly), `added`, `aliases`.
- `content/composers/*.md`: `title`, `slug`, `nationality`, `gender`, `race`, `born`, `died` (years), `wikidata` (ID, e.g. Q918509), `photo` (`/media/composers/<slug>.jpg`), `photo-credit`, `photo-source`, `aliases`. Body = bio. A composer counts as living when born within the last 100 years with no `died` (`layouts/_partials/living.html`).
- Composer photos are always local copies in `static/media/composers/` (never hotlinked, so no link rot). Commons photos carry photographer and license in `photo-credit`; other photos link their source.
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
- `scripts/import_notes_from_export.py`: copies piece notes (197 pages) from the official Notion Markdown export into works that have no body yet. Never overwrites a body. Notes link to other pages with `[[File Name]]`, resolved by `layouts/_partials/body.html`; an unresolved link fails the build.
- `scripts/migration/build_page_map.py` → `page-map.csv`: where every non-catalog Notion page goes (status import / view / private / ask). Private and "ask" pages are never published.
- `scripts/import_pages_from_export.py <export folder> <zip>`: imports the `import` rows (curriculum, reading, recordings, lists, resources) and copies attached files into `static/media/`. Refuses to overwrite a page that has `notion-id:` unless `--force`. `--work-attachments` links attached files in piece notes. Files over 30 MB are not copied (need separate hosting).
- `scripts/migration/wayback_lookup.py` → `wayback.json`: verified Wayback snapshots for each `original-url`; the importer adds them as `wayback-url`.
- `scripts/wikidata_composers.py`: fills `wikidata`, `born`, `died` for composers with no `wikidata`. Applies only an exact-name musician with matching citizenship; the rest go to `scripts/migration/wikidata-review.json`. Hand decisions live in `scripts/migration/wikidata-overrides.json` (null = ruled out). Common names produced wrong people (a rock bassist for "John Cooper"): review new matches before trusting them.
- `scripts/composer_photos.py`: `--notion` (photos Tim set in Notion), `--wikidata` (Commons portrait), `--credits`, `--add NAME URL --credit TEXT`. Never replaces a photo; `scripts/migration/photo-skip.json` lists composers whose photo was ruled out.
- `scripts/check_living.py` + `.github/workflows/living-composers.yml`: monthly, asks Wikidata whether any composer with no `died` has died and opens a GitHub issue. Never edits files; Tim confirms and fills in `died`.
- `scripts/migration/notion-ids.json`: Notion page ID → file name map, plus each work's Recordings relation IDs (recordings not yet imported).

## Design

Ported from the 2026-10-06 prototype. Tokens, light/dark (follows the visitor's system setting) and all component styles are in `static/css/site.css`; fonts load from Google Fonts in `layouts/baseof.html`. The home page is a client-side catalog: `layouts/home.json` builds `/index.json`, `static/js/catalog.js` filters it, and filters live in the query string (`/?sax=Alto+Saxophone&lvl=First+Year&rec=1`), which the "Start here" tiles use; `sort=title|level` changes the order (composer by last name is the default). The Composers index (`layouts/composers/section.html`) is static HTML grouped by last-name initial, listing only composers with works; `static/js/composers.js` filters it in place from the rows' `data-` attributes (`/composers/?nat=French&lvl=First+Year&women=1`). Level colors come from `layouts/_partials/level.html`. Site paths in Markdown (`/media/...`) get the base path from `layouts/_markup/render-link.html` and `render-image.html`; always use `relURL` in templates so the site works under any base path.

## Custom domain (planned: saxobrain.timothyrosenberg.com)

`hugo.toml` already has the new baseURL and the workflow builds with the base URL GitHub reports, so no code change is needed at cutover. Steps for Tim: (1) add a DNS CNAME record `saxobrain` pointing to `timrosenberg.github.io`; (2) in the repo's Settings > Pages, set the custom domain and tick "Enforce HTTPS" once it is available; (3) push, or re-run the Publish workflow. `scripts/check_addresses.py` compares against both the new domain and the old github.io list, ignores a domain that does not resolve yet, and strips the `/SaxoBrain` prefix so the move does not look like lost pages. Old github.io links redirect to the new domain on their own. Update links in the Fall 2026 syllabi at the next semester break.

## Third-party content

Pages with `third-party: true` (articles by others) or `third-party-files: true` (pages hosting others' PDFs) show a notice that they are outside Tim's CC BY-SA license (`layouts/_partials/notice.html`). Tim approved publishing these on 2026-10-06. Keep the notice on any new page that reproduces others' work.

## Build

The repo sits in iCloud-synced `~/Documents`. On 2026-10-06 macOS made 1,415 conflict copies ("Name 2.md", and numbered names like "Op. 101" becoming "Op. 102"); Tim approved deleting them. If untracked files named like existing pages reappear, they share a slug with the real page and override it in the build.

`hugo --minify` locally. Publishing: `.github/workflows/publish.yml` on push to `main`.

## Known data issues (fix in content, then delete from this list)

- 8 works have no composer.
