# Portable Agent-Governance Bootstrap Plan

validated_against: preview, 2026-06-08

Supersedes: `bootstrap-planv3.claude.md`. v4 keeps v3's structure but tightens the
engineering contract around LLM handoff, secret safety, write safety, approval flow, and
portability.

## What changed from v3

v3 resolved the major conceptual and operational review findings. v4 makes five
corrections:

- Replaces implicit "the script controls what the LLM reads" with an explicit
  **LLM input packet / LLM output packet** contract. The script cannot control a chat
  model by hope; it can only prepare safe inputs and validate outputs.
- Narrows the secret-safety guarantee. The process can make leaks unlikely by
  construction when its packet workflow is followed; it cannot promise impossibility if a
  human or agent bypasses the packet and opens denied files manually.
- Replaces "atomic write as a unit" with a practical staged-apply contract:
  preflight, backup, write staging, replace, validate, and rollback-best-effort.
- Makes approval explicit and durable: `apply` requires an approved review packet or an
  explicit `--approved-review <path>`.
- Separates the **portable process** from the first implementation language. PowerShell
  may be the first implementation, but the process itself must remain OS/harness neutral.

---

# PART 1 - Refined Specification

## Purpose

Create a reusable hybrid process that can be applied to any repository to generate and
maintain repo-specific agent support files. The goal is for a fresh agent to turn a
plain-English request into working, validated code while minimizing drift, regressions,
outdated repo facts, and untracked local process state.

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

## Process Model

The bootstrap is hybrid.

The deterministic layer handles mechanical work:

- list tracked files
- list ignored/local-only file names and locations
- run the secret deny-list scan
- build an LLM-readable input packet from cleared files only
- detect known agent harness files
- detect package, build, test, and CI files
- record git status and current commit
- run approved checks
- write manifests
- stage artifacts, apply them safely, and prevent accidental overwrites
- compute the canonical outdated-facts verdict
- enforce version naming
- verify generated artifacts are tracked or intentionally external
- emit the objective layer of the acceptance grade

The LLM layer handles judgment work:

- read only the prepared LLM input packet
- assess existing docs and agent instructions included in that packet
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
.\bootstrap-agents.ps1 test-current <repo>
.\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>
.\bootstrap-agents.ps1 update <repo>
```

- `discover`: inspect the repo and produce a human-readable review packet plus an LLM
  input packet. Do not write durable repo guidance.
- `apply`: write approved artifacts. Requires an approved review packet. Refuses when
  durable guidance already exists and routes the human to `update`.
- `test-current`: print exact steps for testing the generated guidance in a new agent
  session using the current checkout.
- `test-clean`: create or use a local clean copy, preferring local `git clone`, then print
  exact steps for testing in a new agent session. Do not require a remote.
- `update`: re-run discovery on a repo that already has durable guidance, compare against
  current artifacts, and produce a proposed diff. Never silently overwrite
  human-reviewed guidance.

Preview or pilot output may live outside the target repo when the human requests it. Real
adoption requires the durable guidance to live in the target repo and be tracked, except
for explicitly local-only or install-derived files.

## LLM Packet Contract

The deterministic layer creates two packet types.

### LLM Input Packet

The input packet is the only content the LLM is expected to read during bootstrap
judgment. It contains:

- repo inventory
- git facts
- cleared file excerpts or summaries
- existing guidance files that passed secret screening
- CI/build/test observations
- denied-file path/existence report, with no values
- explicit questions for the LLM to answer

It does not contain:

- contents of deny-listed files
- raw secrets, tokens, private keys, passwords, connection strings, or credential values
- ignored/local-only file contents unless explicitly cleared by the secret scanner

### LLM Output Packet

The LLM writes a structured output packet containing:

- proposed evidence classifications
- doc/agent-file assessment
- proposed repo map
- proposed playbooks
- proposed harness adapter decisions
- proposed plain-language human questions
- unresolved conflicts

The deterministic layer validates and redacts the output packet before rendering durable
artifacts. If validation finds denied values or unsupported claims, the packet is rejected
or returned for revision.

## Secret-Safe Discovery

Secret-safe discovery is enforced by the deterministic layer and by packet validation.

1. **Deny-list by name/glob.** Flag files matching at minimum: `.env*`, `*.pem`,
   `*.key`, `*.pfx`, `*.p12`, `id_rsa*`, `id_dsa*`, `*.tfvars`, `*.pubxml.user`,
   `appsettings*.Secrets.json`, `secrets.*`, and any name containing `secret`,
   `credential`, `password`, `token`, or `apikey`.
2. **Path-and-existence only for flagged files.** For flagged files, record only that
   they exist and where. Do not read, copy, summarize, or pass contents to the LLM.
3. **Cleared-file packet.** The LLM input packet includes only cleared files or approved
   summaries.
4. **Output validation.** Before artifacts are written, scan the LLM output packet for
   common secret patterns and redact or reject.

This is a process guarantee, not magic. It holds when agents use the packet workflow. If a
human or LLM bypasses the workflow and opens denied files manually, the bootstrap cannot
guarantee safety.

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

### CI Nuance

A CI file proves a job exists. It does not prove the job runs or passes. CI commands are
claims until executed once. Treat "CI config references command X" as strong evidence
that X is intended; treat "X was executed and its result recorded" as the authority for
verification.

## Evidence Precedence And Promotion

Default precedence:

1. `human_confirmed`
2. executed verification results
3. `observed_from_tests`
4. `observed_from_code`
5. `observed_from_ci`
6. `observed_from_git`
7. `inferred`
8. `doc_claim_unvalidated`
9. `question`

When evidence conflicts, higher-precedence evidence wins unless the human explicitly
overrides it.

Promotion rules:

- `human_confirmed`, executed verification results, and `observed_*` findings may become
  binding repo rules.
- `inferred`, `doc_claim_unvalidated`, and `question` findings must not become hard rules
  until promoted by human confirmation or corroborated by current code, tests, CI, or git
  state.
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

Repo changes do not automatically change agent principles or binding behavior rules. They
can only make repo facts outdated. Any change to binding rules still requires
human-readable review.

## Fact Refresh Versus Rule Change

The human should not be asked to classify technical repo fact changes.

Classification rules:

- Objective repo fact changed: update the fact record.
- Verification became stronger or equivalent: recommend updating checks.
- Verification became weaker or a safety boundary changed: ask the human in plain
  English.
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

### Discovery Budget

Discovery must be bounded:

- Cap files the LLM reads per project.
- Prefer entry points, manifests, CI, tests, and representative modules over exhaustive
  reads.
- Cap generated playbooks per project.
- Summarize directories rather than enumerating every file in artifacts.

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

### Opt-Out Mechanism

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
custody risk:

- old instructions that may conflict with canonical guidance
- ignored/local-only files that will not survive clone or review
- files that should become generated adapters
- files that should be preserved as archived reference

Questions to the human should be plain-language.

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

## Canonical Outdated-Facts Definition

There is exactly one definition of outdated repo facts, implemented in the deterministic
layer and consumed everywhere.

Inputs:

- `validated_against` commit recorded in `.agents/repo-map.md`
- current `HEAD`
- fact-bearing paths: CI/build/test/package files, project-structure files, canonical
  guidance, adapter templates

Verdict:

- `fresh`: no fact-bearing path changed since the stamp and any commit threshold is not
  exceeded.
- `outdated`: a fact-bearing path changed, or the configured threshold is exceeded.
- `unknown`: preconditions for a reliable answer are not met.

The calculation requires git history. If history or a valid stamp is unavailable, return
`unknown` and print:

```text
Freshness unknown - git history unavailable or validation stamp missing.
```

It must never silently report `fresh` when it cannot actually tell.

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
- Were deny-listed secret files modified or were obvious secret values surfaced?

Layer 2 is judgment. The script emits a checklist; a human or separate LLM judge fills it
in:

- Did the agent find the correct playbook?
- Did it avoid treating unvalidated docs as authority?
- Did it ask only necessary product-scope questions?
- Did it keep changes consistent with the repo's architecture?

The script never scores layer 2.

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
- Refuses if durable guidance already exists and routes to `update`.
- Runs preflight checks before writing: target paths, ignored-file status, write
  permissions, existing guidance, and custody expectations.
- Writes to a staging directory first.
- Backs up any replaceable generated artifacts before replacement.
- Moves staged files into place.
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
11. Outdated repo-facts policy proposal.
12. Secret-safety report: deny-listed files found, path/existence only.
13. LLM packet validation result.

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
does not matter; the outdated-facts check should return `unknown` there.

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

# PART 2 - Implementation Plan

PowerShell can be the first implementation because the initial environment is Windows.
The process itself is not PowerShell-specific. A portable implementation may later use
another language while preserving the same command contracts.

## Command Contracts

| Mode | Inputs | Preconditions | Side-effects | Outputs | Exit codes | Refuses when |
|---|---|---|---|---|---|---|
| `discover` | `<repo>` | repo readable | writes preview review packet and LLM input packet outside durable guidance paths | review packet, LLM input packet, secret-safety report, baseline health | 0 ok / 2 read error / 8 secret-scan failure | repo missing |
| `apply` | `<repo> --approved-review <path>` | approved review packet exists | staged durable artifact write, manifest regen, custody verify | written artifacts + custody report | 0 ok / 3 refused / 4 write error / 9 rollback incomplete | existing guidance, missing approval, failed preflight |
| `test-current` | `<repo>` | artifacts exist | writes `test-current.md`, scaffolds `test-results/` | printed steps | 0 / 5 missing artifacts | no artifacts |
| `test-clean` | `<repo> <clean-copy>` | git available preferred | creates clean local copy | printed steps + clean copy | 0 / 6 copy error / 10 git unavailable fallback used | target path occupied |
| `update` | `<repo>` | durable guidance exists | writes proposed diff/review packet only until approval | proposed diff vs. current | 0 / 7 nothing-to-do | no existing guidance |

All modes refuse cleanly when preconditions are unmet and must never silently partially
write.

## Script Module Layout

```text
bootstrap-agents.ps1        # CLI dispatch only; parses mode, delegates
lib/
  Discover.ps1              # read-only discovery, review packet, LLM input packet
  SecretScan.ps1            # deny-list, cleared allow-list, output redaction checks
  GitFacts.ps1              # status, current commit, changed-paths-since-stamp
  Apply.ps1                 # preflight, staging, backup, apply, validate, rollback
  Staleness.ps1             # the one canonical fresh/outdated/unknown verdict
  Grade.ps1                 # objective layer + checklist scaffold emit
  Render.ps1                # deterministic artifact/adapter templating
templates/
```

`SecretScan.ps1` runs before any LLM packet is produced. `Apply.ps1` is the only writer of
durable guidance. `Staleness.ps1` is imported by both generated checks and update.

## Artifact Templates

Templates under `templates/`:

- `AGENTS.md`
- `repo-map.md`
- `playbooks/*.md`
- `checks.ps1`
- `artifact-manifest.md`
- `test-current.md`
- `test-clean.md`
- `grade-agent-run.ps1`
- `bootstrap.config`
- harness adapters

## Deterministic / LLM Boundary Table

| Step | Owner |
|---|---|
| List tracked / ignored files, git status, current commit | Deterministic layer |
| Secret deny-list scan | Deterministic layer |
| Produce LLM input packet | Deterministic layer |
| Read and interpret packet | LLM |
| Classify evidence and flag conflicts | LLM proposes; deterministic layer records |
| Decide adapter inclusion | LLM recommends; config/human approval decides |
| Render artifact and adapter bodies | Deterministic layer |
| Compose checks from observed commands | LLM proposes; deterministic layer validates and executes |
| Execute checks once; capture baseline health | Deterministic layer |
| Compute outdated-facts verdict | Deterministic layer |
| Apply artifacts safely | Deterministic layer |
| Draft playbooks and plain-language questions | LLM |
| Objective acceptance grade | Deterministic layer |
| Subjective acceptance grade | Human / LLM judge |

## Hooks

Hook installation remains opt-in, reversible, and explicitly approved. The repo tracks
hook source files and installer/uninstaller scripts; `.git/hooks` runtime files are never
the tracked authority.

---

# PART 3 - Build & Verification Sequence

1. **Skeleton + dispatch.** Implement command parsing and clean refusal for all modes.
2. **Secret-safe discovery.** Implement deny-list, cleared-file packet generation, and
   output packet validation before any durable artifact rendering.
3. **Discovery packet.** Implement git facts, repo inventory, review packet, and LLM input
   packet.
4. **LLM output schema.** Define the structured output packet schema and validation
   errors.
5. **Apply.** Implement preflight, staging, backup, apply, validation, rollback-best-effort,
   and custody verification.
6. **Checks + outdated facts.** Implement the canonical outdated-facts calculation and
   generated checks entry point.
7. **Grader.** Implement objective grade and subjective checklist scaffold.
8. **Tests.** Implement current-checkout and clean-local-copy test step generation.
9. **Update.** Diff discovery against existing artifacts and produce a proposed review
   packet; no silent overwrite.
10. **Pilot.** Run against a real repo in preview mode, then review the packet before any
    target-repo writes.

## Verifying This Document

- Every generated artifact has a template listed.
- Every operating mode has a command contract.
- Secret safety has a packet-level mechanism.
- Apply semantics do not claim impossible filesystem atomicity.
- The LLM boundary is explicit.
- Existing v0, v1, v2, and v3 drafts remain available for comparison.
