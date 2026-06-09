# Portable Agent-Governance Bootstrap Plan — v3

validated_against: preview, 2026-06-08

Supersedes: `bootstrap-plan.v2.md`. Review that produced this revision:
`bootstrap-plan-review_claude.md`.

## What changed from v2

v0→v2 settled the *epistemics* (evidence classes, precedence, custody, the hybrid
script/LLM split, stable principles vs. repo facts). v2's remaining weakness was
**operational**: it described a tool (`bootstrap-agents.ps1`, a grader, secret-safe
discovery) that does not exist, and asserted its hardest mechanics — secret redaction,
overwrite safety, grading — as mandates with no mechanism.

v3 keeps v2's conceptual core intact and closes the operational gaps. It is organized in
three parts:

- **Part 1 — Refined Specification.** v2's design, with the review's H/M/L fixes merged
  into the relevant sections.
- **Part 2 — Implementation Plan.** Command contracts, script module layout, artifact
  templates, and the deterministic/LLM boundary — concrete enough to build.
- **Part 3 — Build & Verification Sequence.** An ordered path from skeleton to a proven,
  self-bootstrapped tool.

A traceability table at the end maps every review finding to its fix.

---

# PART 1 — Refined Specification

## Purpose

Create a reusable hybrid process that can be applied to any repository to generate and
maintain repo-specific agent support files. The goal is for a fresh agent to turn a
plain-English request into working, validated code while minimizing drift, regressions,
outdated repo facts, and untracked local process state.

This process is portable. It does not assume repo-specific implementation rules in advance.
Repo-specific rigidity is generated after discovery, evidence classification, and
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

The static script handles deterministic work:

- list tracked files
- list ignored/local-only file names and locations
- run the secret deny-list scan and decide which files the LLM may read (see Secret-Safe
  Discovery)
- detect known agent harness files
- detect package, build, test, and CI files
- record git status and current commit
- run approved checks
- write manifests
- write artifacts atomically and prevent accidental overwrites
- compute the canonical staleness verdict
- enforce version naming
- verify generated artifacts are tracked or intentionally external
- emit the objective layer of the acceptance grade

The LLM handles judgment work:

- read only the files the script has cleared
- assess existing docs and agent instructions
- identify conflicts
- draft repo-specific playbooks
- decide whether a given harness adapter is needed (the script renders its body)
- ask plain-language questions only when intent cannot be inferred
- explain findings and recommendations

Neither half is sufficient alone. The script should not pretend to understand repo intent
universally. The LLM should not be trusted to remember custody, overwrite, secret-safety,
or verification mechanics without deterministic checks.

The deterministic/LLM ownership of each step is enumerated in Part 2 (Boundary Table) so
the split is executable, not aspirational.

## Operating Modes

The bootstrap supports these command-level modes:

```powershell
.\bootstrap-agents.ps1 discover <repo>
.\bootstrap-agents.ps1 apply <repo>
.\bootstrap-agents.ps1 test-current <repo>
.\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>
.\bootstrap-agents.ps1 update <repo>
```

- `discover`: inspect the repo and produce a human-readable review packet. Do not write
  durable repo guidance.
- `apply`: write approved artifacts. Refuses when durable guidance already exists and
  routes the human to `update`. Writes atomically (see Apply Semantics).
- `test-current`: print exact steps for testing the generated guidance in a new agent
  session using the current checkout.
- `test-clean`: create or use a local clean copy with ignored/local-only files excluded,
  then print exact steps for testing in a new agent session. Do not require a remote.
- `update`: re-run discovery on a repo that already has durable guidance, compare against
  current artifacts, and produce a proposed diff. Never silently overwrite human-reviewed
  guidance.

Each mode's full contract (inputs, preconditions, side-effects, outputs, exit codes,
refusal conditions) is in Part 2.

Preview or pilot output may live outside the target repo when the human requests it. Real
adoption requires the durable guidance to live in the target repo and be tracked, except
for explicitly local-only or install-derived files.

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

Secret-safe discovery is mandatory and is enforced by the script, not by LLM goodwill.

### Secret-Safe Discovery (mechanism)

The deterministic script is the gate. The LLM never chooses what to open.

1. **Deny-list by name/glob.** The script flags files matching a deny-list, including at
   minimum: `.env*`, `*.pem`, `*.key`, `*.pfx`, `*.p12`, `id_rsa*`, `id_dsa*`,
   `*.tfvars`, `*.pubxml.user`, `appsettings*.Secrets.json`, `secrets.*`, and any name
   containing `secret`, `credential`, `password`, `token`, or `apikey`. The deny-list is
   defined once in `lib/SecretScan.ps1` and is extensible per repo via
   `.agents/bootstrap.config`.
2. **Path-and-existence only for flagged files.** For a flagged file the script records
   *that it exists and where*. It never reads, copies, summarizes, or passes the contents
   to the LLM.
3. **Cleared-file allow-list.** The script produces the explicit set of files the LLM is
   permitted to read. The LLM half operates only on that set.
4. **Redaction by default.** If a value-like token (long random string, `KEY=...`,
   PEM block, connection string) appears in any text the LLM is about to write to an
   artifact, the script redacts it to `[REDACTED]` before the artifact is committed.

One leaked secret in a tracked `repo-map.md` undoes the entire "durable, tracked in git"
benefit; this gate exists to make that failure impossible by construction, not by trust.

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

### CI nuance

A CI file proves a job *exists* (`observed_from_ci`). It does **not** prove the job runs or
passes — a job can be disabled, conditionally skipped, or always-green. CI *commands* are
claims until executed once (see Derived Verification). Treat "the CI config references
command X" as strong evidence X is intended, and "X was executed and its result recorded"
as the thing that makes X authoritative.

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

When evidence conflicts, higher-precedence evidence wins unless the human explicitly
overrides it.

Promotion rules:

- `human_confirmed` and `observed_*` findings may become binding repo rules.
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

The bootstrap should update objective fact records by reading the repo, then explain the
impact plainly:

```text
I found that the repo's test command changed.

Before:
dotnet test

Now:
dotnet test -c Release --no-build

Impact:
Future agents should use the new command because CI uses it.

This does not change agent behavior rules. It only updates the command agents run before
saying work is done.
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

### Discovery budget

Discovery must be bounded so a large monorepo does not cause runaway read cost or an
unmanageable playbook count:

- Cap files the LLM reads per project (default: a configurable ceiling; prefer entry
  points, manifests, CI, and representative modules over exhaustive reads).
- Cap generated playbooks per project; prefer a small set of high-value recipes over one
  per task variant.
- Summarize directories rather than enumerating every file in artifacts.

Budgets live in `.agents/bootstrap.config` and have safe defaults.

## Harness Adapter Baseline

The bootstrap has a default agent harness adapter baseline:

- Claude Code
- Codex CLI
- Aider
- Cursor
- Antigravity CLI *(lower-confidence/optional; include only if requested or detected)*

### Opt-out mechanism

Do not ask the human which baseline harnesses to support for every repo, but make opting
out concrete:

- `.agents/bootstrap.config` may set `harness_adapters: [claude, codex]` (or `[]`). When
  present, `discover`/`apply` honor exactly that list.
- When no config exists, `discover` asks once, in plain language, and writes the answer to
  `.agents/bootstrap.config` so it is not re-asked.
- Absent any signal, generate the default baseline (excluding the optional Antigravity
  entry).

Existing harness files do not decide support. They are inspected only for migration and
custody risk:

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

### Adapter authorship boundary

The LLM decides *whether* an adapter is needed and which canonical sources it should
reflect. The **script renders the adapter body deterministically** from those tracked
sources, so regeneration is drift-free.

When a harness supports pointers to `AGENTS.md` and `.agents/*`, the adapter should point
instead of duplicating rules.

When a harness requires its own file content and cannot point to canonical files, the
script generates the adapter from tracked canonical sources. The adapter may be tracked if
the harness requires it, but it must include a generated-file header:

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

Before a checks script becomes durable support material, it must be executed once and its
result recorded. (This is what promotes a CI *command* from claim to authority — see CI
nuance.)

Discovery must also capture baseline health:

- current commit
- commands run
- pass/fail status
- known failures, if any
- commands skipped and why

This lets future agents distinguish pre-existing breakage from regressions they introduced.

The verification entry point also warns when repo facts may be outdated. That warning is
computed by the **single canonical staleness function** (see below), not re-derived inline.

```text
WARNING: Repo facts used by agent playbooks may be outdated. Run bootstrap-agents update
before relying on them.
```

## Canonical Staleness Definition

There is exactly one definition of "outdated," implemented in `lib/Staleness.ps1` and
consumed everywhere (the checks script's warning, the Outdated-Facts policy, `update`).
Prose sections reference it; they do not restate the rule.

Inputs: the `validated_against` commit recorded in `.agents/repo-map.md`, current `HEAD`,
and the set of fact-bearing paths (CI/build/test/package files, project-structure files,
canonical guidance, adapter templates).

Verdict is one of:

- `fresh` — no fact-bearing path changed since the stamp and any commit threshold is not
  exceeded.
- `stale` — a fact-bearing path changed, or the threshold is exceeded.
- `unknown` — preconditions for a reliable answer are not met (see below).

### Preconditions and graceful degradation

The staleness calc requires git history: an attached, non-shallow checkout and a valid
stamp. When those are absent (e.g. a file-copy clean test, a shallow clone, or a missing
stamp), it must return `unknown` and print:

```text
Freshness unknown — git history unavailable or validation stamp missing.
```

It must never silently report `fresh` when it cannot actually tell.

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`: short tracked root-level source of truth for future agents.
- `.agents/repo-map.md`: observed repo mechanics and architecture map.
- `.agents/playbooks/*.md`: task-specific recipes, such as add-module, fix-bug,
  review-change, change-deployment.
- `.agents/checks.ps1` or `.agents/checks.sh`: one verification entry point.
- `.agents/artifact-manifest.md`: git custody and generated-artifact report.
- `.agents/test-current.md`: exact manual steps for a new-session test in the current
  checkout.
- `.agents/test-clean.md`: exact manual steps for a new-session test in a clean local copy.
- `.agents/grade-agent-run.ps1`: acceptance grader (contract below).
- `.agents/bootstrap.config`: per-repo settings (harness opt-out, deny-list extensions,
  discovery budgets, staleness threshold).
- Optional harness adapters generated from tracked sources.

Each generated repo-fact artifact must include a validation stamp:

```text
validated_against: <commit-sha> on <date>
```

For preview artifacts outside a repo, use:

```text
validated_against: preview, <date>
```

## Acceptance Grader Contract

The grader resolves the v2 contradiction where a `.ps1` was implied to judge inherently
subjective criteria. It has two layers.

**Layer 1 — Objective (deterministic, scriptable).** `grade-agent-run.ps1` checks only
machine-decidable signals and exits nonzero on hard failure:

- Did the agent run the repo's verification entry point (or explicitly report why not)?
- Did changes stay within the declared task scope (changed-file set vs. scope)?
- Is there a final-answer / executive-summary section present?
- Were any deny-listed secret files modified or their values surfaced?

Inputs: the agent's run/result file and the repo path. Output: an objective pass/fail
report plus a populated checklist scaffold for layer 2.

**Layer 2 — Subjective (human or LLM judge, never regex).** The script emits a checklist;
a human or a separate LLM judge fills it in:

- Did the agent find the correct playbook?
- Did it avoid treating unvalidated docs as authority?
- Did it ask only necessary product-scope questions?
- Did it keep changes consistent with the repo's architecture?

The script never scores layer 2. It only structures it. This keeps deterministic claims
deterministic and judgment claims honest.

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

Harness adapters should point to `AGENTS.md` and tracked `.agents/` files when possible.
Generated adapters should be treated as derived outputs from canonical guidance.

## Apply Semantics

`apply` is the only mode that writes durable repo guidance, so its safety rules are
explicit:

- **Refuse-or-route.** If durable guidance already exists in the target repo, `apply`
  refuses and instructs the human to run `update`. It never silently overwrites
  human-reviewed guidance.
- **Atomic write.** All artifacts are written to a staging area first, then moved into
  place as a unit. A failure partway through leaves the repo unchanged — never
  half-written, half-tracked.
- **Custody-verified.** After writing, `apply` regenerates `artifact-manifest.md` and
  confirms each artifact is tracked (or intentionally external/local-only). It reports any
  artifact that future agents are expected to obey but that is not tracked.

## Git Custody Requirement

The bootstrap must identify every file future agents are expected to obey or use and report
whether each is:

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

### Self-referential note

This very repo (`D:\source\AgentGovernanceBootstrap`) is a *preview*: it holds the plan
lineage, not yet the implemented tool, and its artifacts live outside any target repo. That
is legitimate preview mode. Real adoption in any target repo means the guidance is in-repo
and tracked, or it has no more authority than the unvalidated docs it replaces.

## Outdated Repo Facts Triggers

Repo fact artifacts are considered outdated exactly when the Canonical Staleness Definition
returns `stale`. The fact-bearing paths it watches include:

- CI/build/test/package files
- project structure or app entry points
- `.agents/` playbooks or `AGENTS.md` changed manually
- verification commands
- generated harness adapter templates
- an explicit human request to update

A commit-count threshold may be set in `.agents/bootstrap.config`, but time alone is not a
freshness source.

When the verdict is `stale`, agents should re-run discovery in `update` mode before relying
on affected playbooks. When the verdict is `unknown`, agents should treat facts as
potentially outdated and say so.

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
12. Secret-safety report: deny-listed files found (path/existence only), confirmation no
    values were read.

The human can approve, reject, or adjust this before durable repo guidance is written.

Open questions must be written for a non-developer. Avoid file-format jargon unless it is
unavoidable, and explain the impact in plain English.

## Current-Checkout Test

The current-checkout test proves the generated guidance works in a new agent session using
the current working copy.

The bootstrap should generate exact steps like:

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

It must not require a remote. **It prefers `git clone <local-path>`** so the copy retains
its `.git` directory — without it, the git-dependent features (staleness calc, "record git
status and current commit", any git-using playbook step) fail in the very environment meant
to validate the guidance, and the staleness calc will correctly report `unknown`. A
flat file-copy is a documented fallback only for repos where git history demonstrably does
not matter.

The bootstrap should generate exact steps like:

```text
1. Run:
   .\bootstrap-agents.ps1 test-clean <repo> <clean-local-copy>

2. Open a brand-new agent session in <clean-local-copy>.
3. Paste the generated prompt.
4. Paste the final answer into the generated result file.
5. Run the generated grading command.
```

These tests evaluate the agent-guidance system, not the application itself.

### Defining "fresh agent context"

A test is only valid in a genuinely fresh context:

1. A new session with no prior conversation history.
2. No custom instructions or system-prompt overrides beyond what the repo's `AGENTS.md`
   loads.
3. A clean workspace — preferably the cloned clean copy — so no uncommitted local-only
   files from prior runs interfere.

Pass/fail is determined by the Acceptance Grader Contract (objective layer scripted,
subjective layer via human/LLM checklist).

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

# PART 2 — Implementation Plan

This part is concrete enough to build the tool. PowerShell is primary (Windows repo); a
`.sh` parity pass is a follow-up.

## Command contracts

| Mode | Inputs | Preconditions | Side-effects | Outputs | Exit codes | Refuses when |
|---|---|---|---|---|---|---|
| `discover` | `<repo>` | repo readable | none (read-only) + writes review packet to a non-durable location | review packet incl. secret-safety report, baseline health | 0 ok / 2 read error | repo missing |
| `apply` | `<repo>` (after approval) | review packet exists; approval given | atomic write of artifacts; regen manifest | written artifacts + custody report | 0 ok / 3 refused / 4 write error | durable guidance already exists (→ `update`) |
| `test-current` | `<repo>` | artifacts exist | writes `test-current.md`, scaffolds `test-results/` | printed steps | 0 / 5 missing artifacts | no artifacts |
| `test-clean` | `<repo> <clean-copy>` | git available (preferred) | creates clean copy (clone preferred) | printed steps + clean copy | 0 / 6 copy error | target path occupied |
| `update` | `<repo>` | durable guidance exists | none until approval; then atomic write | proposed diff vs. current | 0 / 7 nothing-to-do | no existing guidance (→ `apply`) |

All modes share: refuse cleanly (nonzero, plain message) when unimplemented or
precondition-unmet; never partially write.

## Script module layout

```
bootstrap-agents.ps1        # CLI dispatch only; parses mode, delegates
lib/
  Discover.ps1              # orchestrates read-only discovery, builds review packet
  SecretScan.ps1            # deny-list; returns flagged paths + cleared allow-list
  GitFacts.ps1              # status, current commit, changed-paths-since-stamp
  Apply.ps1                 # staging + atomic move-into-place + custody verify
  Staleness.ps1             # the one canonical fresh/stale/unknown verdict
  Grade.ps1                 # objective layer + checklist scaffold emit
  Render.ps1                # deterministic artifact/adapter templating
templates/                  # artifact skeletons (see below)
```

`SecretScan.ps1` runs before any LLM read. `Apply.ps1` is the only writer of durable
guidance. `Staleness.ps1` is imported by both the generated `checks.ps1` and `update`.

## Artifact templates

Skeletons under `templates/`, each carrying the `validated_against:` stamp (and, for
adapters, the generated-file header):

- `AGENTS.md` — mission, source-of-truth order, task classification, playbook triggers,
  ask-the-human triggers, verification entry point, final-answer expectations, pointers.
- `repo-map.md` — observed mechanics, architecture, per-project sections, validation stamp.
- `playbooks/*.md` — recipe shape: when-to-use, steps, verification, scope boundaries.
- `checks.ps1` — runs derived checks; calls `Staleness.ps1`; prints freshness verdict.
- `artifact-manifest.md` — custody table (tracked/ignored/generated/local-only/
  install-derived/missing).
- `test-current.md`, `test-clean.md` — generated step lists.
- `grade-agent-run.ps1` — objective checks + checklist scaffold.
- `bootstrap.config` — `harness_adapters`, `deny_list_extra`, `discovery_budget`,
  `staleness_threshold`.
- adapters (`CLAUDE.md`, Codex/Cursor/Aider files) — pointer when supported, else rendered
  body + generated-file header.

## Deterministic / LLM boundary table

| Step | Owner |
|---|---|
| List tracked / ignored files, git status, current commit | Script |
| Secret deny-list scan; decide LLM-readable allow-list | Script |
| Read & interpret cleared files; assess docs/agent files | LLM |
| Classify evidence; flag conflicts | LLM (script records classes) |
| Decide whether an adapter is needed | LLM |
| Render adapter/artifact bodies from canonical sources | Script |
| Compose checks from observed commands | LLM proposes, Script records |
| Execute checks once; capture baseline health | Script |
| Compute staleness verdict | Script |
| Atomic write + custody verify | Script |
| Draft playbooks, plain-language questions, summaries | LLM |
| Objective acceptance grade | Script |
| Subjective acceptance grade | Human / LLM judge |

## Hooks

Hook installation remains opt-in, reversible, and explicitly approved. The repo tracks
hook *source* files and an installer/uninstaller script; `.git/hooks` runtime files are
never the tracked authority.

---

# PART 3 — Build & Verification Sequence

An ordered path from spec to a proven, self-bootstrapped tool. Each step is independently
testable.

1. **Skeleton + dispatch.** `bootstrap-agents.ps1` parses all five modes; each unimplemented
   mode refuses cleanly with a plain message and a distinct exit code.
2. **`discover`.** Implement `SecretScan.ps1` (deny-list, path-only, allow-list) and
   `GitFacts.ps1`, then `Discover.ps1` to assemble the review packet — including the
   secret-safety report and baseline health.
3. **`apply`.** Implement `Apply.ps1`: staging, atomic move-into-place, refuse-or-route on
   existing guidance, custody verification via regenerated manifest.
4. **`checks.ps1` + staleness.** Implement `Staleness.ps1` (fresh/stale/unknown with
   precondition handling), and generate a `checks.ps1` that runs derived checks and prints
   the verdict.
5. **`grade-agent-run.ps1`.** Implement `Grade.ps1`: objective layer (verification run,
   scope adherence, summary present, no secret exposure) + checklist scaffold for the
   subjective layer.
6. **`test-current` / `test-clean`.** Generate step lists; `test-clean` prefers
   `git clone <local-path>`; confirm the staleness calc reports `unknown` in a flat
   file-copy.
7. **`update`.** Diff discovery vs. existing artifacts into a review packet; never silent
   overwrite.
8. **Self-bootstrap dogfood.** Run the tool against a real pilot repo (e.g.
   `D:\source\ExchangeAdminWeb`, named in `artifact-manifest.md`) in preview mode. Confirm:
   review packet is coherent; secret-safety leaked no values; baseline health captured; a
   fresh-agent acceptance run passes the objective grade and produces a sane subjective
   checklist.

## Verifying this document (v3 itself)

Because v3 is a spec, its "test" is an internal consistency pass — all of which hold:

- Every artifact in *Generated Artifacts* has a Part 2 template — including
  `grade-agent-run.ps1` (the v2 gap).
- Every mode in *Operating Modes* has a Part 2 command contract.
- No section asserts a mandate (secrets, overwrite, grading, staleness) without a
  mechanism.
- Every review finding maps to a concrete change (table below).

## Traceability — review findings → fixes

| Finding | Section that resolves it |
|---|---|
| H1 grader undefined / not machine-gradable | Acceptance Grader Contract (two layers); template + contract added |
| H2 secret-safety had no mechanism | Secret-Safe Discovery (script-owned deny-list, allow-list, redaction) |
| H3 `apply` semantics + atomicity undefined | Apply Semantics; `apply` command contract |
| M1 clean-copy breaks git features | Clean-Local-Copy Test (clone preferred, file-copy fallback) |
| M2 staleness defined in 3 places | Canonical Staleness Definition (single source) |
| M3 outdated-facts assumes git history | Staleness preconditions → `unknown` + graceful message |
| M4 harness opt-out undefined | Harness opt-out mechanism via `bootstrap.config` |
| L1 adapter authorship ambiguous | Adapter authorship boundary (LLM decides, script renders) |
| L2 CI commands treated as near-top authority | CI nuance (config = exists; command = claim until executed) |
| L3 no discovery budget | Discovery budget subsection |
| L4 self-referential custody gap | Git Custody → self-referential note |
