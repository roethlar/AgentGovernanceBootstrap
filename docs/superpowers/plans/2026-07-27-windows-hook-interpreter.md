# Plan: make the Claude governance hook select a working Python on Windows

Status: APPROVED 2026-07-27 — the owner answered `y` to the gate approving
the viability-probed `py -3` → `python3` → `python` chain, preserved blocking
exit 2, and regression coverage. Implementation is in progress.

## Problem

The Claude Code `PreToolUse` command in
`templates/hooks/claude/settings.json` tests only command presence and checks
`python3` before `py -3`:

```sh
if command -v python3 ...; then python3 ...; elif command -v py ...; then py -3 ...
```

Windows App Execution Alias stubs satisfy `command -v python3` even though
they cannot run Python. The command therefore selects the stub and exits
before reaching a working Windows launcher. On the 2026-07-27 Windows
reproduction, an unprotected-file payload exited 126 from the current
command while `py -3` was usable. Claude reported the same failure for every
Write/Edit attempt.

This regressed a behavior previously fixed for the retired advisory tripwire
in `63b5db0`: `py -3` ran first because command presence is not interpreter
viability on Windows. The blocking replacement hook introduced in `3f2a99e`
restored a presence-only, `python3`-first chain. Its test protects exit-code
preservation but does not protect interpreter order or viability.

The repo's current interpreter contract is already settled:
`procedures/bootstrap.md` probes `py -3`, then `python3`, then `python`, and
treats Store stubs and failed version probes as absent. This fix applies that
existing contract to the hook; it creates no new product decision.

## Design

Replace presence checks with executable Python 3.10+ probes, in the settled
Windows-first order:

```sh
if py -3 -c "<3.10+ probe>" >/dev/null 2>&1; then
  py -3 "<hook>"
elif python3 -c "<3.10+ probe>" >/dev/null 2>&1; then
  python3 "<hook>"
elif python -c "<3.10+ probe>" >/dev/null 2>&1; then
  python "<hook>"
else
  exit 0
fi
```

The JSON keeps this as one `sh`-compatible command line.

- Probe stderr is suppressed, so absent commands and Store aliases fall
  through without producing a hook error.
- The actual hook invocation is a separate command in the selected branch.
  Its exit 2 remains the final command status and still blocks protected
  edits. No `a || b` fallback chain is introduced.
- When no working interpreter exists, the hook remains deliberately
  fail-open with exit 0. The invariant and strict refresh remain the primary
  protection layers.
- The unversioned `python` fallback closes the third branch already required
  by the repo's interpreter contract.

The candidate command was exercised before implementation on Windows with
Git Bash: unprotected payload exit 0; protected `AGENTS.md` payload exit 2
with the governance message; a PATH containing only the Store aliases exit 0
without output.

## Implementation

### Slice 1 — shipped fix, regression guard, and evidence

Land one technical commit containing all four coupled changes:

1. `templates/hooks/claude/settings.json` — replace the `PreToolUse`
   interpreter chain with the design above.
2. `tests/test_templates.py` — define the canonical protect-hook command
   beside `CANONICAL_REGROUND_COMMAND` and require exact equality in
   `ShippedHooks`. Keep the existing explicit no-`||` assertion so the
   blocking-exit rationale remains visible.
3. `tools/shipped-set.json` — append the outgoing normalized SHA-256 of
   `templates/hooks/claude/settings.json` to that artifact's `formerly[]` in
   the same commit. `FormerlyListMaintenance` must stay green.
4. `docs/harness-capabilities.md` — update the fail-open description to the
   three viability-probed candidates and record the 2026-07-27 Windows live
   evidence.

Do not edit this repo's installed `.claude/settings.json`. It is
refresh-installed and toolkit-owned; the expected template/copy lag closes
only through the owner's product publish and owner-only self-refresh route.

### Slice 2 — close the record

After Slice 1 is committed and verified:

1. Mark this plan CLOSED with the Slice 1 commit and verification results.
2. Update `.agents/state.md`: the source fix is landed; the remaining rollout
   is product publication followed by the owner's self-refresh.
3. Commit and push the bookkeeping immediately.

## Verification

Use the interpreter selected by `.agents/repo-guidance.md`; on Windows this
machine uses `py -3` from Git Bash.

1. Run `py -3 -m unittest tests.test_templates -v`.
2. Run `py -3 -m unittest discover -s tests -v`.
3. Guard proof: with the new test retained, temporarily restore only the old
   `PreToolUse` command in the working template; the canonical-command test
   must fail. Restore the new command and rerun green.
4. Run the exact command loaded from the edited JSON under Windows Git Bash:
   an unprotected payload must exit 0; a protected `AGENTS.md` payload must
   exit 2 and print the block message.
5. Run the same command with `py` absent and only the Windows Store
   `python3`/`python` aliases visible; it must exit 0 without output.
6. Run `git diff --check`.

## Rollout boundary

`tools/publish` runs only on the owner's `publish` word, and this repo's
self-refresh is owner-only. Neither action is authorized by plan approval.
Until both happen, the source repo contains the fix while Bixi and this
repo's installed `.claude/settings.json` remain on the prior command.
