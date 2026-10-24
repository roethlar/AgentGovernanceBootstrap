# Agent State

## Now

- Disputed waste-pass functionality restored from f1497c4 in source
  6f90a8f, retaining the owner's readable-response rule and Headroom removal.
  Published as Bixi 53f5d77; installed here by rollback aafab41.
- All 226 original tests pass. Installed artifacts match source under
  refresh's newline-equivalence rule; catchup, drift, skill triggers,
  tools, hooks and procedures match the baseline byte-for-byte.
  Scope and token measurements: .agents/decisions.md (2026-09-10).
- 2026-10-24: host `q` is retired (owner); the trusted LAN fetch fallback is
  now the magneto gitea pull mirror (8703c94, 74af9e9), published as Bixi
  d59c5cd. This repo's installed governance is not refreshed (owner-only).

## Next

- Deferred owner draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Implementation remains unapproved.

## Verification

- Entry point: .agents/repo-guidance.md.
