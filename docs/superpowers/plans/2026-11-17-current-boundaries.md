# Plan: make consequential current boundaries directly discoverable

Status: COMPLETE 2026-11-17 — G1 verified and integrated into master; work branch deleted. Published to Bixi; receiving-repo migration remains separate.

## Current contract

G1 improves discoverability of existing, adopted constraints. It does not
invent product policy, reopen settled decisions, or grant findings authority
to expand scope. Put the operative boundary in startup text and put the
active task's current contract above its amendment history. Validate that a
fresh reader can distinguish exclusions, assumptions and current rulings.

The four refresh defects have their own approval/status lifecycle in
[the refresh plan](2026-11-17-refresh-defects.md). Neither plan waits for
implementation approval of the other. Planning branch:
`plan/bixi-issues-2026-11-17`, based on `0574fd1`.

## Evidence and bounded diagnosis

The [incident record](../../../.agents/review/incidents/2026-11-17-scope-expansion.md)
contains transcript evidence, independently checked source commits and
the remaining uncertainty. At the pre-amendment commit, the mandatory
guidance offered a less precise Wayland-first summary while the exact X11
exclusion lived at line 776 of a 2,711-line plan; decisions occupied 2,567
lines and state 551. That organization is verified. What the process
actually read, and whether record volume caused its disobedience, remain
unverified. Later owner clarifications supersede older descriptive text.

This supports a targeted discovery improvement, not a claim that another
prohibition would have prevented the incident. Existing explicit-go,
finding-intake, decision-lifecycle, and archive rules already cover
authority. Keep them. A synthetic fixture with a permitted fallback is a
test of preserving qualifiers, not a statement of the source project's
current platform policy.

## Proposed changes and exact wording

The owner's G1 approval covers the two source behaviors below and their
verification. Receiving-repo product decisions remain outside this scope.

### 1. Put consequential adopted boundaries in the existing startup file

Add this section immediately after Mission Detail in
`templates/repo-guidance.template.md`:

```markdown
## Product boundaries
<!-- State consequential adopted exclusions and constraints here in full,
     including their exceptions. Keep the operative wording precise and
     short; link to evidence and rationale, not to an unread rule.
     Distinguish settled decisions from assumptions and pending choices.
     When moving a rule here, replace its former operative copy with a
     pointer; preserve its provenance. If none are established, say so
     without inventing constraints or reopening settled choices. -->
```

This makes the existing one-home rule concrete. Binding wording is inline
in a file startup already requires. Only evidence/rationale remains behind
links, satisfying the 2026-07-25 point-of-use ruling. Detailed specs still
own their implementation detail; this section owns the adopted high-level
boundary. Transfer cannot silently narrow an exception or broaden a ban.

No AGENTS text is added, removed or displaced. Its existing startup,
authority and verification requirements remain byte-identical, so its
token ceiling is unaffected. State, decisions, drift and review playbooks
also retain their existing authority/lifecycle rules. Do not duplicate
them in new prose or create a new facts ledger.

### 2. Keep an active plan's current contract above its history

After the existing cold-agent paragraph in `templates/playbooks/plan.md`,
add:

> Keep the current approved task scope, task-specific non-goals, assumptions
> and pending choices at the top, before rationale and amendment history.
> Apply an adopted amendment to that current contract; do not make readers
> reconstruct it from a chronological log. Keep permanent product boundaries
> in the already-read repo guidance rather than copying them into each plan.

This changes the location and maintenance of existing plan information,
not who can approve an amendment. Archive rationale under the existing
decision/hygiene rules only after its operative conclusion has a home.
No mandatory whole-history search, automatic policy inference, arbitrary
content quota or per-turn instruction injection is introduced.

## Adoption and file scope

Source edits: `templates/repo-guidance.template.md`,
`templates/playbooks/plan.md`, `procedures/verification.md`,
`procedures/bootstrap.md`, `procedures/setup.md`,
`templates/approval-summary.template.md`, and `docs/design.md`.
The latter procedure/template changes wire the same two proposed behaviors;
they add no new operator or authority rule.
`tools/shipped-set.json` records the outgoing plan-playbook
hash; `tests/test_templates.py` may gain only meaningful structural checks
needed by the changed route. Record the adopted rule and incident provenance
in `.agents/decisions.md`; keep current status in `.agents/state.md`.

Bootstrap and new-project already draft repo guidance from its template.
Update their explicit section lists to include Product boundaries so both
routes populate it. Do not add new setup questions when the owner
has supplied no constraints. Existing repositories need a separately scoped
judgment-file update: inspect relevant current decisions, propose exact
transfers, preserve exceptions, and replace former operative copies with
pointers. Document this path in `docs/design.md`. Refresh keeps repo-owned
guidance intact. No fleet migration, Vela edit, or owner-only self-refresh
is part of G1.

Reviewers discover these boundaries through their existing repo startup
instructions; openreview's unprimed prompt stays unchanged. Nothing here
modifies the incident's external stop-check. If a check does not read the
same governing files, this change does not fix that integration. Record
that limitation rather than claiming enforcement that Bixi does not own.

## Acceptance and verification

Extend `procedures/verification.md`'s existing fresh-eyes questions with:

> Which consequential product boundaries and task-specific non-goals apply?
> Distinguish adopted exclusions from assumptions and pending choices. Cite
> their current operative wording. If asked to treat an excluded feature as
> a missing capability, what existing authority would permit that change?

An explicit “none established” or “no active plan” is valid when supported
by the repo; absence of a not-yet-needed policy is not a missing-guidance
defect. Update the approval summary's example from “all six questions” to
“the verification questions” so it does not retain a stale copied count.

Use a small, neutral rehearsal repository with a narrow settled exclusion,
an explicitly permitted fallback, an unverified hardware assumption, and a
superseded proposal. Supply only normal startup files with the operative
statements inline; keep rationale/history outside the reading set. A fresh
reader must preserve the fallback, reject the excluded item as an authorized
gap, leave the assumption unresolved, and identify the current ruling.

Negative control: remove the operative boundary from startup text while
keeping an archival link; report the missing current operative statement.
Reconstructing an answer from history does not pass this discoverability
check, even if that answer is correct. Then change the fixture through
an explicitly adopted owner amendment: the new current contract must win
over old history. Record the harness, inputs, outputs, and observed limits.
This is a manual discoverability rehearsal, not a guarantee of obedience
or a new automated benchmark system. A failed rehearsal leaves G1 open.

Do not change existing mandatory startup behavior to make the test pass.
Verify the installed rehearsal actually loads/reads repo guidance and the
active plan where applicable. A pointer that is never read is a failure.

Implementation verification: the repo's full Python unittest entry point,
`git diff --check`, the rehearsal above, source-rule provenance, and any
required outgoing artifact hashes. No exact-sentence tests substitute for
the rehearsal. AGENTS must remain byte-identical. Planning-only checks are
`python3 -m unittest tests.test_plan_lint -v` and `git diff --check`.

## Review and pending decisions

Claude `claude-fable-5-2` at `xhigh` reviewed the original combined draft
and returned Acceptable with changes. This separate proposal responds by
recording source evidence, narrowing the scope, giving exact wording,
removing the indirect binding-rule option and leaving AGENTS unchanged.
[Review provenance](../../../.agents/review/2026-11-17-plan-review.md).

Claude's follow-up judged the narrowed G1 approvable as an approach. Its
adjacent procedure-wiring/grading corrections were confirmed in the final
pass. This is a plan verdict, not implementation or owner approval.

G1 implementation and the named plan branch's integration/deletion are
approved. Verification is in [the G1 finding](../../../.agents/review/findings/G1.md);
closeout is recorded in [the completion receipt](../../../.agents/review/2026-11-17-completion.md).
No source-project product
ruling is adopted; publication was subsequently authorized and completed as recorded in that receipt.
Receiving-repo migration remains separate.
