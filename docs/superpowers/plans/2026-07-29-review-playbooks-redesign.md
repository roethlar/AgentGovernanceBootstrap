# Plan: reallocate the review playbooks — codereview reviews landed changes, openreview judges approach soundness

Status: DRAFT 2026-07-29 — owner ruling authorized drafting this plan and
one openreview smoke dispatch of the plan's own commit (codex,
gpt-5.6-sol) using the Design below; template implementation awaits a
separate owner go after the smoke review's outcome is reported.

## Problem

GitHub issue #11 reports that an openreview dispatch on a design-heavy
change returned a narrow file-consistency defect audit instead of an
independent judgment of the approach. The root cause is structural, not
a single bad prompt — the two shipped review playbooks have their roles
misallocated:

1. The defect-audit verdict contract (`clean|findings`, each finding
   carrying evidence, predicted failure, severity, better approach)
   lives in `templates/playbooks/openreview.md`, whose documented
   purpose is an unprimed goal-first judgment. The contract's shape
   biases any reviewer toward enumerating discrete defects, defeating
   the playbook's purpose.
2. `templates/playbooks/codereview.md` cannot generate a review at all:
   it verifies pre-supplied findings against their records ("whether
   findings come from a human, the coder, a separate review pass, or a
   second model"). "Review this landed change for defects" has no home
   in the toolkit; generation has been ad hoc.
3. codereview's fix mechanics are pre-merge — per-finding branch,
   accepted verdict → owner-gated merge — while governed repos land work
   per slice on the default branch (`AGENTS.md` Prime Invariants). The
   playbook already concedes branches are internal mechanics, but its
   accepted-verdict ending still assumes an unmerged branch.
4. openreview's fixed question "Is the code as implemented the best way
   to achieve the goal?" has no sensible reading when the reviewed
   change is a plan or design document — the case issue #11 hit.

## Design

The transport layer is untouched in both playbooks: probe-and-verify
incantation derivation, `.agents/review/harnesses.local.json` cache and
tier→pair routing, self-permissioning launch, pinned base/head SHAs,
`capability_ok` proof, `Reviewer:` provenance lines, JSON envelope,
fail-closed parsing with extraction-before-rejection and the single
re-emission re-prompt. Only the semantic layer moves: what question each
playbook asks and what shape each answer takes.

### openreview → approach-soundness review

`templates/playbooks/openreview.md` keeps its unprimed framing, fixed
frontier-tier routing, and grade-based eligibility. Changes:

- The reviewed object is "a change" throughout — implementation, plan,
  or design document; the playbook says so explicitly.
- The substantive prompt becomes exactly:

  > From your own reading of the repository, state the goal this change
  > serves and how you would achieve it. Then judge: is the change as
  > made the best way to achieve that goal?

  That stays the whole substantive framing; the mechanical coordinates
  (workspace, base/head SHAs, worktree isolation, side-effect
  boundaries, verdict schema) are unchanged in kind.
- The verdict contract is replaced. New result payload schema:

  ```json
  {"verdict":"best_approach|acceptable_with_changes|replace",
   "capability_ok":true,
   "reviewed_sha":"<head-sha>","base_sha":"<base-sha>",
   "goal":"<one sentence: the goal the reviewer discovered>",
   "recommended_approach":"<how the reviewer would achieve the goal>",
   "comparison":"<how the reviewed change compares with that approach>",
   "material_changes":["<change that should be made>"],
   "findings":[{"title":"…","evidence":"file:line — …",
    "predicted_failure":"…","severity":"CRITICAL|HIGH|MEDIUM|LOW",
    "better_approach":"…"}]}
  ```

  Verdict semantics: `best_approach` — the change's approach is the one
  the reviewer would take (or better); `material_changes` must be empty.
  `acceptable_with_changes` — the approach stands but the listed
  material changes should be made; `material_changes` must be
  non-empty. `replace` — the reviewer's `recommended_approach` should
  supplant the change's; `material_changes` must be non-empty.
  `findings` stays optional at every verdict (empty list allowed) and
  keeps the codereview intake shape.
- Fail-closed acceptance adds the enum and the
  `material_changes`-emptiness rule above to the existing transport
  checks; everything else (SHA pins, `capability_ok`, envelope, parse
  handling) is unchanged.
- Downstream: `findings` entries still enter the codereview intake gate
  unchanged. `recommended_approach`, `comparison`, and
  `material_changes` are design judgments, not defect findings — they
  route to the owner, who rules what is adopted. The recorded outcome
  line gains the verdict word:
  "openreview <agent> (<model> @ <effort>, <grade>) over <base>..<head>:
  <verdict>".

### codereview → landed-change defect lifecycle

`templates/playbooks/codereview.md` keeps everything it has — tiers,
escalation triggers T1–T5, dispatch grammar, intake/triage, per-finding
flow, guard proofs, records, index — and gains a generation front half
plus landed-fix mechanics:

- New section "## Change review (defect generation)" ahead of intake.
  Grammar: `codereview <harness> <model> <effort> <base>..<head>` — a
  trailing pinned commit range dispatches a whole-change defect review
  of landed commits. Without a range, the verb continues the active
  per-finding loop exactly as today. Range endpoints are SHAs resolved
  at dispatch; the reviewer evaluates `git diff <base-sha>..<head-sha>`
  from the shared workspace under the same self-permissioning grant.
- The generation pass uses the `clean|findings` verdict contract,
  moved verbatim from openreview (one canonical location — it appears
  only in codereview after this change):

  ```json
  {"verdict":"clean|findings","reviewed_sha":"<head-sha>",
   "base_sha":"<base-sha>","capability_ok":true,
   "findings":[{"title":"…","evidence":"file:line — …",
    "predicted_failure":"…","severity":"CRITICAL|HIGH|MEDIUM|LOW",
    "better_approach":"…"}]}
  ```

  Fail-closed rules move with it, including findings/verdict
  consistency. A `clean` verdict is a complete, valid result recorded
  with provenance, exactly as the intake section already insists.
- Every returned finding passes the existing intake/triage gate before
  any work; ADMITTED findings enter the per-finding flow. Tier routing
  for generation: standard by default; T1 (sensitive paths) evaluates
  against the range diff pre-dispatch; the owner `frontier` force
  applies as everywhere. T2–T5 are per-finding and unchanged.
- Per-finding fix mechanics become policy-relative. Where repo policy
  lands work per slice on the default branch, the loop's atomic unit is
  "one finding ↔ one commit ↔ one verdict": the fix lands as one
  commit; the verify dispatch pins base = pre-fix head, head = post-fix
  head; the guard proof still runs in the reviewer's disposable
  worktree; `accepted` closes the finding and its paperwork in the same
  motion (no merge step exists); `reopened` → follow-up commit, never
  an amend; `invalid` → contested, unchanged. Where repo policy uses
  branches, the current per-finding branch mode with owner-gated merge
  stays available. The "Atomic unit" and "Per-finding flow" sections
  are reworded to carry both modes; the branch mode's text is otherwise
  preserved.
- The "Framing" paragraphs in both playbooks are reworded to describe
  the new split: codereview = defect review of landed changes plus
  per-finding verification; openreview = approach-soundness judgment of
  a whole change, code or plan. The owner still selects per invocation,
  by name.

### Wrappers, skills, and repo guidance

One-line semantics updates, no structural change:

- `templates/commands/claude/codereview.md`,
  `templates/commands/claude/review.md`,
  `templates/skills/shared/codereview/SKILL.md`,
  `templates/skills/shared/review/SKILL.md` — description covers both
  halves: review a landed change for defects (optional
  `<base>..<head>` range) and verify each finding's fix against its
  record.
- `templates/commands/claude/openreview.md`,
  `templates/skills/shared/openreview/SKILL.md` — "unprimed
  approach-soundness review of a whole change — implementation or
  plan".
- `.agents/repo-guidance.md` (Earned Practices, repo-owned): update the
  bullet describing the two playbooks' split.

## Smoke test (precedes implementation)

One openreview dispatch of this plan's own commit, run under the Design
above in place of the installed contract — the dispatch prompt carries
the new substantive question and verdict schema. This validates the new
shape on exactly the change-type issue #11 hit (a plan) before any
template edit.

- Object: base = `1577754c1901ce055cbcf08b5e76a047dc5f9ff4` (pre-plan
  HEAD), head = the commit that adds this plan.
- Reviewer: codex / gpt-5.6-sol — the machine cache's frontier pair,
  grade `competitive`, so openreview-eligible without a further ask.
  Effort: the recorded pair's `xhigh` (the harness exposes no higher
  level; the recorded pair is authoritative, per the playbook).
- Mechanics per the shipped openreview playbook: derived incantation,
  self-permissioned launch, pinned SHAs, JSON envelope, fail-closed
  parse with one re-emission re-prompt, provenance from the invocation
  transcript. Allowlisted capability-proof command: the plan-lint gate
  from `.agents/repo-guidance.md` (Verification).
- Outcome handling: transport result and verdict are recorded in this
  plan (Smoke result below) with the provenance line; all
  `material_changes` and `findings` go to the owner — nothing enters
  intake or implementation without the owner's per-item go.

### Smoke result

Pending dispatch.

## Implementation

No template edit begins until the owner's post-review go is recorded in
the Status line.

### Slice 1 — openreview redesign (closes issue #11)

One commit:

1. `templates/playbooks/openreview.md` — Design above.
2. `templates/commands/claude/openreview.md`,
   `templates/skills/shared/openreview/SKILL.md` — description updates.
3. `tools/shipped-set.json` — append the outgoing normalized SHA-256
   (`nhash` in `tools/refresh.py`) of each edited artifact to its
   `formerly[]`.
4. `tests/test_templates.py` (`PlaybookReviewMechanics`) — add a
   structural pin: openreview body contains
   `best_approach|acceptable_with_changes|replace`,
   `recommended_approach`, and `material_changes`, and does not contain
   `clean|findings`. Existing openreview pins (frontier, "Reviewer
   tiers and routing", "owner-named") stay green.

### Slice 2 — codereview generation half and landed-fix mechanics

One commit:

1. `templates/playbooks/codereview.md` — Design above.
2. `templates/commands/claude/codereview.md`,
   `templates/commands/claude/review.md`,
   `templates/skills/shared/codereview/SKILL.md`,
   `templates/skills/shared/review/SKILL.md` — description updates.
3. `tools/shipped-set.json` — `formerly[]` appends as in Slice 1.
4. `tests/test_templates.py` — add a structural pin: codereview body
   contains "## Change review (defect generation)",
   `<base>..<head>`, and `clean|findings`. Existing codereview pins
   (tiers, T1–T5, dispatch grammar, self-permissioning) stay green.

### Slice 3 — record close

1. `.agents/repo-guidance.md` — Earned Practices bullet update.
2. Close GitHub issue #11 with a comment naming the landing commits.
3. `.agents/state.md` — landed entry; plan Status → CLOSED with
   verification results.

## Verification

Interpreter per `.agents/repo-guidance.md` (Verification); on this
machine `python3.14` per `.agents/machines.md`.

1. `python3.14 -m unittest discover -s tests -v` after each slice.
2. Guard proof for each new structural pin (`AGENTS.md` Verification):
   with the pin retained, temporarily revert the paired playbook edit
   in the working tree; the pin must fail; restore; rerun green.
3. `git diff --check`.
4. This plan file: `python3.14 -m unittest tests.test_plan_lint -v`.

## Rollout boundary

Landing in this repo changes what ships, not what is installed
anywhere: this repo's `.agents/playbooks/` and `.claude/commands/`
copies lag until the owner's self-refresh from the product clone, and
Bixi receives the change only on the owner's `publish` word. Neither
action is authorized by this plan.
