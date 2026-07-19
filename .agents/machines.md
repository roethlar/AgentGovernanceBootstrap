# Machine Facts

Machine-specific facts, one heading per machine, each fact dated. Written
by `handoff`, pruned by `drift` (rule adopted 2026-07-10; see
`.agents/decisions.md` archive and the `handoff`/`drift` operator bullets).
Facts here are true on the named machine only — never treat them as
repo-portable.

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
