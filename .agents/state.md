# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Diagnosed 2026-07-27: the Claude Code `PreToolUse` hook presence-checks
  `python3` before `py -3`; Windows' Microsoft Store alias passes that check,
  fails when invoked, and prevents the working launcher fallback. Plan:
  `docs/superpowers/plans/2026-07-27-windows-hook-interpreter.md`, approved
  2026-07-27; implementation is in progress.

## Next

- Implement and verify the approved Windows hook interpreter plan.

## Blockers

- None recorded.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- None recorded.
