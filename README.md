# AgentGovernanceBootstrap — development source for [Bixi](https://github.com/roethlar/Bixi)

This is the working repository. The released product is **Bixi** (赑屃, the
dragon-turtle who carries stone steles for eternity); `tools/publish` mirrors
`tools/`, `templates/`, `procedures/` and `product/README.md` into it. The
public front page is [`product/README.md`](product/README.md) — edit that one
for anything a newcomer reads.

A personal governance toolkit for repositories maintained with LLM coding
agents. It keeps code, docs, decisions, and agent behavior aligned so future
agents do not work from stale assumptions or missing chat context.

Every governed repo gets the same two-layer setup:

- `AGENTS.md` — the portable constitution, identical bytes in every repo,
  installed and replaced whole by the toolkit (never hand-edited): prime
  invariants, universal invariants, the operator vocabulary, verification
  and git-safety rules.
- `.agents/` — everything repo-specific: `repo-guidance.md` (rules, reading
  order, the verification command), `state.md` (current work, with rotation
  to an archive), `decisions.md` (settled decisions), `push-policy.md`,
  and the operator playbooks (the shipped set is enumerated in
  `tools/shipped-set.json`, the toolkit's manifest).

Plus harness adapters (the `CLAUDE.md` shim, operator command
wrappers, and two hooks — the Claude Code compaction re-ground and the
blocking protect-governance pre-edit deny), shipped only where the mechanism
is verified to work (see the harness-capability record linked below).

## Install into a new project (one command)

```sh
<path-to-this-repo>/tools/new-project <project-dir> [hint]
```

(Windows: `<path-to-this-repo>\tools\new-project.cmd <project-dir> [hint]` —
verified on macOS/Linux; the Windows launcher follows the repo's documented
Windows probe contract and is unverified live until its first Windows run.)

Creates the directory, initializes Git and stages governance. Continue in
the current agent; an interactive shell can offer a harness launch. Setup
uses your hint and established push policy, asks only for missing answers,
and finishes with a scoped first commit. The launcher resolves Python.

## The two flows

**Bootstrap (judgment — an agent session).** Use the current agent in
the target repo and request:

```text
Read <path-to-this-repo>/procedures/bootstrap.md and follow it.
```

The agent syncs once, discovers relevant governance, drafts repo-specific
files and presents changes needing a decision. It reuses existing authority.
Approved drafts and installation share one scoped commit, including legacy
replacement through refresh's force option. Follow repo branch policy;
work branches require merge and deletion before completion.

**Refresh (mechanical — one command).** From any governed repo:

```bash
py -3 <path-to-this-repo>/tools/refresh.py    # or python3 on macOS/Linux
```

(or `/update-governance` in Claude Code; codex, grok, and agy sessions get
the same entry point as the `update-governance` skill, installed under
`.agents/skills/` — verified on all three). The script syncs the toolkit,
reconciles the repo to the shipped artifact set — installs what's new,
updates stale files, removes retired ones — and makes one scoped commit
recording the toolkit version. Installed governance is toolkit-owned:
committed content that matches no shipped version is drift and is restored
(or, for retired files, removed), reported as a DRIFT line naming the
commits that introduced it; uncommitted or untracked content on touched
paths makes the run refuse and change nothing. A repo gets current the next
time you work in it; there is no registry and nothing to maintain
centrally.

## Feedback

Toolkit defects and field-earned governance rules are filed as GitHub issues
on [Bixi](https://github.com/roethlar/Bixi/issues) (agents
file only on an explicit owner go; no secrets or PII — issues are public).
Open issues are the triage queue; closed issues are the outcome ledger.

## Requirements

- Git.
- Python 3.10+ (`tools/refresh.py`, stdlib only). On Windows prefer `py -3`;
  a bare `python3` on PATH is often the Microsoft Store stub.
- An agent harness that can read files and run commands (bootstrap only;
  refresh is plain Python).

Governed repos inherit no runtime dependency: installed guidance is Markdown
plus one JSON hook settings file.

## Layout

- `procedures/` — greenfield setup, bootstrap/migration for an existing
  repo, governance remediation, and the fresh-eyes check.
- `templates/` — the AGENTS template, `.agents/` file templates, shims,
  wrappers, playbooks, the hook settings.
- `tools/refresh.py` + `tools/shipped-set.json` — the refresh mechanism and
  the manifest of what ships where.

- `product/README.md` — the public front page, published as Bixi's
  `README.md`. Not read by anything in this repo.
- `docs/` — design notes, [`harness-capabilities.md`](docs/harness-capabilities.md)
  (the per-harness verify-once record), usage, and `docs/history/` (archives).

Live repo state is tracked in [`.agents/state.md`](.agents/state.md);
settled decisions in [`.agents/decisions.md`](.agents/decisions.md). The
2026-07-08 zero-based consolidation that produced this shape is recorded in
[`docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`](docs/superpowers/plans/2026-07-08-zero-based-consolidation.md).
