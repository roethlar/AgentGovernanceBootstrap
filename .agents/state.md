# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `59439e7` (= GitHub canon, verified via `git ls-remote`
  2026-07-09; this handoff's own commit lands on top): the 2026-07-08
  zero-based consolidation is landed and self-applied; the product shape is
  owned by `.agents/repo-guidance.md` (Mission Detail). Latest product
  change: a refused **core-file** replacement now ends in an unmissable
  ATTENTION banner plus an offer to run bootstrap — TTY-gated interactive
  launch of a PATH-detected harness, non-TTY prints ready-to-paste launch
  commands, nothing auto-runs; landed `f65e892` 2026-07-09 on owner go,
  decision entry 2026-07-09, plan closed with commit map:
  `docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`. Prior:
  git-aware dead-path lint (`e9e04b4`, plan closed:
  `docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`) and the
  newline-equivalence fix for GitHub issue #1 (plan closed:
  `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`).
  Rollout is DONE for vela, Blit_v2, ai-rpg-engine, and
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
- `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`
- `docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`
- `docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`

## Unrecorded Repo Memory

- None known.
