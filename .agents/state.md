# Agent State

## Now

- 2026-11-17: F5, F6, F7, F8 and G1 are complete in the development source
  through `aaa1a09`; integration into master and local/remote work-branch
  deletion are verified in the [completion receipt](review/2026-11-17-completion.md).
  The owner subsequently authorized publication; the verified Bixi release
  is recorded in that receipt. Receiving-repo migration and self-refresh remain separate.
  Completed plans: [refresh defects](../docs/superpowers/plans/2026-11-17-refresh-defects.md)
  and [current boundaries](../docs/superpowers/plans/2026-11-17-current-boundaries.md).
  The baseline suite's historical fixture-path note was clarified in `a199383`.
  [F5](review/findings/F5.md) and [F6](review/findings/F6.md) are verified;
  [F7](review/findings/F7.md), [F8](review/findings/F8.md) and
  [G1](review/findings/G1.md) are verified too.
  [Plan review record](review/2026-11-17-plan-review.md).
- Disputed waste-pass functionality restored from f1497c4 in source
  6f90a8f, retaining the owner's readable-response rule and Headroom removal.
  Published as Bixi 53f5d77; installed here by rollback aafab41.
- Current verification is in the finding records above. Installed governance
  was deliberately left unchanged and may lag source (self-refresh is owner-only).
  The AGENTS template remains byte-identical to the baseline; earlier scope
  and token measurements are recorded in .agents/decisions.md (2026-09-10).
- 2026-10-24: host `q` is retired (owner); the trusted LAN fetch fallback is
  now the magneto gitea pull mirror (8703c94, 74af9e9), published as Bixi
  d59c5cd. This repo's installed governance is not refreshed (owner-only).
- 2026-10-25: catchup Step 0 hardened in source so harness default-taking
  can't skip the sweep question (.agents/decisions.md, 2026-10-25).
  Published as Bixi b1c3728; this repo's installed copy is not refreshed
  (owner-only).

## Next

- Existing-repo adoption of Product boundaries remains separately scoped.
  Proposed next action: identify a receiving repo and approve the transfer
  of its current adopted boundaries; refresh preserves repo-owned guidance.
- Owner review, after the fact: the `tools/refresh.py` change in 74af9e9
  (q URL replaced by the magneto mirror in CANONICAL_URLS, 5+/4- lines)
  shipped code without an approved plan, against AGENTS.md. It was done
  under the 2026-10-24 "q is gone" sweep. Ratify it or ask for a revert.
- Deferred owner draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Implementation remains unapproved.

## Verification

- Entry point: .agents/repo-guidance.md.
