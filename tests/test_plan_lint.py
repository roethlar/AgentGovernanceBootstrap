"""Lint still-open plan documents for chat leakage, stale path references,
and bloat, per docs/superpowers/plans/2026-07-10-plan-lint-suite.md.

Scans docs/superpowers/plans/*.md. Plans dated before 2026-07-10 are exempt
history; closed plans are exempt from content checks. Part of the normal
suite, and the targeted gate for plan-only changes."""
from __future__ import annotations

import datetime
import re
import sys
import tempfile
import unittest
import unittest.mock
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import refresh  # noqa: E402

try:
    from tests.test_refresh import init_repo, commit_all
except ImportError:  # top-level import under `unittest discover -s tests`
    from test_refresh import init_repo, commit_all

Finding = namedtuple("Finding", "path line kind detail")

LEAKAGE_PHRASES = (
    "this session", "this conversation", "in this chat",
    "as discussed", "per our discussion", "approved in chat",
    "approval in chat", "wording from chat",
)

CUTOFF = datetime.date(2026, 7, 10)
MAX_LINES = 600
ALLOW_MARKER = "plan-lint: allow"
PLANS_DIR = "docs/superpowers/plans"

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_INLINE_CODE = re.compile(r"(?<!`)(`+)([^`\n]+?)\1(?!`)")
_STATUS = re.compile(
    r"^ {0,3}(?:Status:|\*\*Status:\*\*|\*\*Status\*\*:)(?!:)[ \t]*(.*)$")
_CLOSED = re.compile(
    r"(?i)^[ \t]*\**[ \t]*"
    r"(CLOSED|DONE|SUPERSEDED|IMPLEMENTED|WITHDRAWN|REJECTED)"
    r"\**[ \t]*($|[ \t](\d{4}-\d{2}-\d{2})\b.*)")
_DATE_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def mask_code(text):
    """Line-count-preserving mask of fenced blocks and inline code spans."""
    lines = text.splitlines()
    out = []
    i, n = 0, len(lines)
    while i < n:
        m = _FENCE_OPEN.match(lines[i])
        if m:
            run = m.group(1)
            closer = re.compile(
                "^ {0,3}" + re.escape(run[0]) + "{" + str(len(run)) + ",}[ \t]*$")
            j = i + 1
            while j < n and not closer.match(lines[j]):
                j += 1
            end = j if j < n else n - 1  # unclosed fence masks to EOF
            out.extend([""] * (end - i + 1))
            i = end + 1
        else:
            out.append(_INLINE_CODE.sub(lambda s: " " * len(s.group(0)), lines[i]))
            i += 1
    return "\n".join(out)


def plan_status(masked):
    """First canonical Status line of the masked text, or None."""
    for line in masked.splitlines():
        m = _STATUS.match(line)
        if m:
            return m.group(1)
    return None


def is_closed(status):
    """Bare closure marker, or marker + valid ISO date + detail. Anything
    else - qualified closures, invalid dates, open/unknown wording - is open."""
    m = _CLOSED.match(status)
    if not m:
        return False
    if m.group(3):
        try:
            datetime.date.fromisoformat(m.group(3))
        except ValueError:
            return False
    return True


def plan_date(name):
    """Valid leading YYYY-MM-DD- date of a plan filename, or None."""
    m = _DATE_NAME.match(name)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _missing_date(rel):
    return [Finding(rel, 0, "missing-date",
                    "filename lacks a valid YYYY-MM-DD- prefix")]


def _missing_status(rel):
    return [Finding(rel, 0, "missing-status", "no canonical Status: line")]


def _stale_paths(repo_root, rel, orig_lines, allow, cache):
    findings = []
    seen = set()
    for i, line in enumerate(orig_lines):
        if i in allow:
            continue
        for m in refresh.PATH_TOKEN.finditer(line):
            tok = m.group(1)
            if tok in seen or not refresh._lintable_repo_path(tok):
                continue
            seen.add(tok)
            if (repo_root / tok.rstrip("/")).exists():
                continue
            dh = refresh._deletion_commit(repo_root, tok, cache)
            if dh:
                findings.append(Finding(
                    rel, i + 1, "stale-path",
                    "`{}` deleted in {}".format(tok, dh)))
    return findings


def scan_plan(repo_root, rel_path, cache=None, history=True):
    cache = {} if cache is None else cache
    repo_root = Path(repo_root)
    rel = Path(rel_path).as_posix()
    text = (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")
    name = Path(rel_path).name

    date = plan_date(name)
    if date is not None and date < CUTOFF:
        return []  # grandfathered history; status not consulted
    findings = []
    if date is None:
        findings += _missing_date(rel)

    masked = mask_code(text)
    status = plan_status(masked)
    if status is None:
        return findings + _missing_status(rel)
    if is_closed(status):
        return findings

    orig_lines = text.splitlines()
    allow = {i for i, ln in enumerate(orig_lines) if ALLOW_MARKER in ln}
    seen = set()
    for i, line in enumerate(masked.splitlines()):
        if i in allow:
            continue
        low = line.lower()
        for phrase in LEAKAGE_PHRASES:
            if phrase in low and (i + 1, phrase) not in seen:
                seen.add((i + 1, phrase))
                findings.append(Finding(rel, i + 1, "leakage", phrase))
    if history:
        findings += _stale_paths(repo_root, rel, orig_lines, allow, cache)
    if len(orig_lines) > MAX_LINES:
        findings.append(Finding(
            rel, 0, "too-long",
            "{} physical lines > {}".format(len(orig_lines), MAX_LINES)))
    return findings


def scan_corpus(repo_root, history=True):
    repo_root = Path(repo_root)
    files = sorted((repo_root / PLANS_DIR).glob("*.md"))
    assert files, "plan corpus glob is empty: {}/{}".format(repo_root, PLANS_DIR)
    cache = {}
    findings = []
    for f in files:
        findings.extend(scan_plan(repo_root, f.relative_to(repo_root),
                                  cache=cache, history=history))
    return findings


# ---------------------------------------------------------------- fixtures

# Literal copies, never derived from the module constants: neutralizing a
# constant during the guard proof must turn these red, not delete them.
FIXTURE_PHRASES = (
    "this session", "this conversation", "in this chat",
    "as discussed", "per our discussion", "approved in chat",
    "approval in chat", "wording from chat",
)
FIXTURE_MARKERS = ("CLOSED", "DONE", "SUPERSEDED", "IMPLEMENTED",
                   "WITHDRAWN", "REJECTED")
OPEN_NAME = "2026-07-10-x.md"
PHRASE = "this session"  # planted literal used by single-phrase fixtures


def write_file(root, name, body):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), "w", newline="\n") as f:
        f.write(body)
    return path


def open_doc(body_lines):
    return "\n".join(["Status: APPROVED 2026-07-10 — fixture", ""] +
                     list(body_lines)) + "\n"


class ScanFixture(unittest.TestCase):
    def scan(self, name, body, history=False):
        with tempfile.TemporaryDirectory() as tmp:
            write_file(tmp, name, body)
            return scan_plan(tmp, name, history=history)

    def kinds(self, findings):
        return sorted(set(f.kind for f in findings))


class LeakageTests(ScanFixture):
    def test_constants_match_fixture_literals(self):
        self.assertEqual(LEAKAGE_PHRASES, FIXTURE_PHRASES)

    def test_each_phrase_found_at_exact_line(self):
        for phrase in FIXTURE_PHRASES:
            found = self.scan(OPEN_NAME, open_doc(["clean", "x " + phrase + " y"]))
            self.assertEqual(
                [(OPEN_NAME, 4, "leakage", phrase)], list(map(tuple, found)),
                phrase)

    def test_case_insensitive(self):
        found = self.scan(OPEN_NAME, open_doc(["THIS Session here"]))
        self.assertEqual([f.kind for f in found], ["leakage"])

    def test_phrase_in_inline_span_ignored(self):
        self.assertEqual([], self.scan(OPEN_NAME, open_doc(["a `this session` b"])))

    def test_phrase_in_fence_ignored(self):
        self.assertEqual([], self.scan(
            OPEN_NAME, open_doc(["```", "this session", "```"])))

    def test_allow_marker_same_line_only(self):
        allowed = open_doc(["this session <!-- plan-lint: allow -->"])
        self.assertEqual([], self.scan(OPEN_NAME, allowed))
        adjacent = open_doc(["<!-- plan-lint: allow -->", "this session"])
        self.assertEqual(["leakage"], self.kinds(self.scan(OPEN_NAME, adjacent)))


class MaskTests(ScanFixture):
    def test_tilde_and_long_fences_mask(self):
        for opener, closer in (("~~~", "~~~"), ("````", "````")):
            body = open_doc([opener, PHRASE, closer])
            self.assertEqual([], self.scan(OPEN_NAME, body), opener)

    def test_three_space_fence_masks_four_space_does_not(self):
        self.assertEqual([], self.scan(
            OPEN_NAME, open_doc(["   ```", PHRASE, "   ```"])))
        found = self.scan(OPEN_NAME, open_doc(["    ```", PHRASE, "    ```"]))
        self.assertEqual(["leakage"], self.kinds(found))

    def test_false_closer_with_trailing_text_does_not_close(self):
        body = open_doc(["```", "``` trailing", PHRASE])  # unclosed -> EOF
        self.assertEqual([], self.scan(OPEN_NAME, body))

    def test_line_numbers_survive_a_fence(self):
        fence = ["```"] + ["code"] * 8 + ["```"]
        found = self.scan(OPEN_NAME, open_doc(fence + ["x " + PHRASE]))
        self.assertEqual(found[0].line, 2 + len(fence) + 1)

    def test_mismatched_backtick_runs_do_not_mask(self):
        found = self.scan(OPEN_NAME, open_doc(["``" + PHRASE + "`"]))
        self.assertEqual(["leakage"], self.kinds(found))

    def test_equal_runs_mask(self):
        self.assertEqual([], self.scan(OPEN_NAME, open_doc(["``" + PHRASE + "``"])))


class StatusTests(ScanFixture):
    def test_canonical_forms_parse(self):
        for header in ("Status: DRAFT", "**Status:** DRAFT", "**Status**: DRAFT"):
            self.assertIsNotNone(plan_status(header), header)

    def test_noncanonical_forms_are_missing_status(self):
        for header in ("status: CLOSED", "Status CLOSED", "Status:: CLOSED",
                       "\tStatus: CLOSED", "    Status: CLOSED",
                       "* Status: CLOSED", "Status", ": CLOSED"):
            found = self.scan(OPEN_NAME, header + "\n\n" + PHRASE + "\n")
            self.assertIn("missing-status", self.kinds(found), header)

    def test_split_line_status_is_missing(self):
        found = self.scan(OPEN_NAME, "Status\n: CLOSED\n" + PHRASE + "\n")
        self.assertIn("missing-status", self.kinds(found))

    def test_first_status_wins(self):
        body = "Status: APPROVED 2026-07-10\n\nStatus: CLOSED\n" + PHRASE + "\n"
        self.assertEqual(["leakage"], self.kinds(self.scan(OPEN_NAME, body)))

    def test_fenced_fake_status_is_missing(self):
        body = "```\nStatus: CLOSED\n```\n" + PHRASE + "\n"
        self.assertIn("missing-status", self.kinds(self.scan(OPEN_NAME, body)))


class ClosureTests(ScanFixture):
    def test_is_closed_table(self):
        closed = [m for m in FIXTURE_MARKERS]
        closed += [m + " 2026-07-12 — detail" for m in FIXTURE_MARKERS]
        closed += ["**CLOSED**", "closed 2026-07-12 x"]
        for status in closed:
            self.assertTrue(is_closed(status), status)
        open_forms = ["CLOSED for Artifact 1", "CLOSED — part 2 remains",
                      "DONE except X", "CLOSED2026-07-12",
                      "CLOSED 2026-99-99 x", "DRAFT", "APPROVED 2026-07-10",
                      "Open", "gibberish", ""]
        for status in open_forms:
            self.assertFalse(is_closed(status), status)

    def test_closed_scanner_docs_exempt_planted_phrase(self):
        for status in ("CLOSED", "CLOSED 2026-07-12 — landed"):
            body = "Status: " + status + "\n\n" + PHRASE + "\n"
            self.assertEqual([], self.scan(OPEN_NAME, body), status)

    def test_open_scanner_docs_report_planted_phrase(self):
        for status in ("CLOSED for Artifact 1", "CLOSED 2026-99-99 x",
                       "CLOSED2026-07-12", "DRAFT"):
            body = "Status: " + status + "\n\n" + PHRASE + "\n"
            self.assertEqual(["leakage"], self.kinds(self.scan(OPEN_NAME, body)),
                             status)


class DateTests(ScanFixture):
    def test_pre_cutoff_grandfathered_entirely(self):
        body = PHRASE + "\n"  # no status, leakage - all exempt
        self.assertEqual([], self.scan("2026-06-01-x.md", body))

    def test_post_cutoff_without_status(self):
        found = self.scan(OPEN_NAME, "no status here\n")
        self.assertEqual(["missing-status"], self.kinds(found))

    def test_undatable_names_get_missing_date_and_content_checks(self):
        for name in ("notes.md", "2026-07-09notes.md", "0000-00-00-x.md"):
            found = self.scan(name, open_doc([PHRASE]))
            self.assertEqual(["leakage", "missing-date"], self.kinds(found), name)


class LengthTests(ScanFixture):
    def doc_of_lines(self, n_physical):
        head = ["Status: APPROVED 2026-07-10 — fixture", ""]
        return "\n".join(head + ["x"] * (n_physical - len(head))) + "\n"

    def test_boundary(self):
        body = self.doc_of_lines(600)
        self.assertEqual(600, len(body.splitlines()))
        self.assertEqual([], self.scan(OPEN_NAME, body))
        self.assertEqual(["too-long"],
                         self.kinds(self.scan(OPEN_NAME, self.doc_of_lines(601))))

    def test_blank_heavy_counts_physical_lines(self):
        head = ["Status: APPROVED 2026-07-10 — fixture", ""]
        lines = head + ["x", "", ""] * 233  # 2 + 699 = 701 physical, ~235 non-blank
        body = "\n".join(lines) + "\n"
        self.assertGreater(len(body.splitlines()), 600)
        self.assertEqual(["too-long"], self.kinds(self.scan(OPEN_NAME, body)))


def repo_with_deleted(tmp, token="docs/gone.md"):
    root = Path(tmp) / "repo"
    init_repo(root)
    write_file(root, token, "old\n")
    commit_all(root, "add")
    (root / token).unlink()
    commit_all(root, "delete " + token)
    return root


class StalePathTests(unittest.TestCase):
    def test_deleted_token_flagged_never_existed_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = repo_with_deleted(tmp)
            body = open_doc(["see `docs/gone.md` and `docs/future-file.md`"])
            write_file(root, OPEN_NAME, body)
            found = scan_plan(root, OPEN_NAME, history=True)
            self.assertEqual([("stale-path", 3)],
                             [(f.kind, f.line) for f in found])
            self.assertIn("docs/gone.md", found[0].detail)

    def test_allow_marker_same_line_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = repo_with_deleted(tmp)
            ok = open_doc(["`docs/gone.md` <!-- plan-lint: allow -->"])
            write_file(root, OPEN_NAME, ok)
            self.assertEqual([], scan_plan(root, OPEN_NAME, history=True))
            adj = open_doc(["<!-- plan-lint: allow -->", "`docs/gone.md`"])
            write_file(root, OPEN_NAME, adj)
            found = scan_plan(root, OPEN_NAME, history=True)
            self.assertEqual(["stale-path"], [f.kind for f in found])

    def test_corpus_cache_makes_one_git_log_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = repo_with_deleted(tmp)
            body = open_doc(["ref `docs/gone.md`"])
            write_file(root, PLANS_DIR + "/2026-07-10-a.md", body)
            write_file(root, PLANS_DIR + "/2026-07-10-b.md", body)
            real_git = refresh.git
            log_calls = []

            def counting_git(repo, *args, **kwargs):
                if args and args[0] == "log":
                    log_calls.append(args)
                return real_git(repo, *args, **kwargs)

            with unittest.mock.patch.object(refresh, "git", counting_git):
                found = scan_corpus(root, history=True)
            self.assertEqual(["stale-path", "stale-path"],
                             sorted(f.kind for f in found))
            self.assertEqual(1, len(log_calls))


class AggregatorTests(unittest.TestCase):
    def test_scan_corpus_wires_every_detector_and_exemption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = repo_with_deleted(tmp)
            plans = PLANS_DIR + "/"
            write_file(root, plans + "2026-07-10-leak.md", open_doc([PHRASE]))
            write_file(root, plans + "2026-07-10-stale.md",
                       open_doc(["`docs/gone.md`"]))
            long_doc = "\n".join(
                ["Status: APPROVED 2026-07-10 — fixture", ""] + ["x"] * 601) + "\n"
            write_file(root, plans + "2026-07-10-long.md", long_doc)
            write_file(root, plans + "notes.md", open_doc(["clean"]))
            write_file(root, plans + "2026-07-10-nostatus.md", "just text\n")
            write_file(root, plans + "2026-07-10-closed.md",
                       "Status: CLOSED 2026-07-10 — done\n\n" + PHRASE + "\n")
            write_file(root, plans + "2026-06-01-old.md", PHRASE + "\n")
            found = scan_corpus(root, history=True)
            expected = {
                ("2026-07-10-leak.md", "leakage"),
                ("2026-07-10-stale.md", "stale-path"),
                ("2026-07-10-long.md", "too-long"),
                ("notes.md", "missing-date"),
                ("2026-07-10-nostatus.md", "missing-status"),
            }
            got = {(Path(f.path).name, f.kind) for f in found}
            self.assertEqual(expected, got)

    def test_empty_corpus_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / PLANS_DIR).mkdir(parents=True)
            with self.assertRaises(AssertionError):
                scan_corpus(tmp, history=False)


class CorpusGateTests(unittest.TestCase):
    repo_root = Path(refresh.__file__).resolve().parent.parent

    def test_corpus_clean(self):
        files = sorted((self.repo_root / PLANS_DIR).glob("*.md"))
        self.assertGreaterEqual(len(files), 25)
        self.assertEqual([], scan_corpus(self.repo_root, history=False))

    def test_corpus_stale_paths(self):
        shallow = refresh.git(self.repo_root, "rev-parse",
                              "--is-shallow-repository", check=False)
        if shallow.stdout.strip() == "true":
            self.skipTest("shallow clone: deletion history unavailable")
        self.assertEqual([], scan_corpus(self.repo_root, history=True))


if __name__ == "__main__":
    unittest.main()
