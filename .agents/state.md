# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- 2026-07-18: owner-driven token-burn audit from local telemetry (this
  machine): since the 2026-07-17 15:00 (local) allotment reset,
  Claude-side burn is ~181M weighted sonnet-equiv; ~88% was interactive
  orchestrator sessions running review rounds inline on the premium
  interactive default (fable) — review labor landed inline after codex
  credits ran out (owner, in-session, 2026-07-17 ~21:30). Codex-side
  reviews ran pinned as designed (~6.2B raw, 98% cache hits). Root
  cause: claude was never a governed reviewer lane —
  `harnesses.local.json` entries are empty skeletons or absent across
  governed repos (machine-local state was load-bearing), and inline
  labor has no pin step. GH #6 (Vela) compounds it: MCP transport
  qualified by a model-only probe while reviewer children cannot use
  tool grants on Claude Code 2.1.214 — 9,378,752 tokens / 291 requests /
  zero verdicts. Owner rulings this session: no per-machine config
  edits; no load-bearing per-repo local state ("any solution that
  doesn't fix the problem globally is rejected"); no playbook leakage
  into AGENTS.md; probe/qualification machinery is too much engineering.
- 2026-07-18 PENDING (awaiting owner go — nothing landed): collapse
  reviewer dispatch to a shipped launch block: literal owner-maintained
  commands with pinned model ids in `templates/playbooks/codereview.md`
  (standard / frontier / claude lanes) + terminal-failure rule (a failed
  launch — retired model, credits, permission denial — stops, records
  one line, asks the owner; never improvise transports, agents, or
  settings around a dead lane); `harnesses.local.json` demoted to
  optional command override (absent = shipped defaults apply); delete
  transport preference, probe cache, and the self-permissioning
  MCP-equivalence claim (closes #6 by deletion; MCP readmitted only by
  passing an actual review); one test: every launch command in shipped
  text carries an explicit model flag. Supersession note: this reverses
  the 2026-07-17 review-economy rule that committed playbook text is
  model-free (curated-denylist lint in `tests/test_templates.py`) — that
  lint and the recorded decision must be amended in the same change.
- 2026-07-17: the review-economy plan is CLOSED with a commit map
  (`docs/superpowers/plans/2026-07-17-review-economy.md`). `codereview`
  now runs tiered reviewer routing — standard@high default,
  frontier@xhigh on mechanical escalation (T1–T5) or owner force;
  `openreview` pins frontier@max with no headroom (above max sits the
  owner). Committed playbook text is model-free (curated-denylist lint
  in `tests/test_templates.py`); concrete pins and per-tier transport
  (`mcp`/`cli`) live in the machine-local, gitignored
  `.agents/review/harnesses.local.json`; every dispatch records a
  `Reviewer:` provenance line with all matched triggers. Owner rulings
  (D1 routing table, D2 reopen escalation, D3 archive, D4 dissolved)
  recorded verbatim in `.agents/decisions.md` (2026-07-17); the GPT-5.6
  commissioning review is archived in `docs/history/`. This repo's
  installed copies lag until the owner's next self-refresh (owner-only).
  Dogfood: a final openreview over the landed range is owner-approved
  (2026-07-17) and runs after the closing commit; its findings are
  triaged in chat per the plan contract.
- Steady state as of `0d05c97` (2026-07-12): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/` (full
  enumeration in the 2026-07-12 rotation in
  `docs/history/state-archive.md`); the 2026-07-09 external holistic
  review is fully triaged, with release engineering deferred by the
  release-posture decision. The owner ran this repo's self-refresh
  2026-07-10 (`32b598a`, toolkit `5574147`). New Active decision
  2026-07-11 (`0d05c97`): push status is never recorded in state files —
  git owns it; the change is template-side, so installed copies lag the
  templates by that one change — the expected steady state until the
  owner's next refresh (owner-only rule, `292a4d2`). The
  reviewloop-branches Open item was closed as adopted and archived
  2026-07-12 (`76c1e5f`). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.

## Next

- **ExchangeAdminWeb**, the last legacy rollout repo, deferred by the owner
  to **2026-07-20** (re-affirmed 2026-07-09): run `tools/refresh.py`,
  resolve FLAG lines; oldest instance — 2026-06-22-era template, no
  repo-guidance.md, so it needs the bootstrap procedure's carve-out, the
  same path qbit-mobile exercised (carve-out done, owner report
  2026-07-12). The owner's fleet refresh (run by 2026-07-12) propagated
  the 2026-07-10/11 template changes to governed repos.

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
