# Processed Harvest Reports (ARCHIVED 2026-07-08)

> This ledger is closed. The dropbox feedback channel was replaced by GitHub
> issues on this repo (zero-based consolidation, 2026-07-08): open issues are
> the triage queue, closed issues the outcome record. This file is the
> verbatim archive of everything triaged through the dropbox era.

One line per report already folded into templates or procedures:
`<repo name> - <report date> - <one-phrase outcome>`

- roon-controller - 2026-06-09 - adopted: revert-the-fix test check added to AGENTS template Verification
- blit2 - 2026-06-10 - adapted: ancestry-vs-content git-safety bullet added to AGENTS template; CI state-gate idea skipped (enforcement machinery; policy already covered by universal invariants)
- ChickenScratch - 2026-06-10 - adapted: one-item-per-commit discipline added to AGENTS template Git Safety (branch-per-item half dropped; branching stays per-repo policy)
- AgentGovernanceBootstrap (self-incident) - 2026-06-10 - adopted: artifact-is-evidence-not-decision and harness-conflict clauses added to AGENTS template invariants, this repo's AGENTS.md, and the bootstrap.md contract (agent executed an unapproved fix sweep from a handed-over defect report)
- AgentGovernanceBootstrap (self-migration pilot, Grok Build) - 2026-06-10 - adopted: self-target wording fixed in migration Step 8.4 (old absolute sentence forbade self-runs and was glossed silently, not flagged); custody redefined as intended post-approval custody proven by git query; shim rule generalized to native AGENTS.md readers; README current-state deduped to .agents/state.md pointer
- Send-MailMessageV2 (non-git greenfield pilot) - 2026-06-11 - adopted: discover.py non-git custody fix (files listed untracked, never tracked; packet states non-git custody) + tests; non-git section in bootstrap.md with owner-gated git-init question; adapted: custody enum example added to artifact-manifest template, non-git variant note in approval-summary template; second-remote note skipped (procedure pins URLs)
- ExchangeAdminWeb (update-route pilot) - 2026-06-11 - adapted: post-rejection commit-scope confirmation added to bootstrap Step 10 and migration Step 8.5; ignored-vs-manifest custody conflict made a mandatory owner question in migration Step 4.3; Approve recommendation gated on no open owner decisions in summary template; skipped: four-phase approval vocabulary, settings-file auto-detection, dedicated update.md, index-state rules

## Processed Bug Reports

One line per triaged report from the dropbox's `bugs/` folder (dropbox files
are append-only, so triage state lives here, not in the reports):
`<report filename stem> - <one-phrase outcome>`

- AgentGovernanceBootstrap-playbook-probe-2026-06-22 - fixed 2026-07-01 under the route-collapse plan: `operator:playbook` probe now word-boundary-matches, guarded by a test that the shipped template self-reports zero missing sections (see the 2026-07-01 decision entry)
- headroom-authority-boundary-overreach-2026-06-23 - folded into `.agents/decisions.md` (2026-06-23 entry citing the report)
- headroom-harness-artifact-overproduction-2026-06-23 - folded into `.agents/decisions.md` (2026-06-23 entry citing the report)
- incident_june-claude-local-only-false-migration-2026-06-24 - fixed 2026-07-02: discover.py routing consumes only durable governance — git-ignored paths and `.claude/settings.local.json` no longer count (879bf93, 4 new tests)
- ExchangeAdminWeb-template-invariant-duplication-2026-06-24 - resolved by prior work: the 2026-07-01 guidance condensation + 2026-07-02.1 reflow already leave each core rule stated once; the report's own bite-proof passes on the current template
- ExchangeAdminWeb-hook-python3-discovery-2026-07-02 - fixed 2026-07-02 (63b5db0, 79783bb; plan `docs/superpowers/plans/2026-07-02-hook-python3-windows-fallback.md`); Windows bite-proof still pending a Windows host
- ai-rpg-engine-shim-harness-scoping-2026-07-02 - fixed 2026-07-02: bootstrap step 5 + migration Step 4 now draft/refresh every shipped shim template, not just the current harness's (c05dc31)
