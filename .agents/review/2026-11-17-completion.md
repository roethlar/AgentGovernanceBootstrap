# Completion receipt — F5–F8 and G1

The owner's approved implementation, named branch closeout and subsequent
public Bixi release are complete. Receiving-repo adoption remains separately
scoped.

## Implemented and verified

- [F5](findings/F5.md), `51ba21c`: honor effective Git re-includes and refuse probe errors.
- [F6](findings/F6.md), `e0b90f1`: distinguish ignored/foreign core targets; force cannot bypass ignores.
- [F7](findings/F7.md), `e7d41f2`: preserve state instructions and retained line endings.
- [F8](findings/F8.md), `d16d40d`, `a4bc7ec`, `3830d38`: compute repairs before approval, pin and preflight the full operation, and rehearse both bootstrap routes.
- [G1](findings/G1.md), `aaa1a09`: inline current boundaries and current task contracts, preserving qualifiers and distinguishing assumptions.

Tested source head: `aaa1a09407fd1f1689a91a9b939f750862806c20`.
The full Python suite ran 252 tests: 251 passed and one filesystem-dependent
skip. Plan lint and whitespace checks passed. Regression tests were shown
to fail against prior behavior or isolated guard-removal mutations, then
pass with the implementation restored. Both bootstrap routes and their
pre-commit drift checks were rehearsed in disposable repositories.

Four fresh contexts exercised current-boundary discovery, an archive-only
negative control, an adopted amendment, and a current-documents-only read.
The targeted criteria passed; broader fixture limitations are recorded in
G1. AGENTS stayed byte-identical. No runtime code review is claimed.

The [requested plan review](2026-11-17-plan-review.md) used Claude Code
`claude-fable-5-2` at `xhigh`. Its final verdict was Acceptable with changes;
the prescribed clarifications were incorporated before the owner approved
implementation. That verdict remains a plan review, not a code certification.

## Integration and deletion evidence

Canonical remote HEAD resolved to `master`. Immediately before integration,
local and remote master were `0574fd120820c51646268b4a12bfd41a2e326904`;
the work branch matched its remote at the tested source head above.
Master fast-forwarded without conflicts or source changes. Canonical remote
master then matched `aaa1a09`.

`git diff --exit-code master plan/bixi-issues-2026-11-17` returned zero.
Remote master and work-branch tips were rechecked at the same full SHA
before deletion. The work branch was deleted remotely and locally, then
both `git branch --list` and `git ls-remote` verified its absence.
This receipt is subsequent non-shipped bookkeeping on master.

## Publication — 2026-11-17

The owner's subsequent instruction, “publish,” authorized the batch release.
`tools/publish /home/michael/dev/Bixi` published development source
`4cceaad52e0b13f6723b322f4f1c19c50602a909` as
[Bixi 6fd69ee](https://github.com/roethlar/Bixi/commit/6fd69ee44ddf2f41bc91b9208e849d658cbf07cd),
following public parent `b1c3728ba44f8d22b4ff1ab732b91eec014b7f1a`.

The release changed the eight intended runtime/template/procedure files.
All 69 committed publish-set files were checked against source by SHA-256,
with exact tracked-path-set equality. Public `main` matched the full release
SHA and the product checkout was clean. Publishable source was unchanged
from the verified implementation; the earlier suite result applies, and no
redundant full-suite run was made for publication. Bookkeeping checks are
plan lint and `git diff --check`.

No public issues were posted or closed. No receiving-repo migration, Vela
edit, hook-trust change or owner-only self-refresh was performed. Existing
repo-owned facts need a separately scoped transfer into Product boundaries;
refresh preserves that guidance. The toolkit changes improve discovery;
they do not guarantee obedience or change an external check's reading set.
