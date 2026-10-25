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
- 2026-10-25: catchup Step 0 hardened in source so harness default-taking
  can't skip the sweep question (.agents/decisions.md, 2026-10-25).
  Published as Bixi b1c3728; this repo's installed copy is not refreshed
  (owner-only).

## Next

- Owner review, after the fact: the `tools/refresh.py` change in 74af9e9
  (q URL replaced by the magneto mirror in CANONICAL_URLS, 5+/4- lines)
  shipped code without an approved plan, against AGENTS.md. It was done
  under the 2026-10-24 "q is gone" sweep. Ratify it or ask for a revert.
- Deferred owner draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Implementation remains unapproved.

## Verification

- Entry point: .agents/repo-guidance.md.
