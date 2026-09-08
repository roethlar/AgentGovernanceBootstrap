# Agent State

## Now

- Repo-wide token-waste fixes verified on master, starting at f1497c4.
  Review changes: ed35ff6; governance simplification: 9aad4ae.
  Remaining runner/test/doc changes: 223 tests passed; publication pending.
  Scope and evidence: .agents/decisions.md.
- Headroom startup/resume hook removed from machine-local
  .claude/settings.local.json.
- Installed governance remains owner-managed and still needs refresh from
  the published Bixi clone. Agents must not self-refresh under existing rules.

## Next

- Publish verified source to Bixi, then obtain the owner's refresh action.
- Deferred draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  No new check-mode implementation; read-only inspection uses --plan-json -.

## Verification

- Entry point: .agents/repo-guidance.md.
