# AGENTS.md as verbatim template: pointer, byte-compare, wholesale replace

Status: DRAFT — awaits owner approval and the open picks below. No code touched.
Implements the 2026-07-01 verbatim-template decision (`.agents/decisions.md`).

## Target state

- `AGENTS.md` in every bootstrapped repo (this one included) is byte-identical
  to `templates/AGENTS.template.md`.
- One designated repo-specific file — **`.agents/repo-guidance.md`** (N1) —
  holds everything repo-specific that used to live inline: mission detail,
  active sources / reading order, verification specifics, earned rule
  variants, remotes and canon-propagation facts, hook descriptions.
- The template carries a short **Repo-Specific Guidance** pointer section
  naming that file, with the precedence rule (O1).
- Discovery byte-compares the target's `AGENTS.md` to the current template;
  any difference → `reconcileRecommended`. Reconciliation = replace the file
  whole; first migration carves repo content out into `.agents/repo-guidance.md`.

## Slices (one scoped commit each; suite green per slice; push policy `always`)

**1. Template: pointer section + precedence.** Add to
`templates/AGENTS.template.md` (after `## Current State`):

> ## Repo-Specific Guidance
> This file is the toolkit template, verbatim — it is replaced whole on every
> governance refresh and never hand-edited. Everything specific to this repo
> — mission detail, reading order, verification commands, earned rule
> variants, remotes — lives in `.agents/repo-guidance.md`. That file extends
> this one; where it sharpens or overrides a non-Prime rule it must cite the
> decision that earned the change (O1). The Prime Invariants are never
> overridden.

Adjust the write-authority invariant ("written only by a gated run" →
"replaced whole by a gated run; never hand-composed") and the portability
invariant's relocation target (name `repo-guidance.md`). Bump
`templateVersion` (next dotted sub-version at implementation date). Lockstep
test-text updates.

**2. New `templates/repo-guidance.template.md`.** Skeleton with the section
headers above and one instruction line each; installed to
`.agents/repo-guidance.md` on every route (greenfield drafts it fresh;
migration fills it from the carve-out). Draft steps added to the greenfield
list, migration Step 2, and the reconciliation branch (create-if-missing).

**3. `discover.py`: byte-compare probe.** `agentsTemplate` gains
`byteIdentical` (target `AGENTS.md` vs `.bootstrap-tmp/templates/AGENTS.template.md`,
exact bytes); `reconcileRecommended = not byteIdentical` (subsumes the stamp
and section probes — both stay as descriptive leads in the manifest, no longer
load-bearing). Tests: a fixture with a current stamp over stale wording must
now recommend reconcile (the incident case, mechanically caught — this is the
acceptance test the old design failed); a byte-identical fixture must not.
Golden regen; mutation-proof per the standard hermetic discipline.

**4. Procedures: replace-whole reconciliation.**
`procedures/bootstrap.md` Step 3 reconciliation branch becomes: (a) if
`.agents/repo-guidance.md` is missing, carve repo-specific content out of the
existing `AGENTS.md` into it (this is the portability sweep's new form — run
once); (b) replace `AGENTS.md` with the template verbatim; (c) both land via
the normal approval summary. `procedures/migration.md` Step 2: the drafted
`AGENTS.md` is the template verbatim, and carried-over earned rules go to
`repo-guidance.md` (supersedes the carry-forward-into-AGENTS.md wording and
the line-by-line sweep added earlier on 2026-07-01).

**5. Dogfood run (owner-initiated, outside this plan's commits):** run
`/update-governance` here. Expected: discovery flags the current mixed-content
`AGENTS.md` (byte-compare fails), the run carves this repo's specifics into
`.agents/repo-guidance.md` (mission detail, Active Sources, Verification
commands, canon-propagation remotes, hook description, the earned
discretionary-rtk stance citing 2026-06-22), replaces `AGENTS.md` verbatim,
and the result passes byte-compare. This supersedes the out-of-band `f697bf9`
content through the sanctioned path — no revert needed, the replacement makes
it moot. If the run does NOT flag the file, slice 3 failed; stop.

**6. Bookkeeping:** decision entry updated to Adopted with commit map;
`state.md`; this plan closed.

## Verification

- `python3 -m unittest discover -s tests -v` per slice; new/changed tests
  proven to bite via hermetic mutation (never the tracked file).
- Slice 5 is the end-to-end validation, with the incident as the test case.
- Docs-only slices: `git diff --check`.

## Non-goals

- No change to harness shims (`CLAUDE.md` stays `@AGENTS.md`, pure adapter).
- No change to the six-operator vocabulary.
- No retro-editing of historical decision entries.

## Open decisions (owner)

- **N1 — repo file name:** `.agents/repo-guidance.md` (**recommend**) vs
  another name.
- **O1 — precedence rule:** repo-guidance may sharpen or override non-Prime
  template rules only when citing the recorded decision that earned it;
  Prime Invariants never overridden; unexplained conflicts get flagged
  (**recommend**) vs extends-only (no overrides — but then this repo's earned
  discretionary-rtk stance has no legal home against the template's rtk
  bullet).
- **O2 — RESOLVED by owner directive 2026-07-01: rtk removed from the product
  entirely** (implemented same day, ahead of the other slices: template bullet
  replaced with the brand-free compact-but-equivalent principle,
  `templateVersion` 2026-07-01.3, test now asserts the shipped template
  contains no `rtk` mention). This repo's own discretionary-rtk stance becomes
  a `repo-guidance.md` fact when slice 5 carves it out.
