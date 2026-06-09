 # Review: Portable Agent-Governance Bootstrap Plan

-Review of `bootstrap-plan.md` on its own merit, with suggested refinements.
-Reviewer: Claude (Opus 4.8). Date: 2026-06-08.
+Review of `bootstrap-plan.md` (v0) and `bootstrap-plan.v1.md`.
+Reviewer: Claude (Expert Software Developer). Date: 2026-06-08.

-## What's strong
+---

-The plan is well above average. Three ideas do real work:
+## Part 1: Original Review of `bootstrap-plan.v0.md`

-- **Evidence classes** — separating `observed_from_code/tests/ci/git` from
-  `doc_claim_unvalidated` is the single best decision here. It directly attacks
-  the most common failure mode: agents trusting stale READMEs and old AGENTS
-  files.
-- **Git custody requirement** — catching the case where ignored/local-only
-  files quietly become durable authority is a subtle, real problem most people
-  miss.
   miss.
 - **Review packet before durable writes** — human-in-the-loop at the right
   moment (before rules calcify), not after.

-## Refinement opportunities
+### Refinement opportunities

 Ordered by how much they'd change outcomes.

-### High impact
+#### High impact

 **1. No lifecycle/staleness story — yet "minimizing drift" is the stated goal.**
 The plan generates artifacts once and stops. But `repo-map.md` and the
 playbooks start rotting the moment the next commit lands. Add:
 - A staleness stamp on every generated artifact:
@@ -33,5 +37,6 @@
 - This converts the bootstrap from a one-shot into a maintainable process,
 discovery step: run the checks on a clean checkout and record the baseline
 (green / known-failures). Cheap, and prevents a whole category of false
 "I broke it" / "it was already broken" confusion.

-### Medium impact
+#### Medium impact

 **5. Latent tension between the plan and its own artifact manifest.** The Git
 Custody Requirement and Success Criteria both insist durable guidance must be
 *tracked in git, in the repo*. But the manifest deliberately stored artifacts
 **outside** the example repo (`D:\source\AgentGovernanceBootstrap`, repo
@@ -74,5 +78,6 @@
 Make this explicit in Pilot Flow step 4: external storage is a pilot/preview
 apps/packages with different build and test commands. Discovery should detect
 project boundaries; playbooks and checks may need to be per-project rather than
 repo-global.

-### Lower impact / polish
+#### Lower impact / polish

 **9. AGENTS.md has no shape — risk it becomes a dumping ground.** It's loaded
 into every agent's context, so token budget matters. Recommend: AGENTS.md stays
 short and stable (mission + pointers to playbooks + the checks entry point),
 while volatile detail lives in `repo-map.md`. Otherwise the file most likely to
@@ -107,5 +111,6 @@
 AGENTS.md is the single source and adapters reference it rather than duplicating
 **12. Generated hooks need to be opt-in and reversible.** Installing hooks
 mutates every contributor's environment. Should require explicit human approval
 and a documented uninstall.

-## One-line take
+---

+## Part 2: Review of `bootstrap-plan.v1.md` (The Updated Plan)
+
+The updated plan (`bootstrap-plan.v1.md`) is an exceptional, production-grade specification. It systematically addresses all 12 refinement opportunities identified in the
initial review.
+
+### How the Refinements Were Addressed
+
+1. **Staleness & Re-Bootstrap Triggers (High Impact #1):** Fully addressed. Added a dedicated section defining clear triggers (commit thresholds, CI/build changes, manual edits)
and requiring a staleness stamp on all artifacts.
+2. **Evidence Precedence & Promotion (High Impact #2):** Fully addressed. Added a clear 8-tier precedence hierarchy (with `human_confirmed` at the top) and strict promotion
rules preventing unvalidated claims from becoming hard rules.
+3. **Derived Verification (High Impact #3):** Fully addressed. Added a "Derived Verification" section ensuring checks are composed only from observed commands (CI/package
scripts) and executed once to prove viability before writing.
+4. **Baseline-Health Capture (High Impact #4):** Fully addressed. Added baseline health capture (current commit, pass/fail status, known failures) to the discovery procedure and
review packet.
+5. **Pilot Flow & Git Custody (Medium Impact #5):** Fully addressed. Clarified the distinction between preview/pilot mode (external storage) and real adoption (in-repo and
tracked).
+6. **Operating Modes (Medium Impact #6):** Fully addressed. Defined explicit `init` and `update` modes to prevent destructive overwrites of human-reviewed guidance.
+7. **Secrets Guard (Medium Impact #7):** Fully addressed. Mandated secret-safe discovery, explicitly forbidding copying of credentials, tokens, or environment values.
+8. **Monorepo Scoping (Medium Impact #8):** Fully addressed. Added discovery of project boundaries and allowed per-project repo maps, checks, and playbooks.
+9. **AGENTS.md Shape (Lower Impact #9):** Fully addressed. Defined a short, stable structure for `AGENTS.md` to preserve token budgets, pushing volatile details to
`.agents/repo-map.md`.
+10. **Tool Adapters as Pointers (Lower Impact #10):** Fully addressed. Specified that tool adapters should point to `AGENTS.md` and tracked files rather than duplicating rules.
+11. **Bootstrap Acceptance Test (Lower Impact #11):** Fully addressed. Added a formal "Bootstrap Acceptance Test" section with a clear pass/fail rubric using a held-out task and
a fresh agent context.
+12. **Opt-in Hooks (Lower Impact #12):** Fully addressed. Explicitly stated that hook installation must be opt-in, reversible, and approved by a human.
+
+---
+
+### Remaining Nuances & New Recommendations for v1
+
+While `bootstrap-plan.v1.md` is highly robust, a few operational nuances deserve attention as this plan moves from specification to implementation:
+
+#### 1. Tool Adapter Limitations (The "No-Pointer" Problem)
+* **The Issue:** The plan states that "Tool adapters should point to `AGENTS.md` and tracked `.agents/` files rather than duplicating large rule sets." However, many popular
developer tools (e.g., Cursor's `.cursorrules`, Copilot's custom instructions, or certain CI/CD agent configurations) do not natively support file inclusion, symlinks, or
pointers.
+* **Recommendation:** Clarify that when a tool adapter cannot natively point to `AGENTS.md`, the bootstrap tool should generate/compile the adapter file automatically during
`init` or `update` modes, treating the adapter as a *generated* file tracked in git, with a header warning developers not to edit it directly.
+
+#### 2. Defining the "Fresh Agent" Context
+* **The Issue:** The acceptance test relies on a "fresh agent context." In practice, LLM agents often carry latent context from system prompts, IDE-level indexing, or previous
chat history.
+* **Recommendation:** Explicitly define "fresh agent context" as:
+  1. A completely new chat session with no prior conversation history.
+  2. No custom instructions or system prompt overrides active other than those loaded directly from the repository's `AGENTS.md`.
+  3. A cleared workspace cache (or a clean git clone) to ensure no local-only uncommitted files from previous runs interfere.
+#### 2. Defining the "Fresh Agent" Context
+* **The Issue:** The acceptance test relies on a "fresh agent context." In practice, LLM agents often carry latent context from system prompts, IDE-level indexing, or previous
chat history.
+* **Recommendation:** Explicitly define "fresh agent context" as:
+  1. A completely new chat session with no prior conversation history.
+  2. No custom instructions or system prompt overrides active other than those loaded directly from the repository's `AGENTS.md`.
+  3. A cleared workspace cache (or a clean git clone) to ensure no local-only uncommitted files from previous runs interfere.
+
+#### 3. Automating the Staleness Check
+* **The Issue:** The plan lists excellent triggers for staleness (e.g., "HEAD differs from the artifact staleness stamp by a human-defined commit threshold"). However, if
checking this is manual, agents or humans will inevitably forget to do it.
+* **Recommendation:** The generated verification entry point (`.agents/checks.sh` or `.agents/checks.ps1`) should automatically perform a quick git diff/log check against the
staleness stamp commit SHA. If the threshold is exceeded or build files have changed, the script should print a prominent warning: `WARNING: Agent guidance artifacts may be
stale. Run bootstrap in update mode.`
+
+---
+
+### Final Verdict
+
+`bootstrap-plan.v1.md` is **excellent**. It is one of the most comprehensive and epistemically sound agent-governance frameworks available. Implementing this plan will
drastically reduce agent drift and ensure high-fidelity, safe, and reproducible agent contributions.


