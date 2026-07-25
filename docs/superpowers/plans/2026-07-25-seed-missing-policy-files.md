# Plan: refresh seeds absent repo-owned policy files

Status: Approved (owner ruling 2026-07-25) — governance refresh creates
`.agents/comms-policy.md` and `.agents/push-policy.md` at their documented
defaults when they are absent, reports each seeding loudly, and never touches
either file again. Implementation may proceed under this ruling; no further
owner decision is open.

## Problem

The two repo-owned policy files are created **only** by the bootstrap
procedure (`procedures/bootstrap.md` Step 4, items 4 and 5). `tools/refresh.py`
never creates them: neither target appears in `tools/shipped-set.json`, and
`classify()` only walks `artifacts[]` and `retired[]`. Refresh reads
`.agents/comms-policy.md` solely to preflight its `<!-- comms-level: N -->`
marker when the file happens to exist (`tools/refresh.py` main preflight
block).

Refresh nevertheless installs artifacts that point at both files:

- `templates/AGENTS.template.md` line 9 → `.agents/push-policy.md`
- `templates/AGENTS.template.md` line 83 → `.agents/comms-policy.md`
- `templates/playbooks/plan.md` line 15 → `.agents/comms-policy.md`
- `templates/playbooks/handoff.md` line 20 → `.agents/push-policy.md`

A repo governed before those files existed (push-policy 2026-06-27,
comms-policy 2026-07-22) that has only ever been refreshed since therefore
carries installed governance whose pointers resolve to nothing, permanently.

The hygiene lint cannot surface it: `lint_governance()` deliberately excludes
`AGENTS.md` ("references are template-intentional") and globs only top-level
`.agents/*.md`, so `.agents/playbooks/` is out of scope too.

## Design

Add a third top-level manifest section, `seeded[]`, alongside `artifacts[]`
and `retired[]`.

Semantics — deliberately narrower than any existing class:

- Target absent → install the source template verbatim, exactly like an
  `install`, and emit one owner-facing ACTION line naming the follow-up.
- Target present → refresh ignores it completely. No hash comparison, no
  `formerly[]`, no update, no restore, no drift report, no removal, and no
  `current` entry. Owner edits are invisible to refresh by construction, so
  the "repo-owned files are never touched" contract in the module docstring
  holds with exactly one exception: creation from nothing.

Seeded entries reuse `plan.install`, so the record/apply/commit path is
unchanged: `build_record()`, `verify_record()`, `check_committability()`,
`assert_safe_dest()`, `apply_plan()`, `stage()`, `touched_paths()` and the
staged-set and committed-set crash checks all cover them with no edit. The
seeded-vs-installed distinction is presentation only and stays out of the
record, so the plan record schema does not change.

Accepted consequences:

- The seeded value is a default, not an owner answer. Both defaults are the
  conservative ones — push policy `ask`, comms level 3 — and the prior state
  was no policy file at all, so nothing loosens. Bootstrap still asks the
  owner; seeding never pre-fills an answer bootstrap would have asked for,
  because seeding only ever fires where bootstrap already did not run.
- A deliberately deleted policy file is re-created on the next refresh. This
  is intended: the installed artifacts reference it unconditionally.

## Implementation

Land as one commit per step, in this order.

### Step 1 — `tools/shipped-set.json`

Add the `seeded` section:

```json
"seeded": [
  {
    "source": "templates/comms-policy.template.md",
    "target": ".agents/comms-policy.md",
    "action": "seeded at the default (level 3 - normal). Set this repo's level by editing the marker line; refresh never touches this file again."
  },
  {
    "source": "templates/push-policy.template.md",
    "target": ".agents/push-policy.md",
    "action": "seeded at the default (ask before pushing). Change it in that file if this repo should push without asking; refresh never touches this file again."
  }
]
```

Extend the manifest `comment` field to define the class: seeded = install if
absent, otherwise ignored entirely; no `formerly[]`, no drift, no removal;
these are bootstrap-seeded repo-owned files and refresh only backfills the
ones a pre-existing governed repo never received.

The `action` text lives in the manifest, not in `refresh.py`: the tool stays
free of per-file knowledge.

### Step 2 — `tools/refresh.py`

1. `Plan.__init__`: add `self.seeded = []  # target - installed because absent`.
2. `validate_manifest()`: walk `shipped.get("seeded", [])` after the retired
   loop. Run `check_rel` on `source` and `target`, fold the target into the
   same `seen` duplicate-set the artifacts and retired loops share (a target
   in two sections must fail before any write), and error when the source
   file is missing. Seeded entries carry no `class` key — do not run the
   `_KNOWN_CLASSES` check against them. Leave `_KNOWN_CLASSES` alone.
3. `classify()`: after the artifacts loop and before the retired loop:

   ```python
   for s in shipped.get("seeded", []):
       if (target_repo / s["target"]).exists():
           continue
       plan.install.append((s["target"], toolkit / s["source"]))
       plan.seeded.append(s["target"])
   ```

4. `summarize()`: in the `installed` loop, print seeded targets as
   `  seeded: <target>` instead of `  installed: <target>`, keyed off
   `set(plan.seeded)`. This is the commit-message wording.
5. `terse_line()`: add a `"{n} seeded"` part when `plan.seeded` is non-empty,
   and subtract seeded targets from the `installed` count so the two do not
   double-count the same paths.
6. `main()`: after the `terse_line()` print and before the lint findings,
   emit one line per seeded target:
   `  ACTION: <target> <action-text-from-manifest>`. This is a deliberate,
   bounded exception to the one-line result rule (2026-07-23 owner-surface
   D3): the D3 rationale covers per-item *detail*, and these lines are a
   follow-up the owner must act on, fired only in the run that seeds.
   Resolve the action text from the manifest, defaulting to a bare
   "seeded (repo-owned from now on)" when an entry omits `action`.
7. Module docstring: amend the repo-owned paragraph so the exception is
   recorded — refresh may create an absent seeded policy file, and never
   touches one that exists.

No change to the comms-marker preflight: it already guards on `exists()`, and
a freshly seeded file carries a well-formed marker by construction.

### Step 3 — tests (`tests/test_refresh.py`)

The fixture toolkit is hermetic (`make_toolkit`), so add a fixture template
and a `seeded` section to its mini manifest rather than reaching for the real
one. Cases:

1. Absent target is seeded: after refresh the file exists with the template's
   bytes, stdout carries the ACTION line and the `seeded` count, the commit
   message says `seeded:` (not `installed:`), and the path is in the refresh
   commit.
2. Present target is inert: write an owner-modified policy file, commit,
   refresh — bytes unchanged, no update/restore/removal/drift for that path,
   and the terse line reports no seeding. A second refresh is a no-op.
3. `--plan-json` lists the seeded target under `installs`, and a subsequent
   `--apply` of that record succeeds (record round-trip unbroken).
4. `validate_manifest()` rejects a seeded entry whose source is missing, whose
   target is absolute or traverses upward, and whose target duplicates an
   `artifacts[]` or `retired[]` target.

Guard proof (per the Verification section of `AGENTS.md`): temporarily revert
the `classify()` hunk from Step 2, confirm cases 1 and 3 fail, restore, confirm
the suite is green. Mutate a throwaway copy, never the tracked file.

### Step 4 — docs and record

- `docs/design.md`: the refresh section describes the shipped-set classes;
  add `seeded` with its one-line semantics.
- `docs/usage.md`: note that a repo governed before the policy files existed
  gets them backfilled at defaults on its next refresh, with the ACTION line
  telling the owner what to set.
- `.agents/decisions.md`: record the 2026-07-25 ruling — installed artifacts
  reference repo-owned policy files unconditionally, so refresh backfills an
  absent one at its documented default and reports it; a present one stays
  untouched. Cite this plan.
- `procedures/bootstrap.md`: unchanged. Bootstrap still asks the owner for
  both values and never pre-fills.

## Verification

`<probed-python> -m unittest discover -s tests -v` (interpreter per
`.agents/repo-guidance.md` Verification and `.agents/machines.md`). The plan
lint rides the same suite.

## Out of scope

- `--lint-only` stays blind to a missing policy file: it is read-only and
  returns before `classify()`, and the next applying refresh fixes the
  condition anyway. Widening `lint_governance()` to `AGENTS.md` or to
  `.agents/playbooks/` is a separate question and is not opened here.
- No new owner prompt. Seeding never asks; bootstrap remains the only surface
  that asks for these two values.
