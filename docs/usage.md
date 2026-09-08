# Usage

Install Git and Python 3.10+, then clone
`https://github.com/roethlar/Bixi.git`. Use that checkout's tools for
governed repositories; this repository develops the toolkit.

## New project

Run `<bixi>/tools/new-project <project-dir> [hint]`
(`tools\new-project.cmd` on Windows).
It initializes Git and stages governance. Continue setup in the current
agent; an interactive shell can offer a harness launch. The agent uses the
project hint and established push policy, asks only for missing information,
and makes the first scoped commit.

## Existing repository

In the target's current agent, request:

```text
Read <bixi>/procedures/bootstrap.md and follow it.
```

Bootstrap discovers relevant governance, drafts repo-owned guidance and
presents the changes requiring a decision. Existing authority stands.
Refresh installs the shipped set; approved legacy replacement uses
`--force`. Judgment files and installation share one scoped commit.
Follow repo branch policy; branch work ends after merge and local/remote
deletion. Hook trust and publishing follow their existing authority.

## Refresh

From the target root, run `<python> <bixi>/tools/refresh.py`, or invoke
`update-governance` in the agent. Use Python 3.10+; Windows prefers `py -3`.

Refresh syncs the toolkit, reconciles shipped artifacts and commits its
scoped changes. Known versions update; committed drift is restored with
provenance. Uncommitted changes on affected paths refuse. A foreign
AGENTS.md requires migration or explicitly requested replacement.
Repo-owned seeded policy files are preserved.

For read-only inspection, use
`<python> <bixi>/tools/refresh.py --plan-json -`.
This neither syncs nor changes either checkout. A saved plan can later be
applied; affected inputs are checked while unrelated changes are tolerated.
Use `--lint-only` for governance-reference findings without installation.

Retirement removes directories it just emptied. `--prune` also removes
empty retired directories left by older runs; nonempty directories stay.
Noninteractive runs print actionable findings and a procedure pointer;
an existing agent can resolve them without launching another session.

## Feedback and verification

File a confirmed toolkit issue only with explicit authority, using
`gh issue create -R roethlar/Bixi --title "..." --body-file <file>`.
Use redacted evidence; do not file speculative or empty reports.

This repo's verification entry point and interpreter guidance live in
`.agents/repo-guidance.md`. Before committing template changes, run
`<python> tools/record-history.py` to register outgoing source hashes.
