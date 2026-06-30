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
