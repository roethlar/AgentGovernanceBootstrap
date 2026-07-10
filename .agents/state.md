# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `be03b2c` (2026-07-10): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/`: the plan
  contract (`d3f49d3`), self-refresh-is-owner-only (`292a4d2`), the
  plan-lint suite (`279d25d`), carve-out two-commit route + git hard
  requirement (`2478103`/`dc87799`), refresh trust-boundary hardening
  (`9b3aa64`..`b24a0ab`), fresh-eyes clone rehearsal (`c85129e`), the
  handoff/drift split with tracked `.agents/machines.md` (`741f846`), the
  refresh plan/apply protocol + manifest schema + re-exec
  (`12b6bd4`..`300bff1`), reviewloop shipping + acceptance hardening
  (`77bbf60`/`7295d19`/`4562923`), and guidance-lint precision with a
  zero-warn baseline (`7074f6b`/`be03b2c`). GitHub issues #2/#3/#4 closed
  2026-07-10. The 2026-07-09 external holistic review is fully triaged:
  every accepted finding landed; release engineering is deferred by the
  release-posture decision; the per-repo verbosity/tech-level tuning idea
  is queued Open in `.agents/decisions.md`. This repo's installed copies
  intentionally lag the templates until the owner's next refresh
  (owner-only rule, `292a4d2`). Earlier landed work: bootstrap-offer
  banner (`f65e892`), dead-path lint (`e9e04b4`), newline equivalence
  (issue #1). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.
## Next

- **Owner refresh loop pending**: the 2026-07-10 template changes (handoff/
  drift split, `machines.md`, plan bullet, review skill/wrapper, playbook
  hardening) reach governed repos — and this repo's own lagging installed
  copies — only when the owner runs the fleet refresh (self-refresh is
  owner-only, `292a4d2`).
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

- `HOLISTIC-REVIEW-GPT-5.6-SOL.md` (untracked, owner-side): external review
  assessed 2026-07-10; its verified findings are triaged into the four
  2026-07-10 draft plans. Untriaged remainder (plan/apply approval
  protocol, provenance pinning, review-loop shipping gap, release/CI
  items) awaits owner direction.
