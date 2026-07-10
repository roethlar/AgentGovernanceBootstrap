# Test-suite lint for open plan documents (leakage, stale paths, bloat)

Status: APPROVED 2026-07-10 — authority and the owner's verbatim approval
are recorded in `.agents/decisions.md` ("Plan linter for leakage and bloat",
2026-07-10, Status: Active). Revision 3 after external review rounds 1
(REVISE, 13 findings) and 2 (REVISE, 2 carried + 9 new); re-review
required before implementation.

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
   `git diff --check`. Without this, a docs-only plan edit never meets
   the linter.
3. Conformance edits to the open 2026-07-10 plans (listed under Slices).

No changes to `tools/refresh.py`. Nothing ships to governed repos.

## Scanner API (all in `tests/test_plan_lint.py`)

Module and its tests must run complete on Python 3.9:
`from __future__ import annotations` at the top; no 3.10+ runtime syntax;
fixture writes use `open(..., "w", newline=...)`, never
`Path.write_text(newline=...)`. Files are read as UTF-8 with
`errors="replace"`.

- `Finding = namedtuple("Finding", "path line kind detail")` — `path`
  repo-relative posix string, `line` 1-based int (0 for whole-file
  kinds), `kind` one of `missing-date`, `missing-status`, `leakage`,
  `stale-path`, `too-long`.
- `mask_code(text) -> str` — line-count-preserving mask, two passes:
  1. Fences: a fence opens at a line whose first non-space characters
     are a run of 3+ backticks or 3+ tildes and closes at the next line
     starting (after up to 3 spaces) with a run of the same character at
     least as long; every line from opener to closer inclusive is
     replaced by an empty line. An unclosed fence masks to end of file.
  2. Inline code, applied per line of the fence-masked text: spans
     matching a run of 1+ backticks, then one or more characters that
     are neither backtick nor newline, then an equal run (regex
     `` (`+)[^`\n]+?\1 ``) are replaced by spaces of equal length.
     Inline spans never cross lines; a would-be multi-line span is
     simply not masked (documented limitation).
  Line numbers in findings therefore always match the original file.
- `plan_status(masked) -> str | None` — first line of the MASKED text
  matching `^\s*\**\s*Status\s*\**\s*:\s*(.*)$` (case-sensitive
  `Status`; the bold `**Status:**` form occurs in the wild and must
  match; lowercase `status:` deliberately does not). Returns the first
  match only; later `Status:` lines are ignored. A `Status:` inside a
  fence is masked and never matches.
- `is_closed(status) -> bool` — True iff the status matches
  `(?i)^\s*\**\s*(CLOSED|DONE|SUPERSEDED|IMPLEMENTED|WITHDRAWN|REJECTED)\b`
  AND the first non-whitespace character after the marker (and after any
  closing `**`) is a digit, `(`, `.`, `,`, `:`, `;`, `-`, `–`, `—`, or
  end of line. A letter there means a qualified closure ("CLOSED for
  part 1, part 2 remains") and reads as OPEN — the decision authorizes
  exempting only closed plans, so partial closure is not closure. Every
  other status wording (`DRAFT`, `APPROVED`, `Open`, unknown) is open.
- `plan_date(path) -> str | None` — leading `YYYY-MM-DD` from the
  filename (regex-validated), else None.
- `scan_plan(repo_root, path, cache=None, history=True) -> list[Finding]`
  — evaluation order:
  1. `plan_date` valid and < `2026-07-10` → return `[]` (grandfathered;
     status not consulted). `plan_date` None →
     `[Finding(path, 0, "missing-date", ...)]` plus continue with the
     remaining checks (an undatable file in the plans glob is a
     post-contract plan with a naming defect, not exempt history).
  2. `plan_status` None → append `missing-status`, stop.
  3. `is_closed` → return findings so far (closure exempts content
     checks only, not the naming/status defects above).
  4. Otherwise append, deduplicated:
     - `leakage`: case-insensitive search of the masked text for the
       module constant `LEAKAGE_PHRASES = ("this session",
       "this conversation", "in this chat", "as discussed",
       "per our discussion", "approved in chat", "approval in chat",
       "wording from chat")`; one finding per (line, phrase).
     - `stale-path` (only when `history` is True): over the ORIGINAL
       text, backtick path tokens accepted by
       `refresh._lintable_repo_path` (import `tools.refresh` as the
       existing suite does) that do not exist under `repo_root` AND for
       which `refresh._deletion_commit(repo_root, token, cache)` returns
       a commit; `cache` is a dict created by the caller (`scan_corpus`
       makes one per run and passes it to every `scan_plan`, so
       duplicate tokens cost one git call). Deliberately narrow: simple
       backtick mentions of previously-deleted paths; never-existed
       tokens are allowed because open plans name files they will
       create, so typos escape (accepted, documented). This does NOT
       mirror the refresh lint, whose NOTE/warn polarity serves a
       different purpose.
     - `too-long`: `len(text.splitlines())` (physical lines, blanks
       included) > 600 → one finding. The largest post-cutoff
       legitimate plan is well under 300 physical lines; 600 is 2x
       headroom.
  5. Any line whose original text contains the marker
     `plan-lint: allow` (conventionally in an HTML comment) is excluded
     from `leakage` and `stale-path` findings on that same line only —
     the visible, reviewable escape hatch for a legitimate quotation or
     historical reference.
- `scan_corpus(repo_root, history=True) -> list[Finding]` — sorted
  `glob("docs/superpowers/plans/*.md")`; raises `AssertionError` if the
  glob is empty (vacuity guard); one shared deletion cache; concatenated
  findings.

## Test specification

Git-backed fixtures use a helper mirroring the existing suite's repo
builder (`tests/test_refresh.py` `make_repo`-style: `git init`, set
`user.name`/`user.email` locally, commit) so tests run with no global
git identity. All fixtures live in temp dirs — hermetic, no tracked file
mutated.

- **Per-detector fixtures**, each asserting exact finding kind, path,
  and line:
  - every phrase in `LEAKAGE_PHRASES` individually planted in an
    otherwise-valid open plan (`Status: APPROVED ...`, dated
    2026-07-10) → exactly one `leakage` finding at the exact line; the
    same phrase inside an inline span and inside a fence → none; a
    phrase on a line with the allow marker → none; a phrase on the line
    ADJACENT to an allow marker → finding (marker is same-line only).
  - fence variants: tilde fence, 4-backtick fence, fence indented up to
    3 spaces, unclosed fence, phrase after a 10-line fence reporting the
    true original line, fenced fake `Status: CLOSED` with no real status
    → `missing-status`.
  - status parsing: `**Status:** DRAFT` (bold) parsed; lowercase
    `status: CLOSED` NOT parsed (→ `missing-status`); two `Status:`
    lines → first wins.
  - every closure marker individually, followed by a date → `[]` even
    with a planted phrase; `DRAFT`, `APPROVED`, `Open`, gibberish →
    open; qualified closure `CLOSED for Artifact 1 ...` → OPEN (phrase
    finding present).
  - dates: `2026-07-10-x.md` without status → `missing-status`;
    `2026-06-01-x.md` (any content) → `[]`; `notes.md` (undatable, with
    valid open status and a planted phrase) → `missing-date` AND
    `leakage`.
  - too-long: exactly 600 physical lines → none; 601 → finding;
    blank-heavy (700 physical / 300 non-blank) → finding.
  - stale-path: scratch repo via the helper (commit a file; delete it;
    commit) → backtick token naming it yields `stale-path`;
    never-existed token → none; duplicate token in two files scanned
    with one cache → exactly one underlying git lookup (assert via the
    cache's state or a counting wrapper).
- **Aggregator test**: temp corpus dir inside a helper-built repo with
  one bad plan per kind plus one clean closed and one grandfathered
  plan → `scan_corpus` returns exactly the expected kind/path set
  (proves every detector and exemption is wired).
- **Corpus gates over this real repo**, split by history dependence:
  - `test_corpus_clean`: `scan_corpus(repo_root, history=False)` → `[]`,
    glob found ≥ 25 files. Runs everywhere, including shallow clones.
  - `test_corpus_stale_paths`: full-history stale-path pass → `[]`;
    when `git rev-parse --is-shallow-repository` is true, `skipTest`
    naming the missing prerequisite. Only the history-dependent check
    is ever skipped.

## Slices (one item per commit, per the git-safety rule)

1. Conformance edits: one commit per affected open 2026-07-10 plan.
   Audit all five (the four parked drafts and this plan) against the
   full check set; external review round 1 found leakage phrases in
   three of the four parked drafts. Wording only — scope and status of
   parked drafts untouched.
2. Scanner + tests + the repo-guidance verification line (the gate and
   its wiring are one item). Suite green before commit.
3. Closure bookkeeping: this plan's Status flips to CLOSED with the
   commit map; the decisions entry gains the landing-commit reference.

## Verification

- Full suite on the newest interpreter available; the targeted module
  additionally run complete under a Python 3.9 when one is present
  (`python3.9 -m unittest tests.test_plan_lint -v`) — this module is a
  required gate and must not deepen the recorded 3.9 floor problem.
- Guard proof, hermetic (never mutate the tracked file): copy
  `tests/test_plan_lint.py` to a temp directory; in the copy, neutralize
  one detector (e.g. empty `LEAKAGE_PHRASES`, force `is_closed` True,
  bump the length bound, drop the stale-path branch, empty the corpus
  glob); load the copy by path with `unittest` and observe its targeted
  fixtures go red; discard the copy; repeat per detector and for the
  aggregator; then run the real module and full suite green. Record the
  red/green table in the closure commit message.
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
  lines); a leakage phrase split across a multi-line span would
  false-positive — no such case exists in the corpus, and the allow
  marker is the escape if one appears.
