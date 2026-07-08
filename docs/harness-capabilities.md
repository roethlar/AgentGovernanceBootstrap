# Per-harness capability record

The durable record of verified facts about how each agent harness loads
governance and supports hooks. This file is the seed input and the durable
home for the toolkit's **verify-once gate**: a harness adapter (hook config,
wrapper set) ships only after a live check on that harness confirms the
mechanism fires; every check's outcome — positive or negative — is recorded
here with its date. Facts below marked "global" describe user-level config,
not the repo-level configs the toolkit ships; do not cite them as evidence
for repo-level behavior.

(Salvaged 2026-07-08 from the closed eval workstream's
`evals/harness-capabilities.md`; original validated 2026-06-29, eval-lane
apparatus dropped. Full original in git history.)

## Governance loading (verified 2026-06-29)

| harness | governance load vector |
|---|---|
| Claude Code | `CLAUDE.md` (+`@AGENTS.md` import). A bare `AGENTS.md` with no `CLAUDE.md` is **inert** in headless mode — the shim is load-bearing. |
| codex | `AGENTS.md` natively — no shim needed. Does not need `CLAUDE.md`. |
| grok | `AGENTS.md` (also reads `CLAUDE.md`; does NOT read `.cursorrules`). |
| agy (Antigravity) | `AGENTS.md` + `GEMINI.md` — but **only with `--new-project`** in headless mode; a plain `--print` loads only the global `~/.gemini/GEMINI.md`. Does not read `CLAUDE.md`. |

## Hook support

| harness | pre-tool-use | session-start / compaction | stop / forced continuation |
|---|---|---|---|
| Claude Code | yes, blocking (verified) | **yes — `SessionStart` matcher `compact` (verified 2026-06-21; the one shipped hook)** | yes — Stop hook can force continuation (Claude-Code-only) |
| codex | yes — parses repo-level `.codex/hooks.json` in Claude schema (normalized to `pre_tool_use`); verified firing 2026-06-29 | **registered but never observed firing**: `session_start` appears in `~/.codex/config.toml` hook state from real repos, but an exec-mode live check (marker hook, 2026-07-08) fired 0 times and eval runs never saw it. Not shipped until a positive observation. | unconfirmed |
| grok | yes, blocking (global `~/.grok/hooks/*.json`; also auto-scans `~/.claude/settings.json`, `.cursor/hooks.json`) | repo-level hook config **unverified** (no hook surface in `--help`, 2026-07-08); shipped repo-level config retired | no — `Stop` passive; substitutes: `--check` / `--max-turns` flags |
| agy | yes — Claude-style events in **global** `~/.gemini/settings.json` (docs: antigravity.google/docs/hooks) | repo-level hook config **unverified** (no hook surface in `--help`, 2026-07-08); shipped repo-level config retired | no — `Stop` passive (`{"decision":"allow"}` only) |
| gemini CLI | — | **not checkable** on the dev machine (CLI not installed, 2026-07-08) | — |

Verify-once ledger:

- 2026-06-21 — Claude Code compaction re-ground: fires (validated when built). Shipped.
- 2026-06-29 — codex `pre_tool_use` from repo-level `.codex/hooks.json`: fires (eval runs, 13–15×/cell). (The tripwire it carried was later retired on the merits, not for non-firing.)
- 2026-07-08 — codex `session_start`: negative (exec-mode marker check, 0 fires; consistent with all prior runs). Re-ground not shipped for codex.
- 2026-07-08 — grok, agy repo-level hook configs: unverified, no help surface; retired. gemini CLI: absent, not checkable.

## Operational harness facts

- Pin models explicitly; unpinned defaults bite (grok's default is
  `grok-composer-2.5-fast`, not Grok Build — use `-m grok-build`).
- agy's OAuth token is short-lived and does not refresh headless; re-auth
  interactively at session start if lapsed.
- agy in a write-blocked workspace does not fail gracefully (it hunts for
  privilege escalation instead of reporting); ensure the workspace is
  writable.
- codex headless: `codex exec` with the prompt piped via **stdin** (the argv
  form has hung); `--skip-git-repo-check` for untrusted dirs.
