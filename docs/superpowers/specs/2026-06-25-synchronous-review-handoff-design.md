# Synchronous cross-harness review handoff (`/review <agent>`)

**Status:** Design, awaiting owner review
**Date:** 2026-06-25

## Problem

The owner reviews code by running two agent harnesses (e.g. Claude Code and
`codex`, or `agy`/`grok`) in the same workspace and copy/pasting review prose and
responses between the two windows by hand. The goal is accuracy and quality — a
second model's independent eyes on a fix — but the manual relay is slow, lossy,
and leaves no durable record.

The `reviewloop` playbook (`templates/playbooks/reviewloop.md`, commit `498c056`)
addressed the *discipline* of a two-role loop (intake triage, guard proof,
contested verdicts, owner-gated merge) but coordinated the two roles through an
asynchronous file-sentinel bus (`ready/` + `results/`, a watcher, JSON schemas).
That machinery assumed a persistent reviewer process. There is no supported way to
inject a turn into an already-running interactive `codex`/`agy`/`grok`/Claude Code
session from outside it, so a persistent reviewer would just reintroduce the
manual TTY relay. The async bus is therefore unnecessary complexity for the
owner's actual workflow.

## Goal

Automate the relay: the coding agent itself dispatches the reviewer agent headless,
reads its verdict, records it in the repo, and acts — with the owner out of the
copy/paste loop but still the gate for merges.

Non-goals: speed/parallelism (the owner explicitly prefers accuracy over a
race-ahead mode), multi-coder/multi-reviewer fan-out, and driving any role as a
long-lived process.

## Design

### Roles

- The **coder** is the current harness — whatever the owner launched from (normally
  Claude Code). It always plays the coder; the owner stays in the driving seat.
- The **reviewer** is the agent named in the command argument (`codex`, `agy`,
  `grok`, a Claude subagent, …). It is dispatched **headless and one-shot** per
  finding. A second model's independent judgment is the entire value.

### Entry point

- **One operator: `review <agent>`.** Harness-neutral vocabulary. In Claude Code it
  is exposed as a tab-completable slash command `/review <agent>`; on another
  harness the owner speaks "review \<agent\>". The slash command is a thin pointer
  to the playbook (matching the existing `.claude/commands/*.md` wrapper pattern);
  the **playbook owns the semantics**.
- There is **no `/reviewquick`** and **no quick/wait WIP toggle.** The flow is
  synchronous by construction — the coder blocks on each review — so "wait" is the
  only mode. This dissolves the prior, underspecified Strict/Faster WIP-mode
  distinction rather than defining a toggle for it.

### Mechanism (per finding)

1. The coder finishes a fix on a per-finding branch (`fix/<id>-<slug>`), having
   passed intake triage and produced a guard proof — all unchanged from the
   discipline the current playbook already defines.
2. The coder dispatches the reviewer **headless, non-interactive, one-shot** against
   that branch and the finding doc. The reviewer reads the code **from the shared
   workspace** — the diff is *not* marshalled across the process boundary. The
   handoff pins an **explicit base**: the coder passes the reviewed branch HEAD SHA
   and the base SHA (the merge-base at dispatch time), so the reviewer evaluates
   `git diff <base-sha>..<head-sha>` against a fixed snapshot. This avoids the drift
   when the main branch moves mid-review (a `main..branch` range is not stable).
   **Guard-proof isolation:** the reviewer performs its independent guard proof
   (revert → confirm FAIL → restore → confirm PASS) in **its own `git worktree`**
   checked out at the head SHA — never by mutating the coder's working tree. A
   reviewer that crashes mid-proof leaves only its disposable worktree dirty, not the
   coder's branch. The reviewer must not write to the coder's tree at all (verdict
   excepted, below).
3. **Verdict contract (structured, fail-closed).** The reviewer is invoked in the
   harness's **JSON output mode** (e.g. grok `--output-format json`; the agy/codex
   equivalents — derived live by the same probe as the launch incantation, since the
   flag appears in `--help`). This separates the *transport* (the harness's JSON
   envelope, free of logs/ANSI/reasoning) from the *verdict payload*. The reviewer is
   instructed to make its result field a JSON object matching:
   ```json
   {"verdict":"accepted|reopened|invalid","guard_confirmed":true,
    "reviewed_sha":"<head-sha>","base_sha":"<base-sha>","comments":["file:line — …"]}
   ```
   The coder parses the envelope's result field against this schema. **Fail closed:**
   any of {non-zero exit, missing/!valid JSON envelope, result field not matching the
   schema, `verdict` not in the enum, `reviewed_sha` ≠ the dispatched head SHA} →
   the outcome is **not accepted**. The coder re-prompts once with the schema
   restated; if it still fails, the finding is routed to the owner as contested. A
   parse miss never silently becomes an accept. (Note: the harness's JSON mode
   guarantees a valid *envelope*, not that the model filled the *payload* to schema —
   hence the inner parse + fail-closed rule, not envelope-validity alone.)
4. **Before acting, the coder records the verdict into the repo** — the durable trail
   that replaces the deleted sentinel/results files. The record (in the finding doc's
   `## Reviewer comments`, with the **Status** flipped) captures: reviewer **harness
   name + version**, the **reviewed head SHA and base SHA**, **`guard_confirmed`**,
   the **verdict**, a UTC **timestamp**, and the comments. Whether that record is
   committed (vs left as a working-tree edit) is stated explicitly in the playbook.
   This satisfies the repo invariant that durable truth lives in the repo, not in
   ephemeral output, and preserves the machine-checkable guard attestation the old
   `guard_proved` sentinel field carried.
5. The coder acts on the recorded verdict:
   - **accepted** → branch is ready for an **owner-gated** merge (never merged or
     pushed on agent authority).
   - **reopened** → coder applies fix-ups on the same branch and re-runs `/review
     <agent>`.
   - **invalid/contested** → coder writes `.agents/review/<id>.contested.md` (or the
     finding doc's contested section) and routes to the owner. Disagreement is a
     recorded verdict, never a silent veto.

### Per-harness isolation

The **only** harness-specific knowledge is the headless-launch incantation for each
agent (e.g. `codex exec "<prompt>"`, and the `agy`/`grok` equivalents). The toolkit
does **not** ship this as a human-maintained table, and does **not** derive it by
parsing `--help` prose as a committed artifact. Both were rejected: a curated table
requires human upkeep (an explicit owner constraint), and a help-text parser is a
brittle committed regex whose failure mode is a silently-wrong flag mid-review.

Instead the coding agent **derives the incantation live, per harness, per session,
by probing** — the same thing a capable agent already does today when a human says
"review this with grok." The playbook ships the *procedure*, not the answer:

1. Confirm presence (`command -v <agent>`) and surface (`<agent> --help`,
   `<agent> --version`).
2. If the headless entry is ambiguous, drill one level (`<agent> exec --help` /
   `<agent> chat --help`, whichever the top level lists).
3. Smoke-test the candidate headless incantation with a trivial prompt (e.g.
   `<agent> exec "say OK"`) under a **bounded probe**: a timeout (a hung process is
   a failed probe, not a wait); **non-interactive detection** (if it opens a TUI /
   alternate screen / waits on a TTY, the incantation is wrong — try the next
   candidate); and run it from a context the harness accepts (the smoke test
   surfaced that codex refuses a non-trusted dir and needs `--skip-git-repo-check`,
   and agy must run from the real repo cwd — a canned `say OK` in an arbitrary temp
   dir does **not** reveal these, so the smoke test runs in a real git repo and the
   procedure treats a launch refusal as a flag to adjust, not a dead end).
4. Use the verified incantation to run the review. Probing is bounded to
   `--help`/`--version`/the trivial smoke prompt — never arbitrary commands.

This keeps the harness knowledge as a *capability the agent exercises*, not a vendor
name baked into a durable artifact — honoring the existing "capabilities, not
harness-specific tool or agent names" principle, with zero human upkeep. The agent
can tell when its guess was wrong (the smoke test failed or opened a UI) and adapt,
which a static table or regex cannot.

**Optional session cache (convenience, not source of truth):** once verified, the
agent may record an incantation in a gitignored machine-local file (e.g.
`.agents/review/harnesses.local.json`) to skip re-probing next session. Harness
availability and CLI syntax are genuinely machine-specific, so a `*.local.*` file is
the correct home (consistent with the repo's treatment of `settings.local.json` as
untracked machine state). The cache is advisory: the source of truth is
"re-derive by probing," so a stale cache self-corrects on the next smoke test.
Probing is bounded to `--help`/`--version`/a trivial smoke prompt — never more —
consistent with the repo's caution about executing unfamiliar binaries.

The reviewer **prompt** is canonical and harness-neutral: one shipped reviewer
instruction (pointing the agent at the branch + base/head SHAs, the finding doc, the
guard-proof requirement, and the JSON verdict schema) is used for every agent, so
review *semantics* are identical regardless of which harness is named. Only the
launch incantation and the JSON-mode flag differ per agent, and both are
probe-derived.

### What is removed vs the current `reviewloop.md`

Deleted (the async machinery, now unnecessary):

- The `ready/<id>.json` sentinel system and the `mv`-into-place atomic-write step.
- The reviewer wake mechanism / polling watcher (current Step 7).
- The sentinel JSON schemas (current Step 9). The machine-checkable guard
  attestation the `guard_proved` field carried is **not** lost — it survives as the
  `guard_confirmed` key in the structured verdict and in the finding-doc record.
- The `results/<id>.verified.json` / `<id>.reopened.md` file protocol, replaced by
  the finding-doc record + a contested file for disagreements.
- The async-only knobs: multiple coders, multiple reviewers, persistent-reviewer
  single-agent mode.

Kept (the accuracy machinery — untouched in intent):

- The atomic unit: **one finding ↔ one branch ↔ one verdict.**
- The intake/triage gate (evidence, predicted observable failure, justified
  severity → ADMITTED or DECLINED).
- The **guard proof**, now performed and recorded synchronously.
- The contested/declined path and owner adjudication.
- Owner-gating of merge/push/history-rewrite throughout.
- The status index and per-finding doc (the index loses its sentinel-watcher framing
  but stays as the human scoreboard).

## Scope of changes

- **Rewrite** `templates/playbooks/reviewloop.md` to the synchronous `/review
  <agent>` shape (replace, not coexist — two overlapping review playbooks would be
  exactly the drift the repo warns against). Largely supersedes commit `498c056`,
  which has not been pushed to canon.
- **Add** a Claude Code slash-command wrapper `.claude/commands/review.md` pointing
  at the playbook (mirroring the existing operator wrappers).
- **Add** `review <agent>` to the operator vocabulary where the toolkit advertises
  operators, if and where that list is canonical (to confirm during planning — e.g.
  `AGENTS.md` Operator Requests and `tools/discover.py` `OPERATOR_WORDS`). Note:
  `OPERATOR_WORDS` currently drives template-staleness detection; adding a word
  there has reconciliation implications to weigh in the plan, not here.
- This is content `discover.py` copies into target repos (user-facing generated
  guidance), so verification per the repo policy is **required**:
  `python3 -m unittest discover -s tests -v` plus `git diff --check`.

## Open questions for planning

1. ~~Exact headless incantations for `codex`, `agy`, `grok`.~~ **Resolved:** the
   agent derives them live by probing (see Per-harness isolation). The remaining
   detail is the exact wording of the probe-and-verify procedure shipped in the
   playbook, and the schema of the optional local cache.
2. Whether `review` should join `OPERATOR_WORDS` (and thus template-version
   detection) or stay a playbook-only operator. This trades discoverability against
   touching the staleness machinery.
3. Where the canonical reviewer prompt physically lives (inline in the playbook vs a
   shipped prompt file the adapter feeds).
4. ~~The structured-verdict contract and the fallback when a foreign agent ignores
   the format.~~ **Resolved:** JSON output mode + an inner schema parse + a
   fail-closed rule (re-prompt once, then route to owner as contested). See the
   Verdict contract in the dispatch steps.

## Cross-harness review test (2026-06-25)

The probe-and-verify procedure and the review flow were exercised end-to-end against
this very spec. All three target harnesses were present, their headless incantations
were derived live from `--help`, and each returned a usable review:

- **grok** → `grok -p "<prompt>"` (`--single`; `--output-format json` available).
- **agy** → `agy -p "<prompt>"` (`--print`; must run from the real repo cwd).
- **codex** → `codex exec --skip-git-repo-check "<prompt>"` (`exec` = non-interactive;
  refuses a non-trusted dir without the flag).

The smoke test (`say OK`) verified launch but did **not** surface codex's
trusted-dir refusal or agy's cwd requirement — which is exactly why the bounded
probe now runs the smoke test in a real git repo and treats a launch refusal as a
flag to adjust. All three independently returned `VERDICT: concerns` and converged on
the same hazards: weak stdout parsing, guard proof mutating a shared tree, and an
unstable diff base. Those findings drove the revisions above (structured fail-closed
verdict, worktree-isolated guard proof, pinned base SHA, enriched record). The raw
reviews are retained as the durable trail (see Declined revisions for what was not
taken).

## Declined revisions (with rationale)

From the cross-harness review, two suggestions were considered and **declined**:

- **Make `harnesses.local.json` the primary human-provided config (agy).** Declined:
  a human-maintained incantation source is an explicit owner constraint against. The
  file stays an optional self-correcting cache; the source of truth is live probing.
- **Re-introduce / preserve the "Faster" disjoint-scope multi-pending WIP mode
  (grok).** Declined as a deliberate non-goal: the owner chose synchronous,
  one-finding-at-a-time accuracy over parallel throughput. Recorded here so the
  dropped contract is an intentional decision, not an oversight.

One lower-altitude observation is **noted, not actioned here:** grok flagged that
adding `review` to `OPERATOR_WORDS` collides with the same deferred `playbook <name>`
staleness-probe false-positive already tracked in `.agents/state.md`. Open question 2
already owns this; planning must weigh it before touching `OPERATOR_WORDS`.
