# Portable Agent-Governance Bootstrap Plan

validated_against: review draft, 2026-06-08

Supersedes: `bootstrap-plan.final.md`. v5 removes the generated content-packet design.
The bootstrap produces manifests and review packets only; it does not copy target-repo
source file contents into LLM packets.

## What Changed From Final

The previous plan included an LLM input packet with selected file excerpts. That is not
needed for this workflow and creates avoidable security and design problems.

v5 changes the model:

- No generated packet contains source file contents.
- Discovery emits a manifest of paths, classifications, repo signals, custody state, and
  recommended files for an in-repo agent to read.
- The LLM/coding agent reads files directly from the repo when operating inside that repo.
- External review happens through normal source sharing, such as a GitHub repository link,
  not through generated content packets.
- Secret handling focuses on not copying secrets into generated artifacts, not on trying
  to sanitize copied source excerpts.

## Purpose

Create a reusable hybrid process that can be applied to any repository to generate and
maintain repo-specific agent support files. The goal is for a fresh agent to turn a
plain-English request into working, validated code while minimizing drift, regressions,
outdated repo facts, and untracked local process state.

This process is portable. It does not assume repo-specific implementation rules in
advance. Repo-specific rigidity is generated after discovery, evidence classification, and
human-readable review.

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

The deterministic layer handles mechanical work:

- list tracked files
- list ignored/local-only file names and locations
- flag likely-sensitive paths
- detect known agent harness files
- detect package, build, test, and CI files
- detect project boundaries
- record git status and current commit
- run approved checks
- write manifests
- stage artifacts, apply them safely, and prevent accidental overwrites
- compute the canonical repo-facts/guidance status
- enforce version naming
- verify generated artifacts are tracked or intentionally external
- emit the objective layer of the acceptance grade

The LLM layer handles judgment work:

- read files directly from the repo, guided by the manifest
- avoid likely-sensitive paths unless there is a specific human-approved reason
- assess existing docs and agent instructions
- identify conflicts
- draft repo-specific playbooks
- recommend harness adapter handling
- ask plain-language questions only when intent cannot be inferred
- explain findings and recommendations

Neither half is sufficient alone. The deterministic layer should not pretend to
understand repo intent universally. The LLM should not be trusted to remember custody,
overwrite, secret-safety, or verification mechanics without deterministic checks.

## Operating Modes

The bootstrap supports these command-level modes:

```powershell
.\bootstrap-agents.ps1 discover <repo>
.\bootstrap-agents.ps1 apply <repo> --approved-review <review-packet>
.\bootstrap-agents.ps1 apply <repo> --update --approved-review <review-packet>
.\bootstrap-agents.ps1 test-current <repo>
.\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>
.\bootstrap-agents.ps1 update <repo>
```

- `discover`: inspect the repo and produce a human-readable review packet plus a
  repo-discovery manifest. Do not write durable repo guidance.
- `apply`: write approved artifacts. Requires an approved review packet. Refuses when
  durable guidance already exists unless `--update` is supplied.
- `update`: re-run discovery on a repo that already has durable guidance, compare against
  current artifacts, and produce a proposed diff/review packet. It does not write changes
  by itself. Approved update changes are landed by running
  `apply <repo> --update --approved-review <review-packet>`.
- `test-current`: print exact steps for testing the generated guidance in a new agent
  session using the current checkout.
- `test-clean`: create or use a local clean copy, preferring local `git clone`, then print
  exact steps for testing in a new agent session. Do not require a remote.

Preview or pilot output may live outside the target repo when the human requests it. Real
adoption requires durable guidance to live in the target repo and be tracked, except for
explicitly local-only or install-derived files.

## Discovery Manifest Contract

`discover` produces a repo-discovery manifest. It contains no source file contents.

It may contain:

- repo path and current git commit
- tracked files
- untracked files
- ignored/local-only files
- likely-sensitive paths with reason codes
- project markers
- CI/build/test/package markers
- existing agent/harness files
- suggested files for an in-repo agent to read
- files intentionally excluded from suggested reading
- discovery coverage status
- baseline health results, when checks were run

It must not contain:

- source file excerpts
- secret values
- environment values
- private keys or certificates
- connection strings
- token bodies
- raw contents of ignored/local-only files

The manifest is a map, not evidence text. It directs an in-repo agent where to look and
what to avoid.

## Secret Handling

Secret handling has three separate contexts.

### Discovery

Discovery does not copy file contents. It flags likely-sensitive paths by name, extension,
and location. Examples:

- `.env*`
- `*.pem`
- `*.key`
- `*.pfx`
- `*.p12`
- `id_rsa*`
- `id_dsa*`
- `*.tfvars`
- `*.pubxml.user`
- `appsettings*.Secrets.json`
- `secrets.*`
- delimiter-separated names such as `password`, `token`, `credential`, `api-key`

The flag is a caution, not a deletion or access block:

> Do not read this path for agent-guidance discovery unless the human explicitly approves
> a specific reason.

### Repo Understanding

Agents read normal repo files directly. They should avoid flagged likely-sensitive files
unless needed and approved. A normal-looking config file can still contain a hard-coded
secret; agents must not copy secret values into generated guidance or final summaries.

### Verification

Builds and tests may rely on secrets already available in the local environment. The
verification runner may execute approved commands using the current environment, but it
must not write secret values into generated docs, manifests, logs, or review packets.

Secret-dependent checks should be reported plainly:

```text
This check appears to require local environment secrets.
It was skipped / run / failed.
No secret values were written to generated artifacts.
```

## Evidence Classes

Use these classes in discovery output and review packets:

- `human_confirmed`
- `executed_verification_result`
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
2. `executed_verification_result`
3. `observed_from_tests`
4. `observed_from_code`
5. `observed_from_ci`
6. `observed_from_git`
7. `inferred`
8. `doc_claim_unvalidated`
9. `question`

CI files prove commands are configured, not that they work. A verification command becomes
authoritative only after it is executed once and the result is recorded.

Promotion rules:

- `human_confirmed`, `executed_verification_result`, and `observed_*` findings may become
  binding repo rules.
- `inferred`, `doc_claim_unvalidated`, and `question` findings must not become hard rules
  until promoted by human confirmation or corroborated by current code, tests, CI, or git
  state.
- Existing docs and agent files are useful inputs, not automatic authority.

## Stable Principles Versus Repo Facts

Stable principles are behavior expectations:

- preserve human intent
- do not drift from the request
- verify before claiming done
- do not silently trust unreviewed docs
- do not overwrite user work
- explain plainly

Repo facts are observed mechanics:

- build commands
- test commands
- CI jobs
- package managers
- module locations
- app entry points
- current architecture patterns
- generated harness adapter locations

Repo changes do not automatically change agent principles or binding behavior rules. They
can only make repo facts outdated. Any change to binding rules still requires
human-readable review.

## Fact Refresh Versus Rule Change

The human should not be asked to classify technical repo fact changes.

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

Project boundary detection should look for common markers:

- JavaScript/TypeScript: `package.json`
- Python: `pyproject.toml`, `setup.py`, `requirements.txt`
- Go: `go.mod`
- Rust: `Cargo.toml`
- .NET: `*.sln`, `*.csproj`
- Java/Kotlin: `pom.xml`, `build.gradle`, `build.gradle.kts`

For monorepos, repo maps, checks, and playbooks may be per-project rather than
repo-global.

## Discovery Budget

Discovery must be bounded:

- Cap files the agent is expected to read per project.
- Prefer entry points, manifests, CI, tests, and representative modules over exhaustive
  reads.
- Cap generated playbooks per project.
- Summarize directories rather than enumerating every file in artifacts.

The discovery manifest must report coverage:

```yaml
coverage:
  status: complete | truncated
  candidate_count: <number>
  included_count: <number>
  cap: <number>
```

If coverage is `truncated`, the review packet must say plainly that the map is partial.

Budgets live in `.agents/bootstrap.config` and have safe defaults.

## Harness Adapter Baseline

The bootstrap has a default agent harness adapter baseline:

- Claude Code
- Codex CLI
- Aider
- Cursor
- Antigravity CLI, optional because it is less standard

Do not ask the human which baseline harnesses to support for every repo. Use defaults
unless the repo has `.agents/bootstrap.config`.

`.agents/bootstrap.config` may set:

```yaml
harness_adapters:
  - claude
  - codex
  - aider
  - cursor
```

When present, `discover` and `apply` honor exactly that list. When no config exists,
`discover` recommends the default baseline in plain language and records the final
approved list in the generated config. If no decision is made, use the default baseline
excluding optional Antigravity.

Existing harness files do not decide support. They are inspected only for migration and
custody risk.

## Adapter Authorship Boundary

The LLM recommends whether an adapter is needed and what canonical sources it should
reflect. The deterministic layer renders adapter bodies from templates and tracked
canonical sources.

When a harness supports pointers to `AGENTS.md` and `.agents/*`, the adapter should point
instead of duplicating rules.

When a harness requires its own file content and cannot point to canonical files, the
adapter may be tracked if the harness requires it, but it must include:

```text
Generated from AGENTS.md and .agents/*. Do not edit directly.
Regenerate with bootstrap-agents update.
```

## Derived Verification

The generated verification entry point must be derived from observed repo mechanics:

- Prefer executed CI-derived commands when available.
- Use package/build/test scripts where CI delegates to them.
- Treat docs as secondary if they disagree with CI or executed checks.
- Do not invent checks that are not supported by the repo.

Before a checks script becomes durable support material, it must be executed once and its
result recorded.

Discovery must capture baseline health:

- current commit
- commands run
- pass/fail status
- known failures, if any
- commands skipped and why

## Canonical Repo-Facts And Guidance Status

There is exactly one repo-facts freshness calculation, implemented in the deterministic
layer and consumed everywhere.

Inputs:

- `validated_against` commit recorded in `.agents/repo-map.md`
- current `HEAD`
- fact-bearing paths: CI/build/test/package files and project-structure files
- guidance paths: canonical guidance, playbooks, checks scripts, adapter templates

Verdicts:

- `facts_fresh`: no fact-bearing path changed since the stamp and any commit threshold is
  not exceeded.
- `facts_outdated`: a fact-bearing path changed, or the configured threshold is exceeded.
- `guidance_clean`: generated guidance paths match the validation stamp.
- `guidance_dirty`: canonical guidance, playbooks, checks scripts, or adapter templates
  changed since validation.
- `unknown`: preconditions for a reliable answer are not met.

`facts_outdated` means repo mechanics may have changed. `guidance_dirty` means the agent
support files themselves changed and need review/re-validation. Do not collapse these into
one generic stale verdict.

Default thresholds:

- Any change to a fact-bearing path returns `facts_outdated`.
- Any change to a guidance path returns `guidance_dirty`.
- A commit-count threshold is optional and defaults to disabled unless configured in
  `.agents/bootstrap.config`.
- Time alone is never a freshness source.

If history or a valid stamp is unavailable, return `unknown`. Never silently report
`facts_fresh` when the tool cannot actually tell.

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`
- `.agents/repo-map.md`
- `.agents/playbooks/*.md`
- `.agents/checks.ps1` or `.agents/checks.sh`
- `.agents/artifact-manifest.md`
- `.agents/test-current.md`
- `.agents/test-clean.md`
- `.agents/grade-agent-run.ps1`
- `.agents/bootstrap.config`
- optional harness adapters generated from tracked sources

Generated artifacts must not include source file contents copied from the target repo
unless the artifact is itself a deliberate adapter/template generated from canonical
guidance.

Each generated repo-fact artifact must include:

```text
validated_against: <commit-sha> on <date>
```

For preview artifacts outside a repo, use:

```text
validated_against: preview, <date>
```

## Acceptance Grader Contract

The grader has two layers.

Layer 1 is deterministic. `grade-agent-run.ps1` checks only machine-decidable signals and
exits nonzero on hard failure:

- Did the agent run the repo's verification entry point, or explicitly report why not?
- Did changes stay within the declared task scope, based on changed-file set versus
  declared scope?
- Is there a final-answer or executive-summary section present?
- Were likely-sensitive files modified without being declared?

Layer 2 is judgment. The script emits a checklist; a human or separate LLM judge fills it
in:

- Did the agent find the correct playbook?
- Did it avoid treating unvalidated docs as authority?
- Did it ask only necessary product-scope questions?
- Did it keep changes consistent with the repo's architecture?

The script never scores layer 2.

The declared scope must be machine-readable. Test run files such as
`.agents/test-results/current-run.md` must begin with frontmatter:

```yaml
---
task: "<plain-language task>"
declared_scope:
  paths:
    - "relative/path/or/glob"
  allowed_sensitive_paths: []
verification:
  ran: true | false
  command: "<command or reason skipped>"
---
```

If the frontmatter is missing, Layer 1 reports `scope unknown` and cannot pass the scope
check.

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

## Apply Semantics

`apply` is the only mode that writes durable repo guidance.

Rules:

- Requires an approved review packet path.
- The human act of passing `--approved-review <path>` is approval. `apply` records
  approval provenance by writing the review packet path, packet hash, current user,
  timestamp, and target repo into the artifact manifest or an approval record.
- The packet hash is audit provenance for what was approved. It is not a tamper-proof
  integrity check against the original discovery output.
- Refuses if durable guidance already exists unless `--update` is supplied. Without
  `--update`, it routes to `update`.
- Runs preflight checks before writing: target paths, ignored-file status, write
  permissions, existing guidance, and custody expectations.
- Writes to a staging directory first.
- Backs up any replaceable generated artifacts before replacement.
- Replaces files using same-directory temporary files and rename/move operations where
  possible. On Windows/NTFS, use same-volume rename behavior and retry transient file-lock
  failures.
- Validates expected files exist and custody status is correct.
- On failure, performs best-effort rollback and reports exactly what changed.

Do not claim perfect atomicity across arbitrary filesystems. The contract is staged,
validated, rollback-best-effort, and never silent.

## Git Custody Requirement

The bootstrap must identify every file future agents are expected to obey or use and
report whether each is:

- tracked
- ignored
- generated
- local-only
- install-derived
- missing

Ignored or local-only files must not silently become durable repo authority. Runtime hooks
under `.git/hooks` cannot be tracked directly; repos should track hook source files and
installer scripts instead.

Hook installation must be opt-in, reversible, and explicitly approved by the human.

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
11. Repo-facts/guidance status policy proposal.
12. Likely-sensitive path report.
13. Discovery manifest path.

Open questions must be written for a non-developer. Avoid file-format jargon unless it is
unavoidable, and explain the impact in plain English.

## Current-Checkout Test

The current-checkout test proves the generated guidance works in a new agent session using
the current working copy.

The bootstrap should generate exact steps:

```text
1. Open a brand-new agent session in <repo>.
2. Paste this prompt:

   <test request>

3. When the agent finishes, paste its final answer into:
   <repo>\.agents\test-results\current-run.md

4. Run:
   .\.agents\grade-agent-run.ps1 .\.agents\test-results\current-run.md
```

## Clean-Local-Copy Test

The clean-local-copy test proves the generated guidance works without hidden local-only
files from the original workspace.

It must not require a remote. Prefer local `git clone <repo> <clean-local-copy>` so the
copy retains git history. A flat file-copy is fallback only for repos where git history
does not matter; the repo-facts check should return `unknown` there.

Local-only and install-derived files are expected to be absent in the clean local copy.
Their absence is not a failure. The clean test should report them as intentionally missing
when the artifact manifest identifies them as local-only or install-derived.

## Fresh Agent Context

A test is valid only in a fresh context:

1. A new session with no prior conversation history.
2. No custom instructions or system-prompt overrides beyond what the repo guidance loads.
3. A clean workspace for the clean-local-copy test.

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

---

# Implementation Direction

PowerShell can be the first implementation because the initial environment is Windows.
The process itself is not PowerShell-specific. A portable implementation may later use
another language while preserving the same command contracts.

Build order:

1. Restore the command dispatcher with clean refusal for unimplemented modes.
2. Implement `discover` as manifest-only: repo inventory, git facts, markers,
   likely-sensitive paths, coverage status, and review packet.
3. Run discovery against a small repo in preview mode.
4. Use the manifest to have an in-repo agent draft the first repo-specific guidance.
5. Only then implement `apply`, checks, graders, and adapters.
