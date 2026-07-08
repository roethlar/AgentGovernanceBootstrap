# Operators

<!-- Upstream-owned. Owner words that trigger a defined process. On seeing one, follow
     its entry here. These load on demand — they are not part of the per-session prompt. -->

- **catchup** — Re-read `AGENTS.md`, `.agents/context.md`, and `.agents/state.md` from
  disk. Report current state, next action, blockers, and one proposed first step.
  Change nothing until the owner responds.

- **handoff** — Rewrite `.agents/state.md` so a fresh session can resume with zero chat
  context. Stamp the `Updated:` line. Commit it.

- **drift** — Compare a guidance claim against repo evidence; fix the lower-authority
  source or report the conflict unresolved. Governance files themselves — `AGENTS.md`
  and everything under `.agents/` — are in scope as targets, not just as sources.
  Upstream-owned files found drifted are reported (and restored only on an explicit
  go), never silently rewritten.

- **decision** — Append the settled decision to `.agents/decisions.md` (date, why,
  supersedes), then update any guidance the decision invalidates so no stale copy
  survives.

- **plan** — Draft or update a durable plan document before broad work begins; get
  owner approval on it before implementation.

- **playbook <name>** — Read `.agents/playbooks/<name>.md` and follow it. If it does
  not exist, say so; never improvise a playbook from its filename.
