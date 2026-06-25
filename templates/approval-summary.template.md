# Bootstrap Approval Summary

<Altitude: everything above the Existing Governance Inventory must fit on one
screen - short paragraphs, no exhaustive detail; the inventory is the only
section that may run long. Always state the scope tier. For migration runs,
include the inventory inline; never just point at another file.>

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

## Recommended Scope

<Tier 1 / Tier 2 / Tier 3, with one sentence explaining why this repo needs that much
process and no more.>

## What The Repo Appears To Be

<Plain-English summary of the repo based on evidence read directly from the repo.>

## Proposed Durable Guidance

<Short summary of what would be written and how it keeps code, docs, decisions,
verification, and future agent behavior aligned.>

## Verification Default

<State the observed automated verification command(s), if any, then apply the verification
default rule from the AGENTS Verification section — do not restate its conditions here, and
do not ask the human to approve this normal default.>

## Assumptions

<List inferred but unverified facts, or "None". Do not state assumptions as facts in the
draft guidance unless the human approves them. Do not turn normal verification hygiene into
a human approval question.>

## Files Proposed For Approval

<Sort every proposed file into the two lists below using `git check-ignore`
on its final path - never by assumption. A path the repo gitignores cannot
enter the commit and must not be listed as committed.>

### Committed (tracked)

- `AGENTS.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `.agents/repo-map.json`
- `.agents/artifact-manifest.json`

### Local-only (gitignored, copied but never committed)

<Files whose final paths an ignore rule covers - harness directories like
`.claude/` often are. Write "None" when the list is empty. If keeping one of
these tracked seems important, raise the ignore rule as a question instead;
never plan a silent `git add -f`.>

<For migration runs, extend these lists with the harness shim (for example
`CLAUDE.md`), the governance inventory, supersession banners on superseded
files, and the harvest report if one was drafted.>

<State the exact commit message that will be used. Approving this summary
authorizes copying the files above and making that ONE scoped commit
(exactly the Committed list, never `git add -A`, never `git add -f`).
Nothing is pushed; pushing remains the owner's action.>

<Non-git targets: there is no commit to authorize yet. Ask here whether to
`git init` and include the scoped first commit (see bootstrap.md, "If the
target is not a git repository"). If the owner declines, replace the two
lists above with one list titled "On disk only - no version control" and
replace the commit paragraph with a plain statement that `git init` remains
the owner's decision.>

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
correctly answered all six questions in the verification procedure; this
checks that the guidance is findable and consistent, not that external
claims are true." Never present this test as proof that CI or deployment
claims are correct. If issues were found and fixed, say so. Required for
migration runs; if skipped on a greenfield run, say "Not run (greenfield).">
