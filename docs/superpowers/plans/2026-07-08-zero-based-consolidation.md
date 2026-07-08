# Zero-based consolidation: every piece justifies its existence or leaves

Status: Draft 2026-07-08 — codex accepted the base plan at r4 (`ddcec13`,
zero findings); post-r4 owner amendments (multi-harness parity, public
issues + redaction rule, vela-first rollout) are under codex re-review (r5).
Awaiting that verdict, then owner approval. No product change lands before
the owner approves this plan.
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
the reviewloop playbook + the compaction re-ground hook (per harness, where
verified to fire) + a GitHub-issues feedback convention. The architecture
stays harness-neutral by construction: all durable truth lives in
`AGENTS.md` + `.agents/`, which every harness reads (codex loads `AGENTS.md`
natively with no shim); harness-specific files are pure adapters, shipped
per harness behind a verify-once gate. Steady-state
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
  - `replace-if-unmodified`: shims (`CLAUDE.md`, `GEMINI.md`, …), operator
    wrappers, playbooks, `.claude/settings.json` — missing ⇒ install;
    byte-matches any formerly-shipped version ⇒ provably unmodified, update
    to the current shipped version; anything else ⇒ owner-modified: **flag,
    never overwrite**. This strengthens the old install-if-missing rule
    (which could never update a provably-unmodified stale wrapper) while
    preserving exactly what the 2026-06-18/2026-07-03 decisions protect:
    owner modifications.
  - `retired`: explicit list of formerly-shipped target paths, each with the
    hash(es) of the shipped version(s); **remove only when the file matches a
    formerly-shipped version, otherwise leave it and flag** — a modified file
    is never deleted by machine.
  - **All content matching and all shipped-version hashes are
    newline-normalized** (`\r\n` → `\n` before compare/hash) — the same
    tolerance the old byte-compare carried accidentally and load-bearingly:
    the fleet spans autocrlf Windows checkouts and LF Unix checkouts, and
    raw byte-matching would false-flag unmodified files on either side.
    Tests include a CRLF-checkout fixture.
  - **Committability, per shipped path** (carrying forward the 2026-06-10
    gitignore-aware custody rule and the 2026-06-18 repair, stated
    harness-neutrally): `refresh.py` runs `git check-ignore` on each target
    path before staging; a path ignored by a known blanket
    harness-adapter-dir pattern (`.claude/`, `.codex/`, `.gemini/`,
    `.grok/` ignored wholesale) gets the established narrow repair — drop
    the blanket rule, add that harness's machine-local exclusions (e.g.
    `.claude/settings.local.json`) — with the `.gitignore` edit included in
    the same scoped commit; a path ignored by any rule the script does not
    recognize is **flagged and skipped**; `git add -f` is never used.
- **Repo-owned files are never touched**: `.agents/state.md`,
  `.agents/decisions.md`, `.agents/repo-guidance.md`,
  `.agents/push-policy.md`, plans, review trails, archives. Division of
  labor with first bootstrap, stated plainly: `refresh.py` installs the
  **shipped set only**; the approved judgment drafts (the repo-owned
  `.agents/` files) are copied from `.bootstrap-tmp/drafts/` to their final
  paths by the bootstrap procedure's existing copy-on-approval step — the
  script's never-touch contract and the bootstrap install are disjoint by
  construction, and both land in the same single scoped bootstrap commit.
- **Safety**: refuse to run over uncommitted changes on any path it would
  touch; idempotent (second run is a no-op); prints a report of
  added/updated/removed/flagged.
- **Commit — two modes.** Default (standalone refresh): stages exactly the
  reconciled paths and makes one scoped commit whose message records the
  toolkit commit hash it synced to (this replaces the `templateVersion`
  stamp as provenance). `--stage-only` (the first-bootstrap mode): stages
  the reconciled paths and stops — the bootstrap procedure then copies and
  stages the approved judgment drafts and makes the **single scoped commit
  covering both groups**, exactly as the approval summary announced. The
  dirty-tree refusal is scoped to the paths `refresh.py` itself would touch,
  so pre-staged judgment drafts never trip it. Neither mode pushes; the
  script prints the repo's push policy as a reminder.
- `templates/commands/claude/update-governance.md` is rewritten to invoke
  the script (the wrapper keeps its hardcoded toolkit URL — personal-toolkit
  decision, owner 2026-07-08). First bootstrap also uses the script: the
  agent drafts the judgment artifacts, and after approval `refresh.py`
  performs the mechanical set install (see slice 5).
- Tests: reconcile add/update/remove, never-overwrite, modified-retired-file
  flagged not deleted, byte-exact (newline-normalized) AGENTS.md, CRLF
  checkout fixture, blanket-adapter-dir ignore repair (one case per adapter
  dir: `.claude/`, `.codex/`, `.gemini/`, `.grok/`), unrecognized-ignore
  flag-and-skip, no-force-add, dirty-tree refusal scoped to own target
  paths, `--stage-only` (stages without committing; pre-staged foreign paths
  untouched), idempotence, offline sync fallback. All guard-proven.

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
  with slice 4); Session Startup's hook-trust step shrinks to one line
  (naming the single surviving compaction hook; the gate-respect rule stays);
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

### Slice 3 — hooks: one survivor, the rest retired

**Kept — the compaction re-ground hook, per-harness behind a verify-once
gate** (owner decisions 2026-07-08: keep the hook on reconsideration; the
toolkit is multi-harness — codex is as important as Claude Code, gemini/
antigravity and grok situational). Its provenance is structural, recorded so
this is never re-litigated: the failure mode it guards — loss of in-context
rules at compaction — cannot be mitigated from inside the context, because
every prose anchor (including the Prime Invariants' own re-read line)
degrades *with* the context being compacted; a hook fires from outside,
after the event, which is the only mechanism shape that survives it. Cost is
one injected line per compaction event. The shipping rule is the evidence
rule applied per harness: **ship the re-ground adapter for each harness
whose event mechanism is verified live, once, during implementation** —
Claude Code is already verified (2026-06-21); codex, gemini/antigravity, and
grok each get a one-time live check (does the harness fire a
session-start/compaction event from a repo-level config?); ship where it
fires, record the negative where it does not. The shipped
`.claude/settings.json` shrinks to this single entry; every surviving hook
config ships `replace-if-unmodified`. One hook-trust line survives in the
template's Session Startup (trimmed, not the current two-step section).
The same verify-once gate applies to **operator wrappers** on harnesses
that support repo-level command files (Claude's `.claude/commands/` is
verified today; codex/gemini equivalents are checked during implementation
and added to the shipped set where they work — the operators themselves
remain harness-neutral prose in `AGENTS.md` and work by being spoken on any
harness).

**Retired — everything else in the class**: the AGENTS.md pre-edit tripwire
on every harness (advisory, a process spawn on every edit in every repo, and
silently inert on stock Windows for weeks with no degradation — its job
transfers to `refresh.py`'s byte-verify-and-repair), the tripwire script
file, and the grok/agy hook configs (never shown to fire — shipped config
with no evidence behind it). Retired entries go into `shipped-set.json` so
deployed repos shed the files on their next refresh; prior shipped
`settings.json` versions (re-ground + tripwire) are in the
formerly-shipped hash list, so an unmodified one updates to the new
single-hook file, while an owner-modified one (e.g. Blit_v2's) is flagged,
never touched.

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
  the toolkit clone). The **drafts directory survives, scoped to
  judgment artifacts only**: bootstrap sessions draft the repo-owned files
  (`repo-guidance.md`, `state.md`, `decisions.md`, `push-policy.md`, plus
  migration supersession banners) under a self-ignored
  `.bootstrap-tmp/drafts/` mirroring final paths, reviewed via the approval
  summary, copied on approval. Shipped-set artifacts (`AGENTS.md`, shims,
  wrappers, playbooks, the hook settings) are **never drafted** — they have
  exactly one installer, `refresh.py`, so the `replace-if-unmodified`
  protections cannot be bypassed by a draft copy. The custody spine is
  unchanged.

### Slice 5 — procedures consolidated

`procedures/bootstrap.md` + `procedures/migration.md` rewritten as one
procedure (~2,500 words, from ~5,200) with the migration inventory as a
conditional section. Survives: Step 0 toolkit sync; a live-discovery
checklist (replacing the script: enumerate governance artifacts via
`git ls-files` + the ignore-aware rule; identify the verification command
from repo evidence; the CI-executability rule); the drafting set — the
**judgment artifacts only**: `.agents/repo-guidance.md`, `state.md`,
`decisions.md`, **`push-policy.md`** (the never-drafted hole, fixed), and
migration supersession banners; the plain-English approval summary, which
lists both the judgment drafts to be copied **and** the shipped set
`refresh.py` will install, so the owner approves one complete picture; the
custody proof; the one-scoped-commit contract covering both groups;
fresh-eyes (`procedures/verification.md`, migrations only, unchanged); the
push-policy consult. `AGENTS.md`, shims, wrappers, playbooks, and the hook
settings are not drafted and not hand-copied — on approval the procedure
invokes `refresh.py --stage-only`, the single installer for shipped
artifacts (one recipe, no drift between bootstrap-install and
refresh-install, no bypass of the replace-if-unmodified protections), then
copies and stages the approved judgment drafts and makes the one scoped
commit covering both groups. Dangling references (the
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
- **Issues are public** (owner decision 2026-07-08: repo stays public). The
  filing convention and both issue templates therefore carry a redaction
  rule: **no PII or sensitive information in issue bodies** — no secrets,
  tokens, credentials, private hostnames/IPs, or personal data; evidence is
  cited by repo-relative path and commit hash, never by pasting sensitive
  content. The pre-filing owner-go presentation includes a redaction check.
- Retirements: the `agent-harvest` dropbox repo (owner archives it),
  `harvest.config.json`, and `harvest/processed.md` (open/closed issues are
  the triage ledger; the existing processed.md is archived verbatim to
  `docs/history/`). The sweep operator becomes "read open issues, decide
  each, close with a reason." `templates/bug-report.template.md` and
  `templates/harvest-report.template.md` are adapted into the two
  `.github/ISSUE_TEMPLATE/` files and the originals deleted (they were
  toolkit-side drafting aids, never installed into target repos — no
  retired-list entries needed).

### Slice 7 — the eval workstream is scrapped entirely

Owner decision 2026-07-08: delete, don't archive. The whole `evals/`
directory (results, test plans, pre-registration, SWE-bench pilots,
governance profiles, `aggregate.py`/`calibrate.py`/`run_trials.py`) plus the
instrument in the product tree (`tools/run_fixture.py`, `tools/drivers.py`,
`tools/polyglot_fixture.py`, `tests/test_run_fixture.py`, 1,231 test lines)
is removed. Git history preserves every line; any future revival starts from
a checkout and a fresh decision.

**One salvage before deletion**: `evals/harness-capabilities.md` relocates
to `docs/harness-capabilities.md` — it is verified per-harness fact, not
eval apparatus (bare `AGENTS.md` inert in Claude Code headless / the
`@AGENTS.md` shim load-bearing; codex loads `AGENTS.md` natively, no shim;
which hook events fire where; Stop-hooks Claude-only), and it is the
evidence base for slice 3's per-harness verify-once checks.

Supersession recorded with this slice: the 2026-07-01 condensation
decision's clause keeping `completeness-general` in
`evals/governance_profiles/` "as a candidate" — the profile is deleted with
the workstream. The product suite becomes the refresh.py tests plus the
surviving structural template tests; the 12 prose-pin phrase-guard tests
are deleted, not moved.

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

After approval and landing, run `refresh.py` against **vela first** (owner
decision 2026-07-08: it is the actively-worked repo — it gets current
tooling first and the owner is present to catch any problem immediately).
Verify the reconcile report (adds the new template, removes the JSON
files/retired hooks, flags anything owner-modified), then the remaining four
repos on the owner's go. This is the removal-semantics bite-proof on real
repos; findings route back as issues.

## Decisions to record in `.agents/decisions.md` on implementation

Each with the incident/evidence citations above:

- **Refresh-by-script + shipped-set reconciliation** — supersedes the
  mechanical half of the agent-run refresh flow and the 2026-06-22
  templateVersion-stamp decision. The 2026-07-03 unconditional-playbook
  decision is **preserved in full**: shipped playbooks still install on
  every run, a target-repo deletion still reinstalls, and the durable
  opt-out is still removing the template from the toolkit — retired-list
  semantics add only the previously-missing half, that toolkit-side removal
  now actually propagates as deletion. The `replace-if-unmodified` class is
  recorded as a strengthening of the 2026-06-18 never-overwrite rule
  (byte-match against formerly-shipped versions proves non-modification).
- **Hooks narrowed to the compaction re-ground, shipped per-harness behind
  a verify-once gate** — amends the 2026-06-21 per-harness re-ground
  decision (per-harness retained, now evidence-gated: Claude verified
  2026-06-21; codex/gemini/grok ship only after their one-time live check
  passes, with negatives recorded; the structural outside-the-context
  rationale recorded); supersedes the tripwire layer (L2) of the 2026-06-25
  boundary decision (L1 prose stays, L3 becomes `refresh.py` repair); moots
  the 2026-07-02 hook-interpreter decision (the surviving hook is a plain
  echo, no interpreter).
- **Discovery-by-checklist** — supersedes the script half of the
  2026-06-09/10 kickoff decision; the single-session kickoff itself stands.
- **JSON layer retired** — amends the 2026-06-09 standard-layout decision
  (layout no longer includes `repo-map.json` / `artifact-manifest.json`);
  the open `governance-lint` queue entry, which depends on repo-map fields
  and discover.py helpers, gets a dated amendment and routes to the owner
  for close-as-obsolete or re-scope.
- **Feedback-via-issues** — supersedes the transport half of the 2026-06-09
  harvest decision (dropbox delivery, `harvest/processed.md` sweep ledger)
  and the 2026-06-22 dropbox/bug-report decisions with their transport
  follow-up; the harvest *discipline* (rare, incident-earned, max three,
  no-report-is-normal, owner-gated publish) is retained verbatim in the
  issue templates.
- **Evals scrapped** — amends the 2026-07-01 condensation decision's
  completeness-general-as-candidate clause (profile deleted with the
  workstream; revival requires a fresh decision from git history); the
  salvaged `docs/harness-capabilities.md` is named as the evidence source
  for the per-harness verify-once gate.
- **Verification's canonical home** (`.agents/repo-guidance.md`); **state
  rotation + write rules**; **the no-rule-without-provenance standing rule**.

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

1. ~~Issues public or private?~~ **Resolved (owner, 2026-07-08): public,
   with the no-PII/sensitive-info redaction rule now in slice 6.**
2. ~~Eval instrument: move or delete?~~ **Resolved (owner, 2026-07-08):
   the entire evals workstream is scrapped — deleted, not archived, with
   one salvage (`harness-capabilities.md` → `docs/`); slice 7 rewritten.**
3. ~~Rollout order?~~ **Resolved (owner, 2026-07-08): vela first** (slice 9
   updated).

## Review log

- r1 (2026-07-08, codex-cli 0.142.5, reviewed_sha `0239cd5`): **reopened**,
  5 findings, all accepted:
  - HIGH: refresh.py's never-touch contract contradicted the first-bootstrap
    delegation — fixed with the explicit division of labor (procedure copies
    approved judgment drafts; script installs shipped set only; one commit).
  - MEDIUM: hook supersession omitted the original 2026-06-21 re-ground
    decision — now amended rather than superseded, because the owner
    (2026-07-08, on reconsideration) kept the compaction re-ground hook as
    the sole shipped hook; slice 3 rewritten accordingly.
  - MEDIUM: the 2026-06-09 harvest decision and the two report templates
    lacked disposition — added to supersessions and slice 6.
  - MEDIUM: the 2026-06-09 layout decision and the open governance-lint
    entry still referenced the JSON layer/discover.py — dispositions added.
  - MEDIUM: the playbook supersession wording wrongly implied retired-list
    semantics replace the deletion-resurrection consequence — corrected: the
    2026-07-03 decision is preserved in full; retired-list adds only
    toolkit-side removal propagation.
  Same revision also introduces the `replace-if-unmodified` class
  (superseding install-if-missing) so provably-unmodified stale artifacts
  update instead of rotting.
- r2 (2026-07-08, codex-cli 0.142.5, reviewed_sha `67f7931`): **reopened**,
  3 findings, all accepted:
  - HIGH: slice 5's drafting set still listed shipped artifacts, leaving two
    installers — fixed: drafts are judgment artifacts only; shipped files
    have exactly one installer (`refresh.py`); the approval summary presents
    both groups; slice 4's drafts-dir wording scoped to match.
  - HIGH: `refresh.py` omitted the gitignore-aware committability rule —
    added: per-path `check-ignore`, the established blanket-`.claude/`
    narrow repair in the same commit, flag-and-skip for unrecognized ignore
    rules, never `git add -f`. With tests.
  - MEDIUM: raw byte-hashes break across the autocrlf fleet — all matching
    and hashes are now specified newline-normalized (the load-bearing
    tolerance the old byte-compare carried), with a CRLF fixture test.
- r3 (2026-07-08, codex-cli 0.142.5, reviewed_sha `3fc6448`): **reopened**,
  1 finding, accepted: refresh.py's auto-commit was incompatible with the
  one-scoped-commit-covering-both-groups bootstrap contract — fixed with a
  `--stage-only` mode (bootstrap: script stages shipped set, procedure
  stages judgment drafts, procedure makes the single commit; standalone:
  script commits as before), dirty-tree refusal explicitly scoped to the
  script's own target paths.
- r4 (2026-07-08, codex-cli 0.142.5, reviewed_sha `ddcec13`): **accepted**,
  zero findings. Commit boundary confirmed unambiguous in both modes; final
  sweep clean.
- r5 (2026-07-08, codex-cli 0.142.5, reviewed_sha `df99fa3`): **reopened**,
  3 findings on the post-r4 delta, all accepted — the decisions-to-record
  hook entry still said "Claude-only" (now states the per-harness
  verify-once gate); a leftover public-vs-private owner question in slice 6
  contradicted the resolved decision (removed); the test list named only the
  `.claude/` blanket-ignore repair (now one case per adapter dir).
- Post-r4 owner amendments (2026-07-08), re-reviewed in r5: (a)
  multi-harness parity — the gitignore repair stated harness-neutrally
  across all adapter dirs; the re-ground hook and operator wrappers ship
  per-harness behind a verify-once gate (codex as important as Claude;
  gemini/antigravity and grok situational); (b) issues public + the
  no-PII/sensitive-info redaction rule in slice 6 and the templates; (c)
  rollout order: vela first (slice 9).
