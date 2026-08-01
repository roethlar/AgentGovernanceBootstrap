# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed 2026-08-01 (`1512b16`, `dfb12f0`, `d5a86f6`, `a906b0a`): the
  governance guard now works on codex — plan CLOSED at
  `docs/superpowers/plans/2026-08-01-harness-engineering-adoption.md`
  (commit map and verification in its Status line). The hook blocks
  via the JSON deny on both harnesses, parses `apply_patch` patch
  envelopes (any protected path denies the whole patch), ships as a
  revived `.codex/hooks.json` artifact, and refresh offers a one-time
  owner-confirmed trust pin driven through codex's own app-server —
  proven live end-to-end without the bypass flag. All probe outcomes:
  `docs/harness-capabilities.md` 2026-08-01 ledger. Released to Bixi
  as `d4bf2be` (2026-08-01 publish, 66 files — codex hook config,
  updated guard script, and refresh trust-pin all spot-verified in
  the product clone). The plan began as
  a six-phase harness-engineering adoption draft the owner collapsed;
  the draft, its openreview verdict, and per-item rulings are in the
  plan file's git history. Owner harness priority (`8bb748a`): Claude
  Code + codex are the enforcement targets; kimi > grok > agy, none
  vital, kimi unprobed. Owner working preferences, applied and
  recorded here until a `decision` lands: no ceremonial asks —
  objective defect fixes inside approved scope are made and committed
  without asking; asks only for genuine choices, with concrete
  plain-language context; fewer, better rules — mechanism over prose;
  no recurring token costs (a per-turn injection hook was proposed
  and rejected); agents never ask about plan weight — plan documents
  only when the owner says `plan`.
- Self-refresh 2026-07-31 (`7073255`, owner-run from the Bixi clone against
  toolkit `f2b2b36`): 9 installed copies updated — `AGENTS.md` and the two
  review playbooks with their three skills and three wrappers. Installed
  governance here is no longer lagging; `AGENTS.md` line 32 now carries the
  seeded-files ownership wording and the plain lint sentence.
- Landed 2026-07-31 (`6c20d03`, `1c7f971`): `tools/publish.py` records the
  product-repo path once per machine instead of once per release, and a
  recorded path containing whitespace now round-trips (reader and writer
  share one shape; bare entries still parse). The second half is CR1, found
  by `codereview codex` over `7fcce43..6c20d03` — the truncating read
  predates the first fix (`272c0a1`) and the first fix had spread it to a
  second call site. Record: `.agents/review/findings/CR1.md`. Released in
  `55e9819` — that run is itself the live proof of the first fix: it recorded
  no new `product-repo:` line.
- Released 2026-07-31 (`71a91b6` on Bixi, 65 files): carries all three of
  today's fixes — Bixi #3 (ownership wording), #2 (`already_staged`) and #4
  (bare review verbs). All three issues closed against it. Owner ruling the
  same day: releases batch, never one publish per fix. Installed copies in
  this repo still lag until the owner's next self-refresh, as always.
- Landed 2026-07-31 (`65f53b0`): the review verbs define their bare form —
  a bare `codereview`/`review`/`openreview` asks which reviewer to run, with
  the machine-local cache's prior dispatches as recall, storing nothing back
  and probing nothing (Bixi issue #4). Explicit dispatches unchanged. The
  ruling and the three rejected alternatives are recorded in
  `.agents/decisions.md` (2026-07-31); guard is `BareReviewInvocation` in
  `tests/test_templates.py`. Suite 206.
- Landed 2026-07-31 (`88e6d6f`, `b75e4e2`, `22dd532`, `69b7233`): the
  `--plan-json` record carries `already_staged`, the shipped paths sitting
  in the index that the run will not write, so a bootstrap approval summary
  describes the whole first commit instead of reporting "nothing to do"
  over a fully staged set (Bixi issue #2). Record schema is now 2. Paths
  only, no content pin, and no new refusal: `new-project` stages the seeded
  push policy and `procedures/setup.md` Step 3 edits that staged file before
  the first commit, so staged-then-modified is the normal greenfield shape,
  and bootstrap restages its own drafted policy between plan and apply.
  Plan closed with its commit map at
  `docs/superpowers/plans/2026-07-31-already-staged-shipped-set.md`. Suite
  204, green except the two known Windows `new-project` failures.
- Landed 2026-07-31 (`a971ba2`): the ownership invariant in
  `templates/AGENTS.template.md` no longer claims everything refresh
  installs is toolkit-owned — it scopes toolkit ownership to
  refresh-governed artifacts and names the seeded files
  (`.agents/push-policy.md`) repo-owned and editable, so an
  owner-authorized push-policy edit no longer reads as prohibited drift
  (Bixi issue #3). Token-neutral at 1656 words (2026-07-28 rule). New
  guard `SeededFilesStayRepoOwned` in `tests/test_templates.py` ties it to
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

- None queued. Unshipped work reaches Bixi on the owner's next
  `publish`; installed copies here (including the updated hook) lag
  until the owner's next self-refresh from the product clone.
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
