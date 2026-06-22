# Agent State

This file is the first place future agents should read for current repo state. Keep it
short and update it when important repo facts change.

## Now

- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
- Governance for this repo itself is in `AGENTS.md` (Prime Invariants, universal and repo-specific rules, operator vocabulary, and pointers) plus this `.agents/` layout (state and decisions).
- 2026-06-21: this repo's own governance was brought current with the product it ships (it had intentionally lagged since 2026-06-20). The self-application added a `CLAUDE.md` shim (`@AGENTS.md`), committed `.claude/commands/` wrappers for the full operator set (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`), and a committed `.claude/settings.json` re-ground hook (fires on context compaction, points back to AGENTS.md). `AGENTS.md` was rewritten to the product shape: a `## Prime Invariants` block, a `## Universal Invariants` section, `## Operator Requests`, a `## Session Startup` trust note, and an updated `## Bootstrap Handoff` that audits wrappers and re-ground hooks. (`.claude/settings.local.json` stays machine-local and untracked.)
- 2026-06-21: the load-bearing-invariant enforcement work landed and is recorded as Adopted — a lean Prime Invariants block plus per-harness re-ground hooks (`templates/hooks/<harness>/`) that fire on compaction, with tests and a design spec (`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`). This resolved the last item that had been deferred to this re-run.
- 2026-06-22: closed the update-route template-reconciliation gap. `AGENTS.md` files now carry a `<!-- templateVersion -->` stamp; discovery records an `agentsTemplate` manifest block (current/target version, `reconcileRecommended`, `missingSections`) and, on the update route, the toolkit reconciles a stale or unstamped `AGENTS.md` to the current template before running the wrapper/hook guarantees. Wrapper/hook guidance treats a missing target section as a staleness signal to reconcile, not a cue to narrow the artifact. See the 2026-06-22 decision in `.agents/decisions.md`.
- The `.agents/decisions.md` Open Decisions queue is clear. Closed (Adopted/Superseded) decisions were rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule, leaving the live decisions doc as Active entries plus an empty queue and a pointer to the archive.

## Next

- No Open Decisions remain; the `.agents/decisions.md` "Open Decisions" section is the authoritative queue and is currently empty.
- Run harvest sweeps in this repo only on explicit owner request as harvest reports accumulate in the dropbox (or fallback).
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.

## Blockers

None recorded.

## Verification

- Changes that touch `tools/discover.py`, `tests/`, or any content under `templates/` or `procedures/` that the discover script copies into target repos: run `python3 -m unittest discover -s tests -v`.
- Documentation-only changes (no effect on setup, commands, runtime behavior, generated files, or user-visible behavior): run `git diff --check`.
- See `AGENTS.md` Verification section and `.agents/repo-map.json` for the policy that applies to future agents.

## Active Sources

- `AGENTS.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `README.md`
- `docs/usage.md`
- `docs/design.md`
- `docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md`
- `tools/discover.py`
- `procedures/*.md`
- `templates/*`

## Unrecorded Repo Memory

None known.
