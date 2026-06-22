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

File the report to the `agent-harvest` dropbox per the shared transport recipe
`procedures/file-to-dropbox.md`, with:

- **dest (path in dropbox):** `bugs/<source-repo>-<slug>-<YYYY-MM-DD>.md` (the
  filename from above, under the `bugs/` folder)
- **in-repo fallback:** `.agents/bug-reports/<name>.md` in the repo you are
  running in (used only when the dropbox is unreachable; mirrors the harvest
  fallback to `.agents/harvest.md`)

That recipe covers the preferred no-clone `gh api` write, the clone fallback, the
append-only rule, and the ask-before-publish gate. Use a commit message like
`bug: <short title>`.

## Not your job here

Filing is not fixing. Reporting a bug does not authorize changing the product to
fix it — that is a separate scoped change under the normal plan/approval
contract. File the report; fix only if and when the owner says so.
