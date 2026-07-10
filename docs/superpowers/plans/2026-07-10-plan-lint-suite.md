# Test-suite lint for open plan documents (leakage, stale paths, bloat)

Status: APPROVED 2026-07-10 — authority and the owner's verbatim approval
are recorded in `.agents/decisions.md` ("Plan linter for leakage and bloat",
2026-07-10, Status: Active). Revision 6 after external review rounds 1–5
(each REVISE); re-review required before implementation.

## Rule being enforced

The plan contract (decision "Plan contract: agent-facing plan documents",
2026-07-10, `.agents/decisions.md`; canonical rule in the `plan` operator
bullet of `templates/AGENTS.template.md`): plan documents are agent-facing
and self-contained — implementable by a cold, less-capable agent, free of
conversational references that need the originating context. This lint
enforces the mechanically checkable subset on open plans in
`docs/superpowers/plans/`. Plans dated before 2026-07-10 are history and
fully exempt: the contract is forward-looking, and both a fleet scan
(2026-07-10) and external review confirmed legacy plans are dirty by these
rules and must not be retrofitted.

## Deliverables

1. `tests/test_plan_lint.py` — scanner and tests, part of the normal suite.
2. One line added to `.agents/repo-guidance.md` (Verification): changes
   under `docs/superpowers/plans/` require the targeted module run —
   `python3 -m unittest tests.test_plan_lint -v` (Windows, from Git Bash:
   `py -3 -m unittest tests.test_plan_lint -v`) — in addition to
   `git diff --check`.
3. Conformance edits to the open 2026-07-10 plans (listed under Slices).

No changes to `tools/refresh.py`. Nothing ships to governed repos.

## Scanner API (all in `tests/test_plan_lint.py`)

Module and its tests must run complete on Python 3.9:
`from __future__ import annotations` at the top; no 3.10+ runtime syntax;
fixture writes use `open(..., "w", newline=...)`, never
`Path.write_text(newline=...)`. Files are read as UTF-8 with
`errors="replace"`. All matching below is line-oriented: the text is
split with `splitlines()` and every regex runs against single lines with
horizontal whitespace classes (`[ \t]`), never `\s` across the whole
document — no pattern can match across a newline.

- `Finding = namedtuple("Finding", "path line kind detail")` — `path`
  repo-relative posix string, `line` 1-based int (0 for whole-file
  kinds), `kind` one of `missing-date`, `missing-status`, `leakage`,
  `stale-path`, `too-long`.
- `mask_code(text) -> str` — line-count-preserving mask, two passes:
  1. Fences: a fence opens at a line matching
     `^ {0,3}(\x60{3,}|~{3,})` (0–3 spaces of indent, then a run of 3+
     backticks or 3+ tildes) and closes at the next line matching
     `^ {0,3}<run>[ \t]*$` where `<run>` is a run of the same character
     at least as long as the opener, with nothing but horizontal
     whitespace after it. Openers indented 4+ spaces are not fences;
     candidate closers with trailing non-whitespace are not closers.
     Every line from opener to closer inclusive is replaced by an empty
     line; an unclosed fence masks to end of file.
  2. Inline code, per line of the fence-masked text: spans matching a
     maximal backtick run, non-backtick non-newline content, then an
     equal maximal run — regex
     `(?<!\x60)(\x60+)([^\x60\n]+?)\1(?!\x60)` — are replaced by spaces
     of equal length. Inline spans never cross lines; a would-be
     multi-line span is not masked (documented limitation).
  Line numbers in findings always match the original file.
- `plan_status(masked) -> str | None` — iterate the MASKED text line by
  line; the first line matching
  `^ {0,3}(?:Status:|\*\*Status:\*\*|\*\*Status\*\*:)(?!:)[ \t]*(.*)$`
  — exactly three canonical shapes, each with ONE mandatory colon
  (plain `Status:`, bold with colon inside `**Status:**`, bold with
  colon outside `**Status**:`), preceded by at most 3 spaces and
  nothing else, and not followed by a second colon — yields the
  captured remainder. Case-sensitive; lowercase `status:`, colonless
  `Status CLOSED`, doubled-colon `Status:: CLOSED`, tab-indented,
  4+-space-indented (indented code), and bulleted (`* Status:`) lines
  all do not match; `Status` and `:` split across two lines never
  match (line-oriented by construction). Later `Status:` lines are
  ignored; fenced fake statuses are masked away.
- `is_closed(status) -> bool` — True iff the status matches, on that
  single line:
  `(?i)^[ \t]*\**[ \t]*(CLOSED|DONE|SUPERSEDED|IMPLEMENTED|WITHDRAWN|REJECTED)\**[ \t]*($|[ \t](\d{4}-\d{2}-\d{2})\b.*)`
  AND, when the date group is present, `datetime.date.fromisoformat`
  accepts it — the closure marker either stands alone or is followed
  by horizontal whitespace, a VALID ISO date, then anything.
  `CLOSED2026-07-12` (no separator), `CLOSED 2026-99-99` (impossible
  date), and every qualified form without a leading date ("CLOSED for
  part 1", "CLOSED — part 2 remains", "DONE except X") read as OPEN:
  the decision exempts only closed plans, and partial closure is not
  closure. Post-cutoff closures therefore are written either as the
  bare marker or as `CLOSED 2026-07-12 — <detail>` (marker, valid
  date, detail). `DRAFT`, `APPROVED`, `Open`, unknown wording → open.
- `plan_date(path) -> datetime.date | None` — filename must match
  `^(\d{4}-\d{2}-\d{2})-` (date then a literal hyphen delimiter); the
  captured string is validated with `datetime.date.fromisoformat`, and
  any `ValueError` yields None. `2026-07-09notes.md` (no delimiter) and
  `0000-00-00-x.md` (invalid date) both yield None.
- `scan_plan(repo_root, path, cache=None, history=True) -> list[Finding]`
  — first line: `cache = {} if cache is None else cache` (the refresh
  helper requires a mapping). Evaluation order:
  1. `plan_date` valid and < 2026-07-10 → return `[]` (grandfathered;
     status not consulted). `plan_date` None →
     `[Finding(path, 0, "missing-date", ...)]` and continue (an
     undatable file in the plans glob is a post-contract plan with a
     naming defect, not exempt history).
  2. `plan_status` None → append `missing-status`, stop.
  3. `is_closed` → return findings so far (closure exempts content
     checks only).
  4. Otherwise append, deduplicated:
     - `leakage`: case-insensitive per-line search of the masked text
       for the module constant `LEAKAGE_PHRASES` (its exact eight
       values are listed in the fenced block after this API section —
       at top level, where the masker's 3-space fence rule masks it);
       one finding per (line, phrase).
     - `stale-path` (only when `history` is True): over the ORIGINAL
       text, backtick path tokens accepted by
       `refresh._lintable_repo_path` (the imported `refresh` module —
       see Import convention below) that do not exist under
       `repo_root` AND for
       which `refresh._deletion_commit(repo_root, token, cache)`
       returns a commit. Deliberately narrow: never-existed tokens are
       allowed (open plans name files they will create), so typos
       escape — accepted, documented. This does NOT mirror the refresh
       lint, whose NOTE/warn polarity serves a different purpose.
     - `too-long`: `len(text.splitlines())` (physical lines, blanks
       included) > 600 → one finding. Largest post-cutoff legitimate
       plan is well under 300 physical lines; 600 is 2x headroom.
  5. Any line whose original text contains the marker
     `plan-lint: allow` (conventionally in an HTML comment) is excluded
     from `leakage` AND `stale-path` findings on that same line only.
- `scan_corpus(repo_root, history=True) -> list[Finding]` — sorted
  `glob("docs/superpowers/plans/*.md")`; raises `AssertionError` if the
  glob is empty (vacuity guard); creates one cache dict and passes it
  to every `scan_plan`; concatenated findings.
- Import convention: follow the existing suite — prepend the `tools/`
  directory to `sys.path` and `import refresh`, exactly as
  `tests/test_refresh.py` does; no `tools.refresh` namespace import.

The `LEAKAGE_PHRASES` constant holds exactly these eight values:

```
LEAKAGE_PHRASES = (
    "this session", "this conversation", "in this chat",
    "as discussed", "per our discussion", "approved in chat",
    "approval in chat", "wording from chat",
)
```

## Test specification

Git-backed fixtures reuse the existing suite's helpers
(`tests/test_refresh.py`: `init_repo` and `commit_all` set local git
identity and commit) or a thin wrapper over them, in temp dirs —
hermetic, no tracked file mutated. Fixture documents embed phrase and
status strings as LITERALS, never derived from the module constants:
neutralizing a constant during the guard proof must turn fixtures red,
not delete them.

- **Per-detector fixtures**, each asserting exact finding kind, path,
  and line:
  - each of the eight leakage phrases, written literally in an
    otherwise-valid open plan (`Status: APPROVED 2026-07-10 ...`, dated
    filename) → exactly one `leakage` finding at the exact line; the
    same phrase inside an inline span and inside a fence → none; on a
    line with the allow marker → none; on the line ADJACENT to an
    allow marker → finding.
  - masking: tilde fence; 4-backtick fence; fence indented 3 spaces
    (masks) and 4 spaces (does not); candidate closer with trailing
    text (does not close); unclosed fence (masks to EOF); phrase after
    a 10-line fence reports the true original line; mismatched backtick
    runs (``` ``x` ```) leave the prose unmasked; equal runs mask.
  - status parsing: `**Status:** DRAFT` (bold) parsed; lowercase
    `status: CLOSED` not parsed (→ `missing-status`); `Status` on one
    line and `: CLOSED` on the next → `missing-status`; 4-space
    indented, tab-indented, and bulleted (`* Status: CLOSED`) forms →
    `missing-status`; two `Status:` lines → first wins; fenced fake
    `Status: CLOSED` with no real status → `missing-status`.
  - closure, two layers: (a) table-driven direct `is_closed`
    assertions — every marker alone → True; every marker + valid ISO
    date → True; `CLOSED for Artifact 1`, `CLOSED — part 2 remains`,
    `DONE except X`, `CLOSED2026-07-12`, `CLOSED 2026-99-99`, `DRAFT`,
    `APPROVED`, `Open`, gibberish → False; (b) scanner fixtures where
    EVERY document above (closed and open alike) carries a literal
    planted leakage phrase — closed forms → `[]`, open forms → the
    `leakage` finding. No closure fixture is ever phrase-free, so
    inverting `is_closed` in either direction turns fixtures red.
  - dates: `2026-07-10-x.md` without status → `missing-status`;
    `2026-06-01-x.md` (any content) → `[]`; `notes.md`,
    `2026-07-09notes.md`, and `0000-00-00-x.md` (valid open status, a
    planted phrase) → `missing-date` AND `leakage`.
  - too-long: exactly 600 physical lines → none; 601 → finding;
    blank-heavy (700 physical / 300 non-blank) → finding.
  - stale-path: repo built with the suite helpers (commit a file;
    delete it; commit) → backtick token naming it yields `stale-path`
    at the exact line; never-existed token → none; the same token on a
    line with the allow marker → none; on the adjacent line → finding.
  - cache: two fixture plans containing the same stale token, scanned
    via `scan_corpus` with `refresh.git` patched to count invocations →
    two `stale-path` findings but exactly one `git log` call.
- **Aggregator test**: temp corpus dir inside a helper-built repo with
  one bad plan per kind plus one clean closed and one grandfathered
  plan → `scan_corpus` returns exactly the expected kind/path set.
- **Corpus gates over this real repo**, split by history dependence:
  - `test_corpus_clean`: `scan_corpus(repo_root, history=False)` → `[]`,
    glob found ≥ 25 files. Runs everywhere, including shallow clones.
  - `test_corpus_stale_paths`: full-history pass → `[]`; when
    `git rev-parse --is-shallow-repository` is true, `skipTest` naming
    the missing prerequisite. Only the history-dependent check skips.

## Slices (one item per commit, per the git-safety rule)

1. Conformance edits: one commit per affected open 2026-07-10 plan.
   Audit all five (the four parked drafts and this plan) against the
   full check set; external review round 1 found leakage phrases in
   three of the four parked drafts. Wording only — scope and status of
   parked drafts untouched.
2. Scanner + tests + the repo-guidance verification line (the gate and
   its wiring are one item). Suite green before commit.
3. Closure bookkeeping, exact edits: this plan's Status line becomes
   `Status: CLOSED <landing date> — landed <commit hashes>` (commit
   map). In `.agents/decisions.md`, the entry's status line becomes
   `Status: Adopted <landing date> — landed <scanner commit>; canonical
   home tests/test_plan_lint.py + the repo-guidance Verification line`,
   and — per that file's own archive rule for entries whose rule now
   lives in its canonical home — the whole entry then moves VERBATIM to
   `docs/history/decisions-archive.md` in the same commit, no stub left
   behind (the refresh lint flags closed decisions awaiting archive).
   In `.agents/state.md`, the plan's line is REMOVED from Active
   Sources and the `## Now` clause "the plan-linter decision is Active,
   its plan approved and under external review (…)" is replaced by:
   "the plan-lint suite is landed (`tests/test_plan_lint.py` +
   repo-guidance Verification line, <scanner commit>); open plans dated
   2026-07-10+ are linted for leakage, stale paths, and bloat." Until
   landing, the decision entry's "implementation in progress" wording
   covers the review phase — no interim edit needed.

## Verification

- Full suite on the newest interpreter available; the targeted module
  additionally run complete under a Python 3.9 when one is present —
  Unix `python3.9 -m unittest tests.test_plan_lint -v`, Windows (Git
  Bash) `py -3.9 -m unittest tests.test_plan_lint -v` — this module is
  a required gate and must not deepen the recorded 3.9 floor problem.
- Guard proof, hermetic (never mutate the tracked file): the runner is
  driven from the real repo checkout, so BEFORE loading the temp copy
  it prepends the real repo's `tools/` directory to `sys.path` (the
  runner knows the repo root; the copy must not derive paths from its
  own relocated `__file__`). Copy `tests/test_plan_lint.py` to a temp
  directory; load it with `importlib.util.spec_from_file_location`; run
  its tests via `unittest.TestLoader().loadTestsFromModule`. Inside the
  module, the real repo root for corpus tests is
  `Path(refresh.__file__).resolve().parent.parent` (works identically
  in the copy because `refresh` resolves through the pre-set
  `sys.path`); `repo_root` is always a function argument, never module
  state. First run the UNMODIFIED copy and require green — proves the
  loader works before any mutation is trusted. Then one mutation at a
  time, each named with the fixtures it must turn red:
  - empty `LEAKAGE_PHRASES` → the eight per-phrase fixtures;
  - force `is_closed` to always True → the open-status and
    qualified-closure scanner fixtures (their planted phrases stop
    being reported) and the False rows of the `is_closed` table;
  - force `is_closed` to always False → the closed-marker scanner
    fixtures (planted phrases start being reported) and the True rows
    of the table;
  - bump the length bound to 10000 → the 601-line and blank-heavy
    fixtures;
  - drop the stale-path branch → the deleted-token fixture;
  - make `plan_date` return None always → the grandfathered-plan
    fixture (its `[]` expectation fails);
  - skip appending the `missing-date` finding → the `notes.md`,
    `2026-07-09notes.md`, and `0000-00-00-x.md` fixtures;
  - make `plan_status` return None always → the closed-marker exempt
    fixtures (they now get `missing-status`);
  - skip appending the `missing-status` finding → the no-status and
    fake-status fixtures;
  - disable `mask_code` (identity function) → the phrase-in-fence and
    phrase-in-span negative fixtures and the fenced-fake-status
    fixture;
  - point the corpus glob at an empty pattern → the empty-glob
    `AssertionError`.
  Observe red per mutation, discard the copy, run the real module and
  full suite green. Record the red/green table in the closure commit
  message.
- Docs edits: `git diff --check`.

## Non-goals and risks

- Not shipped to governed repos; no `tools/refresh.py` changes. Fleet
  plan locations vary (fleet scan 2026-07-10: `.agents/plans/`,
  `docs/plan/`, `docs/plans/`, `docs/*-Plan.md`, repo root), so a
  fleet-wide version would need a per-repo location record — out of
  scope.
- Typos in path references escape the stale-path check (never-existed
  tokens read as planned files). Accepted for a forward-looking lint.
- The phrase list catches only listed phrasings; it grows by evidence.
  The allow marker keeps legitimate quotations possible without
  weakening the default.
- Multi-line inline code spans are not masked (spans never cross
  lines); the fenced-block form is the sanctioned way to write
  multi-phrase listings, as this plan itself does.
- Post-cutoff closure wording rule: a BARE closure marker (`CLOSED`,
  `DONE`, ...) closes, and a marker followed by an ISO date closes;
  any trailing detail without a leading date ("CLOSED for part 1")
  stays open under lint until reworded. Chosen over any heuristic for
  "partial" closure — enforced loudly, trivially satisfied by writing
  the date.
