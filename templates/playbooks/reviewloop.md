# Playbook: two-agent review loop (`reviewloop`)

A portable workflow for running a **coder** role and a **reviewer** role over a
multi-fix sweep (security pass, refactor, bug-fix batch) on one git repo, with
strong per-fix verification and a structured handoff channel. One agent can play
both roles (single-agent mode) or two agents can run in parallel.

Invoke it with the `playbook` operator: `playbook reviewloop`. This file is durable
guidance; it defers to this repo's `AGENTS.md` and `.agents/` layout wherever they
overlap. Where this playbook and the repo's invariants disagree, the invariants win.

## Atomic unit

The whole loop rests on one rule: **one finding ↔ one branch ↔ one sentinel ↔ one
verdict**. That is what keeps each fix independently reviewable and bisectable. It is
the same discipline as the repo's one-item-per-commit rule, applied across two roles.
Broad multi-finding branches are forbidden unless the owner explicitly asks for a
sweep.

## Governance alignment (read first)

This playbook is reconciled with the standard `.agents/` governance so it does not
create a parallel canon or bypass owner gates:

- **Status nests under `.agents/`, it does not compete with it.** `.agents/state.md`
  remains the single discoverable current-state entry point. The loop's status index
  lives at `.agents/review/index.md`; `state.md` *points* to it while a loop is
  active rather than duplicating the finding table (pointer doc points; it does not
  keep a second copy of an enumeration another doc owns). There is no root
  `REVIEW.md`.
- **Merging into the main branch is owner-gated.** A reviewer "accept" verdict
  records that a branch passed review; it does **not** authorize the agent to merge
  into the main branch. Default: leave the accepted branch (or hand off a
  `merge-<id>` branch) for an owner-approved merge. Never merge, push, or rewrite
  history without an explicit owner go (see the repo's Git Safety invariants). The
  "auto-merge" knob below is opt-in and requires standing owner authorization.
- **Verification is the repo's observed command, not a hardcoded suite.** Run the
  automated verification command recorded in this repo's `AGENTS.md` / `.agents/`
  guidance before any commit. The example commands in this playbook are illustrative
  only.
- **Capabilities, not harness-specific tool or agent names.** Where this playbook
  says "dispatch a reviewing agent" or "arm a file-watch", it means *whatever
  mechanism your harness provides*; every such step has a no-special-capability
  fallback. Substitute your harness's equivalents.

## Prerequisites

- A git repo.
- An agent (or two) that can run shell commands, read/write files, and — ideally —
  dispatch a subagent and watch files for changes. Both extras have fallbacks below.

## Directory layout

Create this under the existing governance root:

```
.agents/
├── state.md                    Single current-state entry point; points to
│                               .agents/review/index.md while a loop is active.
├── playbooks/reviewloop.md     This playbook.
└── review/                     Working channel for an active loop.
    ├── index.md                Human-readable status index (state.md points here).
    ├── findings/<id>.md        Implementation record per finding.
    ├── ready/<id>.json         Coder → reviewer signal (sentinel).
    └── results/
        ├── <id>.verified.json  Reviewer → coder: accepted (awaiting owner-gated merge).
        └── <id>.reopened.md    Reviewer → coder: needs fix-ups.
```

Commit `.agents/review/` to git: the `ready/` and `results/` trail is part of the
project's verification history.

## Step 1 — Scaffold

```bash
mkdir -p .agents/review/{findings,ready,results}
```

Then add the status index and seed findings (Steps 2–3) before committing.

## Step 2 — Status index: `.agents/review/index.md`

Short, human-readable scoreboard. Per-finding detail lives in
`.agents/review/findings/<id>.md`; do not turn the index into a discussion log.

```markdown
# Review status

Workflow: see `.agents/playbooks/reviewloop.md`.
Per-finding detail: see `.agents/review/findings/<id>.md`.

## Legend
- `[ ]` Open
- `[~]` In progress / pending review
- `[x]` Verified (awaiting owner-gated merge unless auto-merge is authorized)

## Findings

| ID    | Severity | Title                       | Status | Branch |
|-------|----------|-----------------------------|--------|--------|
| sec-1 | HIGH     | <one-line title>            | `[ ]`  |        |
| ...   | ...      | ...                         | ...    | ...    |
```

Add one line to `.agents/state.md` while a loop is active, e.g. "Active review loop:
see `.agents/review/index.md`." Remove it when the loop is done. `state.md` points;
it does not copy the table.

## Step 3 — Per-finding record: `.agents/review/findings/<id>.md`

Written by the coder when they start a finding.

```markdown
# <id>: <title>

**Severity**: CRITICAL | HIGH | MEDIUM | LOW
**Status**: Open | In progress | Verified
**Branch**: `fix/<id-lowercased>-<short-slug>`
**Commit**: `<git-sha>` (filled in after commit)

## What
Concise statement of the bug or risk, with file:line citations. One paragraph.

## Approach
What was done and why it fixes the root cause rather than the surface symptom. Cite
the new/changed functions and files. 2–6 sentences.

## Files changed
- `path/to/file:lines` — what changed

## Tests added
- `path/to/test::name` — what it asserts

## Known gaps
Anything uncertain, out of scope, or overlapping another finding the reviewer should
grade explicitly. Empty if nothing.

## Reviewer comments
(Reviewer writes here on reopen; coder addresses; sentinel resets.)
```

## Step 4 — Branch contract

- **One branch per finding**, named `fix/<id-lowercased>-<short-slug>`.
- **Smallest coherent slice** that addresses one finding id. No bundling.
- Touch only files declared under **Files changed** in the finding doc. Declare any
  unavoidable overlap under **Known gaps**.
- Use `git worktree add <path> fix/<id-…>` for parallel work without checkout thrash.
- Branch from the repo's current main branch; substitute its actual name (`main`,
  `master`, …) wherever this playbook says "the main branch".

## Step 5 — Coder loop

1. Pick the highest-priority `[ ]` (Open) finding in `.agents/review/index.md`.
2. Create the branch (and a worktree if working in parallel). Implement the fix and
   write tests.
3. Run **this repo's observed verification command** (from `AGENTS.md`). Do not
   commit on failure. (Illustrative only — your repo's command may differ:
   `cargo test --workspace`; `npm run lint && npm run build`; `pytest`.)
4. Commit on the finding branch with subject `Fix <id>: <one-line summary>` and a
   body mirroring the finding doc. This is a scoped, per-item commit on a feature
   branch — not the main branch.
5. Fill in **Files changed / Tests added / Known gaps** in the finding doc.
6. Update the index row: `[ ]` → `[~]`, link the branch.
7. Write the sentinel atomically (write to a temp file, then `mv` into place):
   ```bash
   tmp=$(mktemp .agents/review/ready/.<id>.json.XXXX)
   cat > "$tmp" <<EOF
   {"id":"<id>","branch":"fix/<id-…>","sha":"$(git rev-parse HEAD)","ts":"<utc-iso8601>"}
   EOF
   mv "$tmp" .agents/review/ready/<id>.json
   ```
8. Move to the next finding. Do not wait for the verdict to start the next branch —
   but do not stack new work on a branch that already has a pending sentinel.

## Step 6 — Reviewer wake mechanism

If your harness has a file-watch / notification capability, point it at
`.agents/review/ready/` so each new sentinel wakes the reviewer. Otherwise use this
portable polling fallback (no `inotify`/`fswatch` dependency); a low-frequency cron
running the same scan also works:

```bash
cd <repo-root> && last=""
while true; do
  current=$(ls .agents/review/ready/*.json 2>/dev/null | xargs -n1 basename 2>/dev/null | sort | tr '\n' ' ')
  for name in $current; do
    case " $last " in
      *" $name "*) ;;
      *) echo "READY: $name" ;;
    esac
  done
  last="$current"
  sleep 5
done
```

Each new sentinel emits one `READY: <id>.json`. Failure for the reviewer is silence,
caught by a periodic human check-in or a separate heartbeat, not by this loop.

## Step 7 — Reviewer loop

On each new sentinel:

1. Read `.agents/review/ready/<id>.json`; parse `branch` + `sha`. Reject a malformed
   sentinel by writing `.agents/review/results/<id>.reopened.md` noting the schema
   violation.
2. Check out the branch (or use a separate worktree). Run the repo's verification
   command.
3. Review the diff `<main-branch>..<branch>` against the finding scope. If your
   harness supports subagents, dispatch one whose expertise matches the finding's
   domain — name the capability you need (security; concurrency/quality; UI/UX;
   cross-cutting architecture) rather than a fixed agent name. If it does not, review
   directly. Ask only: (a) does the fix address the root cause, (b) are the tests
   adequate, (c) are any regressions introduced.
4. Write the verdict:
   - **Accepted** → `.agents/review/results/<id>.verified.json` (schema below).
     Update the index row to `[x]`. Delete `.agents/review/ready/<id>.json`. Do
     **not** merge into the main branch on your own authority — leave the accepted
     branch (or hand off a `merge-<id>` branch) for an owner-approved merge, unless
     auto-merge is authorized (see Knobs).
   - **Reopened** → `.agents/review/results/<id>.reopened.md` with concrete file:line
     comments. Update the index row to `[ ]`. Delete the ready sentinel. The branch
     stays; the coder pushes fix-ups and writes a fresh sentinel.

## Step 8 — Sentinel schemas

`.agents/review/ready/<id>.json` — all four fields required:

```json
{"id":"sec-1","branch":"fix/sec-1-<slug>","sha":"<git-sha>","ts":"<utc-iso8601>"}
```

`.agents/review/results/<id>.verified.json`:

```json
{"id":"sec-1","sha":"<git-sha>","ts":"<utc-iso8601>","reviewer":"<name>"}
```

`.agents/review/results/<id>.reopened.md`: free-form Markdown with concrete file:line
comments. Clarity over structure.

## WIP limit

- **Strict (default)**: at most one branch may have a pending sentinel at a time.
- **Faster**: multiple pending sentinels allowed only if each branch's **Files
  changed** set is fully disjoint from every other pending branch.

## Migrating existing WIP

If multi-finding WIP accumulated before adopting this loop, split it into per-finding
branches; the reviewer does **not** commit on the coder's behalf:

```bash
git stash
git stash show -p > /tmp/wip.patch            # inspect
# For each finding id:
git checkout -b fix/<id>-<slug> <main-branch>
git checkout -p stash@{0} -- <relevant paths>  # or: git apply a path-filtered patch
# run verification, commit, write sentinel
```

For genuinely entangled WIP, document the entanglement under **Known gaps** and ship
one branch covering both; the reviewer grades them together and flags the bundling as
a process violation, not a code defect.

## Anti-patterns

- **Broad sweeps.** "Fix sec-1..sec-9 in one commit" kills bisection. Owner-request
  only.
- **Merging or pushing without an owner go.** Accept is a verdict, not merge
  authority.
- **Rewriting history** (amend/rebase/squash/force-push) on reviewed work without an
  explicit owner go.
- **Editing the index prose freely.** It is a status board; discussion goes in the
  finding or reopened doc.
- **Skipping the sentinel.** No sentinel = no review; the watcher watches sentinels,
  not commits.
- **Stacking commits on a pending-review branch.** Wait for the verdict or signal a
  fresh sentinel.
- **Reviewer modifying the coder's branch.** Reviewer's job is verdict + (owner-gated)
  merge or reopen, not pushing fix-ups.

## Knobs

- **Single-agent mode**: one agent alternates coder and reviewer hats; drop the WIP
  limit (it serializes naturally) but keep per-finding branches and the sentinel /
  results trail.
- **Multiple coders**: each owns disjoint findings; enforce disjointness via the
  faster-mode WIP limit; coders add `"coder":"<name>"` to the sentinel.
- **Multiple reviewers**: reviewer identity goes in the verified sentinel; load-balance
  with a per-reviewer watch and a domain filter.
- **Auto-merge (opt-in, owner-authorized only)**: with standing owner authorization
  for the session, the reviewer may fast-forward an accepted branch into the main
  branch. Without that authorization the default stands: hand off for an owner-approved
  merge.
