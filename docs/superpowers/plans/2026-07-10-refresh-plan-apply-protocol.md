# refresh.py: read-only plan / verified apply protocol + provenance integrity

Status: APPROVED 2026-07-10 — owner approval, verbatim: "Approved. Do the
plans for the rest as well." Implementation in progress.

## Why this plan exists

Remaining verified findings from the 2026-07-09 external holistic review
(untracked report; each restated here so this plan is self-contained), the
approval-integrity and provenance cluster:

1. **Approval is not bound to an immutable operation (review H1).**
   `tools/refresh.py` has no read-only planning mode: every mode mutates
   the target (apply/commit or stage). The bootstrap approval summary is
   reconstructed by an agent rather than rendered from the exact operation,
   and `procedures/bootstrap.md` syncs the toolkit at Step 0 but Step 7
   runs refresh WITHOUT `--no-sync` — a second sync can change the manifest
   and templates between what the owner approved and what installs.
2. **Provenance can name bytes that were not installed (review H4).**
   Refresh stamps the target commit with the toolkit `HEAD` while reading
   artifact bytes from the toolkit worktree; a dirty worktree installs
   dirty bytes under a clean SHA. Separately, `sync_toolkit()` can
   fast-forward the toolkit AFTER the running Python process loaded the
   old runner — new manifest read under old code semantics.
3. **Manifest is unversioned (review M2 residue).** Runtime validation of
   paths/classes/hashes landed at `d86856b`; there is still no schema
   version and no digest an approval can pin.
4. **Non-TTY launch commands render POSIX-only (review M7 residue).** The
   banner's ready-to-paste commands use `shlex.join`, which is wrong for
   Windows shells.
5. **"Nothing changes before approval" is broader than intended (review
   M12).** Step 0 syncs the toolkit clone before any approval; the promise
   should name the protected state exactly: the target repository.

## Design

**Plan mode (read-only).** New flag `--plan-json <path or ->`: runs sync
(unless `--no-sync`), classification, committability, and lint exactly as
today, then writes a JSON operation record and exits WITHOUT touching the
target. Record fields: `schema` (int, starts at 1), `toolkit_sha` (full),
`toolkit_dirty` (bool, from `git status --porcelain` on the toolkit),
`manifest_digest` (sha256 of the shipped-set file bytes), `target_head`
(full), `installs`/`updates` (target path + source path + source content
sha256), `removes`, `gitignore_repairs` (line, old, new), `flags`,
`staged_paths` (the exact commit scope), and `digest` (sha256 over the
canonical JSON of everything above). Exit 0.

**Apply mode (verified).** New flag `--apply <plan.json>`: implies
`--no-sync`. Refuses (exit 4, nothing written) unless ALL hold: plan
`schema` is supported; current full toolkit SHA equals `toolkit_sha`;
toolkit worktree is clean AND plan `toolkit_dirty` is false; current
manifest digest equals `manifest_digest`; target `HEAD` equals
`target_head`; a fresh classification reproduces exactly the plan's
installs/updates/removes/repairs (source content hashes included). Then
performs today's apply/stage/commit path (`--stage-only` composes with it
for the bootstrap flow). The commit message body gains the full toolkit
SHA and the plan digest.

**Default mode unchanged.** Direct `refresh.py <repo>` keeps today's
one-shot behavior for the owner's fleet loop, with one addition: if the
toolkit worktree is dirty, the summary prints a loud
`NOTE: toolkit tree is dirty; installed bytes may not match <sha>` line.

**Self-update re-exec.** When `sync_toolkit()` fast-forwards the toolkit
to a NEW head, the runner re-executes itself once
(`os.execv(sys.executable, [... same argv plus --no-sync ...])`, guarded
by an environment marker `AGB_REFRESH_REEXEC=1` so it cannot loop): the
freshly synced runner then reads the freshly synced manifest.

**Manifest schema version.** `tools/shipped-set.json` gains
`"schema": 1`; `validate_manifest` requires it; plan/apply pin it.

**Bootstrap wiring.** `procedures/bootstrap.md`: Step 6 instructs
generating the approval summary's install list FROM a `--plan-json` run
(the machine plan is the single source the summary renders); Step 7's
refresh invocations become `--apply <that plan>` (standard route with
`--stage-only`, carve-out route commit 2 without). The intro's
nothing-changes wording is scoped exactly: "No target-repository files,
index entries, commits, remotes, or settings change before approval;
Step 0 may update the local toolkit clone." Approval-summary template:
the shipped-set section says the list is rendered from the plan run.

**Windows command rendering.** `non_tty_commands` renders each launch
command with `subprocess.list2cmdline` on Windows (`os.name == "nt"`) and
`shlex.join` elsewhere.

## Slices (one commit each)

1. Plan mode: record construction + `--plan-json` + digest; tests (plan
   run mutates nothing — tree, index, and HEAD byte-identical before and
   after; record fields present; digest stable across two runs; digest
   changes when a template byte changes).
2. Apply mode: verification + refusal paths; tests (each pinned field
   drifted one at a time → exit 4, tree untouched; undrifted apply
   reproduces exactly the default mode's result including commit scope;
   `--stage-only --apply` stages without committing).
3. Toolkit provenance: dirty-tree NOTE in default mode + clean-tree
   requirement in apply + full SHA and digest in the commit body; tests
   (dirty toolkit → NOTE printed, apply refused; commit body carries full
   SHA).
4. Self-update re-exec: tests with a fixture remote ahead of the clone —
   the run reports the POST-sync SHA as its operating version and the
   re-exec marker prevents a second exec (subprocess env assertions).
5. Manifest `schema` key + validation + real-manifest update; tests
   (missing/unsupported schema → exit 4).
6. Bootstrap Steps 0/6/7 + approval-summary template wording; Windows
   `list2cmdline` rendering with a unit test on the composed string per
   platform branch (no real launch).

## Verification

Full suite per `.agents/repo-guidance.md` (Verification) after every
slice; every new guard proven by running its tests against the pre-slice
`tools/refresh.py` in a scratch copy (red), then green in the tree. Plans
directory untouched except this file: targeted plan lint on each commit
that touches it.

## Non-goals and risks

- Default mode's behavior is unchanged except the dirty-toolkit NOTE: the
  owner's existing fleet loop needs no flag changes.
- No signed releases, no version/channel policy, no CI — deliberately
  excluded; a separate owner decision covers that ground.
- The plan JSON is a scratch artifact of a bootstrap run (lives under
  `.bootstrap-tmp/`), never committed; nothing new ships to governed
  repos.
- Re-exec is the riskiest piece (argv/env passthrough across platforms);
  its loop guard and tests are mandatory before it lands, and slice 4 can
  be dropped alone if it proves flaky without weakening the other slices
  (apply's SHA pinning already catches the skew it addresses).
