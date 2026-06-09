# Portable Agent-Governance Bootstrap Plan

validated_against: review draft, 2026-06-08

Supersedes: `bootstrap-plan.v6.md`. v7 keeps the manifest-only discovery model and
separates the core governance system from the implementation surface. It also adds an
explicit rule preventing transient chat corrections from leaking into durable repo
guidance as contextless rules.

## Purpose

Create a reusable process that can be applied to any repository to generate and maintain
repo-specific agent support files. The goal is for a fresh agent to turn a plain-English
request into working, validated code while minimizing drift, regressions, outdated repo
facts, and untracked local process state.

This process is portable. It does not assume repo-specific implementation rules in
advance. Repo-specific rigidity is generated after discovery, evidence classification,
and human-readable review.

## Stable Agent Mission

Future agents should be guided toward this behavior in every repo:

- Understand the human's natural-language request.
- Discover the correct implementation path for the current repo.
- Make changes that fit the repo's actual architecture and workflows.
- Avoid regressions and unapproved scope expansion.
- Validate with the repo's real checks.
- Explain the delivered result in plain English, with executive-level clarity.

These principles do not change automatically when code changes.

## Core System

The core system is documentation and structured data:

- `AGENTS.md`
- `.agents/repo-map.md` or `.agents/repo-map.json`
- `.agents/playbooks/*.md`
- `.agents/artifact-manifest.json`
- `.agents/bootstrap.config.json`
- `.agents/review-packets/*.md`
- optional harness adapters generated from canonical guidance

Executable helpers are optional support for repeatable inventory, validation, and grading.
They are not the source of truth. The source of truth is the tracked repo guidance and its
manifest.

## No Chat-Context Leakage

Durable repo files must not encode transient chat corrections as unexplained universal
rules.

Bad:

```text
Do not use Font X.
```

Good:

```text
Use the typography tokens defined in `styles/theme.css`. New UI should follow the existing
body and heading font scale unless a design change is explicitly approved.
```

Rules created from chat must be generalized, sourced, and written so they make sense to a
future maintainer without access to the conversation. If a correction is situational, it
belongs in the current task notes or review packet, not in `AGENTS.md`, code comments, or
long-lived playbooks.

## Manifest-Only Discovery

Discovery produces a repo-discovery manifest. It contains no source file contents.

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

## Implementation Surface Options

The process can be implemented in several ways. The choice affects installation,
portability, and maintenance, but it must not change the generated repo-governance model.

### Option A: Markdown/JSON Only

No executable helper is provided.

Workflow:

1. An agent follows a written discovery checklist.
2. The agent runs ordinary repo commands such as `git ls-files` and `git status --ignored`.
3. The agent fills the manifest and review packet manually.
4. The agent drafts or updates repo guidance from the manifest.

Strengths:

- no runtime dependency
- easiest to inspect
- least tooling surface

Tradeoffs:

- less repeatable
- more dependent on agent discipline
- mechanical checks are easier to miss

### Option B: Repo-Local Shell Helper

A repo-local helper such as `.agents/reposcan.sh` performs deterministic discovery.

Workflow:

1. A slash command or agent instruction runs the helper.
2. The helper emits the repo-discovery manifest and review packet.
3. The agent reads those outputs and continues with guidance generation.

Strengths:

- simple
- easy to invoke from slash commands
- works naturally on Linux/macOS and on Windows when a compatible shell is available
- no standalone product binary

Tradeoffs:

- shell availability varies by environment
- Windows invocation may require an explicit shell path
- robust cross-platform path handling is harder than in a general-purpose language

### Option C: Repo-Local PowerShell Helper

A repo-local helper such as `.agents/reposcan.ps1` performs deterministic discovery.

Workflow:

1. A slash command or agent instruction runs the helper.
2. The helper emits the repo-discovery manifest and review packet.
3. The agent reads those outputs and continues with guidance generation.

Strengths:

- strong git/process/filesystem orchestration
- available in many Windows-heavy environments and usable cross-platform with PowerShell 7
- structured JSON support is built in

Tradeoffs:

- PowerShell availability varies outside Windows
- script behavior can be affected by execution policy and shell conventions
- maintaining parity with shell helpers can create drift if both are used

### Option D: External Source-Run CLI

An external CLI implemented in a source language such as Python performs deterministic
discovery and validation.

Workflow:

1. The user or agent runs the external CLI against a target repo.
2. The CLI writes preview outputs outside the target repo or approved artifacts inside it.
3. The agent reads the manifest and review packet.

Strengths:

- one implementation can run across platforms when the runtime is available
- easier to test than shell scripts
- keeps helper logic outside target repos

Tradeoffs:

- requires installing or locating the runtime
- introduces a separate tool lifecycle
- should not impose that runtime on target repos

### Option E: External Binary CLI

An external compiled CLI performs deterministic discovery and validation.

Workflow:

1. The user or agent runs the binary against a target repo.
2. The binary writes preview outputs outside the target repo or approved artifacts inside it.
3. The agent reads the manifest and review packet.

Strengths:

- no runtime required on target machines
- consistent invocation
- strong fit for repeatable file/git/process operations

Tradeoffs:

- requires build/release artifacts per platform
- less transparent than source-run scripts
- introduces a binary distribution lifecycle

## Slash Command Shape

A harness-specific slash command can be a thin entry point:

```text
/reposcan
```

Expected behavior:

1. Run the configured discovery helper for the current repo.
2. Read the generated manifest and review packet.
3. Report important findings in plain English.
4. Continue with the requested governance task or stop for approval if durable repo files
   would be written.

The slash command should not duplicate the governance rules. It should point to
`AGENTS.md`, `.agents/playbooks/*`, and the helper invocation.

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

Budgets live in `.agents/bootstrap.config.json` and have safe defaults.

## Harness Adapter Baseline

The bootstrap has a default agent harness adapter baseline:

- Claude Code
- Codex CLI
- Aider
- Cursor
- Antigravity CLI, optional because it is less standard

Do not ask the human which baseline harnesses to support for every repo. Use defaults
unless the repo has `.agents/bootstrap.config.json`.

`.agents/bootstrap.config.json` may set:

```json
{
  "harnessAdapters": ["claude", "codex", "aider", "cursor"]
}
```

When present, discovery and apply honor exactly that list. When no config exists,
discovery recommends the default baseline in plain language and records the final approved
list in the generated config. If no decision is made, use the default baseline excluding
optional Antigravity.

Existing harness files do not decide support. They are inspected only for migration and
custody risk.

## Adapter Authorship Boundary

The LLM recommends whether an adapter is needed and what canonical sources it should
reflect. Deterministic helpers render adapter bodies from templates and tracked canonical
sources.

When a harness supports pointers to `AGENTS.md` and `.agents/*`, the adapter should point
instead of duplicating rules.

When a harness requires its own file content and cannot point to canonical files, the
adapter may be tracked if the harness requires it, but it must include:

```text
Generated from AGENTS.md and .agents/*. Do not edit directly.
Regenerate through the governance update process.
```

## Derived Verification

The generated verification entry point must be derived from observed repo mechanics:

- Prefer executed CI-derived commands when available.
- Use package/build/test scripts where CI delegates to them.
- Treat docs as secondary if they disagree with CI or executed checks.
- Do not invent checks that are not supported by the repo.

Before a checks entry point becomes durable support material, it must be executed once and
its result recorded.

Discovery must capture baseline health:

- current commit
- commands run
- pass/fail status
- known failures, if any
- commands skipped and why

## Canonical Repo-Facts And Guidance Status

There is exactly one repo-facts freshness calculation, consumed everywhere.

Inputs:

- `validated_against` commit recorded in `.agents/repo-map.md` or `.agents/repo-map.json`
- current `HEAD`
- fact-bearing paths: CI/build/test/package files and project-structure files
- guidance paths: canonical guidance, playbooks, checks entry points, adapter templates

Verdicts:

- `facts_fresh`: no fact-bearing path changed since the stamp and any commit threshold is
  not exceeded.
- `facts_outdated`: a fact-bearing path changed, or the configured threshold is exceeded.
- `guidance_clean`: generated guidance paths match the validation stamp.
- `guidance_dirty`: canonical guidance, playbooks, checks entry points, or adapter
  templates changed since validation.
- `unknown`: preconditions for a reliable answer are not met.

`facts_outdated` means repo mechanics may have changed. `guidance_dirty` means the agent
support files themselves changed and need review/re-validation. Do not collapse these into
one generic stale verdict.

Default thresholds:

- Any change to a fact-bearing path returns `facts_outdated`.
- Any change to a guidance path returns `guidance_dirty`.
- A commit-count threshold is optional and defaults to disabled unless configured in
  `.agents/bootstrap.config.json`.
- Time alone is never a freshness source.

If history or a valid stamp is unavailable, return `unknown`. Never silently report
`facts_fresh` when the process cannot actually tell.

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`
- `.agents/repo-map.md` or `.agents/repo-map.json`
- `.agents/playbooks/*.md`
- `.agents/checks.*`, only if a repo-native wrapper is useful
- `.agents/artifact-manifest.json`
- `.agents/test-current.md`
- `.agents/test-clean.md`
- `.agents/bootstrap.config.json`
- optional harness adapters generated from tracked sources

Generated target-repo artifacts should be docs/data plus optional repo-native wrappers.
They must not impose the helper implementation language as a target-repo runtime
dependency.

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

The grader may live outside the target repo as part of the governance helper, or it may be
a repo-native wrapper when that fits the repo. The target repo should not inherit a runtime
dependency solely for grading.

Layer 1 is deterministic and checks only machine-decidable signals:

- Did the agent declare that it ran the repo's verification entry point, or explicitly
  report why not?
- Did changes stay within the declared task scope, based on changed-file set versus
  declared scope?
- Is there a final-answer or executive-summary section present?
- Were likely-sensitive files modified without being declared?

Layer 1 verifies the presence and consistency of declarations. It does not prove that a
self-reported command actually executed unless the run includes verifiable command output
or exit-code evidence.

Layer 2 is judgment. A human or separate LLM judge fills it in:

- Did the agent find the correct playbook?
- Did it avoid treating unvalidated docs as authority?
- Did it ask only necessary product-scope questions?
- Did it keep changes consistent with the repo's architecture?

The deterministic grader never scores layer 2.

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

Volatile repo detail belongs in `.agents/repo-map.*` and playbooks, not in `AGENTS.md`.

## Apply Semantics

`apply` is the only mode that writes durable repo guidance.

Rules:

- Requires an approved review packet path.
- The human act of passing `--approved-review <path>` is approval. The process records
  approval provenance by writing the review packet path, packet hash, current user,
  timestamp, and target repo into the artifact manifest or an approval record.
- The packet hash is audit provenance for what was approved. It is not a tamper-proof
  integrity check against the original discovery output.
- Refuses if durable guidance already exists unless an approved update mode is supplied.
- Runs preflight checks before writing: target paths, ignored-file status, write
  permissions, existing guidance, and custody expectations.
- Writes to a staging directory first.
- Backs up any replaceable generated artifacts before replacement.
- Replaces files using same-directory temporary files and rename/move operations where
  possible. Retry transient file-lock failures.
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
   <repo>/.agents/test-results/current-run.md

4. Run the configured grading helper, if one exists, or review the Layer 2 checklist.
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

## Implementation Direction

Do not choose the implementation surface by chat preference alone. Select the smallest
surface that can perform manifest-only discovery repeatably in the environments where it
will actually run.

Recommended first implementation:

1. Start with a repo-local slash-command helper if the target harness can run one reliably.
2. Keep the helper manifest-only.
3. Use the helper to scan a small repo in preview mode.
4. Only add a larger external CLI if repo-local helpers prove insufficient.

Build order:

1. Define the manifest and review-packet templates.
2. Implement the smallest deterministic discovery helper for one environment.
3. Run discovery against a small repo in preview mode.
4. Use the manifest to have an in-repo agent draft first repo-specific guidance.
5. Implement apply/checks/grading only after discovery proves useful.
