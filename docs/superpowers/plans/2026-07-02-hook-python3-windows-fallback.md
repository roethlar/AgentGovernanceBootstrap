# Hook templates: replace bare `python3` with a `py -3 || python3` fallback chain

Status: DRAFT 2026-07-02, awaiting owner approval.

## Why this plan exists

Harvest bug `roethlar/agent-harvest` →
`bugs/ExchangeAdminWeb-hook-python3-discovery-2026-07-02.md` (filed from an
ExchangeAdminWeb bootstrap run on Windows, toolkit @ ca53e71): the AGENTS.md
pre-edit tripwire hook is invoked via bare `python3`. On a stock Windows host
`python3` on PATH is a Microsoft Store App Execution Alias stub, not an
interpreter, so the `PreToolUse` hook runs the stub, prints nothing, and the
advisory reminder never fires — no error, no signal, the hook is silently
inert. Verified against this repo: `templates/hooks/claude/settings.json:9`
and `templates/hooks/codex/hooks.json:9` hardcode `python3`, while the
bootstrap procedure's own Step 1 interpreter probe (`procedures/bootstrap.md`
~95-106) already documents this exact stub pitfall and prescribes probing
`py -3` first. The lesson was applied to discovery but never to the hook
templates. `procedures/bootstrap.md:243` additionally overclaims the tripwire
invocation as "portable" — the path resolution is; the interpreter is not.

Harness facts (Claude Code hooks docs, code.claude.com/docs/en/hooks.md,
checked 2026-07-02):

- Shell-form hook commands run via `sh -c` on macOS/Linux; on Windows via
  **Git Bash if installed, else PowerShell**. There is no OS-conditional hook
  mechanism — one committed command string serves every machine.
- `${CLAUDE_PROJECT_DIR}` (braced) is substituted by Claude Code itself before
  the shell sees it; the current unbraced `$CLAUDE_PROJECT_DIR` relies on
  POSIX shell env expansion.

Owner decision (2026-07-02, this session): Git for Windows is already a
Claude Code requirement, so targeting the Git Bash path on Windows is
acceptable; PowerShell-only Windows hosts are out of scope for the hook
command. Recorded in `.agents/decisions.md`.

## The fix

One POSIX-compatible command line per hook, interpreter-adaptive, mirroring
the procedure's probe order (`py -3` first, `python3` fallback):

`templates/hooks/claude/settings.json` (and this repo's byte-identical
`.claude/settings.json`):

```
py -3 "${CLAUDE_PROJECT_DIR}/.claude/agents-md-tripwire.py" 2>/dev/null || python3 "${CLAUDE_PROJECT_DIR}/.claude/agents-md-tripwire.py"
```

`templates/hooks/codex/hooks.json`:

```
py -3 "$(git rev-parse --show-toplevel)/.codex/agents-md-tripwire.py" 2>/dev/null || python3 "$(git rev-parse --show-toplevel)/.codex/agents-md-tripwire.py"
```

Behavior: on Windows (Git Bash) `py` is the real launcher and runs first —
the stub is never touched. On POSIX, `py` is normally absent, the first leg
fails silently (stderr suppressed covers the `command not found` noise), and
`python3` runs as today. Braced `${CLAUDE_PROJECT_DIR}` makes the Claude path
resolution shell-independent as a bonus. Accepted edge: if `py -3` exists but
the script itself crashes, the `||` retries under `python3` — a duplicate run
of an advisory, idempotent, exit-0 script; harmless.

## Assumptions (labeled)

- Codex CLI's Windows hook shell is unverified. The codex template already
  assumes a POSIX shell (`$(git rev-parse …)` command substitution); this fix
  improves the interpreter half under that same standing assumption and does
  not widen the codex template's Windows claims.
- The bite proof from the bug report (edit AGENTS.md on a Windows host,
  confirm the reminder appears) cannot be run here; Windows behavior rests on
  the harness docs plus the reporter's evidence. POSIX behavior is verified
  locally (see S2).

## Slices

- S1 (docs): this plan + decision entry in `.agents/decisions.md`
  (Git-Bash-on-Windows scope for hook commands; interpreter fallback chain as
  the standing pattern for shipped hooks that invoke Python).
  Verification: `git diff --check`. — commit:
- S2 (code): apply the two template command edits; mirror
  `templates/hooks/claude/settings.json` into `.claude/settings.json`
  byte-identically (repo-guidance requires the copies not desync); strengthen
  `tests/test_discover.py::test_tripwire_hook_present_advisory_and_portable`
  to pin the fallback chain (assert `py -3` leg, `||`, `python3` fallback, and
  braced `${CLAUDE_PROJECT_DIR}` in the claude command) — the current
  assertion (`python3` substring) passes on both old and new bytes, so it
  does not guard this fix. Guard proof per Verification invariant: revert the
  template edit, confirm the strengthened test fails, restore, confirm suite
  green. POSIX smoke: pipe the tripwire an AGENTS.md payload through the new
  command string under `sh` on this machine and confirm `additionalContext`
  appears. Verification: `python3 -m unittest discover -s tests -v`.
  — commit:
- S3 (docs/procedure): fix `procedures/bootstrap.md` — replace the line-243
  "portable" interpreter overclaim with the fallback-chain description and
  the Git Bash-on-Windows scope note; add a pointer from the Step 1 probe
  rationale if natural. Procedures ship to target repos, so run the suite.
  Verification: `python3 -m unittest discover -s tests -v` +
  `git diff --check`. — commit:
- S4 (docs): update `.agents/state.md`, fill this commit map, mark the plan
  DONE. Verification: `git diff --check`. — commit:

## Non-goals

- No PowerShell / pwsh variant, no dual-script dispatch, no `shell` field —
  ruled out by the owner's Git Bash scope decision and by the absence of
  OS-conditional hooks in the harness.
- No change to `agents-md-tripwire.py` itself (its `#!/usr/bin/env python3`
  shebang is inert under both invocation legs — the interpreter is named
  explicitly by the command).
- No edit to the harvest bug report's status. Updating it to fix-landed is an
  outward push to another repo; follow-up on explicit owner go, via the
  harvest procedure.
