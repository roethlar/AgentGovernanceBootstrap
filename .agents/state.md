# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- In flight: the 2026-07-23 decisions-as-claims audit (plan:
  `docs/superpowers/plans/2026-07-23-decisions-as-claims-audit.md`).
  Pass 1 + Pass 2 complete in
  `docs/superpowers/plans/2026-07-23-audit-findings.md` — 41 rulings
  audited (16 HOLDS, 20 HOLDS-UNENFORCED, 2 HOLDS-UNSHIPPED, 2 STALE,
  1 CONTRADICTED); architecture verdict: incremental surgery. Routed
  verdicts (F1–F3) go to the owner one at a time; queued fixes F4+
  await per-item owner go.
- Steady state as of `b7448e2` (2026-07-22): the holistic toolkit
  improvement plan and the model-map reviewer dispatch plan are both
  CLOSED, each with its per-finding commit map in its plan doc under
  `docs/superpowers/plans/` (rotation details in
  `docs/history/state-archive.md`). GitHub issues #5–#8 are closed with
  commit receipts, each fix verified at HEAD first. Newest Active
  rulings in `.agents/decisions.md`: paperwork follows technical work
  (verified-fixed bookkeeping proceeds without an owner ask), and owner
  communication is a per-repo 1–5 tunable in `.agents/comms-policy.md`
  (this repo: level 2).
- Steady state as of `0d05c97` (2026-07-12): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/` (full
  enumeration in the 2026-07-12 rotation in
  `docs/history/state-archive.md`); the 2026-07-09 external holistic
  review is fully triaged, with release engineering deferred by the
  release-posture decision. New Active decision 2026-07-11 (`0d05c97`):
  push status is never recorded in state files — git owns it. The
  reviewloop-branches Open item was closed as adopted and archived
  2026-07-12 (`76c1e5f`). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer, and ExchangeAdminWeb (details in
  `docs/history/state-archive.md`). Per-harness capability record:
  `docs/harness-capabilities.md`.

## Next

- Present the audit's routed verdicts (F1–F3: two STALE amendments, one
  CONTRADICTED amendment) to the owner one at a time; then the Fix Queue
  behind per-item owner go.

## Blockers

- None recorded.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- None recorded.
