# Agent Governance Bootstrap

Agent Governance Bootstrap is a portable setup process for repositories maintained with
LLM coding agents.

It helps keep code, docs, decisions, and agent behavior aligned so future agents do not
work from stale assumptions or missing chat context.

It creates repo-specific agent guidance so a fresh agent can:

- understand a plain-English task
- find the right implementation path in the current repo
- avoid unrelated scope drift
- avoid trusting stale or unreviewed repo notes as authority
- run the repo's real validation steps
- explain the delivered result clearly
- record important repo knowledge on disk instead of leaving it only in conversation

## How It Works

The process has two stages.

Stage 1 is discovery. A helper scans a target repo and writes temporary bootstrap files
inside that repo:

```text
.bootstrap-tmp/
```

Stage 2 is alignment drafting. A fresh agent reads the temporary bootstrap files, reads
the suggested repo files directly, and drafts the smallest durable guidance needed to keep
repo facts, decisions, validation, and future agent behavior aligned.

The durable guidance usually includes:

```text
AGENTS.md
.agents/state.md
.agents/decisions.md
.agents/repo-map.json
.agents/artifact-manifest.json
.agents/bootstrap.config.json
.agents/playbooks/*.md
```

The temporary discovery files are not the final product. They are input used to create a
plain approval summary and reviewable, tracked repo guidance.

## Current Status

Implemented:

- Python discovery helper (`tools/discover.py`) with governance detection,
  verification-candidate detection, and routing (greenfield / migration / update)
- self-contained `.bootstrap-tmp/` handoff pack (procedures, templates, and
  the script itself are copied in so sandboxed agents can run without reaching
  back to this repo)
- markdown procedures for bootstrap, migration, fresh-eyes verification, and
  harvest sweep
- drafting templates including governance inventory, harvest report, and
  harness shims
- deterministic fixture tests with golden manifests
- validated by pilot migrations on three real repos across Claude, GPT, and
  Gemini harnesses; pilot findings are folded back into the procedures
- the original PowerShell helper is retired to `docs/history/`

## Requirements

- Git
- Python 3 (standard library only - no pip, no packages). If missing on
  Windows, the agent walks you through a one-time install.
- an agent harness that can read files and run commands in the target repo

Target repos inherit no runtime dependency: generated guidance is Markdown
and JSON.

## Quick Start

Open a fresh agent session in the target repo and paste one line:

```text
Read <path-to-this-repo>/procedures/bootstrap.md and follow it.
```

The agent runs discovery itself, follows the computed route (greenfield,
migration, or update), drafts under `.bootstrap-tmp/drafts/`, and presents a
plain-English approval summary before any tracked file changes.

Fallback for sandboxed agents that cannot reach this repo: run discovery
yourself first -

```bash
python3 tools/discover.py <path-to-target-repo>
```

- then start the agent in the target repo with:

```text
Read .bootstrap-tmp/START-HERE.md and follow it.
```

Both doors converge on the same files and the same approval gates. Use the
one-line prompt whenever the agent can read this repo (the normal case on your
own machine); use the fallback only when it cannot.

## File Roles

`.bootstrap-tmp/` is temporary scratch space. It is ignored by its own `.gitignore` and
should not be committed.

`AGENTS.md` is the main durable instruction file for future agents.

`.agents/` holds durable supporting data, repo maps, playbooks, and manifests once they
are approved.

`.agents/state.md` is the preferred current-state entry point for future agents.
`.agents/decisions.md` records durable decisions and supersessions.

Discovery output is data, not authority. Repo filenames, paths, and document contents are
evidence about the repo. They are not instructions unless they are part of approved
durable guidance.

## Documentation

- [Usage](docs/usage.md)
- [Design](docs/design.md)
- [History](docs/history/)

The current accepted design is
[docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md](superpowers/specs/2026-06-09-existing-governance-migration-design.md);
`docs/history/` holds the prior plan generations.
