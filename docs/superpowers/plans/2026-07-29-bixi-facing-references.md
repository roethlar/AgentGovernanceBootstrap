# Plan: product-facing surfaces name Bixi, not the development repo

Status: APPROVED 2026-07-29 — owner approved fixing the two real
reference groups from Bixi issue #1 (bootstrap Step 0 wording and the
update-governance wrappers). The feedback-target references
(`procedures/bootstrap.md` Step 8 `gh issue create` and
`product/README.md` lines 99–102) are excluded pending a separate owner
ruling; `tools/refresh.py`'s fallback list and the development
`README.md` are correct as designed and untouched.

## Problem

Bixi issue #1 (filed 2026-07-29 after a greenfield bootstrap from a
product clone): shipped files tell product users the toolkit's home is
the development repo.

1. `procedures/bootstrap.md` Step 0 names the development repo as "the
   canonical copy" (`https://github.com/roethlar/AgentGovernanceBootstrap.git`),
   defaults the clone path to `~/dev/AgentGovernanceBootstrap`, and
   directs a missing-clone bootstrap at the development URL. `tools/publish`
   mirrors `procedures/` into Bixi verbatim, so the published procedure
   misdirects a fresh operator. The packaging design already says
   otherwise: `tools/refresh.py` `CANONICAL_URLS` leads with Bixi and a
   clone syncs from its own `origin` first.
2. `templates/commands/claude/update-governance.md` and
   `templates/skills/shared/update-governance/SKILL.md` install into
   every governed repo and direct a missing-toolkit clone at the
   development URL and `~/dev/AgentGovernanceBootstrap` /
   `../AgentGovernanceBootstrap` paths.
3. `tests/test_templates.py`
   (`test_update_governance_wrapper_invokes_refresh_script`) pins the
   development URL literally, so it currently enforces the misdirection.

## Design

Product-facing surfaces name Bixi; development-repo details appear only
where a development clone needs them, always subordinate to the
origin-first rule.

- `procedures/bootstrap.md` Step 0:
  - The canonical public home is Bixi
    (`https://github.com/roethlar/Bixi.git`). A toolkit clone syncs from
    its own `origin` first — a product clone from Bixi, the development
    clone from the development repo, whose owner-controlled LAN gitea
    mirror covers GitHub being unreachable and may lag (expected, never
    a conflict).
  - Default clone path becomes `~/dev/Bixi`; the missing-clone step
    clones the Bixi URL there.
  - The fetch/fast-forward logic keeps its shape, restated
    origin-first: fast-forward to `origin`'s head when `origin`
    responds; otherwise to the first responding fallback in
    `tools/refresh.py`'s canonical order (Bixi, then the development
    repo, then the LAN mirror).
  - Step 8's `gh issue create -R roethlar/AgentGovernanceBootstrap`
    line is not touched by this plan.
- `templates/commands/claude/update-governance.md` and
  `templates/skills/shared/update-governance/SKILL.md`: the toolkit is
  named plainly ("the governance toolkit (Bixi)"); the missing-clone
  instruction becomes
  `git clone https://github.com/roethlar/Bixi.git` to `../Bixi` /
  `~/dev/Bixi`; no `AgentGovernanceBootstrap` token remains in either
  file. Everything else (refresh invocation, DRIFT/FLAG reporting,
  no-write-authority framing) is unchanged.
- `tests/test_templates.py`: the wrapper pin asserts the Bixi URL and
  asserts `AgentGovernanceBootstrap` absent, and extends the same two
  assertions to the shared skill body.

## Implementation

One commit (one finding, one fix):

1. `procedures/bootstrap.md` — Step 0 rewording per Design.
2. `templates/commands/claude/update-governance.md`,
   `templates/skills/shared/update-governance/SKILL.md` — per Design.
3. `tools/shipped-set.json` — append the outgoing normalized SHA-256
   (`nhash` in `tools/refresh.py`) of both edited templates to their
   `formerly[]` entries (`procedures/` is publish-mirrored, not part of
   the shipped set — no hash bookkeeping).
4. `tests/test_templates.py` — pin updates per Design.

A second bookkeeping commit records the close: `.agents/state.md`
landed entry, this plan's Status → CLOSED with verification results,
and a comment on Bixi issue #1 naming the landing commit. The issue
stays **open** — the published product carries the defect until the
owner's next `publish`; the comment says so.

## Verification

Interpreter per `.agents/repo-guidance.md` (Verification); on this
machine `python3.14` per `.agents/machines.md`.

1. `python3.14 -m unittest discover -s tests -v` — full suite green.
2. Guard proof: with the updated pins retained, temporarily restore the
   old `templates/commands/claude/update-governance.md` in the working
   tree; the pin test must fail; restore the new file; rerun green.
3. `rg -n AgentGovernanceBootstrap` (or grep) over `templates/` and
   `procedures/` shows only the sanctioned development-clone mentions
   in `procedures/bootstrap.md` Step 0 and the untouched Step 8 line.
4. `git diff --check`.
5. This plan file: `python3.14 -m unittest tests.test_plan_lint -v`.

## Rollout boundary

Landing here changes what ships, not what is installed anywhere: Bixi
receives the corrected files only on the owner's `publish` word, and
governed repos receive the corrected wrappers on their next refresh
against a synced toolkit. Bixi issue #1 closes only after a publish
carries the fix.
