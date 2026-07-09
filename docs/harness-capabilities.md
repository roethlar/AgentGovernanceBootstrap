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
| codex | `AGENTS.md` natively — no shim needed. Does not need `CLAUDE.md`. **Does NOT process `@` imports** (documented: codex discovers/concatenates `AGENTS.override.md` + `AGENTS.md` + configured fallback filenames root-down; no include expansion — developers.openai.com/codex/guides/agents-md, checked 2026-07-08 via codex itself). `@.agents/repo-guidance.md` is literal text there; repo-guidance loads on codex only via the template's explicit read-it-directly instruction — a directed read, one diligence-hop weaker than injection. |
| grok | `AGENTS.md` (also reads `CLAUDE.md`; does NOT read `.cursorrules`). |
| agy (Antigravity) | `AGENTS.md` + `GEMINI.md` — but **only with `--new-project`** in headless mode; a plain `--print` loads only the global `~/.gemini/GEMINI.md`. Does not read `CLAUDE.md`. |

## Hook support

| harness | pre-tool-use | session-start / compaction | stop / forced continuation |
|---|---|---|---|
| Claude Code | yes, blocking (verified) | **yes — `SessionStart` matcher `compact` (verified 2026-06-21; the one shipped hook)** | yes — Stop hook can force continuation (Claude-Code-only) |
| codex | historical: `pre_tool_use` fired in eval runs 2026-06-29 (global `CODEX_HOME` config era). Repo-local: **dormant in exec mode** — differential probe 2026-07-08 on 0.143.0 (SessionStart + PreToolUse markers, one file) fired NEITHER, in an untrusted temp repo AND a trusted repo with registered hook state. | **negative, thoroughly**: 0 fires across 0.142.5 + 0.143.0, Claude-schema + snake_case, trusted + untrusted repos, exec mode (2026-07-08). Interactive mode untestable headless. Not shipped. | unconfirmed |
| codex **skills** | — | — | **POSITIVE (2026-07-08, codex-cli 0.143.0): codex discovers and invokes repo skills from `.agents/skills/<name>/SKILL.md`, untrusted repos included** (marker probe returned exactly). The operator wrapper set ships for codex as pointer skills (`templates/skills/codex/`), same pure-adapter class as `.claude/commands/`. |
| grok | yes, blocking (global `~/.grok/hooks/*.json`; also auto-scans `~/.claude/settings.json`, `.cursor/hooks.json`) | repo-level hook config **unverified** (no hook surface in `--help`, 2026-07-08); shipped repo-level config retired | no — `Stop` passive; substitutes: `--check` / `--max-turns` flags |
| agy | yes — Claude-style events in **global** `~/.gemini/settings.json` (docs: antigravity.google/docs/hooks) | repo-level hook config **unverified** (no hook surface in `--help`, 2026-07-08); shipped repo-level config retired | no — `Stop` passive (`{"decision":"allow"}` only) |
| gemini CLI | — | **not checkable** on the dev machine (CLI not installed, 2026-07-08) | — |

Verify-once ledger:

- 2026-06-21 — Claude Code compaction re-ground: fires (validated when built). Shipped.
- 2026-06-29 — codex `pre_tool_use` from repo-level `.codex/hooks.json`: fires (eval runs, 13–15×/cell). (The tripwire it carried was later retired on the merits, not for non-firing.)
- 2026-07-08 — codex `session_start`: negative (exec-mode marker check, 0 fires; consistent with all prior runs). Re-ground not shipped for codex.
- 2026-07-08 — grok, agy repo-level hook configs: unverified, no help surface; retired. gemini CLI: absent, not checkable.
- 2026-07-08 (later, 0.143.0) — codex repo-local hooks re-checked after the version bump and codex-docs claims of repo-local hook support: differential probe (SessionStart + PreToolUse in one `.codex/hooks.json`, tool-forcing prompt) fired **neither** event, untrusted temp repo and trusted registered repo alike. Negative deepened: the repo-local hook engine is dormant in exec mode; the 2026-06-29 `pre_tool_use` fires were global-config-era. Still not shipped.
- 2026-07-08 (later, 0.143.0) — codex repo skills from `.agents/skills/`: **positive** (probe skill invoked by name in an untrusted temp repo, exact marker returned). Operator skills shipped via `tools/shipped-set.json`.

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
