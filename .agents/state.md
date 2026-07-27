# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Reported 2026-07-27; diagnosis pending: on Windows, Claude Code's
  `PreToolUse:Write` and `PreToolUse:Edit` governance hooks fail because
  their command invokes bare `python` and reaches the Microsoft Store
  not-found stub. The owner requested a fix after this catchup.

## Next

- Diagnose the Windows hook interpreter resolution, draft a narrow code-change
  plan for owner approval, then implement and verify the approved fix.

## Blockers

- No technical blocker recorded; implementation requires an approved plan.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- None recorded.
