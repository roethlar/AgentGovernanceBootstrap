# Plan: port the governance guard to codex

Status: APPROVED 2026-08-01 — owner collapsed the original six-phase
draft to this single item; all other phases are withdrawn (the full
draft, its openreview verdict, and the owner's per-item rulings are
in this file's git history). Implementation starts on the owner's
word.

## History

Openreview outcome (recorded here as the review-outcome home):
openreview codex (gpt-5.6-sol @ xhigh, competitive) over
`8bb748a..1dd3788`: acceptable_with_changes; all six material
changes ruled 2026-08-01; the adopted ones relevant to this item
(codex `apply_patch` target parsing; portable verification
interpreter) are folded in below. Cross-phase owner rulings that
bind this work: a hook may only enforce what is already absolutely
forbidden to an agent acting alone; a single-repo request never
widens into a shipped-set change without the owner's explicit word;
installed `AGENTS.md` stays toolkit-owned, and deny messages name
the repo-local route that sticks (`.agents/repo-guidance.md`).

## Goal

`templates/hooks/claude/protect-governance.py` blocks agent edits to
installed governance files on Claude Code. Make the same protection
fire on codex, which is verified capable of running it
(`docs/harness-capabilities.md`, 2026-08-01 ledger): codex 0.146.0
runs repo-local `.codex/hooks.json` (Claude-compatible schema) in
exec mode, and blocks **only** via stdout JSON
`{"hookSpecificOutput": {"hookEventName": "PreToolUse",
"permissionDecision": "deny", ...}}` — exit 2 is logged as a hook
failure and the tool proceeds.

## Slices

1. **Deny shape.** Probe the JSON deny on Claude Code (its current
   positive covers exit-2 only). If positive: one code path, JSON
   deny everywhere. If not: branch — Claude Code sets
   `CLAUDE_PROJECT_DIR`, codex does not; exit-2 under it, JSON
   otherwise. The deny message names the route that sticks:
   repo-local rules go to `.agents/repo-guidance.md`. Ledger entry;
   `formerly[]` append for the hook file.
2. **`apply_patch` target parsing.** The script reads only
   `tool_input.file_path` / `notebook_path`, which codex's
   `apply_patch` payload does not carry — target paths arrive inside
   the patch text in `tool_input`
   (`docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`
   records the shape). Parse all paths in a patch; any protected
   path denies the whole patch. Unit tests: protected, unprotected,
   and mixed multi-file patches on both payload shapes; existing
   Claude-shape behavior unchanged and still covered.
3. **Ship the codex hook config.** Revive
   `templates/hooks/codex/hooks.json` <!-- plan-lint: allow -->
   (path retired in `0af5d31`), target `.codex/hooks.json`, class
   `replace`: a `PreToolUse` entry running the one canonical script
   at `.claude/hooks/protect-governance.py`. The target sits in
   `tools/shipped-set.json` `retired[]` with four historical hashes:
   move it to `artifacts[]` keeping every hash in `formerly[]` (a
   target may not appear in both lists — manifest validation).
   Interpreter selection reuses the viability-probed
   `py -3`/`python3`/`python` chain from
   `templates/hooks/claude/settings.json`; probe how codex executes
   hook commands on Windows (`commandWindows` exists) before fixing
   the command shape.
4. **Trust write.** Codex runs a repo's hooks only behind
   `[features] hooks = true`, project trust, and a per-handler hash
   pin. No printed instructions (owner ruling — interactive codex
   surfaces trust itself). For headless activation: probe a
   codex-native non-interactive trust surface first (whatever the
   TUI `/hooks` writes through); failing that, a deterministic
   script — parse `~/.codex/config.toml` → backup → append the one
   `[hooks.state]` pin (hash recipe from codex-rs source,
   probe-verified) → re-parse → abort-and-restore on mismatch.
   Either path asks the owner once, at install/update time, before
   writing. Agent judgment never touches the TOML.
5. **Live proof.** In a fixture repo with the installed set: a codex
   `apply_patch` against `AGENTS.md` is denied by the installed hook
   without the trust-bypass flag; Claude Code still blocks via its
   shipped path; outcomes recorded in the capability ledger.

One slice per commit, suite green per slice.

## Verification

Interpreter: resolve `<probed-python>` per `procedures/bootstrap.md`
Step 1 (floor 3.10); the executing machine's resolved command and
environment are in `.agents/machines.md`.

1. `<probed-python> -m unittest discover -s tests -v` per slice.
2. Guard proof for each new test: revert the paired change, test
   fails, restore, green.
3. Live probes per the verify-once gate, outcomes into
   `docs/harness-capabilities.md`.
4. `git diff --check`; this file:
   `<probed-python> -m unittest tests.test_plan_lint -v`.

## Rollout boundary

Landing here changes what ships, not what is installed anywhere:
this repo's installed copies lag until the owner's self-refresh from
the product clone, and Bixi receives the change only on the owner's
`publish` word. Neither is authorized by this plan. Per-repo codex
trust remains an owner action.
