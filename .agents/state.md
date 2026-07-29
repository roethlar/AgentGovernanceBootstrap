# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed 2026-07-28 (`c171dd0`, `e18cda7`): the toolkit-owned invariant in
  `templates/AGENTS.template.md` now tells governed repos to keep linters
  and formatters off installed copies — nothing polices files no agent may
  fix — paid for token-neutrally by collapsing the invariant's restated
  prohibition. Ruling and the new template-additions-pay-token-rent rule:
  `.agents/decisions.md` (2026-07-28); the editorial rule also rides the
  template bullet in `.agents/repo-guidance.md` (Earned Practices). An
  owner-directed full compression pass followed: 1772 → 1656 words
  (−6.6%), all rules and earned examples preserved, suite green. Not yet
  published to Bixi; reaches installed copies via publish + owner
  self-refresh.
- Landed in `4bc53c9` (2026-07-27): the Claude Code `PreToolUse` hook now
  viability-probes `py -3`, `python3`, then `python`, so Windows Store aliases
  cannot mask a working launcher; blocking exit 2 is preserved. Plan CLOSED:
  `docs/superpowers/plans/2026-07-27-windows-hook-interpreter.md`. Published
  to Bixi as `0dc9176` (2026-07-27); this repo's installed
  `.claude/settings.json` still awaits owner self-refresh.

## Next

- The owner runs this repo's sanctioned self-refresh from the product clone.

## Blockers

- This repo's self-refresh is owner-only.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`

## Unrecorded Repo Memory

- None recorded.
