# Agent State

This file is the first place future agents should read for current repo state. Keep it
short and update it when important repo facts change.

## Now

- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
- Governance for this repo itself is in `AGENTS.md` (Prime Invariants, universal and repo-specific rules, operator vocabulary, and pointers) plus this `.agents/` layout (state and decisions).
- 2026-06-21: this repo's own governance was brought current with the product it ships (it had intentionally lagged since 2026-06-20). The self-application added a `CLAUDE.md` shim (`@AGENTS.md`), committed `.claude/commands/` wrappers for the full operator set (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`), and a committed `.claude/settings.json` re-ground hook (fires on context compaction, points back to AGENTS.md). `AGENTS.md` was rewritten to the product shape: a `## Prime Invariants` block, a `## Universal Invariants` section, `## Operator Requests`, a `## Session Startup` trust note, and an updated `## Bootstrap Handoff` that audits wrappers and re-ground hooks. (`.claude/settings.local.json` stays machine-local and untracked.)
- 2026-06-21: the load-bearing-invariant enforcement work landed and is recorded as Adopted — a lean Prime Invariants block plus per-harness re-ground hooks (`templates/hooks/<harness>/`) that fire on compaction, with tests and a design spec (`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`). This resolved the last item that had been deferred to this re-run.
- 2026-06-22: closed the update-route template-reconciliation gap. `AGENTS.md` files now carry a `<!-- templateVersion -->` stamp; discovery records an `agentsTemplate` manifest block (current/target version, `reconcileRecommended`, `missingSections`) and, on the update route, the toolkit reconciles a stale or unstamped `AGENTS.md` to the current template before running the wrapper/hook guarantees. Wrapper/hook guidance treats a missing target section as a staleness signal to reconcile, not a cue to narrow the artifact. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: trimmed the per-session guidance tax. A density audit showed prose compression saves only ~2.7% (the guidance is dense, not padded), so instead the `## Bootstrap Handoff` section was collapsed to a conditional pointer to the synced `.bootstrap-tmp/procedures/bootstrap.md` (~600 tokens/session off `AGENTS.md`; the procedure is now the single canonical home for the handoff/reconciliation/wrapper-guard logic), and the token-efficiency invariant now encourages `rtk` as a discretionary per-command proxy (not an auto-rewrite hook) plus compact-but-equivalent working. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: the `agent-harvest` dropbox now also stores bug reports (defects in this product) under a `bugs/` folder. Agents auto-write a report from `templates/bug-report.template.md` and file it via the canonical recipe `procedures/file-bug-report.md` (gh-api preferred, clone fallback, in-repo last resort), publishing only on an explicit owner go; the harvest sweep triages `bugs/`. See the 2026-06-22 decision in `.agents/decisions.md`. The `agent-harvest` repo gained a `bugs/` folder and a README section to match.
- 2026-06-22: unified the two dropbox-write paths. The transport mechanics now live in one shared recipe, `procedures/file-to-dropbox.md`, used by both harvest reports (`migration.md` Step 8) and bug reports (`file-bug-report.md`). Harvest submissions gained the no-clone `gh api` transport and lost their former standing auto-push: every dropbox publish now asks for an explicit owner go. The `gh api` PUT/DELETE path was verified end-to-end against `roethlar/agent-harvest`.
- `.agents/decisions.md` owns the live decision queue (Active entries plus the `## Open Decisions` queue); closed entries are rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule. See that file for the current open/active set rather than echoing a count here.
- 2026-06-25: rewrote the `reviewloop` playbook template (`templates/playbooks/reviewloop.md`) from the async sentinel/watcher design to a synchronous `review <agent>` flow, and added the `.claude/commands/review.md` wrapper. The coder (current harness) dispatches a named reviewer harness (codex/agy/grok/subagent) headless and one-shot per finding, deriving the headless incantation live by probing (no human-maintained table), parses a structured fail-closed JSON verdict (`{verdict, guard_confirmed, reviewed_sha, base_sha, comments}`), records it into the finding doc, and acts under owner-gated merge. The reviewer's guard proof runs in its own git worktree against a pinned base SHA. Design and the cross-harness review that hardened it: `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`; plan: `docs/superpowers/plans/2026-06-25-synchronous-review-handoff.md`. `review` is a playbook operator, intentionally kept out of `OPERATOR_WORDS`.
- 2026-06-25: added the **stall-not-length** Universal Invariant to `templates/AGENTS.template.md` (iterative processes escalate on a cycle that banks no verifiable progress, never on duration; long converging runs are not capped), `templateVersion` bumped to 2026-06-25. Adopted — see the 2026-06-25 entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance).
- 2026-06-25: implemented the **AGENTS.md governance boundary** (portable + write-authority) in three layers. Two Universal Invariants in `templates/AGENTS.template.md` (portability copy-test; written-only-by-gated-bootstrap/update); the `drift` operator now names AGENTS.md portability/write-authority as drift targets; and an advisory, non-blocking `PreToolUse` pre-edit tripwire (one stdlib-Python `agents-md-tripwire.py` shared by the Claude Code + Codex hook configs) ships under `templates/hooks/`. `templateVersion` 2026-06-25 → 2026-06-25.2 (same-day second structural change). Layer 2 was validated live before building (fires/visible/non-blocking on Codex and on GLM via Claude Code; self-revert seen once); evidence reframed the spec to L1-primary / L3-backstop / L2-advisory. `TestHookTemplates` was reworked from shape-banning to a portability principle so script hooks pass without per-category exceptions. Adopted — see the 2026-06-25 boundary entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance). Spec: `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`.
- 2026-06-25: wrote the **AGENTS.md retroactive-cleanup follow-on spec** (`docs/superpowers/specs/2026-06-25-agents-cleanup-via-update-route-design.md`) — design only, awaiting owner review then a `plan`. Decision recorded in it: cleanup is the update-route reconciliation *extended*, not a parallel flow. Key design move (owner insight): detect leaks as **surplus over the portable template** — the structural inverse of `missingSections` (which flags what the target *lacks*; surplus flags what it *has beyond baseline*), so a leaky-but-current, structurally-complete `AGENTS.md` still triggers, and non-path leaks (prose, restated state, the repo's name) are caught where a regex would miss them. Discovery computes surplus structurally; the agent sorts each surplus item into allowed-repo-specific vs leak (surplus ≠ leak: the Current State pointer, Active Sources list are legitimate surplus). Relocation rule (owner-settled): move leaks into `.agents/` with **no per-fact pointer** — keep only the existing structural pointers; rare exception when a governance rule's meaning references a repo-specific detail.
- 2026-06-27: **push policy is now repo-specific, delegated to `.agents/push-policy.md`.** The Prime Invariant push clause in `templates/AGENTS.template.md` no longer carries a blanket push-needs-go rule; it reads "History-rewrite and destructive or outward-facing actions always need an explicit go. Push policy: see `.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the default (`ask`); `templates/approval-summary.template.md` gained a Push Policy section that presents four standardized options (1 always / 2 operators / 3 docs / 4 ask) and must ask the human at approval time (do not pre-fill from the decisions log); `procedures/bootstrap.md` Step 10 consults the policy file after committing. `templateVersion` bumped to `2026-06-27.1`. Adopted — see 2026-06-27 push-policy decision in `.agents/decisions.md`.
- 2026-06-27: **this repo's own governance brought current via a dogfood / self-application run** (the deferred frozen-instance reconciliations all landed in one scoped commit `b844c72`): `AGENTS.md` reconciled `2026-06-22` → `2026-06-27.1` (push clause now delegates to push-policy; stall-not-length invariant; both governance-boundary invariants; sharpened drift/playbook operators; Session Startup mentions the tripwire), `.agents/push-policy.md` created set to **`always`** (every commit here pushes immediately), and the advisory AGENTS.md pre-edit tripwire installed (`.claude/settings.json` PreToolUse block + `.claude/agents-md-tripwire.py`, byte-identical to the shipped template). Repo-specific leaks left in place — their relocation is the separate owner-gated cleanup spec.
- 2026-06-27: **dogfood / self-application named as a case of the update route** — `procedures/bootstrap.md` now states that running the toolkit against itself is an in-place update run and a missing `.bootstrap-tmp/` at kickoff is the normal start, never a stop. Docs handrail only, no `compute_route()` detection. Adopted — see 2026-06-27 dogfood decision in `.agents/decisions.md`. Earned by two fresh sessions stopping to ask "is there anything to do here" on the canonical kickoff line.
- 2026-06-27: **`drift` cleanup of `.agents/decisions.md`** — two adopted entries that were parked in `## Open Decisions` (push-needs-explicit-go, and `run_git` fails open / Adopted 2026-06-23) moved **verbatim** to `docs/history/decisions-archive.md` per the archive rule; the push-policy decision relocated from Open into `## Decisions` as Active (its stale "must be created by running the update route" line corrected — the dogfood run already created it, set to `always`). The Open queue is now exactly nine genuine `Open:` items, no adopted/active mixed in.
- 2026-06-27: all work this session pushed to GitHub (`origin/master` at `1c4fb50`); the gitea mirror follows downstream (observed lagging earlier in the session; catches up). Per the `always` push policy, commits here push immediately rather than awaiting a per-instance go. (This handoff's own commit lands on top and is pushed next; a state line cannot name its own not-yet-created hash.)

## Next

- 2026-06-29 **HANDOFF — RESUME HERE. Eval workstream pivoted to SWE-bench Pro; blocked on an
  amd64 Linux box.** Read this block first, then the two plans named below. Owner will pick up on
  their own x86_64 Linux machine.

  **Where we are:** the governance-efficacy eval's *measurement instrument* is fully built and
  pushed (Phase 0 hardening + the Phase-1 fixture/arms machinery — see the dated entries below).
  But the **synthetic-fixture approach is DEAD**: the frontier-calibration run (Slice F) showed
  Claude clean-passes all 5 hand-built fixtures 10/10 and GPT-5 the same on the 2 it finished —
  zero naive traps, every fixture drops as "too easy" (a model can't invent a bug that stumps
  itself). That result is the whole reason for the pivot; do not retry synthetic fixtures.

  **The pivot (owner-directed):** use **ScaleAI SWE-bench Pro** as the fixture source. Full local
  checkout at **`/Users/michael/Dev/SWE-bench_Pro-os`** (731 real instances in
  `helper_code/sweap_eval_full_v2.jsonl`, 11 repos, multi-language, frontier-resistant). Mapping:
  **FAIL_TO_PASS = our FuncPass, PASS_TO_PASS = our SecPass/regression guard**, so our existing
  **`joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS`** metric and invalid-trial accounting apply
  unchanged. Their `swe_bench_pro_eval.py` is a pure function `(predictions.json, sample) →
  resolved` that scores a patch inside a per-instance Docker image — agent and scorer are
  decoupled by a predictions-JSON file boundary. Integration plan (DRAFT, pre-codex-review):
  **`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`** (pipeline,
  phases P0–P3, open decisions G1–G5). Background + why-the-synthetic-approach-died:
  **`docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`** (its SWE-bench Pro
  addendum supersedes it; the crafting loop is the documented fallback only).

  **THE BLOCKER (why we stop here):** SWE-bench Pro instance images are **amd64-only** and their
  **test runtimes segfault under Rosetta/QEMU on Apple Silicon** — verified: `uname -m` works
  (`x86_64`) but `python3 --version` segfaults inside `jefzda/sweap-images:ansible...`; stock
  amd64 ubuntu runs fine, so emulation is engaged but unfaithful for CPython/Node test frameworks.
  Owner's decision: **run the Docker eval on a real x86_64 Linux box.** Local Colima (vz+rosetta,
  8cpu/24gb/200gb disk) is up on the Mac but is NOT a usable substrate for scoring; it can stay
  for our own unit tests but not for SWE-bench Pro images.

  **Public images:** `jefzda/sweap-images` on Docker Hub (the metadata jsonl points at a *private*
  ScaleAI ECR; ignore that). Derive the pull tag with `helper_code/image_uri.get_dockerhub_image_uri(
  instance_id, 'jefzda', repo)` (it truncates tags >128 chars). Score with
  `swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
  --dockerhub_username jefzda --use_local_docker`.

  **NEXT ACTIONS on the Linux box (in order):**
  1. **P0 — gold round-trip (no governance yet):** on the amd64 box with Docker, pull ONE instance
     image, run `swe_bench_pro_eval.py` on that instance's **gold `patch`** (shipped in the jsonl)
     and confirm it scores **resolved**. This proves the substrate before producing any agent patch.
  2. Decide the architecture (open in the plan): **Option A** = agent runs + scores all on the box;
     **Option B** = governed agent runs on the Mac (our harness/hooks/keys already work), patches
     copied to the box which only scores. Option B needs local `git clone <repo>@base_commit` for the
     agent's workspace; Option A needs model API keys + our harness on the box.
  3. Then P1 (instance adapter + clean patch capture — exclude governance overlay/sentinels from the
     diff), P2 (subset selection: ungoverned FAIL_TO_PASS probe, keep ~20 mid-band instances across
     diverse repos), P3 (the none/prose/prose-hooks factorial). Codex-review the integration plan to
     convergence before building (the workstream's standing discipline).

  **Biggest risk to watch (in the plan):** floor mirror of the earlier ceiling — SWE-bench Pro is
  HARD, so a one-shot Claude-Code/codex driver may resolve ~0 ungoverned, leaving no room to show
  improvement. Subset selection (mid-range ungoverned rate) guards this; if even mid-band instances
  resolve at ~0 the driver (G3) needs a real agentic loop before the factorial.

  **What's reusable as-is:** governance profiles (`evals/governance_profiles/`: none,
  current-template, hook-gate, hook-guard, prose-hooks), `joint_pass`+invalid accounting in
  `evals/aggregate.py`, the claude/codex drivers in `tools/drivers.py`, `evals/calibrate.py`
  (its classify/Wilson logic still scores an ungoverned probe). **Retire/ignore for SWE-bench Pro:**
  the 5 synthetic fixtures, `--check-discrimination`, the calibration *band* gate as a fixture
  source. **Test interpreter: homebrew `python3` (3.14)** — system 3.9 can't parse the tests.
  All eval work pushed to `origin/master` (last: SWE-bench Pro integration plan draft).

- 2026-06-28: **active research workstream — governance-efficacy measurement (`evals/`).** A
  validated, three-times-externally-reviewed experiment plan to measure whether (and which)
  governance components causally help coding agents, lives at **`evals/TEST-PLAN.md`** — start at
  its **§15 "Resume here"** for status, the built harness, model hosts, gotchas. Screening
  findings in `evals/RESULTS-*.md` (frontier models ceiling; security prose ≈ placebo; hooks
  transfer, prose is model-capped). This is a measurement effort *about* the toolkit, separate
  from the toolkit's product backlog below.
- 2026-06-28: **Phase 0 (harness hardening) is COMPLETE and pushed** (master 2bcf6ae..747078b).
  Owner suspended per-slice go for this eval workstream; plan was codex-reviewed to convergence
  (3 passes) first. Seven slices, each committed + mutation-proven + pushed (push policy `always`):
  S1 changed_files fix (overlay before trial-base) + profile collision guard; S2 strip
  pre-existing governance (deletion-safe subset, narrower than discover's detection list);
  S3 driver telemetry (tokens/cost/tool_calls) + transcript redaction to a **gitignored**
  `evals/results/transcripts/`; S4 hook telemetry (present/supported_by_driver/fired via an
  **external** sentinel) + new `hook-smoke` profile; S5 `profile_tokens`; S6 result
  `schema_version`=2 + aggregator telemetry columns & mixed-schema flag. Plan +
  S7 live-smoke evidence: `docs/superpowers/plans/2026-06-28-phase0-harness-hardening.md`.
  **Test interpreter note:** the suite needs **homebrew `python3` (3.14)** — the system
  `/usr/bin/python3` (3.9) cannot parse the tests' `X | None` annotations. 104 tests green.
  Four clean baseline fixture repos prepped under `../test_ground/` (blit_v2, headroom,
  qbit-mobile, rtk — governance stripped, fresh `git init`, no remotes).
  **Model-host note:** drive local models via the **on-host ollama (`localhost:11434`)** —
  local set is `qwen3.6:35b-mlx`, `gemma4:31b-mlx`, `ornith:35b`,
  `north-mini-code-1.0:mlx-mxfp8`. The remote `10.1.10.221` ("Q") is a different host
  serving mostly `:cloud` models and is **not** the local-model source. S7 smoke was
  validated on the local `qwen3.6:35b-mlx` (FuncPass + live hook firing).
  **Next: Phase 1** (build the real-repo fixture set from those repos, calibrate, freeze) —
  per TEST-PLAN §10. Phase 1 is approvable once fixture manifests + metric defs exist; the
  open owner decisions in TEST-PLAN §12 (tier, repos, H6 approval arm, proportionality rule)
  still gate the *screening* runs, not fixture construction.
- The `.agents/decisions.md` "Open Decisions" section is the authoritative queue for deferred/owner-approved-but-unimplemented items; consult it for what is awaiting a plan. Do not echo its count or contents here (anti-enumeration invariant) — read the section.
- **Decided 2026-06-28 — collapse the `update` route into `migration`.** Resolves the former self-contradictory `Open: bootstrap.config.json` fork (the owner chose to dissolve it, not pick (a)/(b)); that Open entry is archived verbatim in `docs/history/decisions-archive.md`, and `bootstrap.config.json` is dropped from the documented layout. The decision is recorded in `.agents/decisions.md` (2026-06-28); the implementation **plan is drafted at `docs/superpowers/plans/2026-06-28-collapse-update-route.md`** (six slices: discover.py+tests, the two procedures, README, the AGENTS template, and Open-entry rewording) and **awaits an owner go to implement** — no code touched yet. Key design point captured in the plan: the `update` route *fork* is removed but the stale-`AGENTS.md` reconciliation is *retained* (re-homed as a conditional in the migration route, gated by `agentsTemplate.reconcileRecommended`, not by a route name). Until the plan lands, the code still has three routes (the "Now" three-route line above is current and correct).
- Possible queue trim (owner hunch, unconfirmed): the `Open: route/verification probes match literal package.json` (monorepo subdir) item is gated on a precondition — whether subdir-scoped bootstrap is a supported mode. If it is not, close as not-applicable rather than fix. Resolving that precondition may drop it from the queue.
- Run harvest sweeps in this repo only on explicit owner request as harvest reports and bug reports accumulate in the dropbox (or fallback).
- Deferred: fix the `tools/discover.py` `operator:playbook` false positive (probe matches bare `` `playbook` `` but the operator is written `` `playbook <name>` ``, so the update route over-reports `reconcileRecommended`). The bug was filed to the `agent-harvest` dropbox on 2026-06-22; the fix (discover.py + a test using the realistic `` `playbook <name>` `` shape) is a separate scoped change awaiting owner go.
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.
- 2026-06-25: the **AGENTS.md governance boundary** (all three layers) is implemented and Adopted (see "Now" and the 2026-06-25 boundary decision). The **retroactive-cleanup follow-on is now specced** (see "Now" above) and **awaits owner review, then a `plan`**. Its three open questions for the plan: (1) signal shape — a separate `cleanupRecommended` vs. folding into `reconcileRecommended` (leaning separate); (2) sequencing — does the surplus computation ship inside the queued `governance-lint` playbook (Open Decision, 2026-06-22) or as a standalone discovery field, given `governance-lint` is approved-but-unbuilt (don't couple two unbuilt pieces); (3) within-section match granularity — how precisely a reworded target bullet must match its template counterpart before the remainder counts as surplus (lean toward over-reporting; the agent confirms, and a missed leak is the unsafe failure).
- 2026-06-27: **push-policy work is complete** (decision adopted, product changed, this repo dogfooded to `always`). The plan is at `docs/superpowers/plans/2026-06-27-push-policy.md`. Out of scope and not done: `discover.py` reading the `push-policy` marker; update-route reconciliation of *already-bootstrapped* foreign repos (they draft the file and ask on their next update run). No follow-up owed unless those are wanted.
- Deferred: the synchronous `review <agent>` operator ships as a playbook + Claude Code wrapper only. If it is ever promoted to a governance operator advertised in every `AGENTS.md`, the `OPERATOR_WORDS` staleness probe must first be reconciled with the existing deferred `operator:playbook` false positive (above) — adding `review` there would compound it. Not blocking; documented so the promotion is a deliberate step.
- Playbook process note: dispatching `codex` as a reviewer needs the prompt piped via **stdin** (`codex exec --skip-git-repo-check < prompt`), not as a positional arg — the argv form hung on stdin and timed out during the 2026-06-25 boundary-spec review. Worth folding into `templates/playbooks/reviewloop.md` when next touched.

## Blockers

None recorded.

## Verification

- Changes that touch `tools/discover.py`, `tests/`, or any content under `templates/` or `procedures/` that the discover script copies into target repos: run `python3 -m unittest discover -s tests -v`.
- Documentation-only changes (no effect on setup, commands, runtime behavior, generated files, or user-visible behavior): run `git diff --check`.
- See `AGENTS.md` Verification section and `.agents/repo-map.json` for the policy that applies to future agents.

## Active Sources

- `AGENTS.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `README.md`
- `docs/usage.md`
- `docs/design.md`
- `docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md`
- `tools/discover.py`
- `procedures/*.md`
- `templates/*`

## Unrecorded Repo Memory

None known.
