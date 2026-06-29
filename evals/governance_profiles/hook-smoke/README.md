# hook-smoke profile

Phase 0 harness-validation profile (not a governance treatment arm). It overlays a
single `.claude/settings.json` whose `PreToolUse` hook appends `fired` to the file
named by the `AGB_HOOK_SENTINEL` env var (an external sentinel `run_fixture` sets,
outside the trial worktree). Purpose: exercise the `hooks_present` /
`hooks_supported_by_driver` / `hooks_fired` telemetry (S4) and the live smoke (S7).
