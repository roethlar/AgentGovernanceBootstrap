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
  (−6.6%), all rules and earned examples preserved, suite green. Published
  to Bixi as `a9b3fcc` and installed here by the owner's self-refresh
  `2beef1f` (both 2026-07-28); installed copies match the templates.
  Publish note: the product checkout does not fetch before mirroring, so a
  release from a stale checkout diverges and the push fails with a
  fix-by-hand message the owner cannot act on — candidate toolkit
  improvement, not yet ruled on.
- Landed in `4bc53c9` (2026-07-27): the Claude Code `PreToolUse` hook now
  viability-probes `py -3`, `python3`, then `python`, so Windows Store aliases
  cannot mask a working launcher; blocking exit 2 is preserved. Plan CLOSED:
  `docs/superpowers/plans/2026-07-27-windows-hook-interpreter.md`. Published
  to Bixi as `0dc9176` (2026-07-27); installed here by the owner's
  self-refresh `2beef1f` (2026-07-28).

## Next

- Owner ruling pending: should `tools/publish` fetch and fast-forward the
  product checkout before mirroring (the stale-checkout gap noted above)?

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
