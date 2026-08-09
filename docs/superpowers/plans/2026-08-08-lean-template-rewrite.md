# Plan: zero-based lean rewrite of the governance template

Status: CLOSED 2026-08-08 — implemented in `4dde8d4` (template redraft,
`formerly[]` hash, TemplateRuleDedup pin update, decisions entry) on
the owner's go; state record in the following commit. Result: 10,745
chars / 1,642 words → 4,077 chars / 630 words. Additional owner rulings
during drafting, all restated in `.agents/decisions.md` (2026-08-08):
no override mechanism — the never-overrides claim is replaced by
specific-rule-wins; the words-first gate is the agreed 29-word form and
the in-workflow completion-report exception moved to playbook flow; the
compaction re-read sentence and internal rank claim are cut (compact
hook / native pinning cover re-grounding), retiring the orphaned
`prime:*` markers. Verification: full suite 224 tests — green except
the two known Windows `new-project` failures and three pre-existing
machine-local `ProductRemoteFreshnessTests` failures (identical on a
clean-HEAD worktree, recorded in `.agents/machines.md`); five hermetic
guard-proof mutations all bite; `git diff --check` clean; plan lint
green. R1 (target size) was struck by owner correction: size is an
output of the admission test, measured after drafting, never a target.
R2 ruled: both hard gates stay — words-first and
no-code-without-approved-plan — redrafted more concise and more
forceful; rationale: agents still misread an owner remark as a blanket
go and answer with code changes, so the gate is a live failure mode,
not legacy scaffolding. The 2026-08-01 owner working preferences stay
repo-local and do not become the shipped default. R3 ruled: this
repo's `.agents/repo-guidance.md` is out of scope; the rewrite touches
the shipped template only.

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

Zero-based redraft of `templates/AGENTS.template.md`; final size is
whatever the admitted rules add up to and is recorded, not targeted.
Method: start from an empty page and admit rules one at a time, each
justified by one of:

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

Owner rulings shaping the draft (status line carries dispositions):

- R2 (ruled): the words-first and no-code-without-approved-plan gates
  survive, redrafted shorter and more forceful. The redraft must make
  the go-signal explicit and narrow: an owner remark, report, or
  musing is never a go; only an explicit instruction authorizes
  action, and a go covers exactly what it names. This wording earns
  its place under admission test 2 — misreading a remark as a blanket
  go is a failure mode current models still exhibit (owner-observed,
  2026-08-08).
- R3 (ruled): no — `.agents/repo-guidance.md` is untouched; this plan
  changes the shipped template only.

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

Slice 2 — record:

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
