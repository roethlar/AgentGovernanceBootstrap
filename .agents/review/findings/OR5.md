# OR5: Openreview outcomes carry no dispatch provenance

**Severity**: MEDIUM — a completed openreview cannot later prove which model/effort actually reviewed the change; the plan's ambient-routing audit problem stays unsolved for one of the two review operators.
**Status**: Resolved (owner-adjudicated 2026-07-18: rides as a follow-up amendment; provenance required on every openreview outcome)
**Branch**: master (owner collapsed per-finding branch ceremony for these doc-only amendments, 2026-07-18)
**Commit**: (single combined OR3/OR4/OR5 commit on master)

## Evidence
`templates/playbooks/openreview.md:100` — a clean result is recorded as one plain sentence ("openreview <agent> over <base>..<head>: no material issue") naming only the agent; findings are handed downstream with no requirement to persist the originating model, effort, tier, or transcript reference. The range's provenance machinery (`Reviewer:` line copied verbatim from the invocation transcript, slice 2 / ec7b62e) was wired into codereview only.

## Predicted observable failure
A misrouted openreview (wrong model or effort) is undetectable after the fact; the review index can attest that "an openreview happened" but not what performed it.

## What
The one-sentence clean record predates this range; the new provenance machinery was not extended to openreview outcomes, leaving the audit gap the plan set out to close.

## Approach
Owner ruling adopted the reviewer's candidate: every openreview outcome — clean or findings — records reviewer provenance (harness, resolved model id, effort, grade) taken from the dispatch record of the session that produced the verdict, never reconstructed. The clean one-liner now embeds it: "openreview <agent> (<model> @ <effort>, <grade>) over <base>..<head>: no material issue".

## Files changed
- `templates/playbooks/openreview.md` (Downstream section: provenance requirement + amended clean-record sentence)

## Guard proof
N/A — doc/template-only amendment; no executable surface. Reverting restores the provenance-free clean sentence cited in Evidence.

## Coder dispute (if any)

## Known gaps
Pre-existing text; the plan is closed, so this is a scope extension rather than a defect in what the plan promised. Owner decides whether it rides as a follow-up amendment.

## Reviewer comments
`Reviewer: codex / gpt-5.6-sol / max / openreview-frontier` — codex-cli 0.144.5, thread 019f72d8-3772-77d1-8c19-1b890aaac07b, reviewed 87e7d5c…, base 10cbe96…, verdict findings, 2026-07-18T01:51Z. Intake: verified one-sentence rule predates range (openreview.md untouched at that line; last prior touch 19f40c8); ADMITTED as scope extension, owner call.
