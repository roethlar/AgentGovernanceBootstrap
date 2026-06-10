# Bootstrap Approval Summary

## Recommendation

Start with exactly one of these:

- Approve
- Approve after edits
- Do not approve yet

Then add one sentence explaining why.

## Recommended Scope

<Tier 1 / Tier 2 / Tier 3, with one sentence explaining why this repo needs that much
process and no more.>

## What The Repo Appears To Be

<Plain-English summary of the repo based on evidence read directly from the repo.>

## Proposed Durable Guidance

<Short summary of what would be written and how it keeps code, docs, decisions,
verification, and future agent behavior aligned.>

## Verification Default

<State the observed automated verification command(s), if any. Apply the default rule:
code changes require current automated verification before claiming completion; docs-only
changes do not require code verification unless they affect setup, commands, runtime
behavior, generated files, or user-visible behavior; behavior not covered by automation
requires the relevant manual check or a clear note that it was not run. Do not ask the
human to approve this normal default.>

## Assumptions

<List inferred but unverified facts, or "None". Do not state assumptions as facts in the
draft guidance unless the human approves them. Do not turn normal verification hygiene into
a human approval question.>

## Files Proposed For Approval

- `AGENTS.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `.agents/repo-map.json`
- `.agents/artifact-manifest.json`

<For migration runs, extend this list with the harness shim (for example
`CLAUDE.md`), the governance inventory, supersession banners on superseded
files, and the harvest report if one was drafted.>

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

<One plain-English sentence reporting the result of the fresh-eyes catchup test,
for example: "A fresh agent given only the drafted files correctly answered all five
questions in the verification procedure." If issues
were found and fixed, say so. Required for migration runs; if skipped on a
greenfield run, say "Not run (greenfield).">
