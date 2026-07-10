# Test-suite lint for open plan documents (leakage, stale paths, bloat)

Status: APPROVED 2026-07-10 — authority and the owner's verbatim approval
are recorded in `.agents/decisions.md` ("Plan linter for leakage and bloat",
2026-07-10, Status: Active). Revision 4 after external review rounds 1–3
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
  `^ {0,3}\**[ \t]*Status[ \t]*\**[ \t]*:[ \t]*(.*)$` (case-sensitive
  `Status`) yields the captured remainder. Bold `**Status:**` matches;
  lowercase `status:` does not (documented choice); a line indented 4+
  spaces is indented code and does not match; `Status` and `:` split
  across two lines never match (line-oriented by construction). Later
  `Status:` lines are ignored; fenced fake statuses are masked away.
- `is_closed(status) -> bool` — True iff the status matches, on that
  single line:
  `(?i)^[ \t]*\**[ \t]*(CLOSED|DONE|SUPERSEDED|IMPLEMENTED|WITHDRAWN|REJECTED)\**[ \t]*(\d{4}-\d{2}-\d{2}\b.*)?$`
  — the closure marker either stands alone or is followed by an ISO
  date and then anything. Every qualified form without a leading date
  ("CLOSED for part 1", "CLOSED — part 2 remains", "DONE except X")
  reads as OPEN: the decision exempts only closed plans, and partial
  closure is not closure. Post-cutoff closures therefore must be
  written `CLOSED 2026-07-12 — <detail>` (marker, date, detail);
  anything else stays under lint. `DRAFT`, `APPROVED`, `Open`, unknown
  wording → open.
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
       for the module constant `LEAKAGE_PHRASES`; one finding per
       (line, phrase). The constant holds exactly these eight phrases:

       ```
       LEAKAGE_PHRASES = (
           "this session", "this conversation", "in this chat",
           "as discussed", "per our discussion", "approved in chat",
           "approval in chat", "wording from chat",
       )
       ```

     - `stale-path` (only when `history` is True): over the ORIGINAL
       text, backtick path tokens accepted by
       `refresh._lintable_repo_path` (import `tools.refresh` as the
       existing suite does) that do not exist under `repo_root` AND for
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
    line and `: CLOSED` on the next → `missing-status`; a 4-space
    indented `Status: CLOSED` → `missing-status`; two `Status:` lines →
    first wins; fenced fake `Status: CLOSED` with no real status →
    `missing-status`.
  - closure: each of the six markers followed by an ISO date → `[]`
    even with a planted phrase; each marker alone → `[]`; `CLOSED for
    Artifact 1 ...`, `CLOSED — part 2 remains`, `DONE except X` (no
    leading date) → OPEN (phrase finding present); `DRAFT`, `APPROVED`,
    `Open`, gibberish → open.
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
3. Closure bookkeeping: this plan's Status flips to CLOSED with the
   commit map; the decisions entry gains the landing-commit reference;
   `.agents/state.md` drops its interim under-review wording.

## Verification

- Full suite on the newest interpreter available; the targeted module
  additionally run complete under a Python 3.9 when one is present —
  Unix `python3.9 -m unittest tests.test_plan_lint -v`, Windows (Git
  Bash) `py -3.9 -m unittest tests.test_plan_lint -v` — this module is
  a required gate and must not deepen the recorded 3.9 floor problem.
- Guard proof, hermetic (never mutate the tracked file): copy
  `tests/test_plan_lint.py` to a temp directory; in the copy,
  neutralize one detector (empty `LEAKAGE_PHRASES`, force `is_closed`
  True, bump the length bound, drop the stale-path branch, point the
  corpus glob at an empty pattern); load the copy with
  `importlib.util.spec_from_file_location` and run its tests via
  `unittest.TestLoader().loadTestsFromModule`, passing this repo's root
  explicitly where a test needs it (`repo_root` is always a function
  argument, never module state, precisely so the copy runs against the
  same repo). Fixture data is literal (see above), so each
  neutralization turns specific fixtures red rather than deleting
  them; the corpus-glob neutralization trips the empty-glob
  `AssertionError`. Observe red per detector, discard the copy, run
  the real module and full suite green. Record the red/green table in
  the closure commit message.
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
- Post-cutoff closures must carry an ISO date after the marker; a
  dateless closure stays under lint until reworded. This is a wording
  requirement on future plans, enforced loudly, chosen over any
  heuristic for "partial" closure.
