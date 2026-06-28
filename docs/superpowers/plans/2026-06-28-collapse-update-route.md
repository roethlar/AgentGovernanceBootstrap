# Plan — Collapse the `update` route into `migration`

Implements the 2026-06-28 decision *"Collapse the update route into migration;
route detection is not load-bearing"* (`.agents/decisions.md`). Owner-gated: this
is the durable plan only. No code lands until the owner gives a go on a slice.

## Goal

`compute_route()` stops emitting `update`. One route (`migration`) handles every
repo that already has governance — a foreign system to inventory, an
already-toolkit-bootstrapped repo, or this toolkit's own self/dogfood run.
`greenfield` (a repo with no governance) stays a distinct route. The
`<!-- templateVersion -->` reconciliation of a stale `AGENTS.md` is **retained**,
re-expressed as a conditional branch *inside* the migration route rather than a
route of its own. `bootstrap.config.json` is dropped from the documented layout.

## The load-bearing realization (read before implementing)

The thing being removed is the **route fork**, not the **detection**. The update
route did two jobs:

1. *Detect* that a repo already carries the standard `.agents/` layout
   (`.agents/state.md`), and
2. *Reconcile* its (possibly stale/unstamped) `AGENTS.md` to the current template
   before the wrapper/hook guarantees run.

Job (2) must survive — early toolkit repos have **unstamped** `AGENTS.md` files
that most need reconciling, so the trigger cannot be narrowed to "has a
`templateVersion` stamp." Job (1)'s signal therefore stays, but as a **manifest
field that gates reconciliation**, no longer as a branch in `compute_route()`.

Why this is safe even when the standard-layout signal misfires on a foreign repo
that happens to have its own `.agents/state.md`: post-collapse, "reconcile
`AGENTS.md`" and "migrate `AGENTS.md`" are the *same* approval-gated operation
(both draft a standard `AGENTS.md` carrying the repo's earned rules forward via
`procedures/migration.md` Step 2 discipline). So a former false-positive *route*
becomes a harmless — indeed correct — *step*. This is exactly the decision's
"routes converge at the approval gate, so detection only affected speed" made
concrete, and it is why no provenance marker (`bootstrap.config.json`) is needed.

## Non-goals

- **Do not** add `bootstrap.config.json` or any new provenance marker (the whole
  point; rejected in the decision).
- **Do not** add self/dogfood detection to `compute_route()` (rejected 2026-06-27;
  stays rejected).
- **Do not** collapse `greenfield` — out of scope; not decided.
- **Do not** change the reconciliation *logic* (missing-section probe, stamp
  compare). Only its *gate* moves off the route name.
- **Do not** edit this repo's own `AGENTS.md` (frozen instance; brought current
  only by a later deliberate self-application run, same handling as the
  2026-06-24 / 2026-06-25 decisions). Scope here is the **product** template.

## Verification (every slice)

`python3 -m unittest discover -s tests -v`. The golden fixtures
(`tests/golden/{governance,greenfield}-manifest.json`) keep `migration` /
`greenfield` and need no regen (no `update` golden exists). For any changed or new
test, apply the **revert-the-fix** proof: revert the code change, confirm the test
fails, restore, confirm green. Two guards are mandatory and called out in Slice 1.

## Slices (one item per commit; commit each before the next)

Recommended order is code-first so the prose then describes real behavior. Each
commit is independently green; transient doc drift between slices 1 and 2–3 is
acceptable and tracked here.

### Slice 1 — `tools/discover.py` + `tests/` (the code change)

`tools/discover.py`:

- `compute_route()` — drop the `update` branch entirely:
  ```python
  def compute_route(governance_markers):
      if governance_markers:
          return "migration"
      return "greenfield"
  ```
  Replace the stale "update requires the standard layout" comment with one noting
  that whether a present `AGENTS.md` is reconciled is decided downstream by the
  template-status signal, not by the route.
- `compute_agents_template_status()` — replace the `route` parameter with the
  already-standard signal. Keep the `standard = {".agents/state.md",
  ".agents/bootstrap.config.json"}` membership test as the **reconciliation gate**
  (it is no longer a routing input). Change `if route == "update":` to gate on
  that boolean. The body (prime-block + operator probe, `reconcile = (current !=
  target) or bool(missing)`) is unchanged. Update the one caller (~line 667) to
  pass the boolean instead of `route`.
  - Note: `bootstrap.config.json` stays in the gate `standard` set here even
    though Slice 4 drops it from the *documented* layout — discovery may still
    honor a file a repo happens to carry. The implementer may prune it for
    consistency; either is acceptable and neither changes a test.
- `ROUTE_BLOCKS` — remove the `"update"` key. Fold its reconciliation guidance
  into the `"migration"` block: "If the manifest reports
  `agentsTemplate.reconcileRecommended`, first reconcile `AGENTS.md` to the
  current template per `bootstrap.md` Step 3, then follow `migration.md`."
- `START_HERE_TEMPLATE` — reword line ~113 "bootstrap handoff or update rule" to
  drop "update."

`tests/test_discover.py` — flip route expectations and retarget block-text
assertions:

- `test_standard_layout_routes_update` → rename to `..._routes_migration`; assert
  `route == "migration"` **and** the reconcile signal is still computed for the
  standard-layout repo. **Mandatory guard A**: reverting `compute_route` (restoring
  the `update` branch) must fail this assertion.
- `test_update_route_flags_stale_unstamped_agents`,
  `test_update_route_flags_missing_section_despite_matching_stamp`,
  `test_update_route_reconciles_stale_stamp_when_sections_present`,
  `test_update_route_no_false_positive_when_current` — keep their
  `reconcileRecommended` / `missingSections` expectations exactly; flip the
  asserted `route` from `update` to `migration`. **Mandatory guard B**: on the
  stale-unstamped case, reverting the gate rehoming (back to `route == "update"`)
  must make `reconcileRecommended` go `False` (the route is now `migration`, so the
  old gate would skip computation) and fail the test.
- `test_update_route_has_reconciliation_step` and the
  `assertIn("Step 3, update route", start_here)` assertion (~line 603) — retarget
  to the migration block / "Step 3" reconciliation wording; drop "update route."
- `test_routes` and `test_agents_dir_without_standard_layout_routes_migration`
  need no change (already `migration`/`greenfield`).

### Slice 2 — `procedures/bootstrap.md`

Reconcile every `update`-route reference (grep `update` in the file and resolve
each):

- Dogfood lead-in (~lines 7–9): "in-place run on the `update` route" → "in-place
  run on the `migration` route (this repo carries the `.agents/` layout, so
  discovery flags `agentsTemplate.reconcileRecommended`)."
- Step 2 (~lines 119–123): reword "the update-route reconciliation" to "the
  reconciliation step (Step 3)."
- Step 3 (~lines 130–149): delete the standalone `update ->` bullet; fold its
  reconciliation paragraph into the `migration ->` bullet as a conditional —
  "follow `migration.md`; **if** discovery reports
  `agentsTemplate.reconcileRecommended`, first reconcile `AGENTS.md` to the
  current template [existing reconciliation-discipline paragraph], then proceed."
  Drop the now-redundant "Step 3, update route" self-reference.
- Operator-wrappers (~lines 178–179) and Hook-install (~line 205): "(the update
  route, Step 3)" → "(Step 3, reconcile `AGENTS.md` first)."
- Any "greenfield, migration, update" enumeration (~line 162) → "greenfield,
  migration."

### Slice 3 — `procedures/migration.md`

Confirm the procedure explicitly owns the already-standard / reconcile-first case
(it already states it "handles already-standard repos as a small inventory" and
Step 2 is the reconciliation-discipline home). Add one sentence near Step 1/Step 2
so a reader arriving from the folded Step 3 branch knows that when
`reconcileRecommended` is set, AGENTS.md reconciliation precedes inventory.
Minimal — no new step number.

### Slice 4 — `README.md`

Remove `.agents/bootstrap.config.json` from the documented `.agents/` layout block
(line 42). No other README change.

### Slice 5 — `templates/AGENTS.template.md` (product template)

- Write-authority invariant (~line 100): "the update route that reconciles a stale
  `AGENTS.md`" → "the reconciliation that updates a stale `AGENTS.md` against the
  current template." The "two sanctioned writers" framing stays: a fresh
  bootstrap draft, and the reconciliation.
- Bootstrap Handoff (~line 112): same "update-route reconciliation" → "reconciliation"
  rewording.
- **`templateVersion` checkpoint**: this is prose rewording only — no section,
  invariant bullet, or operator added/removed, and the `missingSections` probe
  (keys on `prime:begin` + operator backticks) is unaffected — so by the bump
  criterion **no `templateVersion` bump is required**. Confirm against the
  criterion before finalizing; bump and reconcile only if the Handoff rewording is
  judged structural. (This repo's own frozen `AGENTS.md` is **not** edited.)

### Slice 6 — `.agents/decisions.md` Open-entry rewording (docs)

Reword the three Open entries that name "the update route" to the single route,
preserving each finding's substance: the monorepo-subdir `package.json` probe, the
committed-wrapper staleness entry ("the update route will not notice" → "the route
will not notice"), and the `governance-lint` entry ("recommended by the update
route's reconciliation step" → "recommended by the route's reconciliation step").
Light touch; the findings still apply to the single route.

## Risks / watch-items

- **Guard B is the subtle one**: if the reconcile gate is left keyed to a value
  that no longer exists (`route == "update"`), reconciliation silently stops
  firing for every already-bootstrapped repo — a silent capability loss. Guard B
  exists to catch exactly that; do not skip it.
- A reviewer may read "collapse" as "delete reconciliation." It is the opposite:
  reconciliation is retained and re-homed. The plan's realization section is the
  reference if that confusion surfaces in review.
- Keep slices 1–6 close together in time so the toolkit's prose and code do not
  describe two different route models for long.
