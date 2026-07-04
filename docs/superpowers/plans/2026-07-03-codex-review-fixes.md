# Fix the four valid findings from the 2026-07-03 codex review

Status: DRAFT 2026-07-03, awaiting owner go. Source: independent codex review
(codex-cli 0.142.5, headless, read-only) over the day's diff
`ba4e23f..ed7e3ad`; all four findings verified against the files before
planning. A grep sweep for stale wording (`optional playbook`, `scope tier
justif*`, `not a default bootstrap output`, `first one installed`) across
active files found no sites beyond those codex named.

## Findings and fixes, one commit each

### F1 — `docs/design.md` contradicts itself twice (drift introduced today)

- `docs/design.md:169`: Tier 1 says "Prefer `AGENTS.md`, `.agents/state.md`,
  decisions, repo map, and artifact manifest **only**", excluding playbooks,
  ten lines above ":179 Shipped playbook templates are part of the standard
  drafted set at every tier."
- `docs/design.md:222`: "Multi-agent review workflows … are not a default
  bootstrap output" — but the shipped default playbook `reviewloop.md` is a
  two-agent review workflow.

Fix: reword both to the current design, plainly (no correction-shaped
emphasis, per the 2026-07-03 wording lesson). Tier 1 lists what Tier 1
*adds* beyond the standard drafted set (nothing), rather than enumerating a
set that omits playbooks. The :222 paragraph keeps its load-bearing
principles (one accountable coding owner; reviewer output is evidence until
accepted) attached to the review workflow that does ship, dropping the
"not a default output" claim. Exact wording at edit time, reading the full
surrounding section first.

### F2 — the active-baseline migration spec still tier-gates playbooks

`docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md:171`
ends the standard draft set with "playbooks as the scope tier justifies".
`.agents/repo-guidance.md` Reading Order names this spec as active baseline,
so it is live drift.

Fix: amend the clause in place to match canon, with a dated provenance note
(the pattern used elsewhere in the repo for amended-in-place text), e.g.:
"…, and every shipped playbook (amended 2026-07-03 per the playbooks
decision in `.agents/decisions.md`; originally 'as the scope tier
justifies')." No other edits to the dated spec.

### F3 — two stale statements in Active `.agents/decisions.md` entries

- `:556` (2026-06-09 layout decision): "… artifact-manifest.json, optional
  playbooks)". Amend the Status line to the repo's as-amended pattern
  ("Status: Active, as amended 2026-07-03: playbooks are part of the
  standard layout — see the 2026-07-03 playbooks decision") and leave the
  original decision text intact below it.
- `:1052` (Open `governance-lint` item): "…and the first one installed into
  this repo" — no longer follows, since `reviewloop.md` installs on any
  refresh/dogfood run. Reword that factual clause with a dated parenthetical;
  the item's substance (the checker design, the owner's 2026-06-22 option-(a)
  pick) is untouched.

The match at `.agents/decisions.md:57` is the new decision's own supersession
explanation — provenance, not drift; no change.

### F4 — `tests/_pyshim.py` probe doesn't survive a hung `python3`

`_python3_works()` passes `timeout=30` but catches only `OSError`
(`tests/_pyshim.py:24-30`); a hanging `python3` raises
`subprocess.TimeoutExpired`, which escapes `setUpModule` and errors the whole
module instead of installing the shim.

Fix: `except (OSError, subprocess.TimeoutExpired): return False`. Ship with
a unit test (new `tests/test_pyshim.py`): monkeypatch `subprocess.run` to
raise `TimeoutExpired` and assert `_python3_works()` returns `False`; second
case raising `OSError` for parity. Guard proof per the Verification
invariant: revert the `except` change, confirm the new test fails
(`TimeoutExpired` propagates), restore, confirm green.

## Out of scope

Archived/history files (verbatim-preservation rule); the codex "No Findings"
categories; anything not in the four findings.

## Verification

`py -3 -m unittest discover -s tests -v` (Windows host, per
`.agents/repo-guidance.md`) after F4 and at the end; `git diff --check` for
the docs-only commits; the F4 revert-the-fix guard proof.

## Commits

1. this plan.
2. F1 (`docs/design.md`).
3. F2 (spec amendment).
4. F3 (`.agents/decisions.md`, both entries — one drift item across one file).
5. F4 (`tests/_pyshim.py` + `tests/test_pyshim.py`).
