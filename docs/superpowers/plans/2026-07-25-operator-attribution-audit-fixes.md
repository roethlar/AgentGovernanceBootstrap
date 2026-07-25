# Plan: fix the operator-attribution and stale-doc findings

Status: CLOSED 2026-07-25 — findings 1, 2, 3, and 5 remediated as specified.
Finding 4 (`new-project` presentation) was deliberately excluded and remains
open: it needs an owner judgment that has not been made.

Commit map:

- `a37e145` — Step 1, `templates/state.template.md` repointed at `catchup`
  (both the rotation sentence and the parked-item re-verification line).
- `a04b45f` — Step 2, `.agents/state.md` header repointed at `catchup`.
- `6718107` — Step 3, duplicated bullet dropped; the superseded audit entry
  rotated verbatim to `docs/history/state-archive.md`.
- `6b7cbbd` — Step 4, `README.md`: retired `GEMINI.md` shim dropped,
  `comms-policy.md` added to the `.agents/` enumeration.
- Step 5 — the two empty directories were removed from the working tree.
  No commit: both were untracked, so git records nothing.

Verification at close: suite 175 green, `refresh --lint-only` clean,
`git diff --check` clean. The plan lint initially failed this document for
naming the two directories Step 5 deleted; both references now carry a
same-line `plan-lint: allow` marker with its reason, since the plan is the
record of what was removed.

## Findings and evidence

The authoritative definitions are the two playbooks:
`.agents/playbooks/handoff.md` line 24 ("No archive rotation, no
re-verification sweep, no mandatory re-anchoring of volatile facts — that
hygiene belongs to `catchup`") and `.agents/playbooks/catchup.md` lines
19-31 (rotation, parked-item re-verification, volatile-fact re-anchoring,
machines.md pruning). `AGENTS.md` agrees: the state-hygiene sweep rides
`catchup`; `handoff` is the fast snapshot. The `drift` operator was retired
2026-07-23 (owner-surface D4) and its sweep moved to `catchup`.

1. **Operator attribution.** Three surfaces name the wrong operator for
   that sweep:
   - `.agents/state.md` line 5 — "At each `handoff`, rotate landed or
     superseded entries verbatim to `docs/history/state-archive.md`".
   - `templates/state.template.md` lines 4-5 — "the `drift` operator's
     hygiene pass rotates landed or superseded entries", naming an operator
     retired 2026-07-23. This template drafts `.agents/state.md` at
     bootstrap, so every new repo inherits the dead reference.
   - `templates/state.template.md` line 26 — "Re-verify each parked item's
     recorded basis at every handoff", which the handoff playbook
     explicitly disclaims.
2. **Stale content in `.agents/state.md`.** Lines 32-33 are the same bullet
   opener twice (copy-paste artifact). A live "In flight" entry says the
   decisions-as-claims audit's "queued fixes F4+ await per-item owner go",
   contradicted by the CLOSED entry above it and by
   `docs/superpowers/plans/2026-07-23-audit-findings.md`
   (`Status: COMPLETE 2026-07-23 — every Fix Queue item is resolved`,
   F4-F13 each with a landing commit).
3. **`README.md` describes a retired shape.** Line 19 lists `GEMINI.md`
   among shipped harness shims; it was retired 2026-07-22 and now sits in
   the manifest's retired list, so refresh removes it from governed repos.
   Lines 13-17 enumerate `.agents/` without `comms-policy.md`, a peer of
   `push-policy.md` since 2026-07-22.
5. **Leftover directories.** `.agents/skills/drift/` <!-- plan-lint: allow (removed by Step 5 of this plan; named as the record of what was removed) --> and
   `.agents/skills/harness-update/` <!-- plan-lint: allow (removed by Step 5 of this plan; named as the record of what was removed) --> exist and are empty: `apply_plan()`
   unlinks a retired target but never prunes the emptied parent, so an
   agent listing `.agents/skills/` sees skills that do not exist. Both are
   untracked, so git cannot surface them.

## Implementation

One commit per finding, in this order.

### Step 1 — `templates/state.template.md`

Repoint both sentences at `catchup`. Not a shipped artifact source (only
`templates/AGENTS.template.md` is), so the manifest MAINTENANCE RULE and
`formerly[]` do not apply — verified against `tools/shipped-set.json`.
Keep the wording generic and portable: name the operator, not this repo's
history.

### Step 2 — `.agents/state.md` header

Same repoint, plus the file's own stated purpose. Repo-owned, so edited in
place.

### Step 3 — `.agents/state.md` content

Delete the duplicated bullet opener at line 32. Rotate the stale "In
flight" audit entry verbatim to `docs/history/state-archive.md` under a
new `## Rotated 2026-07-25` heading, per the rotation rule the same file
carries — the CLOSED entry above it already holds the live truth, so no
information is lost.

### Step 4 — `README.md`

Drop `GEMINI.md` from the shim list (keep `CLAUDE.md`, which still ships)
and add `comms-policy.md` to the `.agents/` enumeration beside
`push-policy.md`.

### Step 5 — leftover directories

Remove the two empty directories locally. Both are verified empty and
untracked; nothing in git changes. The systemic half — teaching
`apply_plan()` to prune a directory it just emptied — is NOT in scope here
and is raised to the owner separately, since it changes refresh behavior
fleet-wide.

## Verification

`<probed-python> -m unittest discover -s tests -v` (interpreter per
`.agents/repo-guidance.md`), which covers `tests/test_templates.py` and the
plan lint. Docs-only steps additionally run `git diff --check`, and
`tools/refresh.py . --lint-only` confirms `.agents/` hygiene stays clean.

## Out of scope

- Finding 4: how `new-project` is presented in `docs/usage.md` and the
  `toolkit` verb list. It is a shell installer, not a slash command, and
  how to say so is an owner call.
- Pruning emptied directories inside `tools/refresh.py` (see Step 5).
