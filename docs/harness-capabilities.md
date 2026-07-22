# Per-harness capability record

The durable record of verified facts about how each agent harness loads
governance and supports hooks. This file is the seed input and the durable
home for the toolkit's **verify-once gate**: a harness adapter (hook config,
wrapper set) ships only after a live check on that harness confirms the
mechanism fires; every check's outcome — positive or negative — is recorded
here with its date. Facts below marked "global" describe user-level config,
not the repo-level configs the toolkit ships; do not cite them as evidence
for repo-level behavior.

Claim discipline: every claim here is one of **observed** (carries a date
and, where it matters, the harness version and command), **assumed**
(labeled), or **historical** (superseded or version-scoped — evidence about
that version only). An observation holds for the version probed; a newer
installed version needs a scoped recheck before the claim is relied on for
recovery or reviewer dispatch. Launch/recovery command shapes recorded here
or seeded into `tools/refresh.py` are syntactically-known invocations —
PATH presence is probed at offer time, and nothing else (auth state,
headless mode, JSON support) is implied.

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
| Claude Code | yes, blocking (verified; the shipped `protect-governance.py` PreToolUse deny live-checked 2026-07-16) | **yes — `SessionStart` matcher `compact` (verified 2026-06-21)** | yes — Stop hook can force continuation (Claude-Code-only) |
| codex | historical: `pre_tool_use` fired in eval runs 2026-06-29 (global `CODEX_HOME` config era). Repo-local: **dormant in exec mode** — differential probe 2026-07-08 on 0.143.0 (SessionStart + PreToolUse markers, one file) fired NEITHER, in an untrusted temp repo AND a trusted repo with registered hook state. | **not needed** — codex re-reads `AGENTS.md` after compaction natively (owner-attested 2026-07-08; consistent with codex delivering instruction files as context rebuilt per turn, outside the compacted conversation). A re-ground hook would duplicate the harness's own behavior. (The hook-engine negative above stands as the mechanism record.) | unconfirmed |
| repo **skills** (`.agents/skills/<name>/SKILL.md`) | — | — | **POSITIVE on three harnesses (2026-07-08)** — codex 0.143.0: discovered + invoked, untrusted repo, headless (marker probe exact). grok (grok-4.5 default): discovered + invoked, untrusted temp repo, headless `-p` (marker exact). agy 1.1.0: exposed as a native slash command (`/pingprobe`) and invoked (marker exact) — **requires a trusted workspace** (owner-verified interactively; headless untrusted probe not viable). The operator set ships as shared pointer skills (`templates/skills/shared/`), same pure-adapter class as `.claude/commands/`. |
| grok | yes, blocking (global `~/.grok/hooks/*.json`; also auto-scans `~/.claude/settings.json`, `.cursor/hooks.json`) | repo-level hook config **unverified** (no hook surface in `--help`, 2026-07-08); shipped repo-level config retired | no — `Stop` passive; substitutes: `--check` / `--max-turns` flags |
| agy | yes — Claude-style events in **global** `~/.gemini/settings.json` (docs: antigravity.google/docs/hooks) | **mechanism verified, hook not needed.** Repo-level `.agents/hooks.json` SessionStart fires in a trusted workspace (owner live check 2026-07-08, agy 1.1.0: at the first prompt; untrusted: silent). But agy attests (2026-07-08, recalled+web grade) that `GEMINI.md`/`AGENTS.md` are system-pinned and **immune to compaction** — same architecture as codex — so a re-ground insures a non-event. The hook shipped and was retired the same day; re-shipping is one shipped-set flip if the pinning claim is ever falsified. | no — `Stop` passive (`{"decision":"allow"}` only) |
| gemini CLI | — | **not checkable** on the dev machine (CLI not installed, 2026-07-08) | — |

Verify-once ledger:

- 2026-06-21 — Claude Code compaction re-ground: fires (validated when built). Shipped.
- 2026-06-29 — codex `pre_tool_use` from repo-level `.codex/hooks.json`: fires (eval runs, 13–15×/cell). (The tripwire it carried was later retired on the merits, not for non-firing.)
- 2026-07-08 — codex `session_start`: negative (exec-mode marker check, 0 fires; consistent with all prior runs). Re-ground not shipped for codex.
- 2026-07-08 — grok, agy repo-level hook configs: unverified, no help surface; retired. gemini CLI: absent, not checkable.
- 2026-07-08 (later, 0.143.0) — codex repo-local hooks re-checked after the version bump and codex-docs claims of repo-local hook support: differential probe (SessionStart + PreToolUse in one `.codex/hooks.json`, tool-forcing prompt) fired **neither** event, untrusted temp repo and trusted registered repo alike. Negative deepened: the repo-local hook engine is dormant in exec mode; the 2026-06-29 `pre_tool_use` fires were global-config-era. Still not shipped.
- 2026-07-08 (later, 0.143.0) — codex repo skills from `.agents/skills/`: **positive** (probe skill invoked by name in an untrusted temp repo, exact marker returned). Operator skills shipped via `tools/shipped-set.json`.
- 2026-07-08 (later) — grok repo skills from `.agents/skills/`: **positive** (headless `-p`, untrusted temp repo, exact marker). agy repo skills: **positive** (owner-verified interactively on agy 1.1.0 — trusted workspace required; skill surfaced as a native slash command). The shipped skill set is renamed `templates/skills/shared/` — a three-harness operator surface.
- 2026-07-08 — grok model facts refreshed: `grok-build` is no longer a valid model id ("unknown model id"); current default is `grok-4.5` (alt: `grok-composer-2.5-fast`). The earlier pin-grok-build note is obsolete.
- 2026-07-08 (later) — agy `.agents/hooks.json` SessionStart in a trusted workspace: **positive** (owner live check, agy 1.1.0: marker fired at the first prompt of a fresh session). Re-ground re-shipped for agy in the probe-verified shape.
- 2026-07-09 — agy re-ground **retired** (owner decision): agy attests its guidance files are system-pinned and immune to compaction (recalled+web grade, consistent with codex's confirmed architecture), so the hook insured a non-event and fired only at session start, where guidance is freshly loaded anyway. The firing mechanism stays verified; `.agents/hooks.json` returns to the retired list with all four historical hashes.
- 2026-07-16 — Claude Code `protect-governance.py` PreToolUse deny (repo-level `.claude/settings.json`, headless `claude -p` in a throwaway temp repo, `--allowedTools Edit`): **positive** — control edit to an unprotected file succeeded, Edit against `AGENTS.md` was blocked with the hook's message and the file was unchanged on disk. Known fail-open limitation: hosts with no working `python3`/`py` interpreter run the hook command to its `else exit 0` arm — the invariant text and refresh's converge-to-shipped restore are the primary layers; the hook is defense in depth, Claude Code only.
- Still open: grok `PostCompact` (needs a real compaction; untestable headless — if a compacted grok session ever shows/misses a re-ground annotation, record it here).

## Operational harness facts

- **User-level durable guidance paths** (for cross-repo owner identity facts —
  the sanctioned out-of-repo store): Claude Code `~/.claude/CLAUDE.md`;
  codex `~/.codex/AGENTS.md`; agy `~/.gemini/GEMINI.md` (global file load
  verified 2026-06-29; combines with repo-level guidance in the system
  prompt). grok: unrecorded.
- **Unverified lead (recalled by agy itself, 2026-07-08 — labeled
  assumption, conflicts in part with our verified facts):** agy claims hooks
  are plugin-bundled (`~/.gemini/antigravity-cli/plugins/<name>/hooks.json`)
  with a blocking `before_tool_call` event, "not configured like
  Claude-style hook events" — yet our owner-verified live check proved a
  Claude-schema repo-level `.agents/hooks.json` SessionStart fires in a
  trusted workspace. Verified beats recalled: the firing MECHANISM stands
  verified (the agy hook itself was retired 2026-07-09 on the merits — see
  the ledger above; this paragraph predates that retirement). The
  plugin `before_tool_call` surface remains a lead for future enforcement
  hooks (verify before use); agy MCP registration reportedly lives in
  `~/.gemini/config/mcp_config.json` / the `/mcp` overlay (also unverified).
  Corroborated from agy's local builtin guide
  (`~/.gemini/antigravity-cli/builtin/skills/antigravity_guide/references/cli.md`,
  read 2026-07-08): CLI config lives at
  `~/.gemini/antigravity-cli/settings.json`; authoritative references are
  `antigravity.google/docs/cli/{features,best-practices,reference}` — note
  those pages are JS-rendered (plain fetch returns an empty shell), so
  verifying the MCP/hook leads takes a browser or agy's own web tool.

- Pin models explicitly; unpinned defaults bite. Grok as of 2026-07-08:
  default `grok-4.5` (alt `grok-composer-2.5-fast`); the former `grok-build`
  id no longer exists.
- **Model-ID denylist (playbook lint).** Committed playbooks
  (`templates/playbooks/*.md`) must stay model-free: tier routing binds to
  owner-granted nicknames resolved through the fleet-global
  `.agents/model-map.json` — the single sanctioned committed home for
  model slugs (2026-07-19) — never to model names baked into governed
  text (review-economy decision, 2026-07-17, as amended 2026-07-19;
  harness flags, transports, and capability grades remain machine-local
  in `.agents/review/harnesses.local.json`). The lint in
  `tests/test_templates.py` reads the fenced list
  below (one token per line, `#` comments allowed, matched case-insensitively
  at a left word boundary). Extend it here whenever a new concrete model
  family or codename enters the capability record — this list lives beside
  the model facts precisely so the two are updated in the same edit.

  ```model-id-denylist
  # model-family prefixes
  sonnet-
  opus-
  haiku-
  gpt-
  grok-
  gemini-
  claude-
  # codenames seen in owner pins / vendor docs
  composer
  terra
  luna
  ```
- agy's OAuth token is short-lived and does not refresh headless; re-auth
  interactively at session start if lapsed.
- agy in a write-blocked workspace does not fail gracefully (it hunts for
  privilege escalation instead of reporting); ensure the workspace is
  writable.
- codex headless: `codex exec` with the prompt piped via **stdin** (the argv
  form has hung); `--skip-git-repo-check` for untrusted dirs.
