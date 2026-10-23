# CLAUDE.md

SaxoBrain is Tim Rosenberg's public saxophone knowledge base. The Hugo source and content live in this repository. Start with [[SaxoBrain - Review and Repair Record]] for completed review and repair history. Internal reference notes are in the root `📁 project-reference/` folder, outside Hugo’s content tree. Reserve `content/` for site material.

## Division of labor

- Tim edits content in Obsidian. The registered SaxoBrain vault currently opens the repository root; `Catalog.base` therefore uses `content/works` folder paths.
- Templates, configuration, workflows and maintenance scripts are the agent's area.
- Never commit or push without Tim's explicit go-ahead.
- Ask before deleting or overwriting existing files.
- Human-facing text uses no em dashes or "not X but Y" framing.

Keep `content/Catalog.base` when retiring review files. It is the maintained catalog interface.

## Project References

- [[SaxoBrain - Research Holds and Identity Questions]]: the 21 retained unassigned works, Sung attribution, Goldstaub identity/scoring and the Shaffer edition caution.
- [[SaxoBrain - Composer Research Record]]: correction precedents, rejected identities and remaining biography gaps.
- [[SaxoBrain - Score Source Findings]]: completed source sweep, unresolved edition leads and Snyder source findings.
- [[SaxoBrain - Retired Catalog Entries]]: archived removals and merges; public redirects remain in surviving aliases.
- [[SaxoBrain - Review and Repair Record]]: archive path, Git recovery revision and completed-pass summary.
- The personal vault's `Notes/SaxoBrain - Project Reference.md`: migration decisions, historical catalog-expansion leads and future ideas.
- The personal vault's `Notes/SaxoBrain - Research Guide.md`: reusable research practices.
- The personal vault's `Notes/SaxoBrain - Repertoire Planner.md`: unfinished planner specification. Its prototype and rebuild dependencies remain in `design/curriculum-and-planner/`.

## Data model

- `content/works/*.md`: one per piece. Fields: `title`, `slug`, `composer` (list of `[[File Name]]` or `[[File Name|Display]]`), `instruments` (list), `composed` (year of composition, of the original work for arrangements), `year-of-study`, `arranger-edition`, `publisher`, `streaming` (a work's own recording; when empty, Listen goes to the album page that lists it, or to the page's Recordings section when several do, via `layouts/_partials/listen-url.html`; album.link/song.link values were cleared 2026-10-09 from works on an album page), `purchase` (list; an entry may be "Label · link", e.g. "B♭ edition (soprano, tenor) · https://...", shown as "Buy the B♭ edition (soprano, tenor)"; `layouts/_partials/purchase-link.html` splits it), `download` (list), `library-recording` (Alexander Street links, not shown publicly), `library-score` (list; library catalog links such as WorldCat, shown on the piece page as a "Find in a library" button), `studied-performed`, `want-to-play` (Tim's personal flags, never shown publicly), `research` (list of sourced facts that help Tim judge difficulty: duration, publisher grade labels, other repertoire lists, program-note remarks on range or technique; each line ends with " · source URL"; never shown publicly; filled 2026-10-09 by web research, so check a line before relying on it; the body also keeps a clickable `## Research notes (private)` list, which `layouts/_partials/body.html` strips from the published page, so edit the body list freely and never rename that heading), `added`, `aliases`.
- `content/composers/*.md`: `title`, `slug`, `nationality`, `gender`, `race`, `born`, `died` (years), `wikidata` (ID, e.g. Q918509), `photo` (`/media/composers/<slug>.jpg`), `photo-source`, `website` (the composer's own site, shown as "Composer's website" under the byline; treated as the authority for facts about that composer's pieces; added only when known), `aliases`, `sort-name` (only when the family name comes first, e.g. Chen Yi → "Chen"; the Composers index and the catalog's composer sort use it in place of the last word of the name). Body = biography and an explicit `caption` callout for the portrait credit. A composer counts as living when born within the last 100 years with no `died` (`layouts/_partials/living.html`).
- `content/lists/competitions/*.md`: competition repertoire lists. A work linked from a list body as `[[Work File]]` shows that list under "Competition lists" on its page (`layouts/_partials/lists-index.html`), so the link is entered only on the list.
- `content/recordings/*.md`: one per album (classical only; Tim alone picks which albums). `works:` lists the pieces as `[[File Name]]`; piece pages find their albums from it at build time (`layouts/_partials/recordings-index.html`), so the link is entered only on the album. Listening links: `youtube` (the album's YouTube playlist, embedded; students' main platform), `spotify`, `apple-music`, `amazon-music`, `tidal`, looked up once 2026-10-07 and checked against each service's album title. `streaming` keeps the old album.link value but is not shown (a non-album.link value such as Bandcamp still gets a Listen button). Odesli's keyless API closed 2026-07-31; album.link pages sometimes resolve to the wrong album. `out-of-print: true` shows an "Out of print" tag on the album page and the Recordings index (Tim decides which albums). `tracks:` ("Title · 8:42 · [[Work File]]", YouTube playlist order; titles and times looked up with yt-dlp 2026-10-08, YouTube cuts titles at 100 characters, hence some "...") builds the track list under the player (`layouts/_partials/recordings/tracks.html`). The link may be a composer file when the piece has no page, or absent; composers come from the catalog, never from YouTube. Consecutive tracks of one work group under its catalog title; `static/js/tracks.js` plays a clicked track through the YouTube IFrame API, by position, so the list must keep the playlist's order and count.
- Album track credits also support a verified plain composer name: `Title · 8:42 · Composer Name`. This displays the name without a composer stub. Linked credits still come from the catalog. Replace the plain name with `[[Composer File]]` after adding that composer if you want the catalog relationship. See the Album Track Credits section of `📁 project-reference/SaxoBrain - Body Components.md`.
- Composer photos are always local copies in `static/media/composers/` (never hotlinked, so no link rot). Photo captions, including Commons photographer/license credits and other source links, live in body `caption` callouts. `photo-source` retains provenance metadata. The photo-maintenance script writes new credits in the body and preserves existing captions.
- Year of Study is Tim's pedagogical call. Never assign or propose levels.
- Titles never repeat the composer in parentheses (Notion-era hack, stripped from 414 titles 2026-10-06 at Tim's request). Two versions of a piece are distinguished by voice, e.g. "Ballade (Alto)" / "Ballade (Tenor)". B♭ and E♭ editions of one piece share a page (merged 2026-10-08 at Tim's request: Mintzer 15 Easy Etudes, Parker Omnibook, Ravel Habanera, Rachmaninoff Vocalise); `instruments` lists every saxophone and each `purchase` entry is labeled with its edition. Original Notion titles are kept in `scripts/migration/notion-ids.json`.

## Addresses (permanent)

- URL = `/works/:slug/`, `/composers/:slug/` from the `slug:` field, never from the file name.
- Changing an address requires adding the old path to `aliases:` (absolute path, leading slash).
- Tim-approved removals without replacement are recorded as exact paths in `scripts/retired-addresses.json`. Never exempt an entire address prefix. The retired Études section's seven addresses are recorded there.
- `scripts/check_addresses.py` runs in the publish workflow: compares `public/addresses.txt` with the live site's copy and fails if any live address disappears or two pages share one.
- `layouts/_partials/composers-of.html` fails the build on any composer link without a matching file.
- Hugo treats file names that differ only in case, spaces or hyphens as the same page. File names must stay distinct under that rule.

## Scripts

- `scripts/check_addresses.py`: publish-time permanent-address and duplicate-address guard.
- `scripts/check_living.py`: monthly Wikidata report for Tim to confirm possible deaths; never edits content.
- `scripts/composer_photos.py`: use `--pending` before a commit to download photo-source images supplied by Tim; preserves existing photos. Other modes include `--wikidata`, `--credits`, `--add` and historical `--notion`. Keep `scripts/migration/photo-skip.json` and `notion-ids.json`, which it reads.
- `scripts/check_links.py`: read-only external-link audit. Writes a generated report to `scripts/migration/link-check.csv`; the report is ignored by Git. Browser-check automated refusals before treating them as dead links.
- `scripts/wikidata_composers.py`: optional biography enrichment with manual review. Keep `scripts/migration/wikidata-overrides.json` so rejected matches are not reused. Its generated `wikidata-review.json` is ignored by Git. Review identity against the saxophone work before using a common-name match.
- Notion importers, old batch applicators, staging files and historical reports were retired after the review/repair passes. Recover exact originals from the external cleanup archive or the revision identified in [[SaxoBrain - Review and Repair Record]]. Never re-import over the maintained catalog.

## Design

Ported from the 2026-10-06 prototype. Tokens, light/dark (follows the visitor's system setting) and all component styles are in `static/css/site.css`; fonts load from Google Fonts in `layouts/baseof.html`. The home page is a client-side catalog: `layouts/home.json` builds `/index.json`, `static/js/catalog.js` filters it, and filters live in the query string (`/?sax=Alto+Saxophone&lvl=First+Year&rec=1`), which the "Start here" tiles use; `sort=title|level|added` changes the order (composer by last name is the default; `added` is newest additions first, from the works' `added` date). The Composers index (`layouts/composers/section.html`) is static HTML grouped by last-name initial, listing only composers with works; `static/js/composers.js` filters it in place from the rows' `data-` attributes (`/composers/?nat=French&lvl=First+Year&women=1`). The Recordings index (`layouts/recordings/section.html`) has an Albums / List switch, albums by default (`static/js/recordings.js`, `/recordings/?view=list`); the cover grid shows only pages with `cover:`. Level colors come from `layouts/_partials/level.html`. Site paths in Markdown (`/media/...`) get the base path from `layouts/_markup/render-link.html` and `render-image.html`; always use `relURL` in templates so the site works under any base path.

## Design prototypes

The unfinished repertoire planner remains in `design/curriculum-and-planner/`, with its template, generated standalone prototype and rebuild dependencies. The folder README explains the workflow. Completed curriculum mockups, earlier rounds and the 12 replaced Notion-era curriculum pages are preserved in the external cleanup archive.

## Curriculum

`content/curriculum/{First,Second,Third,Fourth} Year.md`, one file per year (`year: N`), plain Markdown with explicit linked headings that `layouts/_partials/curriculum/parse.html` reads: `## [Technique](#technique)`, `## [Études](#etudes)`, `## [Solo repertoire](#repertoire)` (paragraph = the rule box; `### Category`, one list per category in Tim's order), `## [Reading](#reading)` (`### Fall` / `### Spring`), `## [Listening](#listening)` (`### group`). Keep fragment IDs stable while editing heading words. Body `focus` and `catalog` callouts hold the reading focus and catalog invitation. The overview body holds its `strands` labels and explanatory `columns`. Repertoire lines are `- [[Work File]] (note)` or, for a piece inside a collection, `- **Title**, Composer, from [[Collection]], No. 3 [Listen](url)`; saxophone tags come from the work's `instruments` (one per saxophone listed, alto included, or "Any saxophone"; a collection line uses the collection's file) (`curriculum/piece.html`). Album lines: `- [[Album File|Display title]] by Performer`, the Listen button opening the album page, which holds the listening links (`curriculum/album.html`; `- [*Album*](url) by Performer` only for an album with no page). No album.link URLs in the curriculum (replaced 2026-10-09). The overview (`layouts/curriculum/section.html`) is built from the year files. Years are numbered, never Junior/Senior; no jazz curriculum (jazz albums are in `content/lists/Jazz Saxophone Listening List.md`). Old per-instrument and jazz addresses are aliases on the year files.

## Custom domain (planned: saxobrain.timothyrosenberg.com)

`hugo.toml` already has the new baseURL and the workflow builds with the base URL GitHub reports, so no code change is needed at cutover. Steps for Tim: (1) add a DNS CNAME record `saxobrain` pointing to `timrosenberg.github.io`; (2) in the repo's Settings > Pages, set the custom domain and tick "Enforce HTTPS" once it is available; (3) push, or re-run the Publish workflow. `scripts/check_addresses.py` compares against both the new domain and the old github.io list, ignores a domain that does not resolve yet, and strips the `/SaxoBrain` prefix so the move does not look like lost pages. Old github.io links redirect to the new domain on their own. Update links in the Fall 2026 syllabi at the next semester break.

## Content authoring

Tim must be able to edit all visible text from Obsidian. Text that belongs to a page's editorial body must live in that note's Markdown body. This includes introductions, section headings, explanations, card descriptions, captions, credits, and page-specific link text. Keep the complete text and links readable in Obsidian. Do not move page copy into template literals, front matter dictionaries, or Site Text keys just to support a layout.

Properties remain appropriate for actual metadata, such as titles, slugs, aliases, authorship, dates, instruments, and Year of Study. Catalog listings and other generated views may display that metadata and relationships. Existing private research and personal flags must remain excluded from public pages.

Prefer ordinary Markdown and a small set of reusable components. A component supplies presentation and behavior while its content stays in the body. Any required structure must be explicit and readable in Obsidian. Do not add page-specific rendering branches or infer component roles from incidental italics, exact prose, or fragile line placement. Plan a shared convention before introducing or replacing a rendering rule. Existing exceptions are migration work, not precedents for new exceptions. See `📁 project-reference/SaxoBrain - Content Authoring Plan.md` for the current findings and migration order. Component syntax and editing examples are in `📁 project-reference/SaxoBrain - Body Components.md`.

## Shared interface text (no hardcoded words)

Shared navigation, buttons, filters, viewer controls, accessibility labels, and system messages live in flat front matter keys in `content/Site Text/*.md` (one file per area, never rendered as pages). Page-specific editorial headings and descriptions belong in the page body under the content-authoring rule above. Templates call `{{ partial "t.html" "key" }}` (`layouts/_partials/t.html`; a missing key fails the build). `layouts/baseof.html` embeds every key starting `js-` or `level-` as JSON (`#site-text`) for the scripts. Placeholders like `{count}` are filled by `replace` or the scripts' `fill`. When adding shared UI text, add a key; never type visible words into a template or script. Matching values (e.g. "First Year" in `year-of-study`, nav slugs, query-string names) stay in code. Check a change with a before/after build diff; the page `<title>`, footer and brand are keys in `Navigation.md`.

## Third-party content

Pages with `third-party: true` (articles by others) or `third-party-files: true` (pages hosting others' PDFs) show a notice that they are outside Tim's CC BY-SA license (`layouts/_partials/notice.html`). Tim approved publishing these on 2026-10-06. Keep the notice on any new page that reproduces others' work.

## Build

The repo sits in iCloud-synced `~/Documents`. On 2026-10-06 macOS made 1,415 conflict copies ("Name 2.md", and numbered names like "Op. 101" becoming "Op. 102"); Tim approved deleting them. If untracked files named like existing pages reappear, they share a slug with the real page and override it in the build.

Use Hugo 0.167.0 or newer locally. Earlier versions have [Hugo issue #15330](https://github.com/gohugoio/hugo/issues/15330): when several content files change in one batch, the preview can retain old metadata and parse positions while reading new file text. This produces stale levels and stray frontmatter fragments in the page body. Version 0.167.0 fixes the collector; `--disableFastRender` alone does not fix affected versions. Verified with three batches of ten metadata edits on 2026-10-12. Keep the installed version and the workflow's `HUGO_VERSION` aligned. `hugo --minify` builds locally; `hugo server --noHTTPCache` starts the local preview. Publishing: `.github/workflows/publish.yml` on push to `main`.

Keep future temporary batch data and scripts in an external working folder. Preserve reusable findings in the project reference notes.

## Current research state

The October 21, 2026 local catalog has 1,138 works. All 21 works without a Year of Study are recorded holds. The active level-review pool is empty. Two identity questions remain separate from those holds: Sung attribution and Goldstaub Graphic IV scoring. Do not reuse the old pre-migration "seven works without composers" checklist as current status. Consult the project references above before starting a fresh pass.
