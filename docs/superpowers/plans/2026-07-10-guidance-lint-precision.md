# refresh guidance lint: kill the false positives, drive the baseline to zero

Status: CLOSED 2026-07-10 — landed on owner approval, verbatim: "Do the
plans for the rest as well." Commit map: slice 1 marker support `7074f6b`
(guard-proven); slice 2 baseline cleanup + zero-warn regression test in
the commit carrying this line — the six live warn findings (protocol
token, illustrative layouts, historical install location, declined
artifact, external-repo file) each got the same-line marker with a short
reason, and `lint_governance` over this repo now returns zero warn-level
findings, enforced by the suite.

## Why this plan exists

The refresh lint (`lint_governance` in `tools/refresh.py`) currently
prints roughly eight false LINT warnings on this repo's own
`.agents/decisions.md` every run — protocol tokens (`tools/list`),
illustrative example paths (`drafts/`, `backend/`, `frontend/`), and
references inside historical rationale. The 2026-07-09 external review
(findings M5/M13) and the owner both flagged the noise: a linter that
cries wolf on legitimate prose trains everyone to ignore it, which is
worse than no linter. The lint's own design comment agrees ("a false LINT
line erodes trust").

## Design

Two changes, both conservative:

1. **Same-line allow marker.** `lint_governance` skips path findings on
   any line containing `lint: allow` (matching the plan lint's
   `plan-lint: allow` convention — the shared suffix `lint: allow` is the
   marker, so one spelling serves both tools; conventionally written as
   an HTML comment). Visible, reviewable, per-line — the same escape the
   plan lint shipped at `279d25d`.
2. **Baseline to zero.** Audit every current LINT warning this repo's
   refresh output shows and fix each at the source: genuine dead
   references get corrected wording; legitimate illustrative or protocol
   tokens get the marker. After the pass, an owner-run refresh prints
   ZERO LINT lines for this repo, so the next real warning is signal.

Deliberately NOT changed: the token filter's heuristics
(`_lintable_repo_path`) stay as they are — teaching it to guess "this
token looks illustrative" is exactly the cleverness that breeds false
negatives; the marker moves that judgment to the author, where it is
visible in review.

## Slices (one commit each)

1. Marker support in `lint_governance` + tests: a warned token on a
   marked line → no finding; the marker on an adjacent line → finding
   stands; guard proof per the standard scratch-copy method.
2. Baseline cleanup of `.agents/decisions.md` (and any other `.agents/`
   file the lint currently warns on): verify each token against repo
   evidence — fix real staleness, mark legitimate mentions. Verified by
   running `lint_governance` in-process over this repo (a unit call, not
   a governance refresh, which stays owner-only) and asserting zero
   warn-level findings; that assertion lands as a corpus-style test so
   the baseline stays clean.

## Verification

Full suite per `.agents/repo-guidance.md` (Verification); guard proofs as
above. The zero-baseline test doubles as the regression net.

## Non-goals and risks

- No allowlists of "known-fine" paths and no smarter token grammar — the
  marker is the whole mechanism.
- The zero-baseline test makes future dead references in `.agents/*.md`
  fail the suite in THIS repo; that is the point, and the marker is the
  documented escape when a reference is legitimately historical.
- Governed repos gain the marker behavior on their next owner-run
  refresh; their baselines are their own business.
