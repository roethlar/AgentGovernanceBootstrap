# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- 2026-07-22: owner-commissioned holistic toolkit review is complete and
  saved as
  `docs/superpowers/plans/2026-07-22-holistic-toolkit-improvements.md`
  (Status: OPEN): ten verified improvement sites from a 60-agent
  adversarial review (39 findings confirmed at `881e63b`), covering the
  open GitHub issues #5–#8, the plan-gate product hole, reviewer-dispatch
  capability probing, evidence discipline, the owner-communication
  contract, template dead weight, stale cross-harness surfaces, refresh
  hardening, and record drift. NO site is approved for implementation:
  per the owner rulings recorded in that plan (R1–R5), each site's
  decisions go to the owner one at a time and land only on an explicit
  per-site go. Context: earlier on 2026-07-22 an unapproved batch
  implementation of issues #5–#8 (ten commits) was pushed and
  owner-ordered reverted — remote reset to `881e63b`; the reverted work
  survives only in the local tag `backup-2026-07-22-governance-edits`.
  Issues #5–#8 remain open on GitHub. Next action: put Site 1's first
  decision (the ship-effect plan gate) to the owner.
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
