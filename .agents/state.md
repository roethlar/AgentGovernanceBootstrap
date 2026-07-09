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
  change: the dead-path lint is git-aware — vouched deletions print
  `NOTE ... deleted in <hash>`, never-tracked mentions stay loud
  (owner-delegated call, slice 2 dropped); landed `e9e04b4` 2026-07-09, plan
  closed with outcome record:
  `docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`. Prior:
  newline-equivalence fix for GitHub issue #1, plan closed:
  `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`;
  issue commented-and-closed on GitHub 2026-07-09 on explicit owner go.
  Rollout is DONE for vela, Blit_v2, ai-rpg-engine, and
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.

## Next

- **Smoother bootstrap/refresh entry — direction named (owner, 2026-07-09);
  plan drafted, awaiting owner go:**
  `docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`. The
  direction: the refresh output that matters is an unmissable notice that a
  core file was NOT replaced, for any reason; the notice resolves to "run
  bootstrap," and refresh offers to run bootstrap with a harness chosen from
  those installed at that moment. The owner constraints still stand (must
  not assume Claude, PowerShell, a remembered path, or a remembered
  interpreter); the earlier declined shim/skill/pointer proposal stays
  declined and archived verbatim in `docs/history/state-archive.md`.
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
- Owner, at leisure: archive the `agent-harvest` dropbox repo (re-verified
  still unarchived 2026-07-09 via `gh repo view --json isArchived`).

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
