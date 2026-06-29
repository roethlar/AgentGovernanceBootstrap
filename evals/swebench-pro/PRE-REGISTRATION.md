# Pre-registration — governance-efficacy factorial on SWE-bench Pro

**Status:** DRAFT for owner review. Written 2026-06-29. This operationalizes the
plan-review must-fixes (`docs/history/2026-06-29-swebench-pro-plan-review_synthesis.md`)
into a pre-registered design, fixed *before* the confirmatory run so the analysis is
not chosen after seeing results. Live status: `.agents/state.md`.

Owner decisions locked 2026-06-29: confirmatory harness = **Claude Code only**
(codex a possible later add if the lift is small; grok/agy testing-only); arms =
**4-arm with placebo**.

## 1. Question

Does repository governance (AGENTS.md prose; prose + enforcement hooks) causally
raise a coding harness+model's rate of correctly fixing real bugs, holding the bug,
harness, and model fixed?

## 2. Subject under test

- **Harness + model:** Claude Code (host native amd64 `claude`, subscription auth,
  in-container as non-root `agent`). No API keys. This is the single confirmatory
  harness. Codex is a pre-registered *secondary* that may be added only if the
  Claude result motivates it and the marginal cost is small; if added it is analyzed
  as a separate replication, never pooled into the primary estimate.
- **Fixtures:** SWE-bench Pro instances (real bugs, real regression tests), drawn
  from the 92-instance complex+regression-rich pool (gold ≥3 files, PASS_TO_PASS ≥15,
  FAIL_TO_PASS ≥3).

## 3. Arms (the factor: governance content present in the agent's repo)

All arms share identical substrate (same image, same anti-leak re-init scrub, same
task prompt, same timeout, same source-only capture, same scorer). They differ ONLY
in what governance material is present in `/app` before the agent starts:

1. **none** — no AGENTS.md, no hooks. (= the 2026-06-29 baseline arm.)
2. **placebo-prose** — an AGENTS.md-sized file of *topically irrelevant* prose
   (length-matched to the real-prose arm in tokens), plus a `CLAUDE.md`/equivalent
   pointer so it is actually loaded. Controls for "any prose in context helps."
3. **real-prose** — the real portable AGENTS.md governance (Prime Invariants +
   universal invariants), no hooks.
4. **prose+hooks** — real-prose **plus** the enforcement hooks (re-ground on
   compaction, AGENTS.md tripwire) installed in the harness config.

Length-matching rule: placebo token count within ±10% of real-prose token count,
measured with the same tokenizer; record both counts in the run metadata.

## 4. Design

- **Within-instance (paired).** Each selected instance is run under all 4 arms, so
  every instance is its own control — this removes between-instance difficulty
  variance, the dominant noise source, and is far more powerful than independent
  groups.
- **Replicates.** Because the harness is stochastic, run **R replicates per
  (instance, arm) cell** (R fixed in the sizing pilot, §6; default R=3). Cell
  outcome = resolved rate over the R replicates (0, 1/3, 2/3, 1) or a per-replicate
  binary for the mixed-model analysis.
- **Randomization / blinding.** Arm order within an instance is randomized; the
  scorer is blind to arm (it only sees a patch + sample). Capture excludes any
  governance overlay files so an arm cannot be inferred from the diff and so
  governance files never reach the scorer.
- **Infra hygiene (inherited, proven):** detect "no output produced" container runs
  and retry; never count an infra-empty run as an agent failure; modest parallelism
  for heavy images. Anti-leak: `rm -rf .git && git init && commit base` (gold fix
  leaves zero trace) on every cell.

## 5. Metrics (report honestly, not collapsed)

- **Primary:** `resolved` = (FAIL_TO_PASS ∪ PASS_TO_PASS) ⊆ passed, per the
  third-party scorer.
- **Report separately** (must-fix): the **FAIL_TO_PASS** (functional fix) and
  **PASS_TO_PASS** (regression guard) components. PASS_TO_PASS is EMPTY on ~64% of
  instances; for those, `resolved` collapses to FAIL_TO_PASS only — flag these rows
  and never present a combined number as if regression-guarding was tested when it
  wasn't.
- Secondary/exploratory: patch size, files touched, tool calls, tokens, wall-clock
  (telemetry already captured) — descriptive only, not confirmatory.

## 6. Power / sample size (sizing pilot gates the confirmatory N)

The paired design's power depends on the **discordance** rate (instances that flip
between arms) and the replicate-level noise — neither is known yet. So:

1. **Sizing pilot (next step, modest compute):** run all 4 arms × R=3 replicates over
   a small set spanning the difficulty band (~8–12 instances, mixing some 2026-06-29
   failures and some near-misses). Estimate: (a) per-arm resolve rate, (b)
   within-instance arm discordance, (c) replicate variance.
2. **Compute MDE / N from the pilot:** target a minimum detectable effect of
   **+15 percentage points** prose-vs-none at **80% power, two-sided α=0.05** (revisit
   after pilot). Use the pilot's discordance to size the paired test (McNemar /
   mixed-effects logistic). Record the chosen N and the assumed discordance *before*
   the confirmatory run.
3. If the band is too small for the required N, expand selection from the 92-pool
   (and, if needed, relax pool thresholds) — selection rule fixed before scoring.

## 7. Subset selection (regression-to-mean guard — must-fix)

The 10-instance failure band from the single n=20 probe is a **starting pool, not the
confirmatory set.** Before freezing: re-measure candidate instances with replicates
(§6 pilot) and select on the *replicated* ungoverned rate, not the one-shot label, so
we don't build the sample from instances that merely got unlucky once. Target band:
instances whose replicated ungoverned resolve rate sits in a mid-range (e.g. 0.2–0.7)
— enough headroom for governance to move, not floor/ceiling-locked.

## 8. Analysis (pre-specified)

- **Model:** mixed-effects logistic regression on per-replicate binary `resolved`,
  fixed effect = arm (none as reference), random intercept per instance (and per
  instance×arm if replicate variance warrants). Pre-specified contrasts:
  (i) real-prose − none, (ii) prose+hooks − real-prose (the hook increment),
  (iii) real-prose − placebo (the content-vs-mere-prose test).
- **Multiplicity:** 3 pre-specified contrasts; control family-wise error (Holm).
- **Primary endpoint:** contrast (i) on the primary `resolved` metric. Contrasts
  (ii)–(iii) are pre-specified secondary.
- **Decision rule:** "governance helps" = contrast (i) CI excludes 0 in the positive
  direction at the corrected level; "content (not mere prose) helps" = (iii) likewise;
  "hooks add beyond prose" = (ii) likewise. Pre-registered so a null is reportable as
  a null.

## 9. What is fixed vs still open

- **Fixed now:** question, arms (4 incl. placebo), within-instance paired design,
  Claude-only confirmatory, metric honesty (F2P/P2P split), anti-leak + infra-retry,
  source-only blinded capture, analysis model + contrasts + multiplicity.
- **Set by the sizing pilot (then frozen):** R (replicates), confirmatory N, the
  replicated-rate band thresholds, the final instance list, the MDE if 15pp proves
  infeasible.

## 10. Threats to validity (carried forward)

- Single harness ⇒ result is about Claude Code; generality to codex/agy/grok is a
  separate study (by design).
- Subscription stochasticity ⇒ replicates + mixed model.
- Placebo realism ⇒ placebo must be plausible-looking prose, not lorem ipsum, or the
  agent may ignore it differently than real governance.
- Leakage ⇒ closed by re-init (validated); re-confirm on any new repo added.
