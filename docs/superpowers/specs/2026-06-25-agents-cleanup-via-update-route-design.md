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

Cleanup therefore needs a **new discovery signal**. The signal is **surplus over the
portable template**, not a scan for specific leak shapes. Discovery does not ask "is
*this line* repo-specific?" (a content judgment); it asks the **structural** question
"does this `AGENTS.md` carry *more than the portable baseline accounts for*?" The
toolkit already ships that baseline (`templates/AGENTS.template.md`), so the surplus is
computable by comparison — and it is the natural **inverse of `missingSections`**:
that signal detects what the target *lacks* versus the template; this detects what the
target *has that the template does not*. Same comparison, opposite sign.

This closes the trigger gap mechanically without any specifics-scan: a current-
versioned, structurally-complete file with an extra leaked line *is* surplus over the
template, so it trips the signal — no regex hunting for `src/` paths, and so no
dependence on a leak "looking like" a path (a leak in prose, a restated-state
sentence, the repo's name as a fact are all caught, because they are all surplus).

Surfaced in the manifest (e.g. `agentsTemplate.surplus` — the diff: sections and
within-section bullets present in the target but absent from the template) and made an
input to a `cleanupRecommended` signal (kept distinct from `reconcileRecommended` so
"structurally stale" and "carries surplus" read differently to an operator; see open
question 1).

Granularity: section-level surplus is trivial (invert the `missingSections`
comparison). Within-section surplus (an extra bullet in a section both files share) is
harder, because the target's bullets are legitimately *reworded* from the template's,
so it is not a clean text diff — it is "which target bullets have no template
counterpart." That is fuzzier but still **structural** (no content semantics), and far
more tractable than "is this line repo-specific." The plan settles how precise the
within-section match must be.

Scope note: discovery is mechanical Python; the surplus is the **candidate set**,
never the final call (see (c)). The signal's job is "this file carries content beyond
the portable baseline — worth a cleanup reconciliation," not "these exact lines are
leaks."

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

## (c) Mechanical vs. agent-judgment — the agent sorts the surplus

The mechanical/judgment split is cleaner under the surplus framing. Discovery computes
the **surplus** structurally (no content semantics) — what the target has beyond the
portable template. The agent then **sorts each surplus item: allowed-repo-specific, or
leak.** That residual judgment is unavoidable and genuinely needs a model, because
surplus is *not* the same as leak: a bootstrapped `AGENTS.md` legitimately carries some
surplus — the `## Current State` pointer, a verification-entry-point reference, an
Active Sources list, earned repo-specific rules migrated in generalized wording. So the
agent's job is "allowed vs. leak," and the cross-harness `drift` audit remains the
semantic backstop.

Why this beats a specifics-scan: "here is everything beyond the portable baseline,
sort it" is a strictly better prompt than "trust this regex found the leaks." No
pattern can miss a leak that does not look like a path, because the candidate set is
*all* surplus, not a guessed subset of it. The structural diff over-includes (it hands
the agent allowed surplus too), but over-inclusion is safe here — the agent is already
in the reconciliation loop and confirms each item; under-inclusion (a missed leak)
would not be safe, and the surplus diff cannot under-include a leak that is genuinely
extra content.

This aligns with the `governance-lint` Open Decision (owner-approved option (a),
2026-06-22), which puts mechanizable **structural** checks in a playbook and leaves
semantic judgment ("evidence-citation sufficiency and prose-reference resolution") to
`drift`. Surplus-over-template is exactly a structural check, so it is a natural member
of that playbook's set — which raises the sequencing question (open question 2):
whether the surplus computation ships *in* `governance-lint` or as a standalone
discovery field the update route reads directly (sequencing matters:
`governance-lint` is approved-but-unimplemented, so making cleanup depend on it
couples two unbuilt pieces — open question 2).

## Scope of changes (when this is planned)

- `tools/discover.py`: compute the **surplus** of the target `AGENTS.md` over
  `templates/AGENTS.template.md` (the inverse of the existing `missingSections`
  comparison), surfaced in the manifest, feeding a `cleanupRecommended` signal. With a
  revert-proof test.
- `procedures/bootstrap.md` Step 3: extend the reconciliation discipline with the
  relocate-don't-breadcrumb rule of (b), and the "agent sorts surplus into
  allowed-vs-leak" step of (c).
- Coordinate the surplus computation with `governance-lint` per (c) — one
  implementation, not two.
- This repo's own `AGENTS.md` is a frozen instance; not edited by this work.
- Verification: `python3 -m unittest discover -s tests -v` (touches `discover.py` and
  copied procedure content).

## Non-goals

- No mechanical *auto-relocation*: discovery computes surplus; the agent makes the
  allowed-vs-leak call and the move, gated by the approval summary.
- Not re-deciding the forward enforcement (the boundary spec owns that). This is repair
  of existing files only.
- No per-fact pointer breadcrumbs (see (b)).

## Open questions for planning

1. (a) signal shape: a separate `cleanupRecommended`, or fold into
   `reconcileRecommended`? A separate flag keeps "structurally stale (version/missing
   sections)" distinct from "carries surplus over baseline," which read differently to
   an operator. Leaning separate.
2. (c) sequencing: surplus computation inside `governance-lint` vs. a standalone
   discovery field — which ships first, and does cleanup-in-update block on
   `governance-lint` (approved-but-unbuilt)?
3. (a) within-section granularity: how precisely must a target bullet be matched to its
   reworded template counterpart before the *unmatched* remainder is called surplus?
   Too loose → real leaks hide as "matched"; too strict → every reworded bullet reads
   as surplus and the agent rubber-stamps. Since the agent confirms each item, lean
   toward *over*-reporting surplus (safe: agent sorts it) rather than under (a missed
   leak is the unsafe failure).
