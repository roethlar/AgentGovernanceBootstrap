# Filing a Bug Report (canonical recipe)

When a run surfaces a defect in the AgentGovernanceBootstrap product — its code
(e.g. `tools/discover.py`) or its procedures — file a structured report to the
shared dropbox so the defect is captured centrally, reachable from any machine.
This is the single canonical recipe; other procedures point here, they do not
duplicate it.

This runs the same whether you found the bug dogfooding the toolkit in its own
repo or running it against a foreign target repo. The toolkit is meant to be
universally applicable, so a defect is a defect regardless of which repo exposed
it.

## When to file

- File only a defect you have PROVEN with a citable command or observation. A
  suspected problem you cannot demonstrate is an assumption — label it, or verify
  it first. The evidence rule applies: a durable claim about a defect must cite
  what proved it active, not merely plausible.
- A defect in the product, not your own mistake this run. If the code/procedure
  behaved correctly and you misread it, there is no bug.

## Write the report (auto, no gate)

Drafting the file is not a publish, so do it without asking. Use
`templates/bug-report.template.md` and its discipline. Name the file
`<source-repo>-<slug>-<YYYY-MM-DD>.md`, where `<source-repo>` is the repo you were
running in when you found the bug and `<slug>` is a few hyphenated words for the
defect (e.g. `AgentGovernanceBootstrap-playbook-probe-2026-06-22.md`). The slug
keeps two same-day reports for one repo from colliding.

## File it to the dropbox

The dropbox is `agent-harvest` (canonical on GitHub at
`roethlar/agent-harvest`, default branch `main`); bug reports live under its
`bugs/` folder. The local clone path, if any, is in this repo's untracked
`harvest.config.json` (`harvestRepoPath`). Bug files are append-only: never
overwrite or edit an existing `bugs/` file; if the name already exists, append
`-2` (then `-3`, …).

Filing a report off this machine — by either path below — publishes it. Ask the
owner once, in one line, before the publishing step. Writing the local file is
not the publish; the commit/push or the direct API write is.

### Preferred — no clone, via `gh`

If `gh` is installed and authenticated (`gh auth status`), write straight to
GitHub without a local clone. This commits directly to `main`, so it IS the
publish — get the owner's go first, then:

```
gh api -X PUT repos/roethlar/agent-harvest/contents/bugs/<name>.md \
  -f message="bug: <short title>" \
  -f branch=main \
  -f content="$(base64 -i <local-report-file>)"
```

(`content` must be base64; `base64 -i` on macOS, `base64 -w0` on GNU.) If the
PUT fails because the path already exists, rename per the append-only rule and
retry.

### Fallback — local clone

If `gh` is unavailable or unauthed: ensure a local clone of the dropbox. Use
`harvestRepoPath` if it is set and on disk; otherwise clone
`https://github.com/roethlar/agent-harvest.git` to a path the owner names (or
`~/dev/agent-harvest`). Before reading or writing, sync fast-forward-only the
same way the harvest sweep does (`git -C <clone> ls-remote --exit-code <remote>
HEAD`, then `fetch` and `merge --ff-only`) so you are not writing onto a stale
tree. Write the report under `bugs/`, then — with the owner's go — commit and
push in the dropbox repo only, naming the remote in the one-line ask. If the push
fails, say so plainly and leave the committed file in place.

### Last resort — neither path works

If the dropbox is unreachable (offline, no clone possible, no `gh`), write the
report to `.agents/bug-reports/<name>.md` in the repo you are running in so it
travels with that repo's git, and say plainly that it landed there instead of the
shared dropbox. (This mirrors the harvest fallback to `.agents/harvest.md`.)

## Not your job here

Filing is not fixing. Reporting a bug does not authorize changing the product to
fix it — that is a separate scoped change under the normal plan/approval
contract. File the report; fix only if and when the owner says so.
