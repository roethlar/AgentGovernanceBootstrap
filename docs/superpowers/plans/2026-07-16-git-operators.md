# `/git` Operator Family: Delegated Git Workflows

Status: CLOSED 2026-07-16 — landed: plan `10f232d`, slice 2 `01ece70`
(playbook + wrapper + skill), slice 3 `933da4c` (manifest entries + hook
protection + hook formerly append), slice 4 in the closing commit
(decision recorded with the owner's verbatim wording in
`.agents/decisions.md`; state and README updated). D1 resolved: ship
through the toolkit — owner wording, verbatim: "yes, anything we do here
is part of the product." D2 resolved by push-policy precedent, no owner
ask.

## Problem

The owner does not operate git directly: merging a branch, creating a
branch, or untangling remote divergence requires delegating to an agent
with an ad-hoc typed request ("figure out what is happening with these
branches"). Ad-hoc requests produce inconsistent behavior across sessions
and repos. The owner wants named, repeatable operators:

- `git push (local|remote|all)` — push to the LAN mirror, the public
  forge, or every remote.
- `git reconcile (local|remote|all)` — fetch and resolve discrepancies
  between the local clone and the named remotes.
- `git add-remote <server>` — add a remote for a server; create the
  repository on that server first when it does not exist there.
- `git branch-cleanup` — inventory branches, delete the provably-landed
  ones, and walk the owner through the rest.

Owner-set boundary (operative rule; verbatim wording goes to
`.agents/decisions.md` at adoption): these operators are delegation
shorthand, not automation. Nothing irreversible happens automatically;
the agent explains state in plain English and asks when there are
questions. The owner's git fluency is never assumed.

## Decisions

- **D1 (pending owner wording):** ship the `git` playbook through the
  toolkit so every governed repo gets `/git` on refresh, versus leaving
  it out of the shipped set. Recommendation: ship it — distribution,
  convergence, and edit protection already exist for exactly this
  artifact shape.
- **D2 (resolved by precedent):** `git push …` executes immediately —
  typing the operator is the instruction, and governed repos already
  push automatically under the owner's standing push policy. Every other
  operation explains before acting wherever an action is irreversible or
  ambiguous. No new owner ask.
- Settled owner boundary (2026-07-16, wording above): dialog before
  anything irreversible; plain-English explanations; delegation, not
  automation.

## Design — one playbook, four operations

One harness-neutral playbook, `templates/playbooks/git.md`, installed at
`.agents/playbooks/git.md`, containing all four operations as sections.
One Claude Code command wrapper (`/git <operation> <args>`) and one
shared skill, both thin pointers to the playbook, mirroring the
codereview/openreview wrapper pattern. Invocation on other harnesses is
the existing `playbook git` operator with the operation named in the
request. No `AGENTS.md` template change: the `playbook <name>` operator
already covers invocation, and the Git Safety section already owns the
history-rewrite and merged-branch rules the playbook defers to.

### Delegation contract (common preamble, binding on every operation)

1. The invoker is the repo owner and does not speak git. Every
   explanation, question, and proposal is plain English — name what a
   command *does to their work*, never git jargon ("this branch's
   changes are already in main by another route, so deleting it loses
   nothing", not "ancestry-merged but content-verified").
2. Gather facts read-only first; report the situation before acting.
3. Freely execute read-only and safely reversible steps (fetch, prune of
   stale remote-tracking refs, fast-forward of a local branch to already
   -published work). Report what was done.
4. Anything irreversible, destructive, or outward-facing waits for an
   explicit yes, asked one question at a time: deleting a branch with
   unlanded content, any merge, resolving diverged history, creating a
   repository on a server, force operations (which are additionally
   banned outright below).
5. Never rewrite history: no rebase, amend, squash, or force-push, per
   `AGENTS.md` Git Safety. If a situation seems to need one, explain the
   situation and stop.
6. Never move refs over a dirty working tree; report the uncommitted
   work and stop.
7. Repo-specific rules in `.agents/repo-guidance.md` outrank this
   playbook's generic behavior (e.g. a repo may declare an expected
   mirror lag that reconcile must not report as a discrepancy).
8. Machine-specific facts discovered while operating (forge CLI paths,
   auth state) go to `.agents/machines.md` per the handoff rule.

### Remote classification (`local|remote|all`)

Deterministic, from configured remote URLs, no per-repo config: a remote
whose URL host is a public forge (`github.com`, `gitlab.com`,
`bitbucket.org`) is **remote**; any other host (LAN names, IPs,
self-hosted) is **local**; **all** is every configured remote. If the
requested class matches nothing, or a URL defies classification, say so
plainly and ask — never guess.

### `git push (local|remote|all)`

Default scope when omitted: `all`. Push the current branch (and its
tags) to each remote in scope, creating the upstream branch where
missing; executes immediately (D2). A push any remote rejects
(non-fast-forward, permissions, unreachable host) is reported in plain
English with a proposed next step — never retried with force. After
pushing, mention any other local branches carrying unpushed work.

### `git reconcile (local|remote|all)`

Fetch from every remote in scope, then per remote × branch report one of
four states and act:

- **in sync** — say so.
- **behind** (remote has work the clone lacks, fast-forward applies) —
  fast-forward, report what arrived (contract §3).
- **ahead** (local work unpublished) — offer to push; on yes, push.
- **diverged** — explain in plain English what each side has (commit
  count and subjects), propose a resolution (normally: merge the remote
  work into the local branch with a plain merge commit), and wait for a
  yes. Rebase is never offered.

Repo-guidance-declared expected lags (contract §7) are reported as
"expected, no action" and never treated as discrepancies.

### `git add-remote <server>`

`<server>` is a forge shorthand or URL. Resolve the target: an existing
configured remote's host, an entry in `.agents/machines.md`, or the URL
given. If the repository does not exist on that server, create it —
`gh` for GitHub, `tea` for gitea, otherwise the forge API with existing
credentials — after stating exactly what will be created (name,
visibility defaulting to private) and getting a yes (contract §4).
Then add the remote, verify with a fetch, and report. Never store or
prompt for credentials; if the CLI/API is unauthenticated, explain what
the owner must run and stop.

### `git branch-cleanup`

1. Inventory local branches and stale remote-tracking refs; prune the
   stale refs (contract §3).
2. Classify every local branch by **content**, never ancestry alone
   (`AGENTS.md` Git Safety): a branch whose changes are provably already
   in the main branch is *landed*; anything else is *carrying work*.
3. Present the inventory in plain English: landed branches proposed for
   deletion as one batch (one yes covers the batch); each
   work-carrying branch described by what it changes, with options —
   merge it (plain merge, then re-verify landed, then propose deletion),
   keep it, or delete it (explicitly flagged as discarding work, own
   yes required) — one branch at a time.
4. Report the end state: branches remaining and why.

## Shipped artifacts (manifest + hook)

New `tools/shipped-set.json` artifacts, all class `replace`, all
`formerly: []`:

| source | target |
| --- | --- |
| `templates/playbooks/git.md` | `.agents/playbooks/git.md` |
| `templates/commands/claude/git.md` | `.claude/commands/git.md` |
| `templates/skills/shared/git/SKILL.md` | `.agents/skills/git/SKILL.md` |

All three new files carry the standard provenance marker (installed-by-
refresh, do-not-edit) — `tests/test_templates.py` marker tests enforce
this automatically. `templates/hooks/claude/protect-governance.py`
gains the three targets in `PROTECTED` (the hook↔manifest sync test
enforces this); per the manifest MAINTENANCE RULE the hook's outgoing
normalized hash is appended to its `formerly` in the same commit.
`templates/hooks/claude/settings.json` is untouched. This repo's own
installed copies lag until the owner's next self-refresh (owner-only) —
expected, not drift.

## Tests and verification

No new test files: the existing structural suite already gates every
moving part (manifest schema/known classes, provenance markers on
playbooks/wrappers/skills, hook `PROTECTED` ↔ manifest sync, refresh
behavior for new `replace` artifacts). Run the full suite
(`.agents/repo-guidance.md` Verification) after the shipping slice; run
the plan lint for changes to this document. The playbook body is prose
guidance — behavioral verification is the owner exercising the operators
in a governed repo, which is explicitly a post-landing field step, not a
slice gate.

## Slices

1. This plan document (lint-clean, committed).
2. Playbook + wrapper + skill content (`templates/…`), markers included.
3. Manifest entries + hook `PROTECTED` + hook `formerly` append; full
   suite green.
4. Decision D1 recorded in `.agents/decisions.md` with the owner's
   wording; `.agents/state.md` updated; this plan closed with the
   commit map.

## Non-goals

- No automation, scheduling, or auto-selection: every operation is
  owner-invoked, per invocation.
- No history rewriting under any operation, ever.
- No credential capture or storage; existing CLI/API auth only.
- No new deterministic tool under `tools/` — the operations are
  judgment-plus-dialog workflows, which is what playbooks are for; the
  only deterministic rule (remote classification) is three lines of
  playbook text.
- Additional operations ("etc.") are future artifacts of the same
  shape, added by their own plan or a trivial template change.
