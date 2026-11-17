# Agent State

## Now

- 2026-11-17: implementing approved F5, F6, F7, F8 and G1 on
  `plan/bixi-issues-2026-11-17`. The owner's approval covers the named
  plan-branch integration/deletion; publishing and self-refresh remain separate.
  Active plans: [refresh defects](../docs/superpowers/plans/2026-11-17-refresh-defects.md)
  and [current boundaries](../docs/superpowers/plans/2026-11-17-current-boundaries.md).
  The baseline suite's historical fixture-path note was clarified in `a199383`.
  [F5](review/findings/F5.md) and [F6](review/findings/F6.md) are verified;
  [F7](review/findings/F7.md) is verified too. [F8a](review/findings/F8.md)
  is verified; F8b/F8c and G1 remain pending;
  integration is still pending.
  [Plan review record](review/2026-11-17-plan-review.md).
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

- Complete F5–F8 and G1, their verification, and the approved branch closeout.
- Owner review, after the fact: the `tools/refresh.py` change in 74af9e9
  (q URL replaced by the magneto mirror in CANONICAL_URLS, 5+/4- lines)
  shipped code without an approved plan, against AGENTS.md. It was done
  under the 2026-10-24 "q is gone" sweep. Ratify it or ask for a revert.
- Deferred owner draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Implementation remains unapproved.

## Verification

- Entry point: .agents/repo-guidance.md.
