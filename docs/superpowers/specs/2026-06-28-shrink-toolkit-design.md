# Shrinking the AgentGovernanceBootstrap toolkit

**Status:** Design exploration, deferred — owner said "decide later" (2026-06-28).
No approach chosen; no implementation. This records the framing and options so a
later session resumes without the conversation.
**Date:** 2026-06-28

## Problem

The toolkit has accreted. The owner wants it smaller along two dimensions (chosen
from four offered; the other two — conceptual surface and accreted history — were
not selected as the primary target):

1. **Maintained / drift surface** — the interlocking files that must stay
   consistent (procedures, templates, `AGENTS.md`, `decisions.md`).
2. **Per-session token cost** — what every agent loads each session (`AGENTS.md`
   via the `@AGENTS.md` import).

The shrink is **feature-preserving**: fewer bytes and interlocks, same
capability. Removing operators/routes/capabilities (conceptual-surface reduction)
is explicitly out of scope.

## Surface measurement

2026-06-28, tracked files, excluding the `docs/history/` archive (10,669 lines):

- `docs/` 4,372 · `templates/` 1,121 · `.agents/` 1,108 (`decisions.md` alone
  866) · `tests/` 1,004 · `tools/` 807 · `procedures/` 750 · root 415
  (`AGENTS.md` 260)
- The bulk is accreted design history plus the decisions queue; the per-session
  load (`AGENTS.md`) is small.

## Approaches

- **(A) Dedup + aggressive archive.** Fully apply the 2026-06-24
  one-statement-plus-pointers rule across template/`AGENTS.md`/procedures; archive
  closed decisions to `docs/history/` (entries marked "Active (historical
  rationale)" whose rule now lives in a template belong there) and resolve/trim
  the Open Decisions queue. `decisions.md` roughly 866 → ~300. Low risk,
  reversible, capability-preserving. Serves dimension 1 strongly, dimension 2
  modestly. The low-risk spine.
- **(B) Layered lazy-load.** Shrink the always-loaded set to a tiny core (Prime
  Invariants + pointers); push reference material to on-demand reads. Serves
  dimension 2 most. **Risk:** pure B fights the drift-prevention-first priority
  and the re-ground-after-compaction design — load-bearing rules moved off the
  always-loaded path can be missed. Use only a thin slice (genuinely
  reference-only content); never move an Invariant off the always-loaded path.
- **(C) Merge interlocking files.** Fold `bootstrap.md` + `migration.md` into one
  routed procedure, merge small templates → fewer cross-referenced files. Serves
  dimension 1. Adds restructuring risk, makes files do more (against the isolation
  principle), and barely helps dimension 2. Held.

## Standing recommendation

A as the spine + the safe slice of B. Hold C.

## Next step

Owner decides among/over the approaches; then a `plan`. Until then the process is
unchanged.
