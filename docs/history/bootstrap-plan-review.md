# Review: Portable Agent-Governance Bootstrap Plan

Review of `bootstrap-plan.md` on its own merit, with suggested refinements.
Reviewer: Claude (Opus 4.8). Date: 2026-06-08.

## What's strong

The plan is well above average. Three ideas do real work:

- **Evidence classes** — separating `observed_from_code/tests/ci/git` from
  `doc_claim_unvalidated` is the single best decision here. It directly attacks
  the most common failure mode: agents trusting stale READMEs and old AGENTS
  files.
- **Git custody requirement** — catching the case where ignored/local-only
  files quietly become durable authority is a subtle, real problem most people
  miss.
- **Review packet before durable writes** — human-in-the-loop at the right
  moment (before rules calcify), not after.

## Refinement opportunities

Ordered by how much they'd change outcomes.

### High impact

**1. No lifecycle/staleness story — yet "minimizing drift" is the stated goal.**
The plan generates artifacts once and stops. But `repo-map.md` and the
playbooks start rotting the moment the next commit lands. Add:
- A staleness stamp on every generated artifact:
  `validated_against: <commit-sha> on <date>`.
- A re-bootstrap / update trigger (e.g. "if HEAD has moved N commits or touched
  build/CI/test config since validation, re-run discovery").
- This converts the bootstrap from a one-shot into a maintainable process,
  which is what the purpose statement actually promises.

**2. Evidence classes are defined but have no precedence or promotion rules.**
What happens when `doc_claim_unvalidated` contradicts `observed_from_code`? It's
implied code wins, but never stated. Add two explicit rules:
- **Precedence:** `observed_* > human_confirmed > inferred >
  doc_claim_unvalidated` (or put `human_confirmed` on top — your call, but state
  it).
- **Promotion gate:** nothing classified `inferred`, `doc_claim_unvalidated`, or
  `question` may become a *hard rule* in AGENTS.md until promoted to `observed_*`
  or `human_confirmed`. Right now the classes are diagnostic but don't constrain
  what gets written.

**3. The verification entry point is asserted, not derived — and that's where
agents get burned.** `checks.ps1/.sh` is listed as an output, but the plan never
says *how* the real checks are discovered or that the generated commands
actually run. Specify:
- Checks are **composed only from observed commands** (CI workflow steps,
  package/build scripts, test runner configs) — never invented.
- Where CI and docs disagree on "how to test," CI wins (it's
  `observed_from_ci`).
- The generated checks file must be **executed once and confirmed to run**
  before it's written as authority. An agent that trusts a checks script that
  doesn't exist is worse off than one with none.

**4. No baseline-health capture.** Before checks can be trusted, you need to
know the repo's *current* state. If `main` already has 3 failing tests, a fresh
agent can't distinguish its own regression from pre-existing breakage. Add a
discovery step: run the checks on a clean checkout and record the baseline
(green / known-failures). Cheap, and prevents a whole category of false
"I broke it" / "it was already broken" confusion.

### Medium impact

**5. Latent tension between the plan and its own artifact manifest.** The Git
Custody Requirement and Success Criteria both insist durable guidance must be
*tracked in git, in the repo*. But the manifest deliberately stored artifacts
**outside** the example repo (`D:\source\AgentGovernanceBootstrap`, repo
untouched). That's correct for a *dry-run/pilot* — but it means the artifacts
are themselves "local-only," exactly the anti-pattern the plan warns against.
Make this explicit in Pilot Flow step 4: external storage is a pilot/preview
mode; the end state for any real adoption is in-repo + tracked, or the guidance
has no more authority than the unvalidated docs it replaces.

**6. Idempotency / init-vs-update mode is undefined.** What happens when you run
this on a repo that already has `AGENTS.md` and `.agents/`? Overwrite? Merge?
Diff for review? Without an update mode, the second run is either destructive or
refuses. Define: **init** (none present) vs **update** (present → produce a diff
into the review packet, never silently overwrite human edits).

**7. Secrets guard during discovery.** The plan explicitly reads
ignored/local-only files — which is exactly where `.env`, credentials, and
tokens live. Add a hard rule: discovery classifies the *location and existence*
of such files, never copies their *values* into any artifact; redact by default.
One leaked secret in a generated `repo-map.md` undoes the whole "durable,
tracked in git" benefit.

**8. Monorepo / multi-project scoping is assumed away.** The plan reads as
"one repo = one architecture = one set of checks." Many repos have multiple
apps/packages with different build and test commands. Discovery should detect
project boundaries; playbooks and checks may need to be per-project rather than
repo-global.

### Lower impact / polish

**9. AGENTS.md has no shape — risk it becomes a dumping ground.** It's loaded
into every agent's context, so token budget matters. Recommend: AGENTS.md stays
short and stable (mission + pointers to playbooks + the checks entry point),
while volatile detail lives in `repo-map.md`. Otherwise the file most likely to
be read is also the one most likely to be stale.

**10. Tool adapters should be pointers, not copies.** "Generate Claude commands
/ Codex prompts" risks content diverging from AGENTS.md over time. State that
AGENTS.md is the single source and adapters reference it rather than duplicating
rules. (`CLAUDE.md` can simply point to `AGENTS.md`.)

**11. The bootstrap has no acceptance test for *itself*.** Success criteria are
all qualitative. Step 6 ("test with a realistic request") would be far stronger
with: a held-out task the bootstrap author didn't design the artifacts around,
run by a genuinely fresh agent (no memory of the bootstrap), with a defined
pass/fail rubric. Otherwise you're grading your own homework.

**12. Generated hooks need to be opt-in and reversible.** Installing hooks
mutates every contributor's environment. Should require explicit human approval
and a documented uninstall.

## One-line take

The plan's *epistemics* (evidence classes, custody, review gate) are excellent;
its *operational lifecycle* (staleness, baseline, idempotency,
derived-and-validated checks) is the thin spot. The highest-leverage additions
are **#1 (staleness stamps + re-bootstrap)**, **#2 (precedence + promotion
rules)**, and **#3 (checks derived from CI and proven to run)** — those three
turn it from a clever one-shot snapshot into a process that actually holds drift
down over time.
