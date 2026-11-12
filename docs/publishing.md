# Publishing SaxRep

## Agent authorization

Agents may commit, push, and open pull requests for Tim's requested work without separate authorization. An agent must have Tim's explicit authorization before merging any pull request. Manual publishing actions and publishing-setting changes still require Tim's explicit authorization. Normal validated publishing after a permitted content push to `main` remains part of that workflow.

## Routine content

Edit notes in Obsidian, inspect the changed pages, then commit and push to `main` without asking for separate authorization. No issue, separate branch, worktree, or PR is required. This path covers existing metadata fields, works, composers, albums, recordings, prose, links, and ordinary media.

Every main push runs **Validate site**. The normal workflow deploys only after it passes. A failed content update can leave main needing correction while the previous live site remains available. Correct the content and push again. Validation compares against the last healthy release, so a broken previous push does not prevent the correction from publishing.

## Structural changes

Start with a complete issue using the structural template. Resolve material design choices with Tim. Develop in an isolated worktree and branch. Add useful regression tests, run full validation, inspect the affected rendered behavior, and open a linked PR. Record the worktree path and actual checks in the PR checklist. Tim reviews and accepts the change. An agent must obtain Tim's explicit authorization before merging it.

Templates, CSS, JavaScript, dependencies, scripts, workflows, metadata conventions, navigation structure, Site Text keys or placeholders, and address-retirement policy are structural. Unknown or mixed changes use this path. Site Text values can change as content while keys and placeholders stay stable.

The normal publishing gate inspects every first-parent commit since the last healthy release. A later content push or direct revert cannot hide an earlier unreviewed structural commit. A structural commit needs a main PR merge with a complete linked issue, checked verification attestations, a successful final-head PR workflow, and Tim as merger. Use a merge or squash commit so GitHub can associate the main commit with its PR. Do not rebase structural work onto main as individual commits.

## Validation

Use Hugo 0.167.0 and Python 3.12 or newer:

```sh
python3 -m venv /tmp/saxrep-validation
/tmp/saxrep-validation/bin/pip install -r scripts/requirements.txt
/tmp/saxrep-validation/bin/python scripts/validate_content.py
/tmp/saxrep-validation/bin/python -m unittest discover -s scripts/tests -p 'test_*.py'
```

For the end-to-end checks, export a trusted healthy revision into a fresh directory and run:

```sh
mkdir -p /tmp/saxrep-baseline
git archive HEALTHY_REVISION | tar -x -C /tmp/saxrep-baseline
/tmp/saxrep-validation/bin/python scripts/run_validation.py \
  --source . --baseline /tmp/saxrep-baseline \
  --output /tmp/saxrep-site \
  --base-url https://saxrep.com/ \
  --revision "$(git rev-parse HEAD)"
```

Use fresh output directories. Existing files are preserved and cause a clear error. `HEALTHY_REVISION` is the source SHA in the most recent successful publishing run named `Publish <40-character SHA>`. Before the first such run, use `.github/publishing-bootstrap.json`, which records a verified successful production revision. Actions selects this baseline automatically. It never rebuilds the possibly broken previous push.

Add `--allow-contract-changes` only for a structural change that deliberately changes Site Text keys or placeholders. CI verifies the structural record separately. The production path checks unpublished history before considering this flag.

Validation rejects malformed YAML, duplicate properties, invalid known field types, missing required titles and catalog slugs, unresolved metadata references, invalid link syntax, missing local media, and broken Site Text contracts. Empty optional years, scores, recordings, and difficulty are valid. Multi-composer collections may have an empty composer list. Existing plain-text photo provenance and numeric durations remain supported. Historical Notion attachment values in `download` remain metadata. Third-party link availability is a separate editorial check.

The full regression suite runs before building. Hugo validates rendered wiki references and embeds. The address guard compares against a build of the healthy source revision and can additionally check live manifests. It refuses to pass without a usable baseline. Local baselines use the same hosting prefix as the new build.

The generated-site check verifies internal routes and local assets, including the hosting prefix. It rejects private research sections, project-reference output, and vault-only Base embeds. PRs get a downloadable `verified-site` preview artifact.

## Deployment and its limits

Validation jobs have read-only permissions. PRs cannot deploy. Only push or manual runs on main can reach the deployment job. That separate job publishes the previously tested artifact, rejects a stale main revision, and runs smoke checks against production. The checks compare the revision marker and representative HTML, catalog data, addresses, CSS, and JavaScript against the artifact.

A successful publishing run becomes the next healthy baseline only after its smoke checks pass. A failed smoke check leaves that baseline unchanged. Production may already have changed when a smoke check fails, so report it as an unhealthy release and follow recovery.

**Tim chose to keep current GitHub Pages hosting with validation and structural process guardrails. These checks protect the normal publishing path against mistakes. A deliberate rewrite of the workflow can bypass them.** The earlier protected-publishing-branch design was rejected during review because GitHub Pages permits alternate deployment environments. It did not create an immutable boundary.

The main ruleset blocks force pushes and deletion while preserving direct content pushes. The normal `github-pages` environment permits main. No blanket PR or required pre-push status check is placed on main. Repository settings do not selectively force structural changes through PRs. That preparation is enforced by contributor instructions and by the normal publishing gate before deployment.

Worktree use, issue quality, source verification, and Tim's design acceptance require human judgment. Their PR attestations preserve a review record. Hard isolation would require a separately controlled deployment repository or provider, which Tim declined for this implementation.

## Activation

1. Review and merge the implementation PR after **Validate site** passes.
2. Run `python3 scripts/configure_publishing.py --apply --implementation-pr NUMBER` only for authorized activation. The command verifies the merged PR and successful validation before configuring main's non-force-push rule and checking the normal Pages environment.
3. Read back settings with `python3 scripts/configure_publishing.py`.
4. Check the first main publishing run and production `release.json`. Record the successful run URL in the implementation PR.

The settings CLI is read-only unless `--apply` is supplied. It refuses unexpected existing environment protections instead of silently replacing them. No separate publishing branch or hosting migration is needed.

## Recovery

Validation or build failures do not deploy. Correct content directly on main. Recover a structural regression through a checked revert PR linked to its original issue. Preserve public addresses or add aliases as needed. The normal workflow validates the corrected current main revision.

If a direct structural commit was pushed before review, the recovery PR must explicitly identify each such commit with full SHAs:

```text
Reviewed prior commits: FULL_40_CHARACTER_SHA
```

The gate accepts this declaration only from a later main PR that Tim merged after successful final-head validation and the normal issue/checklist requirements. A label, comment, unmerged PR, or unchecked recovery PR cannot authorize earlier commits. This permits a reviewed revert or retrospective acceptance without force-resetting main.

If deployment completed but smoke checks failed, use the last successful publishing run to identify the last good source. Restore its behavior with a checked revert on current main, then publish through the same checks. Confirm matching production bytes before declaring recovery complete. Do not dispatch arbitrary historical revisions around the gate.

The automated suite covers failed smoke checks, explicit reviewed recovery of a prior direct commit, rejected unreviewed recovery, and selection of a healthy baseline after a failed run. A live production recovery requires an authorized release.

## Validation-driven article repair

Initial validation found two broken imported image blocks in Introduction to Saxophone Acoustics. Tim authorized their repair. Three local originals were retrieved from the [UNSW source article](https://newt.phys.unsw.edu.au/jw/saxacoustics.html): `graphics/saxophoneequals.GIF`, `graphics/saxsmall.jpg`, and `graphics/effectofbell.gif`. The article's existing attribution and third-party notice remain in place.
