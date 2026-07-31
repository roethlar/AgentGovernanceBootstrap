# Plan: the plan record accounts for an already-staged shipped set

Status: DRAFT 2026-07-31 — awaiting owner approval. No open decisions.

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

Add one record field, `already_staged`: the sorted manifest-known targets
that are staged with a difference against `HEAD` (in an unborn repository,
every staged path qualifies) and that this run will not itself write.

It answers one question — **what is already in the index and will therefore
be in the approved commit** — and nothing else.

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

One `git status --porcelain --no-renames -z -- <candidates>` call answers it:
for each entry, the index column `X` in `AMDRC` means staged, and `?` or `!`
(untracked, ignored) and anything else means not staged. The worktree column
`Y` is deliberately **not** consulted, and staged-then-modified paths
(`AM`) are listed like any other:

- It is the normal greenfield flow, not a pathology. `new-project` stages
  `.agents/push-policy.md` at its default and `procedures/setup.md` Step 3
  then edits that same staged file to record the owner's answer before the
  first commit.
- The scope answer is the same either way: the path is in the index and will
  be in the commit. Which bytes land is settled by the `git add` the
  procedure already performs at commit time.

**Paths only, no content hashes.** The field carries no `sha256` or index
object id, unlike `installs`/`updates`/`restores`. Pinning content here
would refuse the standard bootstrap flow: `procedures/bootstrap.md` drafts
its own `.agents/push-policy.md`, so Step 7 legitimately restages that path
between plan and apply, and a content pin would read that as drift.
`verify_record()` compares the path list, which is stable across that flow
and still catches a real scope change — a shipped path staged or unstaged
after approval.

Accepted consequence: for these paths the record pins scope, not content.
That matches what they are — paths outside anything refresh writes, whose
content is the owner's and the procedure's business.

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
   self.already_staged = []  # target - staged already, not written by us
   ```

2. New helper next to `dirty_conflicts()`:

   ```python
   def staged_shipped_paths(target_repo: Path, shipped: dict, plan: Plan) -> list:
       """Manifest-known targets already staged against HEAD that this run
       will not write. An unborn repo has no HEAD, so its whole index
       qualifies - which is the bootstrap case this exists for."""
   ```

   - Candidates: `[a["target"] for a in shipped["artifacts"]]` plus
     `[s["target"] for s in shipped.get("seeded", [])]`, minus
     `set(touched_paths(plan))`.
   - Return `[]` on an empty candidate list, without a git call.
   - One `git status --porcelain --no-renames -z -- <candidates>` call. Split
     on `\0`, drop empty trailing entries, take `X = entry[0]` and
     `path = entry[3:]`.
   - Keep the path when `X in "AMDRC"`. Return sorted.

3. `classify()` does not change. Call the helper from `main()` immediately
   after `check_committability()` and before `core_flags()`, assigning
   `plan.already_staged`. Rationale: `classify()` is the worktree-vs-canonical
   comparison and stays that; this is an index question about the plan
   `classify()` produced.

### Step 2 — `tools/refresh.py`: the record and the summary

1. `build_record()`: add `"already_staged": list(plan.already_staged),` and
   set `"schema": 2`.
2. `verify_record()`: treat `record.get("schema") != 2` as the unsupported
   case, and add `"already_staged"` to the compared field tuple.
3. `summarize()`: after the install/update/restore/remove lines, one line per
   path, `  already staged: <target>`, and suppress the
   `nothing to do - repo is current` line when `plan.already_staged` is
   non-empty — that sentence is the misreading the issue reports. The
   summary is what the plan run prints, so the agent writing the approval
   summary sees the same set the record carries.
4. `terse_line()` is unchanged: it reports what the run did, and this run
   does nothing to these paths.
5. Module docstring: one sentence recording that the plan record accounts for
   shipped files already staged but not committed.

No new refusal. Nothing about this condition blocks a run.

### Step 3 — `procedures/bootstrap.md` and the approval-summary template

- `procedures/bootstrap.md` Step 6: state that the summary's shipped-set list
  is rendered from the record's `installs`, `updates`, `restores` **and**
  `already_staged`, marking the already-staged paths as already in the index;
  the commit scope the summary announces is the union.
- `procedures/bootstrap.md` Step 7, standard route: note that
  `refresh.py --apply ... --stage-only` writes nothing for already-staged
  paths and that the scoped commit still covers them.
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
   `already_staged` lists exactly the staged shipped targets; stdout does not
   contain `nothing to do - repo is current`; exit 0.
2. **Committed is silent.** Commit that same tree, re-run `--plan-json`:
   `already_staged` is empty and the summary is back to
   `nothing to do - repo is current`.
3. **Seeded target counted.** The seeded file staged by the first run appears
   in `already_staged` (it is invisible to the seeded loop once present).
4. **Staged then modified is still listed, never refused.** Overwrite one
   staged canonical file in the worktree with different bytes and leave it
   that way: the run still exits 0 and still lists that path in
   `already_staged`. This is the `new-project` + `setup.md` Step 3 shape.
5. **Apply round trip.** `--apply` of the record from case 1 succeeds and
   still writes nothing; unstaging one of those paths and re-applying the
   same record refuses with a `drift in already_staged` problem.
6. **Schema.** A record carrying `"schema": 1` is refused by `--apply` with
   `unsupported plan schema`.

Guard proof: revert Step 1's helper call in `main()` on a throwaway copy,
confirm cases 1, 3, 4 and 5 fail; restore and confirm the suite is green.

### Step 5 — docs and record

- `docs/design.md`: the plan-record section — new `already_staged` field,
  what it means, schema now 2.
- `docs/usage.md`: one line in the bootstrap flow — a repo whose shipped set
  is already staged still gets a complete approval summary.
- `.agents/state.md`: landed entry.
- `.agents/decisions.md`: no entry. Nothing here settles a durable policy
  question; the field is a record completeness fix.

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
