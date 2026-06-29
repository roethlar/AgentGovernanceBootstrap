# Grok secondary-harness — SWE-bench Pro (viability smoke)

Grok is the **most mission-relevant** subject: its harness ≈ Cursor, the gap this
toolkit targets. Separate provider (xAI), so no Anthropic rate-limit contention.
Smoke 2026-06-29 (subagent-run) — VIABILITY + keystone only, patches not yet scored.

## Harness mechanics (validated)

- Binary: native static ELF (`~/.grok/downloads/grok-*-linux-x86_64`, symlinked
  `~/.local/bin/grok` and `~/.local/bin/agy`); mounts cleanly into sweap containers.
- Headless: `grok -p "$(cat task.md)" --always-approve --cwd /app` (`--always-approve`
  = the bypass/auto-approve flag).
- Auth: subscription OIDC token at `~/.grok/auth.json` (NOT an API key); mount + copy to
  `/home/agent/.grok/auth.json` (writable for refresh), set `GROK_HOME`. Direct to
  `api.x.ai` (NOT headroom).
- Fast: ~60–75s/cell (vs Claude ~200–400s). xAI Tier 5 → cap full pilot at ~3–4 workers.

## KEYSTONE (canary-confirmed): grok reads **AGENTS.md** natively

Five candidate files seeded with unique tokens; only these were loaded:

| file | loaded? |
|------|---------|
| AGENTS.md | **YES** (primary injection vector) |
| CLAUDE.md | yes (also read) |
| .cursorrules | no |
| GROK.md | no |
| .grok/rules.md | no |

So the prose arm writes directly to `AGENTS.md` — no `CLAUDE.md`/`@import` shim needed
(grok scans the same Agents/Claude/AGENT/AGENTS set as Claude Code).

## Design: 3-arm (none / placebo / prose), NO hooks

Hooks don't port to grok → prose-only is the cleanest isolation of the prose effect
across the whole study.

## Smoke results (R=1, patches PRODUCED — not yet scored for resolved)

| instance | none | placebo | prose |
|----------|------|---------|-------|
| qutebrowser-f7753550 (Opus-ceiling) | 6219c/4f | 5394c/3f | 5371c/3f |
| ansible-e40889e7 (mid) | 2529c/3f | 2429c/3f | 2605c/3f |
| element-web-71fe08ea | EMPTY (3×timeout, ALL arms) | EMPTY | EMPTY |

- Grok produces valid non-empty patches fast on qutebrowser + ansible, all arms.
- **element-web-71fe08ea timed out on all 3 arms** — image-level infra issue (heavy JS
  build), NOT a grok problem (all-arms-identical failure). **Drop it** from the grok
  band; substitute a mid instance (openlibrary-f0341c0 / NodeBB).
- Arm-level differences are within noise at R=1 — viability only; need R=2–3 + scoring.

## Recommendation

Viable prose-test subject — all green. For the real grok pilot: 3-arm, R≥2, score the
patches (resolved), drop element-web, ~3–4 workers. NOTE: this smoke confirmed grok
*produces* patches; it did NOT measure *resolution* — that's the next step.
