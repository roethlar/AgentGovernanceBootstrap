# Zero-based consolidation: every piece justifies its existence or leaves

Status: Draft 2026-07-08 — under cross-harness review (reviewloop, codex), then
owner approval. No product change lands before the owner approves this plan.
Supersedes `2026-07-08-field-audit-hardening.md` (narrower same-day draft;
its field-audit evidence base and its state-lifecycle/write-rule slices carry
forward into this plan).

## Scope discipline

Two categories, kept separate throughout:

- **Product** — what ships into target repos or executes against them:
  `templates/*`, `procedures/*`, `tools/*`, and this repo's GitHub issue
  templates (toolkit infrastructure for the feedback channel).
- **This repo's documentation** — `README.md`, `docs/usage.md`,
  `docs/design.md`: maintainer-facing descriptions of the product. They are
  not shipped; they get one truth-maintenance slice at the end, after the
  product has changed.

## Evidence base

Two audits on 2026-07-08, both independently re-checkable:

1. **Field audit of the five deployed repos** (Blit_v2, vela,
   Powershell-Token-Killer, ai-rpg-engine, ExchangeAdminWeb). The core loop —
   state → handoff → decisions → plan gate → review loop → gated commit —
   demonstrably works: handoffs resumed across sessions and machines (a
   checklist written on one machine executed item-by-item on another four
   days later; findings queued in state.md closed 22 days later; a handoff's
   Next list mapping 1:1 onto the following session's commits), decisions and
   pauses held, and the reviewloop caught real pre-ship bugs (vela `eh-10`,
   `eh-5`, `sspf-13`). The recurring failures are equally consistent:
   state.md journals without rotation (537/457/578 lines, live
   self-contradictions), volatile facts rotting in days (push status, CI
   color), duplicated counts diverging (43/29 vs 70/37; "nine decisions" vs
   six), machine-local facts written as repo truth (a remotes doc
   "drift-fixed" to opposite configurations by two machines in one day),
   clones silently far behind canon (75 commits), and the JSON layer
   (`repo-map.json`, `artifact-manifest.json`) frozen and wrong everywhere
   while the prose files stayed accurate.
2. **Product audit of this repo.** Fleet refresh is a manual gated agent
   session per repo per template change — one deployment sits 10 template
   versions stale. Three of the seven bug reports in the ledger are
   `tools/discover.py`'s own defects. The AGENTS.md pre-edit tripwire hook
   was silently inert on stock Windows for weeks and nothing degraded — the
   strongest evidence on record that it is not load-bearing. The per-harness
   grok/agy hook configs have never been shown to fire. Scope tiers condition
   no behavior. The stamp/missingSections staleness probes are subsumed by
   the byte compare. 53% of the Python under `tools/`+`tests/` is the closed
   eval workstream's instrument. The dropbox feedback transport is three
   procedures, two templates, a config file, and a second repo for what one
   authenticated `gh` command does.

Standing rule adopted with this plan (owner, 2026-07-08): **no shipped rule
without provenance** — a template rule is added, kept, or changed only with a
`decisions.md` entry citing its earning incident. During slice 2 every kept
template line is cross-checked against the decision record; any line with no
traceable earning incident is reported to the owner as a cut candidate at the
approval gate, not silently retained.

## What the product becomes

The template set + one bootstrap/migration procedure + `tools/refresh.py` +
the reviewloop playbook + a GitHub-issues feedback convention. Steady-state
maintenance is one command run in whatever repo you are standing in. Agent
sessions are for judgment only: first bootstrap, migration inventory, and
repo-guidance changes.

## Slices

Ordered; each slice is its own commit (or small commit series), suite green
before each completion claim.

### Slice 1 — `tools/refresh.py`: pull-based per-repo governance refresh

The mechanical core that replaces per-repo agent refresh sessions. No
registry, no central state: run it while standing in a governed repo.

- **Sync**: fast-forward the local toolkit clone from its canonical remote
  (reusing the existing Step 0 logic: `git -C`, `ls-remote` liveness,
  `--ff-only`; offline ⇒ proceed on the local copy with a printed flag;
  self-provision by cloning if no local copy exists).
- **Shipped set**: a manifest in the toolkit, `tools/shipped-set.json`, maps
  each shipped artifact to its target path and class:
  - `replace-whole`: `AGENTS.md` (byte-exact copy of the template);
  - `install-if-missing`: shims (`CLAUDE.md`, `GEMINI.md`, …), operator
    wrappers, playbooks — never overwrite an existing file (preserves
    owner-modified copies, the existing rule);
  - `retired`: explicit list of formerly-shipped target paths, each with the
    byte-hash(es) of the shipped version(s); **remove only when the file
    byte-matches a formerly-shipped version, otherwise leave it and flag** —
    a modified file is never deleted by machine.
- **Repo-owned files are never touched**: `.agents/state.md`,
  `.agents/decisions.md`, `.agents/repo-guidance.md`,
  `.agents/push-policy.md`, plans, review trails, archives.
- **Safety**: refuse to run over uncommitted changes on any path it would
  touch; idempotent (second run is a no-op); prints a report of
  added/updated/removed/flagged.
- **Commit**: stages exactly the reconciled paths, one scoped commit whose
  message records the toolkit commit hash it synced to (this replaces the
  `templateVersion` stamp as provenance). It does not push; it prints the
  repo's push policy as a reminder.
- `templates/commands/claude/update-governance.md` is rewritten to invoke
  the script (the wrapper keeps its hardcoded toolkit URL — personal-toolkit
  decision, owner 2026-07-08). First bootstrap also uses the script: the
  agent drafts the judgment artifacts, and after approval `refresh.py`
  performs the mechanical set install (see slice 5).
- Tests: reconcile add/update/remove, never-overwrite, modified-retired-file
  flagged not deleted, byte-exact AGENTS.md, dirty-tree refusal, idempotence,
  offline sync fallback. All guard-proven.

Why a script and not the agent, on the record: refresh is
synchronize-to-an-exact-set, the documented agent failure mode — a dogfood
refresh concluded "content already current" while seven stale template
passages sat under a matching stamp (`.agents/state.md`, 2026-07-01 entry);
an update run narrowed wrappers to fit a stale file (2026-06-22 decision,
Reason); and removal is currently impossible by construction (deleted
playbooks resurrect, 2026-07-03 decision, Consequence). Byte-exactness and
deletion are deterministic work.

### Slice 2 — `templates/AGENTS.template.md` redline (owner-reviewed 2026-07-08)

Current: 97 lines / ~1,660 words loaded into every session of every repo.
Target: ~65 lines / ~1,100 words. Same four Prime Invariants.

- **Cut**: the `## Bootstrap Handoff` section (`.bootstrap-tmp/` routing dies
  with slice 4); Session Startup's hook-trust step (hooks die in slice 3);
  the `templateVersion` stamp (provenance moves to the refresh commit
  message); `## Mission` as a section (its one real rule — no scope expansion
  without approval — moves into the Prime Invariants); the
  "verify-before-claiming" pointer bullet (the Verification section speaks
  for itself); the three durable-writing bullets merged into one (record or
  report-unrecorded + survives-without-conversation + no transient chat
  wording), with label-assumptions folded into the merged bullet.
- **Changed**: the write-authority invariant shrinks to one sentence
  ("`AGENTS.md` is the toolkit template, installed and replaced whole by
  governance refresh; never hand-edit it — repo-specific rules go in
  `.agents/repo-guidance.md`") now that refresh repairs divergence
  mechanically; Verification's recorded home becomes
  `.agents/repo-guidance.md` (the JSON home dies in slice 4); the `handoff`
  operator gains the three field-earned clauses — (a) rotate
  landed/superseded entries verbatim to `docs/history/state-archive.md`,
  `## Now` holds only live items; (b) volatile predicates carry
  `as of <commit>` or are dropped, counts owned elsewhere become pointers,
  machine-local facts are labeled `machine-local (<host>)` or not recorded;
  (c) parked/blocked items get their recorded factual basis re-verified —
  the `drift` operator's AGENTS.md leak-scan paragraph shrinks (script
  repairs divergence); Source Of Truth compresses from 8 ranked items to ~5.
- **Added** (one line): Session Startup clone-freshness check — read-only
  `git ls-remote <canonical-remote> HEAD` compared to the local ref before
  trusting `state.md`; behind/diverged ⇒ say so and treat state as possibly
  stale; unreachable ⇒ proceed with a one-line caveat, **never block**.
- **Kept, each with provenance cross-check** (per the standing rule):
  words-first; plan-gate; commit-each-slice + push-policy pointer;
  repo-is-memory + re-ground anchor; harness-local-memory;
  one-canonical-location; single current-state entry point; flag-conflicts;
  specific-over-generic; smallest-set; roadblock-provenance;
  stall-not-length; portability test; the three Git Safety bullets; the six
  operators. Lines with no traceable earning incident are reported as cut
  candidates at the approval gate.
- Companion template changes in the same stamp-free release:
  `state.template.md` header carries the rotation + write rules and its
  Verification section becomes a pointer to repo-guidance;
  `approval-summary.template.md` drops scope tiers (condition nothing) and
  the JSON files, keeps the push-policy question and custody discipline;
  `repo-guidance.template.md` Verification comment notes it is the canonical
  home; `decisions.template.md` unchanged; `push-policy` template unchanged.

### Slice 3 — hooks retired as a shipped artifact class

Delete `templates/hooks/` (all four harnesses, tripwire script included) and
the hook-install steps from the procedures. Rationale on the record: the
tripwire is advisory, costs a process spawn on every edit in every repo, and
was silently inert on stock Windows for weeks with no degradation — its job
(protect `AGENTS.md` from hand-edits) transfers to `refresh.py`'s
byte-verify-and-repair. The re-ground echo goes with the class (unproven
benefit; the Prime Invariants block keeps its own re-ground anchor text).
The grok/agy configs were never shown to fire. Retired entries go into
`shipped-set.json` so deployed repos shed the files on their next refresh
(byte-match rule protects any owner-modified `settings.json`; a shipped
settings file with owner additions is flagged, not deleted).

### Slice 4 — discovery and the JSON layer retired

- Delete `tools/discover.py`, `tools/manifest-schema.md`, the golden
  manifests, and their tests. Three of seven ledger bugs were its defects;
  a frontier agent re-derives its outputs live. Its irreplaceable knowledge
  folds into the procedure as prose: the Windows Store-stub probe order
  (`py -3` → `python3` → `python`, "Microsoft Store" output means absent),
  ignore-aware governance detection (git-ignored and machine-local files are
  not governance evidence), and the CI-executability rule (a workflow is
  evidence only in a provider-executed path with branch triggers matching;
  otherwise verification is local-only).
- `repo-map.json` and `artifact-manifest.json` leave the product: templates
  deleted, drafted-set references removed, retired entries added to
  `shipped-set.json`. Frozen-and-wrong in every audited repo; custody is
  proven live by git at the approval gate; the verification command's single
  home is `repo-guidance.md`.
- `.bootstrap-tmp/` as a copied handoff pack dies (no discover output, no
  START-HERE, no sandboxed fallback flow — the agent must be able to read
  the toolkit clone). The **drafts directory survives**: bootstrap sessions
  still draft under a self-ignored `.bootstrap-tmp/drafts/` mirroring final
  paths, reviewed via the approval summary, copied on approval — the custody
  spine is unchanged.

### Slice 5 — procedures consolidated

`procedures/bootstrap.md` + `procedures/migration.md` rewritten as one
procedure (~2,500 words, from ~5,200) with the migration inventory as a
conditional section. Survives: Step 0 toolkit sync; a live-discovery
checklist (replacing the script: enumerate governance artifacts via
`git ls-files` + the ignore-aware rule; identify the verification command
from repo evidence; the CI-executability rule); the drafting set — now
explicitly `AGENTS.md`, `.agents/repo-guidance.md`, `state.md`,
`decisions.md`, **`push-policy.md`** (the never-drafted hole, fixed), shims,
wrappers, playbooks; the plain-English approval summary; the custody proof;
the one-scoped-commit contract; fresh-eyes (`procedures/verification.md`,
migrations only, unchanged); the push-policy consult. The mechanical install
after approval is delegated to `refresh.py` (one recipe, no drift between
bootstrap-install and refresh-install). Dangling references (the
"bootstrap.md Step 4" pointer) die with the rewrite. Deleted outright:
`procedures/harvest.md`, `procedures/file-bug-report.md`,
`procedures/file-to-dropbox.md`.

### Slice 6 — feedback channel: GitHub issues on this repo

- `.github/ISSUE_TEMPLATE/toolkit-defect.md` and `harvest-rule.md`, carrying
  the discipline text that survives from the dropbox era: a defect report
  needs the incident and evidence; a harvest rule must be earned by a real
  citable incident, not already covered, useful across repos; the expected
  outcome of most sessions is **no report**; never file "nothing found".
- One paragraph in the procedure: on confirming a toolkit defect or a
  qualifying rule from a target-repo session, draft the issue body, present
  it, and file with `gh issue create -R <toolkit-repo>` **only on an
  explicit owner go**; offline or no-go ⇒ the existing in-repo fallback note.
- Retirements: the `agent-harvest` dropbox repo (owner archives it),
  `harvest.config.json`, and `harvest/processed.md` (open/closed issues are
  the triage ledger; the existing processed.md is archived verbatim to
  `docs/history/`). The sweep operator becomes "read open issues, decide
  each, close with a reason."
- Owner decision at approval: leave this repo public (issues public) or flip
  it private.

### Slice 7 — eval instrument leaves the product tree

`tools/run_fixture.py`, `tools/drivers.py`, `tools/polyglot_fixture.py`, and
`tests/test_run_fixture.py` (1,231 lines) move under `evals/` with a
README line marking the workstream closed (owner may choose deletion instead
— git history preserves either way). The product suite becomes the refresh.py
tests plus the surviving structural template tests; the 12 prose-pin
phrase-guard tests are deleted, not moved.

### Slice 8 — this repo's documentation (not product)

`README.md`, `docs/usage.md`, `docs/design.md` rewritten to describe the
consolidated product truthfully: the bootstrap prompt, the refresh command,
the issues convention; no routes table, no fallback flow, no dropbox setup,
no discovery-manifest sections. This repo's `.agents/repo-guidance.md`
(reading order, verification command) updated to match the new tree. Known
current drift (the collapsed `update` route still documented, the broken
spec link, the canonical-remote wording) dies in the rewrite rather than
being patched first.

### Slice 9 — validation rollout (owner-gated per repo)

After approval and landing, run `refresh.py` against one low-stakes deployed
repo first, verify the reconcile report (adds the new template, removes the
JSON files/hooks, flags anything modified), then the remaining four on the
owner's go. This is the removal-semantics bite-proof on real repos; findings
route back as issues.

## Decisions to record in `.agents/decisions.md` on implementation

Each with the incident/evidence citations above: refresh-by-script +
shipped-set reconciliation (supersedes the mechanical half of the agent-run
refresh flow; the 2026-07-03 unconditional-playbook decision's intent is
preserved and now script-enforced, and its deleted-playbooks-resurrect
consequence is replaced by retired-list semantics); hooks retired (supersedes
the tripwire layer of the 2026-06-25 boundary decision — L1 prose and the
new mechanical repair remain — and moots the 2026-07-02 hook-interpreter
decision); discovery-by-checklist (supersedes the script half of the
2026-06-09/10 kickoff decision; the single-session kickoff itself stands);
JSON layer retired; feedback-via-issues (supersedes the 2026-06-22 dropbox
decisions and the transport follow-up); verification's canonical home;
state rotation + write rules; the no-rule-without-provenance standing rule.

## Verification

- Slices 1, 3, 4, 7: `py -3 -m unittest discover -s tests -v` (Git Bash)
  green before each completion claim; every new test guard-proven (revert →
  fail → restore → pass).
- Slice 2 (templates): surviving structural tests green; token/word count of
  the new template reported at the approval gate against the ~1,100-word
  target.
- Slices 5, 6, 8 (procedures/docs): `git diff --check` plus a full sequential
  read-through of the consolidated procedure; slice 6 additionally verified
  by filing one test issue end-to-end (owner-gated).
- Slice 9 is itself the end-to-end verification of slices 1–4 on real repos.

## Open questions for the owner (at approval)

1. Issues public (repo stays public) or repo flips private?
2. Eval instrument: move under `evals/` or delete outright?
3. Rollout order for slice 9 (which repo first)?

## Review log

- r1 (2026-07-08, codex): pending.
