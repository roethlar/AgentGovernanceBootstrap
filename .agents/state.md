# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- 2026-07-22: the holistic toolkit improvement plan is CLOSED —
  `docs/superpowers/plans/2026-07-22-holistic-toolkit-improvements.md`
  carries the per-site commit maps (the `Implemented 2026-07-22:` line
  under each site heading). All ten sites landed one at a time on
  recorded per-site owner gos (second-pass rulings in the plan header;
  Site 6 as the owner's tunable communication-level spec). GitHub issues
  #5–#8 remain open: per R1, each issue's closure goes to the owner one
  at a time as an Owner Gates ask. Next action: put issue #5's closure
  to the owner.
- 2026-07-22: model-map reviewer dispatch is CLOSED with its commit map in
  `docs/superpowers/plans/2026-07-19-model-map-reviewer-dispatch.md`:
  the fleet-global `.agents/model-map.json` (owner-granted nickname →
  per-harness model id; seeded `sol`/`terra` on codex) is the single
  sanctioned committed home for model slugs; reviewer dispatch resolves
  nicknames through the map at launch; playbook model-freedom governs
  templates with the map as the explicit lint boundary (F11);
  `.claude/commands/review.md` returns to the shipped set as a pure
  alias (`templates/commands/claude/review.md`, F6). Supersessions
  recorded as dated amendments in `.agents/decisions.md` (2026-07-19);
  `docs/harness-capabilities.md` points at the map. The Slice 5 converge
  run (evidence in the plan's Verification section) proves the alias
  installs or updates rather than vanishing, and discriminates: the same
  harness fails against a mutant toolkit carrying the F6 collision.
- Steady state as of `0d05c97` (2026-07-12): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/` (full
  enumeration in the 2026-07-12 rotation in
  `docs/history/state-archive.md`); the 2026-07-09 external holistic
  review is fully triaged, with release engineering deferred by the
  release-posture decision. New Active decision 2026-07-11 (`0d05c97`):
  push status is never recorded in state files — git owns it. The
  reviewloop-branches Open item was closed as adopted and archived
  2026-07-12 (`76c1e5f`). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer, and ExchangeAdminWeb (details in
  `docs/history/state-archive.md`). Per-harness capability record:
  `docs/harness-capabilities.md`.

## Next

- None recorded.

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
