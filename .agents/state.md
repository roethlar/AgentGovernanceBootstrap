# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `741f846` (2026-07-10): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). The 2026-07-10 session
  landed, all plans CLOSED with commit maps under
  `docs/superpowers/plans/`: the plan contract (agent-facing plans, owner
  decisions in chat — `d3f49d3`), self-refresh-is-owner-only (`292a4d2`),
  the plan-lint suite (`279d25d`), carve-out two-commit route + git hard
  requirement (`2478103`/`dc87799`), refresh trust-boundary hardening
  (slices `9b3aa64`..`b24a0ab`: floor 3.10, preflight, containment,
  pathspec commits, mirror wording, equivalence boundary), fresh-eyes
  clone rehearsal (`c85129e`), and the handoff/drift split with tracked
  `.agents/machines.md` for machine facts (`741f846`). GitHub issues #2,
  #3, #4 are resolved in the product and await the owner's go to close.
  This repo's installed copies (`AGENTS.md`, skills, wrappers)
  intentionally lag the templates until the owner's next refresh
  (owner-only rule, `292a4d2`). Earlier landed work: bootstrap-offer
  banner (`f65e892`), dead-path lint (`e9e04b4`), newline equivalence
  (issue #1). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.
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

## Unrecorded Repo Memory

- `HOLISTIC-REVIEW-GPT-5.6-SOL.md` (untracked, owner-side): external review
  assessed 2026-07-10; its verified findings are triaged into the four
  2026-07-10 draft plans. Untriaged remainder (plan/apply approval
  protocol, provenance pinning, review-loop shipping gap, release/CI
  items) awaits owner direction.
