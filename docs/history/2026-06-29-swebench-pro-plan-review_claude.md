# Claude review — SWE-bench Pro governance integration plan (2026-06-29)

Independent review by `claude -p --allowedTools "Read Grep Glob"` (read-only, kept blind to
the codex review) of the same plan + `.agents/state.md`. Evidence to assess, not decisions.

---

# Skeptical Review: SWE-bench Pro × Governance Integration

Bottom line up front: the substrate engineering is genuinely solid and the empirical update has retired the most dangerous *unknowns* (round-trip works, metric discriminates, gold patches clean). But the experiment as designed is at serious risk of producing an **uninterpretable null** — not because governance doesn't help, but because the design hasn't yet committed to the things that determine whether any effect is *detectable* or *attributable*. The highest-impact gaps are statistical power and the floor risk, and they interact multiplicatively. I'll prioritize accordingly.

---

## P1 — Statistical power is the experiment-killer, and the plan never computes it (re: G4, Risks §4-missing)

This is the single most important thing and the plan is silent on it. Let's do the arithmetic the plan should contain.

- Binary outcome, ~20 instances, comparing two arms (none vs prose). Suppose ungoverned resolve = 30%, and governance lifts it to 50% — a **large** 20-point absolute effect. A two-proportion test at n=20/arm has power ≈ **0.18**. You would miss a real, large effect ~80% of the time.
- To detect a 30%→50% lift at 80% power you need **~93 instances per arm**. At n=20 you can only reliably detect a lift of roughly 30%→75%+.
- G4's "n=3" makes this dramatically worse if n=3 means **3 trials per instance** rather than 20 distinct instances. Three Bernoulli trials per instance with a stochastic agent gives near-zero per-instance resolution power, and the clustering (trials nested in instances) destroys the naive "20×3=60 independent observations" intuition. **The plan must state explicitly whether the unit of analysis is the instance or the trial, and the analysis must be a paired/mixed model** (instance as random effect, arm as fixed effect), not a pooled two-proportion test.

What to do, in order:
1. **Run a power calculation before P3 and put it in the plan.** Pick the minimum detectable effect (MDE) you'd accept and back out n. If the honest answer is "we can only detect a 40-point swing," say so up front — that reframes the whole experiment.
2. **Exploit pairing.** Because every instance is run under every arm, use a **within-instance paired design** (McNemar / mixed-effects logistic with instance random intercept). This is far more powerful than between-subjects and is the only thing that makes n≈20–40 remotely viable. The plan's analysis step (line 84) says "join resolved results per arm" — that's a between-arm comparison and leaves the pairing on the table. Fix the analysis spec.
3. **Reframe the deliverable honestly.** At this n, this is a **pilot / effect-size estimation study**, not a confirmatory test. Report effect sizes with wide CIs and treat a "win" as "CI excludes zero AND point estimate is decision-relevant," not p<0.05. The word "wins" (line 56) and "report deltas with CIs" (line 175) should be hardened: with n=20 the CI on a single-arm proportion is ±~21 points — a delta CI will routinely span zero even for real effects.

---

## P1 — Floor risk and ceiling risk both alias to "no effect"; the subset band is necessary but not sufficient (re: Risks §1, Subset selection, G3)

The plan correctly identifies the floor (line 149) and the subset band (20–70% ungoverned, line 119) as the mitigation. Three problems remain:

1. **The band is estimated from n≈3–5 probes per instance** (line 120). A 3-trial estimate of an instance's resolve rate has a 95% CI of roughly ±35 points — you cannot distinguish a 20% instance from a 60% instance at n=3. **You will mis-bin instances**, and the very instances you select as "mid-band" are disproportionately those that *fluctuated* into the band by chance (regression to the mean). After selection, their true rates will drift toward the pool mean, deflating any apparent governance headroom. This is a selection-on-noise artifact and it biases *against* finding an effect in the frozen subset.
   - Mitigation: select on a larger probe (n≥10) or select on a *predictor* of difficulty (repo, patch size, #files in gold) rather than on the noisy outcome itself, then verify the band post hoc.

2. **The band guards the floor but introduces a confound** (see P2-conf below): selecting instances *by their ungoverned resolve rate* and then measuring whether governance raises the resolve rate is partially circular — you've conditioned the sample on the dependent variable. Mid-band selection is defensible for power, but the headline number is then "effect *within an enriched band*," not "effect on SWE-bench Pro." State that scope limit.

3. **The deeper floor question the plan defers (G3):** a one-shot `claude -p` may resolve ~0 even mid-band, and the plan's lean (rely on Claude Code's internal agentic loop, option (a), line 137) is asserted, not measured. **This must be answered in P2 before P3 is greenlit** — and P2 as written only produces the band, not a go/no-go on driver adequacy. Add an explicit gate: "if ungoverned mid-band resolve < ~15%, stop and strengthen the driver." Right now that decision is implicit in prose; make it a numbered gate with a threshold.

---

## P2 — The empty-PASS_TO_PASS problem changes what the primary metric *measures*, not just how it's computed (re: Empirical update lines 31-33, Goal line 55)

This is well-flagged operationally but under-analyzed scientifically. PASS_TO_PASS empty for ~64% of instances means:

- For those instances, `joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS` collapses to `FAIL_TO_PASS` — i.e. **the regression-guard dimension silently vanishes for the majority**. The "SecPass" half of your headline metric is only exercised on ~36% of the sample. If governance's *real* benefit is "doesn't break existing tests" (a very plausible mechanism for governance prose about discipline/verification!), you've removed the dimension where it would show up — on most instances.
- Worse: the metric is now **inconsistent across instances** (two-dimensional on some, one-dimensional on others). Pooling them treats a hard joint pass and a single-test pass as the same unit. That's a metric-validity problem, not a coding gotcha.

What to do:
1. **Report FAIL_TO_PASS and PASS_TO_PASS as separate pre-registered outcomes**, not only their conjunction. The conjunction can be secondary. This also recovers power (FAIL_TO_PASS is defined on 100% of instances).
2. **Pre-specify the empty-P2P semantic.** Is empty-P2P "vacuously true" (current behavior) or "not evaluable"? The plan should state this as a decision, because it changes the denominator.
3. **Consider stratifying** the subset to ensure enough P2P-nonempty instances to say anything about the regression dimension at all — otherwise drop the SecPass claim from the goal honestly.

---

## P2 — Governance-injection confounds: you are changing more than the treatment (re: Pipeline step 2, line 90; Risks §3)

Injecting AGENTS.md/hooks into arbitrary OSS repos introduces confounds the plan only treats as *patch-capture hygiene*, not as *validity threats*:

1. **Context-window / token displacement.** The governed arms put a large governance prose blob (and hook output) into the agent's context. On long-horizon tasks that's not neutral — it consumes context budget and could *hurt* via crowding, or *help* via priming, independent of governance *content*. **You need a placebo/control-prose arm** (equal-length irrelevant or generic prose) to separate "governance content" from "more tokens in context." The plan has none vs prose vs prose-hooks (line 172); there's no length-matched placebo. Without it, a prose effect is confounded with a prose-*length* effect. (The state.md notes a prior finding "security prose ≈ placebo" — that history makes a placebo arm *more* important here, not less.)
2. **Hook behavior in foreign repos.** The hooks were authored for *this* toolkit's workflow. In an arbitrary OSS repo at an arbitrary base_commit, do the re-ground/tripwire hooks fire meaningfully, or fire spuriously, or no-op? An inert hook in the hook arm makes prose-hooks ≡ prose and dilutes the contrast. The "inert hooks" invalid-trial accounting (line 85) catches the egregious case but not "hook fired but was irrelevant to this repo."
3. **Repo-governance collision.** Some of the 11 repos may already contain CONTRIBUTING.md / linters / their own agent guidance. Overlaying AGENTS.md on top creates conflicting instructions — a confound that varies by repo and could swamp the arm effect. The plan should inventory and either neutralize or record per-repo pre-existing governance.
4. **Per-arm patch-capture asymmetry.** The exclusion logic (lines 88-90) must be proven *per arm* — the none arm has nothing to exclude, the hook arm has sentinels. An asymmetric capture bug would manifest exactly as an arm effect. The P1 "patch applies in fresh checkout" test (line 181) should run **on a governed-arm capture specifically**, not just a gold/none capture.

---

## P2 — The capability-spectrum idea is a good hypothesis but a power trap as currently floated (re: Empirical update line 44, G1)

Spanning weak (agy/grok) vs strong (codex/claude) harnesses is scientifically the *right* instinct — the genuinely interesting hypothesis is the **interaction**: "governance helps weak harnesses more than strong ones." But:

- An interaction test needs **~4× the sample** of a main-effect test to reach the same power. If 20 instances can barely see a main effect, an arm×capability interaction at this n is hopeless. Floating it as a casual "design lever" risks spreading a fixed budget across a 2(capability)×3(arm) grid and detecting nothing in any cell.
- It also multiplies confounds: weak harnesses fail for *different reasons* (can't navigate the repo, loop forever) than strong ones, and governance prose might be unreadable/ignored by a weak model — so a null in the weak arm could be "governance didn't transfer" rather than "no headroom."

Recommendation: **pick ONE harness for the confirmatory factorial** (the strongest realistic product — the thing you'd actually ship), get a clean main-effect estimate, and treat capability-spanning as an explicit, separately-powered follow-up — not a lever pulled inside the same underpowered run. If you must span, span on a *large* instance set for the weak harness only (where the floor risk is lowest and headroom largest), as a targeted second study.

---

## P3 — Agent nondeterminism and the "what is one observation" question (re: G3, G4, Agent-run mechanism line 38)

The subject is a stochastic agent on a subscription. Two issues:

1. **No seed / temperature control is mentioned.** Run-to-run variance is a major noise source. You can't fix a subscription model's sampling, which means the *only* way to characterize per-instance resolve probability is repeated trials — which collides head-on with the n-budget. The plan must acknowledge that the irreducible per-instance Bernoulli noise sets a power floor independent of instance count.
2. **Subscription rate-limits / drift over a multi-day run.** A factorial run spanning days on a subscription risks the model version or rate-limiting changing mid-experiment, confounding arm with time-of-run. **Randomize/interleave arm order across instances and time** (don't run all-none-then-all-prose), and record model version/timestamp per trial. The pipeline (lines 73-86) runs arms in a fixed inner structure; specify interleaving.

---

## P3 — Smaller but real

- **Multiple comparisons:** 5 arms (line 94) → 10 pairwise contrasts. With the expand-if-signal rule (G4, line 141) you're also doing **optional stopping / data-peeking**, which inflates false positives. Pre-register the primary contrast (none vs prose-hooks, say) and treat the rest as exploratory, or correct for it.
- **"Expand arms only if signal appears" (line 142)** is a garden-of-forking-paths hazard dressed as thrift. Decide the arm set up front for the confirmatory comparison.
- **Gold-resolvability ≠ agent-solvability.** 33/33 gold resolving (line 14) proves the *substrate* is clean; it says nothing about whether the *agent* can solve them. Don't let the strong 33/33 number create false confidence about the floor — they measure different things.
- **The transient-infra-failure handling is correct and important** (lines 35-37, 71-78) — retry-on-absent-output, never count as agent failure. One addition: **log the retry count per (instance, arm)** and check it's not correlated with arm, or a heavier governed context (more tokens → longer runs → more likely to hit the OOM/no-output mode at given parallelism) becomes a silent confound that *looks* like governance hurting.
- **Network-on during agent run (G5, line 145)** is a reproducibility and confound risk: dependency-install flakiness varies by repo and time, adding noise that varies across arms if governed runs take longer. Pin/cache dependencies if at all possible.

---

## What's missing entirely

1. **A pre-registration / analysis plan.** Primary outcome, unit of analysis, statistical model, MDE, stopping rule — none are pinned. At this n, pre-registration is the difference between "estimated effect" and "p-hacked artifact."
2. **A power/MDE number.** (P1.) The plan cannot be greenlit to P3 without it.
3. **A placebo (length-matched) prose arm.** (P2-conf.) Without it, "prose helps" is confounded with "more context helps."
4. **A numeric driver-adequacy gate at P2.** (P2-floor.) "Strengthen if ~0" is prose; make it a threshold.
5. **A stated scope limit.** Given band-selection + empty-P2P + single-harness, the honest claim is narrow: "within a difficulty-enriched subset of N instances on harness H, governance prose changed FAIL_TO_PASS by X% (CI …)." The Goal (lines 50-56) currently implies a broad causal claim about "frontier agents" that the design cannot support.

---

## Net assessment

The substrate and integration-contract work is real and de-risks the *plumbing*. The **science** is the unfinished part: as specified, the most likely outcome of P3 is a wide-CI null that cannot distinguish "governance doesn't help," "underpowered," "wrong difficulty band," "wrong metric dimension," and "context-length confound." Before spending on the factorial, the two must-fixes are **(1) a power/MDE computation that commits to a unit of analysis and a paired mixed-effects model, and (2) a placebo arm + separated FAIL_TO_PASS/PASS_TO_PASS outcomes.** Without those, the run will burn budget producing a number you can't interpret.

I have not run anything; this is a documents-only review of the plan and state file.
