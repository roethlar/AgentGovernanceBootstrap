# Harness capabilities — injection vector + hook support (for the hooks lane)

Which subjects can carry the **transferable hooks** intervention (the high-value lane per
TEST-PLAN v1/v2), how to inject governance prose, and how to drive each headless.
All auth is subscription/OAuth (no API keys). Validated 2026-06-29 (canaries where noted;
agy partly from binary inspection — auth expired blocked its live canary).

| harness | provider | governance inject vector | pre-edit GUARD hook | Stop / loop-control | headless invocation | auth |
|---|---|---|---|---|---|---|
| **Claude Code** (`claude`) | Anthropic (via headroom) | **CLAUDE.md** (+`@AGENTS.md`); bare AGENTS.md is INERT | yes — PreToolUse (blocking) | **yes — Stop hook can force continuation** (the reference) | `claude -p "…" --permission-mode bypassPermissions` | `~/.claude/.credentials.json` |
| **codex** (`codex`) | OpenAI (via headroom) | **AGENTS.md** (native) | yes — PreToolUse (fired heavily in runs) | unconfirmed (template has SessionStart+PreToolUse) | `codex exec --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust --skip-git-repo-check -C /app` (prompt on stdin) | `~/.codex/auth.json` |
| **grok** (`grok`) | xAI (direct) | **AGENTS.md** (+CLAUDE.md; NOT .cursorrules) | **yes** — PreToolUse blocking, deny via stdout/exit-2 (fail-open) | **NO hook** — `Stop` is passive; substitute = built-in flags `--check` / `--max-turns` | `grok -p "…" --always-approve --cwd /app` | `~/.grok/auth.json` (OIDC) |
| **agy** (Antigravity, `agy`) | Gemini/Google | **AGENTS.md + GEMINI.md** (canary-CONFIRMED; REQUIRES `--new-project`) | yes — `BeforeTool` matcher on write tools | **`OnStop` event present** (stop-equiv; force-continuation semantics TBD) | `agy --print "…" --dangerously-skip-permissions --model gemini-3.5-flash` | `~/.gemini/oauth_creds.json` (OAuth) |

## Models (set explicitly — unpinned defaults bit us)
- Claude Code: pin `--model` (no model key in settings.json → ambiguous default). Confirmatory = Opus 4.8.
- codex: `gpt-5.5` @ xhigh (token-heavy — small batches).
- grok: **Grok Build = `grok-build`** via `-m grok-build`. Default is `grok-composer-2.5-fast` (the earlier smoke ran the default by mistake).
- agy: **Gemini 3.5 Flash = `gemini-3.5-flash`** via `--model gemini-3.5-flash`.

## Hook config locations (place in GLOBAL/trusted to avoid per-project trust steps)
- Claude/codex: `~/.claude/settings.json` / `.claude/` (codex: `CODEX_HOME/hooks.json`, `--dangerously-bypass-hook-trust`).
- grok: `~/.grok/hooks/*.json` (global = always trusted); also auto-scans `~/.claude/settings.json` + `.cursor/hooks.json`.
- agy: `~/.gemini/settings.json` (`hooks` block; events: BeforeTool, OnStop, PreInvocation, PostInvocation, Stop).

## Hooks-lane readiness
- **pre-edit guard (AGENTS.md tripwire equivalent): portable to ALL four** — same shell-command-on-tool-event shape.
- **Stop / keep-going-until-verified (loop control):** native hook on **Claude Code** (and likely codex); **grok = flag substitute (`--check`)**; **agy = `OnStop` (verify if it can force continuation)**. This is the discriminating capability — only Claude Code is confirmed to force continuation via hook.

## agy viability — CONFIRMED 2026-06-29 (auth refreshed; ran end-to-end)

Re-auth done (owner ran `agy` interactively). Full smoke passed:
- **Host + in-container PONG ✓** on `gemini-3.5-flash` (`--model` accepts both the API id
  and the display name). **glibc OK** — agy needs only stock libs (libc/pthread/m/dl/rt/
  resolv/ld), all present in the sweap images (Debian glibc 2.36); `agy --version` runs
  in-container.
- **Valid patch ✓** on qutebrowser-f7753550 (arm=none): 7885 B, 3 source files, 0 test
  files, ~2 min.
- **Headless invocation (eval form):** `agy --print "$(cat task.md)" --dangerously-skip-permissions --model gemini-3.5-flash --new-project`
- **KEYSTONE confirmed:** agy loads **AGENTS.md AND GEMINI.md** — but **only with
  `--new-project`** (a plain `--print` registers no project → loads neither, only the
  global `~/.gemini/GEMINI.md`). So every governed agy run MUST pass `--new-project`.
  Does NOT read CLAUDE.md or `.gemini/rules`.

**Two load-bearing operational caveats for the agy driver:**
1. **`/app` MUST be chowned to `agent`.** If the workspace is write-blocked, agy does NOT
   fail gracefully — it spends the whole run attempting **sandbox breakout** (reading
   /etc/shadow, seeking sudo/su, namespace/bind-mount escapes) and produces an empty
   patch. With `/app` writable it does the task normally. (Behavior trait worth noting;
   the chown fixes it. arms4 already chowns.)
2. **Strip the host `rtk` BeforeTool hook** from the mounted `~/.gemini/settings.json`
   (rtk isn't in the container).

Auth note: the OAuth token is short-lived and does NOT refresh headless — re-auth
(`agy` interactively) at the start of a session if it has lapsed.

## Weak local model via Claude Code → ollama — CONFIRMED 2026-06-29 (the key Q2 hooks cell)

`qwen3.6:27b` runs as a **Claude Code subject** (full harness: tools, hooks, CLAUDE.md) —
so the high-value hooks (incl. the **forced-continuation Stop hook**, which only the Claude
Code harness supports) can be measured on a **weak model that actually needs the
scaffolding**, on **free local GPU**. This is the single most valuable cell: weak model
(real headroom) × full hook support × no cap. Per v1, qwen3.6 is a primary Q2 subject.

- **No gateway needed:** ollama 0.30.11 exposes a native Anthropic-compatible
  `/v1/messages` on `:11434`; `claude` points straight at it.
- **Wiring (in-container, user `agent`):** run container `--network host` (host ollama on
  `0.0.0.0:11434`); mount `~/.local/bin/claude`; env: `CLAUDE_CONFIG_DIR=/home/agent/.claude_qw`
  (fresh → ignores the headroom settings.json), `ANTHROPIC_BASE_URL=http://127.0.0.1:11434`,
  `ANTHROPIC_API_KEY=ollama`, `CLAUDE_CODE_MAX_OUTPUT_TOKENS=500000`; cmd
  `claude --model qwen3.6-hictx:27b -p "$(cat task.md)" --permission-mode bypassPermissions`.
- **Required fixes:** deliver task as `-p "$(cat task.md)"` (NOT the path — qwen won't auto-read);
  directive imperative prompt (else it chats); high context — a `qwen3.6-hictx:27b` variant
  (`ollama create … PARAMETER num_ctx 65536`) + 500K output cap (qwen is thinking-token-hungry).
- **Viability result:** SOLVED qutebrowser-f7753550 (Opus-ceiling) with a real source fix
  (~197s); FAILED ansible-e40889 (took a `conftest.py` warning-suppression shortcut, ~402s).
  → **usable difficulty window, not a floor.** Scope qwen to the easier/well-specified band.
- **Caveats:** slow (200–400s/instance even on a 5090); prone to test-infra shortcuts
  (source-only diff + test-file excludes already guard scoring against this).
