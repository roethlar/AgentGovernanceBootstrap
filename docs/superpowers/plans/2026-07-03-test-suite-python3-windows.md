# Test suite: interpreter-portable `python3` on Windows Store-stub hosts

Status: DRAFT 2026-07-03 (owner go same session: "plan and fix").

## Why this plan exists

On a stock Windows host, `python3` on PATH is the Microsoft Store App
Execution Alias stub (exit 9009, runs nothing). The product was hardened
against this twice — the discovery interpreter probe (2026-06-10) and the
shipped hook commands' `py -3 || python3` fallback (2026-07-02, Adopted) —
but the test suite itself still assumes a working `python3`. Observed
2026-07-03 on this Windows 11 host (suite run under `py -3` from Git Bash):
142 tests, 12 failures + 4 errors — 15 share one root cause in two shapes,
plus one unrelated Windows path-separator assertion (below):

1. **argv invocations**: `tests/test_discover.py:609` and
   `tests/test_run_fixture.py:748` run scripts via
   `subprocess.run(["python3", script])` — the stub exits 9009.
   `test_tripwire_script_fires_on_agents_md_only_and_never_blocks` fails
   asserting `9009 != 0`; the four `TestGovernanceHooks.test_guard_*` error.
2. **shell command strings**: fixture `verify` commands embed `python3 …` —
   the synthetic fixtures built inside `test_run_fixture.py` (lines 80, 86,
   205, 215, 235) and the frozen eval fixtures
   `evals/fixtures/py_{boxes_ceildiv,page_size,vault_twopath}` exercised by
   `TestFrozenFixturesDiscriminate`. `run_fixture.run_command` executes them
   `shell=True` (→ cmd.exe on Windows), the stub yields exit 9009, and
   scoring/discrimination assertions fail.

Worse than red: two green tests are **vacuous on Windows** —
`test_gate_allows_when_visible_green` and `test_guard_allows_source_edit`
assert the hook emits no decision, and a stub that runs nothing also emits
no decision. On this host they pass without testing anything.

## The fix (tests only; no product code, no frozen eval data)

Windows suite support is scoped to Git Bash PATH semantics, consistent with
the 2026-07-02 decision (Git for Windows is already required; its `usr/bin`
supplies the `sh`/`test`/`true`/`false` the fixtures also use).

1. **argv call sites → `sys.executable`.** `tests/test_discover.py:609` and
   `tests/test_run_fixture.py:748` invoke the script with the interpreter
   already running the suite. Correct on every platform; no probe needed.
2. **A `python3` PATH shim for shell command strings.** New helper
   `tests/_pyshim.py`: probe `python3 -c "print('ok')"`; if it does not
   print `ok` with exit 0 (missing, stub, or broken), create a temp dir
   containing a `python3` shim that execs `sys.executable` — `python3.bat`
   (`@"<sys.executable>" %*`) on Windows, an executable sh script on POSIX —
   and prepend it to `os.environ["PATH"]` for the test process. Idempotent;
   a no-op on any host where `python3` works, so POSIX runs are unchanged.
   `tests/test_run_fixture.py` calls it from `setUpModule`. This honors the
   fixtures' declared `python3` contract instead of rewriting fixture data —
   the frozen `evals/fixtures/*/fixture.json` stay byte-identical.
3. **Path-separator assertion** (`tests/test_run_fixture.py`
   `TestPolyglotFixture`, ~:1109): the 16th red test asserts
   `copy_dir.endswith("/practice/foo")`, but `polyglot_fixture.build` writes
   `str(ex_dir)` — a host-local native path that `run_fixture` consumes via
   `Path()` (either separator is valid on Windows). The assumption lives
   only in the test: normalize separators before the `endswith`. Fixture
   data stays native.
4. **`.agents/repo-guidance.md` Verification** gains the Windows note: run
   the suite as `py -3 -m unittest discover -s tests -v` from Git Bash; the
   suite self-shims `python3` for its subprocesses.

## Verification

Guard proof is the red→green delta on this host: 12F+4E before (twice
confirmed, including on a stashed clean tree), 0 after, same 142 tests, with
the two previously-vacuous hook tests now exercising the real scripts
(spot-check: guard emits an actual `deny` JSON on the deny cases). POSIX
behavior is unchanged by construction (shim is probe-gated); not re-run on a
POSIX host this session — noted as the residual risk. `git diff --check`
clean.

## Commits

1. this plan.
2. the fix (`tests/_pyshim.py`, two argv call sites, `setUpModule`,
   repo-guidance note) + suite run.
