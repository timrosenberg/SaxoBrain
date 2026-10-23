# Content Authoring Plan

## Authoring Rule

Page copy lives in the corresponding Obsidian note's body. Tim can read and edit introductions, headings, descriptions, credits, captions, and editorial links where they appear in that note. Templates supply presentation and behavior. All visible words remain editable from Obsidian.

Properties hold metadata such as titles, slugs, aliases, authors, and catalog fields. Generated catalogs and relationship lists can continue to use those fields. Shared interface labels remain in `content/Site Text`.

## Findings Before Consolidation

- Altissimo credits now live in the note body. `layouts/_partials/resource-credits.html` moves an italic line after a file link into its box. Its dependency on italics and exact placement is an implicit authoring convention that needs replacement.
- PDF and image cards share viewer behavior through `layouts/_markup/render-link.html`. Preserve their working zoom, download, keyboard, and mobile behavior while consolidating authoring.
- The equipment hub, mouthpiece index, and reed index use `equipment-intro-key`, `equipment-links`, and `equipment-reading` properties to assemble page text from Site Text. Their introductions and card descriptions belong in those notes' bodies.
- Equipment layouts also assemble sections from named pages and interpret heading levels as products or methods. Review each transformation for an explicit reusable structure. Keep intentional relationships between notes and preserve their source links.
- The home page's quick-start descriptions come from Site Text. Review them as editorial content during migration. Search, sorting, filters, and other shared controls retain shared UI labels.
- Ordinary article bodies, Markdown tables, and existing wikilinks already provide an authoring path to retain.

## Rendering Design

Use ordinary Markdown wherever it meets the layout requirement. Introduce an explicit reusable block only where a box or interaction requires one. Obsidian callouts are a candidate because their title, text, and links stay readable in the note. Establish the small shared vocabulary before changing page layouts.

Do not require a page's title, URL, exact wording, incidental emphasis, or a neighboring line to select a component's behavior. A body component must keep its complete editorial content together. It must accept ordinary Markdown links and text of varying lengths. Shared viewer controls can use Site Text defaults.

An unsupported block must retain its content as readable text. Missing formatting must never silently discard copy.

## Migration Order

1. Define the shared block structure using the current altissimo and Scale Series pages as examples. Include an article link, a PDF, an image, and an optional credit.
2. Convert altissimo to that structure. Replace its implicit italic-credit parsing. Verify the same five boxes, source links, viewers, and Steve Lacy redirect.
3. Apply the same components to equipment introductions and cards. Move their editorial text into the appropriate note bodies. Preserve wording, order, links, source notes, and existing addresses.
4. Review the remaining section pages and home quick-starts using the same authoring rule. Add a component only when an existing reusable component cannot express the content.

## Verification

- Compare each migrated page's visible text and link targets with its previous rendering.
- Confirm that the same editorial content is present in the note body and readable in Obsidian.
- Check optional descriptions, long text, linked credits, and blocks with no credit.
- Verify desktop and mobile layouts, PDF and image controls, article navigation, and ordinary link fallbacks.
- Preserve aliases, existing content, and the exclusion of private research and personal flags.
- Run a fresh Hugo build, check changed-file whitespace, and check addresses. Report unrelated build failures separately.

## Status

The Altissimo and Equipment consolidation is implemented and verified. Resource boxes, topic cards, introductions, sections, figures, and quick-reference links now use shared body components. Equipment hubs use whole-note embeds for shared material. The Scale Series and existing Equipment file links use the same resource component.

The implicit italic-credit rule and the equipment hub's hardcoded page assembly are no longer used. Introductions, descriptions, editorial headings, credits, diagram captions, and shared-note inclusions are authored in their page bodies. Shared controls remain in Site Text. Existing reusable leaf presentations remain available through `equipment-format` metadata.

Authoring examples are in [[SaxoBrain - Body Components]]. The first implementation covered Altissimo, the shared resource component, and Equipment. The remaining-page pass below completes the editorial-copy consolidation.

Verification on 2026-10-21: a fresh Hugo build and all 10 body-component tests passed. Browser checks covered desktop and mobile layouts, PDF and image viewing, zoom, downloads, keyboard focus, article navigation, instrument tabs, reed controls, and JavaScript-disabled fallbacks. Dark-mode card colors match the previous rendering. All 2,561 baseline addresses remain, including the old Steve Lacy redirect.

Concurrent Equipment copy edits and return-navigation changes were preserved. The published-address guard reports seven existing retired Études addresses, unrelated to this consolidation. No commit or push was made.


## Remaining Pages Implementation

Continue the same authoring rule without changing the public design. Generated catalog metadata, relationships, and shared controls remain in their existing sources.

1. Home: replace Site Text quick-start copy with explicit `starts` and `start` callouts in `content/_index.md`. Preserve the three destinations, card typography, responsive behavior, catalog filters, and detail panel.
2. Curriculum: put overview explanations and strand labels in `content/curriculum/_index.md`. Put each reading focus and catalog invitation in its year note. Use linked section headings with stable fragment IDs so heading text can change without changing the section role. Keep repertoire, reading, listening, counts, and year navigation intact.
3. Composer captions: move displayed credits into explicit body `caption` callouts. Keep image paths and provenance as metadata. Update the photo-maintenance script to write captions in the body and preserve existing editorial captions.
4. Reading PDFs: replace the implicit whole-body-link rule with explicit `pdf` callouts on its two current pages. Preserve their ordinary links and inline frames.
5. Verify: add Hugo fixture tests for editable cards, section titles, focus, counts, captions, and PDF embeds. Compare all generated HTML pages and address manifests before and after. Exercise desktop/mobile catalog, curriculum navigation, composer filters, album views, and existing resource viewers. Document the syntax in [[SaxoBrain - Body Components]].

Work continues in the current checkout so the local preview includes the existing uncommitted consolidation. No commits, pushes, file deletions, or replacement of unrelated edits are authorized. Temporary snapshots and browser artifacts stay outside the repository.


### Remaining Pages Verification

Completed on 2026-10-21. The home note now holds its entry cards. The Curriculum overview and four year notes hold explanations, section labels, reading focuses, and catalog invitations. The 310 displayed composer photo captions now live in body callouts. Both reading pages with inline PDF frames use explicit body components. Other articles and section pages already use note bodies. Generated catalog metadata, relationships, and shared interface labels retain their established sources.

A fresh Hugo build and all 16 tests passed. Comparing all 2,063 rendered content pages found identical normalized visible text, destinations, images, embedded-media targets, and IDs. The catalog JSON is unchanged. All 2,562 baseline address entries remain. Desktop (1280 px) and mobile (390 px) component dimensions match the baseline, with no horizontal overflow on the checked pages.

Browser checks passed for home entry-card navigation, search, filtering, sorting and detail panels; Curriculum matrix/section/year/catalog links; composer filtering and captions; album-view persistence; both inline PDF links/frames; and the earlier Altissimo, Scale Series, and Equipment viewers and controls. JavaScript-disabled fallbacks also passed. A fresh reviewer checked the shared rendering and maintenance changes. Regressions for bold/linked reading-focus text and uppercase caption blocks pass.

The published-address guard still reports the same seven retired Études addresses. A broad whitespace scan also finds two existing trailing spaces in the unrelated Ferling Project note. Files changed by this consolidation pass their whitespace checks. Temporary verification builds and screenshots remain outside the repository. No commit or push was made.
