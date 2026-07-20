# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- 2026-07-19: model-map reviewer dispatch is landed through Slice 4
  (records) of
  `docs/superpowers/plans/2026-07-19-model-map-reviewer-dispatch.md`:
  the fleet-global `.agents/model-map.json` (owner-granted nickname →
  per-harness model id; seeded `sol`/`terra` on codex) is the single
  sanctioned committed home for model slugs; reviewer dispatch resolves
  nicknames through the map at launch; playbook model-freedom governs
  templates with the map as the explicit lint boundary (F11);
  `.claude/commands/review.md` returns to the shipped set as a pure
  alias (`templates/commands/claude/review.md`, F6) — this repo's
  installed copies converge at the owner's next self-refresh
  (owner-only). Supersessions recorded as dated amendments in
  `.agents/decisions.md` (2026-07-19);
  `docs/harness-capabilities.md` points at the map. Remaining before
  plan closure: Slice 5 — converge proof (`tools/refresh.py` against a
  scratch clone of a governed repo; the alias must install, not
  vanish) and recorded evidence, then the commit map.
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

- **ExchangeAdminWeb**, the last legacy rollout repo, deferred by the owner
  to **2026-07-20** (re-affirmed 2026-07-09): run `tools/refresh.py`,
  resolve FLAG lines; oldest instance — 2026-06-22-era template, no
  repo-guidance.md, so it needs the bootstrap procedure's carve-out, the
  same path qbit-mobile exercised (carve-out done, owner report
  2026-07-12). The owner's fleet refresh (run by 2026-07-12) propagated
  the 2026-07-10/11 template changes to governed repos.

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
