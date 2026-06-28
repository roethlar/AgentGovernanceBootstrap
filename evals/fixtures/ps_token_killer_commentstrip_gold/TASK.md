# Gold fixture — PowerShell-Token-Killer, minimal-level comment stripping

> Harness documentation only — **not** sent to the agent. The agent-facing prompt is
> `PROMPT.md` (no source slug / commit SHA).

Derived from a real fix-commit (`PowerShell-Token-Killer` @ `2f14522`); base is its
parent `b90329a`. Proves the gold-standard machinery on a second toolchain (Pester /
PowerShell), not just TypeScript. The runner derives the test diff live from the source
repo and injects it; the agent must make the suite pass by editing
`src/PwshTokenCompressor.psm1` only.

## Oracle

- Verify: `pwsh -NoProfile -Command "Invoke-Pester -Path tests -Output Minimal -CI"`
  (pwsh exits 1 on any failing test, 0 when all pass).
- Without the source fix the new test is red; with the reference fix it passes. Confirm:
  `python3 tools/run_fixture.py evals/fixtures/ps_token_killer_commentstrip_gold --check-oracle`
