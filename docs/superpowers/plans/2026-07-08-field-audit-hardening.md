# Field-audit hardening: state lifecycle, write rules, and toolkit correctness

Status: Draft 2026-07-08 — under cross-harness review (reviewloop, codex), then
owner approval. No product change lands before the owner approves this plan.

## Why this plan exists

On 2026-07-08 the owner commissioned an effectiveness audit of the toolkit's five
main deployments — `Blit_v2`, `vela`, `Powershell-Token-Killer` (PTK),
`ai-rpg-engine`, and `ExchangeAdminWeb` (EAW), all siblings under the same dev
root. Each repo's full governance set was inventoried, its state claims verified
against code and git history, and its usage traced through commit history. The
evidence lives in those repos' histories (anchors cited below), so every claim
here is independently re-checkable.

**The core loop works.** In all five repos, handoffs were demonstrably resumed
across sessions (EAW: a phase named in a 2026-06-18 handoff landed as specified
six days later, `49e3010`; ai-rpg-engine: review findings queued in state.md on
2026-06-11 were closed 22 days later, `a3f60f2`; PTK: a cross-machine handoff
checklist written on a Mac was executed item-by-item on Windows four days later,
`9ec73fe` → `180da71`). Decisions were honored, including reversals (PTK: an
owner pause decision gated all code commits for a day, `af96cdf` → `48a7a66`;
vela: a feature drop + partial reversal implemented exactly as scoped). The
reviewloop playbook caught real pre-ship bugs (vela `eh-10`, `eh-5`, `sspf-13`).
Spot-checked state claims came back overwhelmingly true, several to the line
number. This plan changes none of that machinery.

**The failures are consistent and concentrated where no operator owns the
artifact or no write rule exists.** Six patterns recurred across the fleet:

1. **state.md has no lifecycle.** The template says "keep it short" and ships no
   pruning mechanism (decisions.md gets a verbatim-archive rule,
   `templates/decisions.template.md:9-11`; state.md gets nothing). Field result:
   PTK state.md hit 537 lines in 12 days; EAW's 457 lines carry live
   self-contradictions ("no protected-principal gaps remain" at state.md:313
   beside "GAP 3 OPEN" at :351); vela's grew 50 → 578 lines in five days with
   three generations of "current" markers.
2. **Volatile predicates are written as durable state and rot in days.** Push
   status, CI color, working-tree notes: vela's pervasive "UNPUSHED" annotations
   and its CI paragraph were false within days (CI was red on ten consecutive
   pushes, `05f9594`..`8483615`, while the recorded rationale said CI "hasn't
   seen" the work); ai-rpg-engine and EAW recorded push posture that the next
   push falsified. All of it is derivable live from git/CI.
3. **Duplicated counts diverge, every time.** PTK repo-guidance said 43/29 tests
   vs the canonical 70/37; EAW carried 21 vs 22 modules and Migration 1.3.0 vs
   1.3.2; ai-rpg-engine's handoff wrote "nine decisions dated 2026-07-03" when
   the file contains six. The one-canonical-location invariant exists; nothing
   enforces it at write time.
4. **Machine-local facts recorded as repo truth.** Blit_v2's remotes doc was
   "drift-fixed" twice in one day to opposite configurations (`60b9d67` →
   `3d8326b`), each session verifying against its own machine and declaring the
   other's naming "never matched"; PTK's "one remote is configured" is false on
   the second box; vela/ai-rpg-engine record wrong or missing remote hostnames.
   The owner's fleet is multi-machine; the toolkit has no concept of a
   machine-scoped fact.
5. **"Repo is memory" silently breaks across clones.** The audited ai-rpg-engine
   clone was 75 commits behind its own remotes; Blit_v2's clone was behind
   GitHub canon (`b187b56` absent locally). Nothing in Session Startup checks
   clone freshness before trusting state.md.
6. **The JSON layer rots while prose thrives.** EAW's repo-map.json froze at
   install and records bare `dotnet test` — the exact vacuous form its own
   AGENTS.md warns against; vela's says "six scenarios" vs 11 on disk;
   ai-rpg-engine's missed an entire 75-commit window. No operator touches these
   files between refreshes.

A separate product audit the same day found toolkit-side correctness defects
(drafting holes, dangling references, stale docs, dead code) and owner-machine
constants shipped in portable files. Those are slices 6–7.

Cost note: governance-only commits ranged 16%–48% of post-install history.
Slices 1–2 attack this directly — most of the bookkeeping weight *is* the
volatile, duplicated, never-rotated content.

## Design principles

- Every new rule below is earned by at least two independent field incidents
  (cited above). No rule is added on taste; the invariant set grows only where
  the ledger demands it.
- Prefer mechanism and template structure over new prose invariants. Where a
  rule must be prose, it lands in the narrowest home that reaches the behavior
  (an operator definition or a template comment, not a new Universal Invariant).
- One `templateVersion` bump (`2026-07-08.1`) covers all template changes in
  slices 1–5, so the fleet reconciles once. Each slice is still its own commit.

## Slices

### Slice 1 — state.md lifecycle (rotation)

- `templates/state.template.md`: header gains the same mechanic decisions.md
  already ships — `## Now` holds only live entries; when an entry is landed or
  superseded, the `handoff` that retires it moves it **verbatim** to
  `docs/history/state-archive.md` (create on first use), never summarized,
  never left as a stub.
- `templates/AGENTS.template.md` `handoff` operator: "update `.agents/state.md`
  so the next session can resume without chat context" gains a pruning clause:
  rotate landed/superseded entries to the archive; Now/Next/Blockers carry only
  live items.
- Tests: presence guards for the new template text (same style as existing
  template tests), guard-proven per the Verification invariant.

### Slice 2 — write rules for state content

Added to `templates/state.template.md` header comments and enforced by the
`handoff` operator wording (one clause each, not new invariants):

- **Volatile predicates** (push status, CI color, test counts, working-tree
  notes) are recorded only with an `as of <commit>` stamp and re-verified or
  dropped at each handoff; prefer omitting what git/CI answers live.
- **No second copy of a count or enumeration another file owns** — write the
  pointer instead. (The Universal Invariant already says this; the handoff
  operator now names it as a check performed at write time.)
- **Machine-scoped facts** (local remote *names*, local toolchain, per-clone
  push posture) are either labeled `machine-local (<host>)` or not recorded;
  durable remote facts are recorded as URL + role, never as a local alias name.

### Slice 3 — clone-freshness check in Session Startup

`templates/AGENTS.template.md` Session Startup gains one step: before trusting
`.agents/state.md`, compare the clone against its canonical remote
(`git fetch --dry-run` / `git ls-remote` + local ref compare); if the clone is
behind or diverged, say so and treat state.md as potentially stale. Kept to one
sentence — this is the cheapest fix for failure pattern 5.

### Slice 4 — one home for verification; staleness tripwire for the JSON layer

- **Canonical home for the verification command becomes
  `.agents/repo-guidance.md` (Verification section)** — the prose file agents
  demonstrably maintain and auto-import. `templates/state.template.md`
  Verification section becomes a pointer; `templates/repo-map.template.json`
  keeps operational metadata but its verification block points at
  repo-guidance rather than duplicating command strings;
  `templates/AGENTS.template.md` Verification first line names repo-guidance
  (currently `repo-map.json`). Procedures that tell the drafting agent where to
  record the command are updated to match.
- **Staleness tripwire:** the `handoff` operator gains a clause — if
  `repo-map.json`/`artifact-manifest.json` `validated_against` predates the
  work being handed off and that work changed the tree's shape (new/removed
  fact-bearing paths), either refresh the file or record the staleness in
  `## Next`. This gives the JSON layer an owner without a new operator.

### Slice 5 — parked-blocker re-verification

`handoff` operator: for each item recorded as parked/blocked, re-verify that
its recorded factual basis still holds (the vela failure: a parked "CI red on
last pushed commit" rationale stayed recorded while CI failed ten more pushes);
a falsified basis moves the item into `## Blockers` with the new evidence.

### Slice 6 — toolkit correctness defects (one commit each)

6a. Draft-set holes: add `.agents/push-policy.md` to the drafted set on both
    routes (`procedures/bootstrap.md` greenfield list, `procedures/migration.md`
    drafted set) and to `templates/approval-summary.template.md`'s Committed
    list; add `.agents/repo-guidance.md` to that Committed list; fix
    `procedures/migration.md:94`'s dangling "bootstrap.md Step 4" reference.
6b. Doc drift: `docs/usage.md` routes section (two routes, not three);
    canonical-remote wording aligned across README/usage (GitHub canonical,
    gitea a mirror); README broken spec link (`superpowers/...` →
    `docs/superpowers/...`); README/design.md drafted-set lists gain
    `repo-guidance.md`.
6c. START-HERE precedence: `tools/discover.py` START-HERE text gains the
    reconcile carve-out (a resident AGENTS.md handoff rule wins *unless*
    `reconcileRecommended` is set — currently stated unconditionally, opposite
    of `procedures/bootstrap.md:126-129`). With test.
6d. `byteIdentical` honesty: `tools/manifest-schema.md` (and any "exact bytes"
    wording) corrected to state the compare is newline-normalized by design —
    the tolerance is load-bearing across autocrlf checkouts. Behavior unchanged.
6e. Dead code: remove `run_git` (zero call sites) and the no-op
    `--coverage-cap` flag; fix the CI branch-trigger heuristic conflating
    `push` and `pull_request` branch filters (PR-only workflows are currently
    false-flagged "likely inactive"). With tests.

### Slice 7 — portability: owner constants out of shipped files

- `templates/commands/claude/update-governance.md`: the toolkit URL becomes a
  draft-time placeholder filled from the origin the bootstrap run actually
  synced from (recorded in `tools/bootstrap-origin.json`), so target repos stop
  committing the owner's GitHub username.
- `procedures/file-to-dropbox.md`: the dropbox slug (`roethlar/agent-harvest`)
  moves into `harvest.config.json` (which already carries the local path); the
  procedure reads it from there and treats a missing config as "no dropbox —
  use the in-repo fallback".
- `procedures/bootstrap.md` Step 0 / `docs/usage.md`: the LAN gitea URL and
  `~/dev` defaults are marked owner-local examples or moved to an owner-local
  note; the GitHub URL stays (it is the toolkit's real canonical remote).

### Slice 8 — repo hygiene: eval instrument out of the product loop

Move `tools/run_fixture.py`, `tools/drivers.py`, `tools/polyglot_fixture.py`,
and `tests/test_run_fixture.py` under `evals/` (with its own `tests/`); the
product verification command keeps running `tests/` (now `test_discover.py` +
`test_pyshim.py` only). `.agents/repo-guidance.md` verification wording updated
here accordingly. No behavior change to either suite.

## Verification

- Slices 1–6c, 6e, 8: `py -3 -m unittest discover -s tests -v` (Git Bash) green
  before each commit claim; every new test guard-proven (revert → fail →
  restore → pass).
- Slices 6b, 6d, 7 (docs/procedures): `git diff --check`; plus a manual
  read-through of each changed procedure step in sequence.
- Template slices: the shipped template's self-report stays zero missing
  sections (existing test), stamp bumped once to `2026-07-08.1`.

## Out of scope

- The 2026-07-03 unconditional-playbook-install decision is **not** reopened
  here, though the field audit recorded one conflict case (Blit_v2's reviewloop
  vs its no-branches policy, predicted by its repo-guidance). Listed under Open
  questions for the owner; any change is a fresh owner decision.
- No new Universal Invariants. All slice-1/2/3/5 rules land in operator
  definitions and template headers.
- No changes to the reviewloop playbook, hooks, or the harvest/bug-report
  transports beyond slice 7's config extraction.

## Open questions for the owner

1. Slice 4 makes `repo-guidance.md` the verification command's canonical home.
   Acceptable, or keep `repo-map.json` and give it the upkeep trigger instead?
2. Slice 7 keeps the GitHub toolkit URL in `procedures/bootstrap.md` as genuine
   canon. Confirm, or should even that be config-derived?
3. The Blit_v2 playbook-conflict case: leave the 2026-07-03 decision as is, or
   take up an "adapt-or-flag on recorded conflict" amendment as a separate
   decision?

## Review log

- r1 (2026-07-08, codex): pending.
