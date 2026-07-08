# Repo-Specific Guidance
<!-- Extends AGENTS.md; never overrides it. Rules and pointers only — state
     lives in .agents/state.md. -->

## Mission Detail

This repo is AgentGovernanceBootstrap, the source of the portable governance
process it ships. The product (post the 2026-07-08 zero-based consolidation):
`procedures/bootstrap.md` (the single bootstrap/migration procedure) +
`procedures/verification.md` (fresh-eyes), `templates/` (the drafting
templates, including the `AGENTS.template.md` this repo's own `AGENTS.md` is
a verbatim copy of), and `tools/refresh.py` + `tools/shipped-set.json` (the
deterministic per-repo governance refresh). Feedback arrives as GitHub
issues on this repo (`.github/ISSUE_TEMPLATE/`). The intended outcome is
repo-specific agent guidance that helps fresh agents turn plain-English
tasks into working, validated code with minimal drift.

## Reading Order

Use these as the active baseline, in order:

1. `README.md`
2. `docs/usage.md`
3. `docs/design.md`
4. `docs/harness-capabilities.md` (the per-harness verify-once record)
5. `tools/refresh.py` + `tools/shipped-set.json`
6. `procedures/*.md`
7. `templates/*`

`docs/history/` and `docs/superpowers/` are archival/provenance records
unless the human explicitly asks to review history; do not treat old plans,
specs, or the decisions archive as current design. The 2026-07-08
consolidation plan (`docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`)
is the provenance for the current shape.

## Verification

For changes to `tools/`, `tests/`, or `templates/`/`procedures/` content:

```bash
python3 -m unittest discover -s tests -v
```

On Windows run it from Git Bash as `py -3 -m unittest discover -s tests -v`
(stock `python3` on PATH is the Microsoft Store stub); the suite self-shims
`python3` for subprocesses (`tests/_pyshim.py`).

For documentation-only changes, run `git diff --check`.

## Remotes & Sync

- Canonical remote: GitHub, `https://github.com/roethlar/AgentGovernanceBootstrap.git`.
  This toolkit's canon propagates only when pushed there.
- LAN gitea mirror: `http://q:3000/michael/AgentGovernanceBootstrap.git` — a
  mirror of GitHub (faster fetch on the LAN); it may lag and is never
  authoritative.
- Push policy lives in `.agents/push-policy.md`.

## Earned Practices

- Token efficiency with a discretionary filter proxy (2026-06-22 decision in
  `docs/history/decisions-archive.md`): work compact-but-equivalent —
  targeted reads over whole-file dumps, scoped searches, no re-reading
  unchanged files. When a token-filtering command proxy is available, invoke
  it per-command at your discretion for routine, high-volume, low-stakes
  output; never wire it as an auto-rewrite hook — it is lossy by design.
- This repo governs itself with its own product: `AGENTS.md` is the template
  verbatim, refreshed by `tools/refresh.py` like any governed repo. Local
  hook/wrapper files may briefly lag the templates between a template change
  and the next self-refresh — that is expected, not drift to hand-fix; run
  the refresh.
- A `review <agent>` wrapper exists at `.claude/commands/review.md`; the
  reusable playbook ships at `templates/playbooks/reviewloop.md` and installs
  into `.agents/playbooks/` via refresh. Dispatching `codex` as a reviewer:
  pipe the prompt via **stdin** (`codex exec ... < prompt`); the argv form
  has hung.
