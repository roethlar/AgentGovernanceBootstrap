# Agent State

## Now

- 2026-11-17: plans and requested Claude review completed for Bixi #5–#8 and current-boundary
  discoverability (G1), on `plan/bixi-issues-2026-11-17` from `0574fd1`.
  Active plans: [refresh defects](../docs/superpowers/plans/2026-11-17-refresh-defects.md)
  and [current boundaries](../docs/superpowers/plans/2026-11-17-current-boundaries.md).
  Planning and Claude `claude-fable-5-2` / `xhigh` review are authorized;
  implementation remains unapproved per item. Three Claude passes returned
  Acceptable with changes; the required revisions are incorporated. Last
  independently reviewed head: `eb147f4`; final prescribed clarifications
  followed it. [Review record](review/2026-11-17-plan-review.md).
  The plan branch still awaits merge/deletion authority; no product changes landed.
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

- Owner implementation go for the chosen scopes F5, F6, F7, F8 and G1.
  Recommended sequence: the three small refresh corrections, then F8's
  plan/apply protocol; G1 can proceed independently. Plan-branch integration
  and deletion also remain unapproved.
- Owner review, after the fact: the `tools/refresh.py` change in 74af9e9
  (q URL replaced by the magneto mirror in CANONICAL_URLS, 5+/4- lines)
  shipped code without an approved plan, against AGENTS.md. It was done
  under the 2026-10-24 "q is gone" sweep. Ratify it or ask for a revert.
- Deferred owner draft: docs/superpowers/plans/2026-08-30-refresh-check-mode.md.
  Implementation remains unapproved.

## Verification

- Entry point: .agents/repo-guidance.md.
