# Design: Existing-Governance Migration and Architecture Restructure

**Date:** 2026-06-09
**Status:** Draft — pending owner review
**Supersedes:** the two-stage PowerShell architecture described in
`docs/history/bootstrap-plan.v9.md` (that document remains the historical record).

## Goal

Extend Agent Governance Bootstrap so it can bootstrap repos that already have a
mature, hand-built governance system (the motivating case is `../Blit`), and
restructure the tooling so the owner — a non-developer — can read and maintain
every part of the process that contains judgment.

## Decisions (settled during design, 2026-06-09)

1. **Migrate to the standard.** Every bootstrapped repo converges on the same
   `.agents/` layout. Existing governance systems are migrated into it, not left
   as parallel canon.
2. **Supersede in place.** After migration, old governance files get a short
   banner at the top pointing to their replacement. Content stays. Deletion can
   happen later, manually, once the new system has proven itself.
3. **Harvest: minimal, gated, dropbox-first (settled 2026-06-09 after several
   rounds).** During migration the agent may record generalizable governance
   rules under strict discipline designed against LLM eagerness: the expected
   outcome is **no report**; an idea qualifies only if it is a rule about
   agent behavior or process, earned by a real citable incident in that repo,
   not already covered by the templates, and useful to other repos; hard cap
   of three ideas; never a "nothing found" file. Delivery after approval: if
   the owner configured a harvest dropbox repo (local path in the untracked
   `harvest.config.json`, surfaced in the manifest as `harvestRepoPath`), the
   report is written there as a NEW uniquely named file — append-only, never
   overwriting or editing anything — then committed and pushed under standing
   owner authorization that covers the dropbox only. Otherwise the report is
   copied to `.agents/harvest.md` in the target repo and travels with it via
   git. **The canonical bootstrap repo is never written by sessions running
   elsewhere; the dropbox is the sole shared-writable location.** A sweep
   session in this repo, run only on the owner's request, reads the dropbox
   and any named fallback files, judges ideas skeptically (default verdict:
   skip), and logs outcomes in `harvest/processed.md`.
4. **AGENTS.md is canonical; shims are generated.** Shims are thin pointers to
   `AGENTS.md`, never copies of its content. Primary harnesses (Claude Code,
   Codex, Gemini) get shims drafted from reference templates maintained in
   `templates/` (source material: the Blit repo's pre-migration governance kit, preserved in Blit's own git history).
   Any other harness (Cursor, aider, etc.) gets a self-knowledge fallback shim
   explicitly labeled best-effort in the approval summary.
5. **Single-session kickoff; script stays, ported to Python.** The agent runs
   discovery itself as step 1 of one session. The deterministic script is kept
   because discovery's required property is completeness, not intelligence: a
   script cannot get lazy on an 830-file repo, costs no tokens, and produces the
   same manifest on every model. The two-stage flow (human runs the script
   first) remains as a documented fallback for sandboxed harnesses.
6. **Freshness self-heals.** A stale or missing manifest causes the agent to
   re-run discovery and continue — never to refuse. The only surviving refusal
   is the sandboxed fallback where the agent cannot run the script; there it
   asks, in plain English, for discovery to be re-run. Note: uncommitted file
   edits never trip the commit check; only commits made after discovery do.
   Additionally, before writing the approval summary the agent re-compares
   current `git status` against the manifest: if the working tree materially
   changed during the session, it re-runs discovery locally, or flags the
   change in plain English when sandboxed. The human is never blocked by
   freshness; the evidence is never silently stale.
7. **The plain-English contract (new invariant).** Anything presented to the
   human for review or approval — approval summaries, inventory verdicts,
   fresh-eyes results — must be understandable without reading
   code, diffs, or JSON. Raw files remain available beneath the summary, but no
   decision may require them.
8. **Approach B (smart scanner parsing prose) is rejected** in every language.
   Parsing freeform governance prose mechanically is the wrong tool. The
   accepted "B-lite" is mechanical detection of verification commands from
   structured files only.
9. **All generated guidance inherits the answer-with-words rule (owner
   decision, 2026-06-09).** Every generated `AGENTS.md` instructs agents:
   answer the human's questions in plain English and stop — never respond to
   a question or musing with code, file edits, or multi-step execution; act
   only on an explicit decision. The owner never tolerates question-prompted
   execution. The same rule binds agents bootstrapping a repo and is recorded
   in this repo's own `AGENTS.md` working rules.
10. **Approved guidance commits itself (owner decision, 2026-06-10).** Once
    the owner approves the summary, the agent copies the files AND makes one
    scoped commit — exact files only, message announced in the summary — with
    no further ask. The approval is the explicit authorization, satisfying
    owner-gated git rules in target repos. Pushing remains the owner's action:
    after committing, the agent asks once whether to push, naming the repo's
    remotes when several exist (the owner juggles GitHub and a personal gitea
    and does not always push to both), and pushes only what the owner names.
    Pilot evidence: requiring a separate "now commit" step left migrations
    sitting uncommitted, unsynced across the owner's machines.
11. **The toolkit syncs itself from canonical remotes (owner decision,
    2026-06-10).** Step 0 of the kickoff procedure fetches the owner's two
    canonical remotes — gitea `http://q:3000/michael/AgentGovernanceBootstrap.git`
    (LAN, primary) and GitHub
    `https://github.com/roethlar/AgentGovernanceBootstrap.git` (public,
    reachable anywhere) — and fast-forwards the local bootstrap repo before
    discovery runs. This is the single sanctioned write to the bootstrap repo
    from a target-repo session: the content originates from the owner's
    remotes, so the session contributes nothing. On no-network, divergence, or
    remote disagreement: proceed on the local copy and flag it in the approval
    summary — never merge, never block. This replaces the per-machine clone
    step and the "pull before you bootstrap" habit; the kickoff
    self-provisions on machines without a clone. Corollary: toolkit changes
    propagate only when pushed, so sessions in this repo offer to push to both
    remotes after committing.

## New repo layout (this repo)

```text
tools/discover.py            single file, Python 3 standard library only
procedures/bootstrap.md      canonical agent procedure: kickoff + greenfield path
procedures/migration.md      existing-governance path
procedures/verification.md   fresh-eyes catchup test
procedures/harvest.md        skeptical sweep folding harvested rules into templates
templates/                   all drafting templates as plain markdown/JSON
harvest/processed.md         log of harvest reports already swept
harvest.config.json          OPTIONAL, untracked, machine-local: path to the
                             owner's harvest dropbox repo
docs/history/                gains the retired PowerShell script at parity
```

All judgment lives in `procedures/` and `templates/` as markdown the owner can
read and edit. The script contains only mechanical work.

## discover.py

Carries over everything `agent-bootstrap-discover.ps1` does today: git facts
(commit, status, tracked/untracked/ignored files), sensitive-path flags, project
and CI markers, suggested read paths, coverage cap, `.bootstrap-tmp/` scratch
directory with self-`.gitignore`, `START-HERE.md`.

Additions:

- **`governanceMarkers`** — known governance artifacts detected by name:
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `STATE.md`, `DEVLOG.md`,
  `DECISIONS.md`, `.review/`, `.claude/commands/`, `.agents/`,
  `.cursor/rules/`, and similar.
- **`verificationCandidates`** — verification commands parsed mechanically from
  structured files only: `package.json` scripts, Makefile targets, `Cargo.toml`
  workspace layout, `pyproject.toml`, CI workflow files. Each candidate records
  its source. Candidates are evidence for the drafting agent to confirm, not
  authority.
- **Self-containment copy** — `procedures/` and `templates/` are copied into
  `.bootstrap-tmp/`, so once discovery has run, the entire process exists inside
  the target repo regardless of who ran it or what the harness can reach.
- **`bootstrapRepoPath`** — recorded in the manifest for provenance and so the
  agent can locate the discovery script for re-runs.
- **`harvestRepoPath`** — copied into the manifest from the bootstrap repo's
  untracked `harvest.config.json` when present; `null` otherwise. Tells the
  migration agent where the owner's harvest dropbox lives on this machine.
- **Routing** — `START-HERE.md` points the agent at the migration procedure when
  governance markers were found, otherwise at the greenfield procedure.
- Coverage cap default rises to 2000.

Requirements: Git and Python 3. No pip, no packages, no virtual environments.
If Python is missing (chiefly a Windows concern), the procedure instructs the
agent to help the human install it — a one-time step.

## Migration procedure (procedures/migration.md)

Executed by the in-repo agent when governance markers exist:

1. **Freshness** — if the manifest commit does not match current HEAD, re-run
   `discover.py` and continue (self-heal). In a sandboxed environment where the
   script cannot run, stop and ask for discovery to be re-run, in plain English.
2. **Governance inventory** — a table covering every artifact in
   `governanceMarkers` plus anything else found while reading: the artifact, its
   role today, a verdict — **migrate / supersede / leave** — and its
   destination. The inventory appears in the approval summary in plain English.
3. **Draft the standard layout** under `.bootstrap-tmp/drafts/`, mirroring final
   paths: `AGENTS.md` (now containing the bootstrap handoff rule),
   `.agents/state.md`, `.agents/decisions.md`, `.agents/repo-map.json`,
   `.agents/artifact-manifest.json`, playbooks as the scope tier justifies.
4. **Migrate content, generalized** — current state into `state.md`; settled
   decisions into `decisions.md`; battle-earned behavioral rules (e.g., Blit's
   git-safety and checkpoint sections) into the new `AGENTS.md`. Transient chat
   phrasing is generalized per the existing universal invariant.
5. **Supersession banners** — one drafted banner per superseded file, applied
   only after approval. Append-only journals (e.g., `DEVLOG.md`) normally get
   the verdict *leave*: they are history, not state.
6. **Harness shim** — drafted for the harness the agent is running in: from the
   reference template for primary harnesses, or as a best-effort self-knowledge
   shim (labeled as such in the approval summary) for others. Always a thin
   pointer to `AGENTS.md`, never a copy of its content.
7. **Trigger-vocabulary commands** — thin command wrappers (for Claude Code:
   `.claude/commands/{catchup,handoff,drift,decision,plan}.md`) pointing at
   canonical playbooks. The reference implementation is the Blit repo's pre-migration command kit, preserved in Blit's own git history
   implementation.
8. **Harvest report (optional, expected absent)** — only when this repo's
   governance contains rules earned from real, citable incidents that other
   repos would benefit from: drafted at
   `.bootstrap-tmp/drafts/harvest-report.md` under the discipline of decision
   3 (no-report default, incident citation required, cap of three, no empty
   reports). After approval it is delivered to the harvest dropbox as a new
   file, or to this repo's `.agents/harvest.md` when no dropbox is reachable.
9. **Approval summary** — verdict-first (`Approve` / `Approve after edits` /
   `Do not approve yet`), scope tier, the inventory, assumptions needing
   approval, risk-ranked limitations, and the fresh-eyes result. Honors the
   plain-English contract.

Nothing outside `.bootstrap-tmp/` is written before approval. After approval the
agent copies drafts to tracked paths, applies banners, and makes ONE scoped
commit whose message the approval summary announced — adding only the approved
files, never `git add -A`. The owner's approval of the summary constitutes the
explicit per-action authorization that repos with owner-gated git rules (like
Blit) require for that commit. Pushing remains owner-triggered.

## Fresh-eyes verification (procedures/verification.md)

After drafting completes, a fresh agent context with no knowledge of the
migration receives only the drafted files and the repo, and performs a
`catchup`: what is this project, what is true now, what is next, what is
blocked, how are changes verified. Failures are fixed by the drafting agent and
the check is re-run once. The outcome is reported in the approval summary as a
plain-English sentence, not test output. Required when existing governance was
migrated; optional for greenfield repos.

## Harvest sweep (procedures/harvest.md)

Run in this repo, only when the owner asks. Reads new files in the dropbox
(path from `harvest.config.json`) and any fallback `.agents/harvest.md` files
in repos the owner names; skips reports already logged in
`harvest/processed.md`. Skepticism is the default: an idea earns adoption only
if it would have prevented a specific, citable mistake and is not already
covered — the owner relies on this filter, not on agent enthusiasm. Verdicts
(adopt / adapt / skip, default skip) are presented in plain English; the owner
decides; approved edits land in `templates/` or `procedures/`; handled reports
are logged here and moved to a `processed/` subfolder inside the dropbox (the
dropbox exception permits that write).

The report format is machine-checkable by design (fixed required headings),
and the collection half of the sweep — scan, validate, drop noncompliant
reports with their names listed, concatenate survivors into a digest — is
deliberately script-ready. The digest script is not built now (YAGNI at
current volume); it becomes a small stdlib Python drop-in the first time a
sweep has enough reports to justify it. Judgment and template editing remain
agent + owner work; scripting those is rejected Approach B.

## Testing

- Two small fixture repos under `test/fixtures/`: one greenfield, one carrying
  mock governance files (a miniature of the Blit pattern).
- A smoke test runs `discover.py` against each fixture and compares the manifest
  to a checked-in golden copy (volatile fields like timestamps and absolute
  paths normalized).
- This repo's verification rule in `AGENTS.md` changes from the PowerShell
  parser check to running the smoke test.
- The acceptance test for the whole design is the Blit pilot, reviewed with the
  existing pilot review checklist in `docs/usage.md`.

## Migration of this repo itself

`README.md`, `docs/usage.md`, `docs/design.md`, and `AGENTS.md` are updated to
describe the new architecture. The PowerShell script is kept until
`discover.py` reaches parity (smoke test passing, one successful pilot), then
moved to `docs/history/`.

## Out of scope

- Hosted harvest collection (MCP endpoints, email, sync services) — rejected;
  the dropbox is a plain git repo or nothing.
- An acceptance grader beyond the fresh-eyes test.
- An automated apply/update command (manual copy-after-approval remains).
- Multi-agent review workflows.
- Parsing prose governance files in the script (rejected Approach B).

## End-to-end picture (Blit)

The owner opens an agent session in Blit and pastes one line: read
`<bootstrapRepoPath>/procedures/bootstrap.md` and follow it. The agent runs
`discover.py`; discovery finds Blit's governance and routes to migration. The
agent inventories `STATE.md`, `DEVLOG.md`, `DECISIONS.md`, `REVIEW.md`,
`.review/`, `.claude/commands/`; drafts the `.agents/` layout preserving Blit's
git-safety rules in the new `AGENTS.md`; drafts banners; runs the fresh-eyes
test; presents one plain-English approval summary with the inventory. On
approval it copies drafts into place and applies banners. The owner commits
when satisfied.
