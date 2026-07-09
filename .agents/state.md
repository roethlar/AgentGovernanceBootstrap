# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- **Zero-based consolidation: IMPLEMENTED and self-applied 2026-07-08** (as of
  `6f08a67` here). Plan (approved, codex-accepted r8, commit map = the slice
  commits `657aa93..6f08a67`):
  `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`; the
  decision entry with the full supersession map is in `.agents/decisions.md`
  (2026-07-08). The product is now: one procedure + templates +
  `tools/refresh.py`/`shipped-set.json` + reviewloop + one hook + GitHub
  issues feedback. This repo refreshed itself with its own script (commit
  `d5ae8b3` + flag cleanup `6f08a67`).
- **Rollout status (2026-07-08):** vela DONE (`88be803` + carve `1b014e9`);
  Blit_v2 DONE (refresh + follow-up, rebased onto GitHub canon on owner go
  2026-07-08 → now `905c7d3` + `e5a78d9` on top of `b187b56`; the tripwire
  block was also removed from its owner settings.json since it invoked the
  deleted script; push-ready, owner pushes);
  ai-rpg-engine DONE (clone fast-forwarded 75 commits to canon `3d2cc87`
  first, then refresh `97f55fd` + follow-up `38cc4b2`; CLAUDE.md normalized —
  it differed only by a trailing newline). All rollout commits are LOCAL in
  their repos; every push policy there requires the owner.

## Next

- Rollout of the last two repos, deferred by the owner (2026-07-08):
  **Powershell-Token-Killer** when the owner's active work there quiets, and
  **ExchangeAdminWeb** after vacation (work-specific). Same recipe: run
  `tools/refresh.py`, resolve FLAG lines (EAW is oldest — 2026-06-22-era
  template, no repo-guidance.md yet, so it likely needs the bootstrap
  procedure's carve-out rather than a bare refresh).
- Owner, at leisure: archive the `agent-harvest` dropbox repo (feedback is
  issues now); disposition for the `governance-lint` Open entry
  (`.agents/decisions.md` — close as obsolete or re-scope).

## Blockers

- None recorded.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`
- `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`

## Unrecorded Repo Memory

- None known.
