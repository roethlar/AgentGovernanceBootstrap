# Repo-Specific Guidance
<!-- Extends AGENTS.md; never overrides it. Rules and pointers only — state
     lives in .agents/state.md. -->

## Mission Detail

This repo is AgentGovernanceBootstrap, the source of the portable governance/bootstrap process it ships. It builds a governance/bootstrap toolkit for repositories maintained with LLM coding agents: `tools/discover.py` (discovery), `procedures/` (the route procedures), and `templates/` (the drafting templates, including the `AGENTS.md` template this repo's own `AGENTS.md` is a verbatim copy of). The intended outcome is repo-specific agent guidance that helps fresh agents turn plain-English tasks into working, validated code with minimal drift.

## Reading Order

Use these as the active baseline, in order:

1. `README.md`
2. `docs/usage.md`
3. `docs/design.md`
4. `docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md`
5. `tools/discover.py`
6. `procedures/*.md`
7. `templates/*`

`docs/history/` is an archival record unless the human explicitly asks to review or revise history; do not treat old plan versions, review files, or the decisions archive as current design. Closed decision entries are archived verbatim from `.agents/decisions.md` into `docs/history/decisions-archive.md`.

## Verification

For changes to `tools/discover.py`, `tests/`, or `templates/`/`procedures/` content that the discover script copies into target repos, run:

```bash
python3 -m unittest discover -s tests -v
```

On Windows run it from Git Bash as `py -3 -m unittest discover -s tests -v`
(stock `python3` on PATH is the Microsoft Store stub); the suite self-shims
`python3` for the subprocesses its fixtures spawn (`tests/_pyshim.py`).

For documentation-only changes, run `git diff --check`.

The original PowerShell helper is retired to `docs/history/agent-bootstrap-discover.ps1` (2026-06-10, after the Blit pilot). It is a historical record; do not modify or resurrect it.

## Remotes & Sync

- Canonical remote: GitHub, `https://github.com/roethlar/AgentGovernanceBootstrap.git`. This toolkit's canon propagates only when pushed there.
- LAN gitea mirror: `http://q:3000/michael/AgentGovernanceBootstrap.git` — a mirror of GitHub (faster fetch on the LAN); it may lag and is never authoritative.
- Sessions in target repos sync the toolkit from GitHub at kickoff, using the gitea mirror as a faster fetch source when reachable (fast-forward only).
- Push policy lives in `.agents/push-policy.md`.

## Earned Practices

- Token efficiency with a discretionary filter proxy (2026-06-22 decision in `docs/history/decisions-archive.md`): work compact-but-equivalent — targeted reads over whole-file dumps, scoped searches, no re-reading unchanged files. When a token-filtering command proxy is available, invoke it per-command at your discretion for routine, high-volume, low-stakes output; never wire it as an auto-rewrite hook, because it is lossy by design — run unfiltered whenever the filtered form might drop something that matters (exact output verification, authoritative content, anything cited as evidence for a durable claim).
- Hooks shipped in this repo: `.claude/settings.json` carries the re-ground hook (on context compaction, prompts a re-read of the AGENTS.md Prime Invariants) and the advisory `PreToolUse` tripwire on `AGENTS.md` edits (`.claude/agents-md-tripwire.py`; it reminds, never blocks). Both are byte-identical to the shipped `templates/hooks/claude/` files.
- A `review <agent>` wrapper exists at `.claude/commands/review.md`; it points at `.agents/playbooks/reviewloop.md`, installed byte-identical from the shipped template `templates/playbooks/reviewloop.md`.
