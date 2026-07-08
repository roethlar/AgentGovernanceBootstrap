# Adapters

Harness-specific plumbing only — an adapter may remind, wire, or re-ground, but it
never carries a rule. Rules live in `AGENTS.md` and `.agents/`; if an adapter and the
constitution ever disagree, the adapter is wrong.

- `claude/settings.json` — Claude Code hook: on context compaction or session restart,
  injects a reminder to re-read `AGENTS.md` from disk. Merge into the target repo's
  `.claude/settings.json` (or copy whole if none exists).

Some harnesses keep hooks inert until the workspace is trusted on a machine. During
install, name the trust step and run it only on an explicit owner go, only for the
harness in use.

v1's edit-tripwire hook is deliberately not carried forward: hand-edit detection is
now mechanical and harness-independent via the checksum manifest
(`.agents/check.py` verify).
