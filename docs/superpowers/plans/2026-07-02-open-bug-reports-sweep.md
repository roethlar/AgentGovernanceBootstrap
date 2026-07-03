# Fix the open bug reports in the agent-harvest dropbox

Status: DRAFT 2026-07-02 — awaiting owner approval before S2 (code) lands.

## Why this plan exists

An owner-requested check of `roethlar/agent-harvest` `bugs/` (2026-07-02) found
six reports. Two (the 2026-06-23 headroom pair) are already folded into
`.agents/decisions.md`. One (`ExchangeAdminWeb-hook-python3-discovery-2026-07-02`)
records its fix as landed (commits 63b5db0, 79783bb) with one loose end. Three
items remain actionable:

1. **`incident_june-claude-local-only-false-migration-2026-06-24` — still live.**
   A repo whose only governance-pattern match is a git-ignored
   `.claude/settings.local.json` routes as `migration` instead of `greenfield`.
   Verified against the current tree: `tools/discover.py` matches `.claude/*` in
   `GOVERNANCE_MARKER_PATTERNS` (line 75), marker matching consumes
   tracked + untracked + **ignored** paths alike (`all_paths`, lines 659–671),
   and `compute_route` returns `migration` on any non-empty marker set
   (line 248–254).
2. **`ai-rpg-engine-shim-harness-scoping-2026-07-02` — still live.**
   `procedures/bootstrap.md` step 5 (lines 313–318) and `procedures/migration.md`
   Step 4 item 1 (lines 110–114) scope shim drafting to "the harness you are
   running in," so shims for other harnesses with shipped templates
   (`templates/shims/CLAUDE.template.md`, `GEMINI.template.md`) are never drafted
   or refreshed. This contradicts the "all routes, regardless of which harness"
   pattern the same file uses for operator wrappers (lines 161–177) and hooks
   (line 211). Owner confirmed during the ai-rpg-engine run: "shims should always
   be copied/updated regardless of harness. that was a rule that drifted out of
   the repo."
3. **`ExchangeAdminWeb-template-invariant-duplication-2026-06-24` — overtaken by
   events, needs a triage record.** The report's own bite-proof passes on the
   current `templates/AGENTS.template.md` (post 2026-07-02.1 reflow): "words
   first", "no code change", and "durable truth" each appear exactly once. No
   product change is needed; the resolution just isn't recorded anywhere, so the
   report still looks open.

Plus one loose end from the fix-landed report: the hook-python3 Windows
bite-proof (edit AGENTS.md on a real Windows host, confirm the tripwire
reminder appears) has never run — no Windows host available in the fix session
or this one. That is a pending-verification note, not work this plan can execute.

## Scope

- `tools/discover.py` + `tests/` (S2).
- `procedures/bootstrap.md`, `procedures/migration.md` (S3).
- `harvest/processed.md`, `.agents/state.md` (S4 closeout records).
- **Not** the dropbox bug files themselves — append-only, never edited in place.

## Slices

- S1 (docs): this plan. Verification: `git diff --check`. — commit: (fill)
- S2 (code): route fix for the false-migration bug. Two changes, each covering
  a case the other misses:
  1. Compute `governance_markers` from tracked + untracked paths only — paths
     whose record source is `ignored` no longer feed route computation.
     Rationale: a git-ignored file is machine-local by definition and cannot be
     durable governance (the toolkit's own custody rules already say ignored =
     local-only). Non-git repos are unaffected (everything is untracked there;
     no ignore semantics exist to consult).
  2. Exclude `.claude/settings.local.json` from governance-marker matching
     regardless of source, so an untracked-but-not-ignored copy (the common
     state on a machine without a global ignore rule) also cannot flip the
     route alone.
  Tests (in `tests/test_discover.py`, pure-function level, plus a fixture run if
  the golden manifests shift — regen via `tests/regen_golden.py` only if the
  shift is the intended one):
  - ignored-source `.claude/settings.local.json` as the only match →
    `greenfield` (the report's reproduction).
  - untracked `.claude/settings.local.json` as the only match → `greenfield`.
  - tracked `.claude/commands/foo.md` → still `migration`.
  - tracked `AGENTS.md` → still `migration`.
  Guard proof per the Verification invariant: revert the fix on a throwaway
  copy, confirm the new tests fail, restore, confirm the full suite passes.
  Verification: `python3 -m unittest discover -s tests -v`. — commit: (fill)
- S3 (procedures): reword shim drafting to the all-harnesses pattern, per the
  report's proposed fix. In `bootstrap.md` step 5 and `migration.md` Step 4
  item 1: loop over every harness the toolkit ships a
  `templates/shims/<harness>.template.md` for — draft any missing shim and
  refresh each one present in the target repo — mirroring the "drafted on every
  route regardless of which harness you are running in… the wrappers are for
  the repo, not for your current session" framing already used for operator
  wrappers. Reserve "judge from self-knowledge of the harness you are running
  in" for exactly two residual calls: whether the *current* harness needs a
  best-effort no-template shim, and native-AGENTS.md-reader judgment.
  Procedures are copied content, so verification is the full suite:
  `python3 -m unittest discover -s tests -v`. — commit: (fill)
- S4 (docs): closeout records. Add triage lines to `harvest/processed.md`
  (extending its ledger to bug reports, which currently have no triage ledger):
  the duplication report as resolved-by-prior-work (2026-07-02.1 reflow /
  condensation, bite-proof passes), and — once S2/S3 land — the false-migration
  and shim-scoping reports as fixed with their commit hashes. Note in
  `.agents/state.md`: hook-python3 Windows bite-proof still pending a Windows
  host. Verification: `git diff --check`. — commit: (fill)

One report per commit (Git Safety): S2 and S3 each close exactly one report.

## Non-goals

- No edits to files in the agent-harvest dropbox (append-only invariant);
  triage state lives in this repo.
- No filtering of `agentMarkers` — it is informational, does not drive routing,
  and truthfully reporting "this repo has harness-local state" is fine.
- No re-fix of the hook-python3 report (fix already landed); only the pending
  Windows verification is recorded.
- No harvest-report sweep (harvest sweeps run only on explicit owner request;
  this plan covers `bugs/` only, as requested).
