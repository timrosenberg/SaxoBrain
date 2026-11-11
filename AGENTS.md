# Publishing rules

Routine content updates may be committed and pushed directly to `main` when Tim authorizes the commit and push. Examples: adding a work or recording using existing fields, correcting metadata or prose, and adding ordinary media. No separate issue, branch, worktree, or PR is required. Validate the content and inspect affected pages first.

Structural changes require a complete issue before development, an isolated worktree and branch, tests, rendered verification, and a linked PR. Structural changes include templates, CSS, JavaScript, navigation contracts, metadata conventions, dependencies, scripts, workflow files, and publishing settings. Mixed changes follow this path. Do not develop structural changes in Tim's everyday content checkout.

Use `.github/ISSUE_TEMPLATE/structural-change.md` and `.github/pull_request_template.md`. Record the actual worktree path and verification results. Tim accepts and merges structural changes. An agent must have Tim's explicit authorization before committing, pushing, merging, or publishing. Never infer permission to delete or overwrite unrelated material.

The normal publishing workflow validates data, regressions, rendered output, addresses, and structural review records before deploying. Follow `docs/publishing.md` for checks, activation, and recovery. Tim chose current GitHub Pages hosting with process guardrails. A deliberate workflow rewrite can bypass workflow checks, so never describe these as an immutable security boundary.

Preserve optional content fields, private research exclusions, and permanent addresses. Never assign Year of Study. Keep `composed` numeric when known and empty when unknown. Do not include private project-reference files in Hugo output.
