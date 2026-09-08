# Agent State

## Now

- Repo-wide waste fixes are committed on master and published to Bixi main
  as c2cfb7e (source ccd8d5d; preceding slices ed35ff6 and 9aad4ae).
  Verification: 223 tests passed; all 70 published files match source.
  Scope, token measurements and evidence: .agents/decisions.md.
- Local installation remains pending: .agents/repo-guidance.md reserves
  self-refresh to the owner. Read-only Bixi plan: 2 installs, 32 updates,
  no restores, removals or flags. Installed copies retain older guidance.
- Headroom startup/resume hook removed from .claude/settings.local.json.

## Next

- Owner refresh action (or explicit override authorizing the agent):
  python3.14 /Users/michael/Dev/Bixi/tools/refresh.py /Users/michael/Dev/AgentGovernanceBootstrap
- Deferred draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Read-only inspection uses --plan-json -; no new check mode was added.

## Verification

- Entry point: .agents/repo-guidance.md.
