# Playbook: two-agent review loop (`reviewloop`)

A portable workflow for running a **coder** role and a **reviewer** role over a
multi-fix sweep (security pass, refactor, bug-fix batch) on one git repo, with
strong per-fix verification and a structured handoff channel. One agent can play
both roles (single-agent mode) or two agents can run in parallel.

Invoke it with the `playbook` operator: `playbook reviewloop`. This file is durable
guidance; it defers to this repo's `AGENTS.md` and `.agents/` layout wherever they
overlap. Where this playbook and the repo's invariants disagree, the invariants win.

## What this loop is for

The loop exists to converge on **correct** code, not merely on **changed** code. Two
roles only add signal if each can return the unwelcome answer: the reviewer must be
able to find nothing, and the coder must be able to reject a finding. A loop where the
reviewer always finds something and the coder always agrees produces motion without
information — it will "fix" non-problems, accept wrong corrections, and oscillate, while
looking productive. Guard against both halves explicitly:

- **Reviewer inflation.** A reviewer who treats "find an issue" as the task will almost
  always return one. A pass that surfaces no material issue is a valid, complete,
  expected result — not a failure to do the job.
- **Author capitulation.** A coder who treats every finding as valid will "fix" things
  that were never broken and accept critiques that are wrong. Agreement is only signal
  when disagreement was available.

The cure is the same one the repo already trusts elsewhere: **route correctness through
verification, not through agreement.** Two roles agreeing is still opinion. A test that
fails before a fix and passes after is evidence. Every gate below is built so that a
finding has to predict an observable failure and a fix has to demonstrate it closed one.

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
- **Disagreement is a recorded verdict, never a silent veto.** Declining a finding,
  disputing one, or ruling a fix invalid are all logged outcomes that route to the
  owner when the two roles cannot agree. An agent never quietly drops a finding or
  overrides a critique without leaving the reason in the results trail. This keeps the
  loop inside the repo's "answer with words, act only on an explicit go" invariant.
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
    ├── findings/<id>.md        Candidate + implementation record per finding.
    ├── ready/<id>.json         Coder → reviewer signal (sentinel).
    └── results/
        ├── <id>.verified.json  Reviewer → coder: accepted (awaiting owner-gated merge).
        ├── <id>.reopened.md    Reviewer → coder: needs fix-ups.
        └── <id>.contested.md   Disagreement (declined / disputed / invalid) → owner.
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
- `[ ]` Admitted, open (passed intake triage; not yet started)
- `[~]` In progress / pending review
- `[x]` Verified (awaiting owner-gated merge unless auto-merge is authorized)
- `[!]` Contested — declined, disputed, or ruled invalid; awaiting owner adjudication
- `[-]` Declined at intake (kept for the record; no work)

## Findings

| ID    | Severity | Impact (one line)            | Status | Branch |
|-------|----------|------------------------------|--------|--------|
| sec-1 | HIGH     | <observable consequence>     | `[ ]`  |        |
| ...   | ...      | ...                          | ...    | ...    |
```

Add one line to `.agents/state.md` while a loop is active, e.g. "Active review loop:
see `.agents/review/index.md`." Remove it when the loop is done. `state.md` points;
it does not copy the table.

## Step 3 — Finding intake and triage

This is the gate the false-positive problem dies at, before any branch is cut. It
applies whether findings come from a human, the coder, a separate review pass, or a
second model.

**A review pass that finds no material issue is a complete, valid result.** Record it
as one plain sentence ("Reviewed <scope>; no material issue found") and stop. Do not
manufacture findings to justify the pass. An empty findings table is a legitimate
outcome of this playbook.

Every candidate finding must carry three things before it can be admitted:

1. **Evidence** — concrete `file:line` citation(s) and the specific input, path, or
   condition that triggers the problem. A finding that cannot point at code is not a
   finding.
2. **Predicted observable failure** — what goes wrong that someone or something could
   detect: a wrong result, a crash, a security exposure, a failing or missing test, a
   measurable regression. "Could be cleaner," "not idiomatic," or "I would have written
   it differently" are not observable failures.
3. **Justified severity** — CRITICAL | HIGH | MEDIUM | LOW, with a one-line reason tied
   to the predicted failure, not to taste.

**Triage each candidate to a verdict:**

- **ADMITTED** → it has evidence, a predicted failure, and a justified severity. Give
  it an id, add a `[ ]` row, write the finding doc (Step 4).
- **DECLINED** → it lacks evidence or a predicted observable failure, is style-only, is
  out of scope, or duplicates another finding. Record it as a `[-]` row and write one
  line in `.agents/review/results/<id>.contested.md` stating why. Declining is the
  expected fate of most stylistic or speculative findings; it is the loop working, not
  failing.

If a single agent is generating and triaging its own findings, it must still write the
DECLINED reasons down — the discipline is in making the rejection explicit and
reviewable, not in who performs it. Severity is not decoration: if you cannot write the
impact line, the finding is a DECLINE or a LOW, not a CRITICAL.

## Step 4 — Per-finding record: `.agents/review/findings/<id>.md`

Written when a finding is admitted; the coder completes the lower half when work starts.

```markdown
# <id>: <title>

**Severity**: CRITICAL | HIGH | MEDIUM | LOW — <one-line justification>
**Status**: Open | In progress | Verified | Contested
**Branch**: `fix/<id-lowercased>-<short-slug>`
**Commit**: `<git-sha>` (filled in after commit)

## Evidence
`file:line` citation(s) and the input/condition that triggers the problem.

## Predicted observable failure
What detectably goes wrong, and — where possible — the test or check that would catch
it. This is the claim the fix must prove it closed.

## What
Concise statement of the bug or risk. One paragraph.

## Approach
What was done and why it fixes the root cause rather than the surface symptom. Cite
the new/changed functions and files. 2–6 sentences.

## Files changed
- `path/to/file:lines` — what changed

## Guard proof
- `path/to/test::name` — the assertion. Reverting the fix makes this FAIL; restoring
  makes it PASS. (See Step 8.) If the change is genuinely untestable, state why and
  name the manual check that was run instead.

## Coder dispute (if any)
If the coder believes the finding is wrong or not worth fixing, state the reason here
instead of implementing, and route to a Contested verdict (Step 6). Empty otherwise.

## Known gaps
Anything uncertain, out of scope, or overlapping another finding the reviewer should
grade explicitly. Empty if nothing.

## Reviewer comments
(Reviewer writes here on reopen; coder addresses; sentinel resets.)
```

## Step 5 — Branch contract

- **One branch per finding**, named `fix/<id-lowercased>-<short-slug>`.
- **Smallest coherent slice** that addresses one finding id. No bundling.
- Touch only files declared under **Files changed** in the finding doc. Declare any
  unavoidable overlap under **Known gaps**.
- Use `git worktree add <path> fix/<id-…>` for parallel work without checkout thrash.
- Branch from the repo's current main branch; substitute its actual name (`main`,
  `master`, …) wherever this playbook says "the main branch".

## Step 6 — Coder loop

1. Pick the highest-priority `[ ]` (Open) finding in `.agents/review/index.md`.
2. **Decide whether the finding holds.** If you judge it wrong, already handled, or not
   worth the change, do not implement it. Fill in **Coder dispute** in the finding doc,
   set the row to `[!]`, write `.agents/review/results/<id>.contested.md` with the
   reason, and move on. The owner (or an adjudication pass) resolves it; you do not
   silently drop it, and you do not implement a fix you believe is unwarranted just to
   clear the row. A disputed finding is the loop working.
3. Otherwise create the branch (and a worktree if working in parallel). Implement the
   fix and write the test that encodes the **Predicted observable failure**.
4. Run **this repo's observed verification command** (from `AGENTS.md`). Do not
   commit on failure. (Illustrative only — your repo's command may differ:
   `cargo test --workspace`; `npm run lint && npm run build`; `pytest`.)
5. **Prove the test guards the fix** (the repo's vacuous-test rule): temporarily revert
   the fix, confirm the new test FAILS, restore the fix, confirm it PASSES. A test that
   passes with the fix reverted proves nothing and must be replaced. Record the result
   under **Guard proof**. If the change is genuinely untestable, say why and name the
   manual check instead.
6. Commit on the finding branch with subject `Fix <id>: <one-line summary>` and a
   body mirroring the finding doc. Scoped, per-item commit on a feature branch — not the
   main branch.
7. Fill in **Files changed / Guard proof / Known gaps** in the finding doc.
8. Update the index row: `[ ]` → `[~]`, link the branch.
9. Write the sentinel atomically (write to a temp file, then `mv` into place):
   ```bash
   tmp=$(mktemp .agents/review/ready/.<id>.json.XXXX)
   cat > "$tmp" <<EOF
   {"id":"<id>","branch":"fix/<id-…>","sha":"$(git rev-parse HEAD)","guard":"<test::name or 'manual: …'>","ts":"<utc-iso8601>"}
   EOF
   mv "$tmp" .agents/review/ready/<id>.json
   ```
10. Move to the next finding. Do not wait for the verdict to start the next branch —
    but do not stack new work on a branch that already has a pending sentinel.

## Step 7 — Reviewer wake mechanism

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

## Step 8 — Reviewer loop

On each new sentinel:

1. Read `.agents/review/ready/<id>.json`; parse `branch` + `sha` + `guard`. Reject a
   malformed sentinel by writing `.agents/review/results/<id>.reopened.md` noting the
   schema violation.
2. Check out the branch (or use a separate worktree). Run the repo's verification
   command.
3. **Independently confirm the guard proof.** Revert the fix commit, confirm the named
   test FAILS, restore, confirm it PASSES. If the guard does not behave as the finding
   doc claims — the test passes with the fix reverted, or there is no test and no
   adequate manual justification — the fix is unproven regardless of how reasonable it
   looks. Treat that as Reopened (no proof) at minimum.
4. Review the diff `<main-branch>..<branch>` against the finding scope. If your
   harness supports subagents, dispatch one whose expertise matches the finding's
   domain — name the capability you need (security; concurrency/quality; UI/UX;
   cross-cutting architecture) rather than a fixed agent name. If it does not, review
   directly. Ask only: (a) does the fix address the root cause, (b) does the guard proof
   hold, (c) are any regressions introduced.
5. Write exactly one verdict:
   - **Accepted** → `.agents/review/results/<id>.verified.json` (schema below), only if
     the guard proof holds. Update the index row to `[x]`. Delete the ready sentinel. Do
     **not** merge into the main branch on your own authority — leave the accepted branch
     (or hand off a `merge-<id>` branch) for an owner-approved merge, unless auto-merge is
     authorized (see Knobs).
   - **Reopened** → `.agents/review/results/<id>.reopened.md` with concrete `file:line`
     comments (missing guard proof, inadequate test, regression, wrong root cause).
     Update the row to `[ ]`. Delete the ready sentinel. The branch stays; the coder
     pushes fix-ups and writes a fresh sentinel.
   - **Invalid** → `.agents/review/results/<id>.contested.md` when the *finding itself*
     does not hold: the predicted failure cannot be reproduced, or the "fix" addresses a
     non-problem. Update the row to `[!]`. This routes to the owner; the reviewer does not
     unilaterally discard a finding the coder implemented, nor rubber-stamp a fix for a
     problem that cannot be shown to exist.

A reviewer that returns Accepted on every sentinel, or never returns Reopened/Invalid,
is exhibiting the same capitulation this playbook exists to prevent. Verdicts should
track the guard proof and the diff, not the wish to close rows.

## Step 9 — Sentinel schemas

`.agents/review/ready/<id>.json` — all fields required:

```json
{"id":"sec-1","branch":"fix/sec-1-<slug>","sha":"<git-sha>","guard":"<test::name or 'manual: …'>","ts":"<utc-iso8601>"}
```

`.agents/review/results/<id>.verified.json`:

```json
{"id":"sec-1","sha":"<git-sha>","guard":"<test::name>","guard_proved":true,"ts":"<utc-iso8601>","reviewer":"<name>"}
```

`guard_proved` records that the reviewer independently saw the test fail on revert and
pass on restore. An Accepted verdict with `guard_proved:false` is only legitimate for an
explicitly justified untestable change, and the justification goes in the finding doc.

`.agents/review/results/<id>.reopened.md`: free-form Markdown with concrete `file:line`
comments. Clarity over structure.

`.agents/review/results/<id>.contested.md`: states which kind of disagreement (declined
at intake / coder dispute / reviewer-invalid), the reason, and what the owner needs to
decide. This is the only channel for dropping or overriding a finding.

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
# run verification, prove the guard, commit, write sentinel
```

For genuinely entangled WIP, document the entanglement under **Known gaps** and ship
one branch covering both; the reviewer grades them together and flags the bundling as
a process violation, not a code defect.

## Calibration anti-patterns

These are the failure modes that make a two-role loop produce motion without signal.
Name them when they appear; they are process defects, not code defects.

- **Reviewer inflation.** Returning a finding on every pass because "no issues" feels
  like not doing the job. Cure: an empty findings table is a valid result; every
  admitted finding needs a predicted observable failure.
- **Author capitulation.** Accepting every finding as valid and implementing a change
  for each. Cure: the coder must judge each finding and route wrong ones to a Contested
  verdict instead of fixing them.
- **Severity decoration.** Tagging findings CRITICAL/HIGH without an impact line.
  Cure: no impact line, no high severity — downgrade or decline.
- **Churn without evidence.** A "fix" that no test can distinguish from the original.
  Cure: the guard proof; if reverting the fix breaks nothing, the change is churn and
  should be Reopened or Declined.
- **Convergence read as correctness.** Treating two roles agreeing as proof the code is
  right. Cure: agreement is not the gate; the guard proof is. The verified sentinel
  records the proof, not the consensus.

## Anti-patterns

- **Broad sweeps.** "Fix sec-1..sec-9 in one commit" kills bisection. Owner-request
  only.
- **Manufacturing findings.** Inventing issues so a pass has output. A clean pass is a
  result.
- **Silent veto.** Dropping or overriding a finding without a Contested record.
- **Merging or pushing without an owner go.** Accept is a verdict, not merge authority.
- **Rewriting history** (amend/rebase/squash/force-push) on reviewed work without an
  explicit owner go.
- **Accepting on an unproven guard.** No guard proof = Reopened, not Accepted.
- **Editing the index prose freely.** It is a status board; discussion goes in the
  finding or results doc.
- **Skipping the sentinel.** No sentinel = no review; the watcher watches sentinels,
  not commits.
- **Stacking commits on a pending-review branch.** Wait for the verdict or signal a
  fresh sentinel.
- **Reviewer modifying the coder's branch.** Reviewer's job is verdict + (owner-gated)
  merge or reopen, not pushing fix-ups.

## Knobs

- **Single-agent mode**: one agent alternates coder and reviewer hats; drop the WIP
  limit (it serializes naturally) but keep per-finding branches, the guard proof, and
  the sentinel / results trail. The discipline that matters in this mode is writing the
  DECLINED and Contested reasons down even though one mind holds both roles — that is
  what stops self-agreement from collapsing the loop.
- **Multiple coders**: each owns disjoint findings; enforce disjointness via the
  faster-mode WIP limit; coders add `"coder":"<name>"` to the sentinel.
- **Multiple reviewers**: reviewer identity goes in the verified sentinel; load-balance
  with a per-reviewer watch and a domain filter.
- **Adjudicator (optional)**: when coder and reviewer disagree (a Contested record),
  a third role — or the owner — reads the finding, the dispute, and the guard proof and
  issues a final ADMIT/DECLINE. Useful when the coder and reviewer are two models prone
  to deferring to each other.
- **Auto-merge (opt-in, owner-authorized only)**: with standing owner authorization
  for the session, the reviewer may fast-forward an accepted branch into the main
  branch. Without that authorization the default stands: hand off for an owner-approved
  merge.
