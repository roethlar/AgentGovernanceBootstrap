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
  rotated verbatim to `docs/history/state-archive.md`);
  **Powershell-Token-Killer DONE 2026-07-09, run by the owner** (refresh
  commit `602ee45` in that repo; the run's false CLAUDE.md flag is the
  evidence in issue #1). Rollout commits were local in those repos awaiting
  owner push as of their run dates — re-verify in those repos, not here.

## Next

- **ExchangeAdminWeb**, the last rollout repo, deferred by the owner until
  **2026-07-20**: run `tools/refresh.py`, resolve FLAG lines (oldest instance
  — 2026-06-22-era template, no repo-guidance.md yet, so it likely needs the
  bootstrap procedure's carve-out rather than a bare refresh).
- **GitHub issue #1** (owner-filed 2026-07-09): `refresh.py` exact-byte
  tracking + no-final-newline canonical shims produce permanent false
  owner-modified FLAGs. Assessed 2026-07-09, confirmed in code: `norm()`
  (`tools/refresh.py:57`) normalizes CRLF only, never a trailing final
  newline, and `templates/shims/CLAUDE.template.md` /
  `GEMINI.template.md` are the only two shipped sources lacking a final
  newline. Fix awaits an owner go and a `plan`; any comparator change must
  keep the recorded `formerly` hash lists matching (regenerate them under
  the new normalization, or hash a candidate set so old hashes stay valid).
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
