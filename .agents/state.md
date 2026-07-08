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
- **Rollout: vela DONE 2026-07-08** — refresh commit `88be803` + JSON-carve
  commit `1b014e9` in `../vela`, both LOCAL there (vela push policy: ask;
  machine-local (this box): owner pushes).

## Next

- Rollout to the remaining governed repos **on owner go**, one at a time:
  Blit_v2, Powershell-Token-Killer, ai-rpg-engine, ExchangeAdminWeb — run
  `tools/refresh.py` in each, resolve its FLAG lines (expect: owner-modified
  settings.json in Blit_v2 flagged; JSON-layer carve like vela's where
  repo-map.json holds the verification commands; EAW is oldest and will see
  the largest template jump). Findings route back as GitHub issues.
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
