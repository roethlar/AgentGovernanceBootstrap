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
issues on this repo (`.github/ISSUE_TEMPLATE/`); each issue is put to the
owner one at a time as an Owner Gates ask and acted on only on an explicit
per-item go — a general "fix them" is not standing batch authority. The
intended outcome is
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

Pick the interpreter with `procedures/bootstrap.md` Step 1's probe order —
the floor is Python 3.10, so a bare `python3` fails where it resolves below
that (a stock macOS `python3` is 3.9; on Windows use `py -3` from Git Bash,
never the Microsoft Store stub). This machine's resolved interpreter path is
in `.agents/machines.md`. The suite runs its subprocesses via the invoking
interpreter, so run it with that same one.

For changes to `tools/`, `tests/`, or `templates/`/`procedures/` content:

```bash
<probed-python> -m unittest discover -s tests -v
```

For documentation-only changes, run `git diff --check`. Changes touching
`docs/superpowers/plans/` additionally run the plan lint
`<probed-python> -m unittest tests.test_plan_lint -v`.

## Remotes & Sync

- Canonical remote: GitHub, `https://github.com/roethlar/AgentGovernanceBootstrap.git`.
  This toolkit's canon propagates only when pushed there.
- LAN gitea mirror: `http://q:3000/michael/AgentGovernanceBootstrap.git` —
  the owner-controlled LAN mirror of GitHub, a trusted fetch source whose
  purpose is covering GitHub being unreachable. It may lag GitHub; lag is
  expected, never a conflict (2026-06-10 decision; owner ruling
  2026-07-10). Canon propagates only via pushes to GitHub.
- Push policy lives in `.agents/push-policy.md`.

## Earned Practices

- `templates/AGENTS.template.md` body stays one line per paragraph/bullet —
  no hard line-wraps; re-wrapping is a regression (2026-07-02 decision,
  archived: wrapping's only remaining effect was a per-session token tax).

- Token efficiency with a discretionary filter proxy (2026-06-22 decision in
  `docs/history/decisions-archive.md`): work compact-but-equivalent —
  targeted reads over whole-file dumps, scoped searches, no re-reading
  unchanged files. When a token-filtering command proxy is available, invoke
  it per-command at your discretion for routine, high-volume, low-stakes
  output; never wire it as an auto-rewrite hook — it is lossy by design.
- This repo governs itself with its own product: `AGENTS.md` is the template
  verbatim, installed by `tools/refresh.py`. **Agents never update this
  repo's installed governance** — not by hand-editing `AGENTS.md`, shims,
  wrappers, skills, hooks, or playbooks, and not by running any toolkit tool
  (including `tools/refresh.py` and the `update-governance` operator)
  against this repo; self-refresh is an owner-only action (owner rule,
  2026-07-10, recorded in `.agents/decisions.md`). Installed copies lagging
  the templates is the expected steady state between owner-run refreshes —
  leave the lag alone; at most note it.
- Review playbooks ship at `templates/playbooks/codereview.md` (per-finding
  conformance loop) and `templates/playbooks/openreview.md` (unprimed
  goal-first whole-change review); both install into `.agents/playbooks/`
  via refresh, each with a Claude Code wrapper and shared skill, and the
  owner invokes them by name (2026-07-16 decision). This repo's installed
  copies lag until the owner's next self-refresh. Dispatching `codex` as a
  reviewer: pipe the prompt via **stdin** (`codex exec ... < prompt`); the
  argv form has hung.
