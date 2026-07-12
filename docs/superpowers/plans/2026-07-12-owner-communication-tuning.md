# Per-Repo Owner-Communication Tuning

Status: CLOSED 2026-07-12 — landed: slice 1 `9d8c156` (repo-guidance
template section), slice 2 `b208067` (approval-summary question +
bootstrap drafting sentence), slice 3 in the closing commit (decisions
entry Adopted and archived; state updated). Direction approved by the
owner 2026-07-12 (owner wording: "agreed, go", on option (a) of the
2026-07-10 Open decision "Per-repo tuning for verbosity and technical
level"). Design settled by owner ruling the same day, verbatim: "yes,
prompt. default is what I currently use- plain english exec summary for
me; token-dense, detailed implementation plan for agents. alternates,
devops - jargon is acceptable, detailed plan. student - accessible,
instructive. any others you can think of, capped at 5." The approval
summary asks (the push-policy pattern); the knob is a single named
profile, five profiles total (three owner-named, two agent-proposed:
`expert`, `brief`).

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

## Design

One `Profile:` line in each repo's `.agents/repo-guidance.md`, chosen by
the owner at the bootstrap approval gate. The five profiles, each defining
the owner-chat register and the plan-document register:

1. `default` — owner chat: plain-English executive summary, no jargon;
   plans: token-dense, detailed, written for agents. (Owner-named;
   reproduces current fleet-wide behavior.)
2. `devops` — owner chat: technical jargon acceptable, summary-first;
   plans: detailed. (Owner-named.)
3. `student` — owner chat: accessible and instructive — explains the why,
   defines terms on first use; plans: detailed, rationale spelled out.
   (Owner-named.)
4. `expert` — owner chat: terse practitioner shorthand, density over
   ceremony; plans: token-dense, detailed. (Agent-proposed.)
5. `brief` — owner chat: plain-English headlines only — the outcome and
   the decision, detail on request; plans: token-dense, detailed.
   (Agent-proposed.)

Token-bloat constraint (owner principle, 2026-07-12 decision "Draft-all
harness artifacts stands"): the drafted `.agents/repo-guidance.md` carries
ONLY the chosen profile line with its one-line definition inline — never
the full five-profile menu, which would cost every session in every repo.
The menu's canonical home is `templates/approval-summary.template.md`
(read once per bootstrap, never per session). The drafted line is
self-contained so a governed repo needs no toolkit lookup to apply it.

Scope guard: a profile tunes registers only. It never changes the plan
contract's structure (plans stay agent-facing; owner decisions still come
in chat, one at a time), any safety, approval, or verification rule, or
the register of durable repo files.

## Slices

### Slice 1: template section

Append to `templates/repo-guidance.template.md`:

```markdown
## Owner Communication
<!-- One profile line tuning owner-facing chat output (answers, summaries,
     decision asks) and plan-document register. The owner chooses at the
     approval gate from the five profiles in
     approval-summary.template.md; never pre-fill from context. Write the
     chosen profile WITH its one-line definition so this file stands
     alone; never copy the full menu here. A profile never changes any
     safety, approval, or verification rule. -->
- Profile: default — owner chat: plain-English executive summary, no
  jargon; plans: token-dense, detailed, written for agents.
```

### Slice 2: approval-summary question + bootstrap drafting sentence

`templates/approval-summary.template.md`: add an `## Owner Communication`
section directly after `## Push Policy`, same shape as the push-policy
question — default stated first (`1 — default`), the five numbered
profiles with one-line definitions, and the guard note: do NOT pre-select
or infer from prior decisions or context; the owner's approval-time reply
is the only valid source; update the drafted repo-guidance line to the
chosen profile (with definition) before the commit.

`procedures/bootstrap.md` Step 4, list item 1 (drafting
`.agents/repo-guidance.md`): append one sentence — draft the Owner
Communication line as `default` with its definition; the approval summary
asks the owner to choose among the five profiles; update the drafted line
to the owner's choice before commit. Step 6's summary-contents sentence
("the push-policy question, ...") gains "the owner-communication
question".

### Slice 3: record adoption

Flip the 2026-07-10 entry in `.agents/decisions.md` from Open to Adopted
(rule's canonical home: the Owner Communication section of
`templates/repo-guidance.template.md`; menu home:
`templates/approval-summary.template.md`), archive it per the decisions
lifecycle, set this plan's Status to CLOSED with the commit map, and
update `.agents/state.md`.

## Propagation

`tools/refresh.py` never touches `.agents/repo-guidance.md`, so existing
governed repos do not gain the section on refresh. They gain it when the
owner asks an agent in that repo to add it (copy the slice-1 section and
set the profile), or on a bootstrap re-run. New bootstraps scaffold it
from slice 1 onward. No shipped-set change, no `AGENTS.md` change, no new
tests by design — drafting-template and procedure prose only, no runtime
surface.

## Verification

- `python3 -m unittest discover -s tests -v` (Windows, from Git Bash:
  `py -3 -m unittest discover -s tests -v`) — guidance lint and template
  tests stay green.
- This plan file: `python3 -m unittest tests.test_plan_lint -v`.
- Manual check, stated in the closing commit message: the `default`
  profile's wording matches the plan contract's register, so an untouched
  repo behaves exactly as before.
