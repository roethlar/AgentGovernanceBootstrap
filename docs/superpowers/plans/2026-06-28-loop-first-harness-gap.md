# Plan — Loop-first harness-gap experiment (eval-gated)

Owner-initiated (owner "go" to draft). **Durable plan only; no code lands until the
owner gives go on a slice.** Cross-harness reviewed by Codex 0.142.1 (read-only) on
2026-06-28; its corrections are folded in below.

Implements the loop-first proposal in `../Notes/agent-governance-loop-first-pack/`
(GPT's revision after the `Review_For_GPT_Agent_Bootstrap.md` critique), restricted
to what this toolkit repo can land safely.

## Motivation

The Endor "Fable 5, take two" result: same model, ~+13 FuncPass and better SecPass
under Cursor than under a native harness. Governance prose is read *by* a harness but
does not change its between-turn loop; only a `Stop` hook does. So we must not ship
attention-shaping prose on faith. **We build the measuring instrument first, then let
evidence decide what ships.**

## Goal

Stand up a durable **eval harness** in this repo that scores a *governance profile*
against fixtures on the dimensions that matter for the harness gap (functional pass,
security pass, no-premature-stop, no-stall-loop, verification honesty), then promote
loop-first pieces into the product templates only where measurement shows a gain
without new stalls.

## Load-bearing realizations (read before implementing)

- This repo is the **toolkit**, not a target app. "Governance profile" = which
  AGENTS.md / hook / repo-map set a *fixture workspace* carries during a trial. The
  harness parameterizes over profiles; it does not touch this repo's own governance.
- The `current-template` profile must be **generated from the product templates**
  (via `tools/discover.py` output), NOT copied from this repo's own `AGENTS.md` —
  this repo carries dogfood/self-specific state that would contaminate the baseline.
- The eval harness is a **durable instrument** useful for any future governance
  change. That is why it lands first and unconditionally; every prose/hook piece
  lands conditionally, behind its results, and stays in an **eval candidate profile**
  until a trial earns it a place in `templates/`.
- Adoption order is the spine, and every arrow is a gate:
  **build instrument → measure baseline → candidate prose → measure → candidate +
  Stop gate → measure → promote only proven pieces.**

## Non-goals

- Do **not** add `stop_gate.py`, the AGENTS snippet, repo-map fields, the
  change-execution playbook, or the 7 rubrics to `templates/` in the early slices.
  They live in an eval candidate profile and are promoted only by Slice 6, gated on
  evidence.
- Do **not** edit this repo's own frozen `AGENTS.md`. Any product AGENTS-template
  change rides the gated update route, not an ad-hoc edit.
- Do **not** ship hard-deny policy hooks. Advisory/ask only.
- Do **not** ship `repo_truth_lint.py` as a second linter. Fold it into the already
  open 2026-06-22 `governance-lint` decision (playbook + small checker) or open a
  separate governance-lint plan. Out of scope here.
- Do **not** claim the experiment "closes the Cursor gap." Framing: it measures
  whether governance moves the needle at the margin.

## Verification (every slice)

- New Python under `evals/` or `tools/` → `python3 -m unittest discover -s tests -v`
  plus the scorer's own unit tests. **Fixtures use stdlib `unittest`, not `pytest`**
  (pytest is not installed here; match the repo baseline).
- Each new test gets the revert-the-fix guard proof (revert change → confirm red →
  restore → confirm green).
- Docs-only slices → `git diff --check`.

## Slices (one item per commit; commit before next)

### Slice 1 — Eval instrument (scaffold / score / record)
The measuring tool, no agent automation yet.
- `evals/fixtures/` — convert the pack's `funcpass_duration_parser` and
  `secpass_path_traversal` fixtures to **stdlib unittest**; each carries TASK.md,
  failing/vulnerable starting code, `test_*.py`, EXPECTED.md.
- `evals/governance_profiles/` — overlay dirs. `none` (empty), `current-template`
  (generated from product templates). Harness-neutral files at profile root; harness
  adapters under `hooks/claude/`, `hooks/codex/` subdirs (only a driver installs an
  adapter). A profile is overlaid onto a fixture workspace at trial start.
- `tools/run_fixture.py` exposing **`scaffold` / `prompt` / `score` / `record`**:
  copy fixture into a temp workspace, `git init`, overlay the chosen profile
  (**reject symlinks / absolute paths / path escapes**; record exact files overlaid;
  hash fixture+profile into the result), print the task; after the agent finishes,
  run fixture tests, derive objective pass/fail, and validate a recorded trial
  result against the schema. **Scorer tamper-protection**: fail the trial if the
  agent modified fixture tests, EXPECTED files, harness metadata, or the scorer
  unless the fixture explicitly allows it.
- `evals/trial_result.schema.json` with metadata sufficient to survive reruns:
  `date, harness, harness_version, cli_version, model, governance_mode,
  profile_hash, fixture, fixture_hash, driver_version, hooks_active, judge_id,
  judge_prompt_hash, duration_sec, timeout, functional_pass, security_pass,
  no_premature_stop, no_stall_loop, verification_honesty, changed_files,
  tests_changed, raw_result_path`.
- `evals/harness_scorecard.md` + `evals/README.md` (the manual protocol) +
  `evals/results/` (durable trial JSON store — repo is memory; scores are not
  chat-only). **All score fields positive-polarity so higher is always better.**
- Unit-test `run_fixture.py` scoring against a pre-baked *good* patch and *bad* patch
  so the scorer is proven before any trial is trusted.

### Slice 2 — Headless drivers (optional, gated)
Thin reproducibility layer that only calls Slice 1 primitives:
- `codex exec` with the prompt piped via **stdin** (no positional / use `-`),
  `-C <workspace>`, `--skip-git-repo-check` only when scaffolding outside a repo,
  capture `--json` so hook + final-message events are machine-readable; and the
  Claude Code `-p` headless equivalent.
- Each trial records a `hooks_active` preflight marker (hooks are **trust-gated** —
  `codex --dangerously-bypass-hook-trust` confirms this; never assume installing a
  config means the hook fired). Explicit bypass is acceptable in a controlled temp
  eval; product docs must not rely on it.
- Gated: if headless driving proves flaky, the Slice 1 manual protocol still yields
  the measurement. Decide go/no-go after one baseline is hand-run.

### Slice 3 — Baseline measurement (Phase 0 evidence)
Run `none` and `current-template` across both fixtures on Claude Code and Codex,
**≥3 runs per harness/profile/fixture** (tiny fixtures → variance dominates a single
run), same model/prompt/timeout/trust-state. Store trial JSON under `evals/results/`
and summarize into the scorecard. This is the evidence a later `decision` needs.

### Slice 4 — Candidate profile: prose only (eval-gated on Slice 3)
- Add a `candidate-loop-first` profile containing the authorized-execution +
  change-loop + completion-report snippet and the four `change_loop` repo-map fields
  — **in the profile, not in `templates/`.**
- Add a **third, multi-step fixture** that creates a "first visible green, still
  incomplete" situation (visible tests pass after a narrow fix, but hidden /
  security / integration expectations still fail unless the agent keeps verifying) —
  required to actually exercise premature-stop behavior.
- Measure the candidate vs baseline.

### Slice 5 — Candidate profile: + bounded Stop gate (eval-gated)
- Add the bounded, fail-open, session-keyed `stop_gate.py` + `stop_judge_prompt.md`
  to the candidate profile's `hooks/` subdirs, with state redirected via
  `AGB_STATE_DIR` to a temp/cache path (**never write under `.agents/`**).
- The semantic judge is **fixed eval-harness configuration, not part of the profile
  being compared**: pin judge model/version (or local command), prompt text/hash,
  temperature/seed, timeout; record raw judge output in trial metadata.
- Add transcript-level **Stop unit fixtures**: good final report, missing
  verification, no-code-change, blocked-by-roadblock, repeated-block-max — to prove
  the gate's bound and judge behave before trusting trial deltas.
- Confirm `{"decision":"block","reason":<non-empty>}` against each harness's Stop
  contract (verified correct for Codex 0.142.1; do not assume Claude Code's
  `permissionDecision`/exit-code semantics port to Codex). Measure premature-stop and
  stall deltas.

### Slice 6 — Promote proven pieces (gated update route + decision)
- Record a `decision` in `.agents/decisions.md` capturing the Slice 3–5 evidence and
  the eval-first adoption-gating.
- Promote **only** measured winners into `templates/` (AGENTS snippet via the gated
  update route with a `templateVersion` bump per criterion; repo-map fields into
  `templates/repo-map.template.json`; `stop_gate.py` into `templates/hooks/common/`
  only if Stop trials showed fewer premature stops with zero new stalls). For a
  product Stop gate, also resolve the hook-state path (gitignore rule or
  harness-local cache, not `.agents/`).

## Promotion gate (explicit)
Promote a candidate piece only if, across the trial set, it: improves or preserves
FuncPass/SecPass; reduces premature stops on the multi-step fixture; introduces zero
repeated no-delta Stop loops; and does not regress verification honesty. Anything
weaker is an anecdote, not an adoption gate.

## Decision linkage
No `decision` is recorded yet. Slices 1–3 (the instrument + baseline) are low-risk
and owner-go-able on their own. Slices 4–6 must be preceded by the Slice-6 `decision`
recording the evidence. The truth-lint folds into the open 2026-06-22
`governance-lint` item, not this plan.
