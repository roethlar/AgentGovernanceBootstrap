# Pre-registration — governance-efficacy factorial on SWE-bench Pro

**Status:** DRAFT for owner review. Written 2026-06-29. This operationalizes the
plan-review must-fixes (`docs/history/2026-06-29-swebench-pro-plan-review_synthesis.md`)
into a pre-registered design, fixed *before* the confirmatory run so the analysis is
not chosen after seeing results. Live status: `.agents/state.md`.

Owner decisions locked 2026-06-29: confirmatory harness = **Claude Code only**
(codex a possible later add if the lift is small; grok/agy testing-only); arms =
**4-arm with placebo**.

## 1. Question

Does task-relevant governance (completion-steering prose; prose + enforcement hooks)
causally raise a coding harness+model's rate of correctly fixing real bugs, holding the
bug, harness, and model fixed?

## 2. Subject under test

- **Harness + model:** Claude Code (host native amd64 `claude`, subscription auth,
  in-container as non-root `agent`). No API keys. This is the single confirmatory
  harness. Codex is a pre-registered *secondary* that may be added only if the
  Claude result motivates it and the marginal cost is small; if added it is analyzed
  as a separate replication, never pooled into the primary estimate.
- **Model must be pinned (reproducibility — 2026-06-29).** The driver now passes an
  explicit `--model`; the confirmatory model is **Opus 4.8** (`claude-opus-4-...`).
  `~/.claude/settings.json` has no `model` key, so any run WITHOUT `--model` uses the
  account default (ambiguous) — acceptable for a sizing pilot, but the powered
  confirmatory run MUST pin `--model` and record the exact id. **Secondary capability
  points** (separate replications, never pooled, throttled like codex): **Sonnet 4.6**
  (`claude-sonnet-4-6`) and **codex gpt-5.5**. Running Opus, Sonnet, and codex/gpt-5.5
  characterizes the governance effect as a function of model capability — governance is
  most detectable where the model is not already saturating.
- **Fixtures:** SWE-bench Pro instances (real bugs, real regression tests), drawn
  from the 92-instance complex+regression-rich pool (gold ≥3 files, PASS_TO_PASS ≥15,
  FAIL_TO_PASS ≥3).

## 3. Arms (the factor: governance content present in the agent's repo)

All arms share identical substrate (same image, same anti-leak re-init scrub, same
task prompt, same timeout, same source-only capture, same scorer). They differ ONLY
in what governance material is present in `/app` before the agent starts:

1. **none** — no governance file, no hooks. (= the 2026-06-29 baseline arm.)
2. **placebo-prose** — a file of *topically irrelevant* prose, length-matched to the
   `task-prose` arm in tokens, plus a `CLAUDE.md`/equivalent pointer so it is actually
   loaded. Controls for "any prose in context helps."
3. **task-prose** — the completion-steering guidance profile
   (`evals/governance_profiles/task-prose/`): understand the failing test, fix the root
   cause not the symptom, do not weaken or skip tests, run the tests and iterate, don't
   stop until green. Task-relevant guidance only — **no** drift / git / human-interaction
   content. No hooks.
4. **task-prose-hooks** — `task-prose` **plus** the two enforcement hooks that *enforce*
   what the prose *states*: `hook-gate` (a Stop hook — don't finish while visible tests
   are red) and `hook-guard` (a PreToolUse hook — refuse edits to test or protected
   files). A clean prose-vs-enforcement factorial.

**Why not the full product governance (owner decision — plan Addendum b).** The full
`current-template` AGENTS.md (Prime Invariants, words-first, approval gates, drift/git
discipline) is built for an agent working *with a human* and is wrong for an autonomous
test-solving run, so it is deliberately **NOT** a prose arm; the prose arm is the
task-relevant subset only. (A 2026-06-29 sizing pilot erroneously injected the full
AGENTS.md as the prose arm — its prose/hooks results are invalid; see
`opus-pilot-results.md`.)

Length-matching rule: placebo token count within ±10% of the `task-prose` token count,
measured with the same tokenizer; record both counts in the run metadata.

**Injection mechanism (validated 2026-06-29, keystone for arm validity):** Claude
Code in `-p` mode loads **`CLAUDE.md`** from the working dir (`/app`) as project
memory, and follows its `@AGENTS.md` import — but a **bare `AGENTS.md` with no
`CLAUDE.md` is INERT** (not loaded). So every governed arm MUST deliver governance
via `CLAUDE.md` (either the prose inline, or a `CLAUDE.md` = `@AGENTS.md` shim + the
profile text in `AGENTS.md`). The task-prose and task-prose-hooks arms deliver the
`task-prose` text through this same loading path; the placebo arm likewise needs
a `CLAUDE.md` (inline or importing the placebo file) or it would be inert and
collapse into the `none` arm. Confirmed by canary probe: CLAUDE.md canary appeared,
bare-AGENTS.md canary did not, `@AGENTS.md`-imported canary did.

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
  (i) task-prose − none, (ii) task-prose-hooks − task-prose (the hook increment),
  (iii) task-prose − placebo (the content-vs-mere-prose test).
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

## 9b. Capture mechanics (critical — learned 2026-06-29, sizing pilot)

The agent's patch MUST be captured as the net diff against a **pinned base tag**
(`git add -A && git diff --cached eval_base`), NOT against HEAD (`git diff --staged`).
Reason: Claude Code commits its work autonomously, and the governed arms' AGENTS.md
explicitly says *"commit each slice as it lands"* — so a vs-HEAD capture returns EMPTY
whenever the agent commits, scoring a real fix as a false failure. This biases the
**governed arms hardest** (they are instructed to commit), which would make governance
look harmful — a catastrophic confound. Setup pins `eval_base` right after the
re-init base commit; capture diffs the base tree against the index, ignoring any
intermediate agent commits. Validated: a committed edit is EMPTY under vs-HEAD and
captured under vs-eval_base. (The 2026-06-29 ungoverned baseline probe used vs-HEAD
but had ZERO empty patches, so no baseline cell committed → that result is unaffected.)

Also hardened (same session): in-container agents retry up to 4× on an empty patch
with a fresh container per attempt (the anti-leak git re-init means in-place reset
can't restore clean base), longer backoff when a connection-error signature appears,
and cells flagged `neterr` when a proxy/network outage caused the empty — so a proxy
outage surfaces as invalid cells, not as agent failures. (Earned: a power outage
rebooted the headroom proxy mid-pilot and corrupted 24/45 cells before the guard.)

## 10. Threats to validity (carried forward)

- Single harness ⇒ result is about Claude Code; generality to codex/agy/grok is a
  separate study (by design).
- Subscription stochasticity ⇒ replicates + mixed model.
- Placebo realism ⇒ placebo must be plausible-looking prose, not lorem ipsum, or the
  agent may ignore it differently than real governance.
- Leakage ⇒ closed by re-init (validated); re-confirm on any new repo added.
- **Hook exercise under single-shot `-p`:** unlike the product's re-ground/tripwire
  hooks (which fire only on *context compaction* or AGENTS.md edits, and so would barely
  fire in a one-shot run), the two hooks under test here fire readily during an ordinary
  bug-fix run: `hook-guard` (PreToolUse) fires on every edit attempt, and `hook-gate`
  (Stop) fires whenever the agent tries to finish, blocking it while tests are red. So
  the task-prose-hooks arm genuinely exercises the enforcement mechanism, not just the
  prose. The driver instruments hook firing (sentinel log) so firing is observed, not
  assumed; a cell where the relevant hook had no opportunity to fire (e.g. the agent made
  no edit, or never attempted to stop with tests red) is recorded, so the hook-increment
  contrast (ii) is computed only over cells where the hook could act (codex review
  must-fix: minimum hook-opportunity criterion).
