# Plan: refresh correctness and discoverable current boundaries

Status: DRAFT 2026-11-17 — planning and Claude review authorized;
implementation awaits an explicit go for each item below.

## Current contract

Repair four open Bixi refresh defects and improve how agents discover and
apply consequential project constraints. Preserve existing owner decisions,
ignore rules, uncommitted work, and the distinction between evidence and
authority. This document proposes changes; it adopts no new product policy.

| ID | Independently approvable outcome | Implementation authority |
|---|---|---|
| F5 | Correctly install files explicitly re-included by Git ignore rules | Pending |
| F6 | Distinguish ignore skips from foreign governance and route recovery correctly | Pending |
| F7 | Preserve the state template's instruction header during repairs | Pending |
| F8 | Make planned, approved and applied mechanical repairs agree | Pending |
| G1 | Keep current product boundaries discoverable and use them when judging gaps | Pending |

Suggested order: F5, F6, F7, F8, G1. F5–F7 make small, independently
verifiable corrections before F8 restructures the shared repair path.
Each item gets its own implementation commit and evidence. Approving one
does not approve the others. Publish the approved fixes together afterward,
only with release authority. Planning/review completion is distinct from
implementation, integration, and publication.

## Baseline and evidence

- Development source: `0574fd120820c51646268b4a12bfd41a2e326904`, matching
  canonical GitHub master on 2026-11-17. Public issue reports name toolkit
  releases `d59c5cd` and `b1c3728`.
- [Bixi #5](https://github.com/roethlar/Bixi/issues/5): a fixture with
  `/*` and `!/AGENTS.md` produces exit 1 from plain `git check-ignore`,
  exit 0 and the negated pattern from its verbose form. Current refresh
  wrongly flags both explicitly re-included top-level governance files.
- [Bixi #6](https://github.com/roethlar/Bixi/issues/6): an ignored, absent
  AGENTS.md produces the foreign-template banner and exit 5.
- [Bixi #7](https://github.com/roethlar/Bixi/issues/7): applying refresh to
  a committed copy of the actual state template deletes exactly its line
  beginning “Stamp volatile facts” and stages the altered state file.
- [Bixi #8](https://github.com/roethlar/Bixi/issues/8): an accepted plan
  omits the committed state file containing a recorded push status;
  `--apply` with `--stage-only` nevertheless repairs and stages that file.
- All four were reproduced in disposable repositories using the fixture
  helpers in `tests/test_refresh.py`, with Python 3.14.10. The development
  worktree was unchanged. These observations do not constitute a suite run.
- G1 evidence is the owner's supplied incident transcript: a settled
  exclusion was omitted from a checklist, repeated by a stop-check, and
  treated as permission to expand an approved plan. Historical volume is
  a plausible contributor, not an independently proven cause. The source
  project's complete records and original execution trace were not inspected.
  Its platform policy must not be inferred or rewritten by this toolkit work.

## F5 — respect Git's effective ignore result

Files: `tools/refresh.py`, `tests/test_refresh.py`.

Use the non-verbose Git ignore result for the yes/no decision in
`check_committability`; obtain verbose provenance only for an actual
ignore. A negation match is not an ignore. Handle unexpected Git probe
errors as errors, not as permission to install. Preserve the existing
narrow adapter-directory repair and never use force-add.

Acceptance: whitelist fixtures re-including AGENTS.md and CLAUDE.md plan,
install and stage both without flags. Truly ignored paths still skip,
including under an excluded parent; literal escaped exclamation patterns
are not mistaken for negation. Existing blanket-adapter repair coverage
stays green. The re-inclusion regression must fail against the old code.

## F6 — retain the reason a core target was blocked

Files: `tools/refresh.py`, `tests/test_refresh.py`,
`procedures/bootstrap.md`, `templates/playbooks/update-governance.md`.

Keep foreign-content and ignore-skip causes distinct internally. Preserve
the public plan record's existing flags representation in this slice;
do not infer a cause by parsing human-readable reason strings. Only a
foreign-content cause may drive the foreign banner, legacy migration
prompt, or foreign-replacement override.

For an ignore skip, name the actual matching rule and source location,
explain that installation was skipped, and direct the owner to resolve
custody/ignore policy. Do not propose a legacy migration or replacement
of a file that is absent. Preserve exit 5 for an unresolved core target,
and clarify its documentation to cover both causes; retain existing
non-core skip behavior. The `--force` foreign-content override must still
pass committability checking and cannot make ignored paths writable.

Acceptance: ignored absent core, genuine foreign core, and a mixed case
produce the correct independent explanations. Genuine foreign content
retains its existing recovery route. `--force` cannot convert an ignore
skip into a foreign replacement. No false legacy prompt appears for the
ignored-only case. The absent-core case must fail on the old code.

## F7 — distinguish state instructions from live entries

Files: `tools/refresh.py`, `tests/test_refresh.py`.

Limit the existing push-status removal to the live body beginning at the
first level-two heading. Preserve everything above it verbatim. If a
legacy document has no such heading, leave it unchanged rather than
guessing which prose is an instruction. Keep the template wording and
dirty-file protection; changing only the current template would leave
already-created state files vulnerable.

Acceptance: repair over the actual state template is byte-preserving;
with a genuine recorded push status below a heading, only the record is
removed. Verify header-only/no-heading files, ordinary work items, push
policy text, dirty state, and a second idempotent run. The real-template
preservation check must fail without this fix.

## F8 — plan repairs before any target write

Files: `tools/refresh.py`, `tests/test_refresh.py`,
`procedures/bootstrap.md`, `templates/approval-summary.template.md`.

Refactor the three existing repairs into read-only planning followed by
application of the computed result. Do not weaken the approval summary's
promise or exempt repairs from it. Ordinary refresh, `--stage-only`, and
`--apply` use the same planning and application path.

1. Build an in-memory view of candidate files and their original Git
   dirtiness. Compute push-status removal, moved-reference repair, and
   closed-decision archiving in their established order. Compose overlapping
   transformations into one final result per path; an earlier planned
   repair must not be mistaken for a pre-existing owner edit.
2. Keep already-dirty repair inputs untouched, including either side of
   the decisions/archive pair. Include a newly created archive when one
   is needed. Preserve existing lint-allow markers and archive text.
3. Introduce plan schema 3. Each repair records its target, action/reason,
   input content hash or explicit absence, output hash, and readable diff.
   Include repairs in the digest and de-duplicated `staged_paths`.
   Capture the archive date as plan data: applying an unchanged approved
   plan across midnight must not silently change its bytes or fail solely
   because today's date changed. Validate that date when loading a record.
4. On `--apply`, recompute the same result from current inputs and the
   recorded date, then compare the complete operation before any write.
   Reject old-schema records with an instruction to regenerate and
   reapprove. Do not silently upgrade their incomplete authorization.
5. Preflight all planned destinations, including repair outputs, with the
   existing safe-destination and custody protections. A changed repair
   input, changed eligibility, unsafe destination, or plan mismatch must
   refuse before target files or index change. Preserve existing treatment
   of unrelated dirty/staged work and `already_staged` shipped paths.
6. Apply only the computed, verified bytes, then stage/commit the announced
   set. Remove the post-verification repair calls. No late repair may add
   a path that the approved record did not contain.
7. Render the approval summary from the record, naming mechanical repairs
   as their own group with reasons/diffs. Include installs, updates,
   restores, removals, ignore-file repairs, and already-staged shipped
   paths in the complete accounting. Reconcile any repair target that is
   also a judgment-draft destination; neither overwrite order nor duplicate
   listing can authorize unreviewed bytes. Step 7 must explain how to
   regenerate the plan when copying drafts changes planned repair inputs.

Acceptance: independently cover all three repair types; an absent and an
existing archive; overlapping repairs; dirty inputs; unrelated staged work;
an ignored new archive; and unsafe repair destinations. `--plan-json`
leaves target files, index and HEAD unchanged. Its paths and output hashes
match the subsequent apply. Input drift refuses without writes. Same-input
plans are deterministic for the same recorded date, and midnight does not
invalidate a plan. Existing schema-2 plans refuse clearly. Exercise plain
refresh, stage-only, and approved apply. The original omission regression
must fail against the old code; each new safety guard needs a meaningful
negative control.

## G1 — surface operative boundaries, keep rationale in history

Sources: `templates/repo-guidance.template.md`,
`templates/state.template.md`, `templates/decisions.template.md`,
`templates/AGENTS.template.md`, `templates/playbooks/plan.md`,
`templates/playbooks/drift.md`, `templates/playbooks/codereview.md`,
`templates/playbooks/openreview.md`, `procedures/setup.md`,
`procedures/bootstrap.md`, `procedures/verification.md`, `docs/design.md`.
Use `tools/shipped-set.json` for affected artifact provenance and
`tests/test_templates.py` for necessary structural regression coverage.

The operative rule belongs in one home. Prefer an early “Product
boundaries” section in repo guidance for concise, consequential exclusions
and settled choices. Where an existing active specification already owns
the full contract, use a direct section pointer and require that section
in the task's reading path; do not create a second competing rulebook.
Keep historical rationale linked and outside routine startup reading.

Proposed lifecycle and behavior:

- Populate the boundary section only from evidenced, adopted decisions.
  Select constraints whose omission would lead to unwanted work or a
  wrong completion judgment. Distinguish settled exclusions from untested
  assumptions and pending choices. Include any scope-limiting exception;
  shortening a statement must not broaden it.
- Give each settled ruling an operative home before marking its decision
  rationale adopted/archivable. Preserve provenance and archive rationale
  verbatim. The cleanup sweep flags an uncertain or homeless rule; it
  neither invents a replacement nor reopens settled policy. Existing
  source records remain authoritative until a precise transfer is adopted.
- Keep the current approved scope, non-goals, assumptions and pending
  decisions at the top of each active plan. An amendment updates that
  current contract only after the applicable owner ruling; older reasoning
  remains historical. State points to the active plan and next action,
  rather than copying permanent product policy or growing a second history.
- Adjust the AGENTS startup/source-of-truth wording so the active approved
  plan and its relevant boundaries are read before scope or completeness
  judgments. An agent-written status/checklist cannot supersede owner
  scope. Use one canonical general rule for finding/completion intake:
  trace a claimed gap to its requirement and check settled exclusions;
  repetition by another agent or a stop-check supplies no new authority.
- Review playbooks direct reviewers to discover current constraints from
  the pinned repository. Dispatch carries source coordinates, never an
  author's restatement of policy. Preserve openreview's unprimed question.
  Apply the same scope check to agent responses to completion/stop-check
  feedback. Bixi does not own the incident's stop-check implementation;
  this change must not claim to modify or enforce that external mechanism.
- Bootstrap/setup seed the new reading structure. Existing governed repos
  need a scoped judgment-file migration before benefiting fully; refresh
  must not overwrite their repo-owned guidance. Describe that adoption
  path, without running a fleet migration or self-refresh here.

Keep AGENTS at or below its current token count using the same tokenizer
before and after, preserving all load-bearing rules and one-line
paragraphs/bullets. Record the earning incident and exact rule changes in
the decisions record. Do not add per-turn injections, a new ledger,
automated policy inference, a mandatory archive search, or arbitrary
content quotas that could discard a consequential constraint.

Acceptance: extend the existing fresh-eyes rehearsal with a small fixture
containing (a) a settled feature exclusion with a narrower supported
fallback, (b) an unverified assumption, and (c) a superseded historical
proposal. From normal startup files and their direct current pointers,
a fresh reviewer must distinguish excluded work from a defect, preserve
the fallback, leave the assumption unresolved, and apply the current
ruling. It must not need to search archives. Remove the current boundary
as a negative control: report missing authority, not an invented policy.
Check that a newly adopted owner amendment supersedes the old boundary
without promoting old history. Record observed behavior and limitations;
this proves discoverability, not guaranteed model obedience. Structural
tests guard routing/pointers, not exact prose. Update formerly-shipped
hashes where required; all installed copies remain untouched here.

## Verification and records

Use the Python interpreter selected by bootstrap's probe order. On this
machine `py` is absent and `/usr/bin/python3` is Python 3.14.10.

- Planning-only gate: `python3 -m unittest tests.test_plan_lint -v` and
  `git diff --check`. Do not claim code regression coverage from these.
- Each approved implementation: `python3 -m unittest discover -s tests -v`,
  plus the item's acceptance cases and fail-without-fix/pass-with-fix proof.
  Broaden/repeat checks only after relevant changes or failures.
- G1 additionally requires token measurements and the manual fresh-context
  rehearsal. Automated prose assertions alone cannot establish its result.
- Record one finding per implementation commit, source-rule provenance in
  `.agents/decisions.md`, and current work through `.agents/state.md`.
  Follow the git playbook through any authorized integration/deletion;
  batch public release via `tools/publish` when separately authorized.

## Plan review and pending steps

Planning branch: `plan/bixi-issues-2026-11-17`, based on the baseline above.
Reviewer requested by the owner: Claude Code, literal model
`claude-fable-5-2`, effort `xhigh` (inline, session-only). No default or
provider substitution is authorized. Perform an unprimed whole-plan
approach review from a committed snapshot; record pins, harness version,
dispatch identity, capability proof, verdict and material recommendations.
Objective corrections within this planning request may refine the draft;
unsettled policy choices remain explicit proposals for the owner.

Pending: finish the requested review and return an executive summary;
obtain implementation go separately for F5, F6, F7, F8 and G1. No product
changes, public issue posting/closure, publish, target-repo migration,
or owner-only self-refresh is authorized by this planning request.
Plan-branch merge/deletion authority has not been given.
