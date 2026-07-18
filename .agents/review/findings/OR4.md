# OR4: T3 escalates orchestrator-established proof breakage to a reviewer that cannot accept

**Severity**: HIGH — a missing/failing proof burns a frontier round that is structurally unacceptable (verdict contract requires `guard_confirmed:true`), and a recorded flake can be laundered into acceptance by one lucky reviewer rerun — defeating both review economy and the guard's purpose.
**Status**: Resolved (owner-adjudicated 2026-07-18: T3 reworked as a pre-dispatch blocker; T1–T5 amendment approved)
**Branch**: master (owner collapsed per-finding branch ceremony for these doc-only amendments, 2026-07-18)
**Commit**: (single combined OR3/OR4/OR5 commit on master)

## Evidence
`templates/playbooks/codereview.md:258` (T3) — missing artifact, nonzero verification exit, or one disagreeing orchestrator-run repeat routes the finding to frontier. `templates/playbooks/codereview.md:312-326` — the reviewer must independently perform the proof (revert→FAIL→restore→PASS) and acceptance fails unless `guard_confirmed` is literally `true`.

## Predicted observable failure
Missing/failing proof: guaranteed-unacceptable frontier dispatch (cost with no possible acceptance). Flaky proof: T3 fired on an observed disagreement, yet acceptance requires only that the reviewer's single rerun passes — the known flake is accepted without ever being resolved.

## What
T3 treats orchestrator-detected proof integrity failures as an escalation trigger when they are pre-dispatch blockers; escalation cannot repair a broken proof, only re-observe it.

## Approach
Owner ruling adopted the reviewer's candidate verbatim: T3 is now a **pre-dispatch blocker, not an escalation** — missing artifact, nonzero verification exit, or an orchestrator-observed flake halts the round and returns it to the coder (or owner if the coder cannot reproduce) until deterministic evidence exists. No frontier dispatch occurs at broken evidence. T5 remains the path for a reviewer disputing the quality of a *valid* proof.

## Files changed
- `templates/playbooks/codereview.md` (T3 text, amended 2026-07-18)

## Guard proof
N/A — doc/template-only amendment; no executable surface. Reverting the T3 text restores the contradiction in Evidence (escalation to a reviewer whose verdict contract cannot accept the input).

## Coder dispute (if any)

## Known gaps
T1–T5 semantics are owner-approved plan content (plan revision 4ae68f6 / grok fold 1fd1065); any change is a plan amendment, not a drive-by edit.

## Reviewer comments
`Reviewer: codex / gpt-5.6-sol / max / openreview-frontier` — codex-cli 0.144.5, thread 019f72d8-3772-77d1-8c19-1b890aaac07b, reviewed 87e7d5c…, base 10cbe96…, verdict findings, 2026-07-18T01:51Z. Intake: contradiction verified against committed T3 text and verdict contract; ADMITTED, owner adjudication required.
