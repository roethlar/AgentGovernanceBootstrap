# Per-Repo Owner-Communication Tuning

Status: DRAFT 2026-07-12 — direction approved by the owner 2026-07-12
(owner wording: "agreed, go", on option (a) of the 2026-07-10 Open decision
"Per-repo tuning for verbosity and technical level" in
`.agents/decisions.md`). Implementation is blocked on one owner decision,
to be recorded here and in `.agents/decisions.md` when made: whether
bootstrap asks the owner for the section's values at the approval gate
(the push-policy pattern) or installs defaults silently for the owner to
change later.

## Problem

The plan contract (2026-07-10 decision; canonical home: the `plan`
operator bullet in `templates/AGENTS.template.md`) fixes the owner-facing
register globally: plain English, roughly 25-50 words per decision, no
jargon. That register is fixed fleet-wide; a repo whose audience is
technical, or where the owner wants terser or fuller answers, has no
supported way to say so.

`AGENTS.md` cannot carry the knob: it is installed verbatim and
byte-verified by `tools/refresh.py`, so per-repo parameters inside it
would break replace-whole matching (option (b) of the Open decision,
ruled infeasible there). `.agents/repo-guidance.md` is per-repo by
design, read at session start (Session Startup step 1 in
`templates/AGENTS.template.md`), and never touched by refresh — it is the
correct home, and no new file class or load mechanism is needed.

## Change

`templates/repo-guidance.template.md` gains an `## Owner Communication`
section; `procedures/bootstrap.md` Step 4 fills it when drafting
`.agents/repo-guidance.md`. The section tunes owner-facing chat output
only — answers, summaries, decision asks. It never changes plan documents
(agent-facing and technical per the plan contract), the register of
durable repo files, or any safety, approval, or verification rule.

### Slice 1: template section

Append to `templates/repo-guidance.template.md`:

```markdown
## Owner Communication
<!-- Tunes owner-facing chat output for this repo: answers, summaries,
     decision asks. Never changes plan documents (agent-facing, per the
     AGENTS.md plan operator), durable repo files, or any approval rule.
     Values shown are the defaults; the owner may change them anytime. -->
- Verbosity: standard        <!-- brief | standard | detailed -->
- Technical register: plain  <!-- plain | mixed | expert -->
- Jargon: avoid              <!-- avoid | allow -->
```

The defaults reproduce the existing fleet-wide behavior (plain English,
no jargon), so a repo that never edits the section behaves exactly as
before. Field semantics for the consuming agent: `Verbosity` scales how
much supporting detail accompanies an answer; `Technical register` sets
the working vocabulary (`plain` = non-engineer owner, `expert` =
practitioner shorthand acceptable); `Jargon: allow` lifts the
translate-all-terms obligation. The 25-50-word decision-ask shape from
the plan operator is unchanged at the defaults and scales with
`Verbosity`/`Technical register` when a repo tunes them.

### Slice 2: bootstrap drafting step

`procedures/bootstrap.md` Step 4, list item 1 (drafting
`.agents/repo-guidance.md` from the template): add one sentence stating
how the Owner Communication section is filled. Pending the owner
decision in the Status line, the sentence is one of:

- ask variant: "Draft the Owner Communication section with the template
  defaults; the approval summary asks the owner to confirm or change
  them (the push-policy pattern — never pre-fill from context)." This
  variant also adds a matching section to
  `templates/approval-summary.template.md`.
- defaults variant: "Draft the Owner Communication section with the
  template defaults verbatim; the owner changes values on request after
  install." No approval-summary change.

### Slice 3: record adoption

When slices 1-2 land: flip the 2026-07-10 entry in
`.agents/decisions.md` from Open to Adopted (rule's canonical home:
the section comment in `templates/repo-guidance.template.md`), archive
it per the decisions lifecycle, and set this plan's Status to CLOSED
with the commit map.

## Propagation

`tools/refresh.py` never touches `.agents/repo-guidance.md`, so existing
governed repos do not gain the section on refresh. They gain it when the
owner asks an agent in that repo to add it (copy the template section and
tune the values), or on a bootstrap re-run. New bootstraps scaffold it
from slice 1 onward. No shipped-set change, no `AGENTS.md` change, no
new tests required by design — the change is a drafting-template section
and one procedure sentence, with no runtime surface.

## Verification

- `python3 -m unittest discover -s tests -v` (Windows, from Git Bash:
  `py -3 -m unittest discover -s tests -v`) — the guidance lint and
  existing template tests must stay green.
- This plan file itself:
  `python3 -m unittest tests.test_plan_lint -v`.
- Manual check, stated in the closing commit message: the drafted
  section's defaults match the plan contract's register (plain English,
  jargon avoided).
