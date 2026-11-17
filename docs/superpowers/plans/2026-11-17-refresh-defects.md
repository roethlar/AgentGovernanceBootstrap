# Plan: four refresh correctness defects

Status: APPROVED 2026-11-17 — owner approved F5, F6, F7 and F8; implementation in progress.

## Current contract

Repair four open Bixi refresh defects. Preserve existing owner decisions,
ignore rules, uncommitted work, and the distinction between evidence and
authority. This document proposes changes; it adopts no new product policy.

| ID | Independently approvable outcome | Implementation authority |
|---|---|---|
| F5 | Correctly install files explicitly re-included by Git ignore rules | Approved 2026-11-17 |
| F6 | Distinguish ignore skips from foreign governance and route recovery correctly | Approved 2026-11-17 |
| F7 | Preserve the state template's instruction header during repairs | Approved 2026-11-17 |
| F8 | Make planned, approved and applied mechanical repairs agree | Approved 2026-11-17 |

Suggested order: F5, F6, F7, F8. F5–F7 make small, independently
verifiable corrections before F8 restructures the shared repair path.
Each item gets its own implementation commits and evidence; F8 has the
three dependent slices below. Approving one
does not approve the others. Publish the approved fixes together afterward,
only with release authority. Planning/review completion is distinct from
implementation, integration, and publication.

The related governance issue has an independent lifecycle in
[the current-boundaries plan](2026-11-17-current-boundaries.md).

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
skip into a foreign replacement. Include an ignored, present, untracked
foreign core file under `--force`: its bytes must survive and no false
claim that Git preserves them may appear. No false legacy prompt appears for the
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

Limit: this slice protects the instruction header. The existing body-level
regex can still mistake a discussion of push status for an actual status
record. It does not establish a general semantic Markdown repair. Record
that residual separately rather than silently expanding this issue.

## F8 — plan repairs before any target write

Files: `tools/refresh.py`, `tests/test_refresh.py`,
`procedures/bootstrap.md`, `procedures/verification.md`,
`templates/approval-summary.template.md`.

Delivery slices, each with its own checks/record and no intermediate public
release: F8a extracts deterministic repair computation and composition behind
the existing application flow, preserving externally visible behavior.
F8b switches the runtime to the complete plan/preflight/apply protocol below,
including schema, prepared-path handling and both target-pin modes.
F8c updates bootstrap, rehearsal and summary instructions together and
rehearses both routes. These are dependent implementation slices; the issue
remains open and nothing is published until all three acceptance gates pass.

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
   as their own group with short plain-English reasons. Keep detailed
   diffs in the machine-plan artifact, linked from the summary; preserve
   its existing one-screen recommendation, not an inline diff dump.
   Include installs, updates, restores, removals, ignore-file repairs, and
   already-staged shipped paths in the complete accounting.
8. Resolve draft collisions explicitly: bootstrap passes each approved
   judgment-draft destination using repeatable `--draft-path PATH` options
   when generating the plan. Normalize/validate repo-relative paths and
   record a sorted, de-duplicated `draft_paths` list in schema 3 and its
   digest. Those files are owned by the reviewed drafts for this operation
   and are excluded from mechanical repair computation. If either side of
   a paired decision/archive move is reserved, skip that entire move;
   continue independent repairs to other paths. The summary shows the
   judgment-draft group and explicitly explains these exclusions.
9. `--apply` derives the same exclusions only from the approved record;
   conflicting command-line exclusions refuse. Copying those approved
   drafts before apply is the expected bootstrap sequence, not drift in
   repair eligibility. Adding a different destination requires a new plan
   and approval. Ordinary refresh has no draft exclusions and continues to
   repair in the run. The existing already-staged scope-only contract is
   unchanged; this does not add content pinning for judgment drafts.
10. Treat approved supersession-banner targets as prepared paths too: pass
    them through the same recorded `--draft-path` mechanism, since bootstrap
    changes their bytes before apply. If a listed destination is a repo-owned
    manifest seed, suppress that seed's install as well: the reviewed draft
    supplies it. Do not suppress ordinary shipped-artifact installs or
    bypass foreign-core custody. Without a listed destination, seeding keeps
    its present behavior. Include these cases in the approval accounting.

### Legacy carve-out: approve the rehearsed second operation

The legacy route still has exactly two commits, but its second operation
must come from a machine record generated after rehearsing the first.

- Freeze commit 1's inputs before rehearsal. Preserve an already-settled
  push policy; if its choice is unresolved, settle it before generating the
  record. The summary must not invite a new policy choice against a frozen
  tree. If an approval response requests edits to any commit-1 file or
  changes its scope, regenerate the rehearsal record and summary before
  making commit 1. The standard route's scope-only draft contract stays as
  it is; this stricter sequencing applies to the legacy tree-pinned route.
- In the existing fresh-eyes scratch clone, replay exactly the proposed
  carve-out commit: copy drafts, apply banners, delete the foreign core
  file, and commit. Before installing the shipped set there, generate the
  second operation with `--plan-json` and a new planning-only
  `--carve-out-base <original-target-head>` option. Save that record outside
  the scratch clone for the approval summary. Use no draft exclusions: the
  copied drafts are now committed inputs, so any repair of them is visible.
- Schema 3 expresses two explicit target-pin modes. Standard records pin
  the target HEAD exactly as today. A carve-out record pins the original
  target HEAD as the required single parent of commit 1 and pins the entire
  post-commit-1 Git tree from the rehearsal. Validate this ancestry when
  generating the record; do not infer the base from an arbitrary branch.
  Record the normal toolkit, manifest, repair-date and operation pins too.
- Rehearsal installs by applying that saved record. The summary presents
  both commit scopes, including the resulting repair paths/reasons/diffs
  from the second record. A repaired draft's final bytes are therefore
  available for approval, including any newly created archive.
- Before making real commit 1, perform a read-only preflight of the record
  and the pins that can already be checked: original target HEAD, toolkit
  SHA/cleanliness, and manifest digest. Confirm the prepared files still
  match the approved frozen inputs. A known mismatch requires a regenerated
  record and summary before any real carve-out mutation, not after the
  legacy core file has been deleted. Keep the post-commit-1 checks too.
- In the real repo, make the approved first commit, then run `--apply` on
  the approved rehearsal record in committing mode for commit 2. It must
  verify the first commit has exactly the pinned parent and tree, then
  recompute and compare all normal operation/input/output pins before
  writing. Commit metadata may differ between rehearsal and reality;
  content, parent, and planned operation may not. There is no generic
  ignore-HEAD flag, automatic rebinding, or fallback to ordinary refresh.
- A mismatch refuses before commit 2 writes anything and leaves the
  already-created commit 1 in place for inspection. Replanning requires
  the ordinary fresh approval. If a rehearsal cannot be made, this route
  cannot claim a complete approval preview; stop before presenting it as
  ready instead of silently using an unplanned second operation.

The rehearsal's fresh reader must inspect the result of applying the second
record. Do not re-copy the original drafts over repaired files afterward;
adjust the existing verification procedure's recopy step for this route.

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

Also rehearse the standard bootstrap sequence with a clean state/decision
file that needs repair and an approved draft replacing it: generate with
draft destinations, copy drafts, then apply once without a second approval.
The copied bytes survive, independent repairs still match their record,
and paired moves cannot archive draft-owned content. Exercise a malformed
or changed exclusion list, a bannered repair target, and an absent seeded
push policy supplied by an approved draft. In the last case, the reviewed
draft is the only proposed write; an unreserved missing policy still seeds.

For the legacy route, include a draft containing an archivable decision so
commit 2 must add an archive; the approved rehearsal record and actual
commit must agree on paths and output bytes. Different commit-1 metadata
with the same parent/tree succeeds. Wrong parent, extra/missing/changed
commit-1 files, different toolkit, and different repairs all refuse before
commit-2 writes. Standard mode still rejects any target-HEAD drift. Rehearse
both commit messages/scopes and preserve unrelated staged work. No claim
of whole-filesystem atomicity is added beyond validation before writes.
Cover a non-default push policy settled before rehearsal, an “approve after
edits” response that changes a prepared file, and base/toolkit/manifest
drift before commit 1. The latter cases must trigger replanning before
real carve-out writes. Check that rehearsal inspection sees the final
repaired draft bytes, not an overwritten pre-repair copy.

## Verification and records

Use the Python interpreter selected by bootstrap's probe order. On this
machine `py` is absent and `/usr/bin/python3` is Python 3.14.10.

- Planning-only gate: `python3 -m unittest tests.test_plan_lint -v` and
  `git diff --check`. Do not claim code regression coverage from these.
- Each approved implementation: `python3 -m unittest discover -s tests -v`,
  plus the item's acceptance cases and fail-without-fix/pass-with-fix proof.
  Broaden/repeat checks only after relevant changes or failures.
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

First verdict: Acceptable with changes. F5–F7 supported; F8 needed a
concrete draft-collision design and delivery slices. Those draft changes
are incorporated above. G1 was separated and narrowed. See
[review provenance and dispositions](../../../.agents/review/2026-11-17-plan-review.md).

Review completed across three Claude passes. The last verdict was
Acceptable with changes at `eb147f4`; its prescribed input-freeze/preflight
and rehearsal-readout clarifications are incorporated above. Those final
clarifications were not sent for another review. Plan-lint and whitespace
checks are the planning validation; no implemented fix is being certified.

Implementation approved for F5, F6, F7 and F8; verification and integration are pending. No product
changes, public issue posting/closure, publish, target-repo migration,
or owner-only self-refresh is authorized by this planning request.
Integration and deletion of the named plan branch were approved with the executive summary.
