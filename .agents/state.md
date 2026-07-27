# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed in `4bc53c9` (2026-07-27): the Claude Code `PreToolUse` hook now
  viability-probes `py -3`, `python3`, then `python`, so Windows Store aliases
  cannot mask a working launcher; blocking exit 2 is preserved. Plan CLOSED:
  `docs/superpowers/plans/2026-07-27-windows-hook-interpreter.md`. Bixi and
  this repo's installed `.claude/settings.json` still await owner rollout.

## Next

- On the owner's `publish` word, publish Bixi; the owner then runs this repo's
  sanctioned self-refresh from the product clone.

## Blockers

- Product publication requires the owner word `publish`; this repo's
  self-refresh is owner-only.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- None recorded.
