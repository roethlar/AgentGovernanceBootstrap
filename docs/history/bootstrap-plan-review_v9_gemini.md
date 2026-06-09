# Review: bootstrap-plan.v9.md

**Reviewer:** Gemini 3.5 Flash (High) · **Date:** 2026-06-08 · **Reviewed at commit:** (working tree / latest)
**Focus:** Mechanical validity, edge-case mitigation, and developer experience (DX) of the updated `.bootstrap-tmp/` handoff workflow.

## Verdict: Excellent resolution of v8's major gotchas. The design is now highly functional, secure, and ready for pilot implementation, with only minor operational clarifications remaining.

Version 9 of the bootstrap plan is a major refinement. It directly and cleanly resolves all major vulnerabilities raised in previous reviews:
1. **Naming:** Renaming the directory to `.bootstrap-tmp/` eliminates the risk of cognitive naming confusion with the durable `.agents/` folder.
2. **First Run:** The introduction of `.bootstrap-tmp/START-HERE.md` solves the "chicken-and-egg" bootstrap problem.
3. **Git Leakage:** The use of `.bootstrap-tmp/.gitignore` containing `*` prevents accidental commits of scratch data without making root-level `.gitignore` modifications.
4. **Stale Handoffs:** The freshness check (matching HEAD commit) prevents stale configurations from hijacking sessions.
5. **Prompt Injection:** Explicitly classifying repo-derived paths as inert data rather than agent instructions closes a key vulnerability.

Below are minor operational details, edge cases, and design suggestions to consider before freezing the spec for implementation.

---

### 1. (HIGH-MED) The Template / Boilerplate Delivery Gap

**The Issue:**
On a first bootstrap, `AGENTS.md` does not exist. The agent is directed via `.bootstrap-tmp/START-HERE.md` to:
> "Draft proposed durable agent guidance, including `AGENTS.md`, repo map, playbooks, and artifact manifest."

However, if the agent is a fresh instance running in a new repository, it does not have access to the bootstrap framework spec itself (`bootstrap-plan.v9.md`). It does not know:
- The required shape and fields of the `AGENTS.md` file (e.g., the exact wording of the "Bootstrap Handoff" and "Minimal Startup" rules).
- The exact schemas for `.agents/repo-map.json` or `.agents/artifact-manifest.json`.

Without concrete templates or guidance on the expected formatting, a fresh agent will have to guess (or hallucinate) the structure of these files, leading to inconsistent outputs that fail Layer 1 grading.

**Recommendation:**
- The discovery helper should write a set of standard templates to the scratch directory (e.g., `.bootstrap-tmp/templates/AGENTS.template.md`, `.agents/repo-map.template.json`, etc.) or embed the required boilerplates directly within `.bootstrap-tmp/bootstrap-review-packet.md`.
- `START-HERE.md` should explicitly direct the agent to copy or adapt these templates.

---

### 2. (MED) Monorepo Subdirectory Boundaries

**The Issue:**
The plan notes that "For monorepos, repo maps, checks, and playbooks may be per-project rather than repo-global."
If a user runs discovery on a specific project directory in a monorepo:
- Where is `.bootstrap-tmp/` written? (At the subdirectory level, or the monorepo root?)
- If it is written to a subdirectory, how does the Git-based metadata collection (e.g. `git status`, HEAD commit) resolve?
- Git commands run from a subdirectory will report paths relative to the Git repository root unless mapped properly, which can corrupt the discovery manifest's path mappings.

**Recommendation:**
- The plan should clarify that the discovery helper always operates relative to the Git root directory, even when scoping discovery to a specific monorepo subdirectory.
- If a project-level `.bootstrap-tmp/` is used, the manifest path mappings must be explicitly normalized to the repository root.

---

### 3. (MED) Co-existence and Precedence of Harness Adapters

**The Issue:**
The plan specifies generating optional harness adapters (e.g., `.cursorrules`, `.aider.conf.yml`) to ensure harnesses point back to `AGENTS.md`.
However, developers often have their own global or pre-existing repository-level configuration files for these harnesses:
- If a developer has a custom `.cursorrules` with project-specific development tips, does the bootstrap overwrite it?
- If it backs it up and replaces it, this might disrupt the developer's normal workflow.

**Recommendation:**
- Specify that the discovery helper should inspect existing harness config files first.
- If a harness config file already exists, the helper should append its pointers/instructions to the existing file rather than overwriting it, or warn the human in the review packet about the conflict and propose a merged version.

---

### 4. (LOW) Agent Git Tool Access Assumption

**The Issue:**
Step 3 of the `AGENTS.md` Bootstrap Handoff Rule states: "Check the manifest commit against current `HEAD`."
This assumes the agent harness provides the agent with access to a terminal tool to execute `git rev-parse HEAD`, or a read-file tool capable of inspecting `.git/refs/heads/`.
While most developer agents have terminal access, some locked-down or web-based agents may not.

**Recommendation:**
- Add a fallback instruction: if the agent cannot query Git directly to get the current HEAD commit hash, it should print the manifest's commit hash and ask the human to confirm if it matches the current checkout.

---

### 5. (LOW) The Self-Ignore Pattern Syntax

**The Issue:**
In the `.bootstrap-tmp/.gitignore` contents:
```gitignore
*
!.gitignore
```
While this correctly ignores everything in the folder except the `.gitignore` itself, some Git configurations or older Git versions can have issues with directory matching if the parent directory itself isn't tracked.
Since `.bootstrap-tmp/` is ignored, Git will not track the directory at all, which is correct.

**Recommendation:**
- No change needed, but ensure the helper implementation tests this pattern against common Git versions to verify `.bootstrap-tmp/` never shows up as untracked under `git status`.

---

## Conclusion

With the changes in v9, the governance bootstrap plan has reached a highly mature state. The operational risks from v8 are mitigated, and the boundary between transient setup data and durable repository configuration is cleanly maintained. The project is ready to begin implementing the first discovery helper prototype.
