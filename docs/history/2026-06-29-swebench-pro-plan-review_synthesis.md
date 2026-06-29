# Plan-review synthesis — SWE-bench Pro governance integration (2026-06-29)

Distilled from two independent, blind reviews (`mem:` n/a):
[`..._codex.md`](2026-06-29-swebench-pro-plan-review_codex.md) and
[`..._claude.md`](2026-06-29-swebench-pro-plan-review_claude.md). These are **recommendations,
evidence for the owner** — not adopted decisions. The plan
(`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`) is not edited to
implement them without owner sign-off.

## Top-line (both reviewers agree)

The substrate/plumbing work is real and de-risks the *engineering*. The **science** is the
unfinished part: as specified, the most likely P3 outcome is a wide-CI null that cannot
distinguish "governance doesn't help" from "underpowered / wrong band / wrong metric /
context-length confound." Do not spend on the factorial until the must-fixes below are settled.

## Converged must-fixes (raised independently by BOTH reviewers)

1. **Pre-registered analysis plan + power/MDE.** Pin the unit of analysis (paired per-instance),
   one primary contrast, the statistical model (paired McNemar / mixed-effects on discordant
   pairs), a minimum detectable effect, and a stopping rule — *before* P3. No greenlight without
   an MDE number for the chosen n.
2. **Placebo (length-matched) prose arm.** none / prose / prose-hooks confounds "governance
   content" with "more tokens in context." Add a length-matched irrelevant-prose arm to separate
   them. (Repo history "security-prose ≈ placebo" makes this more important, not less.)
3. **Metric honesty under empty PASS_TO_PASS.** P2P is empty for ~64% of sampled instances, so
   `joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS` collapses to FAIL_TO_PASS there. Report FAIL_TO_PASS
   and PASS_TO_PASS separately; keep official `resolved` as primary; do not advertise a joint
   FuncPass∧SecPass claim the data can't support.
4. **Floor pilot as a NUMERIC gate before P3.** "Strengthen the driver if ~0 ungoverned solves"
   is prose; make it a threshold (e.g. require ≥K ungoverned `resolved` in the target band).
   Gold-resolvability 33/33 proves the *substrate*, NOT agent-solvability — don't conflate them.
5. **Subset-selection rigor.** Selecting on noisy n≈3-5 probes invites regression-to-mean; select
   on the official metric, predeclare the estimand ("difficulty-enriched subset of N on harness
   H"), and do NOT reuse screening runs as confirmatory evidence.
6. **One harness for the confirmatory factorial.** Capability-spectrum (weak agy/grok vs strong
   codex/claude) is the interesting *interaction* hypothesis but needs ~4× the sample; run it as a
   separate, separately-powered study, not a lever inside the underpowered main run.

## Additional points (one reviewer, worth adopting)

- **Run discipline:** randomize/interleave arm order across instances AND time (subscription model
  drift / rate-limits otherwise confound arm with time); record CLI + model version + timestamp
  per trial; isolate per-run home/config/cache (not credentials).
- **Accounting:** intention-to-treat primary, per-protocol secondary; infra-empty runs
  retried/excluded arm-blind (already noted). Log retry count per (instance, arm) and check it is
  not arm-correlated — heavier governed context → longer runs → more no-output flakes would
  *look* like governance hurting.
- **Per-arm capture validation:** prove patch-capture on a *governed-arm* capture specifically
  (sentinel/overlay exclusion), not just the gold/none case.
- **Multiple comparisons / optional stopping:** "expand arms only if signal appears" is a
  garden-of-forking-paths hazard; predeclare the arm set for the confirmatory comparison.
- **Dependency flakiness:** network-on during the agent run adds arm-correlated noise; pin/cache
  deps if possible.
- **Honest scope limit:** the supportable claim is narrow (subset + single harness + FAIL_TO_PASS
  primary), not a broad "frontier agents" causal claim.

## Open decisions for the owner (these gate the next plan revision)

- Primary contrast: none vs prose-hooks, or none vs prose?
- Which single harness for the confirmatory run (strongest realistic, or a mid-capability one with
  more headroom)?
- Accept the placebo arm's added cost? (Reviewers: yes.)
- Sample size vs repeated-trials trade-off given irreducible per-instance agent (Bernoulli) noise.

## Critical-path note

The **floor pilot** (measure ungoverned `resolved` rate across a sample) is simultaneously the #1
de-risking step both reviewers want AND only needs the **launch-gate sanction** already pending
with the owner (see `.agents/state.md` Blockers). Settling that one decision unblocks the single
highest-value next experiment, whose result then informs band selection and the power calculation.
