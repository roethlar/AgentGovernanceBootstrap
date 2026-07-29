# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed 2026-07-29 (`6a2466a`): product-facing surfaces now name Bixi —
  `procedures/bootstrap.md` Step 0 leads with the Bixi URL
  (origin-first sync, fallbacks in `tools/refresh.py`'s canonical
  order, default clone path `~/dev/Bixi`) and the `update-governance`
  wrapper + skill clone Bixi; pins guard-proven, suite green (195).
  Plan CLOSED: `docs/superpowers/plans/2026-07-29-bixi-facing-references.md`.
  The feedback-target ruling landed the same day (2026-07-29 decision
  in `.agents/decisions.md`): the public inbox is Bixi's issues —
  consumed and fixed here, shipped back via `tools/publish`, with this
  repo planned to go private; `procedures/bootstrap.md` Step 8 and
  `product/README.md` now point at Bixi. Released to Bixi as `f55170a`
  (2026-07-29 publish, 62 files — carries the review-playbooks
  reallocation, the Bixi-first references, and the feedback pointers;
  release contents spot-verified in the product clone) and Bixi issue
  #1 closed against it. This repo's installed copies lag the templates
  until the owner's self-refresh from the product clone — expected;
  leave the lag alone.
- Landed 2026-07-29 (`87d3825` Slice 1, `36e025f` Slice 2): the review
  playbooks are reallocated per
  `docs/superpowers/plans/2026-07-29-review-playbooks-redesign.md`
  (CLOSED) — openreview now renders an approach-soundness judgment of a
  whole change, code or plan (verdict
  `best_approach`/`acceptable_with_changes`/`replace`); codereview owns
  landed-change defect generation over a pinned `<base>..<head>` range
  plus the per-finding conformance loop. Closes GitHub issue #11. Suite
  green (195 tests), new structural pins guard-proven. Ships to Bixi on
  the owner's next `publish`; this repo's installed copies lag until
  the owner's self-refresh.
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
  The stale-checkout publish gap this exposed (no fetch before mirroring;
  hit live during the release) is fixed in `39a3e44`: behind
  fast-forwards, split histories refuse in plain words, unreachable
  remotes warn and proceed; three guard-proven tests. The fixed
  `tools/publish.py` reached Bixi in release `b68906d` (2026-07-29).
- Landed in `4bc53c9` (2026-07-27): the Claude Code `PreToolUse` hook now
  viability-probes `py -3`, `python3`, then `python`, so Windows Store aliases
  cannot mask a working launcher; blocking exit 2 is preserved. Plan CLOSED:
  `docs/superpowers/plans/2026-07-27-windows-hook-interpreter.md`. Published
  to Bixi as `0dc9176` (2026-07-27); installed here by the owner's
  self-refresh `2beef1f` (2026-07-28).

## Next

- None recorded.

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
