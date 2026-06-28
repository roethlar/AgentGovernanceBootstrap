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

A profile may also carry literal files (overlaid as-is); harness adapters belong under
per-harness subdirs and are installed by a driver, not overlaid blindly.

Note: hooks in a profile only take effect if the harness trusts and runs them in the
trial workspace — record `hooks_active` rather than assuming an installed hook fired.
