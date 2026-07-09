# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `ce0db15` (= GitHub canon, verified via `git ls-remote`
  2026-07-09; this handoff's own commit lands on top): the 2026-07-08
  zero-based consolidation is landed and self-applied. The product shape is
  owned by `.agents/repo-guidance.md` (Mission Detail); provenance is the
  2026-07-08 decision entry and its plan. Landed since the consolidation's
  commit map: the always-on governance lint in `tools/refresh.py`
  (`lint_governance`, adopted 2026-07-08 from the former governance-lint Open
  entry — `b9a867c`, refined `8e6a42f`: never lint `AGENTS.md`,
  create-on-first-use archive paths exempt); operator skills shared via
  `.agents/skills/` with verify-once positives on codex, grok, and agy
  (`f544dfc`); the agy compaction re-ground shipped (`3d3b7f5`) then retired
  on owner decision (`dfbd0c9` — agy pins guidance across compaction
  natively); dead `.agents/RTK.md` removed (`6040a53`). Per-harness
  capability record: `docs/harness-capabilities.md`.
- Rollout: vela, Blit_v2, and ai-rpg-engine are DONE (2026-07-08; details
  rotated verbatim to `docs/history/state-archive.md`). Their rollout commits
  were local in those repos awaiting owner push as of 2026-07-08 — re-verify
  in those repos, not here.

## Next

- Rollout of the last two repos, deferred by the owner (2026-07-08):
  **Powershell-Token-Killer** when the owner's active work there quiets, and
  **ExchangeAdminWeb** after vacation (work-specific). Same recipe: run
  `tools/refresh.py`, resolve FLAG lines (EAW is oldest — 2026-06-22-era
  template, no repo-guidance.md yet, so it likely needs the bootstrap
  procedure's carve-out rather than a bare refresh).
- Owner, at leisure: archive the `agent-harvest` dropbox repo (feedback is
  issues now; re-verified still unarchived 2026-07-09 via
  `gh repo view roethlar/agent-harvest --json isArchived`).

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
