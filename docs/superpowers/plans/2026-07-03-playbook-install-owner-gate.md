# Playbook installation: owner choice at the approval gate, never agent discretion

Status: DONE 2026-07-03 (owner directive same day: "the model cannot assess
future needs. nothing is up to the discretion of the model. document, plan,
and execute that change" — the directive covers documentation, plan, and
execution in one go). Commit map: decision `0e48bda`, plan `441996e`,
implementation `24449e1`. Suite on the landed bytes: 142 tests, 12 failures +
4 errors, all in `test_run_fixture.py` plus the hook-tripwire test —
byte-identical result on the pre-change tree (stash-verified), so
pre-existing on this Windows host and unrelated; `git diff --check` clean.

## Why this plan exists

The drafting steps delegate the playbook-install decision to agent judgment:

- `procedures/bootstrap.md` Step 4 (~:305-309): "playbooks only if the scope
  tier justifies them … install one into `.agents/playbooks/<name>.md` when
  the repo's work calls for it".
- `procedures/migration.md` Step 2 item 6 (:94): "Playbooks only where the
  scope tier justifies them."
- `docs/design.md` Guidance Scope (~:169-174): tiers 2/3 "Add plan templates
  or playbooks where they prevent drift" / "area-specific playbooks".

"The repo's work calls for it" is a prediction about future needs, which the
model cannot make. Live consequence found 2026-07-03: the
Powershell-Token-Killer bootstrap installed no `.agents/playbooks/` at all —
the owner never saw that `templates/playbooks/reviewloop.md` existed to
accept or decline. The owner's directive: no agent discretion anywhere in
this choice.

Precedent: the Push Policy section of
`templates/approval-summary.template.md` (decision 2026-06-27) — a
repo-specific choice presented as standardized options at the approval gate,
answered only by the owner's approval-time reply, never pre-filled.

Decision entry: `.agents/decisions.md`, 2026-07-03 "Playbook installation is
an owner choice at the approval gate, never agent discretion".

## The change

1. **`templates/approval-summary.template.md`** — add a `## Playbooks`
   section between Push Policy and Risks, modeled on Push Policy:
   - Enumerate every template under `.bootstrap-tmp/templates/playbooks/`
     (mechanically — list the directory, never a hardcoded name) with a
     one-line purpose read from the template itself.
   - Default: **none installed**. The owner replies at approval time with the
     names to install.
   - Explicit guard sentence mirroring Push Policy: do NOT pre-select or
     infer the answer from the scope tier, the decisions log, or context; the
     owner's approval-time reply is the only valid source.
2. **`procedures/bootstrap.md` Step 4** — replace the "playbooks only if the
   scope tier justifies them … when the repo's work calls for it" clause:
   playbooks are never drafted or installed at the agent's discretion; the
   approval summary's Playbooks section lists every shipped template and the
   owner picks; install exactly the owner-selected ones into
   `.agents/playbooks/<name>.md` (invoked later via the `playbook` operator);
   they join the Committed list and the single scoped commit.
3. **`procedures/migration.md` Step 2 item 6** — replace with a pointer to
   the canonical rule in `bootstrap.md` (per the 2026-06-24 one-full-
   statement-plus-pointers decision).
4. **`docs/design.md` Guidance Scope** — remove playbooks from the tier
   definitions' add-lists and state that playbook installation is owner-
   selected via the approval summary regardless of tier.

Out of scope: the `/review` wrapper (its promotion has its own recorded
deferral in `.agents/state.md`); `templates/AGENTS.template.md` (untouched —
no `templateVersion` bump; the stamp tracks the template's structural
contract only); the dated 2026-06-09 migration spec and plan under
`docs/superpowers/` (historical records; the decision entry names the
supersession).

## Verification

`python3 -m unittest discover -s tests -v` (procedures/templates are content
the discover script copies into target repos). No test pins the replaced
wording (checked: `tests/` matches on `playbook` cover only the
`operator:playbook` probe), so the suite is a regression backstop, not a
guard for this specific change; the change is prose whose guard is the
approval-summary template itself. `git diff --check` for the docs edits.

## Commits

One item per commit:

1. decision entry (`.agents/decisions.md`) — this decision.
2. this plan.
3. the four-file implementation + suite run.
