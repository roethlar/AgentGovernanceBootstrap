# Governance profiles

A *profile* is the governance a fixture workspace carries during a trial. The runner
overlays it after scaffolding and before the agent runs, so a trial measures the agent
**under that governance**. Comparing profiles on the same fixtures is the whole point of
the eval.

- **`none`** — implicit empty profile (no directory needed). The baseline: the agent
  gets the bare repo, no governance.
- **`current-template`** — what the toolkit ships today. Generated from the product
  templates via `profile.json` `copies` (no duplicated content committed here):
  `AGENTS.md` from `templates/AGENTS.template.md`, `CLAUDE.md` from the shim. This is the
  current product, NOT this repo's own dogfooded `AGENTS.md`.
- **`candidate-loop-first`** (later) — current-template plus the loop-first additions
  under evaluation; promoted into `templates/` only if trials show a gain.

### Mechanism arms (prose vs hooks vs both)

These locate *where* governance helps — model-read prose, harness-enforced hooks, or
both:

- **`current-template`** — **prose only** (the model reads AGENTS.md/CLAUDE.md and may
  or may not follow it). Model-capped by construction.
- **`hook-gate`** — **hooks only**: a Stop hook that blocks finishing while the visible
  test suite is red (bounded retries; visible suite only — never leaks the hidden
  SecPass test).
- **`hook-guard`** — **hooks only**: a PreToolUse hook that refuses edits to protected
  paths (visible tests, runner config, governance files) and assertion-weakening edits.
- **`prose-hooks`** — **both**: current-template prose + the gate and guard hooks (the
  shipped combination).

The full factorial is `none, current-template, hook-gate, hook-guard, prose-hooks`.

A profile may also carry literal files (overlaid as-is); harness adapters belong under
per-harness subdirs and are installed by a driver, not overlaid blindly.

### Hooks only count when they fire

A hook profile measures nothing if the driver's harness doesn't honor the hook. The
harness records `hooks_present` / `hooks_supported_by_driver` / `hooks_fired` (S4), and
the aggregator marks a hook-arm trial **invalid** (excluded, reported) when the driver
doesn't support hooks or they never fired — never a silent no-op (Slice C). The
gate/guard hooks read their config from hook-side env (`AGB_VERIFY_CMD`,
`AGB_PROTECTED_PATHS`, `AGB_GATE_STATE`) the harness exports — never from the agent's
prompt.
