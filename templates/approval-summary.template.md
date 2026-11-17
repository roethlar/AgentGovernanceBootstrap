# Bootstrap Approval Summary

<Altitude: everything above the Existing Governance Inventory must fit on one
screen - short paragraphs, no exhaustive detail; the inventory is the only
section that may run long. For migration runs, include the inventory inline;
never just point at another file.>

## Recommendation

Start with exactly one of these:

- Approve
- Approve after edits
- Do not approve yet

Then add one sentence explaining why.

<While any open question still requires an owner decision - an unresolved
custody conflict, an ignore-rule question, a scope choice - the recommendation
must not be `Approve`. Use `Do not approve yet` or `Approve after edits` until
the owner has settled it.>

## What The Repo Appears To Be

<Plain-English summary of the repo based on evidence read directly from the repo.>

## Proposed Durable Guidance

<Short summary of what would be written and how it keeps code, docs, decisions,
verification, and future agent behavior aligned.>

## Verification Default

<State the verification commands run and their results. For a docs-only
change exempt from the full suite, state why and report `git diff --check`.
Name checks not run. Report evidence, not a generic policy or an approval
question.>

## Assumptions

<List inferred but unverified facts, or "None". Do not state assumptions as facts in the
draft guidance unless the human approves them. Do not turn normal verification hygiene into
a human approval question.>

## Files Proposed For Approval

<Group every proposed file below using `git check-ignore`
on its final path - never by assumption. A path the repo gitignores cannot
enter the commit and must not be listed as committed.>

### Committed — judgment drafts (copied from `.bootstrap-tmp/drafts/` on approval)

- `.agents/repo-guidance.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `.agents/push-policy.md`
- <migration runs: supersession banners on superseded files>

<Standard route: name the record's `draft_paths`. These reviewed drafts and
banners supply those files; mechanical repairs skip them, including the
whole decision/archive move if either side is reserved. A reserved missing
policy comes from its draft. Legacy route: no exclusions; show any final
repair of a committed draft in the mechanical-repair group below.>

### Committed — shipped set (installed by `tools/refresh.py --apply`)

<List everything the commit will contain from the shipped set, rendered from
the `--plan-json` record this run generated (`AGENTS.md`, harness shims,
operator wrappers, playbooks, hook settings) — never reconstructed by hand.
That is the record's `installs`, `updates` and `restores`, plus its
`already_staged` paths, which an earlier `--stage-only` run put in the index
and the script will not rewrite; mark those "already staged". These files are
never drafted or hand-copied; the script is their single installer, and Step 7
applies exactly this record.>

### Committed — repairs and removals

<Render `repairs`, `removes`, and `gitignore_repairs` from the record. Name
each path with a short action/reason; link the machine-plan JSON for repair
diffs and hashes. Include newly created archives. Write "None" if empty.
The complete refresh scope is `staged_paths`, plus `already_staged` for the
bootstrap commit; do not omit a group because it is outside the shipped set.>

### Local-only (gitignored, copied but never committed)

<Files whose final paths an ignore rule covers. The refresh script repairs a
known blanket harness-dir ignore itself; anything else it flags. Write
"None" when the list is empty. If keeping one of these tracked seems
important, raise the ignore rule as a question instead; never plan a silent
`git add -f`.>

<Follow repo branch policy; name any work branch and its integration
target. Initial creation establishes main. State the exact commit
message that will be used. Approving this summary
authorizes copying the judgment drafts, running the refresh install, and
making ONE scoped commit covering all groups (exactly the lists above,
never `git add -A`, never `git add -f`). Nothing is pushed yet; the push
policy written by this run governs all subsequent commits.>

<Legacy carve-out runs (a foreign `AGENTS.md` is being superseded): state
BOTH exact commit messages instead — commit 1, the carve-out (judgment
drafts + supersession banners + the legacy file's deletion); commit 2, the
refresh operation's own commit, including repairs to the first commit's
drafts. Link the rehearsal's schema-3 record and frozen-input receipt; name
its original base and post-carve-out tree pin. The preview shows the final
repaired bytes, not a re-copy of the earlier drafts. Approving this summary authorizes exactly
those two commits, in that order, and nothing else. Git is a hard
requirement settled at Step 1; a target without git never reaches this
summary.>

## Push Policy

<Name and preserve the existing owner-approved push policy unless a change
was requested. Standard route: if none exists, present **4 — ask** as the
default and ask for the owner's choice. Legacy route: the policy was
settled before rehearsal; report it, omit the choice prompt below, and
explain that a requested change requires a new rehearsal and summary
before commit 1. The same applies to edits to any frozen prepared file.>

To change it, reply with a number when you approve:

  1 — always: Always push after every commit.
  2 — operators: Push automatically after operator-invoked commits (handoff, decision, drift, plan); ask for all others.
  3 — docs: Push automatically after docs/state-only commits; ask for code or tool changes.
  4 — ask: Always ask before pushing. (default)

<Prior explicit approval remains valid. Ask only for an unresolved choice;
do not infer new push authority from approval of unrelated work.>

## Risks, Limitations, Or Open Questions

<List unresolved questions, inferred facts, stale evidence, unread areas, or decisions
that still need human approval. Questions should be answerable as owner intent, scope, or
risk tolerance, not require code expertise. Label each item Low, Medium, or High risk for
approving the proposed durable guidance. Use "None identified" only when that is true.>

## Repo Memory Check

<State whether any important repo-specific facts, decisions, invariants, verification
rules, non-goals, or open questions remain unrecorded.>

## Existing Governance Inventory

<Migration runs only. Include the completed inventory table from
`governance-inventory.template.md`: every existing governance artifact, its role,
its verdict (migrate / supersede / leave), and its destination, in plain
English. For greenfield runs write "Not applicable - no existing governance.">

## Fresh-Eyes Verification

<One plain-English sentence reporting the result of the fresh-eyes catchup
test, stating what it covers - discoverability and internal consistency, not
external truth. For example: "A fresh agent given only the drafted files
correctly answered the verification questions; this
checks that the guidance is findable and consistent, not that external
claims are true." Never present this test as proof that CI or deployment
claims are correct. If issues were found and fixed, say so. Required for
migration runs; if skipped on a greenfield run, say "Not run (greenfield).">
