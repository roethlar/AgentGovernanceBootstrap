# Adversarial bug-crafting loop (difficulty as the search target)

Status: DRAFT for external perspectives, 2026-06-29. Not approved, no code.
Supersedes the fixed-fixture approach of `2026-06-28-discriminating-fixtures-and-arms.md`
for the *fixture-sourcing* problem (the harness, arms, metric, and discrimination
gate built in that plan are kept — see "What we keep").

## Why this plan exists

The 2026-06-28 frozen-fixture run died at the calibration gate: both frontier models
(Claude, GPT-5) **clean-passed all 5 synthetic fixtures ~100% of the time** under
`none` — zero naive traps, every fixture dropped as ceiling. Root cause: a model asked
to *design* a trap designs one calibrated to a weaker agent than itself, so the bugs it
invents are bugs it doesn't fall for. Guessing a hard-enough bug and hoping it lands
in-band does not work against frontier models.

**The flip (owner's proposal):** stop guessing. Make *difficulty itself* the search
target. An adversarial loop crafts and sharpens a bug until a chosen model, **ungoverned
in a fresh context, reliably cannot fix it**; freeze that bug; then run the **same model
with governance** and measure whether governance recovers it. The fixture set becomes
whatever survives the search, not a fixed bet.

## The core loop

```
craft -> validate -> probe(ungoverned) -> decide
  craft:     crafter (this agent + codex, iterating) proposes/sharpens a fixture
             (buggy source, visible test, hidden test, naive+solution patches)
  validate:  --check-discrimination must pass (buggy F/T, naive T/F, solution T/T)
             — a malformed or non-discriminating bug is rejected before any spend
  probe:     run TARGET model, no governance, fresh context, N times -> ungoverned
             joint-pass rate
  decide:    if ungoverned pass rate is still HIGH  -> too easy -> sharpen, loop
             if ungoverned pass rate is LOW enough  -> FREEZE this bug as a fixture
             if the loop stalls (K rounds, no drop) -> stop, surface (don't burn budget)
```

Then, on each frozen bug, the measurement run:

```
run TARGET model WITH each governance arm (prose / hook-gate / hook-guard / both)
compare governed joint-pass vs the frozen ungoverned baseline
```

The keep-rule inverts from the old plan: instead of "naive-trap rate in [20%,80%]",
the gate is "ungoverned joint-pass rate <= T" (the bug stumps the model often enough to
leave recovery room). T is an open parameter (see Decisions).

## What we keep (already built, 2026-06-28..29, all pushed)

- The harness: scaffold, governance overlay, FuncPass/SecPass scoring, transcript +
  telemetry capture, changed_files attribution, hook firing logs.
- `--check-discrimination`: the mechanical truth-table gate every crafted bug must pass.
- `joint_pass = FuncPass AND SecPass` primary metric + invalid-trial accounting
  (protected-file edits, inert hooks).
- The three governance arms (hook-gate, hook-guard, prose-hooks) and the factorial.
- `calibrate.py` (repurposed: its classify/Wilson logic still scores the ungoverned
  probe; only the keep-rule threshold changes).

What is NEW in this plan: the **crafter loop** itself (orchestration, the sharpen step,
the stall detector) and the **difficulty-type steering** (below).

## The central validity risk: which "hard"?

"The model can't fix it ungoverned" has two very different causes, and only one is worth
measuring:

- **Capability-hard** — the bug needs knowledge/reasoning the model lacks (a deep
  algorithm, an obscure spec). Governance cannot conjure capability, so these yield a
  guaranteed null and waste the experiment. They are also the *easier* kind for a
  crafter to produce, so a naive "just make it fail" loop drifts here.
- **Discipline-hard** — the model *can* fix it (a small correct fix is within reach) but
  reliably *doesn't*: it writes the naive fix, stops before verifying, weakens the test,
  or doesn't read the adjacent code. This is exactly what governance ("verify", "don't
  weaken checks", the gate/guard hooks) is meant to recover. **This is the regime where
  the experiment can show a real effect or a real null.**

The loop's steering toward discipline-hard is the make-or-break design choice (Decision A).

## Open decisions (for external perspectives)

### Decision A — what difficulty should the crafter optimize for?
- **A1 (lean): discipline-hard only.** Steer the sharpen step toward "small correct fix
  within reach, but the tempting path fails the hidden test," pushing the trap until the
  model reliably takes the bait ungoverned. Validity: high (effect attributable to
  governance). Risk: harder to craft; the loop may stall more often.
- **A2: any high-failure bug.** Simpler loop, search purely on ungoverned failure rate.
  Risk: drifts to capability-hard, biases toward a null, weakest result.
- **A3: produce both, labelled.** Crafter tags each frozen bug discipline-hard vs
  capability-hard; run governance on both. Most informative (shows governance recovering
  discipline-hard and, expectedly, not capability-hard — itself a clean story). Cost: ~2x
  fixtures and runs.

### Decision B — target model the difficulty is calibrated against
- **B1: a Claude model** (e.g. claude-haiku-4-5 or sonnet via the claude driver) —
  matches the Claude Code side; haiku is cheap enough for a long search loop.
- **B2: a GPT-5 codex model** (e.g. gpt-5.x-codex via the codex driver) — matches the
  "stump GPT-5" framing and the Cursor side.
- **B3: a mid-tier/local coder** (qwen/gemma/north-mini via ollama) — cheapest search,
  biggest gap, but weakest external-validity claim ("helps models that aren't already
  near-perfect"). 
- **B4: one primary + confirm on a second.** Calibrate difficulty on one model, then
  replicate the governed-vs-ungoverned delta on a second so the result isn't
  one-model-specific. Strongest, most expensive.
- Note: difficulty is model-specific. A bug frozen as "stumps haiku" may be trivial for
  GPT-5 — so the frozen set is per-target-model unless B4 forces overlap.

### Decision C — the freeze threshold T (ungoverned joint-pass rate)
- **C1: T <= 20%** (model fails >= 80% ungoverned) — strong "stumped" signal, lots of
  recovery room, but a slower/longer search to reach.
- **C2: T <= 40%** — easier to reach, still clear room; the governed arm has to beat a
  low-but-nonzero baseline.
- **C3: a band, e.g. 10–40%** — avoid T=0 (a bug the model *never* solves ungoverned may
  be capability-hard / unrecoverable). Lean: a band that excludes near-0.
- n per probe and the Wilson-CI requirement on T also need setting (lean n=10, require
  the CI upper bound below the band ceiling so a noisy probe doesn't freeze a fluke).

### Decision D — crafter mechanics (how the sharpen step works)
- **D1: model-proposes, harness-validates.** Crafter model emits a full fixture; the
  harness runs --check-discrimination + the ungoverned probe; on "too easy" the crafter
  is shown the model's *successful ungoverned transcript* and asked to sharpen the trap
  to defeat that specific path. (Lean — uses the model's own solution as the thing to
  beat.)
- **D2: template mutation.** Start from a human seed bug and the loop only mutates
  parameters (boundary values, added edge cases) — narrower, more controllable, less
  creative.
- **D3: codex-vs-claude adversarial pair.** One model crafts, the other attacks; iterate.
  Richest, most expensive, most likely to find genuine discipline-hard traps.

### Decision E — stall / budget discipline
- The loop must bank a verifiable delta each round (ungoverned pass rate dropping) or
  stop after K stalled rounds (lean K=2–3) — the repo's stall-not-length invariant.
- A per-bug spend cap and a total-search cap (open: dollar or trial-count budget).

## Risks / unknowns to get perspectives on

1. **Does discipline-hard even exist at frontier scale for bug-fixing?** Maybe a model
   that can write the correct fix simply *does*, and there is no reliable "it knows but
   doesn't" regime for small bug-fixes. If so, the honest finding is "governance doesn't
   move frontier bug-fixing" and the eval should pivot task type (long multi-step tasks,
   convention-following, not-breaking-adjacent-code over a session) — flag for D.
2. **Overfitting the fixture to one model's quirks.** A bug sharpened until *this* model
   fails may be a brittle artifact, not a general trap. Mitigate with B4 / cross-model
   replication.
3. **Crafter leakage.** The crafter must never see the governance arms while crafting, or
   it could craft bugs that trivially benefit the specific hook — craft against the
   ungoverned baseline only.
4. **Cost.** A search loop is open-ended spend by nature; the caps in Decision E are
   load-bearing, not optional.

## Proposed default (if no other steer comes back)

A1 (discipline-hard) + B1 primary on a cheap Claude model with B4 cross-check on GPT-5
for any frozen bug + C3 band (10–40%, Wilson-gated) + D1 sharpen-against-transcript +
E with K=3 and an explicit trial-count cap. Rationale: maximizes the chance of a *valid*
effect (or a credible null), keeps search cost bounded, and the cross-check guards
against per-model overfitting.

## ADDENDUM 2026-06-29 — SWE-bench Pro changes the recommendation

Owner located a full local checkout of **ScaleAI SWE-bench Pro**
(`/Users/michael/Dev/SWE-bench_Pro-os`, the official `scaleapi/SWE-bench_Pro-os`
repo). This likely **supersedes both** the synthetic-fixture plan AND this
bug-crafting loop, because it already provides — curated from real commits, not
model-invented — exactly what those were trying to manufacture.

### What it is (verified by inspection)
- **1000 real instances** across 11 substantial repos (ansible, qutebrowser, NodeBB,
  navidrome, gravitational/teleport, protonmail, element-hq, …). Long-horizon tasks
  explicitly built to resist frontier saturation (the public leaderboard shows top
  agents well under 100%).
- Each instance ships: `Base Commit`, `Test Files`, **`FAIL_TO_PASS`** (the target
  test the fix must make pass) and **`PASS_TO_PASS`** (tests that must STAY green).
- Patch-based scoring: `swe_bench_pro_eval.py` applies a candidate **patch** in the
  instance's Docker image, runs the tests, scores FAIL_TO_PASS + PASS_TO_PASS. It is
  agnostic to how the patch was produced — the agent and the scorer are decoupled.
- Agent scaffolds are git submodules (`SWE-agent`, `mini-swe-agent`, ScaleAI forks),
  currently un-checked-out. Per-instance Docker images (base + instance Dockerfile).

### Why this maps onto our experiment perfectly
- **FAIL_TO_PASS = FuncPass** (our visible/functional dimension).
- **PASS_TO_PASS = SecPass / regression guard** — a real, curated "don't break the
  adjacent behaviour" trap. This is the exact discriminator the synthetic plan hand-
  built as a `hidden` test, but real and already calibrated.
- Real difficulty means a **real ungoverned failure rate** — the thing the calibration
  gate found missing in the synthetic set. No crafting loop needed: difficulty is
  intrinsic, not searched.

### What we keep vs retire
- **Keep:** the governance arms (none / current-template / hook-gate / hook-guard /
  prose-hooks), `joint_pass = FuncPass AND SecPass` (here: FAIL_TO_PASS AND
  PASS_TO_PASS), invalid-trial accounting, transcript/telemetry capture.
- **Retire (likely):** synthetic fixtures, `--check-discrimination`, the calibration
  band gate, and this bug-crafting loop — SWE-bench Pro removes the need to source or
  calibrate difficulty ourselves.

### The integration becomes the work — open questions
- **F1. Execution substrate.** The official scorer runs patches in per-instance Docker
  containers. **Docker is not currently running on this machine.** Options: (a) install
  + run Docker locally and build/pull instance images (heavy: 1000 images, disk + time);
  (b) use **Modal** (their cloud path, `modal>=0.50` — paid cloud, no local Docker);
  (c) subset to a handful of instances/repos and only stand up those images.
- **F2. Which agent generates the patch.** (a) Our existing Claude/codex drivers +
  our governance overlay, producing a diff we hand to their scorer — keeps our hooks
  and arms intact, closest to the Cursor↔Claude-Code question. (b) Their SWE-Agent
  scaffold with governance injected — more faithful to the benchmark's own numbers but
  our Claude-Code hooks don't ride in SWE-Agent. Lean (a): the experiment is about our
  governance on a Claude-Code-style agent, and (a) preserves the arms we built.
- **F3. Where the hooks ride.** With (a), the agent runs in a workspace we control, so
  the overlay + gate/guard hooks work as built; the produced patch is then scored in
  the container. Need to confirm the agent's workspace == the repo state the scorer
  expects (same base commit, clean tree minus the agent's diff).
- **F4. Subset + cost.** 1000 instances × 5 arms × n is far too much for a first pass.
  Lean: pick a small, diverse subset (e.g. 15–30 instances across 3–4 repos and
  languages) where a target model's ungoverned FAIL_TO_PASS rate is mid-range, run the
  factorial there, expand only if a signal appears.

### Revised recommendation
Pivot to SWE-bench Pro as the fixture source. New (small) plan: stand up the execution
substrate for a chosen subset (F1), wrap our governed driver to emit a patch (F2/F3),
score with their harness, and run the existing 5-arm factorial with joint_pass =
FAIL_TO_PASS ∧ PASS_TO_PASS. This is a fresh plan to draft and codex-review; the
bug-crafting loop above is retained in the repo as the fallback if the SWE-bench Pro
integration proves infeasible (e.g. Docker/Modal cost is prohibitive).

## Verification plan (when/if approved)

- Crafter loop unit-tested on the mechanics (sharpen step wiring, stall detector,
  threshold gate) with a *fake* model so it's hermetic; the model calls themselves are
  the live spend.
- Every frozen bug must pass --check-discrimination (mechanical) before it counts.
- The governed-vs-ungoverned measurement reuses the existing joint_pass + invalid-trial
  machinery; no new metric.
