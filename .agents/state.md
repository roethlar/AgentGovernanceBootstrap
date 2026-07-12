# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `0d05c97` (2026-07-12): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/` (full
  enumeration in the 2026-07-12 rotation in
  `docs/history/state-archive.md`); the 2026-07-09 external holistic
  review is fully triaged, with release engineering deferred by the
  release-posture decision. The owner ran this repo's self-refresh
  2026-07-10 (`32b598a`, toolkit `5574147`). New Active decision
  2026-07-11 (`0d05c97`): push status is never recorded in state files —
  git owns it; the change is template-side, so installed copies lag the
  templates by that one change — the expected steady state until the
  owner's next refresh (owner-only rule, `292a4d2`). The
  reviewloop-branches Open item was closed as adopted and archived
  2026-07-12 (`76c1e5f`). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.

## Next

- **Owner fleet-refresh pending**: the 2026-07-10/11 template changes
  (handoff/drift split, `machines.md`, plan bullet, review skill/wrapper,
  playbook hardening, push-status-never-recorded) reach governed repos only
  when the owner runs the fleet refresh. This repo's own installed copies
  were refreshed 2026-07-10 (`32b598a`) and lag only by the 2026-07-11
  push-status template change (self-refresh is owner-only, `292a4d2`).
- Per-repo verbosity/tech-level tuning sits Open in `.agents/decisions.md`
  awaiting an owner go for a plan.
- **ExchangeAdminWeb**, the last legacy rollout repo, deferred by the owner
  to **2026-07-20** (re-affirmed 2026-07-09): run `tools/refresh.py`,
  resolve FLAG lines; oldest instance — 2026-06-22-era template, no
  repo-guidance.md, so it needs the bootstrap procedure's carve-out, the
  same path qbit-mobile is exercising now.
- qbit-mobile (fleet context, 2026-07-09): refresh at toolkit `319324e`
  installed the shipped set and flagged its legacy `AGENTS.md`; the owner is
  running the bootstrap carve-out there — the first live exercise of the
  legacy-flag path. Not this repo's work item; friction observed there fed a
  smoother-entry proposal, declined by the owner 2026-07-09 (rotated
  verbatim to `docs/history/state-archive.md`).

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
