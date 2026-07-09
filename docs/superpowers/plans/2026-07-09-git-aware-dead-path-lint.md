# refresh.py: git-aware dead-path lint — deliberate deletions print a NOTE, not a warning

Status: DRAFT 2026-07-09, awaiting owner go on this plan. Direction and
output shape are already owner-set (this session, 2026-07-09): rejected —
live-with-it, a per-repo list, a global list, recent-only scoping; chosen —
consult git history, and **print the note** (not silence). One open
sub-question for the owner: slice 2 (the six never-tracked mentions).

## Why this plan exists

`lint_governance()` (`tools/refresh.py:221`) scans `.agents/*.md` for
backticked repo-relative paths (`PATH_TOKEN`, filtered by
`_lintable_repo_path`) and warns on any that don't exist on disk (`:247`,
printed at `:358` as `LINT <file>: references missing path ...`). Decision
records are append-only and never rewritten, so historical entries naming
substrate retired by the 2026-07-08 zero-based consolidation warn on **every
refresh run, forever** — measured baseline this session, 12 lines:

- `.agents/decisions.md` (10): `tools/discover.py`, `drafts/`,
  `harvest/processed.md`, `.bootstrap-tmp/templates/playbooks/`,
  `.agents/repo-map.json`, `backend/`, `frontend/`,
  `.agents/repo-facts.jsonl`, `procedures/migration.md`,
  `bugs/headroom-harness-artifact-overproduction-2026-06-23.md`
- `.agents/state.md` (2): `tools/discover.py`, `procedures/migration.md` —
  both quoted inside the drift-sweep Next bullet itself; they rotate away
  with this plan's bookkeeping.

The cost is not the twelve lines; it is that a *real* dead reference (a typo,
genuine drift) hides in permanent noise. The owner also asked "is there a
note somewhere?" — today, no: the mention site carries no marker that the
file was retired; the evidence lives only in the consolidation plan and in
git itself.

## Design: git is the no-maintenance evidence source

On a missing path, ask git whether the path was deliberately deleted:

    git -C <repo> log --diff-filter=D --format=%h -1 -- <tok minus trailing />

- **Deletion commit found** → the finding is a *note*, not a warning:
  `NOTE <file>: historical: `<tok>` — deleted in <hash>`. The lint output
  itself becomes the "note somewhere": each run tells the reader exactly
  which commit retired the file.
- **No evidence** (never tracked, shallow clone, git failure) → the loud
  `LINT ... references missing path` warning is unchanged. Degradation is
  always toward loud, never toward silent-wrong.

Mechanics:

- Findings gain a kind (`warn` / `note`); the printer at `:358` prefixes
  `LINT` or `NOTE` accordingly, so warnings stay scannable.
- One evidence lookup per unique missing path per run (cached dict); zero
  git subprocesses when nothing is missing — no cost in clean repos.
- `lint_governance()` stays read-only and non-blocking; `git log` only.

Why this satisfies the owner's rejections: no list to maintain anywhere —
git already records every deliberate deletion in every repo, automatically.
`LINT_EXEMPT_PATHS` (`:202`) is *not* extended: it stays exactly its current
three create-on-first-use homes (a template-intentionality exemption, not a
dead-path allowlist). Typo protection is preserved: a typo'd path has no
deletion commit, so it stays loud.

## Measured reach on this repo (2026-07-09)

Git vouches for 4 of the 10 `decisions.md` paths:

| path | deleted in |
|---|---|
| `tools/discover.py` | `f901ad2` |
| `harvest/processed.md` | `19bc791` |
| `.agents/repo-map.json` | `6f08a67` |
| `procedures/migration.md` | `a576b17` |

Six have **no deletion commit** and would stay loud after slice 1:
`backend/` + `frontend/` (illustrative monorepo prose, decisions.md:205 —
never real paths here), `drafts/` + `.bootstrap-tmp/templates/playbooks/` +
`.agents/repo-facts.jsonl` (by-design-untracked scratch, never committed),
and `bugs/headroom-harness-artifact-overproduction-2026-06-23.md` (lived in
another repo; cross-repo mention).

## Slice 1 — evidence lookup + NOTE (code and tests)

- `tools/refresh.py`: `_deletion_commit(repo, tok, cache)` helper
  (subprocess `git log --diff-filter=D --format=%h -1`, any failure →
  `None`); missing-path branch in `lint_governance()` emits
  (`rel`, msg, `note`) when evidence exists, (`rel`, msg, `warn`)
  otherwise; printer prefixes `NOTE`/`LINT` by kind.
- `tests/test_refresh.py`, fixture repo: (1) committed-then-deleted file
  mentioned in `.agents/decisions.md` → `NOTE` carrying the deletion short
  hash, no `LINT` line; (2) never-existed path → `LINT` warning unchanged;
  (3) deleted directory mentioned with trailing `/` → `NOTE`; (4) evidence
  lookup forced to fail → degrades to the `LINT` warning.
- Guard proof: with the evidence lookup stubbed to `None`, tests 1 and 3
  fail; restored, full suite passes.

## Slice 2 — the never-tracked six (OWNER DECISION REQUIRED, not implemented without a word)

The six unvouched lines stay loud after slice 1, permanently, for the same
original reason (verbatim records). List-free option on the table: the
entry segmentation already in `lint_governance()` (the `### ` + `Status:`
parser used for the closed-decision nag) can downgrade never-tracked missing
paths to a distinct note — `NOTE ...: never tracked here (closed entry)` —
**only when the mention sits inside a closed entry** (`Status: Adopted` /
`Superseded`). Open entries and non-decisions files keep the loud warning,
so live typos are still caught. Alternatives: leave the six loud (accept 6
permanent lines), or another shape the owner names.

## Slice 3 — bookkeeping

- `.agents/state.md`: resolve the drift-sweep Next bullet (this also removes
  the two self-referential state.md lint lines); roll the as-of forward.
- Self-refresh this repo and record the actual output. Expected: `nothing
  to do - repo is current`, 4 `NOTE` lines, and (absent slice 2) 6 `LINT`
  lines.
- This plan's Status updated with the commit map.

## Verification

Full suite per `.agents/repo-guidance.md` (Verification) after every slice,
plus the slice-1 guard proof. Slice 3 doc edits: `git diff --check`.

## Non-goals and risks

- **No rewriting of verbatim records** — decisions/state history is
  untouched; the note lives in the lint output, not in the files.
- **No allowlists** (owner-rejected 2026-07-09): `LINT_EXEMPT_PATHS` is not
  extended; no new list, per-repo or global.
- Evidence trusts the local default-branch history: shallow clones or
  rewritten history lose deletion commits → those paths degrade to the loud
  warning (noisier, never wrong).
- Lint remains advisory and read-only; nothing starts blocking.

Provenance: owner direction this session (2026-07-09) — "live with it? no /
a custom list for every repo? a global list? no to both / check recent …
may bite"; "draft it. print the note."
