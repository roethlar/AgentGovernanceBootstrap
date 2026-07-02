# Usage

## One-time setup

Globally, once: create the harvest dropbox - an empty private git repo pushed
to your remote. (Optional. Without one, harvest reports use the in-repo
fallback and nothing is lost.)

On each machine you bootstrap from:

1. Install Git and Python 3. Windows:
   `winget install Git.Git Python.Python.3.12`. macOS and Linux usually have
   both already.
2. Clone this process repo from a canonical remote - gitea on the LAN
   (`http://q:3000/michael/AgentGovernanceBootstrap.git`) or GitHub anywhere
   (`https://github.com/roethlar/AgentGovernanceBootstrap.git`) - to
   `~/dev/AgentGovernanceBootstrap`. (Even this is optional: the kickoff
   procedure self-provisions by cloning when no local copy exists.)
3. Optional: clone the harvest dropbox repo, then create an untracked
   `harvest.config.json` in this repo's root:
   `{"harvestRepoPath": "/path/to/harvest-repo"}`. The config file is what
   makes the dropbox discoverable - the clone alone does nothing.
4. Optional: allowlist the dropbox path in your harness permissions so
   delivery does not prompt.

Freshness is automatic: every bootstrap run starts by syncing this repo from
the canonical remotes (fast-forward only; offline or diverged clones proceed
as-is with a plain-English flag in the approval summary). Your half of the
bargain: push this repo to BOTH remotes when you change it - toolkit changes
that are not pushed do not propagate to your other machines.

## Normal flow (local agent)

Open a fresh agent session in the target repo and paste:

```text
Read <path-to-AgentGovernanceBootstrap>/procedures/bootstrap.md and follow it.
```

The agent: runs `tools/discover.py` against the repo, reads the generated
`.bootstrap-tmp/` evidence, follows the computed route, drafts guidance under
`.bootstrap-tmp/drafts/`, runs the fresh-eyes check when migrating, and
presents a plain-English approval summary. Nothing outside `.bootstrap-tmp/`
changes until you approve. On approval the agent copies the files into place
and makes one scoped commit whose message the summary announced; pushing
stays yours.

## Fallback flow (sandboxed agent)

Run discovery yourself:

```bash
python3 tools/discover.py <path-to-target-repo>
```

On Windows prefer `py -3 tools/discover.py ...`: a `python3` found on PATH is
often the Microsoft Store stub, which prints "Python was not found" even
though the real launcher works fine.

The supported floor is Python 3.9 (the macOS system interpreter), and the
toolkit's product code stays within it. Homebrew installs newer versions
under versioned names (`python3.14`) that a plain `python3` never resolves
to; nothing in the toolkit requires them, but if a task ever needs a newer
interpreter, probe the versioned names explicitly.

Then start the agent in the target repo with:

```text
Read .bootstrap-tmp/START-HERE.md and follow it.
```

Small or local models: prefer this fallback flow (START-HERE.md is shorter and
self-contained) and run them with a plugin-free harness profile - heavy plugin
stacks can distract a weak model from the kickoff instruction entirely.

## Starting over or switching agents

Delete the target repo's `.bootstrap-tmp/` before re-running the bootstrap
with a different agent. Drafts deliberately survive discovery re-runs (so a
mid-session refresh never loses work), which means a new agent would otherwise
inherit the previous agent's drafts.

## Routes

Discovery computes one of three routes, shown in `START-HERE.md`:

- **greenfield** - no governance found; standard drafting workflow.
- **migration** - existing governance found (STATE.md, DEVLOG.md, agent
  contracts, command files...). The agent inventories every artifact with a
  verdict - migrate / supersede / leave - and you approve the
  reconciliation as a plain-English table.
- **update** - the repo already uses the standard `.agents/` layout; the
  repo's own `AGENTS.md` handoff rule applies.

## What you review

One file: `.bootstrap-tmp/drafts/approval-summary.md`. It starts with
`Approve`, `Approve after edits`, or `Do not approve yet`, and is written so
you never need to read code, diffs, or JSON to decide. For migrations it
includes the governance inventory and the fresh-eyes verification result.

## What gets committed in target repos

The bootstrap commit happens automatically once you approve, and contains
only the approved guidance: `AGENTS.md`, `.agents/*`, harness shims, command
wrappers, and supersession banners on old governance files. Unrelated
working-tree changes are never swept in, `.bootstrap-tmp/` never gets
committed (it self-ignores), and pushing is yours: the agent asks once after
committing, naming your remotes when there are several, and pushes only what
you name.

## Harvest (optional, expected to be rare)

If a migration uncovers a governance rule earned from a real incident, the
agent may record it - at most three ideas, never padding; producing no report
is the normal, correct outcome. After your approval the report goes to your
harvest dropbox repo (a plain git repo whose local path you put in this
repo's untracked `harvest.config.json`), written append-only as a new file,
or - when no dropbox is reachable - into that repo's own `.agents/harvest.md`,
where it travels with the repo. When you feel like it, say "run the harvest
sweep" in a session here: ideas are judged skeptically (default: skip), you
decide each one in plain English, and outcomes are logged in
`harvest/processed.md`.

## Verifying this repo

```bash
python3 -m unittest discover -s tests -v
```

## Pilot review checklist

After a pilot run, collect: the approval summary, the drafted files, the
governance inventory (for migrations), the fresh-eyes result, the agent's
final answer, anything confusing, and whether `.bootstrap-tmp/` stayed out of
`git status --short`. Use those to decide the next fix.
