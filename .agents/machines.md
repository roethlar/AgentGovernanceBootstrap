# Machine Facts

Machine-specific facts, one heading per machine, each fact dated. Written
by `handoff`, pruned by `catchup` (the hygiene sweep moved there when the
`drift` word retired 2026-07-23, owner-surface D4; see
`.agents/decisions.md`). Facts here are true on the named machine only —
never treat them as repo-portable.

## nagatha (macOS)

- 2026-07-10: stock `python3` is 3.9.6 — below the 3.10 floor; run the
  suite with `python3.14` (Homebrew). The targeted plan lint
  (`tests/test_plan_lint.py`) still runs complete on stock 3.9.
- 2026-07-10: harness CLIs on PATH: `claude`, `codex` (codex-cli 0.144.1),
  `agy`, `grok`. Codex reviewer dispatch: pipe the prompt via stdin
  (`codex exec ... < prompt`); a codex review round at ultra effort runs
  roughly 15-25 minutes.
- 2026-07-18: the saved Claude Code default model on this machine is
  Fable 5 (set mid-session via `/model`); headless `claude -p` inherits
  the saved default — pin `--model` explicitly in anything scripted.
  Claude Code here is 2.1.214.
- 2026-07-18: local burn telemetry for audits:
  `~/.claude/projects/*/*.jsonl` carries per-turn `usage` on assistant
  lines (tool results arrive as `type:user` lines — do not count them
  as prompts); `~/.codex/sessions/**/rollout-*.jsonl` carries
  `token_count` events. Codex credits exhausted 2026-07-17 ~21:30.
- product-repo: /Users/michael/Dev/Bixi (recorded 2026-07-24, first publish)

## ASHBIAMWEB1 (Windows)

- 2026-07-30: two `tests/test_new_project.py` cases fail on this machine
  on a clean HEAD (`test_no_harness_prints_procedure_path` — the test's
  hard-coded `/usr/bin:/bin` PATH hides git.exe from the Windows
  subprocess; `test_print_python_finds_a_310_or_better`). Pre-existing,
  unrelated to any current work; the rest of the 195-test suite is green.
- 2026-07-27: `py -3` resolves to
  `C:\Program Files\Python314\python.exe` (Python 3.14.6). Set
  `PYTHONIOENCODING=utf-8` when running the suite so child Python output
  matches the tests' explicit UTF-8 subprocess decoding.
- product-repo: D:\source\Bixi (recorded 2026-07-27, first publish)

## netwatch-01 (Windows)

- 2026-07-31: `py -3` is 3.14.6
  (`C:\Users\michael\AppData\Local\Programs\Python\Launcher\py.exe`). Run
  the suite with `PYTHONUTF8=1` (same fact as ASHBIAMWEB1's 2026-07-27
  `PYTHONIOENCODING=utf-8` entry). Without it, `refresh.py`'s em dashes
  reach the tests' pipe as cp1252, the UTF-8 reader thread dies, and
  ~40 `test_refresh` cases error on `proc.stdout is None` instead of
  reporting anything — the suite is blinded, not red for cause.
- 2026-07-31: the two `test_new_project.py` failures recorded under
  ASHBIAMWEB1 reproduce here on a clean HEAD worktree; with UTF-8 mode
  on, they are the only failures.
- product-repo: F:\dev\Bixi (recorded 2026-07-30, first publish from
  this machine; publish.py's recorded-path lookup reads the first
  `product-repo:` line in this file, so on this machine the path must be
  passed explicitly: `py -3 tools/publish.py F:\dev\Bixi`)
