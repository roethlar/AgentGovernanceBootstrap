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
   that branch and the finding doc. Both are read by the reviewer **from the shared
   workspace** — the diff is *not* marshalled across the process boundary; the
   reviewer runs its own `git diff <main>..<branch>`, reads
   `.agents/review/findings/<id>.md`, and independently performs the guard proof
   (revert → confirm FAIL → restore → confirm PASS). The shared filesystem is the
   bus; the handoff passes only a pointer + the reviewer instruction, never content.
3. The reviewer emits its verdict on **stdout**. The coder reads it directly. The
   verdict is one of: **accepted**, **reopened** (fix-ups needed), or **invalid/
   contested** (the finding does not hold). The reviewer is asked to lead its output
   with a structured line (`VERDICT: accepted|reopened|invalid`) followed by
   `file:line` comments, so classification is unambiguous.
4. **Before acting, the coder records the verdict into the repo** — the durable trail
   that replaces the deleted sentinel/results files. The reviewer's verdict and key
   comments go into the finding doc's `## Reviewer comments`, the finding **Status**
   flips, and whether the reviewer confirmed the guard proof is noted. This satisfies
   the repo invariant that durable truth lives in the repo, not in ephemeral output.
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
agent (e.g. `codex exec "<prompt>"`, and the `agy`/`grok` equivalents). This is
quarantined in one place — a small labelled table in the playbook (and/or a thin
adapter the playbook points to) — so adding a new reviewer harness is a one-line
change and the rest of the playbook names capabilities, not vendors. This honors the
existing "capabilities, not harness-specific tool or agent names" principle.

The reviewer **prompt** is canonical and harness-neutral: one shipped reviewer
instruction (pointing the agent at the branch, the finding doc, and the guard-proof
+ verdict requirements) is used for every agent, so review *semantics* are identical
regardless of which harness is named. Only the launch incantation differs per agent.

### What is removed vs the current `reviewloop.md`

Deleted (the async machinery, now unnecessary):

- The `ready/<id>.json` sentinel system and the `mv`-into-place atomic-write step.
- The reviewer wake mechanism / polling watcher (current Step 7).
- The sentinel JSON schemas (current Step 9), including `guard`/`guard_proved`
  fields — the guard-proof *record* survives as prose in the finding doc.
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

1. Exact headless incantations for `codex`, `agy`, `grok` (and the Claude-subagent
   case) — verified against each CLI, not assumed.
2. Whether `review` should join `OPERATOR_WORDS` (and thus template-version
   detection) or stay a playbook-only operator. This trades discoverability against
   touching the staleness machinery.
3. Where the canonical reviewer prompt physically lives (inline in the playbook vs a
   shipped prompt file the adapter feeds).
4. The minimum-viable structured-verdict contract the reviewer must emit, and the
   coder's fallback when a foreign agent ignores the format.
