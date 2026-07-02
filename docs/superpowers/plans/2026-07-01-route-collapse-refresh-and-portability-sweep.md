# Route collapse, `/update-governance` refresh command, reconciliation portability sweep (+ Python floor, fixture fix)

Status: DONE 2026-07-01. Owner picks: W2 = always fetch fresh from the
canonical GitHub URL; W3 = do NOT hand-install the wrapper here — a dogfood
self-application run (which doubles as the end-to-end test) installs it into
this repo through the wrapper guarantee and approval gate; B1 = yes, fix the
`operator:playbook` probe false positive as its own commit within A1.
Landed as: D2 ad7e9e8 · A1 07ceb09 · B1 5120ee4 · A2 a48790d · A3 e6f8316 ·
B 294ad5d · C 7b8a8fc · D1 c7551be. Suite 132/133 throughout — the 1 failure
is the pre-existing `py_vault_twopath` discrimination-gate mismatch (eval
workstream; unhidden by D2; owner decision pending, see `.agents/state.md`).

Bundles four related pieces of work; slices land as separate scoped commits in
the order listed. Slices A and B implement decisions already on record; C and D
are new small work surfaced by owner questions on 2026-07-01.

## A — Implement the 2026-06-28 route-collapse decision

The decision is settled (`update` folds into `migration`; detection was never
load-bearing; `greenfield` stays); this is its deferred implementation.

**A1 — code + tests (`tools/discover.py`, `tests/test_discover.py`):**
- `compute_route()` (discover.py:252): drop the `update` branch and the
  `standard` marker set (`.agents/state.md` / `.agents/bootstrap.config.json`);
  any governance markers → `migration`, none → `greenfield`.
- `compute_agents_template_status()` (discover.py:288-311): populate
  `missingSections` and `reconcileRecommended` on the `migration` route
  (greenfield still drafts fresh, so the probe stays inapplicable there).
  Update docstrings and the guidance line at discover.py:146.
- Tests: rewrite the six `route == "update"` assertions
  (test_discover.py:411,422,588,599,613,659) and any `update`-named test
  methods to the single route; the reconciliation behavior they guard is
  unchanged in substance. Prove the updated tests still bite by temporarily
  restoring the `update` branch (hermetic copy) and confirming failures.

**A2 — procedures, docs, template wording:**
- `procedures/bootstrap.md`: Step 3 loses the `update` bullet; the `migration`
  bullet absorbs the reconciliation branch (when
  `agentsTemplate.reconcileRecommended`, draft the reconciled `AGENTS.md` per
  migration Step 2 discipline before the wrapper/hook guarantees). Reword the
  "update route" references at :9 (self-application lens), :121, :162, :179,
  :205. The dogfood-in-place lens (2026-06-27 decision) is renamed to the
  single route, per the collapse decision's amendment.
- `procedures/migration.md`: absorb the already-canonical case (inventory
  verdicts "leave / already-canonical" + the templateVersion reconciliation as
  a branch of Step 2); reword :50 ("future runs route as `update`").
- `README.md`: drop `bootstrap.config.json` from the documented `.agents/`
  layout (decision scope; nothing ships it).
- `templates/AGENTS.template.md`: reword the write-authority invariant's "the
  update route that reconciles" to name the single route's reconciliation.
  This is a template edit → bump `templateVersion` to the next dotted
  sub-version at implementation date.
- Tests asserting procedure text (e.g. test_discover.py:120 "first reconcile
  the repo's `AGENTS.md`"; :131 "predates the current template") updated in
  lockstep where wording moves.
- Sweep check before commit: `grep -rn "update route\|bootstrap.config.json"`
  across docs/procedures/templates/tools; every hit either reworded or
  justified (history/ is exempt).

**A3 — decisions doc rewording:** the three Open entries that name "the update
route" (monorepo-subdir probe, committed-wrapper staleness, `governance-lint`
recommendation) reworded to the single route, exactly as the 2026-06-28
decision's scope instructs. Mark the collapse decision Adopted with the landing
commit.

## B — Portability sweep inside reconciliation

Implements, for the refresh path, the retroactive cleanup the 2026-06-25
boundary decision deferred: when a run redrafts a target `AGENTS.md` (the
reconciliation branch of the single route), it must also apply the portability
test to every carried-forward line — repo-specific content relocates to
`.agents/` with a pointer left behind, through the same approval summary.

- Edit site: the reconciliation discipline in `procedures/migration.md` Step 2
  (one added instruction), referenced from the bootstrap.md Step 3 branch text
  added in A2. One full statement, pointer from the other site (2026-06-24).
- This is the sanctioned `AGENTS.md` write moment, so it creates no
  write-authority tension; mid-task relocation stays the `drift` operator's
  job.
- Docs-only within `procedures/` (suite still runs; it copies these files).
- The landing decision entry should note it narrows the 2026-06-25 "retroactive
  cleanup" deferral: cleanup now happens on every refresh run; a dedicated
  one-shot cleanup spec is no longer needed for repos that refresh.

## C — `/update-governance` refresh command

A committed wrapper in target repos that triggers the existing manual flow
("sync toolkit, read `procedures/bootstrap.md`, follow it") as one word.

- New `templates/commands/claude/update-governance.md`. Content: a
  one-paragraph instruction — verify the toolkit is reachable
  (`git ls-remote` the canonical GitHub URL; LAN mirror as faster fetch when
  reachable), obtain a current copy (W2), then read its
  `procedures/bootstrap.md` and follow it. Portable: no machine-local path
  baked in; the canonical remote URL is toolkit canon, true in every
  bootstrapped repo. Everything the run does still flows through the normal
  approval gate — the wrapper adds no write authority.
- `procedures/bootstrap.md` "Operator command wrappers": rekey the wrapper set
  from "each operator word" to "each template shipped under
  `templates/commands/<harness>/`", so new wrappers join the standing
  guarantee (2026-06-18) without editing the operator vocabulary.
  `update-governance` is NOT added to `OPERATOR_WORDS` or the AGENTS template's
  operator list — it is a wrapper-only entry point (precedent: `review`), so no
  extra template bump beyond A2's.
- Tests: presence + pointer-shape test for the new wrapper template alongside
  the existing wrapper coverage; mutation-proven hermetically.
- Smoke test (in-session, cheap): execute the wrapper's instructions manually —
  `git ls-remote` the canonical URL, shallow-clone to scratch, confirm
  `procedures/bootstrap.md` is present and current.
- Install into this repo (W3): NOT hand-added. A subsequent dogfood
  self-application run — itself the end-to-end test of the new flow — drafts
  the missing wrapper here via the wrapper guarantee, through the approval
  gate. That run is owner-initiated, outside this plan.

## D — Python floor + fixture fix

- **D1 (docs):** README.md/docs/usage.md state the supported floor: Python 3.9
  (proven: `tools/discover.py` parses and the product suite passes on 3.9).
  Product code stays within the floor. `procedures/bootstrap.md` step 3 probe
  gains one sentence: on macOS, if the probed `python3` is older than the
  floor a task requires, also probe versioned binaries (`python3.14`,
  `python3.13`, …) before declaring Python unusable — Homebrew installs
  versioned names that the current probe order never reaches.
- **D2 (code, one line):** `tests/test_run_fixture.py:19` — replace the PEP 604
  `dict[str, str] | None` annotation with a 3.9-compatible form so the suite
  imports on the floor. Suite goes fully green (47/47) on Python 3.9. This is
  the only currently-known breakage the Homebrew gap causes.

## Ordering and dependencies

D2 (tiny, unblocks a fully-green suite for everything after) → A1 → A2 → A3 →
B (lands in the merged procedure text) → C (wrapper points at the collapsed
procedure) → D1. Each slice is one commit; push policy `always`.

## Verification

- Every slice touching `tools/`, `tests/`, `templates/`, `procedures/`:
  `python3 -m unittest discover -s tests -v` green (fully green once D2 lands).
- Changed/new tests proven to bite via temporary revert on a hermetic copy
  (never the tracked file).
- A2/C include the grep sweep for stale wording before commit.
- C smoke test as described; docs-only slices: `git diff --check`.

## Non-goals

- No fold of `greenfield` into the single route (explicitly out of the
  2026-06-28 decision).
- No new `AGENTS.md` operator word; no harness ports of the wrapper beyond
  Claude Code this pass (other harness command dirs don't exist yet).
- No retroactive relocation of this toolkit repo's own `AGENTS.md`
  repo-specifics (separate owner-gated work, unchanged).
- No chasing newer Python: the floor stays 3.9 until something needs more.

## Open decisions (owner)

- **W2 — wrapper's toolkit acquisition:** always fetch/clone fresh from the
  canonical GitHub URL into scratch (**recommend**: portable, self-healing,
  matches Step 0 freshness-from-git) vs. preferring a human-supplied local
  clone path with clone as fallback.
- **W3 — install the wrapper here too:** add `.claude/commands/update-governance.md`
  to this toolkit repo in slice C (**recommend**: yes — dogfood, one file).
- **B1 — fold the known `operator:playbook` probe false-positive fix**
  (bug filed 2026-06-22: probe seeks `` `playbook` `` but the template writes
  `` `playbook <name>` ``, so it always reports missing) into A1, as its own
  commit touching the same lines (**recommend**: yes, with a test proving the
  probe now matches the template's own wording).
