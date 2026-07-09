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

### 2026-07-08 — Zero-based consolidation: every product piece justifies its existence or leaves

Status: Active (implemented same day; plan with eight-round codex review
trail: `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`;
owner approval 2026-07-08).

The owner commissioned a zero-based review — every piece justifies itself on
the incident ledger and a five-repo field audit (Blit_v2, vela,
Powershell-Token-Killer, ai-rpg-engine, ExchangeAdminWeb; evidence anchors in
the plan) or is removed/replaced. The field audits established that the core
loop works (handoffs demonstrably resumed across sessions and machines,
decisions and pauses honored, reviewloop caught real pre-ship bugs) and that
the recurring failures cluster where no operator or write rule existed.

What changed, and what each change supersedes or amends:

- **Steady-state refresh is `tools/refresh.py`** — pull-based, per-repo, no
  registry: reconcile-to-shipped-set (`tools/shipped-set.json`) with
  newline-normalized matching, `replace-whole` for `AGENTS.md` gated on a
  known-template match, `replace-if-unmodified` for shims/wrappers/playbooks/
  hook settings (missing ⇒ install; matches a formerly-shipped version ⇒
  update; else flag, never overwrite), a `retired` list so toolkit-side
  removal actually propagates (empty formerly-hashes = always flag, never
  machine-delete — protects generated files), gitignore-aware committability
  with the blanket adapter-dir repair, dirty-tree refusal scoped to its own
  targets, `--stage-only` for the bootstrap single-commit contract, and the
  toolkit sha in the commit message as provenance. Rationale on record: sync-
  to-exact-set is the documented agent failure mode (the 2026-07-01 dogfood
  "content already current" miss; wrappers narrowed to fit stale files;
  deletions resurrecting). This supersedes the mechanical half of the
  agent-run refresh flow, the 2026-06-22 templateVersion-stamp decision (the
  stamp is removed; byte-compare + commit-message provenance replace it), and
  strengthens the 2026-06-18 never-overwrite rule (`replace-if-unmodified`:
  byte-match against formerly-shipped versions proves non-modification, so
  provably-unmodified stale artifacts now update instead of rotting). The
  2026-07-03 playbooks decision is **preserved in full** (unconditional
  install; target-repo deletion still reinstalls; opt-out = remove the
  template from the toolkit — which now actually propagates).
- **Discovery is a live checklist, not a script** — `tools/discover.py` and
  its manifest/schema/golden machinery deleted (three of the seven ledger
  bugs were its own defects; a frontier agent re-derives its outputs).
  Salvaged knowledge lives in `procedures/bootstrap.md`: the Windows
  Store-stub probe order, ignore-aware governance detection, the
  CI-executability rule. Supersedes the script half of the 2026-06-09/10
  kickoff decision; the single-session kickoff, Step 0 sync, and evidence
  rule stand. The `.bootstrap-tmp` handoff pack dies with its generator; the
  self-ignored `drafts/` custody convention survives in the procedure.
- **The JSON layer is retired** — `repo-map.json` / `artifact-manifest.json`
  templates deleted; both on the retired list (flag-only). Field evidence:
  frozen and wrong in every audited repo while the prose files stayed
  accurate; custody is proven live by git at the approval gate. The
  verification command's single canonical home is
  `.agents/repo-guidance.md` (Verification). Amends the 2026-06-09
  standard-layout decision (layout no longer includes the JSON files).
- **Hooks narrowed to the Claude compaction re-ground behind a per-harness
  verify-once gate** — the sole shipped hook; the AGENTS.md pre-edit
  tripwire is retired everywhere (advisory; per-edit process spawn; silently
  inert on stock Windows for weeks with no degradation — the strongest
  not-load-bearing evidence on record; the write boundary is now refresh's
  byte-verify-and-repair), as are the never-verified grok/agy configs and
  the codex config (session_start registered but never observed firing —
  2026-07-08 live check negative). Ledger + structural rationale (a
  compaction failure can only be mitigated from outside the context):
  `docs/harness-capabilities.md`, the durable per-harness capability record.
  Amends the 2026-06-21 per-harness re-ground decision (per-harness retained,
  now evidence-gated); supersedes L2 of the 2026-06-25 boundary decision (L1
  prose stays, L3 is refresh repair); moots the 2026-07-02 hook-interpreter
  decision (the survivor is a plain echo). Codex/gemini/grok adapters and
  non-Claude wrappers re-enter only on a recorded positive live check.
- **Feedback is GitHub issues on this repo** (public; hard no-PII/secrets
  redaction rule in the issue templates; agents file only on an explicit
  owner go; offline fallback = in-repo note). Supersedes the transport half
  of the 2026-06-09 harvest decision and the 2026-06-22 dropbox/bug-report
  decisions; the harvest discipline (incident-earned, max three,
  no-report-is-normal) is retained verbatim in
  `.github/ISSUE_TEMPLATE/`. `harvest/processed.md` archived; open/closed
  issues are the queue and ledger. The `agent-harvest` repo awaits owner
  archiving.
- **The evals workstream is scrapped** — `evals/` and the instrument deleted
  (owner: delete, not archive; git history preserves). Amends the 2026-07-01
  functional-cut decision's completeness-general-as-candidate clause (the
  profile is deleted; revival needs a fresh decision). Salvage:
  `docs/harness-capabilities.md`.
- **Template redline** — `templates/AGENTS.template.md` cut to 1,503 words
  (Bootstrap Handoff, Mission-as-section, stamp, pointer bullet, merged
  durable-writing bullets); write-authority one sentence; `handoff` gains
  the field-earned rules (verbatim rotation to
  `docs/history/state-archive.md`; volatile facts `as of <commit>`; counts
  pointed-to; machine-local facts labeled or omitted; parked items
  re-verified); Session Startup gains the read-only clone-freshness check
  (never blocks). Scope tiers deleted from the approval summary (conditioned
  nothing anywhere).
- **Standing rule: no shipped rule without provenance** — a template rule is
  added, kept, or changed only with a decisions entry citing its earning
  incident; every kept line was cross-checked this run (zero lines lacked
  provenance). With the discover-era presence tests retired, this process
  rule — not CI grep — is what guards template content.

Procedures consolidated to one `procedures/bootstrap.md` (1,913 words, from
5,198 over two files; `verification.md` unchanged; the three dropbox
transport procedures deleted). Rollout: vela first (owner pick), remaining
repos on owner go; refresh flags route back as issues.

### 2026-07-04 — Specific-over-generic precedence: explicit boundaries and no-discretion rules outrank generic defaults

Status: Adopted 2026-07-04 (rule lives in `templates/AGENTS.template.md`
`## Universal Invariants`, stamp `2026-07-04.1`; presence-guarded by
`test_universal_invariants_rank_specific_over_generic` in
`tests/test_discover.py`).

Decision: an explicit authority or scope boundary, or a rule or decision whose
wording removes discretion for the case it names ("unconditional", "no per-run
choice", "deterministic"), outranks every generic default for that case —
flag-conflicts, one-canonical-location, smallest-guidance-set included. Agents
apply it as written and do not reopen the settled case as a conflict or
approval question against surrounding repo state such as git history; generic
defaults govern only questions no more specific rule has already resolved.

Earned by the second reproduction of the same missing-precedence defect shape:

- 2026-06-23 (`bugs/headroom-authority-boundary-overreach-2026-06-23.md` in
  the `agent-harvest` dropbox): the "fold into canonical home" content-quality
  instinct overrode the read-only authority boundary — an agent in a headroom
  dogfood run wrote 19 unauthorized lines into this repo's
  `.agents/decisions.md`. Recorded then as the narrower Open finding "the
  authority/scope boundary has no stated precedence over the content-quality
  invariants", whose recommended fix was scoped to that one pair.
- 2026-07-04
  (`bugs/AgentGovernanceBootstrap-flag-conflicts-invariant-no-precedence-over-nondiscretionary-decisions-2026-07-04.md`,
  which supersedes the same run's earlier wiring-gap report): a
  `/update-governance` run read the 2026-07-03 unconditional-playbook-install
  decision, quoted its no-discretion language verbatim, and still raised the
  reinstall of a recently-reverted playbook as an approval-summary question by
  invoking the generic flag-conflicts invariant against git history —
  reproducing the exact behavior that decision forbids.

The recurrence between a different pair of rules shows the gap is between rule
*classes*, not one pair, so the fix is the general precedence rule above (the
bug report's proposed fix; owner fix instruction 2026-07-04). This broadens
and adopts the 2026-06-23 Open finding rather than adding a third, narrower
entry; that finding is archived verbatim in
`docs/history/decisions-archive.md` in this same change.

Deliberately not implemented: the original finding's procedure-level echoes (a
read-only echo in `procedures/bootstrap.md` Step 0, an authorization-scope
bound on `procedures/migration.md`'s fold-into-canon guidance). The Universal
Invariant is the single full statement (2026-06-24 dedup decision); procedure
echoes are future hardening only if the invariant alone proves insufficient in
a reproduced incident. Outstanding bite proof, per the bug report: a re-run of
the reinstall scenario (a shipped playbook missing after a recent deliberate
revert) must draft the reinstall as a plain fact citing the 2026-07-03
decision, with no question raised — checkable on the next refresh/dogfood run.
The presence test guards the text, not the behavior.

Relationship: supplies the precedence backbone the 2026-06-10
answer-with-words / artifact-is-evidence decisions and the 2026-07-03
playbooks decision assumed; refines, does not weaken, the flag-conflicts
Universal Invariant (document-vs-document disagreements are still flagged —
the default now yields only where a more specific rule has settled the exact
case). Structural template change, so the stamp bumps `2026-07-02.1` →
`2026-07-04.1` per the 2026-06-22 reconciliation machinery. This repo's own
`AGENTS.md` stays a frozen instance, reconciled by the next self-application
run.

### 2026-07-03 — Playbooks install unconditionally on every run, like wrappers and hooks

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): preserved in full; installation is now `tools/refresh.py`'s replace-if-unmodified class, and toolkit-side template removal now propagates via the retired list. (implemented same day; plan:
`docs/superpowers/plans/2026-07-03-playbook-install-owner-gate.md`, as
corrected by its supersession note).

Decision: every playbook template shipped under
`.bootstrap-tmp/templates/playbooks/` is installed into
`.agents/playbooks/<name>.md` on every route, unconditionally — the same
standing-guarantee class as operator wrappers and hooks (2026-06-18). There is
no approval-summary question, no default, no per-run choice, and no tier
gating: installation is deterministic. A playbook already present at its final
path is never silently overwritten (same rule as committed wrappers);
installed playbooks join the Committed list and the single scoped commit like
every other drafted artifact.

Supersedes, same-day, the "playbook installation is an owner choice at the
approval gate" entry (archived verbatim in
`docs/history/decisions-archive.md`). The no-discretion principle that entry
recorded stands unchanged — the model cannot assess a repo's future needs, and
"playbooks only if the scope tier justifies them" was wrong — but the
mechanism was also wrong: it removed the agent's discretion by inserting a
per-run owner question, which the owner never asked for. The first live run
that hit the gate produced exactly the friction it should not have (owner,
2026-07-03: "there are no options. everything is installed every time").
Discretion is removed by determinism, not by asking. Consequence, stated
plainly: a playbook deleted from a target repo reappears on the next refresh
run (install-when-missing is unconditional); the durable opt-out is removing
the template from the toolkit itself. Never-overwrite protects owner-modified
playbooks, not deletions.

Relationship: extends the 2026-06-18 standing-guarantee decision to the
playbook artifact class. Amends the 2026-06-09 layout decision's "optional
playbooks" wording: every shipped playbook lands at install time. The Push
Policy approval-time question (2026-06-27) is unaffected: that is
configuration the owner chose to be asked about, not installation.

### 2026-07-03 — Subdir-scoped bootstrap is not a supported mode; monorepo probe finding closed as not-applicable

Status: Active (this entry is the canonical home of the rule; the closed Open
finding is archived verbatim in `docs/history/decisions-archive.md` in this
same change; no code change).

Decision: the toolkit is pointed only at a governance root — the directory
that owns an `AGENTS.md` + `.agents/` set, normally the repo root.
Subdir-scoped bootstrap (running the toolkit against a subdirectory of a
governed repo to give that subtree its own governance) is not a supported
mode. The 2026-06-22 Open finding "route/verification probes match literal
`package.json` against repo-relative paths (monorepo subdir miss)" is closed
as not-applicable: the probe mismatch only bites on a subdir-scoped run,
which no supported path produces.

Rationale: the 2026-07-01 verbatim-template decision makes nested governance
waste by construction — `AGENTS.md` is byte-identical in every governed repo,
so a per-subtree copy duplicates the same bytes and adds a second
reconciliation surface carrying zero content. Per-subtree facts that genuinely
differ (e.g. backend vs frontend verification commands) already have a home
inside the single `.agents/` set: path-conditional rules in
`.agents/repo-guidance.md` and per-path entries in `.agents/repo-map.json`.
Splitting state or decisions per subtree would violate the
one-discoverable-current-state-entry-point invariant. Real-world nested
per-directory `AGENTS.md` layouts exist (observed 2026-07-03 in the `agentrq`
repo: `backend/` and `frontend/` each carry their own `AGENTS.md` plus a
`@AGENTS.md` shim), but they are evidence about content-bearing `AGENTS.md`
systems and do not transfer to this toolkit, whose `AGENTS.md` carries no
repo-specific content.

Deferred, not decided: the don't-own-the-root scenario — a team owning only a
subtree of a large monorepo, unable to write files at the top level. The
natural handling would be pointing the toolkit at that subtree and treating it
as the governance root (one `AGENTS.md`, one `.agents/`, all paths relative to
it), not nested governance. No pilot or request has hit this; supporting it is
deferred until real demand and would be a fresh decision.

Decision-locus note, recorded for whenever this reopens: if scoped runs were
ever supported, the scope decision belongs to the human at kickoff (where the
tool is pointed is the decision); discovery only surfaces candidate-boundary
evidence as leads; the model proposes a layout through the approval summary.
Consistent with the route-collapse finding (Adopted 2026-07-01) that
mechanical detection is not load-bearing in this toolkit.

### 2026-07-02 — Shipped hook commands: `py -3 || python3` fallback chain; Windows scope is Git Bash

Status: Adopted 2026-07-02

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): mooted — the sole surviving shipped hook is a plain inline echo; no shipped hook invokes an interpreter. (plan with commit map:
`docs/superpowers/plans/2026-07-02-hook-python3-windows-fallback.md`; rule
lives in the hook templates, the strengthened tripwire test, and the
bootstrap procedure's hook-install step).

Decision: shipped hook commands that invoke Python use the interpreter
fallback chain `py -3 <script> 2>/dev/null || python3 <script>` — never bare
`python3` — mirroring the bootstrap procedure's Step 1 probe order. On
Windows the supported execution path is Git Bash (owner, 2026-07-02: Git for
Windows is already a Claude Code requirement, so PowerShell-only Windows
hosts are out of scope for hook commands). Claude Code hook commands
reference the project root as braced `${CLAUDE_PROJECT_DIR}` (substituted by
the harness itself, shell-independent), not unbraced shell expansion.

Rationale: harvest bug
`bugs/ExchangeAdminWeb-hook-python3-discovery-2026-07-02.md`
(roethlar/agent-harvest) — on stock Windows, `python3` on PATH is a Microsoft
Store stub, so the AGENTS.md tripwire ran the stub and was silently inert;
the discovery probe was hardened against this exact pitfall
(`procedures/bootstrap.md` Step 1) but the hook templates were not. Harness
facts per Claude Code hooks docs (checked 2026-07-02): Windows shell-form
hooks run in Git Bash if installed, else PowerShell; no OS-conditional hook
mechanism exists, so one committed command string must serve all machines.

### 2026-07-02 — AGENTS.template.md ships reflowed: no hard line-wraps; future template edits preserve this

Status: Adopted 2026-07-02 (plan with commit map:
`docs/superpowers/plans/2026-07-02-template-reflow.md`), stamp `2026-07-02.1`.

Decision: the body of `templates/AGENTS.template.md` is written one line per
paragraph or bullet — no hard line-wrapping. Future template edits preserve
this format; re-wrapping is a regression. Scope is the verbatim-installed
template only: `repo-guidance.template.md`, shims, and `procedures/*` stay
wrapped (they are hand-edited in target repos or in this repo, where wrapped
lines keep diffs reviewable).

Rationale: the 2026-07-01 verbatim-template decision removed every consumer
of wrapping in target repos — the installed `AGENTS.md` is never hand-edited,
reconciles by byte-compare + replace-whole (no hunk diffs), and is read raw
by models. Wrapping's only remaining effect is a per-session token tax: each
wrapped continuation line spends a newline plus indent. Measured 2026-07-02
via the token-counting API (`claude-opus-4-8` tokenizer): 3,873 → 3,700
tokens, a lossless −4.5% per session in every governed repo. Accepted cost:
template-source diffs in this toolkit repo become paragraph-blob diffs.
Consistent with the 2026-06-22 rejection of word-level compression (~2.7%):
that trade risked meaning for tokens and was declined; this one changes no
words.

The same version bump executes T1 of the 2026-07-01 verbosity-sweep report
(Session Startup hook-trust trim, ~26 words of rationale clauses; behavioral
contract unchanged) — owner go 2026-07-02 covered folding it in, so the
governed fleet reconciles once, not twice. The remaining sweep findings stay
pending owner IDs.

### 2026-07-01 — Governance refresh entry point; portability sweep in reconciliation; Python 3.9 floor

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the update-governance wrapper now invokes `tools/refresh.py` (the mechanical refresh); the bootstrap procedure remains the judgment path. The 3.9 floor stands and now covers refresh.py. (implemented same day; plan:
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

Status: Adopted 2026-07-01.

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): carried further — the two procedures are consolidated into one `procedures/bootstrap.md` with the migration inventory as a conditional step; mechanical reconciliation moved to refresh.py. Implemented per
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

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): superseded — defects are filed as GitHub issues on this repo (`.github/ISSUE_TEMPLATE/toolkit-defect.md`), owner-gated, redacted; the dropbox transport is retired.

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

Status: Active, as amended 2026-07-03

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the standard layout no longer includes `repo-map.json` / `artifact-manifest.json` (retired, flag-only on refresh); the verification command's canonical home is `.agents/repo-guidance.md`.: playbooks are part of the standard
layout, no longer optional — every shipped playbook template installs on
every run (see the 2026-07-03 playbooks decision above). The original
wording below is retained.

Decision:
Every bootstrapped repo converges on the same `.agents/` layout (AGENTS.md + .agents/state.md, .agents/decisions.md, repo-map.json, artifact-manifest.json, optional playbooks). Existing governance systems are migrated into it via inventory (migrate/supersede/leave verdicts), not left as parallel canon. Old governance files (when they stay) receive a short supersession banner at the top pointing to the replacement; content is retained as history.

Reason:
This eliminates drift from competing sources of truth and gives every future agent (including in this toolkit repo) one discoverable current-state entry point plus one place for settled decisions. The layout is the outcome of the 2026-06-09 architecture restructure.

Supersedes:
The prior two-stage PowerShell architecture (historical record only in `docs/history/`).

### 2026-06-09 - Harvest is minimal, gated, dropbox-first

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): transport superseded — harvest rules are filed as GitHub issues (`.github/ISSUE_TEMPLATE/harvest-rule.md`); the discipline (incident-earned, max three, no-report-is-normal, owner-gated publish) is retained verbatim there.

Decision:
During a migration the agent may (rarely) record generalizable governance rules in a harvest report, under strict limits: expected outcome is no report; an idea qualifies only if earned by a real citable incident, not already covered by templates, useful to other repos, and at most three ideas total; never a "nothing found" file. Delivery: write append-only as a new dated file in the `agent-harvest` dropbox via the shared transport recipe (`procedures/file-to-dropbox.md`), which any session may publish to only with an explicit owner go; otherwise fall back to `.agents/harvest.md` in the target. Harvest reports are never delivered into the canonical bootstrap repo itself. (Supersedes the earlier "standing authorization" auto-push: as of 2026-06-22 every dropbox publish — harvest report or bug report — asks before pushing, so the two paths share one transport and one gate.)

Reason:
Prevents over-eager padding and keeps the shared canon clean. A separate sweep session (owner-initiated only) in this repo judges new reports skeptically and logs outcomes in `harvest/processed.md`.

Supersedes:
Earlier ideas of richer or automatic harvesting.

### 2026-06-09/10 - Single-session kickoff with Python discovery; self-healing freshness

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the discovery script is retired; discovery is a live checklist in the consolidated procedure. The single-session kickoff, Step 0 sync, and self-healing freshness principles stand.

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

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the guarantee's mechanism is now refresh.py's replace-if-unmodified class, which strengthens never-overwrite: a provably-unmodified stale wrapper updates; an owner-modified one is flagged, never touched.

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

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): superseded — the stamp is removed; refresh.py's newline-normalized compare against known template versions carries the decision, and the refresh commit message records the toolkit sha as provenance.

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

Status: Adopted 2026-06-25.

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): L2 (the advisory tripwire) is retired on ledger evidence (silently inert on stock Windows, nothing degraded); L1 (the invariants) stands; L3 is now refresh.py's byte-verify-and-repair. The two boundary invariants landed as bullets in
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

The following were assessed on 2026-06-22 from three external repo
reviews (DeepSeek, GPT-5.5, Grok) read against current repo evidence. The
reviews' other suggestions were rejected as scope-inflating or already covered
and are not recorded. Recommendation order below is the suggested implementation
sequence. (The batch's monorepo-subdir probe finding was closed 2026-07-03 as
not-applicable — see that decision above and the archive.)

### Open: hook-merge strategy is underspecified in the procedure

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): mooted — hooks are no longer agent-merged; refresh.py installs the single shipped settings file replace-if-unmodified and flags anything owner-modified. Recommend closing at next sweep.

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

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): resolved — replace-if-unmodified updates a wrapper that byte-matches any formerly-shipped version and flags owner-modified ones. Recommend closing at next sweep.

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

### Open: foreign-model governance validation

Owner needs a way for a *different* model to validate that a repo's governance
works (the in-bootstrap fresh-eyes test only ever runs the same model that drafted
the guidance). Not yet designed or decided — surfaced 2026-06-22, undecided.

The following were assessed on 2026-06-23 from bug reports filed to the
`agent-harvest` dropbox during a `headroom` (chopratejas/headroom) dogfood
migration run, read against current repo evidence. They are appended at the end of
the queue; the implementation sequence of the items above is unchanged. (The
batch's authority/scope-boundary precedence finding was broadened into the
general specific-over-generic precedence rule and adopted 2026-07-04 — see that
decision; the original entry is archived verbatim.)

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

The following two were recorded 2026-07-06 on the owner's explicit instruction
("just add these as open items"). They are owner-surfaced product gaps, not yet
designed or decided.

### Open: the `reviewloop` playbook hard-requires git branches; it should not

Evidence: `templates/playbooks/reviewloop.md` makes a per-finding git branch a
load-bearing requirement of the loop, not a repo-configurable choice. The atomic
unit is stated as "**one finding ↔ one branch ↔ one verdict**" (`:38`); the
per-finding flow opens with "Finish the fix on a per-finding branch
`fix/<id>-<slug>`" (`:124`); the reviewer dispatch pins "the reviewed branch
**head SHA**" and merge-base (`:127-130`); accepted/reopened/invalid actions are
all phrased in branch terms (`:156-163`); and both the finding-doc template
(`**Branch**:`, `:211`) and the status index (a `Branch` column, `:270-273`)
bake a branch in. This collides with this repo's own 2026-06-10
"One-item-per-commit discipline" decision, which settled that "**Whether work
happens on a branch is repo policy, not this rule**" — the playbook removes the
per-repo discretion that decision reserves. Owner (2026-07-06): the playbook
"demands git branches. it should not."

Options: (a) re-express the atomic unit as "one finding ↔ one reviewable
change ↔ one verdict" and make the branch one *permitted* isolation mechanism
among others (branch, worktree, or a single commit on the working branch),
deferring the choice to repo policy the way the commit-discipline decision does;
the pinned base/head SHA contract (which needs only two commits, not a branch)
and the reviewer's own disposable worktree stay unchanged. (b) keep branches as
the documented default but add an explicit "no-branch" knob. (c) leave as-is.

Recommendation: (a) — it aligns the playbook with the repo's existing
branch-is-repo-policy decision and keeps the actual review discipline (pinned
SHAs, guard proof, recorded fail-closed verdict) intact, since none of it
depends on a branch existing. Playbook-template change only; no `discover.py`
surface. A `plan` should confirm the SHA-pinning and worktree language survives
the rewording before implementation.

### Open: a fast-update route/command for docs-only refreshes without a full update or migration

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): resolved — `tools/refresh.py` is exactly this: the mechanical refresh path, seconds, no agent ceremony. Recommend closing at next sweep.

Evidence: discovery currently computes two routes — `greenfield` and
`migration` (the former `update` route was collapsed into `migration`,
Adopted 2026-07-01; `compute_route()` returns `"migration" if
governance_markers else "greenfield"`, `tools/discover.py:253-259`). Every
already-governed repo therefore takes the one heavy path: full discovery, an
inventory/reconciliation pass, the fresh-eyes check, and the approval summary
(`procedures/bootstrap.md` Step 3; `procedures/migration.md`). There is no
lightweight path for the common case of "just refresh the docs" — updating
`README.md`, `docs/*`, or other non-governance prose — without paying for the
whole reconciliation ceremony. Owner (2026-07-06): "we need a fast-update
option to update docs without doing a full update or migration." Naming is
open ("route? command? option? no fucking clue what you want to call it").

Open questions for the design (not yet decided):
- **Shape** — a third `compute_route()` route, a standalone operator/command
  wrapper (like `update-governance`), or a documented fast-path *mode* within
  the existing route. Note the standing repo lean that route *detection* is not
  load-bearing (2026-06-28 collapse, Adopted 2026-07-01), which argues against a
  new detected route and toward a command/mode.
- **Scope boundary** — what "docs" means precisely, and how the fast path
  refuses (or escalates) when a requested change touches governance
  (`AGENTS.md`, `.agents/*`, templates, `discover.py`) rather than plain docs.
  The docs-only verification carve-out already exists as a concept
  (`git diff --check` vs. the full test suite) and could anchor the boundary.
- **Gate** — whether a docs-only fast path still routes through the approval
  summary or uses a lighter confirmation, given the smaller blast radius.

Recommendation: none yet — recorded for a future decision, then a `plan`. The
most likely fit given the no-load-bearing-detection stance is a command/mode
rather than a fourth detected route, but that is a design call for the owner.
