# Plan: refresh prunes directories it leaves empty

Status: Approved (owner go 2026-07-25) — "if folder empty remove it in final
cleanup step with Y/n prompt". No open decision blocks the work below.

## Problem

`apply_plan()` unlinks a retired target but never touches the directory that
held it, so removing the last file from a directory leaves the directory
behind. Git cannot see the result — it does not track empty directories — so
nothing reports it and it survives every later run.

Observed in this repo after the 2026-07-24 refresh (`064c27e`) retired the
`drift` and `harness-update` skills: `.agents/skills/drift/` and
`.agents/skills/harness-update/` remained as empty directories, and an agent
listing `.agents/skills/` saw two skills that did not exist. Every governed
repo that carried either skill has the same litter.

## Design

A final cleanup step, after the reconcile and its commit, asking once before
removing anything.

**Scope — which directories are candidates.** Only directories at or below
the governance roots the manifest itself names: the first path segment of
every `artifacts[]`, `retired[]`, and `seeded[]` target (`.agents`,
`.claude`, `.codex`, `.grok`). Never the repo root, never a path outside
those roots, never a root itself even when empty. This keeps the sweep
inside the tree the toolkit owns.

**Condition.** A candidate is removable only when it contains no entries at
all, including dotfiles. An empty directory cannot hold tracked content —
git does not track directories — so removal can never destroy committed
work, and the dirty-tree refusal has already run.

Walk bottom-up so a directory whose only child was itself an emptied
directory is caught in the same pass.

**Consent.** One Y/n prompt listing the directories, defaulting to yes
(`[Y/n]`), asked only at a real TTY (`sys.stdin.isatty() and
sys.stdout.isatty()`), matching how `offer_bootstrap()` and
`new-project.offer_launch()` gate their prompts. Non-interactive runs — CI,
loops, `--plan-json`, `--apply` — never prompt and never remove; they print
one line naming the count and the paths so the condition is visible.
`--no-remediate` also suppresses the prompt, since that flag already means
"never ask, this is automated".

**Reporting.** Removals print one `pruned:` line per directory. Nothing
enters the commit: the removals are untracked by definition, so there is
nothing to stage, and the plan record is unchanged. This keeps the step
outside `build_record()`/`verify_record()` entirely — a pruned directory can
never invalidate an approved plan.

## Implementation

### Step 1 — `tools/refresh.py`

1. `governance_roots(shipped)` — the set of first path segments across
   `artifacts[]`, `retired[]`, and `seeded[]` targets.
2. `emptied_dirs(target_repo, shipped)` — walk each existing root bottom-up
   with `os.walk(topdown=False)`, collecting directories with no entries,
   excluding the roots themselves. Returns repo-relative POSIX paths,
   sorted. Read-only.
3. `prune_dirs(target_repo, dirs)` — `rmdir` each, deepest first; a
   non-empty directory (racing writer) raises `OSError` and is skipped with
   a printed note rather than escalated.
4. Call site in `main()`, after the commit and the terse line, before the
   lint findings: compute candidates; if none, do nothing at all. If a TTY
   and not `--no-remediate`, print the list and ask
   `Remove N empty director{y,ies} left by retired files? [Y/n]`; empty
   input or `y` removes, anything else declines. Otherwise print the list
   with a note that nothing was removed. Never reached in `--lint-only` or
   `--plan-json`, both of which return earlier.

### Step 2 — tests (`tests/test_refresh.py`)

Against the hermetic fixture, extending the existing retired-target
coverage:

1. Retiring the last file in a directory leaves the directory empty, and a
   non-interactive run reports it without removing it (the file is gone, the
   directory remains, stdout names it).
2. `emptied_dirs()` finds a nested empty directory bottom-up and excludes a
   root that is itself empty.
3. `emptied_dirs()` ignores a directory holding an unrelated untracked file,
   and one outside the governance roots entirely.
4. `prune_dirs()` removes deepest-first and survives a directory that is not
   empty.
5. The consent path: with the prompt function stubbed, "y" and empty input
   remove, "n" declines, and the declined directories still exist.

Guard proof: revert the `emptied_dirs()` call site, confirm the reporting
tests fail, restore, confirm green. Mutate a throwaway copy, never the
tracked file.

### Step 3 — docs

`docs/design.md` gains the cleanup step in the refresh description;
`docs/usage.md` notes that refresh offers to tidy directories left empty by
retired files and never removes anything without asking.

## Verification

`<probed-python> -m unittest discover -s tests -v` (interpreter per
`.agents/repo-guidance.md`), plus a live run against a throwaway repo that
carries an empty governance directory, checking both the accept and decline
paths.

## Out of scope

- Pruning empty directories anywhere outside the manifest's own roots.
- Any change to what is committed: pruning stays out of the plan record and
  out of the refresh commit.
