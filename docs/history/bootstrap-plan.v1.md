# Portable Agent-Governance Bootstrap Plan

validated_against: draft process, 2026-06-08

## Purpose

Create a reusable process that can be applied to any repository to generate and maintain repo-specific agent guidance. The goal is for a fresh agent to turn a plain-English request into working, validated code while minimizing drift, regressions, stale guidance, and untracked local process state.

This process is portable. It does not assume repo-specific rules in advance. Repo-specific rigidity is generated after discovery, evidence classification, and human review.

## Stable Agent Mission

Future agents should be guided toward this behavior in every repo:

- Understand the human's natural-language request.
- Discover the correct implementation path for the current repo.
- Make changes that fit the repo's actual architecture and workflows.
- Avoid regressions and unapproved scope expansion.
- Validate with the repo's real checks.
- Explain the delivered result in plain English, with executive-level clarity.

## Operating Modes

The bootstrap supports two modes:

- `init`: no durable agent guidance exists yet. Produce a review packet, then generate artifacts after approval.
- `update`: durable guidance already exists. Re-run discovery, compare against current artifacts, and produce a proposed diff. Never silently overwrite human-reviewed guidance.

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

## Derived Verification

The generated verification entry point must be derived from observed repo mechanics:

- Prefer CI commands when available.
- Use package/build/test scripts where CI delegates to them.
- Treat docs as secondary if they disagree with CI.
- Do not invent checks that are not supported by the repo.

Before a checks script becomes durable guidance, it must be executed once and its result recorded.

Discovery must also capture baseline health:

- current commit
- commands run
- pass/fail status
- known failures, if any
- commands skipped and why

This lets future agents distinguish pre-existing breakage from regressions they introduced.

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`: short tracked root-level source of truth for future agents.
- `.agents/repo-map.md`: observed repo mechanics and architecture map.
- `.agents/playbooks/*.md`: task-specific recipes, such as add-module, fix-bug, review-change, change-deployment.
- `.agents/checks.ps1` or `.agents/checks.sh`: one verification entry point.
- `.agents/artifact-manifest.md`: git custody and generated-artifact report.
- Optional tool adapters generated from tracked sources, such as Claude commands, Codex prompts, or hook installers.

Each generated artifact must include a staleness stamp:

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

Tool adapters should point to `AGENTS.md` and tracked `.agents/` files rather than duplicating large rule sets.

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

## Staleness And Re-Bootstrap Triggers

Generated artifacts should be considered stale when:

- `HEAD` differs from the artifact staleness stamp by a human-defined commit threshold
- CI/build/test/package files changed since validation
- project structure or app entry points changed
- `.agents/` playbooks or `AGENTS.md` changed manually
- verification commands changed
- the human requests re-bootstrap

When stale, agents should re-run discovery in `update` mode before relying on affected playbooks.

## Bootstrap Review Packet

Before writing durable repo guidance, produce a compact review packet:

1. Repo mechanics observed.
2. Baseline health and commands run.
3. Existing guidance found, with git status and trust status.
4. Proposed agent artifacts.
5. Proposed playbooks.
6. Proposed verification entry point.
7. Evidence conflicts and promotion requests.
8. Open questions needed to avoid wrong durable rules.
9. Git custody risks.
10. Staleness/update policy proposal.

The human can approve, reject, or adjust this before durable repo guidance is written.

## Pilot Flow

For a pilot repo:

1. Run discovery read-only.
2. Produce the review packet.
3. Get human review.
4. Generate preview artifacts outside or inside the repo as directed.
5. If adopting for real, move approved artifacts into the repo and track them.
6. Execute the generated verification entry point once.
7. Verify artifact custody.
8. Test with a realistic held-out plain-English request using a fresh agent context.

## Bootstrap Acceptance Test

Each mature bootstrap should include at least one held-out task the artifact author did not design around.

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
- Identify stale guidance before relying on it.
- Distinguish baseline failures from new regressions.
- Produce a plain-English executive summary.
- Leave durable guidance tracked in git when artifacts are intended to live in the repo.
