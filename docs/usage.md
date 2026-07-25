# Usage

## One-time setup, per machine

1. Install Git and Python 3.10+. Windows:
   `winget install Git.Git Python.Python.3.12`.
2. Clone this toolkit — `git clone
   https://github.com/roethlar/AgentGovernanceBootstrap.git
   ~/dev/AgentGovernanceBootstrap` (the LAN gitea mirror
   `http://q:3000/michael/AgentGovernanceBootstrap.git` also works as a
   faster source; GitHub is canonical). Even this is optional: both flows
   self-provision by cloning when no local copy exists.

Your half of the freshness bargain: push this repo to GitHub when you change
it — toolkit changes that are not pushed do not propagate to your other
machines. (Push the gitea mirror too when convenient; it is never
authoritative.)

## Starting a brand-new project (one command)

```bash
~/dev/AgentGovernanceBootstrap/tools/new-project <project-dir> [hint]
```

(Windows: `tools\new-project.cmd`.) It creates the directory, runs
`git init`, installs the governance set staged but uncommitted, then offers
to launch a detected agent harness there with a kickoff prompt pointing at
`procedures/setup.md` — the agent asks the setup questions, drafts the
judgment files, and makes the first commit. The optional hint is a one-line
description of the project; it primes that conversation so it opens with a
confirmation instead of an interrogation. If the directory already has
governance the command refuses and tells you to refresh instead.

## Bootstrapping a repo (an existing repo, with or without governance to migrate)

Open a fresh agent session in the target repo and paste:

```text
Read <path-to-AgentGovernanceBootstrap>/procedures/bootstrap.md and follow it.
```

The same line works on any harness. Codex CLI headless example (prompt via
stdin — the argv form has hung):

```bash
echo "Read ~/dev/AgentGovernanceBootstrap/procedures/bootstrap.md and follow it." | codex exec
```

The agent syncs the toolkit, discovers the repo live, inventories existing
governance if any (you approve the reconciliation as a plain-English table),
drafts the repo-specific `.agents/` files, and presents
`.bootstrap-tmp/drafts/approval-summary.md` — the one file you review. It
starts with `Approve`, `Approve after edits`, or `Do not approve yet`, and
is written so you never need to read code, diffs, or JSON to decide. On your
approval: drafts are copied, `tools/refresh.py --stage-only` installs the
shipped set, and everything lands as ONE scoped commit. Pushing follows the
push policy you choose at approval time.

## Keeping a repo current

From the repo root, any time you're working in it:

```bash
py -3 ~/dev/AgentGovernanceBootstrap/tools/refresh.py      # Windows
python3 ~/dev/AgentGovernanceBootstrap/tools/refresh.py    # macOS/Linux
```

or type `/update-governance` in a Claude Code session (codex/grok/agy: the
`update-governance` skill, installed under `.agents/skills/`; agy needs the
workspace trusted first). Seconds, no agent
judgment involved: the script syncs the toolkit (offline it proceeds on the
local copy and says so), installs new shipped artifacts, updates stale ones,
removes retired ones, and commits once with the toolkit version in the
message. Installed governance is toolkit-owned: a file that matches no
shipped version is drift — whoever wrote it — and is restored to the shipped
version, reported as a DRIFT line naming the commits that introduced it
(uncommitted changes on touched paths make the run refuse instead, so
nothing uncommitted is ever destroyed). If it flags `AGENTS.md` as a foreign
governance file, the repo needs the bootstrap flow above, not a refresh.

A repo governed before the per-repo policy file existed gets it backfilled:
refresh writes `.agents/push-policy.md` (ask before pushing) if it is
missing, and prints an ACTION line telling you what to set. Once the file
exists — however you have edited it — refresh ignores it for good.

When retiring a file empties its directory, the run lists the empty
directories and asks once — `[Y/n]`, Enter accepts — before removing them.
Answer no and they stay. Runs that aren't interactive (loops, CI) list them
and remove nothing.

A repo you don't touch stays stale, and that's fine — it catches up the next
time you work there.

## Filing feedback

When a session (here or in a governed repo) confirms a toolkit defect or a
governance rule worth generalizing, the agent drafts a GitHub issue from the
templates in `.github/ISSUE_TEMPLATE/` and files it **only on your go**:

```bash
gh issue create -R roethlar/AgentGovernanceBootstrap --title "..." --body-file ...
```

Issues are public: no secrets, tokens, private hostnames, or personal data —
evidence is cited by path and commit hash. Triage by reading open issues and
closing each with a reason; the closed list is the ledger.

## Verifying this repo

```bash
py -3 -m unittest discover -s tests -v    # Git Bash on Windows; python3 elsewhere
```
