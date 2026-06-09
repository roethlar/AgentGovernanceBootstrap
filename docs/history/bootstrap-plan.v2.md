# Portable Agent-Governance Bootstrap Plan

validated_against: draft process, 2026-06-08

## Purpose

Create a reusable hybrid process that can be applied to any repository to generate and maintain repo-specific agent support files. The goal is for a fresh agent to turn a plain-English request into working, validated code while minimizing drift, regressions, outdated repo facts, and untracked local process state.

This process is portable. It does not assume repo-specific implementation rules in advance. Repo-specific rigidity is generated after discovery, evidence classification, and human-readable review.

## Stable Agent Mission

Future agents should be guided toward this behavior in every repo:

- Understand the human's natural-language request.
- Discover the correct implementation path for the current repo.
- Make changes that fit the repo's actual architecture and workflows.
- Avoid regressions and unapproved scope expansion.
- Validate with the repo's real checks.
- Explain the delivered result in plain English, with executive-level clarity.

These principles do not change automatically when code changes.

## Process Model

The bootstrap is hybrid.

The static script handles deterministic work:

- list tracked files
- list ignored/local-only file names and locations
- detect known agent harness files
- detect package, build, test, and CI files
- record git status and current commit
- run approved checks
- write manifests
- prevent accidental overwrites
- enforce version naming
- verify generated artifacts are tracked or intentionally external

The LLM handles judgment work:

- read relevant files
- assess existing docs and agent instructions
- identify conflicts
- draft repo-specific playbooks
- propose generated harness adapters
- ask plain-language questions only when intent cannot be inferred
- explain findings and recommendations

Neither half is sufficient alone. The script should not pretend to understand repo intent universally. The LLM should not be trusted to remember custody, overwrite, or verification mechanics without deterministic checks.

## Operating Modes

The bootstrap supports these command-level modes:

```powershell
.\bootstrap-agents.ps1 discover <repo>
.\bootstrap-agents.ps1 apply <repo>
.\bootstrap-agents.ps1 test-current <repo>
.\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>
.\bootstrap-agents.ps1 update <repo>
```

- `discover`: inspect the repo and produce a human-readable review packet. Do not write durable repo guidance.
- `apply`: write approved artifacts.
- `test-current`: print exact steps for testing the generated guidance in a new agent session using the current checkout.
- `test-clean`: create or use a local clean copy with ignored/local-only files excluded, then print exact steps for testing in a new agent session. Do not require a remote.
- `update`: re-run discovery on a repo that already has durable guidance, compare against current artifacts, and produce a proposed diff. Never silently overwrite human-reviewed guidance.

Preview or pilot output may live outside the target repo when the human requests it. Real adoption requires the durable guidance to live in the target repo and be tracked, except for explicitly local-only or install-derived files.

## Bootstrap Inputs

The bootstrap may inspect:

- tracked files
- ignored/local-only file names and locations
- package and build files
- CI workflows
- test projects
- app entry points
- scripts
- existing docs
- existing agent files
- hooks or hook installers

Secret-safe discovery is mandatory. The bootstrap may record that ignored/local-only files exist, but it must not copy secrets, tokens, passwords, private keys, environment values, or raw credential-like content into generated artifacts.

## Evidence Classes

Use these classes in discovery output:

- `human_confirmed`
- `observed_from_code`
- `observed_from_tests`
- `observed_from_ci`
- `observed_from_git`
- `doc_claim_unvalidated`
- `inferred`
- `question`

## Evidence Precedence And Promotion

Default precedence:

1. `human_confirmed`
2. `observed_from_ci`
3. `observed_from_tests`
4. `observed_from_code`
5. `observed_from_git`
6. `inferred`
7. `doc_claim_unvalidated`
8. `question`

When evidence conflicts, higher-precedence evidence wins unless the human explicitly overrides it.

Promotion rules:

- `human_confirmed` and `observed_*` findings may become binding repo rules.
- `inferred`, `doc_claim_unvalidated`, and `question` findings must not become hard rules until promoted by human confirmation or corroborated by current code, tests, CI, or git state.
- Existing docs and agent files are useful inputs, not automatic authority.

## Stable Principles Versus Repo Facts

The process must separate stable principles from repo facts.

Stable principles are behavior expectations such as:

- preserve human intent
- do not drift from the request
- verify before claiming done
- do not silently trust unreviewed docs
- do not overwrite user work
- explain plainly

Repo facts are observed mechanics such as:

- build commands
- test commands
- CI jobs
- package managers
- module locations
- app entry points
- current architecture patterns
- generated harness adapter locations

Repo changes do not automatically change agent principles or binding behavior rules. They can only make repo facts outdated. Any change to binding rules still requires human-readable review.

## Fact Refresh Versus Rule Change

The human should not be asked to classify technical repo fact changes.

The bootstrap should update objective fact records by reading the repo, then explain the impact plainly:

```text
I found that the repo's test command changed.

Before:
dotnet test

Now:
dotnet test -c Release --no-build

Impact:
Future agents should use the new command because CI uses it.

This does not change agent behavior rules. It only updates the command agents run before saying work is done.
```

Classification rules:

- Objective repo fact changed: update the fact record.
- Verification became stronger or equivalent: recommend updating checks.
- Verification became weaker or a safety boundary changed: ask the human in plain English.
- Binding agent rule would change: always ask the human in plain English.

Suspicious example:

```text
I found that tests appear to have been removed from CI.

Impact:
If accepted, future agents may stop running tests automatically.

Recommended action:
Do not update the verification rule yet. Confirm whether test removal was intentional.
```

## Discovery Procedure

Discovery should identify:

- project boundaries, including monorepo packages or multiple apps
- languages, frameworks, runtime versions, and package managers
- build, test, lint, format, and deploy entry points
- CI jobs and commands
- app architecture and common extension points
- test structure and coverage patterns
- high-risk areas suggested by code, CI, scripts, or human input
- existing docs and agent files, with trust status
- tracked, ignored, generated, local-only, and install-derived guidance files

For monorepos, repo maps, checks, and playbooks may be per-project rather than repo-global.

## Harness Adapter Baseline

The bootstrap has a default agent harness adapter baseline:

- Claude Code
- Codex CLI
- Antigravity CLI
- Aider
- Cursor

Do not ask the human which of these to support for every repo. Generate or propose adapters for the default baseline unless the repo explicitly opts out.

Existing harness files do not decide support. They are inspected only for migration and custody risk:

- old instructions that may conflict with canonical guidance
- ignored/local-only files that will not survive clone or review
- files that should become generated adapters
- files that should be preserved as archived reference

Questions to the human should be plain-language:

```text
I found existing agent instructions. They overlap with the new generated guidance.

Recommended action:
Preserve the old files as archived reference and generate new adapter files from AGENTS.md.

Do you want to use the recommended action?
```

When a harness supports pointers to `AGENTS.md` and `.agents/*`, the adapter should point instead of duplicating rules.

When a harness requires its own file content and cannot point to canonical files, generate the adapter from tracked canonical sources. The adapter may be tracked if the harness requires it, but it must include a generated-file header:

```text
Generated from AGENTS.md and .agents/*. Do not edit directly.
Regenerate with bootstrap-agents update.
```

## Derived Verification

The generated verification entry point must be derived from observed repo mechanics:

- Prefer CI commands when available.
- Use package/build/test scripts where CI delegates to them.
- Treat docs as secondary if they disagree with CI.
- Do not invent checks that are not supported by the repo.

Before a checks script becomes durable support material, it must be executed once and its result recorded.

Discovery must also capture baseline health:

- current commit
- commands run
- pass/fail status
- known failures, if any
- commands skipped and why

This lets future agents distinguish pre-existing breakage from regressions they introduced.

The verification entry point should also warn when repo facts may be outdated, based on:

- validation commit recorded in `.agents/repo-map.md`
- changes to CI/build/test/package files
- changes to project structure files
- changes to canonical guidance or playbooks

The warning should be plain:

```text
WARNING: Repo facts used by agent playbooks may be outdated. Run bootstrap-agents update before relying on them.
```

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`: short tracked root-level source of truth for future agents.
- `.agents/repo-map.md`: observed repo mechanics and architecture map.
- `.agents/playbooks/*.md`: task-specific recipes, such as add-module, fix-bug, review-change, change-deployment.
- `.agents/checks.ps1` or `.agents/checks.sh`: one verification entry point.
- `.agents/artifact-manifest.md`: git custody and generated-artifact report.
- `.agents/test-current.md`: exact manual steps for a new-session test in the current checkout.
- `.agents/test-clean.md`: exact manual steps for a new-session test in a clean local copy.
- Optional harness adapters generated from tracked sources.

Each generated repo-fact artifact must include a validation stamp:

```text
validated_against: <commit-sha> on <date>
```

For preview artifacts outside a repo, use:

```text
validated_against: preview, <date>
```

## AGENTS.md Shape

`AGENTS.md` should stay short and stable:

- mission
- source-of-truth order
- required task classification
- when to use playbooks
- when to ask the human
- verification entry point
- final-answer expectations
- pointers to `.agents/` files

Volatile repo detail belongs in `.agents/repo-map.md` and playbooks, not in `AGENTS.md`.

Harness adapters should point to `AGENTS.md` and tracked `.agents/` files when possible. Generated adapters should be treated as derived outputs from canonical guidance.

## Git Custody Requirement

The bootstrap must identify every file future agents are expected to obey or use and report whether each is:

- tracked
- ignored
- generated
- local-only
- install-derived
- missing

Ignored or local-only files must not silently become durable repo authority. Runtime hooks under `.git/hooks` cannot be tracked directly; repos should track hook source files and installer scripts instead.

Hook installation must be opt-in, reversible, and explicitly approved by the human.

## Outdated Repo Facts Triggers

Repo fact artifacts should be considered potentially outdated when:

- CI/build/test/package files changed since validation
- project structure or app entry points changed
- `.agents/` playbooks or `AGENTS.md` changed manually
- verification commands changed
- generated harness adapter templates changed
- the human requests update

Commit-count thresholds may be added as a local policy, but time alone should not be the default freshness source.

When repo facts are outdated, agents should re-run discovery in `update` mode before relying on affected playbooks.

## Bootstrap Review Packet

Before writing durable repo guidance, produce a compact review packet:

1. Repo mechanics observed.
2. Baseline health and commands run.
3. Existing guidance found, with git status and trust status.
4. Proposed agent artifacts.
5. Proposed playbooks.
6. Proposed verification entry point.
7. Existing harness files found and recommended handling.
8. Evidence conflicts and promotion requests.
9. Open questions needed to avoid wrong durable rules.
10. Git custody risks.
11. Outdated repo-facts policy proposal.

The human can approve, reject, or adjust this before durable repo guidance is written.

Open questions must be written for a non-developer. Avoid file-format jargon unless it is unavoidable, and explain the impact in plain English.

## Current-Checkout Test

The current-checkout test proves the generated guidance works in a new agent session using the current working copy.

The bootstrap should generate exact steps like:

```text
1. Open a brand-new Codex session in <repo>.
2. Paste this prompt:

   <test request>

3. When the agent finishes, paste its final answer into:
   <repo>\.agents\test-results\current-run.md

4. Run:
   .\.agents\grade-agent-run.ps1 .\.agents\test-results\current-run.md
```

## Clean-Local-Copy Test

The clean-local-copy test proves the generated guidance works without hidden local-only files from the original workspace.

It must not require a remote. It can create a local copy from tracked files or use a local git clone from the source repo path.

The bootstrap should generate exact steps like:

```text
1. Run:
   .\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>

2. Open a brand-new Codex session in <clean-local-copy>.
3. Paste the generated prompt.
4. Paste the final answer into the generated result file.
5. Run the generated grading command.
```

These tests evaluate the agent-guidance system, not the application itself.

Pass/fail rubric:

- the fresh agent finds the correct playbook
- asks only necessary product-scope questions
- avoids unvalidated docs as authority
- keeps changes within task scope
- runs or reports the required verification
- gives a plain-English executive summary

## Success Criteria

A fresh agent can:

- Start from a plain-English request.
- Find the correct repo-specific playbook.
- Avoid trusting unvalidated docs.
- Avoid inventing out-of-scope behavior.
- Make changes consistent with the repo.
- Run the right verification.
- Identify outdated repo facts before relying on them.
- Distinguish baseline failures from new regressions.
- Produce a plain-English executive summary.
- Leave durable guidance tracked in git when artifacts are intended to live in the repo.
