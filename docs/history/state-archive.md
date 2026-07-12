# State archive

Landed or superseded `.agents/state.md` entries, rotated here verbatim at
handoff per the state-rotation rule (first applied 2026-07-08). New
rotations are appended at the end of the file; entries are never edited
after rotation. (Rule flipped from newest-first by owner ruling
2026-07-12 — appending is what writers naturally do, and the old rule was
violated three times; entries rotated before the flip are in mixed order
and stay where they landed.)

## Rotated 2026-07-12 (owner report) — fleet refresh run; qbit-mobile carve-out done

Disposition: owner reported both done 2026-07-12. The fleet refresh
propagated the 2026-07-10/11 template changes to governed repos; this
repo's own installed copies were not re-refreshed (no new commits — local
and GitHub HEAD both `e27fbc8` at the report) and still lag by the
2026-07-11 push-status template change, as `## Now` records. The two
`## Next` entries, verbatim:

- **Owner fleet-refresh pending**: the 2026-07-10/11 template changes
  (handoff/drift split, `machines.md`, plan bullet, review skill/wrapper,
  playbook hardening, push-status-never-recorded) reach governed repos only
  when the owner runs the fleet refresh. This repo's own installed copies
  were refreshed 2026-07-10 (`32b598a`) and lag only by the 2026-07-11
  push-status template change (self-refresh is owner-only, `292a4d2`).
- qbit-mobile (fleet context, 2026-07-09): refresh at toolkit `319324e`
  installed the shipped set and flagged its legacy `AGENTS.md`; the owner is
  running the bootstrap carve-out there — the first live exercise of the
  legacy-flag path. Not this repo's work item; friction observed there fed a
  smoother-entry proposal, declined by the owner 2026-07-09 (rotated
  verbatim to `docs/history/state-archive.md`).

## Rotated 2026-07-12 (drift) — be03b2c steady-state anchor; holistic-review pointer resolved

Disposition: superseded by re-anchoring to `0d05c97`. Two commits landed
after the `be03b2c` anchor: the owner ran this repo's self-refresh
(`32b598a`, 2026-07-10, toolkit `5574147`), and the push-status-never-recorded
decision landed with its template change (`0d05c97`, 2026-07-11). The
`## Now` entry, verbatim:

- Steady state as of `be03b2c` (2026-07-10): the 2026-07-08 zero-based
  consolidation is landed; the product shape is owned by
  `.agents/repo-guidance.md` (Mission Detail). Every 2026-07-10 plan is
  CLOSED with a commit map under `docs/superpowers/plans/`: the plan
  contract (`d3f49d3`), self-refresh-is-owner-only (`292a4d2`), the
  plan-lint suite (`279d25d`), carve-out two-commit route + git hard
  requirement (`2478103`/`dc87799`), refresh trust-boundary hardening
  (`9b3aa64`..`b24a0ab`), fresh-eyes clone rehearsal (`c85129e`), the
  handoff/drift split with tracked `.agents/machines.md` (`741f846`), the
  refresh plan/apply protocol + manifest schema + re-exec
  (`12b6bd4`..`300bff1`), reviewloop shipping + acceptance hardening
  (`77bbf60`/`7295d19`/`4562923`), and guidance-lint precision with a
  zero-warn baseline (`7074f6b`/`be03b2c`). GitHub issues #2/#3/#4 closed
  2026-07-10. The 2026-07-09 external holistic review is fully triaged:
  every accepted finding landed; release engineering is deferred by the
  release-posture decision; the per-repo verbosity/tech-level tuning idea
  is queued Open in `.agents/decisions.md`. This repo's installed copies
  intentionally lag the templates until the owner's next refresh
  (owner-only rule, `292a4d2`). Earlier landed work: bootstrap-offer
  banner (`f65e892`), dead-path lint (`e9e04b4`), newline equivalence
  (issue #1). Rollout DONE for vela, Blit_v2, ai-rpg-engine,
  Powershell-Token-Killer (details in `docs/history/state-archive.md`).
  Per-harness capability record: `docs/harness-capabilities.md`.

The `## Unrecorded Repo Memory` entry, verbatim (resolved: the untracked
review file no longer exists in the working tree — `git status` clean,
2026-07-12 — and the `## Now` entry above already records the review fully
triaged, with the "untriaged remainder" items landed as the 2026-07-10
plans or deferred by the release-posture decision):

- `HOLISTIC-REVIEW-GPT-5.6-SOL.md` (untracked, owner-side): external review
  assessed 2026-07-10; its verified findings are triaged into the four
  2026-07-10 draft plans. Untriaged remainder (plan/apply approval
  protocol, provenance pinning, review-loop shipping gap, release/CI
  items) awaits owner direction.

## Rotated 2026-07-09 (fifth rotation, mid-session on plan close) — dead-path lint landed

Disposition: landed 2026-07-09. Slice 1 (git-vouched deletions print `NOTE
... deleted in <hash>`) shipped in `e9e04b4`; slice 2 dropped on the owner's
call (added complexity for a low-value operation — the six never-tracked
mentions stay loud); plan closed with outcome record:
`docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`. Entry
rotated verbatim from `.agents/state.md` ## Next:

- Dead-path lint noise — plan drafted, awaiting owner go:
  `docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`. Owner set
  the direction 2026-07-09 (rejected live-with-it, per-repo list, global
  list, recent-only scoping; chose git-history evidence + "print the note"):
  git-vouched deletions print `NOTE ... deleted in <hash>` instead of the
  loud warning. Measured: clears 4 of the 10 decisions.md lines (and both
  state.md lines rotate away with this bullet); the plan carries one open
  owner question — slice 2, disposition of the six never-tracked mentions.

## Rotated 2026-07-09 (fourth rotation, mid-session on owner decision) — smoother-entry proposal declined

Disposition: declined by the owner 2026-07-09 (answer: "no"). Per its own
terms nothing was recorded: no decision entry, no plan, no code. The related
owner attestation (never hand-edits `AGENTS.md`) was record-on-go and
therefore remains unrecorded; the deferred fingerprint-gated option lapses
with the proposal. Entry rotated verbatim from `.agents/state.md` ## Next:

- **Smoother bootstrap/refresh entry — proposal on the table, awaiting the
  owner's go and a command name** (discussed 2026-07-09; no decision entry,
  no plan, no code yet). The shape: (1) launcher shims `bin/agb` +
  `bin/agb.cmd` (POSIX sh / Windows cmd only — no PowerShell) that embed the
  documented interpreter-probe order, resolve the toolkit root from their
  own location, and exec `tools/refresh.py`, plus a one-time per-machine
  PATH step; (2) a `bootstrap` operator skill + wrapper added to the shipped
  set (no machine paths — anchored on the canonical GitHub URL like the
  `update-governance` wrapper; self-guards when `.agents/repo-guidance.md`
  already exists); (3) refresh's closing output points at `/bootstrap`
  whenever the judgment layer is missing or `AGENTS.md` flags foreign.
  Owner-set constraints: must not assume Claude, PowerShell, a remembered
  path, or a remembered interpreter. Related owner attestation (stated
  2026-07-09, **not yet a decision entry** — record on go): the owner never
  hand-edits `AGENTS.md`; in this fleet an unmatched `AGENTS.md` is
  old-generator output to relocate, never owner edits. Deferred option if
  the EAW carve-out grates: fingerprint-gated preserve-then-replace for
  legacy `AGENTS.md` (old file preserved under `docs/history/`, template
  installed, only when toolkit fingerprints are present).
## Rotated 2026-07-09 (third rotation, mid-session on owner decision) — issue #1 closed on GitHub

Disposition: explicit owner go received 2026-07-09; the issue was commented
and closed the same day, citing fix commits `0151f5b` / `05e6c1e` /
`59439e7` and the plan's commit map. Entry rotated verbatim from
`.agents/state.md` ## Next:

- Issue #1 GitHub closure (comment-and-close, outward-facing): **awaits an
  explicit owner go**.
## Rotated 2026-07-09 (second rotation, evening) — PTK rollout done; issue #1 fixed

(Both landed 2026-07-09. The GitHub closure of issue #1 stays live in
`.agents/state.md` ## Next until the owner's explicit go.)

- Rollout: vela, Blit_v2, and ai-rpg-engine are DONE (2026-07-08; details
  rotated verbatim to `docs/history/state-archive.md`);
  **Powershell-Token-Killer DONE 2026-07-09, run by the owner** (refresh
  commit `602ee45` in that repo; the run's false CLAUDE.md flag is the
  evidence in issue #1). Rollout commits were local in those repos awaiting
  owner push as of their run dates — re-verify in those repos, not here.
- **GitHub issue #1 FIXED 2026-07-09** (owner approved the plan same day;
  slices `0151f5b` + `05e6c1e`; plan closed with commit map:
  `docs/superpowers/plans/2026-07-09-refresh-newline-equivalence.md`):
  refresh matching is newline-equivalent (at most one trailing final
  newline; candidate-set hashing keeps every recorded `formerly` hash
  valid) and both shims ship with a final newline. Suite 41 green,
  guard-proven both slices; post-fix self-refresh: "nothing to do".
  Remaining: comment-and-close issue #1 — **awaits an explicit owner go**
  (outward-facing).

## Rotated 2026-07-09 — consolidation/rollout landed entries and a resolved Next item

(The two `## Now` entries below landed 2026-07-08. In the `## Next` bullet,
the governance-lint disposition was resolved 2026-07-08 — adopted as the
always-on `lint_governance` in `tools/refresh.py` (`b9a867c`, refined
`8e6a42f`) and archived in the decisions archive sweep (`f3173ef`); the
agent-harvest half of that bullet stays live in `.agents/state.md`.)

- **Zero-based consolidation: IMPLEMENTED and self-applied 2026-07-08** (as of
  `6f08a67` here). Plan (approved, codex-accepted r8, commit map = the slice
  commits `657aa93..6f08a67`):
  `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`; the
  decision entry with the full supersession map is in `.agents/decisions.md`
  (2026-07-08). The product is now: one procedure + templates +
  `tools/refresh.py`/`shipped-set.json` + reviewloop + one hook + GitHub
  issues feedback. This repo refreshed itself with its own script (commit
  `d5ae8b3` + flag cleanup `6f08a67`).
- **Rollout status (2026-07-08):** vela DONE (`88be803` + carve `1b014e9`);
  Blit_v2 DONE (refresh + follow-up, rebased onto GitHub canon on owner go
  2026-07-08 → now `905c7d3` + `e5a78d9` on top of `b187b56`; the tripwire
  block was also removed from its owner settings.json since it invoked the
  deleted script; push-ready, owner pushes);
  ai-rpg-engine DONE (clone fast-forwarded 75 commits to canon `3d2cc87`
  first, then refresh `97f55fd` + follow-up `38cc4b2`; CLAUDE.md normalized —
  it differed only by a trailing newline). All rollout commits are LOCAL in
  their repos; every push policy there requires the owner.
- Owner, at leisure: archive the `agent-harvest` dropbox repo (feedback is
  issues now); disposition for the `governance-lint` Open entry
  (`.agents/decisions.md` — close as obsolete or re-scope).

## Rotated 2026-07-08 — pre-consolidation CURRENT FOCUS, Now, and Next

(All entries below were landed or superseded by the 2026-07-08 zero-based
consolidation — see that entry in `.agents/decisions.md` and the plan
`docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`.)

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

## Rotated 2026-07-08 — closed eval workstream's `## Next` history

(Superseded by the CURRENT FOCUS block of 2026-07-02: model testing and
end-to-end trials are closed; the evals workstream's files were deleted
from the tree 2026-07-08 — full record in git history.)

- 2026-06-29 **Ungoverned baseline probe DONE → Option A confirmed; 10-instance
  failure band in hand.** Ran the leak-free ungoverned arm (Claude Code, subscription
  auth, in-container as non-root `agent`, re-init anti-leak scrub) over a 20-instance
  complex+regression-rich sample. **Resolved 10/20 (50%)** — a usable headroom band
  (not the ~80% ceiling that killed the easy sample). **All 20 produced genuine
  non-empty source patches: 0 empty/infra failures, 0 non-`ok` statuses**, so the 10
  non-resolves are real agent failures, not measurement noise. Full result table +
  the 10 failure-band instance IDs (the candidate set for the governed factorial):
  `evals/swebench-pro/probe-2026-06-29-ungoverned-baseline.md`. Failures by repo:
  NodeBB ×3, openlibrary ×3, ansible ×2, qutebrowser ×1, element-web ×1. **NEXT:**
  before the factorial, apply the reviewers' must-fixes (pre-registered analysis +
  power/MDE; length-matched PLACEBO prose arm; F2P/P2P reported separately; re-measure
  the band with replicates so the confirmatory set isn't a single-n=20 regression-to-mean;
  ONE harness). Then the governed none/prose/prose-hooks factorial over the band.
  (Probe driver is still scratch; formalizing into `evals/` with arg-list hardening
  remains the deferred engineering step.)
  **Owner decisions (2026-06-29):** confirmatory harness = **Claude Code only** (codex
  a possible later add only if Claude motivates it and marginal cost is small;
  grok/agy testing-only); arms = **4-arm with placebo** (none / placebo-prose /
  real-prose / prose+hooks). **Pre-registration drafted** (the reviewers' gate):
  `evals/swebench-pro/PRE-REGISTRATION.md` — within-instance paired design, F2P/P2P
  reported separately, mixed-effects logistic with 3 pre-specified contrasts (prose−none,
  hooks−prose, prose−placebo), Holm multiplicity. **IMMEDIATE NEXT (modest compute,
  no further gate needed): the SIZING PILOT** — 4 arms × R=3 over ~8–12 band instances
  to estimate discordance + replicate variance, which sets R, the confirmatory N, and
  the replicated-rate selection band. Subset selection re-measures the band with
  replicates (regression-to-mean guard) before the confirmatory set is frozen.
  **PILOT RAN, but prose/hooks arms are INVALID (flagged 2026-06-30).** The sizing pilot
  completed (8 instances × 4 arms × 3 reps = 96 cells) and its results are committed at
  `evals/swebench-pro/opus-pilot-results.md` — BUT `arms4.py` injected the full
  `current-template` AGENTS.md as the prose arm, which the plan (Addendum b) deliberately
  excludes. The prose / `prose+hooks` columns are wrong-arm junk (and the hooks were
  re-ground/tripwire, not the `hook-gate`/`hook-guard` the plan specifies); `none` /
  placebo and the band-selection lesson stand. `PRE-REGISTRATION.md` §3 is corrected; the
  driver prototype still encodes the wrong arm (warned in its README). **Re-run the sizing
  pilot with `task-prose` / `task-prose-hooks` before reading any prose/hooks result.**
  KEYSTONES (in PRE-REGISTRATION): governance loads only via CLAUDE.md (bare AGENTS.md
  inert; `@AGENTS.md` import works); the arms' hooks — `hook-guard` (PreToolUse) and
  `hook-gate` (Stop) — DO fire in one-shot runs (the re-ground hook, which needs
  compaction, is not a test arm).
  **ROUTING (owner-decided 2026-06-29):** in-container agents route through the owner's
  **headroom** token-compression proxy (`ANTHROPIC_BASE_URL=http://10.1.10.221:8787`,
  passed via `docker exec -e`; PONG-verified through the proxy). Validity-safe and the
  more faithful subject: headroom compresses ONLY the newest user msg + latest tool
  result and NEVER mutates the system prompt — and Claude Code delivers CLAUDE.md/
  @AGENTS.md governance via the system prompt, so the treatment is uncompressed;
  compression is uniform across arms (constant factor, contrast preserved) and is a
  compressor not a response-cache (replicates stay independent). The first pilot launch
  was direct-to-Anthropic and was KILLED + relaunched so all 96 cells share one routing
  path (mixed routing would confound). Absolute rates reflect claude+headroom (the
  owner's real setup), which is intended.
  **CODEX secondary harness — keystones validated, but first pilot INVALID
  (2026-06-29).** Codex runs headless in-container via its native musl binary
  (`@openai/codex-linux-x64/.../bin/codex exec --dangerously-bypass-approvals-and-sandbox
  --dangerously-bypass-hook-trust --skip-git-repo-check -C /app`, prompt via stdin),
  subscription auth (`~/.codex/auth.json`, no API key), model gpt-5.5 at xhigh via the
  same headroom provider (`config.toml`). Validated: PONG, native binary, and codex
  loads `/app/AGENTS.md` natively (so governance injects as AGENTS.md directly, no
  CLAUDE.md shim; placebo = AGENTS.md-sized irrelevant prose). Driver
  `arms4_codex.py` (capture-vs-base + retry + preflight PONG). The 96-cell pilot
  COMPLETED but is unusable: **codex hit ITS OWN usage limit mid-run** (resets
  ~10:45 PM) → 69/96 empty (≈57 usage-limit + 12 proxy-blip neterr), only 27 real
  attempts, 0 resolved across all arms (not interpretable). LESSONS: (1) gpt-5.5 xhigh
  is far too token-heavy for a 96-cell window — chunk codex runs or lower effort;
  (2) the driver's invalid-cell detector must add the usage-limit signature
  ("hit your usage limit") as a distinct QUOTA-invalid flag, not counted as agent
  failure. Both Claude and codex caps were exhausted 2026-06-29; owner added Claude
  usage credits.

- 2026-06-29 **Leak fix validated + baseline confirmed GENUINE (not leakage).** Anti-leak scrub =
  re-init the agent workspace's git (`rm -rf .git && git init && git add -A && commit -m base`) so
  the gold fix leaves zero trace (bulletproof; ref-deletion+gc left it in a cruft pack, `git fsck
  --unreachable` still surfaced it — re-init is the robust fix). Ansible re-test with history wiped:
  STILL resolves, tests still run → (a) re-init doesn't break the build, (b) ansible's solve was
  genuine independent work, not the suspected leak. ⇒ the ~80% ungoverned baseline is a REAL ceiling,
  confirming the need for harder instances. **Candidate pool for option A:** 92 instances that are
  complex (gold ≥3 files) AND regression-rich (PASS_TO_PASS ≥15, F2P ≥3) — element-web 25,
  qutebrowser 23, ansible 19, NodeBB 12, openlibrary 7, others few. (Only 359/731 have ANY P2P.)
  Decision (owner 2026-06-29): go with **A — mine existing 731** for the hard/regression-rich band;
  reassess toward bug-authoring only if A yields too few agent-failures. NEXT: larger ungoverned probe
  over the 92 to find instances the agent FAILS (the experiment's headroom band).

- 2026-06-29 **Floor pilot v2 (5 instances, ungoverned): 4/5 resolved — but two big caveats that
  reshape the experiment.** (v1 was invalid: driver hardcoded the `node` user, which only exists in
  JS images; agent never ran on Python/Go. Fixed by creating an `agent` user in any image.)
  Verification of v2: element-web (1 file vs gold's 9) and flipt (3 vs 7) are genuine INDEPENDENT
  minimal fixes (low similarity to gold); qutebrowser same 3 files but 0.22 similarity (likely
  genuine); **ansible same 2 files + 0.76 added-line similarity → SUSPECTED LEAK**; navidrome
  genuine fail (8-file attempt, 2 PASSED).
  **CRITICAL — LEAKAGE VECTOR:** the gold fix commit exists as a reachable object in each
  container's git repo (`git cat-file -t <fix>` = commit; `git log --all` exposes future commits).
  An agent can search history and copy the fix. MUST be closed before any trustworthy rate:
  scrub the agent workspace's git to base only (e.g. `git checkout -B evalbase <base>`; delete all
  other refs; `git reflog expire --all --expire=now`; `git gc --prune=now`) so the fix is
  unreachable/pruned while base ancestry (version info) is preserved. Applies to ALL arms. Scoring
  is unaffected (it uses its own fresh image container).
  **CEILING RISK (owner flagged):** even discounting the leak, the ungoverned agent solves most of
  these → little headroom for governance to show an effect. Need HARDER instances (difficulty band
  where ungoverned fails) and a LARGER sample (power). Owner direction 2026-06-29: "we probably
  need more tests and more complex bugs." Open: select hard SWE-bench Pro instances vs author new
  bugs (cf. `docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`) — pending decision.

- 2026-06-29 **KEYSTONE COMPLETE — eval fully operational end-to-end with a real agent; launch
  gate CLEARED.** Owner added the `Bash(docker exec:*)` permission rule; the autonomous
  bypass-permissions agent now runs. First real ungoverned run (NodeBB instance
  `...04998908...-vnan`): agent investigated, produced a 231-line/7-file source fix, captured
  source-only (excluding the 3 test files + `dump.rdb`/`config.json`/`logs` test-run artifacts),
  scored **resolved=FALSE** — the agent did NOT solve it ungoverned. Notable: the agent CLAIMED
  its tests passed, but the held-out GOLD tests fail → the metric discriminates real resolution
  from agent self-report (good validity signal). Mechanics now proven for real:
  `docker run` instance image (mount host `claude` + cred) → setup non-root `node` user, chown
  `/app` → reset to base → `claude -p "$(cat task.md)" --permission-mode bypassPermissions` as node
  → `git add -A && git diff --staged` with test/artifact excludes → score via swe_bench_pro_eval.py.
  **NEXT: floor pilot** — run this ungoverned loop over a diverse ~15-20 instance sample to measure
  the baseline `resolved` rate (the reviewers' #1 de-risk; informs band selection + power). Then
  the design must-fixes (see review synthesis) before the governed factorial.

- 2026-06-29 **Plan reviewed by codex + claude (two blind reviews); science under-specified.**
  Synthesis: `docs/history/2026-06-29-swebench-pro-plan-review_synthesis.md` (raw reviews:
  `..._codex.md`, `..._claude.md`). Verdict: plumbing solid, experiment design/power not yet
  greenlightable. Converged must-fixes before P3: pre-registered analysis + power/MDE; a
  length-matched PLACEBO prose arm; metric honesty (report F2P/P2P separately, P2P empty ~64%);
  a NUMERIC floor-pilot gate; subset-selection rigor (no n=3-5 regression-to-mean); ONE harness
  for the confirmatory factorial (capability spectrum = separate study). The floor pilot is the
  #1 de-risk AND only needs the launch-gate sanction (Blockers). Plan NOT yet revised — design
  changes await owner decisions (see synthesis "Open decisions").

- 2026-06-29 **Keystone recon DONE — one remaining GATE: a sanctioned way to launch the
  autonomous agent.** Proven on netwatch-01: the host `claude` (native amd64 ELF v2.1.195) binary
  + `~/.claude/.credentials.json`, MOUNTED into an instance container, run **headless with
  subscription auth and NO API key** (a "reply PONG" test returned PONG; claude auto-wrote
  `~/.claude.json`, no onboarding block). Containers have node18 + working network (api.anthropic.com
  reachable) + the repo at `/app` checked out at base_commit. **Scoring contract mapped** from
  `swe_bench_pro_eval.py:114-126`: entryscript does `cd /app` → `git reset --hard base` →
  `git checkout base` → `git apply /workspace/patch.diff` → then overlays gold test files (ONLY the
  LAST line of `before_repo_set_cmd`) → runs run_script + parser. ⇒ the agent must submit a
  **SOURCE-ONLY diff vs base_commit**; P1 strips test files (scoring overlays gold tests regardless,
  but stripping blocks test-gaming).
  **GATE (needs owner):** the eval's core is an unsupervised, permission-bypassed coding agent run
  in-container. This Claude Code session's auto-mode classifier blocks the agent (me) from spawning
  `claude -p --permission-mode bypassPermissions` ([Create Unsafe Agents]) — a legitimate guard;
  do NOT evade it (no hiding the spawn inside a wrapper script). Sanctioned options: (1) owner adds
  a scoped Bash permission rule allowing the eval's bypass-agent invocation, so this session can
  develop+run it autonomously; (2) owner runs the eval driver themselves; (3) run the eval in a
  non-auto-mode session.
  **UPDATE 2026-06-29 (capability fully proven; only the sanction remains):** in-container claude
  refuses bypass as ROOT, but runs fine as the image's non-root `node` user (uid 1000) — credential
  copied to `/home/node/.claude/`, `/app` chowned to node. A trivial bypass edit
  (`AGENT_PROOF.txt`) succeeded → the headless autonomous-edit capability works end to end. BUT the
  classifier then blocked the REAL autonomous source-editing run, explicitly reading the owner's
  "invoke … to run tests or review plans" grant as NOT covering an unsupervised bypass source-editing
  agent. So the eval's core still needs an explicit sanctioned launch: (1) owner adds a Bash
  permission rule (e.g. allow `docker exec`) so this session drives it; (2) owner runs the driver
  themselves (spawns happen in their process, not via this session's classifier); or (3) non-auto-mode
  session. Do NOT add such a rule to repo/owner settings unilaterally — it is a security-relevant
  roadblock; owner decides. Everything UP TO the agent spawn is buildable/validatable now using the
  gold patch as a stand-in agent (plain git/scorer calls, not gated).
  **VALIDATED 2026-06-29:** capture round-trip works — gold applied into `/app` as a stand-in agent
  output, captured a SOURCE-ONLY diff via `git add -A && git diff --staged -- . ':(exclude)<testfiles>'`,
  fed to the scorer as a mock prediction → resolved=true. So container-working-tree → source-only
  capture → scorer is proven; only the sanctioned autonomous agent spawn remains. (Note: after
  chowning `/app` to node, root git needs `git config --global --add safe.directory /app`.)

- 2026-06-29 **Gold-resolvability sweep (3 instances/repo, 33 total): 33/33 ≈ 100% resolvable.**
  One openlibrary instance scored false on the first parallel pass but resolved on isolated retry
  (6 PASSED) — so the dataset's gold patches are clean on this substrate; no instance needed
  exclusion in this sample.
  **CRITICAL methodological finding — transient infra failure under parallelism:** at
  `--num_workers=4`, heavy containers occasionally produce **NO output at all** (the instance
  output dir has the workspace but no `gold_output.json` / no stdout/stderr logs), which the scorer
  counts as `resolved=false`. This is DISTINGUISHABLE from a real test failure (empty/absent output
  vs. `gold_output.json` present with FAILED tests) and is RETRYABLE. **P1 MUST: (a) detect the
  "no output produced" case and retry it, (b) never count an infra-empty run as an agent failure,
  (c) keep parallelism modest for heavy repos (Go/webclients images are 5–12 GB).** Counting a
  transient infra flake as the agent failing would silently corrupt the governance-effect measurement.

- 2026-06-29 **P0 DONE — substrate PROVEN on the amd64 Linux box; the blocker below is CLEARED.**
  Box: `netwatch-01` (CachyOS, x86_64, native amd64 — no QEMU), Docker engine active, system
  `python3` is **3.14** (parses the tests), SWE-bench Pro checkout is at
  **`/home/michael/dev/SWE-bench_Pro-os`** on this box (NOT the Mac `/Users/...` path the block
  below names). P0 gold round-trip on instance
  `instance_NodeBB__NodeBB-04998908ba6721d64eba79ae3b65a351dcfbc5b5-vnan`: gold patch scores
  **resolved=true** (300 PASSED/0 FAILED, clean `--redo` container run ~11s); empty-patch negative
  control scores **resolved=false** — so the metric genuinely discriminates. Artifacts in session
  scratchpad, not committed.

- 2026-06-29 **Multi-repo gold round-trip: 11/11 PASS — substrate generalizes across ALL 11 repos**
  (one instance each: NodeBB, qutebrowser, ansible, openlibrary, element-web, navidrome, teleport,
  vuls, flipt, tutanota, webclients; JS/Python/Go/TS). Every gold patch scores resolved=true with
  non-vacuous PASSED counts (each ≥ its F2P+P2P). Done via a reusable adapter
  (`scratchpad/adapter.py`, the P1 seed) that encodes the two gotchas below.
  **Finding (metric design):** `PASS_TO_PASS` is EMPTY for 7 of the 11 sampled instances
  (element-web, navidrome, teleport, vuls, flipt, tutanota, webclients) — so the planned SecPass
  dimension is frequently absent and `joint_pass` collapses to FuncPass there. The plan's
  FuncPass∧SecPass framing must account for SecPass being empty on many instances.
  **Disk sizing (corrected):** on-disk image footprint is **1.6 GB (ansible) → 12 GB (webclients),
  avg ~4.4 GB**; 11 images = 48 GB on disk; 367 GB free. NOTE the earlier "807 MiB" was the
  *compressed pull* size, not on-disk — NodeBB is 3.18 GB unpacked. A ~20-instance subset is
  roughly 50–130 GB on disk depending on repo mix (not "<20GB").

  **Adapter gotchas the P1 instance-adapter MUST encode** (the shipped `swe_bench_pro_eval.py` was
  written for the leaderboard CSV; our jsonl trips two real mismatches — worked around by deriving
  a per-instance sample file, NOT by editing the third-party script):
  (1) **case** — jsonl has `FAIL_TO_PASS`/`PASS_TO_PASS`, scorer reads lowercase
  `fail_to_pass`/`pass_to_pass`; must alias. (2) **type** — scorer does `eval(field)` expecting a
  *string*, but in the jsonl `FAIL_TO_PASS` is a native JSON **list** while `PASS_TO_PASS` is a
  **string** (inconsistent source data); coerce both to string form (survives the pandas
  `read_json` round-trip). Operational: `run_scripts/` (1000 dirs) is present and `instance_id`
  matches dir names exactly; image = `get_dockerhub_image_uri(uid, 'jefzda', repo)`; **always pass
  `--redo`** or the per-instance output cache silently reuses a stale run.

  **Next:** architecture decision, then P1 adapter, P2 subset selection.
  **CORRECTION (owner, 2026-06-29): there are NO API keys in this eval.** The subject under test is
  a **(harness + model)** pair authenticated by a **subscription login** (e.g. Claude Code on a
  Claude subscription, Codex on a ChatGPT subscription) — not API access to a model. So "Option A
  needs API keys" was wrong; Option A's only setup cost is doing the harness's **subscription login
  on netwatch-01**. (Assumption pending owner confirmation, not yet a settled decision: the agent
  should run *inside* the instance container so it can run tests/verify while solving — both because
  the containers are amd64-only/native here and because governance is largely verification
  discipline; that points to running the harness here = Option A.)

- 2026-06-29 **HANDOFF (superseded by the P0 entry above for substrate status; pivot context still
  valid). Eval workstream pivoted to SWE-bench Pro.** Read the P0 entry first, then the two plans
  named below.

  **Where we are:** the governance-efficacy eval's *measurement instrument* is fully built and
  pushed (Phase 0 hardening + the Phase-1 fixture/arms machinery — see the dated entries below).
  But the **synthetic-fixture approach is DEAD**: the frontier-calibration run (Slice F) showed
  Claude clean-passes all 5 hand-built fixtures 10/10 and GPT-5 the same on the 2 it finished —
  zero naive traps, every fixture drops as "too easy" (a model can't invent a bug that stumps
  itself). That result is the whole reason for the pivot; do not retry synthetic fixtures.

  **The pivot (owner-directed):** use **ScaleAI SWE-bench Pro** as the fixture source. Full local
  checkout at **`/Users/michael/Dev/SWE-bench_Pro-os`** (731 real instances in
  `helper_code/sweap_eval_full_v2.jsonl`, 11 repos, multi-language, frontier-resistant). Mapping:
  **FAIL_TO_PASS = our FuncPass, PASS_TO_PASS = our SecPass/regression guard**, so our existing
  **`joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS`** metric and invalid-trial accounting apply
  unchanged. Their `swe_bench_pro_eval.py` is a pure function `(predictions.json, sample) →
  resolved` that scores a patch inside a per-instance Docker image — agent and scorer are
  decoupled by a predictions-JSON file boundary. Integration plan (DRAFT, pre-codex-review):
  **`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`** (pipeline,
  phases P0–P3, open decisions G1–G5). Background + why-the-synthetic-approach-died:
  **`docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`** (its SWE-bench Pro
  addendum supersedes it; the crafting loop is the documented fallback only).

  **THE BLOCKER — CLEARED 2026-06-29 (see P0 entry above).** It was: SWE-bench Pro instance images
  are **amd64-only** and their **test runtimes segfault under Rosetta/QEMU on Apple Silicon**
  (verified: `python3 --version` segfaulted inside `jefzda/sweap-images:ansible...` on the Mac).
  Resolution: the eval now runs on the amd64 Linux box `netwatch-01` where images run natively;
  P0 gold round-trip passed there. The Mac Colima path is abandoned for scoring.

  **Public images:** `jefzda/sweap-images` on Docker Hub (the metadata jsonl points at a *private*
  ScaleAI ECR; ignore that). Derive the pull tag with `helper_code/image_uri.get_dockerhub_image_uri(
  instance_id, 'jefzda', repo)` (it truncates tags >128 chars). Score with
  `swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
  --dockerhub_username jefzda --use_local_docker`.

  **NEXT ACTIONS on the Linux box (in order):**
  1. **P0 — gold round-trip (no governance yet):** on the amd64 box with Docker, pull ONE instance
     image, run `swe_bench_pro_eval.py` on that instance's **gold `patch`** (shipped in the jsonl)
     and confirm it scores **resolved**. This proves the substrate before producing any agent patch.
  2. Decide the architecture (open in the plan): **Option A** = agent runs + scores all on the box;
     **Option B** = governed agent runs on the Mac (our harness/hooks/keys already work), patches
     copied to the box which only scores. Option B needs local `git clone <repo>@base_commit` for the
     agent's workspace; Option A needs model API keys + our harness on the box.
  3. Then P1 (instance adapter + clean patch capture — exclude governance overlay/sentinels from the
     diff), P2 (subset selection: ungoverned FAIL_TO_PASS probe, keep ~20 mid-band instances across
     diverse repos), P3 (the none/prose/prose-hooks factorial). Codex-review the integration plan to
     convergence before building (the workstream's standing discipline).

  **Biggest risk to watch (in the plan):** floor mirror of the earlier ceiling — SWE-bench Pro is
  HARD, so a one-shot Claude-Code/codex driver may resolve ~0 ungoverned, leaving no room to show
  improvement. Subset selection (mid-range ungoverned rate) guards this; if even mid-band instances
  resolve at ~0 the driver (G3) needs a real agentic loop before the factorial.

  **What's reusable as-is:** governance profiles (`evals/governance_profiles/`: none,
  current-template, hook-gate, hook-guard, prose-hooks), `joint_pass`+invalid accounting in
  `evals/aggregate.py`, the claude/codex drivers in `tools/drivers.py`, `evals/calibrate.py`
  (its classify/Wilson logic still scores an ungoverned probe). **Retire/ignore for SWE-bench Pro:**
  the 5 synthetic fixtures, `--check-discrimination`, the calibration *band* gate as a fixture
  source. **Test interpreter: homebrew `python3` (3.14)** — system 3.9 can't parse the tests.
  All eval work pushed to `origin/master` (last: SWE-bench Pro integration plan draft).

- 2026-06-28: **active research workstream — governance-efficacy measurement (`evals/`).** A
  validated, three-times-externally-reviewed experiment plan to measure whether (and which)
  governance components causally help coding agents, lives at **`evals/TEST-PLAN.md`** — start at
  its **§15 "Resume here"** for status, the built harness, model hosts, gotchas. Screening
  findings in `evals/RESULTS-*.md` (frontier models ceiling; security prose ≈ placebo; hooks
  transfer, prose is model-capped). This is a measurement effort *about* the toolkit, separate
  from the toolkit's product backlog below.
- 2026-06-28: **Phase 0 (harness hardening) is COMPLETE and pushed** (master 2bcf6ae..747078b).
  Owner suspended per-slice go for this eval workstream; plan was codex-reviewed to convergence
  (3 passes) first. Seven slices, each committed + mutation-proven + pushed (push policy `always`):
  S1 changed_files fix (overlay before trial-base) + profile collision guard; S2 strip
  pre-existing governance (deletion-safe subset, narrower than discover's detection list);
  S3 driver telemetry (tokens/cost/tool_calls) + transcript redaction to a **gitignored**
  `evals/results/transcripts/`; S4 hook telemetry (present/supported_by_driver/fired via an
  **external** sentinel) + new `hook-smoke` profile; S5 `profile_tokens`; S6 result
  `schema_version`=2 + aggregator telemetry columns & mixed-schema flag. Plan +
  S7 live-smoke evidence: `docs/superpowers/plans/2026-06-28-phase0-harness-hardening.md`.
  **Test interpreter note:** the suite needs **homebrew `python3` (3.14)** — the system
  `/usr/bin/python3` (3.9) cannot parse the tests' `X | None` annotations. 104 tests green.
  Four clean baseline fixture repos prepped under `../test_ground/` (blit_v2, headroom,
  qbit-mobile, rtk — governance stripped, fresh `git init`, no remotes).
  **Model-host note:** drive local models via the **on-host ollama (`localhost:11434`)** —
  local set is `qwen3.6:35b-mlx`, `gemma4:31b-mlx`, `ornith:35b`,
  `north-mini-code-1.0:mlx-mxfp8`. The remote `10.1.10.221` ("Q") is a different host
  serving mostly `:cloud` models and is **not** the local-model source. S7 smoke was
  validated on the local `qwen3.6:35b-mlx` (FuncPass + live hook firing).
  **Next: Phase 1** (build the real-repo fixture set from those repos, calibrate, freeze) —
  per TEST-PLAN §10. Phase 1 is approvable once fixture manifests + metric defs exist; the
  open owner decisions in TEST-PLAN §12 (tier, repos, H6 approval arm, proportionality rule)
  still gate the *screening* runs, not fixture construction.

## Rotated 2026-07-09 — agent-harvest archive reminder, owner took it off the books

Owner direction 2026-07-09: stop tracking the `agent-harvest` dropbox-repo
archive item in this repo's state; the owner will clean it up directly. Not
done, not declined — just no longer this repo's ledger entry. The `## Next`
bullet, verbatim:

- Owner, at leisure: archive the `agent-harvest` dropbox repo (re-verified
  still unarchived 2026-07-09 via `gh repo view --json isArchived`).

## Rotated 2026-07-09 — smoother bootstrap/refresh entry, landed

Landed as the banner + bootstrap offer in `f65e892` (plan closed:
`docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`; decision
entry 2026-07-09 in `.agents/decisions.md`). The `## Next` bullet, verbatim:

- **Smoother bootstrap/refresh entry — direction named (owner, 2026-07-09);
  plan drafted, awaiting owner go:**
  `docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`. The
  direction: the refresh output that matters is an unmissable notice that a
  core file was NOT replaced, for any reason; the notice resolves to "run
  bootstrap," and refresh offers to run bootstrap with a harness chosen from
  those installed at that moment. The owner constraints still stand (must
  not assume Claude, PowerShell, a remembered path, or a remembered
  interpreter); the earlier declined shim/skill/pointer proposal stays
  declined and archived verbatim in `docs/history/state-archive.md`.

## Rotated 2026-07-10 — Codex 0.144 surface evaluation, settled

- Tooling evaluation, no product change (`fbe9087`, 2026-07-09): the Codex
  CLI's newer surface (`codex-cli 0.144.0`) was checked against the
  `reviewloop` dispatch contract. `codex mcp-server` was tested (MCP
  `initialize` + `tools/list` over stdio, inspection-only): protocol
  `2025-06-18`, exposes `codex` + `codex-reply` tools with structured
  `sandbox`/`approval-policy` inputs. Viable alt reviewer transport but not
  adopted (returns free-form `content`, not our fail-closed verdict envelope;
  stateful `threadId` vs. our one-shot atomic unit); `codex exec`+stdin
  dispatch retained. Decision entry 2026-07-09 in `.agents/decisions.md`.

Rotation note: settled by decision and then exercised for real — the
2026-07-10 pxpipe reviewloop ran nine `codex exec`+stdin dispatches
(codex-cli 0.144.1) end-to-end, confirming the retained contract.
