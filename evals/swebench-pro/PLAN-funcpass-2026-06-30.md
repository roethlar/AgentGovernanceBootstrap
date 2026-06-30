# FuncPass governance experiment — plan v2 (2026-06-30)

Status: DRAFT v2 — codex-reviewed (round 1), fixes folded in. **Open: owner picks scope
A/B/C (§Scope) — that sets Stage-2 sizing. Nothing runs until approved.**

## Question
Can repo-governance **guidance** (completeness-steering prose) raise a coding agent's
**FuncPass** (rate of producing a functionally-correct fix for a real bug) on a *strong*
subscription harness — i.e. make it behave more like the stronger **Cursor** harness, which
the reference papers show produces *more complete* patches with the same model?
**FuncPass is the sole objective** (SecPass is a subset of FuncPass and security-steering can
reduce FuncPass — out of scope).

## Hard constraints (violating any = stop)
- Subscription/OAuth only. **NO API keys. No Cursor.**
- Guard time, money, AND power. No stage scales before a cheaper prior stage justifies it.
- FuncPass = FAIL_TO_PASS only (PASS_TO_PASS zeroed in the scored sample).

## What already exists (reuse; no rebuild)
SWE-bench Pro local on netwatch-01: images pulled, scorer validated, driver
`/home/michael/dev/SWE-bench_Pro-os/run_eval.py` smoke-proven end-to-end (anti-leak `.git`
re-init + `eval_base` tag, source-only capture, FuncPass scoring, neterr/quota
invalid-accounting, preflight PONG, grok token-persistence). Driver currently
`--harness qwen|grok|agy`; a `--harness claude-sonnet` path is a thin add (Claude-family code
exists from the validated `arms4_model.py` prototype).

## Non-negotiable principle (the thing all prior waste violated)
**A band must match the subject's capability.** Governance only moves FuncPass on instances
whose *ungoverned* rate is mid-range (~1/3–2/3). Floor (≈never) and ceiling (≈always) cells are
wasted. `band-ids.txt` is Opus's *failure* set → floor for everyone (proven: agy 8/10 floor,
90-cell run wasted). **No factorial on any band whose per-subject ungoverned rate is unmeasured.**

## Subject (codex S1: keep Sonnet primary; widen its pool, don't switch to Opus)
- **Primary: Claude Code + Sonnet 4.6** (subscription; the harness we want to improve). An
  Opus-calibrated band makes Sonnet under-yield likely — the fix is a **wider candidate pool**,
  not switching to Opus.
- Capability-confirm Opus 4.8, and cross-harness grok-build (Cursor-like, needs owner re-auth):
  only as Stage-3 follow-ups *if* the primary shows signal.
- qwen/agy: **wiring smoke tests only, never inference** (codex: Path B off-target — weak models
  floor and don't benefit from completion prose; agy showed this directly).

## Arms (codex H1: prose-only; no hook arm in the first experiment)
- `none` — no governance.
- `placebo` — topically-irrelevant prose, token-length-matched to the prose arm (code-style notes).
- `completeness-prose` — the intervention: *"Trace the failing behavior to every code path and
  input case it implies. Don't stop at the first plausible fix — check the other paths. After
  each edit, re-read your change and confirm the intended logic is still present."*

**No hook arm now.** A hook is only worth running if it enforces a *measurable invariant* with
reliable edit-event observation (codex H1). That is a separate, self-gated investigation
(its own wiring/instrumentation test proving it fires and changes behavior) — not bundled into
this factorial, where it would measure implementation noise.

## Anti-cheating (codex A1; proportionate)
- Git-history leak: closed (anti-leak re-init, proven).
- Memorization can be **detected, not prevented**. Minimum: (a) post-hoc **trajectory scan** of
  each passing cell for web/git-history retrieval (curl github/raw.githubusercontent, `git log`,
  etc.); (b) **patch-vs-gold similarity** flag; (c) adjudicate flagged cells (don't trust
  similarity alone — a memorized fix can be semantically identical but textually different).
- Network: SWE-bench Pro images have deps pre-baked, but the agent's *model* calls need egress
  (Sonnet via headroom LAN proxy). So an egress **allowlist** (permit only the LAN model proxy,
  deny public web) is feasible for the headroom-routed primary and is the right network control;
  a blanket block would kill the model and is wrong. Applied only if cheap to wire; otherwise
  post-hoc detection carries validity. Decide at Stage-2 wiring.

## Staged execution — each gate must pass or STOP
- **Stage 0 — design freeze (zero spend):** arm prose final (above); plan codex-reviewed (done,
  round 1) + owner-approved with a Scope pick.
- **Stage 1 — adaptive band-finding (codex P1/biggest-waste-fix):**
  1. **Pool rule (define before spending):** assemble ~40–60 candidates from the 92-instance
     complex pool (gold ≥3 files, P2P≥15, F2P≥3) spanning repos/difficulty — *not* only the
     known failures. Record the rule.
  2. **Cheap screen:** Sonnet `none`, **R=2** over the pool (~80–120 cells). Classify each:
     0/2 floor, 2/2 ceiling, 1/2 borderline.
  3. **Re-probe only borderline** candidates at +R (to R=4–5 total) to confirm true mid-band
     (rate strictly between floor/ceiling). Adaptive — don't pay R=3+ for obvious floor/ceiling.
  - **GATE:** require a **confirmed mid-band mass** sufficient for the chosen Scope's power
    (below). If too few mid-band instances exist, STOP — widen pool once, else the question
    isn't answerable on this substrate for this subject without more work.
- **Stage 2 — prose factorial (only if Stage-1 gate passes):** Sonnet, arms
  none/placebo/completeness-prose, within-instance paired, on the confirmed mid-band. Size = the
  Scope pick. Output: paired FuncPass deltas (prose−none, prose−placebo) + variance.
- **Stage 3 — confirm/extend (only if Stage-2 signal):** replicate headline delta on Opus and/or
  grok (re-auth) to speak to the cross-harness gap.

## Scope — OWNER PICK (sets Stage-2 size; codex power-fix)
A credibly powered +15pp test needs ~**10–20 mid-band instances × R≥5 × 3 arms** (≈150–300
metered Sonnet cells) on top of the Stage-1 probe (~80–120 cells). There is no cheap
decision-grade path. Pick one:
- **A — decision-grade:** fully fund the powered factorial (gated by Stage-1). Real answer.
- **B — directional pilot:** smaller prose-only run on whatever mid-band is found; explicitly
  **inconclusive** — only estimates effect + variance to justify a later A-sized run.
- **C — stop:** not worth the spend.

## Cost ceilings (committed)
- Stage 1 ≤ pool size × (2 screen + ≤3 re-probe borderline) cells, one subject.
- Stage 2 ≤ Scope-defined cell budget, one subject, announced before launch.
- No stage without the prior gate; no batch without a 1-cell smoke of any changed wiring.
- Serialize same-provider; bound every batch; weak-model/local for wiring checks only.

## Non-goals
No Cursor, no API keys, no SecPass target, no runs on unvalidated bands, no hook arm until a
measurable invariant is designed and separately gated, no SusVibes (it measured SecPass).

## Review trail
- codex round-1 (read-only): verdict "not safe as-is" → must-fix (1) drop/strictly-define hook,
  (2) replace R=3-over-20 with adaptive wider band-finding, (3) set real Stage-2 power threshold.
  All folded into v2 above. Re-review of v2 optional before launch.

## 2026-06-30 — owner direction: this is PRODUCT work, not just measurement (do not lose)

The eval now feeds the product, not only measures it. The completeness-steering prose — and,
later, a general completion-enforcement hook — are intended to become part of the shipped
governance product.

Demonstration that earned this (free, local qwen via `run_fixture.py` + `ollama_driver`, new
fixture `evals/fixtures/py_vault_twopath`: a two-path `read`/`remove` path-escape bug where the
prompt+visible test name only `read`; R=3 per arm):
- `none`: 0/3 fix the second method (hidden test) — incomplete patch every time.
- `hooks-only` (`evals/governance_profiles/hooks-only`, gate+guard, NO prose): 0/3 — hooks
  *fire* (`hooks_fired=True`) but don't address completeness (gate enforces the visible test,
  which the `read` fix already satisfies; guard only blocks test edits).
- `completeness-prose` (`evals/governance_profiles/completeness-prose`, NO hooks, never names
  `remove`/`Vault`): 3/3 — complete fix every time. **INVALID as evidence (2026-06-30):** this
  prose encodes the trap's solution *procedure* ("fix every sibling method that handles the same
  input the same way") — answer-encoding for a fixture built to need exactly that. It says nothing
  about whether *generalized* guidance helps.
- ⇒ **CORRECTED (2026-06-30): this does NOT show generalized guidance works** — see the INVALID
  note above; the prose used was answer-encoding for this fixture. The product candidate is the
  *generalized* prose `evals/governance_profiles/completeness-general` (no answer-encoding), whose
  efficacy is UNESTABLISHED: the only valid run (grok, 9 real bugs, with/without) was null with no
  mechanism evidence, and qwen re-validation with the generalized prose is underway. The eval
  gate/guard hooks are measurement instrumentation, not the product. (Existing
  fixtures `py_boxes_ceildiv`/`py_page_size`/`ts_interval_merge`/`go_topk_nomutate`/
  `rs_redirect_guard` are all ceiling for qwen — too easy — which is why the trap had to be built.)

General completion-gate hook — discovery is NOT the blocker (owner): the product already runs
discovery (`tools/discover.py`) during bootstrap; tighten it to extract the per-repo test
command/runner the hook needs, instead of re-discovering heuristically at hook time. The eval's
harness-injected `AGB_VERIFY_CMD` is the throwaway stand-in for that discovered detail.

Parallel workstreams (owner — do NOT duplicate or build here): (1) integrating these findings
into the total product; (2) making the existing guidance more token-efficient (current AGENTS.md
is too large — same motivation as the `test_ground/AGENTS_*.md` compaction attempts, which are
scratch/trash and must NOT be sent to any model). This eval workstream stays on
measurement/demonstration; it does not build the product hook or the compaction.
