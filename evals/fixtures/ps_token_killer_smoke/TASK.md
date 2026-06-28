# Smoke fixture — PowerShell / Pester

This is a **harness smoke fixture**, not yet a gold-standard task. Its only job is to
prove the language-agnostic runner can scaffold a real owned repo, run its native test
command (`Invoke-Pester`), and read pass/fail.

- Source: `PowerShell-Token-Killer` @ `5e7d117`, scaffolded into a throwaway clone with
  remotes stripped.
- Verify: the repo's existing Pester suite (`tests/`). At the pinned commit it is green
  (31 tests), so a correctly-wired harness scores `functional_pass: true`.

The gold-standard upgrade (later slice): pick a real fix-commit from this repo's
history, set `base_commit` to its parent, write the agent task from the commit message,
and let the fix-commit's own test be the oracle (fails on parent, passes after the fix).
