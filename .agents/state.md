# Agent State

This file is the first place future agents should read for current repo state.
Keep it short: `## Now` holds only live entries. At each `handoff`, rotate
landed or superseded entries verbatim to `docs/history/state-archive.md`.
Volatile facts carry `as of <commit>`; counts owned elsewhere are pointed to;
machine-local facts are labeled or omitted.

## Now

- Steady state as of `59439e7` (= GitHub canon, verified via `git ls-remote`
  2026-07-09; this handoff's own commit lands on top): the 2026-07-08
  zero-based consolidation is landed and self-applied; the product shape is
  owned by `.agents/repo-guidance.md` (Mission Detail). Latest product
  change: refresh matching is newline-equivalent and both shims ship with a
  final newline — GitHub issue #1, fixed 2026-07-09, plan closed with commit
  map: `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`.
  Rollout is DONE for vela, Blit_v2, ai-rpg-engine, and
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.

## Next

- **Smoother bootstrap/refresh entry — proposal on the table, awaiting the
  owner's go and a command name** (discussed 2026-07-09; no decision entry,
  no plan, no code yet). The shape: (1) launcher shims `bin/agb` +
  `bin/agb.cmd` (POSIX sh / Windows cmd only — no PowerShell) that embed the
  documented interpreter-probe order, resolve the toolkit root from their
  own location, and exec `tools/refresh.py`, plus a one-time per-machine
  PATH step; (2) a `bootstrap` operator skill + wrapper added to the shipped
  set (no machine paths — anchored on the canonical GitHub URL like the
  `update-governance` wrapper; self-guards when `.agents/repo-guidance.md`
  already exists); (3) refresh's closing output points at `/bootstrap`
  whenever the judgment layer is missing or `AGENTS.md` flags foreign.
  Owner-set constraints: must not assume Claude, PowerShell, a remembered
  path, or a remembered interpreter. Related owner attestation (stated
  2026-07-09, **not yet a decision entry** — record on go): the owner never
  hand-edits `AGENTS.md`; in this fleet an unmatched `AGENTS.md` is
  old-generator output to relocate, never owner edits. Deferred option if
  the EAW carve-out grates: fingerprint-gated preserve-then-replace for
  legacy `AGENTS.md` (old file preserved under `docs/history/`, template
  installed, only when toolkit fingerprints are present).
- **ExchangeAdminWeb**, the last legacy rollout repo, deferred by the owner
  to **2026-07-20** (re-affirmed 2026-07-09): run `tools/refresh.py`,
  resolve FLAG lines; oldest instance — 2026-06-22-era template, no
  repo-guidance.md, so it needs the bootstrap procedure's carve-out, the
  same path qbit-mobile is exercising now.
- qbit-mobile (fleet context, 2026-07-09): refresh at toolkit `319324e`
  installed the shipped set and flagged its legacy `AGENTS.md`; the owner is
  running the bootstrap carve-out there — the first live exercise of the
  legacy-flag path. Not this repo's work item; friction observed there fed
  the smoother-entry proposal above.
- Issue #1 GitHub closure (comment-and-close, outward-facing): **awaits an
  explicit owner go**.
- Owner, at leisure: archive the `agent-harvest` dropbox repo (re-verified
  still unarchived 2026-07-09 via `gh repo view --json isArchived`).
- Drift-sweep candidate, advisory only: the always-on lint reports dead-path
  references inside historical `.agents/decisions.md` entries (retired
  substrate named in verbatim records — e.g. `tools/discover.py`,
  `procedures/migration.md`). Reproduce with any refresh run; decide
  annotate-or-leave at leisure.

## Blockers

- None recorded.

## Verification

- See `.agents/repo-guidance.md` (Verification) — canonical home.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
- `.agents/decisions.md`
- `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`

## Unrecorded Repo Memory

- None known.
