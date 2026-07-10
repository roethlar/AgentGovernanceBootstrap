# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `292a4d2` (verified `git ls-remote origin HEAD` ==
  local, 2026-07-10; clean tree except untracked items noted below): the
  2026-07-08 zero-based consolidation is landed and self-applied; the
  product shape is owned by `.agents/repo-guidance.md` (Mission Detail).
  2026-07-10 owner session landed: governance refresh at toolkit `d3f49d3`
  (`65a8543`), the plan-contract decision (plan docs are agent-facing;
  owner decisions in chat, 25–50 plain words, one at a time — `d3f49d3`),
  the self-refresh-is-owner-only decision (`292a4d2`), and four draft plans
  from the holistic review (`650a122` trust-boundary hardening, `decace2`
  handoff fast-snapshot split, `eaffc7a` fresh-eyes clone rehearsal,
  `a7a6cd7` legacy carve-out commit shape); the plan-lint suite is landed
  (`tests/test_plan_lint.py` + repo-guidance Verification line, `279d25d`);
  open plans dated 2026-07-10+ are linted for leakage, stale paths, and
  bloat. Earlier landed work: bootstrap-offer banner
  (`f65e892`), dead-path lint (`e9e04b4`), newline equivalence (issue #1) —
  plans closed under `docs/superpowers/plans/`. Rollout DONE for vela,
  Blit_v2, ai-rpg-engine, Powershell-Token-Killer (details in
  `docs/history/state-archive.md`). Per-harness capability record:
  `docs/harness-capabilities.md`.
## Next

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
- `docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-handoff-snapshot-and-machine-local-state.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-fresh-eyes-clone-rehearsal.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-carve-out-commit-shape.md` (open, drafted 2026-07-10)

## Unrecorded Repo Memory

- `HOLISTIC-REVIEW-GPT-5.6-SOL.md` (untracked, owner-side): external review
  assessed 2026-07-10; its verified findings are triaged into the four
  2026-07-10 draft plans. Untriaged remainder (plan/apply approval
  protocol, provenance pinning, review-loop shipping gap, release/CI
  items) awaits owner direction.
