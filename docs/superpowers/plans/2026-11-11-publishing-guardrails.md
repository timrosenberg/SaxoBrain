# Publishing guardrails implementation plan

> Execute inline with the executing-plans and test-driven-development skills. Keep this work isolated until review and merge.

Goal: direct content updates to main remain easy; production accepts only validated content and reviewed structural changes.

Spec: https://github.com/timrosenberg/SaxoBrain/issues/2, approved by Tim in chat on November 11, 2026.

Architecture: main and PRs run validation with read-only permissions. The normal publishing gate checks every commit since the previous healthy release and validates the exact current main revision. A separate deployment job publishes that tested artifact and runs smoke checks. Tim chose to keep the existing hosting and process guardrails after review demonstrated that an environment-protected branch would not provide hard isolation against deliberate workflow rewrites.

Tech stack: Hugo 0.167.0, Python 3, PyYAML 6.0.3, unittest, GitHub Actions and GitHub REST API.

## Constraints and review focus

- Content can go directly to main without PRs or worktrees.
- Optional metadata stays optional; unknown years and levels stay valid.
- No unrelated content edits or deletion of existing work.
- Normal direct structural pushes must fail the publishing gate. Deliberate workflow rewrites remain outside enforcement under Tim's chosen hosting model.
- Check accumulated history, including changes later reverted, since the last successful deployment.
- Unreachable live address lists must not erase address protection.
- Production gets the artifact from the exact tested commit.
- A failed smoke check must not silently advance the healthy release baseline.
- Worktree use and Tim's design acceptance are contributor attestations; GitHub cannot observe a local worktree.

## Task 1: content validation

Create scripts/validate_content.py and scripts/tests/test_validation.py. Pin PyYAML in scripts/requirements.txt. Inspect existing data before choosing required fields and accepted types. Write failing fixture tests for YAML errors, duplicate YAML keys, type errors, unresolved references, unsafe URLs, missing assets, and Site Text placeholders. Implement validate(root, baseline=None) returning actionable errors. Preserve existing nullable metadata and supported scalar/list forms. Run fixtures and validate the real catalog.

## Task 2: publishing policy and address baseline

Create scripts/publishing_policy.py and scripts/tests/test_publishing_policy.py. Test content classification, structural Markdown changes, and cumulative unreviewed commits using temporary Git repositories and recorded API fixtures. Verify structural commits belong to merged main PRs with linked complete issues, completed verification checklists, successful validation, and Tim as merger. Support explicit reviewed recovery of exact prior direct commits. Extend scripts/check_addresses.py with required local baseline support and offline hosting-prefix tests. Build the last healthy revision to obtain a trustworthy offline address baseline.

## Task 3: validation, deployment and recovery

Create scripts/validate_site.py, scripts/smoke_site.py and workflow integration tests. Update publish.yml to validate PRs and main and separate build from deployment permissions. Validate generated HTML references and private-content exclusions. Add a deployment revision marker and production smoke checks. Recovery uses a healthy baseline and reviewed revert on current main. Test failures block deployment, feature-branch dispatches, stale revisions and unreviewed recovery. Reject stale build output without deleting existing files.

## Task 4: documentation, review and activation

Add AGENTS.md, structural issue template, PR template and docs/publishing.md. Update README with both workflows. Test all checks, full build, valid content, invalid content, and recovery fixtures. Request a whole-branch review, address material findings, and open a linked PR. Preserve Tim's main checkout. Supply an explicit settings CLI that requires a reviewed merged PR before applying main's force-push protection. Do not activate an unmerged feature workflow. Record remaining activation steps concretely in the PR.

## Progress

- Baseline: 47 tests passed on origin/main 7aba3bfd.
- Isolated worktree: /Users/trosenberg/.codex/worktrees/publishing-guardrails/SaxoBrain.
- Initial protected-branch design rejected in independent review: GitHub Pages permits alternative unprotected deployment environments.
- Ruling: Tim explicitly chose current hosting with validation and structural process guardrails after being offered separate-repository hard isolation. Deliberate workflow rewrites can bypass the checks. Document this limitation and use the simpler normal main publishing workflow.
- Task 1: complete. Real catalog passes data validation; supported legacy types preserved.
- Task 2: complete. History, recovery, address fallback, and hosting-prefix regression fixtures pass.
- Task 3: complete locally. 99 tests, full Hugo build, 2,791-address preservation check, generated-site validation, workflow lint, and diff checks pass. GitHub-hosted execution pending.
- Task 4: templates and settings CLI implemented; reviewed PR and activation pending.
- Independent review findings addressed: healthy baseline for correction pushes; explicit exact-SHA recovery approval; API read permissions; hosting-prefix checks. The stronger deployment isolation requirement was revised by Tim.
- Follow-up review found malformed content syntax was incorrectly treated as structural history. Recovery now compares a correction with the nearest valid note contract; malformed notes still fail data validation. Real-history regression tests cover direct correction and attempted contract changes hidden behind invalid syntax.
- Full validation exposed existing composer-photo and local-score hosting-prefix defects. Minimal template fixes and a rendered regression test address both.
- Article repair was explicitly authorized by Tim after the initial full asset check found two broken image blocks. Existing attribution was preserved.
