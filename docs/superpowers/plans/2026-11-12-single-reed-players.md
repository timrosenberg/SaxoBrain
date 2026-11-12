# Single Reed Expressions Players Implementation Plan

> Implement inline in this session. Tim authorized committing, pushing and opening the PR on 2026-11-12. Merging remains unauthorized.

**Goal:** Display an album player for each of the eight volumes on one page.

**Spec:** https://github.com/timrosenberg/SaxoBrain/issues/8

**Architecture:** Extend the existing opt-in body YouTube link renderer to accept playlist URLs. Keep the first album's existing template player and track controls; author Volumes 2–6 as ordinary playlist links under volume headings. Optional Markdown link titles provide distinct accessible player titles. An explicit recording callout reuses the existing recording-player partial for Spotify albums for Volumes 7–8, as Tim approved after their YouTube embeds returned auth errors.

**Worktree:** `/Users/trosenberg/.codex/worktrees/single-reed-players/SaxoBrain`

**Branch:** `codex/issue-8-single-reed-players`

## Constraints

- Preserve all public addresses, optional fields and private research exclusions.
- Do not modify the everyday checkout's templates.
- Retain individual-video start times and opt-out/custom-label link behavior.
- No dependencies or publishing changes. Track-list styles are scoped to preserve the same appearance inside and outside prose.

## Implementation

- [x] Verify eight official playlist identities and track counts.
- [x] Run the existing regression suite on the isolated baseline.
- [x] Add real Hugo fixture tests for eight ordered recording players, Volume 1 controls, lazy loading, accessible titles, opt-out/custom-label links, invalid hosts and individual-video start times. Observe the playlist assertions fail before editing the renderer.
- [x] Extend `layouts/_markup/render-link.html` with anchored playlist matching under `embed-youtube` and preserve existing video matching.
- [x] Replace the table with volume headings and playlist links in the series note; retain its slug and first-volume track metadata.
- [x] Add a recording callout to `layouts/_partials/content-block.html`, reusing the existing player partial, after a failing rendered Spotify-callout test. Use Spotify for Volumes 7–8 with Tim's explicit approval.
- [x] Run fixture tests, full regressions, content validation, Hugo build, site validation and address comparison.
- [x] Inspect desktop/mobile preview and keyboard focus. Record evidence in this plan.
- [x] Prepare the PR description and obtain Tim's explicit authorization to commit, push and open the linked PR.

## Review Focus

- Multiple playlists must render once each in source order.
- Existing individual-video links must retain start times.
- Custom-label links and pages without the opt-in must remain links.
- Invalid hosts must never become embedded YouTube content.
- Volume 1 track buttons must stay paired with their existing iframe.

## Evidence

- The isolated baseline passed 100 tests. The playlist tests failed at the expected missing-player assertions before implementation and passed afterward. The Spotify callout test likewise failed before implementation and passed afterward.
- Official YouTube playlist counts matched Apple: 19, 15, 20, 13, 20, 21, 19 and 27 tracks.
- YouTube 7–8 watch metadata reported OK and playableInEmbed, while unsigned embedded playback returned auth errors. Tim chose Spotify for those volumes. The connected Spotify catalog returned both albums as PLAYABLE.
- Latest healthy publishing revision: `83cb75f9b77ec2cda1a94011a02e92cf9dbd83d2`, verified through the successful GitHub Actions publishing run.
- An initial address comparison used the dirty everyday checkout's preview, which contained unrelated unpublished pages. Replaced it with an archive/build of the healthy publishing revision so the comparison measures this branch correctly.
- Browser plugin absent; used installed Playwright without adding dependencies. Desktop and 390px mobile layout checks covered ordered headings, eight unique players, no horizontal overflow, and keyboard activation of Volume 1 track controls.
- Independent initial and final Spotify-callout reviews found no actionable issues.
- Final verification: 107 regression tests passed; content validation passed; Hugo 0.167.0 built successfully; generated-site validation passed; 2,787 addresses preserved with no unapproved losses; `git diff --check` passed.
- Final browser check: six YouTube and two Spotify album iframes, in volume order; 19 Volume 1 track buttons with keyboard activation; no horizontal overflow at 390px; no page JavaScript exceptions.
- Final preview: http://127.0.0.1:8875/recordings/single-reed-expressions-vol-1/. Rendered artifact: `/tmp/saxrep-single-reed-players-spotify-preview`. Screenshots: `/tmp/single-reed-final-desktop.png`, `/tmp/single-reed-final-mobile.png`, `/tmp/single-reed-final-mobile-vol8.png`.
- Unrelated everyday-vault changes remain untouched. Tim authorized committing, pushing and opening this PR on 2026-11-12. No merge or production deployment was authorized.

## Track-list follow-up

Tim requested complete track lists for Volumes 2–6 after inspecting the preview. The recording callout now accepts a body list using the existing track title, duration and credit format. It reuses the existing track renderer and pairs each list with its own YouTube iframe. The JavaScript initializes every pair independently and loads the shared API once.

- Official playlist rows supply track order and timings; composer credits were checked against the series review. The Volume 6 suite's inconsistent opus/work metadata remains source wording without a new catalog identity.
- New rendered and JavaScript tests failed before implementation and passed afterward. They verify separate player/list pairs, reset playlist indexes, queued clicks, independent highlights, existing API readiness and duplicate script protection.
- The full suite passed 109 tests; content, Hugo build, generated-site and address checks passed. All 2,787 addresses remain preserved.
- An independent review found no actionable bugs.
- The existing preview URL now has six track lists containing 19, 15, 20, 13, 20 and 21 tracks. Volumes 7–8 retain Spotify's built-in track lists.
- Desktop and 390px mobile browser checks confirm six independent keyboard playback targets, matching track-header styles, no horizontal overflow and no JavaScript page errors. Screenshots: `/tmp/single-reed-tracks-desktop.png` and `/tmp/single-reed-tracks-mobile.png`.
