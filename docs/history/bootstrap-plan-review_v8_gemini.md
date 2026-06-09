# Review: bootstrap-plan.v8.md

**Reviewer:** Gemini 3.5 Flash (High) · **Date:** 2026-06-08 · **Reviewed at commit:** (working tree / latest)
**Focus:** Mechanical consistency, security/data leak boundaries, and operational developer experience (DX) of the `.agent-bootstrap/` handoff mechanism.

## Verdict: Strong operational advance in v8, but contains several structural "chicken-and-egg" and lifecycle failure modes that could disrupt developer workflows.

Version 8 introduces the `.agent-bootstrap/` handoff directory, which provides a concrete interface between an external discovery tool and the in-repo agent. This is a significant improvement over the more abstract/prose-heavy descriptions in v6 and v7. However, the mechanism introduces new operational vulnerabilities, edge cases around the first bootstrap, and name collision risks.

---

### 1. (CRITICAL) The First-Bootstrap "Chicken-and-Egg" Problem

**The Issue:** 
The plan relies on the "Bootstrap Handoff" rule inside `AGENTS.md` to instruct the agent to read `.agent-bootstrap/` and follow the bootstrap process.
However, in a fresh, un-bootstrapped repository, **`AGENTS.md` does not yet exist**. It is one of the primary artifacts that the bootstrap process is supposed to generate.
When a user runs discovery and starts a fresh agent in the repository:
1. The agent will not find `AGENTS.md` (or any other governance instructions).
2. The agent will proceed under its default system instructions, completely unaware of the temporary `.agent-bootstrap/` directory or the workflow it should execute.
3. The user will be forced to manually copy/paste the bootstrap workflow or kickoff prompt, defeating the primary ergonomic benefit of the handoff folder.

**Recommendation:**
- Either the external discovery tool must print a specific kickoff prompt that the user copy-pastes to start the agent, OR
- The external discovery helper should write a temporary, self-contained kickoff instruction file directly inside `.agent-bootstrap/` (e.g., `.agent-bootstrap/START_HERE.md` or `.agent-bootstrap/kickoff.txt`) that the user can feed to the agent, OR
- The developer instructions should explicitly state that on a first run, the user must explicitly direct the agent to read `.agent-bootstrap/`.

---

### 2. (HIGH) The Stale Handoff Hijacking Risk

**The Issue:**
Under the "Bootstrap Handoff" rule, the agent is told: "If `.agent-bootstrap/` exists, treat it as temporary bootstrap input. 1. Read `.agent-bootstrap/bootstrap-review-packet.md`...".
However, humans frequently forget to clean up temporary directories. If `.agent-bootstrap/` is left in the repository:
1. In a subsequent, unrelated session where the developer wants to perform standard work (e.g., fixing a bug), the agent will boot up, see that `.agent-bootstrap/` exists, and immediately enter "Bootstrap/Update" mode.
2. The agent will read stale discovery data (which might be weeks or months old) and prioritize it over the developer's actual task.
3. This creates a silent hijacking of the agent's attention and risks introducing regressions if the agent updates durable rules based on outdated manifests.

**Recommendation:**
- The handoff rule in `AGENTS.md` must include a freshness check. The agent should compare the `validated_against` commit in the manifest against the current `HEAD` commit.
- If they do not match, or if the diff contains changes to key project files, the agent must refuse to automatically run the handoff and warn the user that the bootstrap scratchpad is stale.
- Add a strict timeout or commit-count threshold to `.agent-bootstrap/` validity.

---

### 3. (HIGH) Silent Git Leaks and `.gitignore` Modification

**The Issue:**
The plan states that `.agent-bootstrap/` "must be ignored by git." However, it does not specify *how* this ignore rule is established.
- If the external discovery helper modifies the root `.gitignore` to add `.agent-bootstrap/`, it violates the core principle that discovery is a read-only/no-durable-change operation.
- If the helper does *not* modify `.gitignore`, the temporary directory remains untracked but not ignored. A developer running `git add .` or `git add -A` will accidentally commit the temporary discovery manifest, review packets, and run logs—introducing untracked local process state into the repo (the exact issue the plan aims to solve).

**Recommendation:**
- The external discovery helper must automatically write a `.gitignore` file inside the `.agent-bootstrap/` directory itself (i.e., `.agent-bootstrap/.gitignore`) containing `*`. 
- This ensures the directory ignores its own contents without modifying the repository's root `.gitignore` file or requiring manual human setup.

---

### 4. (HIGH-MED) Naming Collision / Cognitive Load between `.agents/` and `.agent-bootstrap/`

**The Issue:**
The repository will contain two directories with very similar names:
- `.agents/` (Durable, tracked, authoritative)
- `.agent-bootstrap/` (Temporary, ignored, scratchpad)
Both human developers and LLM agents are highly susceptible to path confusion when names are this similar.
- An agent might accidentally write durable playbooks to `.agent-bootstrap/` where they are git-ignored and lost.
- An agent might write temporary test outputs or run logs to `.agents/` where they get committed as noise.
- A human might delete `.agents/` by mistake when trying to clean up `.agent-bootstrap/`.

**Recommendation:**
- Rename the temporary handoff directory to something that clearly conveys its disposable and external nature, such as `.agent-setup-scratch/`, `.agent-bootstrap-temp/`, or `.agent-handoff/`. 
- Ensure the name contains a clear "temp" or "scratch" keyword to prevent cognitive slip.

---

### 5. (MED) Harness Auto-Loading Dependency

**The Issue:**
Both the "Bootstrap Handoff" and "Normal Startup" rules rely on the assumption that the agent harness automatically reads and respects `AGENTS.md` at session start.
In reality, baseline harnesses (Claude Code, Cursor, Aider, Codex CLI) have different discovery mechanisms:
- Aider looks for `.aider.conf.yml` or standard prompt files.
- Cursor relies on system prompts or `.cursorrules`.
- Claude Code uses its own startup conventions.
If a harness does not natively load `AGENTS.md` on startup, the entire handoff and startup status rituals will be bypassed unless the adapter forces the insertion of these rules.

**Recommendation:**
- Explicitly state that for harnesses lacking native `AGENTS.md` auto-loading, the generated harness adapter MUST inject a startup instruction pointing the agent to `AGENTS.md`.

---

### 6. (MED) Deterministic Grader Output Verification

**The Issue:**
The plan requires the agent to write a YAML frontmatter to `.agents/test-results/current-run.md` containing `declared_scope` and `verification` status.
If the agent fails to write this frontmatter, or writes it with invalid YAML syntax, Layer 1 of the grader reports `scope unknown` and fails.
Because LLMs frequently make minor syntax errors in structured blocks (especially when mixing Markdown and YAML), a deterministic grader requiring strict YAML formatting will reject many valid runs due to minor formatting discrepancies.

**Recommendation:**
- The Layer 1 grader should use a resilient parser that can extract fields even if the frontmatter has minor syntax issues (e.g., missing quotes or spacing errors).
- Alternatively, provide a helper tool or script that generates this frontmatter template for the agent to fill out, or let the agent output this metadata via a tool call rather than writing it manually.

---

### 7. (LOW) Over-reaching Deletion Permissions

**The Issue:**
Step 7 of the handoff rule requires the agent to "delete `.agent-bootstrap/`".
Allowing an agent to execute directory deletion commands (`rm -rf`) poses safety and stability risks, particularly if path resolution goes wrong (e.g., resolving relative paths incorrectly or hitting the wrong folder due to name confusion).

**Recommendation:**
- The agent should not directly execute directory deletions. Instead, it should output a recommendation to the user to delete the directory (e.g., "I have finished the bootstrap. You can now safely delete `.agent-bootstrap/`").
- If the agent must perform the deletion, it should be restricted to a specific, hardcoded path validation check.

---

## Conclusion / Path Forward

The `.agent-bootstrap/` mechanism in v8 is a major step toward operationalizing the bootstrap process. By addressing the chicken-and-egg problem for first runs, fixing the gitignore leakage, renaming the scratch directory to avoid confusion, and adding freshness validation to handoffs, the plan will become significantly more robust and production-ready.
