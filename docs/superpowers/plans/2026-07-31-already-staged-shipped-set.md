# Plan: the plan record accounts for an already-staged shipped set

Status: DRAFT 2026-07-31 — awaiting owner approval. One open decision, D1
(Step 2's refusal), is unruled; if D1 is declined, Step 2 drops the refusal
and keeps only the record field, and Step 4's case 5 is dropped with it.
Nothing else in this plan depends on D1.

Addresses Bixi issue #2 (`refresh plan omits canonical files already staged
before the first commit`).

## Problem

`tools/refresh.py` classifies a shipped-set target by comparing the
**working tree** against the canonical source, and knows nothing about the
index. `classify()` puts every byte-identical target in `plan.current`,
`build_record()` serializes only `install`/`update`/`restore`/`remove`, and
`touched_paths()` (the record's `staged_paths`) lists only paths this run
will write.

So in a repository whose canonical shipped set is already staged and not yet
committed — the state `tools/new-project.py` leaves behind, since it runs
`refresh.py --stage-only` before handing the repo to an agent — a plan run
produces an empty record:

- `installs`, `updates`, `restores`, `removes`, `staged_paths`: all empty.
- `summarize()` prints `nothing to do - repo is current`.
- `git diff --cached --name-only` in the same tree lists the constitution,
  the harness shims, the operator wrappers, the playbooks, the skills, and
  the hook files.

`procedures/bootstrap.md` Step 6 requires that the approval summary's
shipped-set list be rendered FROM that record ("never reconstructed by
hand"), and `templates/approval-summary.template.md` repeats the rule. The
record therefore cannot describe the commit the owner is being asked to
approve: the approval summary lists nothing under the shipped set while the
root commit that Step 7 makes contains the whole set.

The hole is not specific to an unborn repository. Any target whose shipped
files were staged by an earlier `--stage-only` run and never committed
reproduces it; the unborn case is simply where it always happens.

`dirty_conflicts()` does not catch it either: it refuses only over paths the
run would touch, and these paths are `current`, so nothing is touched.

## Design

Add one record field, `already_staged`: the manifest-known targets that are
staged with a difference against `HEAD` (in an unborn repository, every
staged path qualifies) and that this run will not itself write.

Properties that make it safe to add:

- **Record-only, for the shipped set only.** Candidates are the `artifacts[]`
  and `seeded[]` targets. Judgment drafts and any other staged path stay out;
  the approval summary already owns those lists from `git check-ignore`.
- **Disjoint from `staged_paths` by construction.** A path this run installs,
  updates, restores, or removes is excluded. A staged non-canonical shipped
  file is already an install/update/restore/flag, and `dirty_conflicts()`
  already refuses over it, so no path can appear in both fields.
- **Seeded targets are included.** A seeded file staged by an earlier run
  (`.agents/push-policy.md` in the `new-project` flow) is invisible to
  `classify()`'s seeded loop once it exists, so it must be picked up here or
  the first commit's scope is understated again.

One `git status --porcelain --no-renames -z -- <candidates>` call answers it.
For each entry, `X` is the index column and `Y` the worktree column:

| X | Y | meaning | result |
| --- | --- | --- | --- |
| in `AMDRC` | `' '` | staged, worktree agrees | `already_staged` |
| in `AMDRC` | not `' '` | staged, then modified in the worktree | `staged_dirty` (D1) |
| `?` or `!` | any | untracked or ignored | ignored here |
| anything else | any | not a staged difference | ignored here |

The `staged_dirty` case is the one state the record cannot describe
honestly: `classify()` read canonical bytes from the worktree, but the
commit would carry the different bytes sitting in the index. **D1 — refuse
it (exit 3), in the shape `dirty_conflicts()` already uses.** The state is
pathological, it is invisible to every existing guard, and the alternative
is a record that says "already staged" about content nobody inspected.

The record must also pin the staged content, not just the path: `--apply`
verifies the record before writing, and an approval that named a path whose
staged bytes have since changed must not silently pass. Each entry carries
the index object id from a single `git ls-files -s` call, treated as an
opaque identity token compared only against itself at apply time (no
assumption about the repository's object-hash format).

The record schema goes to `2`. `verify_record()` accepts exactly the current
schema, so the bump gives an exact refusal ("unsupported plan schema: 1")
instead of a field-drift message for a record made by an older toolkit. No
record survives a toolkit upgrade anyway — `toolkit_sha` and
`manifest_digest` are already compared — and a bootstrap record is generated
and applied inside one session.

## Implementation

One commit per step, in this order.

### Step 1 — `tools/refresh.py`: detection

1. `Plan.__init__`: add

   ```python
   self.already_staged = []  # (target, index object id) - staged, not ours
   self.staged_dirty = []    # target - staged and then modified (D1)
   ```

2. New helper next to `dirty_conflicts()`:

   ```python
   def staged_shipped_paths(target_repo: Path, shipped: dict, plan: Plan):
       """Manifest-known targets already staged against HEAD that this run
       will not write. An unborn repo has no HEAD, so its whole index
       qualifies - which is the bootstrap case this exists for."""
   ```

   - Candidates: `[a["target"] for a in shipped["artifacts"]]` plus
     `[s["target"] for s in shipped.get("seeded", [])]`, minus
     `set(touched_paths(plan))`.
   - Return early on an empty candidate list (no git call).
   - One `git status --porcelain --no-renames -z -- <candidates>` call. Split
     on `\0`, drop empty trailing entries, take `X = entry[0]`,
     `Y = entry[1]`, `path = entry[3:]`.
   - `X in "AMDRC"` and `Y == " "` → staged; `X in "AMDRC"` and `Y != " "` →
     dirty.
   - For the staged set, one `git ls-files -s -z -- <staged paths>` call;
     parse `<mode> <object> <stage>\t<path>` and pair each path with its
     object id. A path that `ls-files` does not report (a staged deletion,
     `X == "D"`) records the empty string as its object id.
   - Sort both lists by target before returning.

3. `classify()` does not change. Call the helper from `main()` immediately
   after `check_committability()` and before `core_flags()`, assigning
   `plan.already_staged` and `plan.staged_dirty`. Rationale: `classify()`
   is the worktree-vs-canonical comparison and stays that; this is an index
   question about the plan `classify()` produced.

### Step 2 — `tools/refresh.py`: refusal and reporting

1. **(D1)** After the existing `dirty_conflicts()` block in `main()`:

   ```python
   if plan.staged_dirty:
       print("refresh: refusing to run; these shipped paths are staged and "
             "then modified in the worktree, so the staged bytes are not the "
             "bytes examined here:", file=sys.stderr)
       for t in plan.staged_dirty:
           print("  " + t, file=sys.stderr)
       return 3
   ```

   Exit 3 is the existing "uncommitted state in the way" code; stage or
   restore the path and re-run.

2. `build_record()`: add

   ```python
   "already_staged": [{"target": t, "index_sha": oid}
                      for t, oid in plan.already_staged],
   ```

   and set `"schema": 2`.

3. `verify_record()`: accept `record.get("schema") != 2` as the unsupported
   case, and add `"already_staged"` to the compared field tuple.

4. `summarize()`: after the install/update/restore/remove lines, one line per
   entry, `  already staged: <target>`, and suppress the
   `nothing to do - repo is current` line when `plan.already_staged` is
   non-empty — that sentence is the misreading the issue reports. The
   summary is what the plan run prints, so the agent writing the approval
   summary sees the same set the record carries.

5. `terse_line()` is unchanged: it reports what the run did, and this run
   does nothing to these paths.

6. Module docstring: one sentence recording that the plan record accounts for
   shipped files already staged but not committed.

### Step 3 — `procedures/bootstrap.md` and the approval-summary template

- `procedures/bootstrap.md` Step 6: state that the summary's shipped-set list
  is rendered from the record's `installs`, `updates`, `restores` **and**
  `already_staged`, marking the already-staged paths as already in the index;
  the commit scope the summary announces is the union.
- `procedures/bootstrap.md` Step 7, standard route: note that
  `refresh.py --apply ... --stage-only` writes nothing for already-staged
  paths and that the scoped commit still covers them — they are already in
  the index, so the `git add` list names only what is not.
- `templates/approval-summary.template.md`, the shipped-set section: the list
  is everything the commit will contain — what the script installs plus the
  canonical files already staged — rendered from the record, never
  reconstructed by hand.
- `procedures/setup.md` is unchanged: the greenfield agent phase commits the
  staged set directly and never generates a plan record.

### Step 4 — tests (`tests/test_refresh.py`)

New `AlreadyStagedTests`, using the hermetic fixture toolkit. Build the
unborn fixture with `init_repo()` and no `commit_all()`, then stage the
shipped set with a `--stage-only` run.

1. **Unborn, staged.** `--plan-json` on the unborn staged repo: `installs`,
   `updates`, `restores`, `removes`, `staged_paths` all empty;
   `already_staged` lists exactly the staged shipped targets, each with a
   non-empty `index_sha`; stdout does not contain
   `nothing to do - repo is current`; exit 0.
2. **Committed is silent.** Commit that same tree, re-run `--plan-json`:
   `already_staged` is empty and the summary is back to
   `nothing to do - repo is current`.
3. **Seeded target counted.** The seeded file staged by the first run appears
   in `already_staged` (it is invisible to the seeded loop once present).
4. **Apply round trip.** `--apply` of the record from case 1 succeeds and
   still writes nothing; unstaging one of the paths and re-applying the same
   record refuses with a `drift in already_staged` problem.
5. **(D1) Staged then modified.** Stage the canonical set, then overwrite one
   of those files in the worktree with different bytes and leave it that way:
   refresh exits 3, names that path on stderr, and writes nothing.
6. **Schema.** A record carrying `"schema": 1` is refused by `--apply` with
   `unsupported plan schema`.

Guard proof: revert Step 1's helper call in `main()` on a throwaway copy,
confirm cases 1, 3 and 4 fail; revert Step 2's refusal, confirm case 5
fails; restore and confirm the suite is green.

### Step 5 — docs and record

- `docs/design.md`: the plan-record section — new `already_staged` field,
  what it means, schema now 2.
- `docs/usage.md`: one line in the bootstrap flow — a repo whose shipped set
  is already staged still gets a complete approval summary.
- `.agents/state.md`: landed entry.
- `.agents/decisions.md`: only if D1 is ruled; the ruling is durable
  (refresh's refusal surface), so record it with its rationale.

## Verification

`<probed-python> -m unittest discover -s tests -v` (interpreter per
`.agents/repo-guidance.md` Verification and `.agents/machines.md`). The plan
lint rides the same suite.

Beyond the suite, one live run against a throwaway repo: `git init`, stage
the shipped set with `--stage-only`, generate a plan record, and confirm the
record and the printed summary both name the staged set.

## Out of scope

- The applying run's terse line and commit message stay as they are: they
  report what the run changed, and an already-staged path is not that.
- No change to `procedures/setup.md` or to `tools/new-project.py`. Leaving
  the shipped set staged is the intended handoff shape; the defect is that
  the plan record could not describe it.
- Judgment drafts, `.bootstrap-tmp/` contents, and any other staged path
  outside the manifest stay out of the record. The approval summary keeps
  sorting those itself.
- `--lint-only` stays blind to the condition: it is read-only, returns before
  `classify()`, and has no record to complete.
