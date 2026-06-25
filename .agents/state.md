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
- 2026-06-22: trimmed the per-session guidance tax. A density audit showed prose compression saves only ~2.7% (the guidance is dense, not padded), so instead the `## Bootstrap Handoff` section was collapsed to a conditional pointer to the synced `.bootstrap-tmp/procedures/bootstrap.md` (~600 tokens/session off `AGENTS.md`; the procedure is now the single canonical home for the handoff/reconciliation/wrapper-guard logic), and the token-efficiency invariant now encourages `rtk` as a discretionary per-command proxy (not an auto-rewrite hook) plus compact-but-equivalent working. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: the `agent-harvest` dropbox now also stores bug reports (defects in this product) under a `bugs/` folder. Agents auto-write a report from `templates/bug-report.template.md` and file it via the canonical recipe `procedures/file-bug-report.md` (gh-api preferred, clone fallback, in-repo last resort), publishing only on an explicit owner go; the harvest sweep triages `bugs/`. See the 2026-06-22 decision in `.agents/decisions.md`. The `agent-harvest` repo gained a `bugs/` folder and a README section to match.
- 2026-06-22: unified the two dropbox-write paths. The transport mechanics now live in one shared recipe, `procedures/file-to-dropbox.md`, used by both harvest reports (`migration.md` Step 8) and bug reports (`file-bug-report.md`). Harvest submissions gained the no-clone `gh api` transport and lost their former standing auto-push: every dropbox publish now asks for an explicit owner go. The `gh api` PUT/DELETE path was verified end-to-end against `roethlar/agent-harvest`.
- `.agents/decisions.md` owns the live decision queue (Active entries plus the `## Open Decisions` queue); closed entries are rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule. See that file for the current open/active set rather than echoing a count here.
- 2026-06-25: rewrote the `reviewloop` playbook template (`templates/playbooks/reviewloop.md`) from the async sentinel/watcher design to a synchronous `review <agent>` flow, and added the `.claude/commands/review.md` wrapper. The coder (current harness) dispatches a named reviewer harness (codex/agy/grok/subagent) headless and one-shot per finding, deriving the headless incantation live by probing (no human-maintained table), parses a structured fail-closed JSON verdict (`{verdict, guard_confirmed, reviewed_sha, base_sha, comments}`), records it into the finding doc, and acts under owner-gated merge. The reviewer's guard proof runs in its own git worktree against a pinned base SHA. Design and the cross-harness review that hardened it: `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`; plan: `docs/superpowers/plans/2026-06-25-synchronous-review-handoff.md`. `review` is a playbook operator, intentionally kept out of `OPERATOR_WORDS`.

## Next

- The `.agents/decisions.md` "Open Decisions" section is the authoritative queue for deferred/owner-approved-but-unimplemented items; consult it for what is awaiting a plan (it is not empty — e.g. the 2026-06-25 stall-not-length invariant).
- Run harvest sweeps in this repo only on explicit owner request as harvest reports and bug reports accumulate in the dropbox (or fallback).
- Deferred: fix the `tools/discover.py` `operator:playbook` false positive (probe matches bare `` `playbook` `` but the operator is written `` `playbook <name>` ``, so the update route over-reports `reconcileRecommended`). The bug was filed to the `agent-harvest` dropbox on 2026-06-22; the fix (discover.py + a test using the realistic `` `playbook <name>` `` shape) is a separate scoped change awaiting owner go.
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.
- 2026-06-25: added a **stall-not-length** Universal Invariant to `templates/AGENTS.template.md` (iterative processes escalate on a cycle that banks no verifiable progress, never on duration; long converging runs are not capped), with `templateVersion` bumped to 2026-06-25 so the update route reconciles stale targets. Adopted; recorded as the 2026-06-25 entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance, updated only by a deliberate self-application run).
- Deferred: the synchronous `review <agent>` operator ships as a playbook + Claude Code wrapper only. If it is ever promoted to a governance operator advertised in every `AGENTS.md`, the `OPERATOR_WORDS` staleness probe must first be reconciled with the existing deferred `operator:playbook` false positive (above) — adding `review` there would compound it. Not blocking; documented so the promotion is a deliberate step.

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
