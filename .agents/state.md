# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. The `catchup` hygiene sweep
rotates landed or superseded entries verbatim to
`docs/history/state-archive.md`; `handoff` is the fast snapshot and rotates
nothing.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Landed 2026-07-25: governance refresh backfills absent repo-owned policy
  files. `tools/shipped-set.json` grew a `seeded` section
  (`.agents/push-policy.md`); `tools/refresh.py`
  installs a seeded target only when it is missing, reports it with an
  ACTION line, and ignores it forever once it exists. Closes the dangling
  references installed artifacts carried in repos governed before those
  files existed. Ruling and rationale in `.agents/decisions.md`
  (2026-07-25); plan
  `docs/superpowers/plans/2026-07-25-seed-missing-policy-files.md`.
- Steady state as of this commit (2026-07-23): the decisions-as-claims
  audit is CLOSED — 41 rulings audited (16 HOLDS, 20 HOLDS-UNENFORCED,
  2 HOLDS-UNSHIPPED, 2 STALE, 1 CONTRADICTED; verdict: incremental
  surgery), the full Fix Queue drained (commits per item in
  `docs/superpowers/plans/2026-07-23-audit-findings.md`). The
  owner-surface redesign Stages 1–3 landed (new-project installer;
  update overhaul + owner-driven remediation; vocabulary with `toolkit`
  verb, `drift` retired), the packaging stage is built (`tools/publish`,
  manifest completeness guard), and the product is named Bixi. The public
  Bixi repo and its first publish landed 2026-07-24 (product-repo path
  recorded in `.agents/machines.md`). Remaining external step: the owner's
  self-refresh of this repo's installed copies.
- Steady state as of this commit (2026-07-23): the model-map apparatus is
  deleted under the owner ruling "the owner's dispatch word is final; no
  committed model lists" — `.agents/model-map.json`, <!-- lint: allow (deleted in this change; named as the record of the deletion) --> its lint, the
  model-denylist lint, and the `harness-update` operator are gone (the
  operator's targets sit on the retired list, so deployed copies are
  removed on next refresh). Dispatch grammar is literal-or-ask in
  `templates/playbooks/codereview.md`; tier pairs are owner-named,
  recorded in the machine-local cache, no confirmation ritual. The
  2026-07-19 and 2026-07-09 (Codex eval) entries are archived.
- Steady state as of `b7448e2` (2026-07-22): the holistic toolkit
  improvement plan and the model-map reviewer dispatch plan are both
  CLOSED, each with its per-finding commit map in its plan doc under
  `docs/superpowers/plans/` (rotation details in
  `docs/history/state-archive.md`). GitHub issues #5–#8 are closed with
  commit receipts, each fix verified at HEAD first. Newest Active
  rulings in `.agents/decisions.md`: paperwork follows technical work
  (verified-fixed bookkeeping proceeds without an owner ask). The
  owner-communication tunable recorded here was retired 2026-07-25.
- Steady state as of `0d05c97` (2026-07-12): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/` (full
  enumeration in the 2026-07-12 rotation in
  `docs/history/state-archive.md`); the 2026-07-09 external holistic
  review is fully triaged, with release engineering deferred by the
  release-posture decision. New Active decision 2026-07-11 (`0d05c97`):
  reviewloop-branches Open item was closed as adopted and archived
  2026-07-12 (`76c1e5f`). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer, and ExchangeAdminWeb (details in
  `docs/history/state-archive.md`). Per-harness capability record:
  `docs/harness-capabilities.md`.

## Next

- None recorded. (Self-refresh is no longer pending: released 2026-07-25
  and verified current from the product clone that day — no template has
  changed since `064c27e`, so installed copies carry zero lag. The
  sanctioned self-refresh route is recorded in `.agents/repo-guidance.md`,
  Earned Practices.)

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
