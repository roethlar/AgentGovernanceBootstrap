# bootstrap Step 7: carve-out commit shape + non-git branch resolution

Status: DRAFT 2026-07-10 — awaiting owner approval; no implementation
authorized. Drafted on owner instruction ("make whatever plans are needed to
address anything new", 2026-07-10).

## Why this plan exists

1. **GitHub issue #4** (2026-07-10, ExchangeAdminWeb live run): bootstrap
   Step 7.3 mandates "ONE scoped commit covering both groups", but on the
   legacy carve-out route that shape is unreachable by construction.
   `tools/refresh.py` cannot install the canonical `AGENTS.md` while the
   legacy file exists (`classify()` flags it, never installs) nor while its
   deletion is uncommitted (`dirty_conflicts()` sees the porcelain line and
   `main()` exits 3). The only state in which refresh installs is
   deletion-already-committed — at which point the single drafts+shipped-set
   commit is impossible and `--stage-only` is unreachable on this route.
   The live run completed correctly only by deviating: carve-out commit
   `ece7b2e`, then refresh's own commit `889f38c`. Every future carve-out
   run must re-derive and re-justify the same deviation.
2. **Holistic review finding H3** (untracked review, GPT-5.6-Sol,
   2026-07-09; verified against the procedures this session): the same
   route gap, plus a second unreachable branch — bootstrap Step 1 lets an
   owner decline `git init` and continue "on disk only" (the approval
   summary template even carries a non-git variant paragraph), but Step 7.2
   unconditionally runs `refresh.py`, which exits 2 on a non-git target
   (`tools/refresh.py:437-439`). The documented on-disk-only path cannot
   execute the install step at all.

## Design

**Carve-out route: two scoped commits, announced up front.** Amend
`procedures/bootstrap.md` Step 7 to define two routes explicitly:

- *Standard route* (no legacy core file): unchanged — `refresh.py
  --stage-only`, stage drafts, ONE scoped commit covering both groups.
- *Legacy carve-out route* (a foreign `AGENTS.md` is being superseded):
  exactly TWO scoped commits, both named with exact messages in the approval
  summary before approval:
  1. the carve-out commit — approved judgment drafts, supersession banners,
     and the legacy file's deletion (the migration itself);
  2. the refresh commit — default-mode `refresh.py` (not `--stage-only`),
     which installs the shipped set and makes its own commit recording the
     toolkit SHA, exactly as the live run demonstrated.
  The owner's approval of the summary covers both commits; nothing between
  them, nothing after without a fresh go.

`templates/approval-summary.template.md`'s commit paragraph gains the
matching carve-out variant (two exact messages, what each contains).

**Rejected alternative** (from issue #4, rejected here): teaching
`refresh.py` to proceed when the only porcelain state on a replace-whole
target is a deletion. That loosens the dirty-tree guard exactly while the
trust-boundary hardening plan
(`docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md`)
is tightening transaction guarantees; a procedure that tells the truth
beats a guard with a carve-out. Revisit only if the two-commit shape
proves problematic in the field.

**Non-git branch: stop cleanly, honestly scoped.** Resolve H3's second gap
in favor of NOT implementing a non-git install (refresh stays git-only; its
"single installer, never hand-copied" protection depends on git custody
checks). Step 1's decline path is rewritten: when the owner declines
`git init`, the run copies ONLY the judgment drafts to their final paths
("On disk only — no version control", limitation recorded as today), states
plainly that the shipped set — `AGENTS.md`, skills, wrappers, hooks — CANNOT
be installed without git because `refresh.py` is its sole installer, and
Step 7.2/7.3 are skipped, closing with the standing offer that a later
`git init` makes a normal bootstrap possible. The approval-summary non-git
paragraph is aligned. If the owner would rather support full non-git
installs, that is a refresh.py feature with its own transaction design —
out of scope here, needs its own plan.

## Slices

1. `procedures/bootstrap.md` Step 7 route split + Step 1 decline-path
   rewrite; `templates/approval-summary.template.md` commit-paragraph and
   non-git-paragraph alignment. Docs/template-only.
2. Regression tests pinning the route's mechanics in `tests/test_refresh.py`
   (current behavior, so the procedure's claims stay true): foreign
   `AGENTS.md` present → flagged, not installed; uncommitted deletion →
   exit 3; committed deletion → default-mode refresh installs and commits.
   Any that already exist are named, not duplicated.
3. Bookkeeping: note issue #4 ready to close (owner go for `gh issue
   close`); the ExchangeAdminWeb 2026-07-20 rollout (`.agents/state.md`
   Next) then runs against a procedure that matches reality.

## Verification

Slice 1: `git diff --check`. Slice 2: full suite per
`.agents/repo-guidance.md` (Verification), with the guard proof for any new
test (mutate a throwaway copy, watch red, restore). Bite proof from issue
#4, run before closing it: a fixture repo with a foreign `AGENTS.md` driven
through the amended Step 7 verbatim ends in the documented two-commit shape
with no deviation note required.

## Non-goals and risks

- No `refresh.py` behavior change (the loosened-guard alternative is
  rejected above; the dirty-path guard stays exactly as strict).
- Two commits on the carve-out route is a deliberate exception to the
  one-commit promise, confined to that route and announced in the approval
  summary — the summary template change is what keeps the owner's approval
  covering the real shape.
- H3's banner-loop observation (the ATTENTION banner repeats until the
  carve-out is done) is resolved by this same change: the procedure the
  banner points at now names the completing operation (commit the deletion,
  then refresh). No banner code change needed.
- ExchangeAdminWeb is due 2026-07-20; landing this first is the point, but
  nothing here blocks that run — at worst it deviates with a note exactly as
  qbit-mobile and ExchangeAdminWeb's own run already did.

Provenance: GitHub issue #4 (2026-07-10, ExchangeAdminWeb live run, commits
`ece7b2e`/`889f38c` in that repo); untracked holistic review H3
(2026-07-09), verified against `procedures/bootstrap.md` Steps 1/7,
`templates/approval-summary.template.md`, and `tools/refresh.py` at
`8c3b6e3` this session; owner instruction 2026-07-10 to draft plans for the
new findings.
