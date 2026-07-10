# refresh.py: trust-boundary and transaction hardening

Status: APPROVED 2026-07-10 — owner rulings (2026-07-10): slices 0–3 and 5
are all in ("all 3 in" covering commit scope, preflight-before-commit, and
the equivalence-boundary overwrite, plus the earlier symlink-containment
go); the mirror-distrust slice is REJECTED and replaced by a wording-only
fix — the gitea mirror is owner-controlled and trusted, GitHub stays the
primary sync source, sync behavior unchanged ("fix wording, keep github
primary"); the Python floor is raised to the actual requirement instead of
restoring 3.9 test compatibility ("just make the required version the
actual required version"). Implementation awaits an explicit owner go.

## Why this plan exists

An independent holistic review (GPT-5.6-Sol, 2026-07-09, delivered as an
untracked report; disposition "review only, no implementation
authorization") found that the refresh runner's mechanics are weaker than
the governance prose promises. Every finding this plan relies on was
re-verified against `tools/refresh.py` at `8c3b6e3` by direct code reading;
the review's controlled reproductions are noted where they add evidence
beyond code inspection. Findings restated in full here so this plan is
self-contained:

1. **Mirror trust (review C1) — REJECTED as a defect by owner ruling
   (2026-07-10).** The review treated the LAN gitea fallback in
   `CANONICAL_URLS` (`tools/refresh.py:51-58`) / `sync_toolkit()`
   (`:106-120`) as a supply-chain risk. The owner's ruling: the gitea host
   is the one machine the owner controls outright; the mirror exists
   precisely to cover GitHub being unreachable, and this is a personal
   toolkit, not a release product. Sync behavior is therefore UNCHANGED
   (GitHub primary, gitea fallback). What remains is wording drift: the
   "never authoritative" phrasing in `.agents/repo-guidance.md` (Remotes &
   Sync) and `procedures/bootstrap.md` Step 0 overstates the 2026-06-10
   decision ("GitHub is authoritative; a lagging mirror is expected, not a
   disagreement to flag" — about lag and canon-for-propagation, not trust)
   and is fixed by slice 4. Subprocess timeouts / prompt suppression are
   deliberately OUT of this plan (behavior change not ruled on).
2. **Symlinks and unvalidated manifest paths can write outside the target
   (review C2).** `classify()` (`:137-168`) and `apply_plan()` (`:298-311`)
   join manifest paths and call `exists()`/`write_bytes()` with no `lstat()`
   check, no symlink rejection, and no proof the resolved destination stays
   under the resolved target root. A broken-symlink `AGENTS.md` in a target
   repo classifies as "install" (`exists()` follows the link, returns
   False) and `write_bytes` then creates the file the link points to —
   outside the repo. The review reproduced exactly this. Manifest `target`
   strings are trusted verbatim (no absolute-path/`..`/duplicate checks at
   runtime).
3. **Unscoped commit consumes unrelated pre-staged work (review H2).**
   `dirty_conflicts()` (`:290-295`) checks only the paths the plan touches,
   `stage()` (`:314-317`) adds exactly those paths, but the commit
   (`:462-464`) is a bare `git commit` that consumes the entire index. The
   review reproduced an unrelated pre-staged file landing inside the
   governance commit — violating the one-scoped-commit promise the approval
   flow is built on.
4. **Fatal checks run after mutation and after commit (review H5).**
   Push-policy parsing (`:472-474`, `splitlines()[-1]`) raises `IndexError`
   on an empty `.agents/push-policy.md` — after the commit already landed.
   Core-flag/banner handling (`:476-484`) also runs post-commit.
   `apply_plan()` writes multiple files non-atomically, so a mid-apply
   failure leaves a partially mutated tree with only a traceback.
5. **Target validation accepts nested directories and bare repos (review
   H7).** `is_git_repo()` (`:102-103`) checks only the exit status of
   `rev-parse --is-inside-work-tree`. A subdirectory of a repo passes, so
   refresh installs and commits nested governance while the root stays
   ungoverned; a bare repo passes the predicate (the command exits 0
   printing `false`) and fails later with a traceback.
6. **A historical hash can widen the current equivalence boundary (review
   M1).** `classify()` consults `formerly` hashes via `candidate_hashes()`
   after the stem-equality check. When an artifact's current content hash
   also appears in its `formerly` list (true today for at least the catchup
   command artifact), a file that is current-plus-one-extra-newline —
   intended to classify as owner-modified — matches `formerly` and is
   silently overwritten as "updated". The review reproduced this against
   the real manifest.
7. **The test suite cannot run at the documented Python 3.9 floor (review
   M9).** `tests/test_refresh.py:62-82` (and helpers) pass `newline=` to
   `Path.write_text()`, a parameter added in Python 3.10, so the canonical
   verification command errors out on 3.9 before asserting anything. The
   README/bootstrap claim of a 3.9 floor is therefore unverifiable by the
   repo's own suite. Related drift: `.agents/repo-guidance.md` says the
   suite "self-shims `python3`" via `tests/_pyshim.py`, but <!-- plan-lint: allow -->
   `ensure_python3()` had no caller (module deleted at `9b3aa64`).

Findings deliberately NOT in this plan (the review's Phase 1+ material —
plan/apply approval protocol, pinned-provenance redesign, self-update
re-exec, release engineering, CI, licensing): they are product-shape
decisions awaiting owner direction, recorded in the final session report,
not silently dropped.

## Slice 0 — raise the documented Python floor (prerequisite)

Owner ruling (2026-07-10): the required version becomes the actual
requirement; no test rewrites for old interpreters.

- The suite's real floor is Python 3.10 (`Path.write_text(newline=...)`,
  added in 3.10, used in `tests/test_refresh.py:62-82`). Update every
  documented floor claim — README, `docs/usage.md`, `procedures/bootstrap.md`
  Step 1 probe wording — from 3.9 to 3.10. On macOS/Windows/Linux this
  means installing a real Python (brew or python.org) rather than relying
  on a stock 3.9; the bootstrap Step 1 probe already falls through to
  versioned interpreter names.
- Resolve the `_pyshim` drift: `ensure_python3()` in `tests/_pyshim.py` <!-- plan-lint: allow -->
  has no caller; wire it back in if subprocess runs still need it, or
  correct the "self-shims" claim in `.agents/repo-guidance.md` — whichever
  the code evidence supports.
- Note: `tests/test_plan_lint.py` intentionally runs on 3.9 and stays so —
  raising the floor does not license new 3.10-only usage there.

## Slice 1 — preflight before mutation (H5 + H7)

All fatal validation moves ahead of the first write:

- Target validation: resolved target must equal
  `git rev-parse --show-toplevel`, and `--is-inside-work-tree` must output
  `true` (rejects bare repos and nested directories with a plain-English
  error). Nested-target installs stop being possible.
- Push-policy preflight: if `.agents/push-policy.md` exists, parse it
  before mutation; malformed/empty → fail with a clear message, exit
  nonzero, nothing written, nothing committed.
- Core-flag computation happens before apply/commit (the banner still
  prints last; only the *computation* moves so a failure cannot follow a
  commit).
- Tests: bare repo rejected; nested directory rejected; empty push-policy
  fails before any write (assert tree untouched, no commit created).

## Slice 2 — filesystem containment (C2)

- Validate the manifest before any mutation: reject absolute targets, `..`
  components, duplicate targets, unknown classes, and malformed hashes.
- For every install/update/remove destination: `lstat()` the leaf and every
  existing parent component; reject symlinks and non-regular files; resolve
  the parent and require containment under the resolved target root.
- Write via a same-directory temporary file and `os.replace()` after
  re-checking the boundary (atomic per file; also shrinks the partial-apply
  window from slice 1's perspective).
- Tests: symlink leaf (broken and live), symlinked parent directory,
  absolute/`..`/duplicate manifest targets — each refused with the tree
  untouched.

## Slice 3 — exact commit scope (H2)

- Commit by explicit pathspec (`git commit -m <msg> -- <touched paths>`)
  so unrelated staged work stays staged and out of the governance commit,
  then verify the created commit's tree touches exactly the planned paths
  (`git show --name-only`); mismatch → report loudly, nonzero exit.
- `--stage-only` keeps its contract (stage and stop); its documented caveat
  is that the bootstrap procedure owns the final commit's scope.
- Tests: unrelated pre-staged file present → governance commit contains
  only planned paths and the unrelated file remains staged; post-commit
  scope verification failure path exercised with a forced mismatch.

## Slice 4 — mirror wording fix (C1 as re-ruled; docs only)

Sync code and behavior UNCHANGED (owner ruling 2026-07-10: GitHub stays
primary, the gitea mirror is owner-controlled and trusted, the fallback is
the mirror's purpose).

- `.agents/repo-guidance.md` (Remotes & Sync): replace "it may lag and is
  never authoritative" with wording matching the 2026-06-10 decision and
  the owner's intent — the mirror is the owner-controlled LAN mirror of
  GitHub, a trusted fetch source that covers GitHub being unreachable; it
  may lag, and lag is expected, never a conflict; canon propagates only
  via pushes to GitHub.
- `procedures/bootstrap.md` Step 0: same alignment where it calls the
  mirror "never authoritative"; the fallback instruction itself stands.
- No test changes (no behavior changed).

## Slice 5 — equivalence boundary integrity (M1)

- When classifying, compute the current source's own candidate-hash set
  first; a `formerly` match that falls inside the current source's
  equivalence class must NOT classify as `update` — it classifies exactly as
  stem-equality dictates (current when stem-equal, otherwise
  owner-modified/flagged). A historical hash never widens the current
  boundary.
- Regression test against the REAL manifest: for every artifact whose
  current candidate hashes overlap its `formerly` list, current-plus-two
  -trailing-newlines must flag as owner-modified, not update.

## Verification

Full suite per `.agents/repo-guidance.md` (Verification) after every slice;
each new guard gets the mutation proof (revert the guard, watch its test go
red, restore). Slice 0's floor check as described there.

## Non-goals and risks

- No plan/apply approval protocol, no manifest schema version, no re-exec
  after self-update, no CI/release work — Phase 1+ material awaiting owner
  direction.
- No sync behavior change and no subprocess timeout/prompt-suppression
  work (owner ruling 2026-07-10; a future one-line ask if hangs ever bite).
- Slice 3's pathspec commit changes commit mechanics on every governed
  repo; the scope-verification step is the guard against surprises.
- Containment checks add `lstat`/`resolve` calls per artifact — negligible
  at shipped-set scale (19 artifacts).

Provenance: untracked holistic review (GPT-5.6-Sol, 2026-07-09), findings
C1, C2, H2, H5, H7, M1, M9, re-verified against `tools/refresh.py` at
`8c3b6e3` by code inspection, 2026-07-10; owner instruction
2026-07-10 to draft plans for the new findings.
