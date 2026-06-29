# SWE-bench Pro × governance integration

Status: DRAFT 2026-06-29, pre-codex-review. Supersedes the synthetic-fixture and
bug-crafting approaches for fixture-sourcing (see
`2026-06-29-adversarial-bugcrafting-loop.md` addendum). No code yet.

## Empirical update — 2026-06-29 (validated facts; supersedes stale substrate/P0 text below)

Substrate work ran on the amd64 Linux box `netwatch-01` (NOT the Mac/Colima setup in
"Execution substrate" below — that section is stale; Apple-Silicon amd64-emulation risk is
MOOT here, images run native). Live authority: `.agents/state.md`.

- **P0 DONE + generalized.** Gold round-trip passes; empty-patch negative control fails
  (metric discriminates). Generalizes 11/11 repos. Gold-resolvability sweep 33/33 ≈ 100%
  (one transient flake, resolved on retry) — gold patches are clean here, so ~all instances
  are usable. ("No code yet" / P0-pending text below is superseded.)
- **Disk sizing (real):** on-disk image footprint 1.6–12 GB each, avg ~4.4 GB (NOT multi-TB
  per image). A 20–40 instance subset ≈ 90–180 GB; 320+ GB free. Subset still wise, numbers
  far smaller than the plan assumed.
- **Integration-contract gotchas the adapter MUST encode:** the shipped scorer targets the
  leaderboard CSV; our jsonl trips two real mismatches — (1) it reads lowercase
  `fail_to_pass`/`pass_to_pass` (jsonl has uppercase); (2) it `eval()`s those expecting a
  *string*, but jsonl `FAIL_TO_PASS` is a list and `PASS_TO_PASS` a string — coerce both to
  string. Predictions accept `model_patch` OR `patch`; always pass `--redo` (per-instance
  output cache silently reuses stale runs).
- **Patch-capture VALIDATED (and bigger than the plan said):** capture = source-only
  `git diff --staged` vs base, EXCLUDING (a) governance overlay/sentinels AND (b) **test
  files** — the scorer overlays gold test files itself (only the LAST line of
  `before_repo_set_cmd`), applied AFTER the agent patch, so agent test edits must be stripped
  (prevents test-gaming). Round-trip proven: gold applied into `/app`, captured, scored resolved.
- **Metric caveat (affects the primary metric):** `PASS_TO_PASS` is EMPTY for 7 of 11 sampled
  instances → `joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS` collapses to FAIL_TO_PASS for those.
  The FuncPass∧SecPass framing must handle frequently-empty SecPass.
- **Transient infra-failure mode (must handle):** at `--num_workers=4`, heavy 5–12 GB
  containers occasionally produce NO output (absent `gold_output.json`) → scored false.
  DISTINGUISHABLE (absent output vs tests-ran-and-failed) and RETRYABLE; retry it, never count
  it as an agent failure.
- **Agent-run mechanism (proven):** host `claude` native binary + subscription credential
  mounted into the instance container, run headless as the non-root `node` user (root refused),
  no API key. Subject = harness+model via SUBSCRIPTION, not API keys.
- **NEW GATE (open):** launching the unsupervised bypass-permissions agent — the eval's core —
  is blocked by the running session's safety classifier; needs an owner-sanctioned launch path
  (settings permission rule / owner-run driver / non-auto-mode).
- **NEW design lever (owner):** harnesses span capability — agy/grok (weaker) vs codex/claude
  (stronger). Weaker agents plausibly have more headroom for governance to help; consider
  spanning capability deliberately rather than a single primary frontier (revisits G1).

## Goal

Measure whether our governance product (prose / hooks / both) makes a frontier agent
reliably better at **real, hard, frontier-resistant** software tasks — using ScaleAI
SWE-bench Pro (`/Users/michael/Dev/SWE-bench_Pro-os`, 1000 instances, 11 repos) as the
fixture source instead of synthetic bugs that frontier models trivially solved.

Primary metric unchanged: **joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS** (their scorer's
two dimensions ARE our FuncPass ∧ SecPass). A governance arm "wins" by raising the
fraction of instances resolved (both the target test passes AND no regression).

## The integration contract (verified by reading swe_bench_pro_eval.py)

Their eval is a pure function over a **predictions file**:
`swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
--output_dir <out> [--use_local_docker]`. The predictions JSON is
`[{instance_id, model_patch}]` (they ship `gold_patches.json` as the reference shape).
For each instance it: builds/pulls the instance Docker image, resets to `base_commit`,
applies `model_patch`, runs the test command, scores FAIL_TO_PASS + PASS_TO_PASS.

**Decoupling:** the agent that produces the patch is entirely separate from the scorer.
Governance lives 100% in patch *production*; the scorer never sees our harness.

## Pipeline (file boundary between our side and theirs)

```
PER (instance, arm):
  1. scaffold instance repo at base_commit            (our harness: scaffold)
  2. overlay governance profile (none/prose/hook-*)   (our harness: overlay_profile)
  3. run our driver (claude/codex) on the problem     (our harness: drivers + hooks)
  4. capture the agent's diff vs base_commit          -> patch text
COLLATE per arm:
  5. write predictions_<arm>.json = [{instance_id, model_patch}]
SCORE (their harness):
  6. swe_bench_pro_eval.py --patch_path predictions_<arm>.json ... --use_local_docker
ANALYZE (our side):
  7. join their resolved results back per arm; joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS;
     reuse invalid-trial accounting (protected-file edits, inert hooks) + telemetry.
```

The patch-capture in step 4 is `git diff` against `base_commit` in the agent's
workspace, EXCLUDING the overlaid governance files and any hook sentinel (those are
environment, not the agent's fix — same exclusion logic as our changed_files work).

## What we keep / build / retire

- **Keep:** governance profiles (none, current-template, hook-gate, hook-guard,
  prose-hooks); joint_pass; invalid-trial accounting; transcript/telemetry capture;
  the claude/codex drivers.
- **Build:** an instance adapter (SWE-bench-Pro instance metadata -> our scaffold +
  a problem prompt for the driver), the patch-capture + predictions-writer, and a thin
  wrapper that shells their `swe_bench_pro_eval.py` and ingests its output.
- **Retire:** synthetic fixtures, `--check-discrimination`, the calibration band,
  the bug-crafting loop. (Left in the repo/history; not used.)

## Execution substrate (Docker confirmed installing)

- Hardware: M4 Max, 16 cores, 48GB, 566GB free — ample for a SUBSET. Colima with
  `--cpu 8 --memory 24 --disk 200`.
- **Not all 1000** — image storage alone is multi-TB. Subset of ~20–40 instances.
- **Arch check (open risk):** some base images may be `linux/amd64` (the ansible base
  is dated 2022). Those run under emulation on Apple Silicon — slow, occasionally
  flaky. Step 0 of execution: probe candidate instances' image arch and prefer
  arm64-clean repos for the subset; pass `--platform` explicitly where needed.

## Subset selection (replaces the calibration gate, on real tasks)

The calibration question is unchanged but now answered on real tasks: pick instances
where the target model's **ungoverned FAIL_TO_PASS rate is mid-range** — solvable
enough that the agent engages, hard enough that it often fails — so governance has room.
- Probe: run the target model under `none` on a candidate pool (n≈3–5 each), keep
  instances whose ungoverned resolve rate is, say, 20–70%.
- Diversity: 3–4 repos, mixed languages, spanning the difficulty band. ~20 survivors.
- This is real spend but bounded (pool × small n under one arm).

## Open decisions

- **G1. Target model(s).** Lean: one primary (cheap-ish frontier — a Claude model or
  GPT-5 codex) for subset selection + the factorial; optionally replicate the headline
  delta on a second. (Owner already chose "both Claude + GPT-5 as arms" for the prior
  plan — carry forward unless cost says otherwise.)
- **G2. Agent scaffold.** Lean: OUR claude/codex drivers + governance overlay (keeps
  the hooks/arms we built; closest to the Cursor↔Claude-Code question). NOT their
  SWE-Agent (our Claude-Code hooks don't ride in it). Risk: our simple one-shot driver
  may resolve far fewer instances than a real agent loop — may need a minimal
  agentic loop (read/edit/run-tests) for the agent to stand a chance on long-horizon
  tasks. This is the biggest unknown; see G3.
- **G3. Driver capability.** SWE-bench Pro is LONG-HORIZON; a single `claude -p` call
  likely resolves very little. Options: (a) rely on Claude Code's own agentic loop
  (it already reads/edits/runs commands within one `-p` invocation) — probably
  sufficient and is the realistic "Claude Code" product; (b) build a minimal
  multi-turn loop. Lean (a) — it is the actual product being measured.
- **G4. n and arms for the real run.** With ~20 instances × 5 arms × n, cost is real.
  Lean: start none vs prose vs prose-hooks (3 arms) on the subset at n=3, expand to the
  full 5 arms only if a signal appears.
- **G5. Network during agent run.** Their scorer can `--block_network`; the agent run
  (dependency install, etc.) may need network. Decide per phase (agent: network on;
  scoring: their default).

## Risks

1. **Floor risk (mirror of the ceiling problem):** SWE-bench Pro is HARD; a one-shot
   Claude-Code driver may resolve ~0 under `none`, leaving no room to show improvement
   in the other direction. The subset-selection band (G,  mid-range ungoverned rate)
   guards against this — but if even mid-range instances resolve at ~0, the driver
   (G3) is too weak and must be strengthened before the factorial.
2. **Image arch / build cost:** amd64 emulation could make runs slow/flaky; mitigated
   by arm64-preferred subset.
3. **Patch-capture fidelity:** the diff must exclude governance overlay + sentinels or
   the patch won't apply cleanly in their clean-base container (it would carry AGENTS.md
   etc.). Reuse the changed_files exclusion logic; test that a captured patch applies in
   a fresh checkout.
4. **Their harness assumptions:** confirm predictions JSON schema + sample schema by
   round-tripping `gold_patches.json` through the scorer first (a gold patch must score
   resolved) BEFORE trusting our patches — a cheap correctness anchor.

## Phased plan (each gated, codex-reviewed)

- **P0 — substrate up + gold round-trip.** Colima running; pull/build ONE instance
  image; run their scorer on that instance's gold patch and confirm it scores resolved.
  Proves the scorer works locally before we produce any patch. (No governance yet.)
- **P1 — instance adapter + patch capture.** Map a SWE-bench Pro instance to our
  scaffold + problem prompt; run our driver under `none`; capture a clean patch; write
  predictions JSON; score it. Confirm end-to-end on 1–2 instances.
- **P2 — subset selection.** Ungoverned probe over a candidate pool; freeze ~20 mid-band
  instances across diverse repos (arch-checked).
- **P3 — factorial.** none / prose / prose-hooks (G4) over the frozen subset; joint_pass;
  invalid accounting; report deltas with CIs. Expand arms/n if signal.

## Verification

- P0 gold round-trip is the substrate correctness anchor.
- P1 patch-applies-in-fresh-checkout test (hermetic-ish: a captured patch must apply on
  a clean base commit).
- Adapter/capture/predictions-writer unit-tested with a fake driver (no model, no
  Docker) for the file-shape contract; the Docker scoring is the live/integration part.
- joint_pass + invalid accounting already tested (Slice C).
