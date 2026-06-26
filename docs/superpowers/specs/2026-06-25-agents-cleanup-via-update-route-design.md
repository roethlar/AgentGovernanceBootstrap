# AGENTS.md retroactive cleanup, via the update route

**Status:** Design, awaiting owner review (no implementation; this defines the
approach the deferred follow-on takes).
**Date:** 2026-06-25
**Parent:** `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`
(this is the "retroactive cleanup" follow-on that spec split off).
**Intersects:** the 2026-06-22 update-route reconciliation machinery; the
`governance-lint` Open Decision (`.agents/decisions.md`, owner-approved option (a),
2026-06-22).

## Problem

The boundary work (2026-06-25, Adopted) defined the *rule* (AGENTS.md is
governance-only and portable) and *forward* enforcement (invariant + advisory hook +
`drift` audit). It did **not** repair repos that were bootstrapped *before* the rule
and already carry repo-specific leakage inside their `AGENTS.md` — concrete source
paths, the repo's own name as a fact, restated current state, a hardcoded
verification command. Those files exist in the wild and will not fix themselves: the
forward invariant steers *new* edits, but a leak already sitting in a structurally-
complete, current-versioned `AGENTS.md` is invisible to every forward mechanism.

## Decision: cleanup is the update route's reconciliation, extended

Cleanup belongs in the **update-route reconciliation** (`procedures/bootstrap.md`
Step 3), not a parallel flow. That step already does the philosophically identical
operation: rewrite a stale `AGENTS.md` into the current shape, "carry the repo's
earned rules forward in generalized wording; migrate the rule, not its stale
examples; verify every migrated fact against current repo evidence" (it reuses
`migration.md` Step 2 discipline), drafting under `.bootstrap-tmp/drafts/` and passing
through the approval summary. Relocating a portability leak into `.agents/` is the
same gated rewrite — one home, one approval gate, not two.

But folding it in naively fails on the common case. The three coupled pieces below are
why this is a spec, not a one-line edit.

## (a) The trigger gap — the blocker

Reconciliation only runs when discovery sets `agentsTemplate.reconcileRecommended`,
which is true on **version-behind** OR **missing whole *sections***
(`agentsTemplate.missingSections`). A non-portable `AGENTS.md` can be **fully
current-versioned and structurally complete** — every required section present — yet
carry a leak *inside* a section (e.g. a `src/api/auth.py` reference within Universal
Invariants). Section probes do not see content within a section (the same blind spot
that forced the `2026-06-25.2` sub-version in the boundary work: a new bullet within
an existing section is invisible to `missingSections`). So a leaked-but-current file
would **never trigger reconciliation**, and cleanup-in-update would be a no-op on
exactly the files that most need it.

Cleanup therefore needs a **new discovery signal**: a portability scan that flags
*candidate* leaks regardless of version/section-completeness, surfaced in the manifest
(e.g. `agentsTemplate.portabilityLeaks` / a candidate list), and made a third input to
`reconcileRecommended` (or a sibling `cleanupRecommended`). Without this, (b) and (c)
have nothing to fire on.

Scope note: discovery is mechanical Python; it produces **candidates**, never the
final call (see (c)). The signal's job is "this file is worth a cleanup
reconciliation," not "these exact lines are leaks."

## (b) The reconciliation step — relocate, don't breadcrumb

Extend the Step 3 reconciliation discipline so that, for each confirmed leak, the
agent **relocates the fact into the appropriate `.agents/` file** (`state.md`,
`decisions.md`, or `repo-map.json` by kind) and **removes it from `AGENTS.md`**.

**Pointer discipline (settled with owner, 2026-06-25): relocate, do not leave a
per-fact pointer.** Most leaks simply leave — a stray source path or a restated-state
sentence belongs in `.agents/` and `AGENTS.md` should not mention it; there is nothing
for a pointer to point at, because the fact was never supposed to be in governance.
`AGENTS.md` keeps only the **structural** pointers that already exist in the template —
the `## Current State` → `.agents/state.md` line and the Source-of-Truth references to
`.agents/decisions.md` etc. — which gesture at the *category* ("repo-specific state
lives in `.agents/`"), not at each moved fact. A pile of "see `.agents/` for X", "see
`.agents/` for Y" is exactly the over-documentation/drift the invariants warn against,
so it is prohibited, not encouraged.

The one narrow exception: when a governance **rule's meaning** references a
repo-specific detail, the rule must name where that detail lives — e.g. a verification
invariant says "run the repo's verification entry point (recorded in
`.agents/repo-map.json`)" rather than copying the command in. That is a pointer to a
*file/key because the rule needs it*, not a breadcrumb for a relocated fact, and it is
rare.

All relocations go through the existing approval summary and land in the same gated
draft → copy flow; no new custody mechanism.

## (c) Mechanical vs. agent-judgment — defer to governance-lint's line

"Is this line repo-specific?" is a content judgment — the same one the whole boundary
rests on — so the **final flag/allow call is the agent's** during reconciliation, and
the cross-harness `drift` audit remains the semantic backstop. Discovery only mechanizes
the **candidate** scan (concrete-looking paths, occurrences of the repo's own
name/dir). That split is already drawn by the `governance-lint` Open Decision
(owner-approved option (a), 2026-06-22), which puts mechanizable structural checks in a
playbook and leaves "evidence-citation sufficiency and prose-reference resolution… for
semantic judgment" to `drift`. The mechanizable portability scan in (a) is a natural
member of that same playbook's check set.

Open sub-question for planning: does the candidate scan ship **in** `governance-lint`
(consistent with its approved scope; cleanup-in-update consumes the playbook's output)
or as a **standalone discovery field** (so the update route does not depend on a
playbook that is itself not yet built)? Sequencing matters: `governance-lint` is
approved-but-unimplemented, so making cleanup depend on it couples two unbuilt pieces.

## Scope of changes (when this is planned)

- `tools/discover.py`: a portability candidate-leak scan over `AGENTS.md`, surfaced in
  the manifest; feed it into `reconcileRecommended` (or a sibling signal). With a
  revert-proof test.
- `procedures/bootstrap.md` Step 3: extend the reconciliation discipline with the
  relocate-don't-breadcrumb rule of (b).
- Coordinate the candidate scan with `governance-lint` per (c) — do not duplicate it.
- This repo's own `AGENTS.md` is a frozen instance; not edited by this work.
- Verification: `python3 -m unittest discover -s tests -v` (touches `discover.py` and
  copied procedure content).

## Non-goals

- No mechanical *auto-relocation*: the agent makes the flag/allow call and the move,
  gated by the approval summary. Discovery only flags candidates.
- Not re-deciding the forward enforcement (the boundary spec owns that). This is repair
  of existing files only.
- No per-fact pointer breadcrumbs (see (b)).

## Open questions for planning

1. (a) signal shape: extend `reconcileRecommended`, or a separate
   `cleanupRecommended`? A separate flag keeps "structurally stale" distinct from
   "leaky-but-current," which read differently to an operator.
2. (c) sequencing: candidate scan inside `governance-lint` vs. standalone discovery
   field — which ships first, and does cleanup-in-update block on `governance-lint`?
3. How aggressive is the candidate scan's recall/precision target? Over-flagging trains
   operators to rubber-stamp; under-flagging misses leaks. Likely: high-recall
   candidates + agent confirmation, since the agent is in the loop anyway.
