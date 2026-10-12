# Research worker instructions

The user authorized research of all 409 remaining unassigned works with existing research. He accepted three GPT-6 Luna research workers and review by the primary agent. This is research for a college and professional saxophone database. The task is to help Tim judge repertoire difficulty and collection fit with useful evidence.

## Ownership and boundaries

Read only your lane's assignment.json. It contains complete source file snapshots and composer website leads. Read the current catalog file before starting each work. If deleted or already assigned, record skipped_catalog_changed with a reason. Do not change any catalog, code, memory, or files outside your own lane directory. Do not commit, push, contact anyone, or request composer access codes. The primary agent owns the master index and shared queue. No agents may spawn further agents.

Research ALL works in your assignment, in the listed batch order. Save each work immediately as records/ID.json with a zero-padded four-digit global ID. Save a Markdown packet per batch in packets/batch-NN.md after its works are researched. Send the primary agent a short message when a packet is ready, then continue with the remaining assignment. Do not stop after the first packet. Persist across context compactions by rereading assignment.json and checking saved records. A research gap is an honest result after a meaningful search, not permission to use only the old catalog note.

## Research standard

Use Research Mode: /Users/trosenberg/.codex/plugins/cache/personal/research-mode/0.1.0/skills/research-mode/SKILL.md. Apply its source rules and report template flexibly to this task. CLAUDE.md in the repo is authoritative for catalog conventions. Year of Study is Tim's call: NEVER assign or propose a year or SaxoBrain difficulty level.

For EACH work:

1. Establish the exact saxophone work/edition from the composer, publisher, original score, institutional library, or performer. Existing research and links are leads, not verified truth.
2. Follow the best leads for readable score/perusal, actual saxophone recording, musical demands, and college/professional programming or pedagogical placement. Look past purchase metadata whenever score or performance evidence can be found.
3. Open sources and verify important claims. Search snippets alone are leads and must be labeled if the underlying document cannot be accessed. Do not label a source opened or a score inspected unless you actually did that. Prefer primary sources. Retailers are acceptable for identifying a specific edition, not as the only basis for technical demands when better evidence exists.
4. With an accessible score, inspect representative musical pages. Text extraction cannot establish notes, articulation, meter, or instrument-specific range. Use view_image on local score pages or PDF screenshots. Inspect both the opening and a contrasting passage where available. You may leave exact range unknown. Distinguish concert-pitch scores from transposed parts. Never transfer another instrument's written range to saxophone.
5. Flag transcriptions of other instruments' music that primarily offer younger players a lyrical melody. Separate documented intended audience from inference. College-relevant Bach and other substantial transcriptions should remain in consideration. A school contest listing alone does not establish simplification or exclude college use. Do not recommend deletion automatically.
6. Keep facts, observations, inference, and gaps distinct. A professional commission proves provenance, not a difficulty level. Record score access limits, edition conflicts, instrumentation corrections, and dead/mismatched recordings.
7. Log exact searches and what was checked. For obscure works, try alternate spelling/title, composer website/catalog, publisher, score/library, and recital/syllabus leads. Do not report no evidence solely after one failed URL.

Use enough searches to reach the same quality bar as the previous ten-work packet, which is at /Users/trosenberg/Documents/GitHub/SaxoBrain/SaxoBrain Review Batch 2026-10-10.md. This does not require finding a score for every work. It requires seeking decision-useful evidence and making missing evidence clear. No fabricated facts, levels, preview observations, listening observations, or guessed URLs.

Do not download remote audio/video just to display it. Identify listening links and credits without claiming auditioned playback. Public score PDFs may be retrieved and inspected; respect protected previews and access barriers. If a PDF skill is needed, read the available PDF SKILL.md. System python3 has fitz and PIL, while bundled Python may not. pdftotext and pdftoppm are installed. PyYAML is not installed; assignment.json eliminates the need for it.

No em dashes or not-X-but-Y framing in human-facing output. Keep sources linked directly near claims. Do not quote source text. Keep source-derived summaries concise, and do not draw more than 200 words total from a single source across your artifacts unless its tool-provided limit permits more. Spread evidence across sources where available. Repeated long catalog descriptions do not improve the research.

## Per-work JSON record

Required keys:
- id: global integer from assignment
- batch: integer
- filename: exact catalog filename
- path: exact catalog absolute path
- title: work title
- status: researched or researched_with_gaps or skipped_catalog_changed
- checked_on: 2026-10-11 (use actual client date if later)
- identity: concise sourced identification and edition qualification
- evidence: array of objects with claim, url, source_name, kind (composer/publisher/score/institution/performer/pedagogy/retailer), access (opened/score_inspected/search_index_only), and optional page
- score_observations: concise observed musical features, or empty; cite evidence source URL
- review_focus: explicitly labeled inference from verified evidence, or empty
- collection_flag: concise documented origin/audience/use, with inferred concern qualified; use unknown if unresolved
- listening: array of objects with url, description, verification; do not claim auditioned
- score_links: array of objects with url, description, inspected (boolean)
- gaps: array of specific unresolved questions
- proposed_corrections: array of evidence-backed proposals, empty if none
- searches: array of actual query strings and checked leads

Add useful fields when justified. Keep each record truthful and self-contained. File existence does not mean enough evidence to assign a level.

## Markdown packets

One work per numbered section using its GLOBAL ID. Include a compact queue table and near-claim citations. Each entry should include local catalog link, sourced new findings, score/listening links if verified, collection/transcription flag, inferred review focus, and specific gaps. Add Tim's decision: pending. Avoid padding unknown sections with generic technique advice. Save assets only when needed in your lane/evidence directory, with absolute image links and source attribution. Do not mirror huge full PDF catalogs into the repo unnecessarily.

Send only concise progress and completion messages to the primary agent. Your files hold the substantive findings.
