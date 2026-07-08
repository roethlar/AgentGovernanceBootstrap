# Refresh

Instructions for updating an installed governance layer to current toolkit canon.
Upstream-owned files are replaced whole — never merged, never partially edited.

## Preconditions

- An explicit owner go to refresh.
- A clean worktree.
- An existing `.agents/governance.json` (otherwise this is an install, not a refresh —
  use `procedures/install.md`).

## Steps

1. Fetch the toolkit at the canon URL recorded in the manifest's `source` field.
2. Run `python3 .agents/check.py` first. If it reports drift in an upstream-owned
   file, someone hand-edited it since the last freeze: stop and present the drift —
   any local intent hiding in the edit must be rescued into `.agents/context.md` (or
   rejected) before it is overwritten.
3. Diff each upstream-owned file (per the manifest's `upstream` list) against canon.
   Present the diff to the owner. No changes → report "current" and stop.
4. On approval: copy the canon files byte-verbatim, then
   `python3 .agents/check.py --freeze`, then `python3 .agents/check.py` — must pass.
   If verification now fails on a repo-owned file (budget, broken pointer), report it;
   the repo layer is the owner's to fix, not the refresh's to rewrite.
5. Commit as one slice and follow the repo's push policy.

Repo-owned files (`context.md`, `state.md`, `decisions.md`, repo playbooks) are never
touched by a refresh.
