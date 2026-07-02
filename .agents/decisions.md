# Agent Decisions

Record durable repo decisions here. Do not use this as a chat log. Each entry should make
sense without conversation history and should name superseded guidance when relevant.

Keep this file to what is currently in force or still open. When a decision is
closed - superseded, or settled and retained only as the rationale for a rule that
now lives in its canonical home elsewhere - move it verbatim, in that same change,
to `docs/history/decisions-archive.md`; never summarize or drop wording, the exact
text is the record. That archive is the provenance log; this file is what is in
force or still open.

Archive: closed (Adopted / Superseded) decisions live in
[`docs/history/decisions-archive.md`](../docs/history/decisions-archive.md).

## Decision lifecycle

A decision moves through these states:

- **Open** - a finding has been assessed but not yet acted on. It lives in the
  `## Open Decisions` queue below, with the verified evidence, the options, and a
  standing recommendation. The process is unchanged until it is adopted; an agent
  records it rather than implementing on the spot.
- **Active** - a decision that is in force now.
- **Adopted YYYY-MM-DD** - an Open finding that has been acted on: its rule now
  lives in its canonical home (a procedure, template, or invariant). Note where the
  rule landed; the finding is retained in place as the rationale that led to it,
  until it is archived.
- **Superseded** - replaced by a later decision; name the replacement.

When an entry becomes purely historical rationale - Adopted or Superseded, with the
live rule now owned elsewhere - archive it per the rule above: move it verbatim to
`docs/history/decisions-archive.md`, do not leave a stub.

## Decisions

### 2026-07-01 — AGENTS.md is the verbatim template, wholesale-replaced on update; repo-specifics live in one designated `.agents/` file

Status: Active (owner decision 2026-07-01; implementation deferred to
`docs/superpowers/plans/2026-07-01-agents-md-verbatim-template.md`).

Decision: In every bootstrapped repo — this toolkit included — `AGENTS.md` is
**byte-identical to the shipped `templates/AGENTS.template.md`**. All
repo-specific guidance (mission detail, active sources, verification
specifics, earned rule variants, remotes/push facts) lives in one designated
repo-specific file under `.agents/` that a template-owned pointer names.
Consequences:

- **Update = wholesale replacement.** A refresh run replaces `AGENTS.md` with
  the current template and touches nothing in `.agents/`. No carry-forward
  judgment, no hunk-walking, no stamp reasoning.
- **Drift detection = byte-compare.** Discovery compares the target's
  `AGENTS.md` against the current template; any difference recommends
  reconciliation. The `templateVersion` stamp becomes informational — the
  byte-compare is the load-bearing signal and is judgment-free.
- **Repo content enters `AGENTS.md` never.** First bootstrap/migration carves
  existing repo-specific guidance into the designated `.agents/` file; the
  portability sweep becomes that carve-out, run once, mechanical thereafter.

Earned by the 2026-07-01 incident chain, which showed the mixed-content design
fails twice over: (1) the dogfood self-application run stamped this repo's
`AGENTS.md` `2026-07-01.2` while seven pre-condensation template passages
remained — the stamp + structural-probe signals cannot see wording drift, and
a wrong stamp write self-seals (every later run reads "current"); (2) the
correction was then applied outside the sanctioned write path (`f697bf9`),
violating write-authority — mixed content invites exactly such judgment
edits. Separating template from repo content removes the judgment from the
loop entirely: the same mechanism-over-prose conclusion the eval workstream
reached for model guidance, applied to our own procedures.

Relationship: operationalizes the 2026-06-25 governance-boundary decision,
which recorded the portable/repo-specific *boundary* but not the
wholesale-replaceability rationale or the designated-file mechanism (the
owner's intent, stated at the time, had not been captured — this entry closes
that gap). Supersedes the 2026-06-25 scope-guard deferral of "retroactive
cleanup of already-bootstrapped repos" for any repo that refreshes (the
replacement run performs the cleanup), and supersedes this repo's own
`AGENTS.md` self-exemption parenthetical (removed when the file is replaced).
Simplifies, does not remove, the 2026-06-22 `templateVersion` machinery (the
stamp stays for reporting; byte-compare carries the decision). The 2026-07-01
portability-sweep rule (earlier entry, this file) is refined from
"relocate line-by-line during reconciliation" to "carve out once at first
migration; thereafter the file is replaced whole."

### 2026-07-01 — Governance refresh entry point; portability sweep in reconciliation; Python 3.9 floor

Status: Active (implemented same day; plan:
`docs/superpowers/plans/2026-07-01-route-collapse-refresh-and-portability-sweep.md`).

Three durable rules landed alongside the route-collapse adoption (see the
Adopted 2026-06-28 entry below):

- **`update-governance` is a wrapper-only entry point** shipped at
  `templates/commands/claude/update-governance.md`: verify the canonical
  remote, shallow-clone fresh to scratch, follow the synced
  `procedures/bootstrap.md`. It is not an `AGENTS.md` operator and adds no
  write authority — every change still passes the approval gate. The wrapper
  guarantee is keyed to the shipped template directory
  (`templates/commands/<harness>/`), not to the operator vocabulary, so
  non-operator wrappers join it without editing governance. The toolkit repo
  itself receives the wrapper only via a dogfood self-application run (owner
  pick, 2026-07-01) — that run doubles as the end-to-end test of the flow.
- **The reconciliation branch runs a portability sweep** (full statement:
  `procedures/migration.md` Step 2): every carried-forward `AGENTS.md` line
  faces the portability test; repo-specifics relocate to `.agents/` with
  pointers, through the same approval summary. This implements, for every
  refresh run, the retroactive cleanup the 2026-06-25 boundary decision
  deferred; a dedicated one-shot cleanup pass is no longer needed for repos
  that refresh. Mid-task relocation remains the `drift` operator's job.
- **Python 3.9 is the supported floor** for the toolkit's product code
  (README / docs/usage.md); below-floor probes fall through to versioned
  interpreter names (`procedures/bootstrap.md` step 3). Earned by a real
  incident: `tests/test_run_fixture.py` used PEP 604 syntax, failed to import
  on the macOS system 3.9, and silently hid 84 tests behind one import error
  (fixed 2026-07-01, commit ad7e9e8).

Also fixed under the same plan: the `operator:playbook` probe false positive
(bug filed 2026-06-22) — the probe now word-boundary-matches, guarded by a test
that the shipped template self-reports zero missing sections.

### 2026-07-01 — Functional cut of the product template; completeness prose deferred entirely

Status: Active (implemented same day; `templateVersion` 2026-07-01.1).

Decision: `templates/AGENTS.template.md` underwent a **functional cut** — every
clause classified as behavioral contract, fact/pointer, or definition was kept
(surviving claims keep full-sentence wording); rationale clauses, worked
examples, and same-altitude duplication were removed. The largest single change
applies the 2026-06-24 dedup decision: the `drift` operator no longer restates
the portability test and its Flag/Allow lists — it points to the
governance-boundary invariants, which keep the single full statement. Session
Startup was reduced to its two load-bearing steps (read state before changes;
hook trust). Result: 13,355 → 10,623 bytes, 1,993 → 1,587 words (−20%),
roughly 600–700 tokens saved per session in every bootstrapped repo.
Owner signed off a full per-claim accounting with an explicit drop list at the
approval gate; plan and drop list:
`docs/superpowers/plans/2026-07-01-guidance-condensation.md`.

Also settled: **`completeness-general` prose is deferred entirely** — not
shipped in any form (not even opt-in). Eval evidence: weak-model-only benefit,
one ceiling harm, null on strong harnesses. The profile remains in
`evals/governance_profiles/` as a candidate; any future ship is a fresh owner
decision. This closes the former G1/G2 question from the 2026-06-30
hook-and-prose plan.

Earned by the closed eval workstream's conclusion (guidance prose is
placebo-to-harmful on strong models; the per-session size of the injected
template is a recurring tax) and by the owner's 2026-06-30 direction to make
the existing guidance more token-efficient. Notably, the cut found **no
capability-exhortation prose in the template** — the removed mass was rationale
and duplication — consistent with the 2026-06-22 density audit.

Relationship: complements, does not supersede, 2026-06-22 (word-level
compression stays rejected; this cut removes whole non-normative clauses, never
squeezes surviving wording) and applies 2026-06-24 (one full statement,
pointers elsewhere) inside the template. Exercises the 2026-06-22/25.2 stamp
machinery (dotted sub-version, enforced by test). Scope: template only —
`procedures/` condensation was explicitly deferred (owner pick S1) and needs
its own plan; this repo's own `AGENTS.md` is a frozen instance reconciled only
by a future self-application run.

### 2026-06-28 — Collapse the update route into migration; route detection is not load-bearing

Status: Adopted 2026-07-01. Implemented per
`docs/superpowers/plans/2026-07-01-route-collapse-refresh-and-portability-sweep.md`:
`compute_route()` is single-route (commit 07ceb09), the reconciliation branch
lives in `procedures/bootstrap.md` Step 3 with `procedures/migration.md` naming
the already-canonical and dogfood cases, and `bootstrap.config.json` left the
documented layout (README, design doc, repo-map template) with `templateVersion`
bumped to 2026-07-01.2 (commit a48790d). Text below retained as rationale until
archived.

Decision: The `update` route collapses into the `migration` route. One route
then handles every repo that already has governance — a foreign governance
system to inventory, an already-toolkit-bootstrapped repo, or this toolkit's own
self/dogfood run — with the `<!-- templateVersion -->` reconciliation of a stale
or unstamped `AGENTS.md` (the 2026-06-22 decision) retained as a branch *within*
that single route, not removed. `greenfield` (a repo with no existing governance)
stays a distinct route; whether it too should fold is explicitly **not** part of
this decision. What is eliminated is the `update`-vs-`migration` "is this repo
already ours" determination in `compute_route()` — that detection was never
load-bearing.

Reason: every route converges behind the same approval-summary gate and produces
the same vetted output, so route selection only ever affected *speed*, never
correctness or safety. A misroute's worst case is "ran the slightly heavier
procedure," not a wrong result. Both candidate ownership signals — the presence
of `.agents/state.md` (a generic name a foreign system could also use) and a
`bootstrap.config.json` marker — are weak as provenance. The owner principle on
record (thorough every time; duration matters less than thoroughness) favors one
thorough path over two paths plus a fragile detector. This also drops
`bootstrap.config.json` from the documented `.agents/` layout in `README.md`:
nothing ships it, and the `AGENTS.md` `templateVersion` stamp already covers the
only real provenance need.

Considered and rejected: (a) ship `bootstrap.config.json` as a provenance/version
marker — adds a new required artifact on every bootstrapped repo and a second
version-of-truth source that drifts from the `templateVersion` stamp the moment
one is edited without the other, against the smallest-guidance-set invariant and
the 2026-06-28 harness-neutral / no-redundant-provenance direction; (b) keep two
routes but switch the update marker to the `templateVersion` stamp — zero new
files, but still treats "is this ours" detection as load-bearing for no
correctness gain. The fork is dissolved rather than answered.

Accepted cost: an already-bootstrapped or dogfood run now does the unified
route's inventory pass over files already in canonical layout (verdict "leave /
already-canonical") — slightly more ceremony than `update`'s reconcile-only path,
converging correctly at the same gate, consistent with thorough-every-time.

Scope / deferral: implementation is owner-gated code/procedure work needing a
separate `plan`, and touches `tools/discover.py` `compute_route()` (drop the
`update` branch), the procedure merge (`procedures/bootstrap.md` +
`procedures/migration.md` into one route, folding in the `templateVersion`
reconciliation branch and the dogfood-in-place lens), `README.md` (drop
`bootstrap.config.json` from the documented layout),
`templates/AGENTS.template.md` Bootstrap Handoff / any "update route" wording,
and the several Open entries that name "the update route" (the monorepo-subdir
probe, committed-wrapper staleness, the `governance-lint` update-route
recommendation) reworded to the single route in that plan. The `templateVersion`
reconciliation machinery is retained — it moves into the single route, it is not
dropped.

Relationship: resolves the `Open: bootstrap.config.json` fork (archived verbatim
in `docs/history/decisions-archive.md` in this same change) and answers its
2026-06-23 reframe — "the question may be better framed as whether to collapse
the update route into migration" — in the affirmative. Exercises, does not
supersede, the 2026-06-22 update-route `templateVersion` reconciliation decision
(that step is folded into the single route). Amends the 2026-06-27
dogfood/self-application decision's "takes the existing `update` route" wording:
the dogfood case becomes a named in-place case of the single route (run the one
procedure in-place; a missing `.bootstrap-tmp/` at kickoff is still the normal
start); that decision otherwise stays Active and its anti-stop handrail is, if
anything, more necessary because the unified route inherits migration's
foreign-target framing.

Earned by the 2026-06-23 reframe of the `bootstrap.config.json` Open Decision and
this session's analysis confirming detection only affects speed and a new marker
file fights the recent harness-neutral direction. Owner decided 2026-06-28.

### 2026-06-28 — Durable truth lives only in harness-neutral files; harness-specific files are pure adapters

Status: Active (principle in force now; enforcement implementation deferred to a plan)

Decision: Durable repo truth — governance and repo-specific facts alike — lives
only in harness-neutral files: `AGENTS.md` (portable governance) and `.agents/`
(repo-specifics). Harness-specific entry and config files — `CLAUDE.md` and
equivalents (`GEMINI.md`, `.cursorrules`), the per-harness hook configs, and the
`.claude/commands/` wrappers — are **pure adapters**: a pointer (`CLAUDE.md` is
`@AGENTS.md` and nothing else) or a thin wrapper that calls a harness-neutral
entry point. They carry no repo facts or governance of their own. A
harness-specific file that holds durable truth is a **drift inflection point**:
invisible to every other harness reading `AGENTS.md`/`.agents/`, maintained in a
silo that diverges from the neutral source.

Corollaries settled in the same session:

- **Durable repo facts a working model learns** (not a decision, not churny
  current-state) have a home: `.agents/repo-facts.jsonl` — JSONL, append-only
  (one fact per line), `evidence` field required, read on demand, never
  auto-injected. It is the in-repo, harness-neutral equivalent of a harness's
  "auto memory" (which the harness-local-memory invariant forbids relying on).
  JSONL is chosen because the data is atomic/append-only/provenance-bearing:
  append-safety enforces the anti-rewrite discipline, a required `evidence` field
  bakes in the evidence rule, and it is mechanically validatable by
  `governance-lint`.
- **`.agents/` is an agent-facing store.** Human-readability is an explicit
  non-goal (JSON tooling covers forensics). Design priority for `.agents/`:
  prevent drift first, then agent efficiency / token savings. This priority
  governs future `.agents/` format and structure choices.
- **A must-always-see operational fact is made reliable the harness-neutral way**
  — encode it as a runnable entry point (e.g. verification = a `make`/script
  target recorded in `.agents/repo-map.json`, run not read), not by auto-loading
  it. An `@`-import auto-load of repo facts (via `CLAUDE.md` or a
  `.agents/repo-facts.*` imported file) was considered and **rejected**: it loads
  on Claude Code but is invisible to other harnesses, bifurcating the source of
  truth.

Enforcement (implementation deferred to a plan): extend the advisory `AGENTS.md`
pre-edit tripwire to also fire before edits to `CLAUDE.md` and other harness entry
files, with a pure-adapter message distinct from the portability message; add a
`governance-lint` structural check that harness-specific files contain no durable
content. The hook stays advisory, non-blocking, Claude Code + Codex only — the
cross-harness floor is unchanged.

Earned by a design near-miss caught in this session's review: to make the
verification command reliably visible under a strict-portable `AGENTS.md`, an
auto-load via a Claude-Code-only `@`-import was proposed and rejected for the
bifurcation above; the same session then established the harness-neutral facts
home and the agent-facing `.agents/` priority.

Relationship: extends the 2026-06-25 governance-boundary decision (which named the
`AGENTS.md`↔`.agents/` *content* boundary) with the harness-neutral↔harness-
specific *file* boundary and the pure-adapter rule; generalizes the
harness-local-memory Universal Invariant (out-of-repo stores are not durable) to
in-repo harness-specific files. Affected guidance to reconcile in the plan:
`templates/hooks/*` (tripwire path matcher + message), `procedures/bootstrap.md`
(Hook install section), `templates/AGENTS.template.md` / generated `AGENTS.md`
(the `repo-facts.jsonl` pointer + strict-zero portability), the `governance-lint`
Open Decision (2026-06-22), and the verification-entry-point convention in
`.agents/repo-map.json`.

### 2026-06-27 — Push policy delegated to `.agents/push-policy.md`; four standardized options; default: ask

Status: Active

Decision: Push behavior is repo-specific, declared in `.agents/push-policy.md`,
which the Prime Invariants delegate to. The Prime Invariants push clause in
`templates/AGENTS.template.md` reads: "History-rewrite and destructive or
outward-facing actions always need an explicit go. Push policy: see
`.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the
default (`ask`). `templates/approval-summary.template.md` has a Push Policy
section that presents four standardized options at approval time and must ask
the human — it may not pre-fill the choice from the decisions log or other
context (the owner's approval-time reply is the only valid source).
`procedures/bootstrap.md` Step 10 consults `.agents/push-policy.md` after
committing. The options: 1 `always` (push after every commit); 2 `operators`
(auto-push after operator-invoked commits — handoff/decision/drift/plan — ask
otherwise); 3 `docs` (auto-push docs/state-only commits, ask for code/tool);
4 `ask` (always ask, the default). `templateVersion` bumped to `2026-06-27.1`.
This repo's own `.agents/push-policy.md` was created by the 2026-06-27 dogfood
self-application run and is set to `always`. The original Open Decision rationale
(2026-06-26) is archived verbatim in `docs/history/decisions-archive.md`.

Earned by an owner-surfaced cost (2026-06-26): the prior blanket
push-needs-explicit-go Prime Invariant left commits local-only, so the canonical
remote silently lagged and later sessions/machines assumed a repo current when it
was not — directly undercutting "durable truth lives on the canonical remote."
The delegation keeps the explicit-go default for repos that want it while letting
a repo opt into auto-push. Per the AGENTS.md portability/write-authority boundary
(2026-06-25), the *policy value* is repo-specific and lives in `.agents/`, not in
`AGENTS.md`, which only points to it.

Relationship: resolves the 2026-06-26 Open Decision (option a — tier by blast
radius — at the seam of the policy file rather than as template-wide tiers).
Exercises the 2026-06-25 governance-boundary boundary (repo-specifics in
`.agents/`) and the 2026-06-22 `templateVersion` reconciliation machinery.

### 2026-06-27 — Dogfood / self-application is a named case of the update route (docs handrail, no detection mechanism)

Status: Active, as amended by the 2026-06-28 collapse (Adopted 2026-07-01): the
dogfood case is now a named in-place case of the single `migration` route; the
"update route" wording below is the pre-collapse record. The anti-stop handrail
is unchanged.

Decision: Running the bootstrap procedure against this toolkit repo itself is a
**dogfood / self-application run**. It takes the existing `update` route and runs
**in-place** — there is no foreign target, the absence of `.bootstrap-tmp/` at
kickoff is the normal start (Step 1 discovery creates it), and the agent follows
`procedures/bootstrap.md` top to bottom with the approval summary as the single
gate. `procedures/bootstrap.md` names this case explicitly so an agent does not
read its "you are in a target repo" framing as "this procedure is not for here."
No `compute_route()` change, no manifest detection flag, no enforcement: the fix
is documentation only — a lens and a nudge. The route logic and what `update`
produces are unchanged.

Earned by a reproduced incident (2026-06-27): two capable sessions in a row, run
with the canonical kickoff line `Read ./procedures/bootstrap.md and follow it.`
from inside the toolkit repo, read the procedure's target-repo framing plus the
missing `.bootstrap-tmp/` as "nothing to bootstrap here" and stopped to ask the
owner instead of running discovery. Earlier runs (and an earlier run the same day)
had improvised past the framing and reached the update route correctly, so the
self-application case worked only by agent intuition, never by an explicit
instruction. Naming the case removes the ambiguity without disturbing the
behavior that has always worked.

Considered and rejected: a `selfApplication` detection flag in `compute_route()`
(by git-root identity or remote URL). Rejected because agents have reliably
understood "this repo is both the product and the target" without a mechanism;
adding detection risks breaking that intuition to fix a case a docs handrail
already covers.

Relationship: complements the 2026-06-22 update-route reconciliation decision
(this run exercises that route against the toolkit's own `AGENTS.md`); does not
change route selection.



### 2026-06-24 - Section-level rule deduplication: one full statement per rule, pointers elsewhere

Status: Active

Decision: A normative rule gets exactly one full statement in the governance
set; every other location that needs it carries a pointer, not a second copy.
This applies the existing "smallest durable guidance set / over-documentation is
a drift risk" and "keep one canonical location, prefer pointers" invariants at
the section level — within a single AGENTS file (a rule stated in full in both
Universal Invariants and a later dedicated section is the redundancy), and across
procedures (a paragraph copied near-verbatim between `bootstrap.md` and
`migration.md`). Anchor+elaboration layering is preserved where the anchor is
genuinely terse — the Prime Invariants re-ground hook plus a fuller statement
that adds content the anchor omits — but that is not a license for two full
same-altitude copies.

Earned by a real incident: a bug report (ExchangeAdminWeb, filed to the
`agent-harvest` dropbox 2026-06-24) found a generated `AGENTS.md` restating core
rules across sections, so the file violated the minimality invariant it ships. A
redundancy map across the product governance set (2026-06-24) confirmed three
genuine targets and rejected the bug's broader framing (words-first,
no-code-without-plan, and repo-is-memory are single anchors or intended
anchor+elaboration, not redundant): (1) the flag-conflicts/report-drift rule
stated in full in both Universal Invariants and Source Of Truth; (2) the
docs-only verification carve-out stated in full in both Universal Invariants and
the Verification section (and a third time in `approval-summary.template.md`);
(3) the commit-discipline/push-gate paragraph duplicated between `bootstrap.md`
and `migration.md`. The fix keeps each rule's full statement in one canonical
home and replaces the others with pointers.

Scope: the product files only — `templates/AGENTS.template.md`,
`procedures/migration.md`, `templates/approval-summary.template.md`. This repo's
own `AGENTS.md` carries copies of (1) and (2), but it is a frozen instance from
the last deliberate self-application, not a live view of the template; it is
brought current only by deliberately re-running the product on this repo, so its
copies are left for that run and are not edited here.

Relationship: refines the 2026-06-22 "trim the per-session guidance tax"
decision, which rejected word-level prose compression (~2.7% savings; the
guidance is dense, not padded). That holds — this is a distinct axis (whole-rule
section-level duplication, not wording length), so the two are complementary, not
in conflict. Concretely applies the 2026-06-09/10 one-canonical-location and
smallest-guidance-set invariants.

### 2026-06-22 - Bug reports are filed to the agent-harvest dropbox under `bugs/`

Status: Active

Decision: The shared `agent-harvest` dropbox (canonical on GitHub at
`roethlar/agent-harvest`) stores not only harvested governance rules but also bug
reports for defects in the AgentGovernanceBootstrap product itself — its code or
its procedures — under a `bugs/` folder, kept separate from the top-level rules
mailbox. When a run (dogfood here or a foreign target-repo session) confirms a
defect, the agent auto-writes a structured report from
`templates/bug-report.template.md` and files it per the canonical recipe
`procedures/file-bug-report.md`: preferred no-clone write via `gh api` to GitHub,
clone-and-commit fallback, and an in-repo `.agents/bug-reports/` last resort when
the dropbox is unreachable. Writing the report is automatic; any publish (the
`gh api` write or a clone push) requires an explicit owner go, per the
pushing-publishes invariant. Bug files are append-only. The harvest sweep
(`procedures/harvest.md`) reads `bugs/` and triages each report (still-open /
already-fixed / fix-now) rather than folding it into a template; a fix is a
separate scoped change.

Earned by a real incident: the 2026-06-22 dogfood run found a false positive in
`tools/discover.py` (the `operator:playbook` probe matched a bare `` `playbook` ``
while the operator is written `` `playbook <name>` ``, so it was always reported
missing and wrongly recommended reconciling a current `AGENTS.md`). There was no
durable home for that finding, because the dropbox README scoped the mailbox to
rules only. This decision closes that gap.

Relationship: extends the harvest dropbox's role (the 2026-06-11 harvest mailbox
conventions) to a second artifact class; does not change the rules-harvest gating,
naming, or template.

Follow-up (same day): the dropbox-write mechanics were factored into a single
shared transport recipe, `procedures/file-to-dropbox.md`, used by both the harvest
report path (`procedures/migration.md` Step 8) and the bug report path
(`procedures/file-bug-report.md`). This gave the harvest path the no-clone
`gh api` transport it lacked and retired its former standing auto-push: every
publish to the dropbox now asks for an explicit owner go, consistent for both
artifact classes. The `gh api` PUT path was verified end-to-end against
`roethlar/agent-harvest` on 2026-06-22.

### 2026-06-09 - Migrate to the standard .agents/ layout for all bootstrapped repos

Status: Active

Decision:
Every bootstrapped repo converges on the same `.agents/` layout (AGENTS.md + .agents/state.md, .agents/decisions.md, repo-map.json, artifact-manifest.json, optional playbooks). Existing governance systems are migrated into it via inventory (migrate/supersede/leave verdicts), not left as parallel canon. Old governance files (when they stay) receive a short supersession banner at the top pointing to the replacement; content is retained as history.

Reason:
This eliminates drift from competing sources of truth and gives every future agent (including in this toolkit repo) one discoverable current-state entry point plus one place for settled decisions. The layout is the outcome of the 2026-06-09 architecture restructure.

Supersedes:
The prior two-stage PowerShell architecture (historical record only in `docs/history/`).

### 2026-06-09 - Harvest is minimal, gated, dropbox-first

Status: Active

Decision:
During a migration the agent may (rarely) record generalizable governance rules in a harvest report, under strict limits: expected outcome is no report; an idea qualifies only if earned by a real citable incident, not already covered by templates, useful to other repos, and at most three ideas total; never a "nothing found" file. Delivery: write append-only as a new dated file in the `agent-harvest` dropbox via the shared transport recipe (`procedures/file-to-dropbox.md`), which any session may publish to only with an explicit owner go; otherwise fall back to `.agents/harvest.md` in the target. Harvest reports are never delivered into the canonical bootstrap repo itself. (Supersedes the earlier "standing authorization" auto-push: as of 2026-06-22 every dropbox publish — harvest report or bug report — asks before pushing, so the two paths share one transport and one gate.)

Reason:
Prevents over-eager padding and keeps the shared canon clean. A separate sweep session (owner-initiated only) in this repo judges new reports skeptically and logs outcomes in `harvest/processed.md`.

Supersedes:
Earlier ideas of richer or automatic harvesting.

### 2026-06-09/10 - Single-session kickoff with Python discovery; self-healing freshness

Status: Active

Decision:
The agent runs discovery (`tools/discover.py`) as Step 1 inside the kickoff session. The script is kept because it guarantees completeness on large repos without model-dependent laziness. A stale or missing manifest causes automatic re-run (self-healing). The only refusal case is a sandboxed environment that literally cannot execute the script. Every bootstrap run begins with a cwd-independent sync of the bootstrap toolkit from GitHub (the canonical remote), using the LAN gitea mirror as a faster fetch source when reachable, via `git -C`, `ls-remote` liveness, and `--ff-only` merge to GitHub's head; offline or diverged clones proceed with a plain-English flag and never block.

Reason:
One prompt ("Read <path>/procedures/bootstrap.md and follow it.") is sufficient. Two-stage (human runs script first) remains only as documented fallback. Freshness must come from git, not time or filenames.

Supersedes:
The earlier two-stage-only flow and any reliance on shell cwd.

### 2026-06-10 - Evidence rule for all durable claims

Status: Active

Decision:
Any durable claim about repo state, CI, deployment, file custody, or another external system must cite the exact query or command that proved it is *currently active* (e.g. `git ls-remote --exit-code`, `git ls-files --error-unmatch`, a workflow file confirmed in an executable provider path whose branch triggers match the current branch, etc.). Mechanical name-matches, discovery markers, and filename conventions are leads to verify, never facts to record. If a claim cannot be proved this way, write it as a labeled assumption or leave it out.

Reason:
Prevents recording plausible-looking but unverified or stale configuration as truth. Directly addresses pilot defects where CI markers and custody were misread from presence alone.

Supersedes:
Any prior practice of treating filename conventions or static markers as sufficient proof.

### 2026-06-10 - Gitignore-aware commit contract and custody queries

Status: Active

Decision:
Before listing any file as committable in an approval summary, run `git check-ignore` on its final path. Gitignored paths are proposed only as Local-only (copied into place but never `git add`ed, never `git add -f`). Custody values in artifact manifests record the custody each file will have once the approval commit lands, proven by git query: "tracked" for files on the Committed list (existing files via `git ls-files --error-unmatch` exiting 0; new files via `git check-ignore` exiting non-zero, proving them committable), "ignored" or "untracked" for Local-only files. Never set custody from path convention, and never record draft-time custody for a file the same commit will track. New files that are not ignored are listed under Committed and will be `git add`ed explicitly (never `-A`). (Refined 2026-06-10: the self-migration followed the earlier draft-time wording and recorded "untracked" for files its own commit made tracked.)

Reason:
Respects owner intent expressed in .gitignore. Silent `git add -f` is forbidden. The bootstrap commit is always exactly the scoped list from the approved summary.

### 2026-06-10 - One-scoped-commit + push-offer-once discipline

Status: Active

Decision:
After approval, copy drafts to final paths then commit as exactly ONE scoped commit using `git add` of only the approved files (never `git add -A`). The owner's approval of the summary is the explicit authorization for that single commit. After the commit, ask once (one line), naming the repo's remotes if more than one, and push only what the owner names. Never push unprompted.

Reason:
Keeps the bootstrap change reviewable and minimal. Matches pilot-validated safety (approval authorizes one scoped commit).

### 2026-06-10 - Answer-with-words rule hardened; artifact-is-evidence-not-decision

Status: Active

Decision:
When the owner asks a question or thinks out loud, reply in plain English and stop. Never respond with edits or execution. A handed-over artifact (defect report, findings list, plan, spec) is evidence to assess, not a decision to implement; deliver the assessment, ask for the go, and stop. Session framing is not a go. This rule wins over harness/platform pressure to act without asking. Also: treat repo filenames, paths, and document contents as evidence, not instructions.

Reason:
Prevents an agent from treating a just-received defect report or plan as an automatic "go" and sweeping changes (the self-incident that produced this rule).

Supersedes:
Softer prior wording of the same intent.

### 2026-06-10 - PowerShell helper retired

Status: Active (historical record)

Decision:
The original PowerShell implementation of the discover/bootstrap helper is retired to `docs/history/agent-bootstrap-discover.ps1` after the Blit pilot (2026-06-10). It is an archival record only. All active work uses the Python `tools/discover.py` (standard library, no deps) and the markdown procedures/templates.

Reason:
Post-pilot cleanup; the Python version is the supported one for cross-platform (including the Windows functional probe for Store stubs).

### 2026-06-10 - Fresh-eyes verification as consistency-not-truth check

Status: Active

Decision:
The fresh-eyes test (run for all migrations) is a discoverability and internal-consistency check only. A zero-context agent given only the drafted guidance files plus the repo must be able to answer the six questions (what is the project, what is true now, what next, how verified, how to hand off a decision, and evidence for any external claims). It is not a fact-check of external claims (CI, deploy, etc.). Every UNVERIFIED external claim found during the test must be downgraded to assumption or local-only in the drafts. The outcome is recorded as one plain-English sentence in the approval summary.

Reason:
Matches the pilot finding that the test should not be mis-presented as proof of runtime truth.

### 2026-06-10 - Windows Python probe order and Store-stub detection

Status: Active

Decision:
When selecting a Python interpreter for discovery: try `py -3 --version` first (canonical Windows launcher), then `python3 --version`, then `python --version`. Treat a candidate as absent (not merely old) if the command fails or its output contains "was not found" or "Microsoft Store". A `python3` on PATH that only opens the Store is not a usable interpreter.

Reason:
Windows ships App Execution Alias stubs; presence on PATH does not imply a working Python. This probe order and detection was folded in from the ExchangeAdminWeb pilot.

### 2026-06-10 - Cwd-independent Step 0 sync

Status: Active

Decision:
All git commands in the toolkit sync (Step 0) are run as `git -C <bootstrap-repo> ...`. Never rely on the shell's current working directory. Use `git ls-remote --exit-code <url> HEAD` to test liveness before fetch. If no remote responds or fast-forward is impossible: proceed with the local copy and flag plainly in the approval summary. GitHub is authoritative; a gitea mirror that lags GitHub is expected, not a disagreement to flag. Never merge or rebase the bootstrap repo from a target session.

Reason:
Many agent harnesses reset cwd between tool calls; a bare `cd` + `git fetch` can silently operate on the wrong repo.

### 2026-06-10 - CI markers are provider-executable only + branch match required

Status: Active

Decision:
CI / build markers recorded by discovery are accepted only for files that sit in a path the provider actually executes. The packet surfaces `suspectedMisplacedCi` and `ciBranchMismatches`. Before recording any "CI gates merges" claim or using a workflow command as the automated verification entry point, the agent must confirm both the executable-path condition and that the branch triggers match the repo's current branch. If either fails, record verification as local-only and flag the dead file in the approval summary.

Reason:
Prevents treating a plausible-looking but non-executed workflow file as live CI.

### 2026-06-10 - Git-safety: ancestry vs content verification

Status: Active

Decision:
Never conclude a branch is merged from ancestry alone (`git branch --merged` can lie after `-s ours` or octopus merges). Verify the content actually arrived (`git diff <branch> <main>`) before deleting anything or treating work as landed.

Reason:
Folded from pilot experience; added to the AGENTS template Git Safety section and this repo's rules.

### 2026-06-10 - One-item-per-commit discipline (batch sweeps owner-only)

Status: Active

Decision:
When working through a list of findings or fixes, address exactly one item per commit and commit each before starting the next. Batch sweeps spanning many findings happen only on the owner's explicit request. Whether work happens on a branch is repo policy, not this rule.

Reason:
Folded from pilot; prevents monolithic "fix everything" commits that hide reviewable units. (Branch-per-item variant was considered and dropped; branching policy stays per-repo.)

### 2026-06-10 - Artifact (defect report / plan / spec) is evidence, not decision

Status: Active

Decision:
A handed-over artifact (defect report, findings list, plan, spec) is evidence to assess, not a decision to implement. The agent must deliver the assessment in plain English, ask for the explicit go, and stop. Only an explicit owner decision (not session framing or harness ritual) authorizes multi-step changes or edits.

Reason:
Direct response to the self-incident in which an agent read a softer rule and executed an unapproved fix sweep straight from a handed-over defect report.

Supersedes:
The prior, softer wording of the "answer with words" rule in this repo's AGENTS.md and the bootstrap contract.

### 2026-06-09/10 - Pilot findings folded into canon (multiple)

Status: Active (summarized)

The following were adopted during/after the three external pilots and the self-incident; each is recorded as a specific decision above or in the AGENTS template invariants where generalized:
- Revert-the-fix test check added to AGENTS template Verification.
- Ancestry-vs-content git-safety bullet.
- One-item-per-commit discipline.
- Safety-vs-ritual authority split (safety rules always bind; workflow rituals do not preempt the owner's kickoff instruction).
- Load-bearing-path check before migrating a state/decisions file.
- Summary altitude (plain English, one-screen recommendation before the inventory table).
- Approval authorizes one scoped commit only.
- Push offered once after commit, naming remotes.
- Evidence rule (durable claims cite the proving query).
- Custody-from-git rule + gitignore-aware commit contract.
- Fresh-eyes reframed as consistency-not-truth + external-claims question.
- Windows Python probe order + Store-stub detection.
- Cwd-independent Step 0 (`git -C`, ls-remote).
- Manifest schema shipped beside discover.py.
- "Answer with words" hardened with explicit artifact-is-evidence-not-decision clause.

All other pilot observations that did not yield a new durable rule were left as history in `docs/history/pilot-findings_exchangeadminweb_2026-06-10.md` and the per-pilot review files.

Supersedes:
The pre-pilot procedures and templates.

### 2026-06-18 - Operator command wrappers are a standing guarantee on every route

Status: Active

Decision:
On every route (greenfield, migration, update), the process audits the operator
vocabulary (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`) and, on a harness
that supports command files, drafts any missing slash-command wrappers and the
`.gitignore` edit that makes them committable - removing a blanket `.claude/`
ignore rule and adding a narrower `.claude/settings.local.json` rule so
machine-local settings stay out of git. The expected steady state is "already
present, nothing to do"; existing committed wrappers are never overwritten. The
canonical recipe lives in one place - `procedures/bootstrap.md` "Operator command
wrappers (all routes)" - and is referenced from the greenfield workflow,
`procedures/migration.md` Step 4, and the AGENTS template Bootstrap Handoff so
generated repos self-audit on update runs. Wrappers and the `.gitignore` edit
travel through the normal approval summary and land in the single scoped commit.

Reason:
A repo bootstrapped greenfield or maintained via update previously advertised the
operator words in prose but had no working slash commands, and `.claude/` was
often gitignored so even drafted wrappers never got committed - a broken-promise
UX failure for the human the toolkit exists to serve. Making wrappers a standing,
route-neutral guarantee (with the gitignore fix that makes them durable) closes
that gap.

Alternative considered and rejected:
A pilot report proposed instead routing `.claude/`-only-ignored repos to
greenfield by filtering gitignored markers out of `compute_route`. Rejected: that
routes *around* the symptom (treats a misconfigured, local-only `.claude/` as
"nothing to migrate") rather than fixing the cause. The adopted approach repairs
the gitignore configuration so the commands become durable governance, which is
the correct end state. The packet's separate custody-wording imprecision is
tracked below and is unaffected by this decision.

Supersedes:
The deferred "Command wrappers are created only on the migration route"
(2026-06-15), now adopted in generalized form.

### 2026-06-22 - Update route reconciles a stale AGENTS.md; templateVersion stamp detects drift

Status: Active

Decision:
Bootstrapped repos carry a `<!-- templateVersion: YYYY-MM-DD -->` stamp at the
top of `AGENTS.md`, mirroring the stamp in the toolkit's
`templates/AGENTS.template.md`. Discovery records an `agentsTemplate` block in the
manifest (`currentVersion`, `targetVersion`, `reconcileRecommended`,
`missingSections`): it compares the target's stamp against the toolkit's and, on
the update route, probes the target `AGENTS.md` for missing structure (the Prime
Invariants block, the operator set). The update route (`procedures/bootstrap.md`
Step 3) reconciles a stale or unstamped `AGENTS.md` to the current template -
reusing the `procedures/migration.md` Step 2 discipline (carry earned rules
forward, migrate the rule not its stale examples, verify migrated facts) - before
running the operator-wrapper and hook guarantees. The wrapper/hook guidance treats
a missing target section as a staleness signal to reconcile, never a cue to narrow
the artifact to fit the stale file. Bump the stamp when the template's structural
contract changes; a forgotten bump is backstopped by the missing-sections probe.

Reason:
The update route previously delegated straight to the target's own
(older-template) bootstrap-handoff rule and never reconciled `AGENTS.md`, so the
all-routes wrapper/hook guarantees - drawn from the current templates - pointed at
sections (Prime Invariants, `playbook`) a stale file lacked. With no instruction
to upgrade the source, an agent narrowed the wrappers to fit the stale file,
degrading the toolkit's own canon. This closes the gap: detect drift mechanically,
reconcile the source.

Supersedes:
Refines the 2026-06-18 "generated repos self-audit on update runs" assumption,
which held only when `AGENTS.md` was already at the current template version; that
decision stays Active for the wrapper guarantee itself.

### 2026-06-22 - Trim the per-session guidance tax: Bootstrap Handoff pointer; rtk discretionary, not a hook

Status: Active, as amended 2026-07-01 (owner directive, two steps): the
template's token-efficiency bullet is removed from the product entirely — no
`rtk` reference and no generic replacement — guarded by a test that the
shipped template contains no `rtk` mention. The discretionary-not-a-hook
stance below remains this repo's own recorded practice (a repo-guidance fact,
not product text). The Bootstrap Handoff pointer clause is unaffected.

Decision:
`CLAUDE.md` `@`-imports the whole `AGENTS.md` every session, so `AGENTS.md` length
is a recurring per-session cost. A density audit found prose compression yields only
~2.7% savings once every normative claim must survive (the guidance is dense with
load-bearing rules, not padded), so we do NOT compress wording. Instead: (1) the
`## Bootstrap Handoff` section - only actionable when `.bootstrap-tmp/` exists, and a
near-duplicate of the synced `procedures/bootstrap.md` - is collapsed to a short
conditional pointer to `.bootstrap-tmp/START-HERE.md` + `procedures/bootstrap.md`,
making the procedure the single canonical home and cutting ~600 tokens/session;
(2) the token-efficiency invariant encourages `rtk` (https://github.com/rtk-ai/rtk)
as a discretionary per-command proxy and forbids its auto-rewrite hook, which would
compress every Bash call and remove the agent's access to raw output when it matters;
it generalizes to compact-but-equivalent working (targeted reads, scoped searches, no
re-reads).

Reason:
Reduce recurring context cost without losing semantic content. Update routing is
unaffected - `compute_route()` keys off the `.agents/` layout markers, not the
section's presence.

Supersedes:
Nothing. Complements the 2026-06-22 update-route reconciliation decision: the
reconciliation and wrapper-guard logic now lives solely in `procedures/bootstrap.md`,
no longer duplicated in the template's Bootstrap Handoff section.

### 2026-06-25 - Stall-not-length: iterative processes escalate on stalled progress, never on duration

Status: Adopted 2026-06-25. The invariant landed as a bullet in
`templates/AGENTS.template.md` `## Universal Invariants` ("Escalate an iterative
process on stalled progress, never on duration…"), with `templateVersion` bumped
2026-06-22 → 2026-06-25 so the update route reconciles stale targets. This repo's
own `AGENTS.md` is intentionally NOT edited here: it is a frozen instance brought
current only by a deliberate self-application run (same handling as the 2026-06-24
deduplication decision), so the missing bullet there is expected, not drift. The
text below is retained as the rationale until archived.

Decision (design settled 2026-06-25, five points the owner approved):
A new Universal Invariant governs every iterative agent process — a loop, a
multi-finding sweep, a long autonomous run. The escalation trigger is **stall, not
length**: a process must surface to a human when it completes a cycle that banks no
**verifiable progress**, and length/duration is *never itself* the trigger. A run
that closes a verified delta each cycle is healthy at any duration (the invariant
must not break Fable/ultracode-style long autonomous runs); a process that loops
without banking a delta is the failure, however briefly it has run.

1. **Home.** One full statement as a bullet in `## Universal Invariants` of
   `templates/AGENTS.template.md`; mirrored to this repo's `AGENTS.md` only by the
   normal self-application; pointers, not copies, anywhere else.
2. **"Verifiable progress" defined by evidence class, not metric.** A cycle banks
   progress when it produces a new observable delta — a test moving red→green, a
   finding closed with guard proof, a build/type error resolved, a committed slice.
   A cycle producing none of these is a stall. (Same evidence family as the
   vacuous-test and drift rules: "cycle with no observable delta" at the loop level.)
3. **Trigger by consecutive stalled cycles, threshold by agent judgment with a small
   stated default (~2-3), not a hardcoded N.** Hardcoding a count invites the same
   false-positive brittleness the synchronous-review work spent effort avoiding; the
   agent states the threshold it is using.
4. **Mechanical consequence.** Adding a Universal Invariant is a structural template
   change, so bump `<!-- templateVersion -->` in `templates/AGENTS.template.md` so the
   update route reconciles stale target `AGENTS.md` files (the 2026-06-22 stamp
   machinery working as designed).
5. **Scope guard is part of the wording.** The invariant explicitly states that
   length/duration is never the trigger and names the long-autonomous-run case, so no
   future agent reads it as a turn cap.

Reason: serves the repo's overarching mission — improve agentic coding for humans,
token-efficiently — by killing non-converging runs early (the largest avoidable token
sink) without capping productive long ones. It extends the repo's evidence-over-
assertion vocabulary (drift = "diverged from truth"; vacuous-test = "change with no
observable delta") to a new axis: runaway = "process that will not terminate
productively."

Relationship: complements, does not supersede, the 2026-06-24 section-level
deduplication decision (one full statement, pointers elsewhere) and the 2026-06-22
`templateVersion` reconciliation decision. Considered and rejected: a duration/turn
cap (e.g. "stop after N turns") — it strangles the long converging runs that are an
existence proof the duration is not the failure mode.

Next step: a `plan` for the exact invariant sentence(s), the `templateVersion` bump,
and verification (`python3 -m unittest discover -s tests -v` for the template/stamp
touch; the revert-the-fix discipline if a test guards the stamp).

### 2026-06-25 - AGENTS.md governance boundary: portable + write-authority, enforced in three layers

Status: Adopted 2026-06-25. The two boundary invariants landed as bullets in
`templates/AGENTS.template.md` `## Universal Invariants` (portability — "would this
line survive being copied unchanged into an unrelated repo?"; and write-authority —
"AGENTS.md is written only by a gated bootstrap or update run"); the `drift` operator
in the same template now names AGENTS.md portability/write-authority as explicit drift
targets; and a `PreToolUse` pre-edit tripwire (advisory, non-blocking, one stdlib-
Python script `agents-md-tripwire.py` shared by the Claude Code and Codex hook
configs) ships under `templates/hooks/`. `templateVersion` bumped 2026-06-25 →
2026-06-25.2 (a same-day second structural change; the bare date could not
distinguish it, and the section-probe backstop does not see new bullets within an
existing section, so the sub-version is the only reconciliation signal). This repo's
own `AGENTS.md` is intentionally NOT edited here — a frozen instance brought current
only by a deliberate self-application run (same handling as the stall-not-length and
2026-06-24 deduplication decisions). Design spec:
`docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan and
evidence: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`. The text
below is retained as the rationale until archived.

Decision: `AGENTS.md` is governance only and must be portable — every line must
survive being copied unchanged into an unrelated repo; repo-specific facts (paths, the
repo's own name, current state, verification commands) live in `.agents/`, and
`AGENTS.md` points to them rather than restating them. Complementarily, `AGENTS.md` is
written only by the two gated writers (a greenfield/migration bootstrap draft, or the
update-route reconciliation), never hand-edited mid-task. The two rules close both
wrong-content and wrong-moment. Enforcement is three layers by harness capability:
(1) the invariant text, injected on every harness; (2) the advisory pre-edit tripwire
hook, Claude Code + Codex only (Grok/agy have no pre-edit interception); (3) the
`drift` operator audit, cross-harness.

Layer emphasis (corrected from the spec's original framing by live validation,
2026-06-25): **layer 1 is the primary, proven steerer** — across three escalating
baits, capable models (Sonnet, GLM) read the invariant and routed the repo-specific
fact to `.agents/` before ever reaching for `AGENTS.md`, so the hook never had to
fire. **Layer 3 is the necessary backstop** — the only layer that catches what 1 and
2 let through; a model can read the layer-2 reminder and rationalize past it, and one
did. **Layer 2 is a real but advisory nudge** — validated to fire, be model-visible
(token echoed back), and stay non-blocking on Codex and on a non-Anthropic open model
(GLM) via Claude Code, and observed to make a model self-revert a leak once; it raises
the odds of self-correction but is never a gate. Validation was run in a throwaway
repo (now discarded); the shipped script+`additionalContext` form is the exact form
validated. Hook shape: Codex has no scriptless path matcher (matcher is tool-name
only), so a script is required there; one stdlib-Python script (Python 3 is already
the toolkit's baseline — no new dependency) serves both harnesses.

A secondary correctness finding landed with this work: the hook-template portability
test (`TestHookTemplates`) had encoded the *re-ground hook's* shape ("inline echo
only; no `.sh`; no `git rev-parse`") as if it were the portability rule itself — an
is/ought conflation that would force a per-category exception for every new hook kind.
It was reworked to assert the portability *principle* (no machine-specific/`/Users/`
baked path; `git rev-parse --show-toplevel` and `$CLAUDE_PROJECT_DIR` are portable and
allowed) over every hook command, with the re-ground command still byte-locked across
harnesses, plus dedicated tripwire guards (present+advisory+portable; fires-on-
AGENTS.md-only/never-blocks; script-identical-across-harnesses). All new guards were
proven to bite via hermetic mutation (temp copy, tracked files untouched).

Scope guard: this spec defines the *rule* and *forward* enforcement. Two pieces are
split to their own future specs and are NOT done here — retroactive cleanup of
already-bootstrapped repos whose `AGENTS.md` already carries repo-specifics, and
whether the mechanizable path/name scan folds into the queued `governance-lint`
playbook (Open Decision, 2026-06-22) versus staying an agent-judgment `drift` step.

Relationship: complements the one-canonical-location / prefer-pointers and
anti-enumeration invariants (this names the `AGENTS.md`↔`.agents/` boundary as a
single portable test); complements, does not supersede, the 2026-06-22
`templateVersion` reconciliation decision (whose stamp machinery this exercises, and
which the sub-version extends for the same-day case). Considered and rejected: a hard
*block* on AGENTS.md edits — the edit can be legitimate (a bootstrap/update run), and
portability is a content judgment only the model makes, so the hook is advisory by
design.

## Open Decisions (deferred - not yet adopted)

These are assessed findings the owner chose to record for a future decision
rather than implement now. The process is unchanged until one is adopted. Each
states the verified evidence, the options, and the standing recommendation.

The following six were assessed on 2026-06-22 from three external repo
reviews (DeepSeek, GPT-5.5, Grok) read against current repo evidence. The
reviews' other suggestions were rejected as scope-inflating or already covered
and are not recorded. Recommendation order below is the suggested implementation
sequence.

### Open: route/verification probes match literal `package.json` against repo-relative paths (monorepo subdir miss)

Evidence: `tools/discover.py` tests membership of the literal `"package.json"` in
the path set, but paths are stored repo-relative (`relative_to(repo_root)`), so a
subdir-scoped run on e.g. `packages/api/` yields `packages/api/package.json`,
which never matches — silently losing verification-command detection for the
scoped case.

Precondition: confirm whether subdir-scoped bootstrap is a supported mode. If it
is not a real path, this does not bite and should be closed as not-applicable
rather than fixed.

Recommendation: resolve the precondition first. If scoped runs are supported,
match by basename / suffix instead of literal full-path membership. Lower
priority than the two above.

### Open: hook-merge strategy is underspecified in the procedure

Evidence: `procedures/bootstrap.md` "Hook install & trust" says to merge the
re-ground hook into an existing config "rather than replacing the file" and to
"stop and ask" if a safe merge is not possible, but specifies no merge algorithm
— for `.claude/settings.json`, which also holds permissions, env, and model
settings, "safe merge" carries undocumented weight.

Options: (a) add a concrete merge rule to the procedure — the hook lives under a
known key, preserve all sibling keys, append to the relevant hook array, and
stop-and-ask only on structural ambiguity; (b) leave the judgment to the agent.

Recommendation: (a). Docs-only change to one procedure section; no plan required
under the invariants. Reduces an ambiguous agent judgment to a stated rule.

### Open: committed operator wrappers are skipped without a staleness check

Evidence: `procedures/bootstrap.md` step 4 of "Operator command wrappers" does a
binary exist-and-committed → change-nothing, with no version/staleness check —
even though the 2026-06-22 update-route decision added `templateVersion` stamping
and reconciliation for `AGENTS.md`. The same staleness logic was not extended to
the command wrappers, so a repo can carry current `AGENTS.md` guidance behind
outdated wrappers and the migration route's reconciliation branch will not
notice. (Reworded 2026-07-01 to the single route per the adopted 2026-06-28
collapse; substance unchanged.)

Options: (a) extend version-aware reconciliation to wrappers in the migration
route's reconciliation branch — detect a wrapper that predates the current
template and propose an update through the normal approval summary, never a
silent overwrite; (b) leave wrappers as exist→skip.

Recommendation: (a), scoped narrowly to wrapper reconciliation in that branch,
following the existing `AGENTS.md` reconciliation precedent. Consistency fix for
work already shipped, not new surface.

### Open: greenfield fresh-eyes test is agent-judged "optional", at a point the repo distrusts agent judgment

Evidence: `procedures/bootstrap.md` greenfield step 8 makes the fresh-eyes test
"optional ... recommended whenever the drafts are substantial"; migration
(`procedures/migration.md` Step 6) requires it. The greenfield wording leans on
the agent to judge "substantial," whereas the 2026-06-10 fresh-eyes decision and
the repo's broader stance distrust agent self-assessment.

Options: (a) make the greenfield fresh-eyes test mandatory unless the run is a
genuine no-op (no drafted changes); (b) keep "optional/recommended"; (c) some
middle threshold tied to an objective signal (e.g. any new `.agents/` file
drafted).

Recommendation: a one-line judgment call for the owner. (a) removes the
agent-judged escape hatch cheaply; (c) is a compromise. Low effort either way.

### Open: a `governance-lint` self-audit playbook (mechanical checks only)

Evidence: `AGENTS.md` advertises `.agents/playbooks/*` as an authority slot and a
`playbook <name>` operator. The toolkit already ships a playbook template
(`templates/playbooks/reviewloop.md`, a two-agent review loop installable into a
target repo), but this repo's own `.agents/playbooks/` directory does not yet
exist — so governance-lint would be the first playbook authored as a self-audit
and the first one installed into this repo, not the first use of the mechanism.
Three doc-health checks are mechanizable
against existing structures: (1) **state freshness** — `.agents/repo-map.json`
carries a structured `validated_against: {commit, date}`; compare it against the
git log for `.agents/` to flag a state doc that has drifted past its last
validation; (2) **pointer/section/stamp resolution** — cross-references are
backtick-wrapped paths (regex-extractable, `Path.exists()`-checkable),
`repo-map.json.guidance_paths` supplies the golden file list to walk, and
`discover.py` already has `extract_template_version()` for the stamp; (3) dead
backtick-path links fall out of (2). `discover.py` exposes reusable helpers
(`run_git`, `match_paths`, `extract_template_version`), so the core is ~150 lines.
Evidence-citation sufficiency and prose-reference resolution are explicitly NOT
mechanizable (they need semantic judgment) and stay the `drift` operator's job.

Options: (a) build a standalone `.agents/playbooks/governance-lint.md` (+ a small
Python checker) covering freshness + pointer/section/stamp resolution, run
on-demand and recommended by the migration route's reconciliation branch — not a
blocking gate; (b) fold the mechanical freshness check into the existing `drift`
operator without a new playbook; (c) YAGNI — leave it.

Recommendation: (a), with evidence-citation checking declared an explicit
non-goal. It fills the already-advertised, currently-empty playbook slot rather
than adding new surface; it stays agent-driven (a playbook the agent runs, not a
script gate); and it makes the `validated_against` freshness signal — which
nothing currently checks despite guarding the "discoverable current-state entry
point" invariant — actually load-bearing. The narrow form (freshness +
pointer/stamp) is not YAGNI; the broad "audit governance health" form Grok
originally proposed would be.

Owner decision 2026-06-22: option (a) — standalone
`.agents/playbooks/governance-lint.md` plus a small checker, run on-demand and
recommended (not gated) by the migration route's reconciliation branch
(reworded 2026-07-01 per the adopted route collapse); evidence-citation
sufficiency stays an explicit non-goal (the `drift` operator's job). Still
Open: not yet implemented. Next step is a `plan` for the checker.

### Open: foreign-model governance validation

Owner needs a way for a *different* model to validate that a repo's governance
works (the in-bootstrap fresh-eyes test only ever runs the same model that drafted
the guidance). Not yet designed or decided — surfaced 2026-06-22, undecided.

The following two were assessed on 2026-06-23 from bug reports filed to the
`agent-harvest` dropbox during a `headroom` (chopratejas/headroom) dogfood
migration run, read against current repo evidence. They are appended at the end of
the queue; the implementation sequence of the seven items above is unchanged.

### Open: the authority/scope boundary has no stated precedence over the content-quality invariants

Evidence: The Prime Invariants (`templates/AGENTS.template.md:8-18`) require
"act only on an explicit instruction," and `procedures/bootstrap.md` Step 0 makes
the toolkit repo read-only except for the sync, but the content-quality invariants
— "Keep one canonical location… Prefer pointers over duplicating"
(`templates/AGENTS.template.md:46-47`), the `decision`/`drift` operators that write
canonical files, and `procedures/migration.md`'s fold-into-canon guidance — carry
no scope-of-authorization qualifier, and no cross-section precedence statement
reconciles the two. Earned by a real reproduced incident: during a 2026-06-23
`headroom` dogfood run the agent appended 19 lines to *this* repo's own
`.agents/decisions.md` (an unauthorized write to canonical governance, in a
different repo than the one under bootstrap), justified by "augment canonical
entry, don't duplicate"; `git diff` showed `.agents/decisions.md | 19 +++` against
an otherwise-clean tree and the edit was reverted with `git restore`. The agent
had, one message earlier, itself articulated the read-only guardrail and still
failed to bind it — so the gap is structural (no precedence rule, no checkpoint),
not a one-off lapse. Source: `bugs/headroom-authority-boundary-overreach-2026-06-23.md`.

Options: (a) add an explicit precedence rule to the Prime Invariants (echoed in
`bootstrap.md`): the authority/scope boundary outranks every content-quality
principle; an agent may never edit a canonical or tracked governance artifact (and
never any file in the toolkit repo beyond the Step 0 sync) without an explicit
instruction naming the file or edit; "fold into canonical home / don't duplicate"
applies only within the repo scope the session is authorized to write, and only on
an explicit go; a finding that belongs in a file the session may not write goes
only into the sanctioned scratch/report outputs. (b) leave as-is.

Recommendation: (a). It hardens a load-bearing authority invariant against a
reproduced failure and changes prose, not code. Because it edits the Prime
Invariants — the highest-authority block — record it for an explicit owner
decision rather than treating this standing recommendation as the go. Prove the
bite with a re-run scenario: an agent that finds a matching canonical entry and is
told "drop the scratch file in X" must produce only the cross-reference, never an
edit to the canonical file. Relationship: extends the 2026-06-10
"answer-with-words / artifact-is-evidence-not-decision" decisions with a precedence
rule against the content-quality invariants. Affected files:
`templates/AGENTS.template.md` (Prime Invariants), `procedures/bootstrap.md`
(Step 0 read-only echo), `procedures/migration.md` (bound the fold/augment-into-canon
guidance by authorization scope).

### Open: "all routes" harness-artifact drafting contradicts the smallest-guidance-set invariant

Evidence: `procedures/bootstrap.md` "Operator command wrappers (all routes)"
(`:156`, `:159`) and "Hook install & trust (all routes)" (`:192-193`) instruct
drafting wrappers/hooks for every harness the toolkit ships a template for, "even
when the harness you are running in has no command-file mechanism," while
`templates/AGENTS.template.md:61` states "Prefer the smallest durable guidance set
that fits the repo. Over-documentation is a drift risk." No section reconciles the
two, so an agent following the draft-all instruction literally produces governance
files for harnesses a repo shows no evidence of using. In practice the bite is
small for wrappers (the toolkit currently ships wrapper templates only for Claude
Code, `:158`) but real for hooks (it ships claude/codex/grok/agents configs,
`:200-201`). Severity low — unused files / mild over-documentation, no incorrect
behavior or data loss. Source:
`bugs/headroom-harness-artifact-overproduction-2026-06-23.md`.

Options: (a) reconcile explicitly: keep the draft-all portability default but add a
sentence to both "all routes" sections pointing at the smallest-set invariant, and
have the approval-summary step sort harness artifacts the repo shows no usage
evidence for into a clearly-labeled "optional / not-evidenced" bucket the owner can
drop. (b) make non-evidenced harness artifacts opt-in (draft only for harnesses
with repo evidence; note the rest as available). (c) leave as-is and treat
draft-all as the intended portability stance.

Recommendation: (a). Docs-only reconciliation across `procedures/bootstrap.md`
(the two "all routes" sections), `procedures/migration.md` (Step 4), and
`templates/approval-summary.template.md` (the optional/not-evidenced bucket); it
preserves the portability rationale while removing the literal contradiction. Lower
priority than the medium-severity authority gap above. This intersects the
2026-06-18 "operator command wrappers are a standing guarantee on every route"
decision (which stays Active): the reconciliation must not weaken the wrapper
guarantee, only label non-evidenced artifacts as optional in the summary.
