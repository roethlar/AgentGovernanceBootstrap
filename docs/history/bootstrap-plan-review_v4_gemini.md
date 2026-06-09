# Review: Portable Agent-Governance Bootstrap Plan (v4)

**Reviewer:** Antigravity (Advanced AI Coding Assistant)  
**Date:** 2026-06-08  
**Target File:** [bootstrap-plan.v4.md](file:///D:/source/AgentGovernanceBootstrap/bootstrap-plan.v4.md)  
**Status:** Highly Approved (Production-Ready Spec)

---

## 1. Executive Summary

The **v4 specification** represents a highly mature, operationally rigorous, and epistemically sound design. It successfully addresses the major gaps identified in earlier iterations (v0 through v3), transitioning from a loose description of desired agent behaviors into a tight engineering contract.

By formalizing the **LLM input/output packet boundary**, establishing a **two-tier grader**, and specifying a **staged apply workflow with rollback**, the plan provides a clear blueprint for a production-grade bootstrap utility.

This review highlights the key strengths of the v4 design, analyzes minor remaining implementation edge cases, and provides concrete recommendations to ensure the upcoming implementation is robust, particularly regarding secret safety and Windows-specific file mechanics.

---

## 2. Key Strengths of the v4 Plan

### 🚀 Explicit LLM Input/Output Packet Contract
* **The Design:** The deterministic layer is the absolute gatekeeper of what the LLM reads and writes. The LLM is restricted to reading the cleared `LLM Input Packet`, and its `LLM Output Packet` must pass through validation before any file is written.
* **Why it matters:** This directly prevents prompt injection or agent confusion from exposing unvalidated documentation or raw secrets, replacing "hope" with structured data verification.

### 🛡️ Narrows Secret-Safety to a Process Guarantee
* **The Design:** Explicitly acknowledges that the bootstrap tool cannot enforce absolute security if a human or an unconstrained agent manually runs commands to bypass the packet system.
* **Why it matters:** Setting realistic security boundaries prevents security theater and focuses effort on securing the pipeline where it is most effective: during automated discovery and artifact output validation.

### 🔄 Staged Apply with Best-Effort Rollback
* **The Design:** Rather than asserting filesystem atomicity, v4 mandates a staged workflow: Preflight ➔ Write Staging ➔ Backup ➔ Replace ➔ Validate ➔ Best-effort Rollback.
* **Why it matters:** Windows environment files are prone to file locks by IDEs and active language servers. This staging sequence ensures that partial writes are detected and rolled back, leaving the repo in a consistent state.

### 📊 Two-Tier Grader (Deterministic vs. Subjective)
* **The Design:** Layer 1 is deterministic (`grade-agent-run.ps1` checks exit codes, scope drift, and presence of mandatory sections); Layer 2 is subjective checklist generation.
* **Why it matters:** Avoids the anti-pattern of a PowerShell script trying to evaluate subjective concepts (like "did the agent ask the right questions?"), while still enforcing strict compliance checks.

---

## 3. Operational Refinements & Edge Cases

To ensure a flawless implementation of the v4 plan, the following technical details should be incorporated into the development of the script modules (`lib/*`):

### A. Secret Redaction: Exact-Match Filtering
> [!IMPORTANT]
> How does the deterministic layer scan the `LLM Output Packet` for secrets if it is not allowed to feed secret values to the LLM?
* **Problem:** Scanning output solely for "common secret patterns" (e.g., regexes for keys) will miss custom or low-entropy secrets.
* **Solution:** The `SecretScan.ps1` module should:
  1. Temporarily load flagged secret files (like `.env`) in local memory.
  2. Extract the exact value strings.
  3. Construct a temporary, in-memory **redaction set** (or Trie).
  4. Scan the `LLM Output Packet` against this set and redact/replace any matches before writing to disk.
  5. *Crucially, these exact values are never written to any intermediate artifacts or passed to the LLM.*

### B. Windows File Lock Mitigation (Apply Staging)
> [!TIP]
> IDE file watchers (e.g., VS Code, Cursor) and terminal sessions often lock files under `.agents/` as soon as they are touched.
* **Recommendation:** In `Apply.ps1`, use robust file replacement tactics:
  - When replacing a file, write to a temporary file in the target directory (e.g., `AGENTS.md.tmp`), then perform a rename/move operation (`Move-Item -Force` or Win32 API calls). Renames are atomic on NTFS if they are on the same volume, whereas overwrites can fail if the file is being read.
  - Implement a retry loop (e.g., 3 attempts spaced 100ms apart) for file moves to accommodate transient locks from IDE indexing.

### C. Defining the Outdated-Facts Thresholds
* **Recommendation:** Under `Staleness.ps1`, define clear, sensible defaults for the commit threshold (e.g., `5 commits` or `any commit touching build/CI/test manifests`).
* **Git Command Implementation:**
  - To check if fact-bearing files have changed since the validation commit:
    ```powershell
    git diff --name-only <validation-commit-sha> HEAD
    ```
  - If this command returns files matching `package.json`, `pom.xml`, `.github/workflows/*`, etc., immediately set the verdict to `outdated`.

### D. Monorepo Package Boundary Discovery
* **Recommendation:** In `Discover.ps1`, boundary discovery should look for marker files at sub-levels:
  - Javascript/Typescript: `package.json`
  - Python: `pyproject.toml`, `setup.py`, `requirements.txt`
  - Go: `go.mod`
  - Rust: `Cargo.toml`
  - .NET: `*.sln`, `*.csproj`
  - Java/Kotlin: `pom.xml`, `build.gradle`, `build.gradle.kts`
  - If subdirectories containing these files are found, group discoveries and playbooks under those sub-project folders (e.g., `.agents/playbooks/backend/` and `.agents/playbooks/frontend/`).

---

## 4. Verdict & Next Steps

The **v4 plan** is fully approved and ready for implementation. The transition from design to code should follow the build sequence outlined in **Part 3** of the plan:

1. **Phase 1:** Implement the dispatcher `bootstrap-agents.ps1` and skeleton commands to verify argument parsing and basic directory structure validation.
2. **Phase 2:** Develop `SecretScan.ps1` and `Discover.ps1` to construct the LLM input packet and review packet.
3. **Phase 3:** Create `Apply.ps1` with the staged write, backup, and best-effort rollback mechanism.

No major architectural modifications are needed for `bootstrap-plan.v4.md` itself. The refinements above should be treated as implementation directives.
