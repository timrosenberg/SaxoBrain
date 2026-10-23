# Equipment Section Design and Implementation

Approved direction: equipment hub with five topic boxes, focused guides, and separate long articles. Tim approved implementation on October 21, 2026. The revised design removes breadcrumbs and topic sub-navigation. A single All equipment link returns from topic pages.

## Structure

- Equipment: five topic boxes and quick links to reed charts and adjustments.
- Mouthpieces: classical recommendations by saxophone, technical comparison table, and a separate jazz artist reference.
- Reeds: four task boxes for strengths, break-in/storage, adjustments, and further reading. Show useful content directly beneath those boxes.
- Saxophones: compact model sections grouped by alto and tenor.
- Ligatures: compact illustrated model sections with existing playing notes.
- Straps and harnesses: preserve selection criteria, product lists, and further reading.
- Keep all 15 existing content pages and their addresses. Short material can also appear within a guide. Long third-party articles retain their own pages and attribution.

## Implementation Plan

**Goal:** Turn the approved design into the existing Hugo section using the maintained Markdown sources.

**Architecture:** Apply an equipment content type through the section cascade. Dedicated section/page templates compose small equipment partials. CSS uses existing site tokens. JavaScript progressively enhances instrument selection and symptom filtering.

**Tech stack:** Hugo 0.167.0, Go templates, Markdown/YAML, CSS, vanilla JavaScript.

**Spec:** The structure above and the revised equipment mockup approved in this chat.

### Constraints

- Preserve slugs, Notion IDs, exact source links, product notes, and unrelated local edits.
- Keep visible template and script labels in content/Site Text/Equipment.md.
- Use the existing PDF/image viewer and retain third-party notices.
- Preserve the source values of unverified prices and measurements. Explain their status without guessing corrections.
- All content and navigation remain available without JavaScript.
- Support mobile, dark mode, keyboard input, direct URLs, and a /SaxoBrain/ base path.
- Do not commit or publish.

### Tasks

- [x] Capture a baseline build and focused checks for navigation, content/link preservation, media, and addresses.
- [x] Add equipment templates, editable labels, topic/task cards, and the All equipment return link.
- [x] Reformat comparison/reference pages and product sections. Reuse the maintained pages within the Mouthpieces and Reeds guides.
- [x] Add responsive styles and progressive instrument/symptom controls.
- [x] Build, inspect rendered links/content, compare all addresses, check whitespace, and exercise desktop/mobile/browser flows.

### Review Focus

- A reader entering an old deep link still reaches the correct content.
- Every existing source link and third-party article survives the reorganization.
- A guide transcluding media loads the viewer and resolves paths under a subdirectory base URL.
- A visitor without JavaScript can read every instrument list and adjustment.
- Narrow screens and keyboard users can operate controls without page overflow or hidden focus targets.

## Validation

- Fresh minified builds pass at the normal base URL and with the /SaxoBrain/ prefix.
- All 18 equipment pages retain their addresses, external/media links, and preexisting fragment IDs.
- Independent review found 17 comparison fragments removed by the table conversion. Those fragments now target the corresponding table cells. A build error catches later edits that remove a mapped cell.
- The address checker reports 2,561 normalized addresses with none lost against the baseline build.
- Browser checks covered topic navigation, instrument selection, symptom filtering, image enlargement, PDF loading, and a former comparison bookmark.
- Responsive checks at 390 and 1,024 CSS pixels showed no horizontal page overflow on the inspected guides and product lists.
- Equipment whitespace checks and JavaScript syntax checks pass. The preexisting Ferling Project whitespace issues are outside this change.
- Concurrent resource-origin and Altissimo source-link edits were preserved.
