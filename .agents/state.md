# Agent State

This file is the first place future agents should read for current repo state. Keep it
short and update it when important repo facts change.

## CURRENT FOCUS — START HERE (HANDOFF 2026-07-02)

**Model testing is CLOSED** (owner: expensive, diminishing returns), and the owner has
additionally closed **end-to-end trials as a method** — future validation is mechanism
smoke tests and real-world dogfood incidents, not factorials. **Nothing is running.**
The 2026-06-30 harness-gap conclusions (prose helps only weak models and can hurt at
ceiling; the strong-harness gap is an attention lapse at edit-failure/re-author, i.e. a
mechanism problem) were recorded in the eval workstream's files, **deleted from the
tree 2026-07-08** (owner: scrap evals entirely; zero-based consolidation plan slice 7)
— full record in git history; the salvaged per-harness facts live in
`docs/harness-capabilities.md`. The workstream's superseded `## Next` history is
rotated to `docs/history/state-archive.md`.

**Specific-over-generic precedence invariant: LANDED 2026-07-04** (fix of the
latest `agent-harvest` bug report, on the owner's explicit fix instruction;
decision Adopted in `.agents/decisions.md`). New Universal Invariant in
`templates/AGENTS.template.md`: an explicit authority/scope boundary, or a
rule/decision whose wording removes discretion for the case it names
("unconditional", "no per-run choice", "deterministic"), outranks the generic
flag-conflicts / content-quality defaults for that case, and git history is
not grounds to reopen a settled case. Stamp `2026-07-04.1`; presence test
added and guard-proven; suite green (145 tests, 2 platform skips). The
2026-06-23 authority-boundary Open finding was broadened into this decision
and archived verbatim. Outstanding: the behavioral bite-proof (next
refresh/dogfood run must draft the reviewloop reinstall as plain fact, no
question raised), and the dropbox bug-file status update, which awaits an
owner go.

**Edit-failure refocus hook: DROPPED (owner, 2026-07-01) — do not resurrect without a
new owner decision.** A Haiku smoke test falsified the planned mechanism: Claude Code
2.1.198 fires neither `PostToolUse` nor `PostToolUseFailure` for edit rejections
(`tool_use_error` results are returned, not thrown; the docs promise otherwise). The
behavioral fix was already declined upstream (anthropics/claude-code#24908, closed
NOT_PLANNED 2026-03-12); our docs-mismatch report was filed on owner request 2026-07-01
as anthropics/claude-code#72996. A working `PostToolBatch` variant was proven
end-to-end, but the owner judged the required machinery (per-batch hook, interpreter
gating, Windows caveats) too much and dropped the artifact. Full findings + decision:
`docs/superpowers/plans/2026-06-30-product-completeness-hook-and-prose.md` (Status +
`## Outcome (2026-07-01)`).

**Live direction — guidance condensation (agreed in words 2026-07-01; NOT started;
needs its own `plan` before any code/template change):** a functional cut of the
product guidance — behavioral contracts, facts, and pointers stay; capability-
exhortation prose goes (eval evidence: placebo on strong models, can hurt at ceiling).
Word-level compression stays rejected (2026-06-22 decision, ~2.7%). The
`completeness-general` prose ships opt-in at most — unconditional inclusion is ruled
out by the evidence — which reframes the old G1 question. Note the 2026-06-30 plan doc
was codex-reviewed at v1 only; its prose sections were never re-reviewed at v2.

**Open-bug-reports sweep: DONE 2026-07-02** (owner go; plan closed with commit
map: `docs/superpowers/plans/2026-07-02-open-bug-reports-sweep.md`). All six
dropbox `bugs/` reports are triaged; the ledger is the new "Processed Bug
Reports" section in `harvest/processed.md`. Fixed this sweep: false-migration
routing (879bf93 — discover.py governance markers skip git-ignored paths and
`.claude/settings.local.json`; 4 new tests, suite 142/142, guard-proven) and
shim harness scoping (c05dc31 — bootstrap step 5 + migration Step 4 draft or
refresh every shipped shim template, not just the current harness's). The
template-invariant-duplication report was resolved by the earlier
condensation/reflow work; its bite-proof passes. Only open thread: the
hook-python3 Windows bite-proof (next block).

**Hook interpreter fix: LANDED 2026-07-02** (plan closed with commit map:
`docs/superpowers/plans/2026-07-02-hook-python3-windows-fallback.md`; decision
Adopted in `.agents/decisions.md`). Harvest bug
`ExchangeAdminWeb-hook-python3-discovery-2026-07-02`: bare `python3` in the
shipped hook commands is a Store stub on stock Windows, so the AGENTS.md
tripwire was silently inert there. Both hook templates (and this repo's
mirrored `.claude/settings.json`) now use `py -3 … 2>/dev/null || python3 …`
with braced `${CLAUDE_PROJECT_DIR}` for Claude; Windows scope is Git Bash
(owner decision). Suite 138/138. Windows bite-proof still outstanding — rests
on harness docs + the reporter's evidence until a Windows host confirms the
reminder fires. Harvest bug report updated to fix-landed (owner go).

**Housekeeping (2026-07-01):** `AGENTS.md.old` removed (41c3753; byte-identical
recovery residue — live `AGENTS.md` was never damaged). Owner fixed the `CLAUDE.md`
import typo (`RTTK.md` → `RTK.md`; landed in 12b0434). `.serena/` is kept tracked by
owner decision (2026-07-01): only the shareable Serena config (`project.yml` + its
`.gitignore`) is versioned (12b0434), while Serena's cache/memories/local settings stay
excluded by `.serena/.gitignore` — consistent with the harness-local-store invariant,
which bars treating such stores as durable repo memory, not versioning their config.
The stale `.bootstrap-tmp/` left over from 2026-06-27 is gone (verified absent
2026-07-01); no live bootstrap run is signaled.

**Guidance condensation: LANDED 2026-07-01** (270814d; decision in
`.agents/decisions.md`, plan closed:
`docs/superpowers/plans/2026-07-01-guidance-condensation.md`). Template −20%
words. `completeness-general` deferred entirely.

**Route-collapse bundle: LANDED 2026-07-01** (plan closed with commit map:
`docs/superpowers/plans/2026-07-01-route-collapse-refresh-and-portability-sweep.md`;
decisions recorded). Single migration route (update collapsed, 2026-06-28
Adopted), reconciliation branch + portability sweep, `/update-governance`
wrapper template, `operator:playbook` probe fixed, Python 3.9 floor documented,
`templateVersion` now 2026-07-01.2. Suite 132/133 on py3.9.

FIXED 2026-07-01 (owner go): the discrimination gate now reads declared
`hidden.semantics` from fixture.json (`security` default / `completeness`);
`py_vault_twopath` declares completeness. Suite fully green: 136/136 on py3.9.
(History: the mismatch had been masked by a py3.9 import error hiding 84
tests, both fixed 2026-07-01.)

**Dogfood self-application run: DONE 2026-07-01** (`03dfc38`), **reconciliation
REDONE same day** (owner-gated): the run installed
`.claude/commands/update-governance.md` correctly, but its "stamp bump only —
content already current" conclusion was wrong — a textual diff found seven
pre-condensation template passages still in `AGENTS.md` under the 2026-07-01.2
stamp (the structural probe cannot see wording-level drift once the stamp
matches). The redo adopted the condensed template text and carried the
repo-specific content forward (canon-propagation invariant, earned
discretionary-rtk stance per the 2026-06-22 decision, hook description,
Verification specifics); AGENTS.md is now −15% and truthfully at 2026-07-01.2.
Product lesson (candidate for the next procedures pass): the reconciliation
discipline should require a textual diff of invariant wording against the
template, not only the section/stamp probe — a run judged "current" without
one.

**Verbatim-template redesign: product implementation LANDED 2026-07-01**
(decision Adopted + plan with commit map:
`docs/superpowers/plans/2026-07-01-agents-md-verbatim-template.md`).
`AGENTS.md` in every bootstrapped repo is the template verbatim; all
repo-specifics live in `.agents/repo-guidance.md` (extends-only, no overrides
— conflicts are defects; the universality test gates template content);
`discover.py` byte-compare (`agentsTemplate.byteIdentical`) carries
reconciliation; refresh = replace whole + first-run carve-out. rtk and the
whole token-efficiency bullet are OUT of the product (owner directives,
test-guarded). The template itself carries the constant
`@.agents/repo-guidance.md` import line (same bytes everywhere, byte-compare
unaffected; auto-injection where `@` is processed, visible pointer elsewhere);
both shims are one-line `@AGENTS.md` adapters (owner-edited). `templateVersion`
2026-07-02.1 (125c991). Suite 138/138.
**Template reflow: LANDED 2026-07-02** (decision Adopted in `.agents/decisions.md`;
plan closed: `docs/superpowers/plans/2026-07-02-template-reflow.md`).
`AGENTS.template.md` body is now one line per paragraph/bullet — no hard
line-wraps; future template edits must not re-wrap. Lossless; folded with the
sweep's T1 hook-trust trim into the same bump: 3,873 → 3,652 tokens (−5.7%,
`count_tokens`, claude-opus-4-8 tokenizer). Scope is the verbatim template
only (`repo-guidance.template.md`, shims, procedures stay wrapped).
**Slice 5 DONE 2026-07-02: `/update-governance` dogfood run on this repo.**
Discovery correctly flagged the mixed-content `AGENTS.md` (`byteIdentical`
false, stamp 2026-07-01.2 vs template 2026-07-02.1) — the end-to-end
validation the plan required. The run carved this repo's specifics into
`.agents/repo-guidance.md` (mission detail, reading order, verification
commands, remotes/canon-propagation, discretionary-rtk practice, hook
description), replaced `AGENTS.md` with the template verbatim (post-copy
`cmp` proven byte-identical), and reduced `CLAUDE.md` to the one-line shim
plus this repo's `@.agents/RTK.md` import (the repo-specific addition, kept
in the shim so Claude Code still loads it). `.agents/repo-map.json` and
`.agents/artifact-manifest.json` updated to record the new file. This
supersedes the out-of-band `f697bf9` content through the sanctioned path.
Slice 5 landed as 35b5436; slice 6 (bookkeeping) done same day: the
2026-07-01 verbatim-template decision entry closed with the hash and archived
to `docs/history/decisions-archive.md`, plan Status closed. The
verbatim-template plan is fully complete.
**NEXT: awaiting owner input on one queued item** — the verbosity-sweep
B*/M*/P* finding IDs below.

**RTK wording conflict: RESOLVED 2026-07-03 (owner ruling).** `.agents/RTK.md`
ships with the RTK app itself — it is a third-party artifact this repo never
edits; its "always prefix" wording is not this repo's governance. The product
carries NO rtk references (confirmed by grep over `templates/`, `procedures/`,
`tools/`; test-guarded), and `.agents/repo-guidance.md` now carries none
either — its Earned Practices bullet keeps the generic
discretionary-filter-proxy practice with the rtk example and the RTK.md
import mention removed. The `CLAUDE.md` `@.agents/RTK.md` import stays (it is
how Claude Code loads the app's own usage doc, not governance).

**Verbosity sweep of the product: REPORT DELIVERED 2026-07-01, awaiting owner
eval — no changes made.** Findings (IDs the owner replies with to execute):
bootstrap.md — B1 intro invariant duplication, B2 Step 0 rationale, B3 Step 1
rationale/triple-statement, B4 Step 3 rationale clause, B5 wrapper-intro
justification, B6 hook design history, B7 custody/commit contract stated ~4×
across bootstrap+migration → one home + pointers; migration.md — M1 evidence
pointer, M2 rationale clauses, M3 Step 8 enumerates the pointed-at recipe;
per-use files — P1 verification.md double scope-warning, P2 harvest.md
sync-why, P3 file-to-dropbox intro, P4 file-bug-report dogfood-or-foreign
paragraph, P5 manifest-schema rationale sentences; T1 AGENTS.template hook-trust
trims — **T1 EXECUTED 2026-07-02** (folded into the template-reflow bump
`2026-07-02.1`, 125c991); the B*/M*/P* findings still await owner IDs.
Total ≈1,100 words (~1,500 tokens) per-run. Flags: F1 owner-machine facts shipped in product (gitea LAN
URL + `~/dev/` defaults in bootstrap.md Step 0 and file-to-dropbox.md); F2 the
canonical GitHub/agent-harvest URLs are owner-specific but arguably toolkit
canon — noted, no change proposed. Deliberately not cut: report-template
discipline blocks, fresh-eyes prompt, recognition lists, quoting warning.
Executing this sweep is the deferred `procedures/` condensation pass — on
owner IDs, no separate plan needed beyond this recorded report.

Owner-gated follow-up, not started: none beyond the sweep eval and the
slice-5 dogfood run above.

**Push:** plain `git push` works again (verified 2026-07-02; the earlier
stale-credential workaround via `gh auth git-credential` is no longer needed).
Push policy here is `always`.

(The eval workstream's superseded `## Next` history was rotated verbatim to
`docs/history/state-archive.md` on 2026-07-08.)

## Now

- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
- Governance for this repo itself: `AGENTS.md` is a verbatim copy of `templates/AGENTS.template.md` (Prime Invariants, universal invariants, operator vocabulary — replaced whole on governance refresh, never hand-edited); everything repo-specific lives in `.agents/repo-guidance.md` (since the 2026-07-02 carve-out) plus this `.agents/` layout (state and decisions).
- 2026-06-21: this repo's own governance was brought current with the product it ships (it had intentionally lagged since 2026-06-20). The self-application added a `CLAUDE.md` shim (`@AGENTS.md`), committed `.claude/commands/` wrappers for the full operator set (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`), and a committed `.claude/settings.json` re-ground hook (fires on context compaction, points back to AGENTS.md). `AGENTS.md` was rewritten to the product shape: a `## Prime Invariants` block, a `## Universal Invariants` section, `## Operator Requests`, a `## Session Startup` trust note, and an updated `## Bootstrap Handoff` that audits wrappers and re-ground hooks. (`.claude/settings.local.json` stays machine-local and untracked.)
- 2026-06-21: the load-bearing-invariant enforcement work landed and is recorded as Adopted — a lean Prime Invariants block plus per-harness re-ground hooks (`templates/hooks/<harness>/`) that fire on compaction, with tests and a design spec (`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`). This resolved the last item that had been deferred to this re-run.
- 2026-06-22: closed the update-route template-reconciliation gap. `AGENTS.md` files now carry a `<!-- templateVersion -->` stamp; discovery records an `agentsTemplate` manifest block (current/target version, `reconcileRecommended`, `missingSections`) and, on the update route, the toolkit reconciles a stale or unstamped `AGENTS.md` to the current template before running the wrapper/hook guarantees. Wrapper/hook guidance treats a missing target section as a staleness signal to reconcile, not a cue to narrow the artifact. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: trimmed the per-session guidance tax. A density audit showed prose compression saves only ~2.7% (the guidance is dense, not padded), so instead the `## Bootstrap Handoff` section was collapsed to a conditional pointer to the synced `.bootstrap-tmp/procedures/bootstrap.md` (~600 tokens/session off `AGENTS.md`; the procedure is now the single canonical home for the handoff/reconciliation/wrapper-guard logic), and the token-efficiency invariant now encourages `rtk` as a discretionary per-command proxy (not an auto-rewrite hook) plus compact-but-equivalent working. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: the `agent-harvest` dropbox now also stores bug reports (defects in this product) under a `bugs/` folder. Agents auto-write a report from `templates/bug-report.template.md` and file it via the canonical recipe `procedures/file-bug-report.md` (gh-api preferred, clone fallback, in-repo last resort), publishing only on an explicit owner go; the harvest sweep triages `bugs/`. See the 2026-06-22 decision in `.agents/decisions.md`. The `agent-harvest` repo gained a `bugs/` folder and a README section to match.
- 2026-06-22: unified the two dropbox-write paths. The transport mechanics now live in one shared recipe, `procedures/file-to-dropbox.md`, used by both harvest reports (`migration.md` Step 8) and bug reports (`file-bug-report.md`). Harvest submissions gained the no-clone `gh api` transport and lost their former standing auto-push: every dropbox publish now asks for an explicit owner go. The `gh api` PUT/DELETE path was verified end-to-end against `roethlar/agent-harvest`.
- `.agents/decisions.md` owns the live decision queue (Active entries plus the `## Open Decisions` queue); closed entries are rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule. See that file for the current open/active set rather than echoing a count here.
- 2026-06-25: rewrote the `reviewloop` playbook template (`templates/playbooks/reviewloop.md`) from the async sentinel/watcher design to a synchronous `review <agent>` flow, and added the `.claude/commands/review.md` wrapper. The coder (current harness) dispatches a named reviewer harness (codex/agy/grok/subagent) headless and one-shot per finding, deriving the headless incantation live by probing (no human-maintained table), parses a structured fail-closed JSON verdict (`{verdict, guard_confirmed, reviewed_sha, base_sha, comments}`), records it into the finding doc, and acts under owner-gated merge. The reviewer's guard proof runs in its own git worktree against a pinned base SHA. Design and the cross-harness review that hardened it: `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`; plan: `docs/superpowers/plans/2026-06-25-synchronous-review-handoff.md`. `review` is a playbook operator, intentionally kept out of `OPERATOR_WORDS`.
- 2026-06-25: added the **stall-not-length** Universal Invariant to `templates/AGENTS.template.md` (iterative processes escalate on a cycle that banks no verifiable progress, never on duration; long converging runs are not capped), `templateVersion` bumped to 2026-06-25. Adopted — see the 2026-06-25 entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance).
- 2026-06-25: implemented the **AGENTS.md governance boundary** (portable + write-authority) in three layers. Two Universal Invariants in `templates/AGENTS.template.md` (portability copy-test; written-only-by-gated-bootstrap/update); the `drift` operator now names AGENTS.md portability/write-authority as drift targets; and an advisory, non-blocking `PreToolUse` pre-edit tripwire (one stdlib-Python `agents-md-tripwire.py` shared by the Claude Code + Codex hook configs) ships under `templates/hooks/`. `templateVersion` 2026-06-25 → 2026-06-25.2 (same-day second structural change). Layer 2 was validated live before building (fires/visible/non-blocking on Codex and on GLM via Claude Code; self-revert seen once); evidence reframed the spec to L1-primary / L3-backstop / L2-advisory. `TestHookTemplates` was reworked from shape-banning to a portability principle so script hooks pass without per-category exceptions. Adopted — see the 2026-06-25 boundary entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance). Spec: `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`.
- 2026-06-25: wrote the **AGENTS.md retroactive-cleanup follow-on spec** (`docs/superpowers/specs/2026-06-25-agents-cleanup-via-update-route-design.md`) — design only, awaiting owner review then a `plan`. Decision recorded in it: cleanup is the update-route reconciliation *extended*, not a parallel flow. Key design move (owner insight): detect leaks as **surplus over the portable template** — the structural inverse of `missingSections` (which flags what the target *lacks*; surplus flags what it *has beyond baseline*), so a leaky-but-current, structurally-complete `AGENTS.md` still triggers, and non-path leaks (prose, restated state, the repo's name) are caught where a regex would miss them. Discovery computes surplus structurally; the agent sorts each surplus item into allowed-repo-specific vs leak (surplus ≠ leak: the Current State pointer, Active Sources list are legitimate surplus). Relocation rule (owner-settled): move leaks into `.agents/` with **no per-fact pointer** — keep only the existing structural pointers; rare exception when a governance rule's meaning references a repo-specific detail.
- 2026-06-27: **push policy is now repo-specific, delegated to `.agents/push-policy.md`.** The Prime Invariant push clause in `templates/AGENTS.template.md` no longer carries a blanket push-needs-go rule; it reads "History-rewrite and destructive or outward-facing actions always need an explicit go. Push policy: see `.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the default (`ask`); `templates/approval-summary.template.md` gained a Push Policy section that presents four standardized options (1 always / 2 operators / 3 docs / 4 ask) and must ask the human at approval time (do not pre-fill from the decisions log); `procedures/bootstrap.md` Step 10 consults the policy file after committing. `templateVersion` bumped to `2026-06-27.1`. Adopted — see 2026-06-27 push-policy decision in `.agents/decisions.md`.
- 2026-06-27: **this repo's own governance brought current via a dogfood / self-application run** (the deferred frozen-instance reconciliations all landed in one scoped commit `b844c72`): `AGENTS.md` reconciled `2026-06-22` → `2026-06-27.1` (push clause now delegates to push-policy; stall-not-length invariant; both governance-boundary invariants; sharpened drift/playbook operators; Session Startup mentions the tripwire), `.agents/push-policy.md` created set to **`always`** (every commit here pushes immediately), and the advisory AGENTS.md pre-edit tripwire installed (`.claude/settings.json` PreToolUse block + `.claude/agents-md-tripwire.py`, byte-identical to the shipped template). Repo-specific leaks left in place — their relocation is the separate owner-gated cleanup spec.
- 2026-06-27: **dogfood / self-application named as a case of the update route** — `procedures/bootstrap.md` now states that running the toolkit against itself is an in-place update run and a missing `.bootstrap-tmp/` at kickoff is the normal start, never a stop. Docs handrail only, no `compute_route()` detection. Adopted — see 2026-06-27 dogfood decision in `.agents/decisions.md`. Earned by two fresh sessions stopping to ask "is there anything to do here" on the canonical kickoff line.
- 2026-06-27: **`drift` cleanup of `.agents/decisions.md`** — two adopted entries that were parked in `## Open Decisions` (push-needs-explicit-go, and `run_git` fails open / Adopted 2026-06-23) moved **verbatim** to `docs/history/decisions-archive.md` per the archive rule; the push-policy decision relocated from Open into `## Decisions` as Active (its stale "must be created by running the update route" line corrected — the dogfood run already created it, set to `always`). The Open queue is now exactly nine genuine `Open:` items, no adopted/active mixed in.
- 2026-06-27: all work this session pushed to GitHub (`origin/master` at `1c4fb50`); the gitea mirror follows downstream (observed lagging earlier in the session; catches up). Per the `always` push policy, commits here push immediately rather than awaiting a per-instance go. (This handoff's own commit lands on top and is pushed next; a state line cannot name its own not-yet-created hash.)

## Next

- The `.agents/decisions.md` "Open Decisions" section is the authoritative queue for deferred/owner-approved-but-unimplemented items; consult it for what is awaiting a plan. Do not echo its count or contents here (anti-enumeration invariant) — read the section.
- **Decided 2026-06-28 — collapse the `update` route into `migration`.** Resolves the former self-contradictory `Open: bootstrap.config.json` fork (the owner chose to dissolve it, not pick (a)/(b)); that Open entry is archived verbatim in `docs/history/decisions-archive.md`, and `bootstrap.config.json` is dropped from the documented layout. The decision is recorded in `.agents/decisions.md` (2026-06-28); the implementation **plan is drafted at `docs/superpowers/plans/2026-06-28-collapse-update-route.md`** (six slices: discover.py+tests, the two procedures, README, the AGENTS template, and Open-entry rewording) and **awaits an owner go to implement** — no code touched yet. Key design point captured in the plan: the `update` route *fork* is removed but the stale-`AGENTS.md` reconciliation is *retained* (re-homed as a conditional in the migration route, gated by `agentsTemplate.reconcileRecommended`, not by a route name). Until the plan lands, the code still has three routes (the "Now" three-route line above is current and correct).
- 2026-07-03: the monorepo-subdir probe Open item was closed as not-applicable — owner resolved the precondition: subdir-scoped bootstrap is not a supported mode (verbatim template makes nested governance waste; per-subtree facts live in the single `.agents/` set). See the 2026-07-03 decision in `.agents/decisions.md`; original finding archived.
- Run harvest sweeps in this repo only on explicit owner request as harvest reports and bug reports accumulate in the dropbox (or fallback).
- Deferred: fix the `tools/discover.py` `operator:playbook` false positive (probe matches bare `` `playbook` `` but the operator is written `` `playbook <name>` ``, so the update route over-reports `reconcileRecommended`). The bug was filed to the `agent-harvest` dropbox on 2026-06-22; the fix (discover.py + a test using the realistic `` `playbook <name>` `` shape) is a separate scoped change awaiting owner go.
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.
- 2026-06-25: the **AGENTS.md governance boundary** (all three layers) is implemented and Adopted (see "Now" and the 2026-06-25 boundary decision). The **retroactive-cleanup follow-on is now specced** (see "Now" above) and **awaits owner review, then a `plan`**. Its three open questions for the plan: (1) signal shape — a separate `cleanupRecommended` vs. folding into `reconcileRecommended` (leaning separate); (2) sequencing — does the surplus computation ship inside the queued `governance-lint` playbook (Open Decision, 2026-06-22) or as a standalone discovery field, given `governance-lint` is approved-but-unbuilt (don't couple two unbuilt pieces); (3) within-section match granularity — how precisely a reworded target bullet must match its template counterpart before the remainder counts as surplus (lean toward over-reporting; the agent confirms, and a missed leak is the unsafe failure).
- 2026-06-27: **push-policy work is complete** (decision adopted, product changed, this repo dogfooded to `always`). The plan is at `docs/superpowers/plans/2026-06-27-push-policy.md`. Out of scope and not done: `discover.py` reading the `push-policy` marker; update-route reconciliation of *already-bootstrapped* foreign repos (they draft the file and ask on their next update run). No follow-up owed unless those are wanted.
- Deferred: the synchronous `review <agent>` operator ships as a playbook + Claude Code wrapper only. If it is ever promoted to a governance operator advertised in every `AGENTS.md`, the `OPERATOR_WORDS` staleness probe must first be reconciled with the existing deferred `operator:playbook` false positive (above) — adding `review` there would compound it. Not blocking; documented so the promotion is a deliberate step.
- Playbook process note: dispatching `codex` as a reviewer needs the prompt piped via **stdin** (`codex exec --skip-git-repo-check < prompt`), not as a positional arg — the argv form hung on stdin and timed out during the 2026-06-25 boundary-spec review. Worth folding into `templates/playbooks/reviewloop.md` when next touched.

## Blockers

- None active. (The eval-core launch gate was CLEARED 2026-06-29 — owner added the
  `Bash(docker exec:*)` permission rule; the autonomous agent now runs. See the keystone entry
  under Next.)

## Verification

- Changes that touch `tools/discover.py`, `tests/`, or any content under `templates/` or `procedures/` that the discover script copies into target repos: run `python3 -m unittest discover -s tests -v`.
- Documentation-only changes (no effect on setup, commands, runtime behavior, generated files, or user-visible behavior): run `git diff --check`.
- See `.agents/repo-guidance.md` (Verification) and `.agents/repo-map.json` for the policy that applies to future agents; `AGENTS.md` carries only the generic verification rules.

## Active Sources

- `AGENTS.md`
- `.agents/repo-guidance.md`
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
