# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed 2026-07-31 (`a971ba2`): the ownership invariant in
  `templates/AGENTS.template.md` no longer claims everything refresh
  installs is toolkit-owned — it scopes toolkit ownership to
  refresh-governed artifacts and names the seeded files
  (`.agents/push-policy.md`) repo-owned and editable, so an
  owner-authorized push-policy edit no longer reads as prohibited drift
  (Bixi issue #3). Token-neutral at 1656 words (2026-07-28 rule). New
  guard `tests/test_templates.SeededFilesStayRepoOwned` ties the prose to
  the manifest's `seeded[]` category — guard-proven, both cases fail on
  the old wording; refresh's half of the contract was already covered by
  `SeedTests.test_present_target_is_never_touched`. Outgoing template
  hash appended to `formerly[]`. Suite 197 tests, green except the two
  known Windows `new-project` failures. Bixi #3 stays open until the fix
  ships: it reaches the product repo on the owner's next `publish`, and
  this repo's installed `AGENTS.md` lags until the next self-refresh.
- Landed 2026-07-30 (`2bd0974`): the toolkit is MIT-licensed —
  `LICENSE` at the root ("Copyright (c) 2026 Michael Coelho"),
  `tools/publish.py`'s `PUBLISH_PATHS` carries it as
  `("LICENSE", "LICENSE")` so mirroring installs it in Bixi; one
  canonical copy, governed repos unaffected. Decision recorded
  (`.agents/decisions.md`, 2026-07-30): the license item is lifted out
  of the 2026-07-10 deferred release-engineering set, the rest stays
  deferred. Mirror-test guard-proven; suite green except two
  pre-existing Windows `new-project` failures (clean-HEAD worktree
  fails identically — PATH/git.exe resolution, machine-local, noted in
  `.agents/machines.md`). Plan CLOSED:
  `docs/superpowers/plans/2026-07-30-mit-license.md`. Released to Bixi
  as `4b01c27` (2026-07-30 publish, 65 files — LICENSE verified in the
  product clone and at GitHub HEAD).
- Landed 2026-07-29 (`722c9ae`): `tools/publish.py` now ships
  `.github/ISSUE_TEMPLATE/` into Bixi (the subdirectory only — dev CI
  and workflows can never auto-ship); mirror test guard-proven, suite
  green (195). Plan CLOSED:
  `docs/superpowers/plans/2026-07-29-publish-issue-templates.md`.
  Released to Bixi as `d5874dd` (2026-07-29 publish, 64 files; both
  templates verified in the product clone) — Bixi's "New issue" form
  now offers the defect and harvest-rule templates, and product clones
  carry them for bootstrap Step 8 drafting.
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
  #1 closed against it. The owner's self-refresh from the product
  clone landed as `cc671b2` (2026-07-29, 12 artifacts, toolkit
  `d5874dd`): installed copies match the templates — the reallocated
  review playbooks, range-grammar wrappers, toolkit menu, and
  Bixi-pointing update-governance are live here.
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

- Two Bixi issues remain open and unactioned, each awaiting its own
  per-item owner go (2026-07-31 triage): #4 (the recorded frontier tier
  is neither durable nor independent of the coder's own model — part
  design ruling, not just a fix) and #2 (`refresh.py --plan-json` reports
  "nothing to do" on an unborn repo whose shipped set is already staged,
  so the bootstrap approval summary cannot enumerate the first commit's
  scope).
- Unshipped: `a971ba2` reaches Bixi only on the owner's next `publish`.

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
