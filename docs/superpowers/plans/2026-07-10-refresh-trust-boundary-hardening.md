# refresh.py: trust-boundary and transaction hardening

Status: DRAFT 2026-07-10 — awaiting owner approval; no implementation
authorized. Drafted on owner instruction ("make whatever plans are needed to
address anything new", 2026-07-10).

## Why this plan exists

An independent holistic review (GPT-5.6-Sol, 2026-07-09, delivered as an
untracked report; disposition "review only, no implementation
authorization") found that the refresh runner's mechanics are weaker than
the governance prose promises. Every finding this plan relies on was
re-verified against `tools/refresh.py` at `8c3b6e3` by direct code reading;
the review's controlled reproductions are noted where they add evidence
beyond code inspection. Findings restated in full here so this plan is
self-contained:

1. **Unauthenticated mirror can decide currency (review C1).**
   `CANONICAL_URLS` (`tools/refresh.py:51-58`) lists the LAN gitea mirror
   (`http://q:3000/...`) after GitHub; `sync_toolkit()` (`:106-120`)
   fast-forwards the toolkit clone to whichever source responds first. When
   GitHub is unreachable, a plain-HTTP LAN host decides what toolkit commit
   is current — and what this repo ships is executable governance
   (`AGENTS.md`, hooks, skills). `procedures/bootstrap.md` Step 0 currently
   endorses the same fallback ("fast-forward ... to gitea's only when GitHub
   did not [respond]"), so this is a recorded-intent change, not just a code
   fix. `.agents/repo-guidance.md` (Remotes & Sync) already says the mirror
   "is never authoritative" — the code and Step 0 are the lower-authority
   sources here. Git subprocesses also have no timeout and no
   `GIT_TERMINAL_PROMPT=0`, so an interactive credential prompt can hang an
   automated run.
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
   suite "self-shims `python3`" via `tests/_pyshim.py`, but
   `ensure_python3()` currently has no caller.

Findings deliberately NOT in this plan (the review's Phase 1+ material —
plan/apply approval protocol, pinned-provenance redesign, self-update
re-exec, release engineering, CI, licensing): they are product-shape
decisions awaiting owner direction, recorded in the final session report,
not silently dropped.

## Slice 0 — test floor repair (prerequisite)

Every later slice adds tests; they must run at the floor the repo claims.

- Replace `Path.write_text(..., newline=...)` in `tests/` with a
  3.9-compatible form (`open(..., "w", newline=...)` or `write_bytes`).
- Resolve the `_pyshim` drift: wire `ensure_python3()` back into the suite
  if subprocess runs still need it, or correct the claim in
  `.agents/repo-guidance.md` — whichever the code evidence supports.
- Verify: full suite green under a 3.9 interpreter if one is available on
  the machine; otherwise state plainly that floor verification was
  code-inspection only and record that as a known gap.

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

## Slice 4 — sync authentication (C1)

- The mirror never decides currency. `sync_toolkit()` fast-forwards only to
  a head attested by GitHub (`ls-remote` on the canonical URL); when GitHub
  is unreachable, proceed on the local copy with the existing flag note —
  never fast-forward to a mirror-only head. The mirror remains usable as an
  object transport for a GitHub-attested SHA (fetch from mirror, verify the
  attested commit is what arrived) — or is dropped from sync entirely if the
  owner prefers; decide at approval.
- All git subprocesses in `refresh.py` gain a bounded timeout and
  `GIT_TERMINAL_PROMPT=0`; a timeout is a failed source, not a hang.
- `procedures/bootstrap.md` Step 0 is amended to match (mirror as transport
  for GitHub-attested heads only; offline → local copy + flag), fixing the
  lower-authority source per the flag-conflicts invariant.
- Tests: fake-remote harness — GitHub down + mirror responding does NOT
  advance the clone; GitHub attesting a SHA the mirror serves does; prompt
  suppression and timeout wiring asserted on the subprocess call.

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
- Slice 4 changes recorded Step 0 behavior; a machine that is offline from
  GitHub but on-LAN loses mirror-driven freshness and proceeds on the local
  copy with a flag. That is the intended trade (mirror is documented
  non-authoritative); the owner should confirm it consciously.
- Slice 3's pathspec commit changes commit mechanics on every governed
  repo; the scope-verification step is the guard against surprises.
- Containment checks add `lstat`/`resolve` calls per artifact — negligible
  at shipped-set scale (19 artifacts).

Provenance: untracked holistic review (GPT-5.6-Sol, 2026-07-09), findings
C1, C2, H2, H5, H7, M1, M9, re-verified against `tools/refresh.py` at
`8c3b6e3` by code inspection, 2026-07-10; owner instruction
2026-07-10 to draft plans for the new findings.
