# Driver prototypes — session-validated, scratch quality (2026-06-29)

Working in-container eval drivers validated during the 2026-06-29 session, preserved so a
fresh session doesn't rebuild from scratch. **They are PROTOTYPES, not the eval.** The plan
(`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`, Addenda) calls
for folding their *mechanics* into `tools/run_fixture.py`'s benchmark path. Do not run these
directly as the eval — `shell=True`, hardcoded paths, and a now-deleted session `scratchpad/`
make them reference-only.

Mechanics they encode (durable per-subject reference lives in `evals/harness-capabilities.md`):

- **arms4.py** — Claude Code driver: anti-leak `git init` + pinned `eval_base` tag; capture
  `git diff --cached eval_base` (vs the TAG, not HEAD — agents commit their work, so vs-HEAD
  reads a committed fix as EMPTY and biases governed arms); source-only diff excluding test +
  governance files; neterr/quota invalid-accounting; empty-patch retry; headroom routing.
- **arms4_model.py** — same, parametrized `--model` (e.g. `sonnet`) with isolated container
  prefix + output paths so it can run alongside another Anthropic run.
- **arms4_codex.py** — codex: native musl binary + `~/.codex` auth mount, `codex exec
  --dangerously-bypass-approvals-and-sandbox`, quota self-abort + invalid-accounting.
- **arms4_grok.py** — grok: native binary + `~/.grok` auth, `grok -p --always-approve`,
  `-m grok-build`, AGENTS.md injection, hook-arm scaffolding (note: a tool-name-scoped guard
  was inert because grok edits via bash — needs an empty matcher + in-script filtering).
- **adapter.py** — SWE-bench Pro instance → predictions.json / scorer glue.

Not archived: one-off PONG/canary/smoke/probe scripts (codex/grok/qwen/agy viability) — their
conclusions are captured in `evals/harness-capabilities.md`.
