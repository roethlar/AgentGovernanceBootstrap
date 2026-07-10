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

## Bootstrapping a repo (first time, or migrating existing governance)

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
local copy and says so), installs new shipped artifacts, updates
provably-unmodified stale ones, removes retired ones, and commits once with
the toolkit version in the message. Owner-modified files are FLAGGED, never
touched — resolve flags yourself or hand them to an agent with instructions.
If it flags `AGENTS.md` as "not a toolkit instance", the repo needs the
bootstrap flow above, not a refresh.

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
