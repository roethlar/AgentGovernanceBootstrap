# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `292a4d2` (verified `git ls-remote origin HEAD` ==
  local, 2026-07-10; clean tree except untracked items noted below): the
  2026-07-08 zero-based consolidation is landed and self-applied; the
  product shape is owned by `.agents/repo-guidance.md` (Mission Detail).
  2026-07-10 owner session landed: governance refresh at toolkit `d3f49d3`
  (`65a8543`), the plan-contract decision (plan docs are agent-facing;
  owner decisions in chat, 25–50 plain words, one at a time — `d3f49d3`),
  the self-refresh-is-owner-only decision (`292a4d2`), and four draft plans
  from the holistic review (`650a122` trust-boundary hardening, `decace2`
  handoff fast-snapshot split, `eaffc7a` fresh-eyes clone rehearsal,
  `a7a6cd7` legacy carve-out commit shape); a plan-linter question is
  queued Open (`b7a5af6`). Earlier landed work: bootstrap-offer banner
  (`f65e892`), dead-path lint (`e9e04b4`), newline equivalence (issue #1) —
  plans closed under `docs/superpowers/plans/`. Rollout DONE for vela,
  Blit_v2, ai-rpg-engine, Powershell-Token-Killer (details in
  `docs/history/state-archive.md`). Per-harness capability record:
  `docs/harness-capabilities.md`.
- pxpipe provenance-safe compression (agent session 2026-07-10; volatile
  facts as of pxpipe branch head `bddb502`): the approved plan is fully
  implemented — slices 1–5 on `fix/provenance-safe-compression` in the
  pxpipe repo — and the slice-by-slice `reviewloop` (codex-cli 0.144.1
  reviewer, independent guard proofs in disposable worktrees) is recorded
  on that branch under `.agents/review/` (canonical scoreboard:
  `.agents/review/index.md` there — pointer, not a copy). Slices 1–4 closed
  **accepted**, with four review-driven fix commits (`371322d`, `4dca949`,
  `ee992d3`, `c3e8744`); slice 5 (`162a00f`, docs+eval) is **reopened at r1
  with 14 findings pending coder adjudication — the next action**
  (adjudication notes pre-written in its finding doc). Verification at
  `bddb502`: 752 tests + typecheck + build green (build needs
  `npx -y -p pnpm@10.21.0 npm run build` when pnpm is off PATH). The live
  A/B matrix (plan §7) is NOT run and stays separately owner-gated; merge
  to pxpipe main stays owner-gated. Canonical plan copy:
  pxpipe `docs/PROVENANCE_SAFE_COMPRESSION_PLAN.md` (checkpoint re-anchored
  `bddb502`; the AGB-root snapshot copy was removed by the owner
  2026-07-10). Machine-local (this Mac): implementation worktree
  `/private/tmp/pxpipe-provenance-fix` (tmpfs-adjacent — lost on reboot;
  the branch itself lives in `/Users/michael/Dev/pxpipe`), codex review
  transcripts `/private/tmp/codex-slice*.jsonl` (verbatim verdicts already
  copied into the finding docs). Dispatch incidents (one codex usage-limit
  window, one codex content-filter kill mid-r3, both recorded fail-closed
  and retried per playbook) are logged in the finding docs.

## Next

- **ExchangeAdminWeb**, the last legacy rollout repo, deferred by the owner
  to **2026-07-20** (re-affirmed 2026-07-09): run `tools/refresh.py`,
  resolve FLAG lines; oldest instance — 2026-06-22-era template, no
  repo-guidance.md, so it needs the bootstrap procedure's carve-out, the
  same path qbit-mobile is exercising now.
- qbit-mobile (fleet context, 2026-07-09): refresh at toolkit `319324e`
  installed the shipped set and flagged its legacy `AGENTS.md`; the owner is
  running the bootstrap carve-out there — the first live exercise of the
  legacy-flag path. Not this repo's work item; friction observed there fed a
  smoother-entry proposal, declined by the owner 2026-07-09 (rotated
  verbatim to `docs/history/state-archive.md`).

## Blockers

- None recorded.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`
- `docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-handoff-snapshot-and-machine-local-state.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-fresh-eyes-clone-rehearsal.md` (open, drafted 2026-07-10)
- `docs/superpowers/plans/2026-07-10-carve-out-commit-shape.md` (open, drafted 2026-07-10)
- pxpipe branch `fix/provenance-safe-compression` → `.agents/review/index.md` + `docs/PROVENANCE_SAFE_COMPRESSION_PLAN.md` (external repo; active agent workstream)

## Unrecorded Repo Memory

- Untracked in the worktree, owner-side, not assessed by the agent:
  `HOLISTIC-REVIEW-GPT-5.6-SOL.md` (evident source of the 2026-07-10 plan
  drafts) and `docs/superpowers/plans/2026-07-10-plan-lint-suite.md` (draft
  behind the Open plan-linter question, `b7a5af6`).
