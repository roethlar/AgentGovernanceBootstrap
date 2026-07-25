# OR6 — openreview of the 2026-07-25 change

Reviewer: openreview codex (gpt-5.6-sol @ xhigh, competitive) over
`9434df6`..`b0f8144`: five findings, all ADMITTED, all fixed.

The verdict envelope carried `capability_ok: true`, the first dispatch to
use the folded-in transport proof rather than a separate smoke round.

## Findings and disposition

| # | Finding | Severity | Disposition |
|---|---------|----------|-------------|
| 1 | `codereview` verdict schema omits `capability_ok` while its Capability proof section says the proof rides the envelope | HIGH | ADMITTED — fixed `bf37ae7` |
| 2 | `check_committability` prunes an ignored target from install/update/restore but not `plan.seeded`, so a skipped seed still reports "1 seeded" plus an ACTION line | MEDIUM | ADMITTED — fixed `0e6a1c3`, guard-proven |
| 3 | "Reviewer tiers and routing" still called the pair cache version-keyed, contradicting the split in the same change | MEDIUM | ADMITTED — fixed `bf37ae7` |
| 4 | Installed `AGENTS.md:83` and `.agents/playbooks/plan.md:15` point at the deleted `.agents/comms-policy.md`; `.agents/state.md` claimed zero lag | MEDIUM | ADMITTED — state corrected `2202185`; the installed copies need the owner's publish + self-refresh |
| 5 | Retiring the comms policy shipped no `retired[]` entry, so every other governed repo keeps a committed `comms-policy.md` forever | MEDIUM | ADMITTED — fixed `fc6e549`, verified end to end |

## Process note

Findings 1, 2, 3 and 5 were regressions introduced earlier the same day by
the changes under review. They were fixed directly, one commit each, rather
than through the per-finding branch-and-verdict flow: the flow's value is
adjudicating contested findings between coder and reviewer, and none of
these were contested — each reproduced on inspection. Finding 2 carries a
guard proof; the rest are prose or manifest changes with no test surface.

## Standing evidence

Finding 1 is the strongest argument for the folded-in capability proof
being written down in both playbooks at once: the section that introduced
it and the schema that must enforce it live ~290 lines apart in the same
file, and only one was updated. A future change to the verdict contract
should check both.
