# OR3: Cache schema cannot represent openreview confirmation state

**Severity**: MEDIUM — the fail-closed gap only materializes when openreview is dispatched on a harness whose frontier is confirmed for codereview but not for openreview (per the plan's routing table: Grok/Gemini "unconfirmed"); no committed mechanism blocks it. Downgraded from reviewer's HIGH: the operator-misdispatch/effort-ambiguity half of the candidate was declined (see Known gaps).
**Status**: Resolved (owner-adjudicated 2026-07-18: grok/agy are fallback frontier models — the confirmation is per pair, not per playbook; schema amended)
**Branch**: master (owner collapsed per-finding branch ceremony for these doc-only amendments, 2026-07-18)
**Commit**: (single combined OR3/OR4/OR5 commit on master)

## Evidence
`templates/playbooks/codereview.md:145` — the cache schema has exactly two tier slots (`standard`, `frontier`), keyed to codereview semantics. `docs/superpowers/plans/2026-07-17-review-economy.md:149` — the closed routing table has a distinct **openreview** column whose Grok/Gemini cells read "unconfirmed" while their codereview frontier cells are confirmed fallbacks; "cells without a confirmed pair block fail-closed." `templates/playbooks/openreview.md:60` — dispatch requires only "the harness's owner-confirmed **frontier** pair," so a codereview-confirmed fallback frontier satisfies the letter of the openreview gate.

## Predicted observable failure
An openreview dispatched on Grok/Gemini passes the only committed confirmation check via the codereview fallback entry, bypassing the routing table's fail-closed "unconfirmed" cell — an owner gate the schema cannot express.

## What
The plan decided per-column confirmation state (routing table) but the committed cache schema and openreview gate can only express per-harness frontier confirmation.

## Approach
Owner ruling: the 2026-07-17 confirmation of grok/agy as fallback frontier was never scoped to codereview only — the plan's "unconfirmed" openreview cells contradicted it. Fix: frontier cache entries gain `openreview_confirmed: "<harness version | null>"` (set at the same owner-confirmation moment, never inferred); openreview's dispatch gate now requires that field to match the current harness version, fail-closed otherwise; fallback-grade pairs so confirmed are legitimate openreview reviewers with grade recorded in the outcome. Plan routing table amended: Grok/Gemini openreview cells now carry their owner-confirmed fallback pairs (Gemini inherits the no-xhigh carve-out).

## Files changed
- `templates/playbooks/codereview.md` (schema: `openreview_confirmed` field + semantics)
- `templates/playbooks/openreview.md` (dispatch gate on `openreview_confirmed`; fallback-grade eligibility)
- `docs/superpowers/plans/2026-07-17-review-economy.md` (routing table cells + 2026-07-18 amendment note)

## Guard proof
N/A — doc/template-only amendment; no executable surface. The reverse check is textual: reverting the schema field re-opens the exact gap in Evidence (openreview gate satisfiable by a codereview-only confirmation).

## Coder dispute (if any)

## Known gaps
DECLINED sub-claim, recorded for review: "whichever effort is cached makes one operator dispatch the wrong profile." Openreview's effort is fixed at **max** by committed text (`openreview.md:60-64`); it never resolves effort from the cache, so no dispatch ambiguity exists on competitive harnesses. The admitted scope is solely the missing openreview confirmation representation.

## Reviewer comments
`Reviewer: codex / gpt-5.6-sol / max / openreview-frontier` — codex-cli 0.144.5, thread 019f72d8-3772-77d1-8c19-1b890aaac07b, reviewed 87e7d5c…, base 10cbe96…, verdict findings, 2026-07-18T01:51Z. Intake: ADMITTED narrowed; fix amends a plan-decided schema → owner adjudication before any branch.
