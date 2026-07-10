# handoff operator: fast snapshot split + machine-local state relocation

Status: APPROVED 2026-07-10 — owner ruling, verbatim: "New tracked file
`.agents/machines.md` — machine-specific facts live there under a heading
per machine, dated. `handoff` writes machine facts only there; the main
state file stays portable and may point to it. `drift` prunes stale
entries. No hidden files, nothing lost on reclone." (Owner reply:
"approved"; the owner proposed the tracked keyed file over both an
untracked local file and omit-only.) The handoff/drift split was
owner-settled 2026-07-09 (decisions log). Implementation awaits an
explicit owner go.

## Why this plan exists

Two settled-in-intent inputs converge on the same template bullet:

1. **The 2026-07-09 Open decision** (`.agents/decisions.md`, "`handoff` is a
   fast save-my-place snapshot; the doc-cleanup pass moves to `drift`"):
   owner-settled in intent, implementation deferred to a plan because the
   template + skill rewrite is a product change with fleet-wide blast
   radius. This is that plan.
2. **GitHub issue #2** (filed 2026-07-09, evidence from vela): the same
   handoff bullet says machine-local facts in tracked `.agents/state.md`
   are "labeled `machine-local (<host>)` or omitted", while
   `templates/playbooks/reviewloop.md:110-115` establishes gitignored
   `*.local.*` files as the correct home for exactly that class of fact
   (consistent with `settings.local.json` treatment). Agents follow the
   bullet because it names the file they are editing, and tracked
   machine-local blocks grow refresh over refresh. Downstream repos cannot
   self-correct — `AGENTS.md` is refresh-owned — so the reconciliation can
   only happen here.

One plan because both changes rewrite the same operator bullet in
`templates/AGENTS.template.md`; shipping them separately would churn the
fleet's `AGENTS.md` twice.

## Design

**`handoff` (fast).** The bullet keeps only: update `## Now` / `## Next` (and
`## Blockers` if something is live) so the next session resumes without chat
context — in-flight work, next action, stop. Seconds, not minutes. No
archive rotation, no re-verification sweep, no mandatory re-anchoring of
volatile facts. Machine-specific facts (CLI paths, local tool versions,
host layout) go to the TRACKED file `.agents/machines.md`, under a heading
per machine (stable host key, e.g. hostname), each fact dated — never into
`.agents/state.md`, which stays portable and may carry at most a pointer
to `.agents/machines.md`. Created on first use, like the history archives.

**`drift` (deliberate).** The bullet absorbs the hygiene rules verbatim from
the current handoff bullet, per the decision entry: rotate landed/superseded
`## Now` entries verbatim to `docs/history/state-archive.md`; re-verify the
recorded basis of parked/blocked items and move falsified ones to
`## Blockers` with new evidence; re-anchor or drop volatile `as of <commit>`
facts; reduce copied counts/enumerations to pointers; and (per the
2026-07-10 ruling) relocate machine-specific facts found in tracked state
to `.agents/machines.md` and prune stale entries there.

**Why tracked-and-keyed (issue #2's fix, owner design 2026-07-10).** The
vela failure was unkeyed machine facts polluting the portable state file,
not trackedness itself; an untracked local file dies on every reclone and
reboot-cleaned temp path. A tracked per-machine-keyed file is durable,
visible in history, works across all the owner's machines, and needs no
gitignore machinery. `tools/refresh.py`'s `LINT_EXEMPT_PATHS` gains
`.agents/machines.md` (a designated create-on-first-use home, same class
as the history archives, so fresh repos do not lint it as a dead
reference). The reviewloop's `harnesses.local.json` probe cache is
unaffected — it is a regenerable self-authored cache, not durable memory.

## Implementation surface

From the decision entry plus issue #2, verified against the shipped set:

- `templates/AGENTS.template.md` — both operator bullets (handoff line 55,
  drift line 56).
- `templates/skills/shared/handoff/SKILL.md`,
  `templates/skills/shared/drift/SKILL.md` — description frontmatter and
  body track the new split.
- `templates/commands/claude/handoff.md`, `templates/commands/claude/drift.md`
  — wrapper prose.
- `templates/approval-summary.template.md` — push-policy option 2 names
  handoff as an operator (no scope assumption found; re-check during the
  slice).
- `procedures/bootstrap.md` Step 4.2 — the state-draft write rules restate
  "machine-local facts labeled or omitted" and must adopt the
  `.agents/machines.md` wording (create on first use; no bootstrap draft).
- The state template under `templates/` (write-rules preamble) — same
  rewording.
- `tools/refresh.py` — add `.agents/machines.md` to `LINT_EXEMPT_PATHS`
  (create-on-first-use home; small code change, suite-covered).
- `docs/design.md:33` — cited by issue #2; verify and align during the
  slice.
- This repo's own `AGENTS.md`, skills, and wrappers — via self-refresh, never
  hand-edited.

## Slices

1. **Template + procedure rewording** (all files above), then self-refresh
   this repo and verify the installed copies match. Structural template
   tests updated where they assert operator wording.
2. **Bookkeeping**: move the 2026-07-09 decision entry to Adopted with the
   landing commit; note issue #2 for closing (owner files the close or an
   explicit go authorizes `gh issue close`); rotate any affected state
   entries.

## Verification

`python3 -m unittest discover -s tests -v` (template structural tests and
the refresh lint exemption ride the suite). Bite proof per issue #2, run
manually after self-refresh: a `handoff` performed with a machine-specific
fact in hand yields zero machine-specific content in `.agents/state.md`
(grep clean) and the fact in `.agents/machines.md` under this machine's
heading, dated. Grep the whole template set for `machine-local` to prove
one canonical rule remains.

## Non-goals and risks

- No new operator vocabulary (owner rejected a `tidy`/`prune` operator,
  2026-07-09); the hygiene rules move homes, they are not deleted or
  weakened.
- No gitignore machinery at all (the 2026-07-10 ruling made the file
  tracked); no untracked `*.local.*` state file ships.
- Fleet-wide wording change: every governed repo's next refresh replaces
  `AGENTS.md`. Repos mid-session during the swap see the old wording until
  their next refresh — acceptable, versions are individually coherent.
- vela's existing tracked machine-local block is downstream cleanup for that
  repo's next drift pass, not this plan's scope.

Provenance: owner direction 2026-07-09 recorded in `.agents/decisions.md`
(Open entry, quoted wording targets); GitHub issue #2 (2026-07-09, vela
evidence); owner instruction 2026-07-10 to draft plans for the new findings.
