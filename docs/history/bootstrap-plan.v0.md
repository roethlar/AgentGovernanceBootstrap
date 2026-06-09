# Portable Agent-Governance Bootstrap Plan

## Purpose

Create a reusable process that can be applied to any repository to generate repo-specific agent guidance. The goal is for a fresh agent to turn a plain-English request into working, validated code while minimizing drift, regressions, and untracked local process state.

This process is portable. It does not assume any repo-specific rules in advance. Repo-specific rigidity is generated after discovery and human review.

## Stable Agent Mission

Future agents should be guided toward this behavior in every repo:

- Understand the human's natural-language request.
- Discover the correct implementation path for the current repo.
- Make changes that fit the repo's actual architecture and workflows.
- Avoid regressions and unapproved scope expansion.
- Validate with the repo's real checks.
- Explain the delivered result in plain English, with executive-level clarity.

## Bootstrap Inputs

The bootstrap process may inspect:

- tracked files
- ignored/local-only files
- package and build files
- CI workflows
- test projects
- app entry points
- scripts
- existing docs
- existing agent files
- hooks or hook installers

It must classify findings instead of treating all files as equal authority.

## Evidence Classes

Use these classes in discovery output:

- `observed_from_code`
- `observed_from_tests`
- `observed_from_ci`
- `observed_from_git`
- `doc_claim_unvalidated`
- `human_confirmed`
- `inferred`
- `question`

Code, tests, CI, and git state can establish repo mechanics. Existing docs and agent files are claims until validated or corroborated.

## Generated Artifacts

A completed bootstrap should produce, as appropriate for the repo:

- `AGENTS.md`: tracked root-level source of truth for future agents.
- `.agents/repo-map.md`: observed repo mechanics and architecture map.
- `.agents/playbooks/*.md`: task-specific recipes, such as add-module, fix-bug, review-change, change-deployment.
- `.agents/checks.ps1` or `.agents/checks.sh`: one verification entry point.
- `.agents/artifact-manifest.md`: git custody report for guidance files.
- Optional tool adapters generated from tracked sources, such as Claude commands, Codex prompts, or hook installers.

## Git Custody Requirement

The bootstrap must identify every file future agents are expected to obey or use and report whether each is:

- tracked
- ignored
- generated
- local-only
- install-derived
- missing

Ignored or local-only files must not silently become durable repo authority. Runtime hooks under `.git/hooks` cannot be tracked directly; repos should track hook source files and installer scripts instead.

## Bootstrap Review Packet

Before writing durable repo guidance, produce a compact review packet:

1. Repo mechanics observed.
2. Existing guidance found, with git status and trust status.
3. Proposed agent artifacts.
4. Proposed playbooks.
5. Open questions needed to avoid wrong durable rules.
6. Git custody risks.

The human can approve, reject, or adjust this before repo guidance is written.

## Pilot Flow

For a pilot repo:

1. Run discovery read-only.
2. Produce the review packet.
3. Get human review.
4. Generate repo-specific artifacts outside or inside the repo as directed.
5. Verify artifact custody.
6. Test with a realistic plain-English request.

## Success Criteria

A fresh agent can:

- Start from a plain-English request.
- Find the correct repo-specific playbook.
- Avoid trusting unvalidated docs.
- Avoid inventing out-of-scope behavior.
- Make changes consistent with the repo.
- Run the right verification.
- Produce a plain-English executive summary.
- Leave durable guidance tracked in git when artifacts are intended to live in the repo.
