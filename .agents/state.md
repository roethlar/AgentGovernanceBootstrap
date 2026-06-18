# Agent State

This file is the first place future agents should read for current repo state. Keep it
short and update it when important repo facts change.

## Now

- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
- Governance for this repo itself is in `AGENTS.md` (rules and pointers) plus this `.agents/` layout (state and decisions).
- No `.agents/` directory existed at root prior to the 2026-06-10 layout migration; only root `AGENTS.md` was present as the governance marker.
- 2026-06-10: the self-migration landed (commit d260a72, run by a Grok Build agent), and the four follow-up fixes it surfaced are folded back: self-target wording in migration Step 8.4, custody redefined as intended post-approval custody proven by git query, shim rule generalized to native AGENTS.md readers, and README's Current Status deduped into a pointer at this file.
- 2026-06-11: two pilot issue reports folded back (see `harvest/processed.md`). Non-git targets are now first-class: discover.py never lists files as tracked without git, bootstrap.md gained an "If the target is not a git repository" section with an owner-gated git-init question, and the templates model custody values beyond `tracked`. Approval semantics tightened: after an explicit rejection, commit re-authorization must be unambiguous; ignored-paths-claimed-tracked conflicts are a mandatory owner question; `Approve` recommendations require no open owner decisions.
- 2026-06-18: operator command wrappers are now a standing guarantee on every route (greenfield, migration, update), not migration-only. The process drafts any missing slash-command wrappers and the `.gitignore` edit that makes them committable (un-ignore `.claude/`, ignore `.claude/settings.local.json`). Canonical recipe lives in `procedures/bootstrap.md` "Operator command wrappers (all routes)"; migration.md Step 4 and the AGENTS template Bootstrap Handoff reference it. This adopts the deferred migration-only-wrappers decision in generalized form and rejects an alternative pilot proposal to route ignored-`.claude/` repos to greenfield.

## Next

- Assessed-but-deferred toolkit decisions remain open; see `.agents/decisions.md` "Open Decisions" for the current list and their status. (The command-wrapper decision from that queue was adopted 2026-06-18.)
- Run harvest sweeps in this repo only on explicit owner request as harvest reports accumulate in the dropbox (or fallback).
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).

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
