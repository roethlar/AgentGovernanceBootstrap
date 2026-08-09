# Plan: zero-based lean rewrite of the governance template

Status: OPEN 2026-08-08 — drafted on the owner's `plan` word. Pending
rulings: R1 (target size), R2 (which hard gates survive and in what
form), R3 (whether this repo's `.agents/repo-guidance.md` gets the same
pass). No implementation until the rulings land; each is recorded in
`.agents/decisions.md` when ruled.

## Problem

`templates/AGENTS.template.md` (and therefore every installed
`AGENTS.md`) is 10,745 characters / 1,642 words — roughly 2.5k tokens
charged to every session of every governed repo before any work starts.
This repo additionally imports `.agents/repo-guidance.md` (~7k
characters, ~1.7k tokens), for ~4.2k tokens of per-session overhead.

The file grew by accretion: incident-driven rules added one at a time,
most earned against older-generation models. Current-generation models
already do much of what the longest sections spell out (verify before
claiming completion, never rewrite history unasked, ask before
destructive actions, don't bypass failing guards). Meanwhile the
2026-08-01 governance hook enforces protected paths mechanically on both
enforcement harnesses, making the prose version of that protection
partially redundant. The owner's standing direction (2026-08-01 working
preferences, `.agents/state.md`) is "fewer, better rules — mechanism
over prose" and no recurring token costs.

The 2026-07-28 compression pass (1772 → 1656 words, −6.6%) shows
editing-in-place cannot produce a large cut; a zero-based redraft can.

## Non-goals

- Deleting the template or adopting an expiry practice. The
  guidance-files-go-stale argument applies to codebase-orientation docs
  that rot with the code; this file is process and authority, which
  rots slowly, and it is the product this repo ships.
- Changing refresh mechanics, the shipped set's membership, or hook
  behavior. This plan changes wording, not machinery.
- Rewriting playbooks or skills. If the template rewrite orphans
  references, fix the references only.

## Design

Zero-based redraft of `templates/AGENTS.template.md` to the ruled
target size (R1). Method: start from an empty page and admit rules one
at a time, each justified by one of:

1. It is a hard authority/process constraint the model would not infer
   (ownership and refresh semantics, operator verbs, owner gates,
   whichever hard gates R2 keeps).
2. It encodes a repo-portable failure mode current models still
   exhibit, with repo evidence (an archived decision or audit finding).
3. It is wiring another artifact depends on (`.agents/` layout,
   `state.md` entry point, playbook dispatch).

Everything else — restatements of current-model default behavior,
multi-sentence rationale where one clause carries the rule, overlapping
invariants — is cut. Enforcement stays with the hook where the hook
covers it; the template says only what is protected and who owns it,
not how the enforcement works.

Structural constraints preserved:

- One line per paragraph/bullet, no hard wraps (2026-07-02 decision).
- The token-rent rule (2026-07-28) remains in force for future
  additions; this rewrite resets the baseline it measures against.
- `@`-imports for `.agents/repo-guidance.md` unchanged.
- Operator verb names unchanged — playbooks, wrappers, and skills
  dispatch on them.

Owner rulings shaping the draft:

- R1: target size ceiling for the template body (recommendation:
  ~800 words).
- R2: disposition of the two most restrictive gates — words-first
  (act only on explicit go) and no-code-without-approved-plan —
  including whether the 2026-08-01 owner working preferences
  (no ceremonial asks; objective defect fixes inside approved scope
  proceed without asking) are folded into the template as the shipped
  default.
- R3: whether `.agents/repo-guidance.md` in this repo gets the same
  zero-based pass in the same effort (repo-owned file, no publish
  coupling).

## Implementation

Slice 1 — template redraft:

1. Rewrite `templates/AGENTS.template.md` per Design and rulings.
2. Append the outgoing template hash to `formerly[]` in
   `tools/shipped-set.json` (established practice for template
   revisions).
3. Update wording pins in `tests/test_templates.py` to the new text.
   Every retained rule that had a guard keeps a guard; guards for cut
   rules are removed with the rule. Each surviving guard is re-proven:
   mutate a throwaway copy of the template so the rule disappears,
   confirm the test fails, restore, confirm green.
4. `.agents/decisions.md`: one dated entry recording the rulings and
   the new baseline word count; supersede the 2026-07-28 compression
   entry's baseline figure where it states one.

Slice 2 (only if R3 rules yes) — repo-guidance rewrite:

1. Zero-based pass on `.agents/repo-guidance.md` with the same
   admission test; Mission Detail, Reading Order, Verification,
   Remotes & Sync survive as the canonical homes they are, compressed.
2. No test pins reference this file; verification is the docs gate.

Slice 3 — record:

1. `.agents/state.md` `## Now` entry once landed.

One commit per slice.

## Verification

Interpreter per `.agents/repo-guidance.md` (Verification); this
machine's resolved path is in `.agents/machines.md`.

1. Full suite: `<probed-python> -m unittest discover -s tests -v` —
   green except the two known machine-local Windows `new-project`
   failures.
2. Guard proofs per Implementation step 3, on throwaway copies.
3. `git diff --check`.
4. Plan lint: `<probed-python> -m unittest tests.test_plan_lint -v`.
5. Token measurement: record the new template's character and word
   count in the decisions entry alongside the old (10,745 chars /
   1,642 words) so the cut is auditable.

## Rollout boundary

The rewritten template reaches Bixi on the owner's next `publish`; this
repo's installed `AGENTS.md` updates only on the owner's next
self-refresh from the product clone (owner-only, 2026-07-10 rule).
Governed repos pick the new template up on their next
`update-governance`/refresh run. Until then, installed copies lagging
the template is the expected steady state.
