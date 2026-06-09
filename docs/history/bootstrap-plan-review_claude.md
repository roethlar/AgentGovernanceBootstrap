# Review: bootstrap-plan.v2.md

**Reviewer:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Reviewed at commit:** `be45d33`

## Verdict

v2 is a strong, epistemically sound **specification**. The conceptual core — separating stable principles from repo facts, the hybrid script/LLM division, and the plain-language fact-refresh-vs-rule-change asymmetry — is genuinely good and addresses agent drift at the right layer. The prior reviews' 12 points were absorbed well.

The weak spot has moved. v1's gaps were *conceptual* (no lifecycle, no precedence). v2's gaps are *operational*: the plan now describes a tool (`bootstrap-agents.ps1`, a grader, secret-safe discovery) that **does not exist yet**, and several of the hardest-to-get-right mechanics are asserted as mandates without a mechanism. The riskiest parts of any such system — secret redaction, overwrite safety, the grader — are exactly the parts left unspecified.

## What v2 adds over v1 (and does well)

- **Hybrid script/LLM model** with an explicit "neither half is sufficient" framing — correct architecture, clearly reasoned.
- **Stable principles vs. repo facts** — the single best addition. It lets repo facts go stale without ever silently mutating behavior rules.
- **Fact refresh vs. rule change**, with the security-aware asymmetry: *fact changed → update silently; verification weakened or safety boundary moved → always ask the human.* The "tests removed from CI" example is exactly the right paranoia.
- **Two-tier testing** (current-checkout + clean-local-copy). The clean-copy test catches local-only contamination — a real, commonly-missed failure mode.
- **Command-driven modes** and the **generated-file header** for non-pointer adapters (resolving Gemini's no-pointer concern).

## Issues, by severity

### High

**H1 — The grader is referenced but undefined, and the rubric isn't machine-gradable.**
The Current-Checkout Test invokes `.agents\grade-agent-run.ps1`, but that script appears **nowhere** in "Generated Artifacts" and is never specified. Worse, the pass/fail rubric is inherently subjective ("finds the correct playbook," "avoids unvalidated docs as authority," "asks only necessary questions"). A `.ps1` cannot judge those. Either the grader is an LLM-in-the-loop (not stated, and then it's judgment work, not deterministic) or a human checklist. Decide which, and either list the grader as a generated artifact with a defined contract or drop the scripted-grading framing in favor of a human rubric.

**H2 — Secret-safe discovery is a mandate with no mechanism.**
The plan forbids copying secrets into artifacts but never says *how*. In the hybrid model, "read relevant files" is assigned to the LLM with no gating — so the deterministic half never decides what the LLM is allowed to read, and an LLM summary of a config file can leak values into `repo-map.md`. Secret-safety should live partly in the **script**: a deny-list (`.env*`, `*.pem`, `*.key`, credential-like names), record *existence and path only*, and never hand raw contents of flagged files to the LLM. As written it's a hope, not a guard.

**H3 — `apply` has no defined init-vs-existing or partial-failure behavior.**
v1's clean `init`/`update` split was replaced by `discover`/`apply`/`update`. But what does `apply` do when artifacts already exist — overwrite, refuse, or diff? "Prevent accidental overwrites" is listed as a script duty but `apply`'s description doesn't state the rule. And there's no atomicity story: if `apply` writes 8 artifacts and fails on the 5th, the repo is left half-written and half-tracked. Specify: apply refuses (or routes to `update`) when durable guidance exists, and writes atomically or rolls back on failure.

### Medium

**M1 — Clean-local-copy "from tracked files" silently breaks git-dependent features.**
`test-clean` says it "can create a local copy **from tracked files** or use a local git clone" — treating these as interchangeable. They aren't. A file-copy has no `.git`, so: the checks script's git-based outdated-facts warning fails, "record git status and current commit" fails, and any git-using playbook step fails — in exactly the environment meant to validate the guidance. Prefer `git clone <local-path>` to preserve fidelity; reserve file-copy only for repos where it demonstrably doesn't matter, and say so.

**M2 — Staleness logic is described in three places and can drift.**
"Outdated Repo Facts Triggers," "Fact Refresh Versus Rule Change," and the verification entry point's warning all encode overlapping freshness rules. Three encodings of one mechanism will diverge. Name one canonical definition (the checks script's computation) and have the prose sections reference it.

**M3 — The outdated-facts check assumes git history that the test env may strip.**
It computes "CI/build files changed since the validation commit." This needs git history, an accurate stamp, and a normal (non-shallow, attached) checkout. Combined with M1, the feature can't run in a file-copy clean test. Note the preconditions and degrade gracefully (e.g., "cannot determine freshness — git history unavailable") rather than silently passing.

**M4 — Hardcoded harness baseline is presumptuous and opt-out is undefined.**
Generating adapters for Claude Code, Codex, Antigravity, Aider, and Cursor *by default for every repo* produces five files of noise for a single-tool team, and the list will age. "unless the repo explicitly opts out" — but *how* does a repo opt out before any guidance exists? Define the opt-out (a config key? a discover-time question?). Also flag: Antigravity CLI is a notably less-standard entry than the other four.

### Lower / polish

- **L1 — Adapter authorship boundary is ambiguous.** "Propose generated harness adapters" sits under LLM judgment, but adapters are "derived outputs" with a `regenerate` command — implying deterministic templating. Drift-free adapters need the *body* generated deterministically (script), with the LLM only deciding *whether* one is needed. State this.
- **L2 — CI is ranked just below human, but a CI yaml is partly a claim.** A CI file can describe a disabled/always-skipped job. "Derived Verification → execute once" mitigates this for checks, but the precedence table still treats unexecuted CI commands as near-top authority. Consider: CI *config* is `observed_from_ci` that something exists; CI *commands* are claims until executed.
- **L3 — No discovery budget for large monorepos.** AGENTS.md token budget is handled, but "read relevant files" + per-project playbooks has no size bound. A big monorepo could blow up discovery cost / playbook count. Add a scoping/budget note.
- **L4 — Self-referential custody gap (carried from v0 review #5).** This plan's own artifacts still live outside the target repo per `artifact-manifest.md`, untracked-in-target — the exact anti-pattern it warns against. Legitimate under "preview mode," but worth an explicit line that this repo *is* the preview and the script itself remains unimplemented.

## The three highest-leverage fixes

1. **H2 — operationalize secret-safety in the deterministic script** (deny-list + path-only recording + never feed flagged contents to the LLM). This is the one failure that's irreversible once it lands in tracked git.
2. **H1 — resolve the grader contradiction** (LLM-grader with a defined contract, or an honest human rubric — not a `.ps1` pretending to judge subjective criteria).
3. **H3 — define `apply` semantics and atomicity** (refuse-or-diff on existing guidance; write atomically or roll back).

## One-line take

The *thinking* in v2 is excellent and largely done; the *engineering contract* is the gap. Before this becomes a script, nail down secret redaction, the grader, and `apply`'s write semantics — everything else is refinement.
