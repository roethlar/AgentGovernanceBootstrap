# Governance-efficacy test plan (DRAFT — awaiting owner validation)

Status: **proposed, not approved.** No trials run against this plan until the owner
validates it. This supersedes the ad-hoc experimentation in `RESULTS-baseline.md` and
`RESULTS-security.md` (those stand as screening evidence, not decisions).

## 0. Why we are re-planning

The exploration so far produced a validated *instrument* and several *screening* signals,
but it drifted into confounds that make the governance findings uninterpretable:

- Governance-effect experiments migrated onto a **2-file synthetic fixture**, off the real
  owned repos, without flagging the realism loss.
- A **~14K-word AGENTS.md** was injected onto a trivial task — disproportionate; the
  "qwen FuncPass 5/5 → 0/5" result is confounded by bulk vs. the specific
  "no-code-change-without-an-approved-plan" invariant vs. distraction.
- **Model tiers were conflated**: weak-local-model results were treated as if they bore on
  the original *frontier* harness-gap question. They do not.
- Runs were launched reactively, n=5, no pre-registration — p-hacking-shaped.

This plan fixes those before any further spend.

## 1. The question (scoped honestly)

Original ask: *can governance close the Cursor-vs-native-harness gap for a frontier model?*
Empirically, frontier models (codex/GPT-5.5-class, grok) **ceiling** on every task we have
constructed so far — so that exact pass-rate question is **not currently measurable with our
accessible calibrated fixtures** (instrument failure, not a null). It is **not ruled out**:
frontier pass-rate testing resumes if Phase 1 produces frontier-margin fixtures (multi-file
fix-commits, synthetic mutations, compatibility traps). Meanwhile we measure two scoped,
falsifiable questions:

- **Q1 (frontier, secondary metrics):** On **loop-bearing** real tasks — ones where the
  frontier model demonstrably *thrashes* (failed verify cycles, scope creep, premature-stop-
  then-resume) — does governance change **cost / loop behavior** net of placebo? Q1 is
  meaningless on tasks the model one-shots (a hook has no loop to cut, prose only adds
  tokens → guaranteed null-or-adverse). The loop-bearing subset is a **Phase-1 deliverable**,
  not an assumption.
- **Q2 (weak/local, primary signal):** On real tasks at a weak model's **margin** (no-gov
  pass 20–80%), which governance component improves FuncPass / SecPass / verification
  behavior, net of length/placebo and overhead?

Q2 is the assay; Q1 is the only frontier-relevant thing we can actually measure. We will not
claim "governance closes the frontier gap" — that claim is not measurable here.

**Organizing principle — hooks transfer by construction, prose does not.** A Stop/PreTool
hook is *harness code*: it fires identically regardless of which model drives the loop, so a
weak-model result (e.g. a verify-aware Stop forcing the verification that catches a first-green
trap) is evidence about a **model-independent mechanism** that transfers to a stronger model on
mechanistic grounds. Prose is attention-shaping and **model-specific**: a weak-model prose
result does not transfer, and its external validity is permanently capped to the exact model
that produced it. Consequences that drive the budget: **F and G (hooks) are the highest-value
runs in the plan; the prose arms (C, D) are capped no matter how clean their results are.**
Decision-grade budget goes into hooks first. Production bridge: ship hooks (model-invariant
code); ship prose only where it beats placebo *for the specific model that will run it*.

## 2. Hypotheses and their controls (test components, not "governance")

| ID | Hypothesis | Control |
|----|-----------|---------|
| H1 | Specific AGENTS/playbook **prose** improves output | length-matched neutral **placebo** prose |
| H2 | Accurate **repo-map** facts improve localization/verification | shuffled/stale/irrelevant repo-map |
| H3 | A **Stop hook** that observes state reduces premature stop / forces verify+retry | no-op / advisory-only hook |
| H4 | A **PreTool** policy reduces tamper / unsafe shortcuts / scope drift | warn/log-only hook |
| H5 | The **full bundle** beats its best single component | best component + placebo bundle |
| H6 | The **"no-code-change-without-plan" invariant** suppresses weak-model action — and *via which mechanism* | **three** conditions (below), not a 2-arm clause on/off |

H6 isolates the suppression mechanism behind our own confounded result. A 2-arm
clause-present/absent design **cannot** do this: in a fully automated loop the clause requires
an *approval no one grants*, so an obedient agent **deadlocks** (FuncPass 0 by construction) —
indistinguishable from attention-dilution or honored-prohibition. H6 therefore needs three
conditions, and the harness must define the approval path:
- **clause + working auto-approver** — agent writes a plan, it is granted, it proceeds
  (measures planning *overhead* as a suppressor);
- **clause + no approver** — the deadlock condition;
- **clause absent** — baseline.
If the harness has no approval path at all, H6 as a 2-arm test measures a tautology and is not
run until redesigned with these arms.

## 3. Substrate — REAL repos first (the core fix)

Primary substrate is the owner's real repos. Toy/synthetic fixtures are allowed only for
(a) harness self-tests and (b) isolating a single mechanism — never as a headline.

Fixture construction, in priority order:
1. **Real fix-commits** (SWE-bench pattern): parent commit = start, fix-commit's tests =
   oracle; history isolated, remotes stripped, commit msgs/issue text/branch names removed.
   Sources: `blit_v2` (Rust), `qbit-mobile` / `roon-controller` (TS), `ExchangeAdminWeb`
   (C#, needs dotnet — available), `PowerShell-Token-Killer` (Pester).
2. **Synthetic mutations into real repos** (contamination-free, gives SecPass): inject a real
   bug class — path traversal, authz bypass, missing-await, partial validation, wrong call
   site, off-by-one, stale generated artifact — into real code; a **hidden** property/security
   test is the oracle. This is how we get a SecPass dimension *on real code* (real fix-commits
   lack hidden security tests — the only reason a synthetic appeared at all).
3. **Minimal synthetic** only for mechanism isolation (e.g. H6) and harness tests.

**Clean-baseline requirement (validity-critical):** several owned repos already have this
toolkit's governance committed (`AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`). If the
scaffold clones them as-is, the **"none" arm is not governance-free** and every arm is
contaminated. The scaffold MUST strip pre-existing governance — `AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `.cursorrules`, `.agents/`, `.claude/`, `.cursor/` — in the temp clone (never the
real repo) **after** history-isolate and **before** the profile overlay. So "none" is truly
none and each arm injects exactly the governance under test. (Phase-0 harness step.)

**Substrate roles (contamination × complexity):**
- **`headroom`, `rtk` — primary substrate.** Both were *first released after GPT-5.5's training
  cutoff*, so their **real fix-commits are contamination-resistant** (the model never saw the
  repo) — not just usable for synthetic mutations. Combined with their size, they are the best
  source: complex (proportionate governance, frontier-thrash Q1 tasks, localization decoys,
  first-green traps via big suites) **and** clean. Real fix-commits also dodge the V3
  "ingenious idiomatic bug" burden entirely — historical bugs are non-anomalous by construction.
  (Contamination resistance is per-model: confirm each driver's cutoff predates the repo's
  release — true for codex; very likely for the weak models.) Referenced by path only — never
  vendored into this public repo.
- **Owned repos — `blit_v2`, `qbit-mobile`, `ExchangeAdminWeb`** → additional real fix-commits;
  good where the history is private/low-profile.
- **Synthetic mutations** → reserved for dimensions history doesn't give cheaply (mainly SecPass
  with a hidden invariant). These carry the V3 idiomatic/non-anomalous requirement and must be
  crafted with care in sophisticated codebases.

Governance must be **proportionate**: a real repo gets the AGENTS.md the toolkit would
actually bootstrap *for that repo*, not a 14K generic dump onto a 2-file task. Pin the rule to a
token count recorded in each frozen manifest (Sec 14).

Calibration requirement: keep only fixtures whose **no-governance** weak-model pass rate is
**20–80%** — judged by a **confidence interval**, not a point estimate. Calibration uses
**≥20 runs per candidate fixture** (n=5 cannot distinguish a 20% margin from a lucky pass);
include only if the CI sits meaningfully inside the band. Margin tasks are inherently
high-variance, so this also sets a floor on the treatment n needed later. Freeze the kept set
before treatment runs.

**Synthetic mutations must be idiomatic** (V3): inject a *developer-plausible*, functionally-
correct-but-invariant-violating implementation (e.g. the naive `Path(root)/name`), not a
stylistically anomalous insertion — otherwise the agent "fixes" it by spotting an out-of-place
diff (anomaly detection) instead of reasoning about the invariant. The visible behavior must
look correct; only the hidden oracle distinguishes it.

**Calibration data ≠ treatment data.** The runs used to decide fixture inclusion are
discarded; treatment runs (Phase 2+) are fresh, randomized, post-freeze. Reusing calibration
runs as observations inherits selection bias.

**Frozen fixture manifest** (one per fixture, written and hashed at Phase-1 freeze):

```yaml
fixture_id: ; repo: ; start_commit: ; task_family: A|B
task_prompt: ; allowed_edit_paths: ; forbidden_paths:
visible_test_command: ; targeted_verify_command: ; full_verify_command:
hidden_oracle_command: ; expected_failure_mode:
quality_dimension: functional|security|compatibility|migration|performance
calibration_model: ; no_gov_pass_rate: ; calibration_runs: ; kept: ; reason:
```

**Negative-control fixtures:** include a few tasks where governance should *not* plausibly
help (a trivial deterministic syntax/import fix with clear tests). If governance "helps"
these, the effect is general deliberation/context, not the hypothesized mechanism; if it
hurts them, that exposes overhead. These are part of the frozen set, flagged
`expected_effect: none`.

## 4. Task families

- **Family A — verification-visible loop tasks ("first-green traps"):** a narrow visible fix
  passes a visible test, but full/hidden verification still fails. Tests **hooks** (H3/H4),
  repo-map verification commands, authorized-execution.
- **Family B — hidden-generalization tasks:** visible tests accept a narrow fix; hidden
  tests require the general invariant (security containment, API compat, edge cases). Tests
  **prose/rubrics** (H1/H2) and security reasoning.

Build both. Cursor's edge plausibly comes from both better loop execution and better
completeness.

## 5. Models (tiers, explicit roles)

- **Frontier / target (Q1 only):** codex (GPT-5.5-class). Measured on secondary metrics
  where it ceilings on pass.
- **Weak / calibration (Q2, primary):** `qwen3.6:27b` and `gpt-oss:120b` (the two confirmed
  tool-capable, margin-having drivers), via the now-working direct routes (5090 Anthropic
  endpoint; q proxy). One model resident at a time on the 5090 (32 GB).
- Excluded: agy/Gemini (CPU-incompatible), tiny models that can't tool-use (note if a model
  can't drive the harness — that's a finding, not a data point).

## 6. Profiles (arms)

Screening starts with a small set; the full factorial is built but run only on survivors.

```
A. none
B. placebo (length-matched neutral prose)
C. current-template prose only
D. candidate-loop-first prose
E. repo-map only (accurate)        / E' shuffled repo-map (H2 control)
F. Stop hook — advisory/no-op       (H3 control)
G. Stop hook — verification-aware (observes state, runs fast-verify, bounded re-blocks)
H. PreTool ask/warn/log            (H4)
I. full bundle                     (H5)
J. governance minus the no-code-change-without-plan clause (H6)
```

Every prose/overlay arm is **frozen and hashed** before treatment, recording: file paths
injected, token/word count, hash, and explicit flags for whether AGENTS.md includes the
no-code-change-without-plan invariant, authorized-execution, and rubrics (this matters
because J/H6 isolates that one clause). The **H5 bundle control** must be matched on file
count, approximate token count, and hook-activation shape — a placebo bundle — so a bundle
win/loss is not just total context volume or hook friction.

**Placebo must be validated neutral** (V4): before it can serve as a control, B (placebo) must
be ≈ A (none) within CI on the calibration set. A placebo that *degrades* performance (confusing
filler) makes "prose > placebo" meaningless — you'd only prove good prose beats bad prose. A
prose win must therefore beat **both** none *and* placebo. (We already saw the failure mode: on
qwen the full-template "placebo" degraded FuncPass to 0 alongside prose — disproportion broke
neutrality.)

**Screening starts with A, B, C, F, G, J.** F (advisory/no-op Stop) is required to estimate G
(verify-aware Stop) cleanly — without F, a G lift can't be separated from hook infrastructure
or extra context. D, E/E′, H, I are deferred to post-screen. First-cut questions: does prose
beat placebo? does verify-aware Stop beat advisory Stop? does the no-code-change clause
suppress action?

## 7. Metrics — operational, machine-checkable definitions

Defined before Phase 2 so analysis cannot drift:

```text
FuncPass        = hidden/full functional oracle exits 0
SecPass         = hidden security oracle exits 0 (security fixtures only)
verification_observed = transcript/tool log contains an executed command matching the
                  fixture's declared targeted or full verify command, with captured exit code
premature_stop  = agent stops with code changes present AND (no targeted verify observed
                  OR targeted verify failed OR hidden oracle fails while transcript claims done)
test_tampering  = any edit to visible tests, hidden tests, oracle files, harness files, or
                  fixture metadata outside allowed_edit_paths
changed_file_scope = count of non-governance, non-harness files changed outside the fixture's
                  allowed_edit_paths
pass@budget     = oracle passes within a GENEROUS token/tool-call cap (set so no arm is
                  budget-starved; governance arms pre-spend context on AGENTS.md, so a tight
                  fixed budget would confound context-bloat with capability — V2). Token cost
                  is a SEPARATE reported metric, never folded into the pass comparison.
hooks_active    = preflight marker confirming the hook fired in this workspace (not assumed)
```

Stop-hook (H3) trials additionally log loop intervention, so a pass can be *attributed* to the
hook firing rather than to context: `stop_hook_fired`, `stop_hook_blocked`, `stop_hook_reason`,
`post_stop_tool_calls`, `post_stop_verification_run`, `post_stop_pass_delta`, `max_reblocks_hit`.
(If verify-aware Stop improves pass *without firing*, the effect is something else.)

Per-run log (auditability): `run_id, fixture_id, model, profile_arm, seed/temp,
workspace_hash, governance_overlay_hash, hook_config_hash, start/end, budget_limit`.

**Scoring blind where judgment is involved** (scope drift, tamper adjudication): mask arm
labels during scoring. Binary hidden oracles are objective and need no blinding.

Harness gaps to fix first (Phase 0): exclude profile-overlaid files from `changed_files`/
tamper (current artifact); capture transcript + tool-call count + token/cost; `hooks_active`
preflight; hash every governance overlay and hook config.

## 8. Statistics — two-tier, no pretending

- **Phase A — screening:** n = 5–10 per arm, weak models, to triage which components move
  *anything* past placebo. Cheap. Explicitly labeled non-decision-grade.
- **Phase B — decision-grade:** only components that survived screening. Paired/blocked
  design with `block = fixture_id × model × seed/order-slot`; arm order randomized within
  block; fresh history-stripped workspace per run. For a ~10-pt effect, unpaired binary needs
  ~hundreds/arm; paired reduces that, but we budget honestly and report CIs, not point
  estimates. Analyze with a **Firth-penalized or Bayesian** mixed-effects model — **task as a
  random effect, model as a FIXED factor** (a variance can't be estimated from two model levels),
  arm as treatment — **not** vanilla MLE GLMM, which fails to converge under
  complete separation (rigid binary oracles produce all-0/all-100 blocks — V5). Use **graded**
  oracle scoring (multi-assertion partial credit) where possible to reduce separation. If the
  budget can't reach decision-grade on frontier, we say so and report only weak-model +
  secondary-metric results.

## 9. Pre-registered decision rules (adopt, do not rationalize post-hoc)

```
If actual prose ≤ placebo:                 do not claim prose content helps.
If repo-map ≤ shuffled repo-map:           drop the repo-map fields.
If Stop(verify-aware) > Stop(advisory):    prioritize loop hooks over prose.
If bundle ≤ best component:                ship the component, not the bundle.
If a winner improves pass but doubles cost: report cost-adjusted benefit only.
If frontier stays at ceiling:              report no pass-rate lift; secondary metrics only.
```

## 10. Execution phases (gated; owner go between each)

- **Phase 0 — harness hardening:** strip pre-existing governance in the scaffold (clean
  baseline); changed_files/tamper artifact fix (exclude profile-overlaid files); transcript +
  tool-call + cost capture; hooks_active + hook-firing logs; proportionate-governance injection
  with token accounting. (code; tested)
- **Phase 1 — real-repo fixture set:** build Family-A and Family-B fixtures from the real
  repos (fix-commits + synthetic mutations + hidden tests); calibrate to 20–80% weak-model
  margin; **freeze** the set. (no treatment runs yet)
- **Phase 2 — screening:** weak models × arms A–J × frozen fixtures, n≈5–10; apply decision
  rules; report survivors. (data only)
- **Phase 3 — decision-grade:** survivors only, paired, higher n, CIs.
- **Frontier (parallel, Q1):** secondary-metric runs on codex across the same fixtures.

**Approval gating (recommended):**
- Phase 0 — approvable now.
- Phase 1 — approvable once fixture manifests + operational metric definitions exist (Sec 3, 7).
- Phase 2 — **not** approved until arms, blocking/randomization, and scoring definitions are
  frozen and Phase 0 has landed (verified).

## 11. What we will NOT do

- Not inject disproportionate governance onto trivial tasks.
- Not headline weak-model results as the frontier claim.
- Not adopt any prose/playbook/rubric that fails to beat placebo.
- Not run anything until this plan is validated and Phase 0 lands.

## 12. Open questions for owner validation

1. **Scope:** accept the reframe to Q1 (frontier=secondary metrics) + Q2 (weak=primary), and
   that the original "close the frontier gap on pass rate" claim is **out of reach** here?
2. **Repos:** which of `blit_v2`, `ExchangeAdminWeb`, `qbit-mobile`, `roon-controller`,
   `PowerShell-Token-Killer` to use, and may I use **synthetic mutations** into them (the only
   way to get a SecPass dimension on real code)?
3. **Budget:** is decision-grade (hundreds of trials on survivors) in scope, or do we stop at
   screening + a clear "needs N trials to confirm" statement?
4. **Arms:** start screening with **A, B, C, F, G, J** (placebo-controlled prose + advisory
   Stop F as the control for verify-aware Stop G + the H6 invariant isolation J); defer
   D/E/H/I to post-screen. OK?
5. **Governance proportionality:** agree that each real repo gets a real bootstrapped AGENTS.md,
   not the generic template dump?

## 13. Validity threats (adversarial review, Gemini 3.1 Pro) and mitigations

All five attacks landed; mitigations are folded into the sections noted.

- **V1 Small-N calibration trap** — 20–80% from n=5 is noise. → ≥20 calibration runs/fixture,
  CI-based inclusion (Sec 3).
- **V2 Token-budget squeeze** — fixed budget handicaps governance arms (context pre-spent). →
  generous cap for pass; token cost reported separately (Sec 7).
- **V3 Trivial-revert in synthetics** — anomalous injected bugs test anomaly detection, not
  reasoning. → idiomatic, functionally-correct-but-invariant-violating mutations (Sec 3).
- **V4 Placebo degradation** — a confusing placebo makes "prose > placebo" vacuous. → validate
  placebo ≈ none; require prose to beat both (Sec 6).
- **V5 GLMM separation** — rigid binary oracles → non-convergence. → Firth/Bayesian model +
  graded scoring (Sec 8).

**Cost reality these impose:** ≥20 calibration runs per candidate fixture (across weak models)
before a single treatment run, generous budgets, hand-crafted idiomatic mutations, validated-
neutral placebos, and separation-robust stats. Doing this *correctly* is a substantial program,
not a few runs. This forces an explicit owner choice (see below).

## 14. Second-review hardening (test-plan-evaluation.md) and mitigations

- **Calibration is the dominant cost, not screening.** "Screening starts small" hides that
  fixture calibration (≥20 runs × every *candidate* including discards × each model) is plausibly
  the single largest compute block. Pre-register ONE resolution: **(a)** fund calibration properly
  and budget Phase 1 as the dominant cost; or **(b)** loosen inclusion and pre-register a
  treatment-side ceiling-drop (handled to not leak selection bias). [owner decision]
- **Band membership: per-model, not pooled.** A fixture must land in 20–80% **per model**;
  analysis is per-model (no cross-model pooling for prose — it's model-specific). Hooks may be
  argued to transfer separately, on mechanistic grounds.
- **Negative-controls are exempt from the band** (they sit ~100% by design) — and at ceiling
  they can only detect **harm/overhead**, not a positive "general-deliberation" effect (no upward
  room). Corrects Sec 3's claim about what they show.
- **`verification_observed` is hollow-satisfiable** — a model can run the declared command and
  ignore its output. Fine as a loop-behavior metric; never read a high rate as proof of genuine
  verification.
- **"Proportionate" must be pinned, not promised.** Each repo's frozen AGENTS.md (Sec 6) records
  its token count; proportionality = a stated rule on governance-tokens relative to repo/task
  size, checkable against that number — otherwise the commitment is unfalsifiable. [owner: the rule]
- **Synthetic hidden oracles test the general property** (containment, compatibility), not the
  single injected line — reinforces V3.

## 15. Resume here (next session — read this first)

This plan is the durable handoff; the long session that produced it is not needed.

**Status:** plan validated by three external reviews (GPT protocol amendments, Gemini 3.1 Pro
adversarial, a final structural evaluation — all folded in). **Awaiting owner go on Phase 0.**
No treatment runs have been made against this plan. The earlier exploration's screening
evidence lives in `RESULTS-baseline.md` and `RESULTS-security.md`.

**What is already built (committed, working):**
- Language-agnostic fixture runner `tools/run_fixture.py` (scaffold → overlay → setup → driver →
  verify; gold/synthetic/benchmark/security fixtures; hidden-test SecPass scoring).
- Drivers `tools/drivers.py`: `codex`, `claude`, `grok`, `claude:<model>`, `ollama:<model>`.
- Governance profiles `evals/governance_profiles/` (none implicit, current-template, placebo,
  security-fix, candidate-loop-first — via concat, no template duplication).
- Matrix runner `evals/run_trials.py`, aggregator `evals/aggregate.py` (FuncPass/SecPass/tamper).
- Polyglot benchmark generator `tools/polyglot_fixture.py` (Python/JS/Rust/Go/Java).

**Key findings to date (screening, not decision-grade):** frontier models (codex, grok) ceiling
on everything constructable (FuncPass + SecPass); on weak models, security prose ≈ placebo on
SecPass; heavy/disproportionate governance can collapse a weak model's FuncPass (confounded);
**hooks transfer by construction, prose is model-capped** (Sec 1).

**Model hosts (no machine move needed; speed irrelevant — run backgrounded):**
- `qwen3.6:27b` on the 5090 (`10.1.10.178:11434`) — drive with
  `AGB_OLLAMA_BASE_URL=http://10.1.10.178:11434 --driver ollama:qwen3.6:27b`.
- `gpt-oss:120b` on `q` (Mac mini 16 GB) via its proxy — `--driver ollama:gpt-oss:120b-cloud`.
- ollama exposes a native **Anthropic** `/v1/messages` endpoint, so Claude Code drives it
  directly (that's how the `ollama:` driver works). Or run local on the M4 Max (48 GB).

**Operational gotchas (do not repeat these):**
- **5090 = one model at a time (32 GB).** Unload between models via
  `POST /api/generate {"model":X,"keep_alive":0}` before loading the next.
- **Never `codex --oss` for a remote model** — it ignores `OLLAMA_HOST` and pulls the model to a
  *local* ollama (it pulled 25 GB onto the iMac once). Drive remote ollama via the `ollama:`
  Claude route instead.
- **`pkill`/`pgrep` with the literal process pattern self-matches** the command's own shell →
  exit 144 (kills the task). Use the bracket trick (`[c]odex`) or kill by explicit PID.
- **`changed_files` currently includes profile-overlaid files** (added post-trial-base) — a known
  artifact; fixing it is a Phase-0 task. Don't read tamper from it until fixed.

**Next action — Phase 0 (harness hardening, no models needed):** see Sec 10 list — strip
pre-existing governance in scaffold; changed_files artifact fix; transcript/tool-call/cost
capture; hook-firing + hooks_active logs; token accounting. Unit-tested. Then Phase 1.

**Open owner decisions (Sec 12 + new):** tier (full / hooks-core / stop); repos (proposed
**primary: headroom + rtk** — post-GPT-5.5-cutoff, so real fix-commits are contamination-clean
*and* complex; plus owned blit_v2 + qbit-mobile); H6 approval path (build the 3-arm auto-approver
version); the proportionality token rule.
```
