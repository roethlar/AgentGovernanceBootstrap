# Governance-efficacy test plan — v2 (operational)

**v2 inherits `TEST-PLAN.md` (v1) wholesale** — its scoping (Q1/Q2), hypotheses
(H1–H6), substrate rules, arms (A–J / `evals/governance_profiles/`), metric
definitions (Sec 7), statistics (Sec 8), decision rules (Sec 9), and validity
threats (V1–V5) all stand unchanged. v2 only **amends** v1 with: (a) SWE-bench Pro
as a substrate, (b) methodology hardening earned the hard way this session, and
(c) a token/time-efficient runbook to restart cleanly when caps reset. Where v2 is
silent, v1 governs. Read v1 first; this is the delta.

> **Why v2 exists / what went wrong:** a multi-hour SWE-bench Pro detour ran the one
> experiment v1 §1 explicitly calls *meaningless*: **frontier × one-shot × pass-rate ×
> full-AGENTS.md-as-prose**. It reproduced v1's predicted null (see §A). v2 captures the
> reusable parts of that detour and routes them back onto v1's rails.

---

## A. Findings from the SWE-bench detour (all confirm v1 — none overturn it)

Treat as **screening evidence only** (off-plan, underpowered, contaminated substrate):

- **Frontier one-shot prose does nothing / slightly hurts pass — exactly as v1 §1
  predicted.** Opus (n≈22/arm, single-shot, SWE-bench): none **50%**, hooks 43%,
  placebo 42%, prose **36%**. codex combined: none ≈ prose ≈ hooks (~30%), placebo
  **0/7**. "A hook has no loop to cut; prose only adds tokens → null-or-adverse."
- **Placebo (irrelevant prose) measurably hurts** on both → reconfirms **V4**: a prose
  win must beat *both* none and placebo, and placebo must be validated ≈ none first.
- **Half of a small hard-band is floor/ceiling-locked** (all-arms-equal → zero
  discordance) → reconfirms the **20–80% calibration band is mandatory**, judged
  per-model by CI (v1 Sec 3), not a convenience pick.
- **Hooks barely fire under single-shot Claude** (re-ground needs compaction; tripwire
  only on AGENTS.md edits) but **fire heavily on codex/grok** (per-edit) → reconfirms
  hooks need **loop-bearing / multi-turn** tasks to be exercised (v1 Q1).
- **Net:** no result here is decision-grade or transferable; they are a costly
  re-derivation of why v1 abandoned the frontier-pass framing.

---

## B. SWE-bench Pro as a substrate (amends v1 Sec 3)

SWE-bench Pro **is** v1's "Fixture construction priority #1: real fix-commits (SWE-bench
pattern)" — pre-built at scale (731 instances, 11 repos), parent commit = start,
fix-commit tests = oracle, with **FAIL_TO_PASS** (→ v1 `FuncPass`) and **PASS_TO_PASS**
(→ a regression-preservation metric; *not* security `SecPass`). It removes Phase-1's
biggest cost (hand-authoring + calibrating fixtures) — **but with hard limits**:

- **Contaminated by construction** (public benchmark; frontier models likely trained on
  it). Therefore: **never use it for a frontier pass-rate claim.** Allowed roles:
  - **Q2 weak-model screening** — fast, large margin-task source (still note contamination
    may inflate weak-model pass; prefer it for *screening which components move anything*,
    not the final weak-model claim).
  - **Q1 frontier loop/cost metrics** — loop behavior is not a pass claim, so contamination
    matters less; good for finding loop-bearing tasks where frontier thrashes.
- **Contamination-clean owned repos remain primary** for any decision-grade or frontier
  claim: **headroom, rtk** (released after GPT-5.5 cutoff → clean real fix-commits) +
  owned blit_v2, qbit-mobile. SWE-bench is the *fast screening lane*; clean repos are the
  *decision lane*. (v1 Sec 3 substrate roles unchanged.)
- **P2P (regression oracle) is empty on ~64% of instances** — split and flag it; never
  present a collapsed "resolved" as if regression-guarding was tested when P2P was empty.
- **Calibrate per-model to 20–80% (v1 Sec 3) before any treatment** — the floor/ceiling
  waste above is the proof. Pick the band on the *weak model that will run it*.

**Integration (efficient — no parallel drivers):** wire SWE-bench instances as a
**`benchmark` fixture type in the existing `tools/run_fixture.py`** (it already supports
gold/synthetic/benchmark/security fixtures), driven by the existing `tools/drivers.py`
(`claude`/`codex`/`grok`/`ollama:<model>`) with `evals/governance_profiles/` overlays and
`evals/run_trials.py` + `calibrate.py`. **Do not** resurrect the scratch `arms4*.py`
drivers — fold their *mechanics* (below) into `run_fixture.py`'s benchmark path.

---

## C. Harness/methodology hardening (fold into `run_fixture.py` / `drivers.py`)

Earned this session; several are validity-critical and not yet in the committed harness:

1. **Capture the agent's patch vs a pinned base TAG, not HEAD.** Agents commit their own
   work (Claude Code autonomously; governed arms are *told* to "commit each slice"), so a
   vs-HEAD diff returns EMPTY on commit → real fix scored as failure → **biases governed
   arms hardest (governance looks harmful)**. Pin `eval_base` after the anti-leak re-init;
   capture `git add -A && git diff --cached eval_base`. *(Highest-priority fix.)*
2. **Governance injection is harness-specific — canary each driver before trusting an
   arm** (the bare-`AGENTS.md`-is-inert trap): **Claude Code** loads only `CLAUDE.md`
   (+`@AGENTS.md` import); **codex** and **grok** read `AGENTS.md` natively (grok also
   `CLAUDE.md`; *not* `.cursorrules`/`GROK.md`). A prose arm injected via the wrong file
   silently collapses into `none`. Add a per-driver canary to `drivers.py`.
3. **Invalid-accounting:** an empty patch from infra/quota/network is **not** an agent
   failure → score `None` (exclude), never 0. Detect provider error signatures
   (rate-limit/quota/429/5xx/connection); **self-abort the batch on quota** and resume
   after reset. Distinguish from a *clean* empty (genuine no-op = real failure).
4. **Anti-leak + source-only capture (validated):** `rm -rf .git && git init && commit
   base && tag eval_base`; capture excludes the instance's **test files AND all governance
   overlay files** (AGENTS.md/CLAUDE.md/.cursorrules/.grok/.claude) so neither the gold fix
   nor the governance reaches the scorer/diff. (v1 Sec 3 clean-baseline + Sec 7 changed_files.)
5. **Weak-model prompting (qwen3.6:27b):** it explores then defaults to "what do you want?"
   without a **directive imperative** prompt and a **high token cap** — needs both, or it
   no-ops. Directly relevant to v1's Q2 primary models.
6. **Warm images before timing** (cold Docker pulls caused false all-arms EMPTY on a 3.8GB
   image); pre-pull, then run.

---

## D. Provider/cost model (new — drives the budget and schedule)

Hard constraints learned by hitting them:

- **Same-provider fleets share one account rate limit.** Concurrent Opus + Sonnet tripped
  Anthropic 429s. **Serialize all Anthropic-model runs**; **parallelize across providers**
  (Anthropic + OpenAI/codex + xAI/grok + local/ollama do not contend).
- **Token-heavy configs exhaust caps fast.** codex gpt-5.5 @ xhigh burned its whole window
  in ~27 cells. Run **small resumable batches** with quota self-abort; **drop reasoning
  effort** where xhigh isn't needed; prefer the smallest model/effort that shows the effect.
- **Caps vs money:** subscription 5-hour caps **reset for free**; **usage-credit overage is
  real spend** — schedule heavy runs to fit inside cap windows, not into credits.
- **In-container agents ride the account's credits headlessly** (no interactive opt-in
  needed) — so a runaway batch *will* spend real money past the cap. Bound every batch.
- **Local models (ollama) = free compute** (RTX 5090, one model at a time / 32GB; unload
  via `keep_alive:0`). Best home for large screening volume.

---

## E. Efficient execution order (token + time) — amends v1 Sec 10

Spend nothing on cells v1 already predicts null. Minimal path to a decision:

0. **Phase 0.5 — fold §C hardening into the committed harness** (capture-vs-tag, per-driver
   injection canary, invalid-accounting, quota self-abort). Unit-test. *No model spend.*
1. **Phase 1 — fixtures, calibration-first.** Verify the `../test_ground/` repos exist
   (came back empty — **blocker to confirm first**). Build Family-A/B from clean repos
   (headroom/rtk/blit_v2/qbit-mobile) **and** ingest a SWE-bench Pro slice as `benchmark`
   fixtures. **Calibrate on the FREE local weak model (qwen3.6:27b)** to the per-model
   20–80% band (≥20 runs/candidate, CI-based) → **freeze**. Calibration is the dominant
   cost; run it on local/free compute. *(v1 Sec 14.)*
2. **Phase 2 — screening, free/cheap first.** Arms **A, B, C, F, G, J** (v1 Sec 6) ×
   frozen fixtures × weak model, n≈5–10, **on local ollama (free)**. Apply v1 Sec 9
   decision rules. Report survivors only. Validate placebo ≈ none (V4) before reading any
   prose arm.
3. **Phase 3 — decision-grade**, survivors only, paired/blocked, higher n, CIs
   (v1 Sec 8). Spend paid caps here, **serialized per provider**, in cap-window batches.
4. **Q1 frontier (parallel lane, different providers concurrently):** loop/cost
   **secondary** metrics on **loop-bearing** fixtures only — never frontier pass-rate.
   This is the grok-≈-Cursor question (loop behavior), not a resolve-rate horse race.

**The efficiency rule of thumb:** local-free for calibration + screening → paid caps only
for decision-grade survivors → frontier only for loop metrics on loop-bearing tasks.

---

## F. Runbook — "start over when caps reset" (do exactly this)

1. Confirm clean slate: no eval containers/procs (we stopped everything).
2. `../test_ground/` repos present & governance-stripped? If empty, re-prep them (history-
   isolate, strip AGENTS.md/CLAUDE.md/.agents/.claude/.cursor, `git init`, no remotes) —
   **Phase-1 prerequisite.**
3. Land §C hardening in `tools/run_fixture.py`/`drivers.py` (Phase 0.5). Unit-test;
   mutation-prove each slice (v1 discipline).
4. Calibrate on **local qwen3.6:27b** (free) → freeze the 20–80% fixture set.
5. Screen arms A/B/C/F/G/J on local weak model (free) → survivors.
6. Only then spend paid caps on decision-grade survivors, serialized per provider, in
   cap windows; frontier loop-metrics in parallel on its own provider.

**Salvage from the detour:** the SWE-bench mechanics in `scratchpad/arms4*.py`
(anti-leak, capture-vs-tag, in-container subscription-auth mounting for claude/codex/grok,
scorer wiring, invalid-accounting) are correct and worth porting into the benchmark path —
but as a `run_fixture.py` fixture type, not standalone drivers. The `evals/swebench-pro/`
result docs are screening evidence (§A); they are **not** a design and do not compete with
this plan.

---

## G. Governance-doc reconciliation (do this when restarting)

- `.agents/state.md` drifted to track the SWE-bench detour, conflicting with this validated
  plan. On restart, reset `.agents/state.md` to point at **TEST-PLAN-v2.md → Phase 0.5/1**
  as the live work, and demote the SWE-bench entries to history.
- v1 `TEST-PLAN.md` remains the validated reference; v2 is the operational head.

---

## H. Codex review amendments (2026-06-29) — apply before decision-grade

Independent codex review verdict: v2 is ready for **Phase 0.5 hardening + fixture prep**,
**not decision-grade as-is**. The single biggest risk it flagged: producing a clean answer
to the *wrong* question — "does this arm do better?" instead of "did the hook fire and
cause it?" Amendments (each ties to the section it tightens):

- **H-a. Isolate the hook effect — never pool loop-control mechanisms.** Forced
  continuation is a *different intervention* per harness: Claude Stop hook (canary-proven
  continuation) ≠ grok `--check` (a CLI loop mode) ≠ codex/agy (unconfirmed). Treat each as
  its own arm; do not average them as "the hooks arm." Gate every hook causal claim on
  **mechanism logs** — `stop_hook_fired`, `stop_hook_blocked`, `post_stop_pass_delta`, and
  for the guard `guard_fired`/`guard_denied`. No mechanism evidence → no hook claim.
  (Amends §A/§E + `harness-capabilities.md`.)
- **H-b. Restate "hooks transfer by construction."** The hook *code* fires identically, but
  the *effect* depends on model compliance, tool-call patterns, deny-interpretation, and
  harness semantics. Correct claim: hooks are **less model-capped than prose, but require
  per-harness activation + behavioral validation** (canary + mechanism logs) before any
  transfer claim.
- **H-c. Invalid/quota exclusion is arm-correlated → can bias.** Governance arms run longer
  → hit quota/timeout empties more; excluding them can hide a real cost. **Report
  invalid-rate by arm**, set abort/retry thresholds, and run **sensitivity bounds** (count
  invalids as fail, and as best-case). If the conclusion flips, it isn't robust.
  (Amends §C item 3.)
- **H-d. Strengthen the placebo.** Topically-irrelevant prose controls token load but not
  instruction *salience* or governance *style*. Add a second control — a **governance-shaped
  inert placebo** (same imperative/process voice + structure, zero useful repo/task
  guidance). A prose win must beat **both** placebos. (Amends §B / v1 V4.)
- **H-e. SWE-bench contamination distorts loop metrics too** (not just pass) — memorized
  solutions cut search/verify loops. Use SWE-bench strictly for **plumbing + candidate
  mining**; **all decision-grade causal claims (Q1 loop and Q2 pass) use clean
  post-cutoff/owned fixtures**, SWE-bench reported separately. (Tightens §B.)
- **H-f. Freeze survivor rules before scoring; confirm on fresh data.** n=5–10 screening is
  triage only, never a "component works" claim. Pre-commit the exact promotion rule; rerun
  survivors on **fresh confirmatory** fixtures; keep **per-model** fixture panels — or limit
  each claim to the calibrated model (don't calibrate on qwen then claim for all). (Amends §E.)
- **H-g. Don't collapse H6 / arm J (the no-plan clause).** Only interpret J if the full
  **auto-approver / no-approver / clause-absent triad** is implemented (v1); a bare
  present/absent comparison is uninterpretable.
- **H-h. Freeze the stats.** Pre-register **one primary contrast per lane**; derive MDE/N
  from pilot discordance; control multiplicity across H1–H6 / arms / metrics with **Holm or
  hierarchical gatekeeping**. (Amends v1 Sec 8.)
- **H-i. Add before decision-grade:** (1) explicit **model/version/effort pinning** for
  every harness (`harness-capabilities.md`) — no unpinned runs; (2) a **minimum
  hook-opportunity criterion** for Family-A tasks (the task must actually present an
  edit/loop the hook can act on, or the hook arm is vacuous); (3) an **intent-to-treat vs
  mechanism-success** analysis split; (4) a guard so **weak/local screening cannot eliminate
  components meant only for frontier/harness-specific loop behavior** (screen those on the
  harness that supports them, not on qwen).

These were independently raised by codex; most are concrete and decision-grade-gating.
