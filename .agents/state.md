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
- 2026-06-20: a long session worked through the Open Decisions queue and adopted the assessed-but-deferred governance findings as product changes, each a scoped commit pushed to GitHub (see `.agents/decisions.md` for the authoritative entries and their Adopted status). Notable durable results: a Git Safety invariant against rewriting history or restructuring commits without owner approval; a roadblock-provenance invariant; the corrected remote topology (GitHub canonical, gitea a mirror); harvest sync-before-read; neutral custody wording for git-collapsed ignored directories; harness-independent command-wrapper drafting with a new `templates/commands/` set; project-memory-must-live-in-the-repo; status-based archiving of closed decisions into `docs/history/`; a soft token-filtering-proxy (e.g. `rtk`) recommendation; and an early git-presence check before discovery. The toolkit's own git remotes were re-pointed to match the adopted topology: `origin` = GitHub (canonical), `gitea` = LAN mirror. All edits were to the product (templates/procedures/tools); this repo carries a stale pre-current bootstrap application, so its own self-application — an Operator Requests section in `AGENTS.md`, committed `.claude/commands/` wrappers, and archiving its adopted decisions — is intentionally deferred to a bootstrap re-run.
- 2026-06-20 (same session, later): beyond the adoptions, several findings were assessed and left in the Open Decisions queue rather than implemented (see `.agents/decisions.md`). One was surfaced by an in-session failure — the answer-with-words invariant was skipped twice under context load — which prompted a queued finding that load-bearing invariants need forceful enforcement (re-assertion at checkpoints, a pre-action gate, or harness hooks), not just statement in a long doc.

## Next

- The remaining work is the open items in `.agents/decisions.md` "Open Decisions" — the authoritative list, not duplicated here so it cannot drift. Resolve those product items first; most of that queue was adopted 2026-06-20.
- Only once the product is stable (queue cleared), re-run the bootstrap on this repo once to bring its own self-application current — add the Operator Requests section and `.claude/commands/` wrappers, archive the adopted decisions into `docs/history/`, and apply the other invariants. Re-running before the queue is cleared would just have to be repeated, so it comes last; until then this repo intentionally lags the product it ships.
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
