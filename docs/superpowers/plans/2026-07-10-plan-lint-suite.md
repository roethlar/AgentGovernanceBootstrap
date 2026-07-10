# Test-suite lint for open plan documents (leakage, stale paths, bloat)

Status: APPROVED 2026-07-10 — authority and the owner's verbatim approval
are recorded in `.agents/decisions.md` ("Plan linter for leakage and bloat",
2026-07-10, Status: Active). Revision 2 after an external review returned
REVISE with 13 findings; re-review required before implementation.

## Rule being enforced

The plan contract (decision "Plan contract: agent-facing plan documents",
2026-07-10, `.agents/decisions.md`; canonical rule in the `plan` operator
bullet of `templates/AGENTS.template.md`): plan documents are agent-facing
and self-contained — implementable by a cold, less-capable agent, free of
conversational references that need the originating context. This lint
enforces the mechanically checkable subset on open plans in
`docs/superpowers/plans/`. Everything dated before 2026-07-10 is history
and fully exempt: the contract is forward-looking, and a fleet scan
(2026-07-10) plus an external review both confirmed legacy plans are dirty
by these rules and must not be retrofitted.

## Deliverables

1. `tests/test_plan_lint.py` — scanner and tests, part of the normal suite.
2. One line added to `.agents/repo-guidance.md` (Verification): changes
   under `docs/superpowers/plans/` require
   `python3 -m unittest tests.test_plan_lint -v` in addition to
   `git diff --check`. Without this, a docs-only plan edit never meets the
   linter (external-review finding: the suite is not currently mandated
   for plan-only changes).
3. Conformance edits to the open 2026-07-10 plans (listed below) so the
   corpus gate passes on the tree this lands in.

No changes to `tools/refresh.py`. Nothing ships to governed repos.

## Scanner API (all in `tests/test_plan_lint.py`)

Module must import on Python 3.9: `from __future__ import annotations` at
the top; no 3.10+ syntax at runtime. Files are read as UTF-8 with
`errors="replace"`.

- `Finding = namedtuple("Finding", "path line kind detail")` — `path`
  repo-relative posix string, `line` 1-based int (0 for whole-file kinds),
  `kind` one of `missing-status`, `leakage`, `stale-path`, `too-long`.
- `mask_code(text) -> str` — line-count-preserving mask. Fenced blocks:
  a fence opens at a line whose first non-space characters are a run of
  3+ backticks or 3+ tildes and closes at the next line starting with a
  run of the same character at least as long; every line in between
  (inclusive of the delimiters) is replaced by an empty line. Inline code:
  spans matching a run of 1+ backticks, non-backtick content, then an
  equal run (regex `` (`+)[^`]+?\1 ``) are replaced by spaces of equal
  length. Line numbers in findings therefore always match the original
  file.
- `plan_status(masked) -> str | None` — first line of the MASKED text
  matching `^\s*\**\s*Status\s*\**\s*:\s*(.*)$`; returns the captured
  remainder. Bold `**Status:**` forms occur in the wild (fleet scan
  2026-07-10) and must match. A `Status:` inside a fence is masked and
  therefore never matches.
- `is_closed(status) -> bool` — `status` matches
  `(?i)^\s*\**\s*(CLOSED|DONE|SUPERSEDED|IMPLEMENTED|WITHDRAWN|REJECTED)\b`.
  Everything else — `DRAFT`, `APPROVED`, `Open`, unknown wording — is
  open. Known accepted escape: a qualified closure ("CLOSED for part 1,
  part 2 remains") reads as closed; post-cutoff plans owe one whole-file
  status, and the fixture suite pins this behavior so it is a documented
  choice, not an accident.
- `plan_date(path) -> str | None` — leading `YYYY-MM-DD` from the
  filename, else None.
- `scan_plan(repo_root, path) -> list[Finding]` — evaluation order:
  1. `plan_date` < `2026-07-10` or undatable filename → return `[]`
     (grandfathered history, status not even consulted).
  2. `plan_status` is None → `[Finding(path, 0, "missing-status", ...)]`,
     stop.
  3. `is_closed` → return `[]`, stop.
  4. Otherwise emit, in this order, deduplicated:
     - `leakage`: case-insensitive search of the masked text for the
       module constant `LEAKAGE_PHRASES = ("this session",
       "this conversation", "in this chat", "as discussed",
       "per our discussion", "approved in chat", "approval in chat",
       "wording from chat")`; one finding per (line, phrase).
     - `stale-path`: over the ORIGINAL text, backtick path tokens
       accepted by `refresh._lintable_repo_path` (import from
       `tools.refresh` — the suite already imports that module in
       `tests/test_refresh.py`) that do not exist under `repo_root` AND
       for which `refresh._deletion_commit` returns a commit. Scope is
       deliberately narrow — simple backtick mentions of
       previously-deleted paths; never-existed tokens are allowed because
       open plans name files they will create, so typos escape this
       check (accepted, documented). This intentionally does NOT mirror
       the refresh lint, whose NOTE/warn polarity serves a different
       purpose.
     - `too-long`: `len(text.splitlines())` (physical lines, blank lines
       included) > 600 → one finding. Metric stated exactly because the
       corpus evidence differs by counter: the largest post-cutoff
       legitimate plan is well under 300 physical lines; 600 leaves 2x
       headroom.
  5. Any line whose original text contains the marker
     `plan-lint: allow` (conventionally in an HTML comment) is excluded
     from `leakage` and `stale-path` findings — the visible, reviewable
     escape hatch for a legitimate quotation or historical reference.
- `scan_corpus(repo_root) -> list[Finding]` — sorted
  `glob("docs/superpowers/plans/*.md")`; raises `AssertionError` if the
  glob is empty (vacuity guard); one shared deletion-commit cache per
  call; returns concatenated findings.

## Test specification

- **Per-detector fixtures**, temp dirs via `tempfile`, hermetic:
  - every phrase in `LEAKAGE_PHRASES` individually planted in an
    otherwise-valid open plan (`Status: APPROVED ...`, dated 2026-07-10)
    → exactly one `leakage` finding with the exact line number; the same
    phrase inside an inline code span and inside a fence → no finding; a
    planted phrase on a line carrying the allow marker → no finding.
  - every closure marker in `is_closed` individually → `[]` even with a
    planted phrase; `DRAFT`, `APPROVED`, `Open`, and gibberish statuses →
    treated as open (phrase finding present); the qualified-closure form
    ("CLOSED for ...") → closed (pins the documented escape).
  - missing status: dated `2026-07-10-x.md` without `Status:` →
    `missing-status`; dated `2026-06-01-x.md` → `[]`; a fence containing
    a fake `Status: CLOSED` with no real status → still `missing-status`.
  - line numbers after a multi-line fence: planted phrase below a 10-line
    fence reports the true original line.
  - too-long: exactly 600 physical lines → no finding; 601 → finding;
    blank-heavy file (700 physical, 300 non-blank) → finding (pins the
    physical-line metric).
  - stale-path: a scratch git repo built in a temp dir (init; commit a
    file; delete it; commit) → a backtick token naming it yields
    `stale-path`; a never-existed token → no finding. No dependence on
    this clone's history.
- **Aggregator test**: temp corpus dir with one bad plan per kind plus
  one clean closed and one grandfathered plan → `scan_corpus` returns
  exactly the expected kinds/paths (proves the aggregator invokes every
  detector and the exemptions short-circuit).
- **Corpus gate**: `scan_corpus` over this real repo returns `[]`, and
  the glob found at least 25 files. If
  `git rev-parse --is-shallow-repository` reports true, skip with an
  explicit `skipTest` naming the missing prerequisite (deletion history)
  rather than passing silently.

The per-detector fixtures are the red side of the bite proof for the
corpus gate; each detector has at least one failing fixture, so the
gate's green is meaningful.

## Conformance edits (same slice, before the corpus gate lands)

Audit every open plan dated 2026-07-10 (currently: the four parked drafts
plus this plan) against the full check set and fix violations with dated,
self-contained wording. Known from the external review: three of the four
parked drafts carry a leakage phrase in their provenance prose, and this
plan formerly carried a real deleted-path token as its fixture example
(now replaced by the scratch-repo fixture above). Scope/status of the
parked drafts is untouched; wording only.

## Slices

1. Scanner + tests + conformance edits + the repo-guidance verification
   line; suite green. One commit.
2. Plan closure bookkeeping: this plan's Status flips to CLOSED with the
   landing commit; the decisions entry ("Plan linter for leakage and
   bloat") already records the approval and design, so it needs only the
   landing-commit reference. One commit.

## Verification

Full suite on the newest interpreter available plus, when a Python 3.9 is
present, an import check of `tests.test_plan_lint` (the module must not
be the thing that breaks the documented floor further; the pre-existing
whole-suite 3.9 incompatibility is recorded separately in
`docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md`).
Fixture tests are the bite proof as specified. Docs edits:
`git diff --check`.

## Non-goals and risks

- Not shipped to governed repos; no `tools/refresh.py` changes. Fleet
  plan locations vary (fleet scan 2026-07-10:
  `.agents/plans/`, `docs/plan/`, `docs/plans/`, `docs/*-Plan.md`, repo
  root), so a fleet-wide version would need a per-repo location record —
  explicitly out of scope.
- Typos in path references escape the stale-path check (never-existed
  tokens are assumed planned files). Accepted for a forward-looking lint.
- The phrase list catches only listed phrasings; it grows by evidence.
  The allow marker keeps legitimate quotations possible without
  weakening the default.
- Post-cutoff plans without a filename date escape the date rule only by
  also lacking the `.md` extension or living outside the plans dir —
  both out of the lint's charter.
