# Site Text Tables Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan in the current session. Track the steps below.

**Goal:** Reduce Obsidian's property suggestions by storing shared wording in ordinary Markdown tables.

**Architecture:** Keep the 12 existing Site Text notes and their titles. Move the 227 wording settings from frontmatter into two-column Setting / Text tables. Read the tables through the existing Hugo site-text partial, preserving its map interface and all text values.

**Tech Stack:** Obsidian Markdown, Hugo templates, Python unittest.

**Spec:** The user approved this conversion in chat on 2026-11-07.

## Global Constraints

- Keep site wording editable in the same notes.
- Preserve setting names, exact text, placeholders, existing prose, public output, and routes.
- Retain publishing controls in Site Text/_index.md.
- Keep unrelated local changes. Do not commit or push.
- Continue in the user's current checkout so the edited vault receives the requested conversion.

## Review Focus

- Preserve quotes, Unicode, placeholders, and literal backslashes; decode escaped table pipes.
- Reject duplicate keys, malformed rows, and empty text with a useful build error.
- Preserve existing JavaScript label data and HTML escaping.
- Keep Site Text out of public output and search indexes.
- Verify actual property reduction; the earlier 228 count included the required build property.

## Task 1: Convert the shared wording source

**Files:** content/Site Text/*.md; layouts/_partials/site-text.html; layouts/_partials/t.html; scripts/tests/test_site_text.py; README.md.

**Interfaces:** Consume plain Setting / Text table rows from each regular Site Text note. Produce the same string-to-string map used by t.html and baseof.html.

- [x] Capture the current 227-value map and full rendered site under /private/tmp.
- [x] Add Hugo fixture tests for table values, errors, editing, and hidden settings pages; run them against the old loader and confirm failure.
- [x] Implement table loading and convert all 12 notes. Preserve titles and existing prose. Add brief editing guidance.
- [x] Confirm the original map is identical, the property count falls from 292 to 65, and every generated public file matches the baseline.
- [x] Run the existing Python regression suite and review the scoped diff.

## Execution Record

- Baseline Hugo build succeeded. Existing Bandcamp lookup warnings were recorded before changes.
- Baseline map was exported by the original Hugo loader, avoiding a second YAML parser.
- User approval covers converting the existing notes and updating the loader. No additional approval step is needed.
- Independent review identified missing support for optional outer table pipes and a literal backslash before an escaped pipe. Both were reproduced in failing Hugo tests, fixed, and verified. Both affect valid table text covered by the design.
- Final Python regression suite: 45 tests passed. Scoped whitespace checks passed.
- All 227 settings retained their exact original values. All 12 wording notes now have only title in frontmatter. The content has 65 distinct property names.
- A concurrent Ceremonias catalog edit changed two files between the initial full builds. Final comparison used one fixed content snapshot with each reader; all 2,922 generated files were byte-for-byte identical. Static files were excluded from this comparison because this conversion does not change them.
- Comparison evidence: /var/folders/qj/mjm2q2y17g16n1flq0xfrxy00000gr/T/saxobrain-site-text-fixed-qcnjae5u.
- No commits or pushes were made.
