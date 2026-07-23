# Agent Decisions

Record durable repo decisions here. Do not use this as a chat log. Each entry should make
sense without conversation history and should name superseded guidance when relevant.

Keep this file to what is currently in force or still open. When a decision is
closed - superseded, or settled and retained only as the rationale for a rule that
now lives in its canonical home elsewhere - move it verbatim, in that same change,
to `docs/history/decisions-archive.md`; never summarize or drop wording, the exact
text is the record. That archive is the provenance log; this file is what is in
force or still open.

Archive: closed (Adopted / Superseded) decisions live in
[`docs/history/decisions-archive.md`](../docs/history/decisions-archive.md).

## Decision lifecycle

A decision moves through these states:

- **Open** - a finding has been assessed but not yet acted on. It lives in the
  `## Open Decisions` queue below, with the verified evidence, the options, and a
  standing recommendation. The process is unchanged until it is adopted; an agent
  records it rather than implementing on the spot.
- **Active** - a decision that is in force now.
- **Adopted YYYY-MM-DD** - an Open finding that has been acted on: its rule now
  lives in its canonical home (a procedure, template, or invariant). Note where the
  rule landed; the finding is retained in place as the rationale that led to it,
  until it is archived.
- **Superseded** - replaced by a later decision; name the replacement.

When an entry becomes purely historical rationale - Adopted or Superseded, with the
live rule now owned elsewhere - archive it per the rule above: move it verbatim to
`docs/history/decisions-archive.md`, do not leave a stub.

## Decisions

### 2026-07-22 — Owner communication is a per-repo tunable level (1–5), seeded like the push policy; supersedes the named-profile design

Status: Active

Decision: owner-facing communication register is a per-repo tunable on a
1–5 scale, configured exactly the way the push policy is — a small
repo-owned policy file, `.agents/comms-policy.md`, seeded at bootstrap
from `templates/comms-policy.template.md` with a machine-readable marker
line (`<!-- comms-level: N -->`) as its first line. The level definitions
live in the policy file itself so it stands alone. The five levels: 1 =
explain like I'm five; 2 = plain English, one decision at a time; 3 =
normal user; 4 = devops shorthand; 5 = devops/jargon, terse.
Template/bootstrap default is level 3 (normal user); the approval summary
asks the owner to choose and never pre-fills. The level tunes register
only — it never changes any safety, approval, or verification rule, and
the Owner Gates structural contract is level-independent. This repo's own
`.agents/comms-policy.md` is set to level 2.

Owner wording (2026-07-22), verbatim: "this needs to be tunable like the
push policy. 1-5, 1 being eli5, 2 plain english one at a time, 3 normal
user, 4-5 devops/jargon".

Supersedes: the 2026-07-12 named-profile owner-communication design
(single `Profile:` line in `.agents/repo-guidance.md`, five named profiles
`default`/`devops`/`student`/`expert`/`brief`, menu home
`templates/approval-summary.template.md`), archived in
`docs/history/decisions-archive.md` under the 2026-07-10 "Per-repo tuning
for verbosity and technical level" entry. The named-profile surfaces are
replaced: the `Owner Communication` section is removed from
`templates/repo-guidance.template.md`, the approval-summary question is
reworded to the 1–5 levels, and bootstrap Step 4 seeds
`.agents/comms-policy.md` instead of drafting a repo-guidance profile line.

Landed: `templates/comms-policy.template.md` (default level 3) and this
repo's `.agents/comms-policy.md` (level 2); the plan-operator styling
sentence in `templates/AGENTS.template.md` becomes a pointer to the level
(see the 2026-07-10 plan-contract amendment). Plan:
`docs/superpowers/plans/2026-07-22-holistic-toolkit-improvements.md`
(Site 6).

### 2026-07-22 — Issue-queue and feedback items are worked one at a time behind an explicit owner go (R1)

Status: Active

Decision: GitHub issues and other feedback filed against this repo are
addressed by putting each item to the owner individually as an Owner Gates
ask with decisive options; nothing is implemented without a clear, explicit
per-item go. A general instruction such as "fix them" is not standing batch
authority. This generalizes to any queue of findings, sites, or fixes: one
owner decision at a time, one item per commit.

Receipt: the 2026-07-22 batch-implementation incident. Ten unapproved
commits editing fleet templates self-classified as docs, were pushed, and
were owner-ordered reverted; the remote was reset to `881e63b` and the
reverted work preserved only in the local tag
`backup-2026-07-22-governance-edits`.

Landed: the issue-queue process lives in `.agents/repo-guidance.md`
(Mission Detail); this entry is the owner ruling (R1) behind it.

### 2026-07-22 — State and governance files are kept current by the working agent as work lands, never gated on a human (R3)

Status: Active

Decision: `.agents/state.md` and the governance files exist for agents and
for humans doing forensics. The working agent keeps them current as part of
the work, as it lands; that upkeep is never gated on a human and never waits
for an owner to invoke an operator. `handoff` and `drift` retain their
distinct deliberate-pass roles — a fast save-my-place snapshot, and the
state-hygiene sweep — but ordinary currency of the record does not depend on
either being invoked.

Receipt: GitHub issue #7. A falsified `.agents/state.md` entry could only be
corrected by asking the owner, because the only state.md write paths named in
the guidance lived inside owner-invoked operators — routine bookkeeping was
gated on a human it should never have needed.

Landed: `templates/AGENTS.template.md` current-state entry-point invariant
reworded so state.md is kept current by the working agent as work lands,
never owner-gated (`handoff`/`drift` keep their deliberate-pass roles); this
entry is the owner ruling (R3) behind it.

### 2026-07-22 — An owner's completion report inside an approved, scoped workflow is the go for that workflow's next defined step (issue #8)

Status: Active

Decision: when the owner reports a step complete inside an approved,
already-scoped workflow ("it's done", "that ran"), the report is the go for
the next step that workflow already defines — no separate ritual "go" is
demanded before continuing. The stops still bind: new scope, a changed risk,
and separately gated actions each still require their own explicit go, and a
handed-over report, plan, or spec remains evidence to assess rather than a
decision to implement. A completion report advances only the workflow's own
next defined step, never new or separately gated work.

Receipt: GitHub issue #8. An owner's mid-workflow completion report was
treated as merely informational and a ritual "go" was demanded before the
already-scoped next step. The same 2026-07-22 incident showed the opposite
failure — a continuation stretched into standing batch authority — so the
rule threads both: the report advances the defined next step, and nothing
beyond it.

Reopens: qualifies the 2026-06-10 "Answer-with-words rule hardened;
artifact-is-evidence-not-decision" decision, for completion reports only.
That decision's "reply in plain English and stop / ask for the go, and stop"
still governs questions, musings, and any step not already defined by an
approved workflow; a dated amendment recording this qualification is appended
to that entry.

Landed: `templates/AGENTS.template.md` Prime Invariants "Words first" bullet
reworded to add the completion-report clause with the three stops (net length
roughly flat); a dated amendment on the 2026-06-10 answer-with-words entry
records the qualification.

### 2026-07-19 — Model slugs get one committed home: fleet-global `.agents/model-map.json`; reviewer dispatch resolves nicknames through the map

Status: Active

Decision: concrete model slugs have exactly one sanctioned committed
home — the fleet-global `.agents/model-map.json`, mapping owner-granted
nicknames to per-harness model ids (seeded from the owner's confirmed
pins: `sol` → codex `gpt-5.6-sol`, `terra` → codex `gpt-5.6-terra`).
Reviewer dispatch resolves nicknames through the map at launch;
nicknames never select tier — `<effort>` selects effort within whatever
tier the trigger machinery dispatches (F5). Playbook model-freedom
(curated-denylist lint) governs templates; the map is the explicit lint
boundary (F11). `.claude/commands/review.md` returns to the shipped set
as a pure alias command (`templates/commands/claude/review.md`, F6).
Plan: `docs/superpowers/plans/2026-07-19-model-map-reviewer-dispatch.md`.

Supersession amendments (the plan's F5 matrix, recorded as dated
amendments):

- 2026-07-17 D1/D2, "concrete pins live in machine-local, gitignored
  `.agents/review/harnesses.local.json`" — **superseded for model
  slugs**: slugs move to the fleet-global map. Harness flags,
  transports, and capability grades remain machine-local, unchanged.
- 2026-07-17 D1, default reviewer tiers and trigger-driven escalation —
  **untouched**: `<effort>` selects effort within whatever tier the
  trigger machinery dispatches; nicknames never select tier (F5).
- 2026-07-17, "committed text is model-free" (curated-denylist lint) —
  **amended**: model-freedom governs templates; the map is the single
  sanctioned committed home for slugs; the lint boundary is explicit
  (F11).
- 2026-07-16, `review` operator split with `.claude/commands/review.md`
  retired (archived entry, `docs/history/decisions-archive.md`) —
  **amended**: the path returns as a pure alias command (F6). The
  archived text stays verbatim; this entry is the amendment record.
- 2026-07-18, reviewer dispatch is self-permissioning — **untouched**:
  grants remain launch-scoped; the map feeds only the model id.

### 2026-07-18 — Reviewer dispatch is self-permissioning; the owner never hand-grants tools

Status: Active

Decision: a review dispatch grants the reviewer its tool set **at launch**, never
by an owner editing `settings.json` or widening persistent config. The set is
bounded and strictly narrower than the coder's — read-only inspection, a
disposable `git worktree`, and the verification command; no write. On Claude Code
the grant is `--allowedTools Read Grep Glob "Bash(git:*)" "Bash(<verify-cmd>)"`;
every harness has an equivalent launch-scoped grant, carried in the harness cache
entry's `flags`. Transport is not a special case: on `cli` the orchestrator passes
the grant per invocation, on `mcp` the same flags live in the server's
registration command — both self-permission, so the `mcp`-preferred default is
unaffected. Canonical home: the "Self-permissioning launch" rule in
`templates/playbooks/codereview.md`, pointed to from
`templates/playbooks/openreview.md`.

Provenance: field incident 2026-07-18 (ai-rpg-engine) — codex, dispatching Claude
Code as an MCP reviewer, stalled because the reviewer lacked its tools and the
fallback assumption was that the owner would grant them by hand in `settings.json`.
Owner ruling (2026-07-18), verbatim: "it should have just invoked with
--allowedTools … I need less work not more." A reviewer's tool set is narrow and
safe, so a hand-grant is pure friction; the launch-scoped grant removes it. The
owner further confirmed MCP-as-server carries the grant in its registration args
("yes it can"), so no transport needs a `settings.json` fallback.

> Amended 2026-07-22 (Site 4 — Evidence): the closing provenance clause above — that MCP-as-server carries the grant in its registration args ("yes it can"), so no transport needs a `settings.json` fallback — is downgraded to a **falsified assumption**. It was recorded from owner say-so, not a probe; GitHub issue #6 and Claude Code 2.1.214 show the MCP registration args do not carry the launch grant on that harness, so the `cli`↔`mcp` self-permissioning equivalence does not hold there. The launch-scoped-grant ruling itself stands; only this provenance/equivalence clause is retracted. The matching equivalence sentence in `templates/playbooks/codereview.md` (Self-permissioning launch) is deleted alongside this amendment.

### 2026-07-17 — Review economy: tiered reviewer routing adopted (D1–D3); D4 dissolved

Status: Active, as amended 2026-07-19 — model slugs superseded into the
fleet-global `.agents/model-map.json` (see the 2026-07-19 entry);
harness flags, transports, and capability grades remain machine-local

Decision: `codereview` runs a two-tier reviewer scheme — standard@high
by default, frontier@xhigh on mechanical escalation (triggers T1–T5) or
owner force; `openreview` pins frontier@max. Canonical mechanics live in
`templates/playbooks/codereview.md` (tier semantics, escalation
triggers, repair-delta redispatch, contested-record adjudicator offer)
and `templates/playbooks/openreview.md` (frontier pin); committed text
is model-free (curated-denylist lint), and concrete pins live in the
machine-local, gitignored `.agents/review/harnesses.local.json`. Plan:
`docs/superpowers/plans/2026-07-17-review-economy.md` (CLOSED with
commit map). The plan's closed owner-gate text, recorded verbatim:

D1 — default tiers per playbook. Owner directives (2026-07-17):
two-tier structure and per-playbook defaults stand (`codereview` →
standard, `openreview` → frontier); opus 4.8 joins standard (on par
with sonnet 5); Luna is dropped — the transport role that briefly
sheltered it is deleted; effort belongs in any capability comparison
(fable-low judged weaker and costlier than sonnet-max — tentative);
keep the scheme simple. Effort pins ruled and confirmed (owner,
2026-07-17, superseding the same-day draft mapping): effort binds to
tier, never to arrival path — `codereview` standard runs high;
`codereview` frontier runs xhigh whether reached by escalation or owner
force (an owner-forced frontier dispatch is the owner saying "this is
hard", which is the xhigh case); `openreview` pins max. The monotonic
ladder high < xhigh < max tracks review depth. openreview@max has no
escalation headroom by design: a contested openreview round resolves by
owner adjudication, never a stronger dispatch — above max sits the
owner. D4 is dissolved (see below). Frontier pins ruled (owner,
2026-07-17): Claude → claude-sonnet-5; OpenAI → gpt-5.6-sol. Grok and
Gemini have no competitive frontier model; their frontier slots carry
fallback-grade pins — grok-4.5 and gemini-3.1-pro — so the two-tier
structure stays total on every harness, but a fallback-grade frontier
verdict is not frontier-grade adjudication and the tiers entry says so
via the frontier `grade` field; frontier routing on fallback-grade
harnesses halts to the owner (ruled 2026-07-17, see the plan's
Escalation triggers). Fable is out of frontier contention (already
judged weaker and costlier than sonnet-max). Sonnet-5 serving as Claude
frontier while opus 4.8 ≈ sonnet 5 sits in standard is legitimate under
pair semantics: tier identity includes effort, so frontier@xhigh and
standard@high differentiate even where model strength is on par.
Standard pins ruled (owner, 2026-07-17), closing the routing table:
Claude standard = sonnet-5 — single-model harness until opus-5
releases; that release is a re-confirmation event under the
once-per-harness-version rule, no automation. OpenAI standard =
gpt-5.6-terra. Grok = single-model grok-4.5 in both slots,
effort-differentiated (standard@high / frontier@xhigh). Gemini (agy) =
gemini-3.5-flash @ high standard (flash ships low / medium / high only)
and gemini-3.1-pro @ high frontier — the owner's exact levels: no xhigh
pair exists on this harness, so Gemini's fallback frontier deviates
from frontier→xhigh by harness limitation, and the owner-confirmed pair
is authoritative where the ladder's level is not exposed. D1 is closed;
no routing decisions remain open.

D2 — reopen auto-escalation. Adopted: any reopened finding escalates
one tier on redispatch — the cheapest defense against a standard-tier
reviewer mis-judging its own reopened work; repair-delta scoping keeps
the escalated call small. Shipped as trigger T5 with the frontier
ceiling rule.

D3 — archive the commissioning review. Adopted: the GPT-5.6 review that
commissioned this work, previously machine-local outside the repo, is
archived verbatim (SHA-verified copy) at
`docs/history/2026-07-17-review-economy-commissioning-review_gpt-5.6.md`.

D4 — xhigh selector. Dissolved (owner, 2026-07-17): xhigh binds to the
frontier tier itself (see D1), so no selector — phrase, path list, or
heuristic — exists or is needed. Escalation *is* the selector:
complexity earns xhigh by defeating the standard reviewer, not by
prediction. Recorded so it is not reopened.

### 2026-07-16 — `/git` operator family ships in the toolkit: delegated plain-English git workflows, dialog before anything irreversible

Status: Active

Decision: the toolkit ships a `git` playbook (installed at
`.agents/playbooks/git.md`, with a `/git` Claude Code wrapper and shared
skill) carrying four owner-invoked operations — `push (local|remote|all)`,
`reconcile (local|remote|all)`, `add-remote <server>`, and
`branch-cleanup`. They are delegation shorthand for an owner who does not
operate git directly, never automation: the agent gathers facts read-only,
explains state in plain English with no git jargon, acts freely only on
reversible steps, and asks one question at a time before anything
irreversible, destructive, or outward-facing. History rewriting is never
offered (`AGENTS.md` Git Safety). `push` executes immediately on
invocation, consistent with the push-policy precedent that typing the
instruction authorizes the push. Remote classification is deterministic by
URL host (public forge hosts are `remote`, every other host is `local`).
Canonical home of the workflow: `templates/playbooks/git.md`; plan:
`docs/superpowers/plans/2026-07-16-git-operators.md`.

Owner wording (2026-07-16), verbatim: "nothing destructive happens
automatically. it's just shorthand for me. I don't speak git well. I can't
merge a branch. I can't even create a branch without googling it. these
would save me typing 'can you figure out wtf is happening with all these
branches?' I'd then expect a dialog if there are questions. nothing
automatic that's irreversible."

Scope ruling (owner, 2026-07-16), on whether the family ships fleet-wide
through the toolkit or stays a personal setup, verbatim: "yes, anything we
do here is part of the product." Recorded as a standing scope principle
for this repo: capabilities built here ship through the toolkit — there is
no personal-tooling side channel.

### 2026-07-12 — Draft-all harness artifacts stands; "smallest guidance set" means no token bloat, not fewer support files

Status: Active

Decision: bootstrap keeps drafting the operator wrappers, shims, and other
harness support files for every harness the toolkit ships templates for, in
every repo — no evidence-of-use gating, no "optional / not-evidenced"
labeling in the approval summary. The smallest-guidance-set invariant in
`templates/AGENTS.template.md` governs guidance content — do not add token
cost that every session pays — not the presence of harness support files.
Owner ruling (2026-07-12), verbatim: "no, all harnesses every time. minimal
means don't add token bloat anywhere. it doesn't mean drop important files
because you think I won't need them."

Closes: the 2026-06-23 Open finding on "all routes" harness-artifact
drafting vs the smallest-guidance-set invariant (archived verbatim in
`docs/history/decisions-archive.md`) — resolved as no contradiction: the
two rules govern different things. Consistent with the 2026-06-18
standing-guarantee decision and the 2026-07-03 playbooks decision
(unconditional, deterministic installation).

### 2026-07-11 — Push status is never recorded in state files; git is the only source

Status: Active

Decision: state files never record push status. Git owns that fact; sessions
check it live (the Session Startup clone-freshness check) and mention
unpushed work only in the moment it matters — about to push, or handing off
unpushed commits. `drift` deletes any recorded push-state line on sight
instead of refreshing it. Owner-approved wording (2026-07-11): "Stop
recording push status in state files, fleet-wide. Git already knows, and
every session checks it live at startup. Agents mention unpushed work only
when it matters right now — about to push, or handing off unpushed commits —
and drift deletes any recorded push line instead of refreshing it."

Basis: a recorded push line is a second copy of a fact git owns. It goes
stale the moment the owner pushes manually outside a session, and every
stale copy became an owner-facing nag — either a prompt to refresh the line
or a false report of unpushed commits. This is the one-canonical-location
invariant applied with git as the owning system.

Changes: `templates/AGENTS.template.md` (drift operator line) and
`templates/state.template.md` (write-time rules) drop push status from the
volatile-facts examples and state the never-record rule. Reaches governed
repos at the owner's next fleet refresh.

Declined alongside (owner, 2026-07-11): a fifth `manual` push-policy option
("agents never push, never ask; the owner handles propagation"). The
2026-06-27 four-option policy set stands unchanged.

### 2026-07-10 — Release posture: perfect privately first, release widely later

Status: Active

Decision: the toolkit is being vetted and perfected in the owner's own
workflows first; wide release is the eventual goal, not the current state.
Owner wording (2026-07-10), verbatim: "Once this is vetted and perfected in
my workflows we can release it widely." Consequence: release-engineering
work (versioned releases, changelogs, license, CI matrices, signed tags —
external-review finding M6) is DEFERRED until the wide-release decision,
not declined; nothing in the product assumes external users until then.
This refines the personal-toolkit framing behind the 2026-07-10
mirror-trust ruling (recorded in
`docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md`).

### 2026-07-10 — Agents never update this repo's own governance while working on the toolkit

Status: Active

Decision: An agent in this repo works on the toolkit product — templates,
tools, procedures, tests, docs. It never updates this repo's own installed
governance: not by hand-editing `AGENTS.md`, shims, wrappers, skills, hooks,
or playbooks, and not by running any toolkit tool (including
`tools/refresh.py` and the `update-governance` operator) against this repo.
Self-refresh is an owner-only action. Installed copies lagging the templates
after a template change is the expected steady state, not drift to fix; at
most, note the lag. Repo-owned records (`.agents/state.md`,
`.agents/decisions.md`, `.agents/repo-guidance.md`, push policy, plans)
remain normal working surfaces under the standard operators — this rule
covers the installed shipped-set copies and the tools that write them.

Owner wording (2026-07-10): "you cannot update this repo's governance while
working on the toolkit. that is a foot-gun. you do not update this repo's
governance, either directly or by running any tools in the toolkit on this
repo."

Supersedes the earned-practice wording "run the refresh" formerly in
`.agents/repo-guidance.md` (rewritten with this decision).

Reason: The dogfood loop let toolkit work rewrite the governance of the very
session doing the work: a template edit followed by an agent-run self-refresh
changed this repo's `AGENTS.md` mid-session (incident 2026-07-10, refresh
commit `65a8543`, run on the strength of the old earned-practice line rather
than a specific owner go). Separating the roles — agents change the product,
the owner refreshes this repo deliberately — removes the foot-gun.

### 2026-07-10 — Plan contract: agent-facing plan documents; owner decisions in chat

Status: Active

> Amended 2026-07-22 (Site 6 — comms level): the fixed styling of the chat ask — "roughly 25-50 plain-English words … no jargon" — is superseded by the per-repo communication level in `.agents/comms-policy.md` (see the 2026-07-22 comms-level entry above). The plan-operator bullet now points at that level for register; the contract's structure is unchanged — plans stay agent-facing, and owner decisions still come in chat one decision at a time, never a batch, each stating the problem, the change, and the cost or risk. Level 2 reproduces the original "one decision at a time, plain words" register, so this repo's asks are unchanged.

Decision: A plan document is written for agents, never for the owner. It must
be self-contained and implementable by a completely cold, less-capable agent
than the one that wrote it: technical, free of human-facing summary prose,
free of chat or session references that need the originating conversation to
make sense. The owner does not read plan documents. Every decision a plan
needs is presented in chat as roughly 25-50 plain-English words — the
problem, the change, the cost or risk — one decision at a time, never a
batch, no jargon. The owner's approved wording is copied verbatim into the
durable record (this log and/or the plan's status line); there is no
separate executive-summary document type. Canonical home of the rule: the
`plan` operator bullet in `templates/AGENTS.template.md` (installed as
`AGENTS.md`); the plan skill and wrappers point to it.

Approved owner wording (2026-07-10): "I'll write this contract into the
toolkit's plan rule — the shared rulebook template and its plan skill — and
record it in the decision log. It changes how plans are written and how I
ask you for decisions, everywhere the toolkit is installed." Owner
constraints recorded verbatim the same day: plans should be "implementable
by a completely cold, far less capable agent than the one that wrote it";
"no superfluous human-focused token bloat, no chat context leakage that
would invite future drift"; "the decisions come in the chat, get recorded to
decisions/state/wherever appropriate."

Reason: Owner direction (2026-07-10). Plan documents read as
engineer-facing; the owner is not a software engineer and does not read
them, so approval stalled whenever it depended on reading a plan file.
Splitting the roles — a technical plan for agents, short plain-English asks
in chat for the owner — fills both roles the owner named. The four
2026-07-10 draft plans in `docs/superpowers/plans/` remain parked; their
decisions are brought to the owner per this contract when unparked.

### 2026-07-09 — Codex 0.144 new surface evaluated; reviewloop keeps `codex exec`+stdin dispatch

Status: Active (evaluation only; no product change).

Decision: the Codex CLI's newer surface (`codex-cli 0.144.0` on this machine)
was evaluated against the reviewer-dispatch contract in
`.agents/playbooks/reviewloop.md`, and the `codex exec` + prompt-piped-via-stdin
dispatch is **retained unchanged**. Three new subcommands were assessed —
`codex review` (first-party non-interactive review), `codex plugin` (plugin
management), and `codex mcp-server` (run Codex as an MCP stdio server):

- **`codex mcp-server` was tested** (MCP `initialize` + `tools/list` over stdio, <!-- lint: allow (MCP protocol method, not a repo path) -->
  bounded, inspection-only — no agent turn invoked). It speaks protocol
  `2025-06-18`, identifies as `codex-mcp-server` `0.144.0`, and exposes exactly
  two tools: `codex` (required `prompt`; structured `sandbox` =
  `read-only`|`workspace-write`|`danger-full-access`, `approval-policy`,
  `model`, `cwd`; output `{threadId, content}`) and `codex-reply` (continue via
  `threadId`). It is a viable *alternative* reviewer transport — structured
  `sandbox: read-only` enforcement at the harness boundary, and no stdin-vs-argv
  hang — but it is **not adopted**: (1) it returns free-form `content`, not the
  fail-closed JSON *verdict envelope* our contract parses, so the verdict-parsing
  responsibility is unchanged; and (2) its `threadId`/`codex-reply` model is
  stateful, whereas the loop's atomic unit is one-shot per finding. Adopting it
  would be a design change, not a swap.
- **`codex review`** is noted but not adopted: it is not a drop-in for our
  custom verdict schema, guard-proof-in-a-worktree, and pinned base/head SHA
  contract.

No change was needed regardless: `reviewloop.md` derives the reviewer
incantation **live, per session, by probing** and names harnesses only as
examples, so CLI drift self-corrects — there is no hardcoded incantation to
update. The one durable, hard-won fact (`docs/harness-capabilities.md`,
`.agents/repo-guidance.md`) — pipe the prompt via **stdin**, not argv, or it
hangs — still holds under `codex exec`.

Reason: owner asked whether the new Codex options affect this repo's reviewer
dispatch. Recorded here so the evaluation and its evidence are not
re-litigated, without touching the probe-driven design that already handles
CLI drift.

Supersedes: nothing.

### 2026-07-09 — Dead-path lint is git-aware: vouched deletions print a NOTE; no allowlists anywhere

Status: Active (implemented same day, commit `e9e04b4`; plan with outcome
record: `docs/superpowers/plans/2026-07-09-git-aware-dead-path-lint.md`).

Decision: when the governance lint in `tools/refresh.py` finds a backticked
repo-relative path that does not exist on disk, it consults git for a
deletion commit (`git log --diff-filter=D --format=%h -1`, one cached lookup
per unique missing path, zero subprocesses when nothing is missing). A
deletion commit turns the finding into an informational note — `NOTE <file>:
historical: <tok> — deleted in <hash>` — so the lint output itself records
exactly which commit retired the file. No evidence (never tracked, typo,
shallow clone, git failure) keeps the loud missing-path warning: degradation
is always toward loud, never toward silent-wrong. No allowlist exists
anywhere — `LINT_EXEMPT_PATHS` was not extended, and per-repo/global lists
were owner-rejected (2026-07-09). Never-tracked mentions in closed decision
entries stay loud permanently: the owner delegated that call the same day
and the closed-entry special case was dropped as "added complexity for an
extremely low-value operation."

Earned by: the 2026-07-08 zero-based consolidation retired substrate that
append-only decision records still name, so every refresh printed the same
dozen missing-path warnings forever, and a *real* dead reference (a typo,
genuine drift) would hide in the permanent noise. The owner asked for the
note, not silence, and not a list.

Relationship: preserves the append-only/never-rewrite record discipline
(the note lives in the lint output, not in edited history); leaves
`LINT_EXEMPT_PATHS` exactly its template-intentionality role from the
2026-07-08 consolidation; lint remains advisory and read-only.

### 2026-07-08 — Zero-based consolidation: every product piece justifies its existence or leaves

Status: Active (implemented same day; plan with eight-round codex review
trail: `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`;
owner approval 2026-07-08).

The owner commissioned a zero-based review — every piece justifies itself on
the incident ledger and a five-repo field audit (Blit_v2, vela,
Powershell-Token-Killer, ai-rpg-engine, ExchangeAdminWeb; evidence anchors in
the plan) or is removed/replaced. The field audits established that the core
loop works (handoffs demonstrably resumed across sessions and machines,
decisions and pauses honored, reviewloop caught real pre-ship bugs) and that
the recurring failures cluster where no operator or write rule existed.

What changed, and what each change supersedes or amends:

- **Steady-state refresh is `tools/refresh.py`** — pull-based, per-repo, no
  registry: reconcile-to-shipped-set (`tools/shipped-set.json`) with
  newline-normalized matching, `replace-whole` for `AGENTS.md` gated on a
  known-template match, `replace-if-unmodified` for shims/wrappers/playbooks/
  hook settings (missing ⇒ install; matches a formerly-shipped version ⇒
  update; else flag, never overwrite), a `retired` list so toolkit-side
  removal actually propagates (empty formerly-hashes = always flag, never
  machine-delete — protects generated files), gitignore-aware committability
  with the blanket adapter-dir repair, dirty-tree refusal scoped to its own
  targets, `--stage-only` for the bootstrap single-commit contract, and the
  toolkit sha in the commit message as provenance. Rationale on record: sync-
  to-exact-set is the documented agent failure mode (the 2026-07-01 dogfood
  "content already current" miss; wrappers narrowed to fit stale files;
  deletions resurrecting). This supersedes the mechanical half of the
  agent-run refresh flow, the 2026-06-22 templateVersion-stamp decision (the
  stamp is removed; byte-compare + commit-message provenance replace it), and
  strengthens the 2026-06-18 never-overwrite rule (`replace-if-unmodified`:
  byte-match against formerly-shipped versions proves non-modification, so
  provably-unmodified stale artifacts now update instead of rotting). The
  2026-07-03 playbooks decision is **preserved in full** (unconditional
  install; target-repo deletion still reinstalls; opt-out = remove the
  template from the toolkit — which now actually propagates).
- **Discovery is a live checklist, not a script** — `tools/discover.py` and
  its manifest/schema/golden machinery deleted (three of the seven ledger
  bugs were its own defects; a frontier agent re-derives its outputs).
  Salvaged knowledge lives in `procedures/bootstrap.md`: the Windows
  Store-stub probe order, ignore-aware governance detection, the
  CI-executability rule. Supersedes the script half of the 2026-06-09/10
  kickoff decision; the single-session kickoff, Step 0 sync, and evidence
  rule stand. The `.bootstrap-tmp` handoff pack dies with its generator; the
  self-ignored `drafts/` custody convention survives in the procedure. <!-- lint: allow (procedure convention, not a repo path) -->
- **The JSON layer is retired** — `repo-map.json` / `artifact-manifest.json`
  templates deleted; both on the retired list (flag-only). Field evidence:
  frozen and wrong in every audited repo while the prose files stayed
  accurate; custody is proven live by git at the approval gate. The
  verification command's single canonical home is
  `.agents/repo-guidance.md` (Verification). Amends the 2026-06-09
  standard-layout decision (layout no longer includes the JSON files).
- **Hooks narrowed to the Claude compaction re-ground behind a per-harness
  verify-once gate** — the sole shipped hook; the AGENTS.md pre-edit
  tripwire is retired everywhere (advisory; per-edit process spawn; silently
  inert on stock Windows for weeks with no degradation — the strongest
  not-load-bearing evidence on record; the write boundary is now refresh's
  byte-verify-and-repair), as are the never-verified grok/agy configs and
  the codex config (session_start registered but never observed firing —
  2026-07-08 live check negative). Ledger + structural rationale (a
  compaction failure can only be mitigated from outside the context):
  `docs/harness-capabilities.md`, the durable per-harness capability record.
  Amends the 2026-06-21 per-harness re-ground decision (per-harness retained,
  now evidence-gated); supersedes L2 of the 2026-06-25 boundary decision (L1
  prose stays, L3 is refresh repair); moots the 2026-07-02 hook-interpreter
  decision (the survivor is a plain echo). Codex/gemini/grok adapters and
  non-Claude wrappers re-enter only on a recorded positive live check.
- **Feedback is GitHub issues on this repo** (public; hard no-PII/secrets
  redaction rule in the issue templates; agents file only on an explicit
  owner go; offline fallback = in-repo note). Supersedes the transport half
  of the 2026-06-09 harvest decision and the 2026-06-22 dropbox/bug-report
  decisions; the harvest discipline (incident-earned, max three,
  no-report-is-normal) is retained verbatim in
  `.github/ISSUE_TEMPLATE/`. `harvest/processed.md` archived; open/closed
  issues are the queue and ledger. The `agent-harvest` repo awaits owner
  archiving.
- **The evals workstream is scrapped** — `evals/` and the instrument deleted
  (owner: delete, not archive; git history preserves). Amends the 2026-07-01
  functional-cut decision's completeness-general-as-candidate clause (the
  profile is deleted; revival needs a fresh decision). Salvage:
  `docs/harness-capabilities.md`.
- **Template redline** — `templates/AGENTS.template.md` cut to 1,503 words
  (Bootstrap Handoff, Mission-as-section, stamp, pointer bullet, merged
  durable-writing bullets); write-authority one sentence; `handoff` gains
  the field-earned rules (verbatim rotation to
  `docs/history/state-archive.md`; volatile facts `as of <commit>`; counts
  pointed-to; machine-local facts labeled or omitted; parked items
  re-verified); Session Startup gains the read-only clone-freshness check
  (never blocks). Scope tiers deleted from the approval summary (conditioned
  nothing anywhere).
- **Standing rule: no shipped rule without provenance** — a template rule is
  added, kept, or changed only with a decisions entry citing its earning
  incident; every kept line was cross-checked this run (zero lines lacked
  provenance). With the discover-era presence tests retired, this process
  rule — not CI grep — is what guards template content.

Procedures consolidated to one `procedures/bootstrap.md` (1,913 words, from
5,198 over two files; `verification.md` unchanged; the three dropbox
transport procedures deleted). Rollout: vela first (owner pick), remaining
repos on owner go; refresh flags route back as issues.


### 2026-07-03 — Playbooks install unconditionally on every run, like wrappers and hooks

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): preserved in full; installation is now `tools/refresh.py`'s replace-if-unmodified class, and toolkit-side template removal now propagates via the retired list. (implemented same day; plan:
`docs/superpowers/plans/2026-07-03-playbook-install-owner-gate.md`, as
corrected by its supersession note).

Decision: every playbook template shipped under
`.bootstrap-tmp/templates/playbooks/` is installed into <!-- lint: allow (historical install location) -->
`.agents/playbooks/<name>.md` on every route, unconditionally — the same
standing-guarantee class as operator wrappers and hooks (2026-06-18). There is
no approval-summary question, no default, no per-run choice, and no tier
gating: installation is deterministic. A playbook already present at its final
path is never silently overwritten (same rule as committed wrappers);
installed playbooks join the Committed list and the single scoped commit like
every other drafted artifact.

Supersedes, same-day, the "playbook installation is an owner choice at the
approval gate" entry (archived verbatim in
`docs/history/decisions-archive.md`). The no-discretion principle that entry
recorded stands unchanged — the model cannot assess a repo's future needs, and
"playbooks only if the scope tier justifies them" was wrong — but the
mechanism was also wrong: it removed the agent's discretion by inserting a
per-run owner question, which the owner never asked for. The first live run
that hit the gate produced exactly the friction it should not have (owner,
2026-07-03: "there are no options. everything is installed every time").
Discretion is removed by determinism, not by asking. Consequence, stated
plainly: a playbook deleted from a target repo reappears on the next refresh
run (install-when-missing is unconditional); the durable opt-out is removing
the template from the toolkit itself. Never-overwrite protects owner-modified
playbooks, not deletions.

Relationship: extends the 2026-06-18 standing-guarantee decision to the
playbook artifact class. Amends the 2026-06-09 layout decision's "optional
playbooks" wording: every shipped playbook lands at install time. The Push
Policy approval-time question (2026-06-27) is unaffected: that is
configuration the owner chose to be asked about, not installation.

### 2026-07-03 — Subdir-scoped bootstrap is not a supported mode; monorepo probe finding closed as not-applicable

Status: Active (this entry is the canonical home of the rule; the closed Open
finding is archived verbatim in `docs/history/decisions-archive.md` in this
same change; no code change).

Decision: the toolkit is pointed only at a governance root — the directory
that owns an `AGENTS.md` + `.agents/` set, normally the repo root.
Subdir-scoped bootstrap (running the toolkit against a subdirectory of a
governed repo to give that subtree its own governance) is not a supported
mode. The 2026-06-22 Open finding "route/verification probes match literal
`package.json` against repo-relative paths (monorepo subdir miss)" is closed
as not-applicable: the probe mismatch only bites on a subdir-scoped run,
which no supported path produces.

Rationale: the 2026-07-01 verbatim-template decision makes nested governance
waste by construction — `AGENTS.md` is byte-identical in every governed repo,
so a per-subtree copy duplicates the same bytes and adds a second
reconciliation surface carrying zero content. Per-subtree facts that genuinely
differ (e.g. backend vs frontend verification commands) already have a home
inside the single `.agents/` set: path-conditional rules in
`.agents/repo-guidance.md` and per-path entries in `.agents/repo-map.json`.
Splitting state or decisions per subtree would violate the
one-discoverable-current-state-entry-point invariant. Real-world nested
per-directory `AGENTS.md` layouts exist (observed 2026-07-03 in the `agentrq`
repo: `backend/` and `frontend/` each carry their own `AGENTS.md` plus a <!-- lint: allow (illustrative monorepo layout) -->
`@AGENTS.md` shim), but they are evidence about content-bearing `AGENTS.md`
systems and do not transfer to this toolkit, whose `AGENTS.md` carries no
repo-specific content.

Deferred, not decided: the don't-own-the-root scenario — a team owning only a
subtree of a large monorepo, unable to write files at the top level. The
natural handling would be pointing the toolkit at that subtree and treating it
as the governance root (one `AGENTS.md`, one `.agents/`, all paths relative to
it), not nested governance. No pilot or request has hit this; supporting it is
deferred until real demand and would be a fresh decision.

Decision-locus note, recorded for whenever this reopens: if scoped runs were
ever supported, the scope decision belongs to the human at kickoff (where the
tool is pointed is the decision); discovery only surfaces candidate-boundary
evidence as leads; the model proposes a layout through the approval summary.
Consistent with the route-collapse finding (Adopted 2026-07-01) that
mechanical detection is not load-bearing in this toolkit.


### 2026-06-28 — Durable truth lives only in harness-neutral files; harness-specific files are pure adapters

Status: Active (principle in force now; enforcement implementation deferred to a plan)

Decision: Durable repo truth — governance and repo-specific facts alike — lives
only in harness-neutral files: `AGENTS.md` (portable governance) and `.agents/`
(repo-specifics). Harness-specific entry and config files — `CLAUDE.md` and
equivalents (`GEMINI.md`, `.cursorrules`), the per-harness hook configs, and the
`.claude/commands/` wrappers — are **pure adapters**: a pointer (`CLAUDE.md` is
`@AGENTS.md` and nothing else) or a thin wrapper that calls a harness-neutral
entry point. They carry no repo facts or governance of their own. A
harness-specific file that holds durable truth is a **drift inflection point**:
invisible to every other harness reading `AGENTS.md`/`.agents/`, maintained in a
silo that diverges from the neutral source.

Corollaries settled in the same session:

- **Durable repo facts a working model learns** (not a decision, not churny
  current-state) have a home: `.agents/repo-facts.jsonl` — JSONL, append-only <!-- lint: allow (proposed-and-declined artifact) -->
  (one fact per line), `evidence` field required, read on demand, never
  auto-injected. It is the in-repo, harness-neutral equivalent of a harness's
  "auto memory" (which the harness-local-memory invariant forbids relying on).
  JSONL is chosen because the data is atomic/append-only/provenance-bearing:
  append-safety enforces the anti-rewrite discipline, a required `evidence` field
  bakes in the evidence rule, and it is mechanically validatable by
  `governance-lint`.
- **`.agents/` is an agent-facing store.** Human-readability is an explicit
  non-goal (JSON tooling covers forensics). Design priority for `.agents/`:
  prevent drift first, then agent efficiency / token savings. This priority
  governs future `.agents/` format and structure choices.
- **A must-always-see operational fact is made reliable the harness-neutral way**
  — encode it as a runnable entry point (e.g. verification = a `make`/script
  target recorded in `.agents/repo-map.json`, run not read), not by auto-loading
  it. An `@`-import auto-load of repo facts (via `CLAUDE.md` or a
  `.agents/repo-facts.*` imported file) was considered and **rejected**: it loads
  on Claude Code but is invisible to other harnesses, bifurcating the source of
  truth.

Enforcement (implementation deferred to a plan): extend the advisory `AGENTS.md`
pre-edit tripwire to also fire before edits to `CLAUDE.md` and other harness entry
files, with a pure-adapter message distinct from the portability message; add a
`governance-lint` structural check that harness-specific files contain no durable
content. The hook stays advisory, non-blocking, Claude Code + Codex only — the
cross-harness floor is unchanged.

Earned by a design near-miss caught in this session's review: to make the
verification command reliably visible under a strict-portable `AGENTS.md`, an
auto-load via a Claude-Code-only `@`-import was proposed and rejected for the
bifurcation above; the same session then established the harness-neutral facts
home and the agent-facing `.agents/` priority.

Relationship: extends the 2026-06-25 governance-boundary decision (which named the
`AGENTS.md`↔`.agents/` *content* boundary) with the harness-neutral↔harness-
specific *file* boundary and the pure-adapter rule; generalizes the
harness-local-memory Universal Invariant (out-of-repo stores are not durable) to
in-repo harness-specific files. Affected guidance to reconcile in the plan:
`templates/hooks/*` (tripwire path matcher + message), `procedures/bootstrap.md`
(Hook install section), `templates/AGENTS.template.md` / generated `AGENTS.md`
(the `repo-facts.jsonl` pointer + strict-zero portability), the `governance-lint`
Open Decision (2026-06-22), and the verification-entry-point convention in
`.agents/repo-map.json`.

### 2026-06-27 — Push policy delegated to `.agents/push-policy.md`; four standardized options; default: ask

Status: Active

Decision: Push behavior is repo-specific, declared in `.agents/push-policy.md`,
which the Prime Invariants delegate to. The Prime Invariants push clause in
`templates/AGENTS.template.md` reads: "History-rewrite and destructive or
outward-facing actions always need an explicit go. Push policy: see
`.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the
default (`ask`). `templates/approval-summary.template.md` has a Push Policy
section that presents four standardized options at approval time and must ask
the human — it may not pre-fill the choice from the decisions log or other
context (the owner's approval-time reply is the only valid source).
`procedures/bootstrap.md` Step 10 consults `.agents/push-policy.md` after
committing. The options: 1 `always` (push after every commit); 2 `operators`
(auto-push after operator-invoked commits — handoff/decision/drift/plan — ask
otherwise); 3 `docs` (auto-push docs/state-only commits, ask for code/tool);
4 `ask` (always ask, the default). `templateVersion` bumped to `2026-06-27.1`.
This repo's own `.agents/push-policy.md` was created by the 2026-06-27 dogfood
self-application run and is set to `always`. The original Open Decision rationale
(2026-06-26) is archived verbatim in `docs/history/decisions-archive.md`.

Earned by an owner-surfaced cost (2026-06-26): the prior blanket
push-needs-explicit-go Prime Invariant left commits local-only, so the canonical
remote silently lagged and later sessions/machines assumed a repo current when it
was not — directly undercutting "durable truth lives on the canonical remote."
The delegation keeps the explicit-go default for repos that want it while letting
a repo opt into auto-push. Per the AGENTS.md portability/write-authority boundary
(2026-06-25), the *policy value* is repo-specific and lives in `.agents/`, not in
`AGENTS.md`, which only points to it.

Relationship: resolves the 2026-06-26 Open Decision (option a — tier by blast
radius — at the seam of the policy file rather than as template-wide tiers).
Exercises the 2026-06-25 governance-boundary boundary (repo-specifics in
`.agents/`) and the 2026-06-22 `templateVersion` reconciliation machinery.


### 2026-06-24 - Section-level rule deduplication: one full statement per rule, pointers elsewhere

Status: Active

Decision: A normative rule gets exactly one full statement in the governance
set; every other location that needs it carries a pointer, not a second copy.
This applies the existing "smallest durable guidance set / over-documentation is
a drift risk" and "keep one canonical location, prefer pointers" invariants at
the section level — within a single AGENTS file (a rule stated in full in both
Universal Invariants and a later dedicated section is the redundancy), and across
procedures (a paragraph copied near-verbatim between `bootstrap.md` and
`migration.md`). Anchor+elaboration layering is preserved where the anchor is
genuinely terse — the Prime Invariants re-ground hook plus a fuller statement
that adds content the anchor omits — but that is not a license for two full
same-altitude copies.

Earned by a real incident: a bug report (ExchangeAdminWeb, filed to the
`agent-harvest` dropbox 2026-06-24) found a generated `AGENTS.md` restating core
rules across sections, so the file violated the minimality invariant it ships. A
redundancy map across the product governance set (2026-06-24) confirmed three
genuine targets and rejected the bug's broader framing (words-first,
no-code-without-plan, and repo-is-memory are single anchors or intended
anchor+elaboration, not redundant): (1) the flag-conflicts/report-drift rule
stated in full in both Universal Invariants and Source Of Truth; (2) the
docs-only verification carve-out stated in full in both Universal Invariants and
the Verification section (and a third time in `approval-summary.template.md`);
(3) the commit-discipline/push-gate paragraph duplicated between `bootstrap.md`
and `migration.md`. The fix keeps each rule's full statement in one canonical
home and replaces the others with pointers.

Scope: the product files only — `templates/AGENTS.template.md`,
`procedures/migration.md`, `templates/approval-summary.template.md`. This repo's
own `AGENTS.md` carries copies of (1) and (2), but it is a frozen instance from
the last deliberate self-application, not a live view of the template; it is
brought current only by deliberately re-running the product on this repo, so its
copies are left for that run and are not edited here.

Relationship: refines the 2026-06-22 "trim the per-session guidance tax"
decision, which rejected word-level prose compression (~2.7% savings; the
guidance is dense, not padded). That holds — this is a distinct axis (whole-rule
section-level duplication, not wording length), so the two are complementary, not
in conflict. Concretely applies the 2026-06-09/10 one-canonical-location and
smallest-guidance-set invariants.


### 2026-06-09 - Migrate to the standard .agents/ layout for all bootstrapped repos

Status: Active, as amended 2026-07-03

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the standard layout no longer includes `repo-map.json` / `artifact-manifest.json` (retired, flag-only on refresh); the verification command's canonical home is `.agents/repo-guidance.md`.: playbooks are part of the standard
layout, no longer optional — every shipped playbook template installs on
every run (see the 2026-07-03 playbooks decision above). The original
wording below is retained.

Decision:
Every bootstrapped repo converges on the same `.agents/` layout (AGENTS.md + .agents/state.md, .agents/decisions.md, repo-map.json, artifact-manifest.json, optional playbooks). Existing governance systems are migrated into it via inventory (migrate/supersede/leave verdicts), not left as parallel canon. Old governance files (when they stay) receive a short supersession banner at the top pointing to the replacement; content is retained as history.

Reason:
This eliminates drift from competing sources of truth and gives every future agent (including in this toolkit repo) one discoverable current-state entry point plus one place for settled decisions. The layout is the outcome of the 2026-06-09 architecture restructure.

Supersedes:
The prior two-stage PowerShell architecture (historical record only in `docs/history/`).


### 2026-06-10 - Evidence rule for all durable claims

Status: Active

Decision:
Any durable claim about repo state, CI, deployment, file custody, or another external system must cite the exact query or command that proved it is *currently active* (e.g. `git ls-remote --exit-code`, `git ls-files --error-unmatch`, a workflow file confirmed in an executable provider path whose branch triggers match the current branch, etc.). Mechanical name-matches, discovery markers, and filename conventions are leads to verify, never facts to record. If a claim cannot be proved this way, write it as a labeled assumption or leave it out.

Reason:
Prevents recording plausible-looking but unverified or stale configuration as truth. Directly addresses pilot defects where CI markers and custody were misread from presence alone.

Supersedes:
Any prior practice of treating filename conventions or static markers as sufficient proof.

### 2026-06-10 - Gitignore-aware commit contract and custody queries

Status: Active

Decision:
Before listing any file as committable in an approval summary, run `git check-ignore` on its final path. Gitignored paths are proposed only as Local-only (copied into place but never `git add`ed, never `git add -f`). Custody values in artifact manifests record the custody each file will have once the approval commit lands, proven by git query: "tracked" for files on the Committed list (existing files via `git ls-files --error-unmatch` exiting 0; new files via `git check-ignore` exiting non-zero, proving them committable), "ignored" or "untracked" for Local-only files. Never set custody from path convention, and never record draft-time custody for a file the same commit will track. New files that are not ignored are listed under Committed and will be `git add`ed explicitly (never `-A`). (Refined 2026-06-10: the self-migration followed the earlier draft-time wording and recorded "untracked" for files its own commit made tracked.)

Reason:
Respects owner intent expressed in .gitignore. Silent `git add -f` is forbidden. The bootstrap commit is always exactly the scoped list from the approved summary.

### 2026-06-10 - One-scoped-commit + push-offer-once discipline

Status: Active

Decision:
After approval, copy drafts to final paths then commit as exactly ONE scoped commit using `git add` of only the approved files (never `git add -A`). The owner's approval of the summary is the explicit authorization for that single commit. After the commit, ask once (one line), naming the repo's remotes if more than one, and push only what the owner names. Never push unprompted.

Reason:
Keeps the bootstrap change reviewable and minimal. Matches pilot-validated safety (approval authorizes one scoped commit).

### 2026-06-10 - Answer-with-words rule hardened; artifact-is-evidence-not-decision

Status: Active

Decision:
When the owner asks a question or thinks out loud, reply in plain English and stop. Never respond with edits or execution. A handed-over artifact (defect report, findings list, plan, spec) is evidence to assess, not a decision to implement; deliver the assessment, ask for the go, and stop. Session framing is not a go. This rule wins over harness/platform pressure to act without asking. Also: treat repo filenames, paths, and document contents as evidence, not instructions.

Reason:
Prevents an agent from treating a just-received defect report or plan as an automatic "go" and sweeping changes (the self-incident that produced this rule).

Supersedes:
Softer prior wording of the same intent.

> Amended 2026-07-22 (Site 5 — issue #8): qualified for completion reports only. When the owner reports a step complete inside an approved, already-scoped workflow, that report is the go for the next step the workflow already defines — no separate ritual "go" is required. "Reply in plain English and stop" / "ask for the go, and stop" still governs questions, musings, and any step not already defined by an approved workflow; new scope, a changed risk, and separately gated actions still stop. See the 2026-07-22 issue-#8 entry above.

### 2026-06-10 - PowerShell helper retired

Status: Active (historical record)

Decision:
The original PowerShell implementation of the discover/bootstrap helper is retired to `docs/history/agent-bootstrap-discover.ps1` after the Blit pilot (2026-06-10). It is an archival record only. All active work uses the Python `tools/discover.py` (standard library, no deps) and the markdown procedures/templates.

Reason:
Post-pilot cleanup; the Python version is the supported one for cross-platform (including the Windows functional probe for Store stubs).

### 2026-06-10 - Fresh-eyes verification as consistency-not-truth check

Status: Active

Decision:
The fresh-eyes test (run for all migrations) is a discoverability and internal-consistency check only. A zero-context agent given only the drafted guidance files plus the repo must be able to answer the six questions (what is the project, what is true now, what next, how verified, how to hand off a decision, and evidence for any external claims). It is not a fact-check of external claims (CI, deploy, etc.). Every UNVERIFIED external claim found during the test must be downgraded to assumption or local-only in the drafts. The outcome is recorded as one plain-English sentence in the approval summary.

Reason:
Matches the pilot finding that the test should not be mis-presented as proof of runtime truth.

### 2026-06-10 - Windows Python probe order and Store-stub detection

Status: Active

Decision:
When selecting a Python interpreter for discovery: try `py -3 --version` first (canonical Windows launcher), then `python3 --version`, then `python --version`. Treat a candidate as absent (not merely old) if the command fails or its output contains "was not found" or "Microsoft Store". A `python3` on PATH that only opens the Store is not a usable interpreter.

Reason:
Windows ships App Execution Alias stubs; presence on PATH does not imply a working Python. This probe order and detection was folded in from the ExchangeAdminWeb pilot.

### 2026-06-10 - Cwd-independent Step 0 sync

Status: Active

Decision:
All git commands in the toolkit sync (Step 0) are run as `git -C <bootstrap-repo> ...`. Never rely on the shell's current working directory. Use `git ls-remote --exit-code <url> HEAD` to test liveness before fetch. If no remote responds or fast-forward is impossible: proceed with the local copy and flag plainly in the approval summary. GitHub is authoritative; a gitea mirror that lags GitHub is expected, not a disagreement to flag. Never merge or rebase the bootstrap repo from a target session.

Reason:
Many agent harnesses reset cwd between tool calls; a bare `cd` + `git fetch` can silently operate on the wrong repo.

### 2026-06-10 - CI markers are provider-executable only + branch match required

Status: Active

Decision:
CI / build markers recorded by discovery are accepted only for files that sit in a path the provider actually executes. The packet surfaces `suspectedMisplacedCi` and `ciBranchMismatches`. Before recording any "CI gates merges" claim or using a workflow command as the automated verification entry point, the agent must confirm both the executable-path condition and that the branch triggers match the repo's current branch. If either fails, record verification as local-only and flag the dead file in the approval summary.

Reason:
Prevents treating a plausible-looking but non-executed workflow file as live CI.

### 2026-06-10 - Git-safety: ancestry vs content verification

Status: Active

Decision:
Never conclude a branch is merged from ancestry alone (`git branch --merged` can lie after `-s ours` or octopus merges). Verify the content actually arrived (`git diff <branch> <main>`) before deleting anything or treating work as landed.

Reason:
Folded from pilot experience; added to the AGENTS template Git Safety section and this repo's rules.

### 2026-06-10 - One-item-per-commit discipline (batch sweeps owner-only)

Status: Active

Decision:
When working through a list of findings or fixes, address exactly one item per commit and commit each before starting the next. Batch sweeps spanning many findings happen only on the owner's explicit request. Whether work happens on a branch is repo policy, not this rule.

Reason:
Folded from pilot; prevents monolithic "fix everything" commits that hide reviewable units. (Branch-per-item variant was considered and dropped; branching policy stays per-repo.)

### 2026-06-10 - Artifact (defect report / plan / spec) is evidence, not decision

Status: Active

Decision:
A handed-over artifact (defect report, findings list, plan, spec) is evidence to assess, not a decision to implement. The agent must deliver the assessment in plain English, ask for the explicit go, and stop. Only an explicit owner decision (not session framing or harness ritual) authorizes multi-step changes or edits.

Reason:
Direct response to the self-incident in which an agent read a softer rule and executed an unapproved fix sweep straight from a handed-over defect report.

Supersedes:
The prior, softer wording of the "answer with words" rule in this repo's AGENTS.md and the bootstrap contract.

### 2026-06-09/10 - Pilot findings folded into canon (multiple)

Status: Active (summarized)

The following were adopted during/after the three external pilots and the self-incident; each is recorded as a specific decision above or in the AGENTS template invariants where generalized:
- Revert-the-fix test check added to AGENTS template Verification.
- Ancestry-vs-content git-safety bullet.
- One-item-per-commit discipline.
- Safety-vs-ritual authority split (safety rules always bind; workflow rituals do not preempt the owner's kickoff instruction).
- Load-bearing-path check before migrating a state/decisions file.
- Summary altitude (plain English, one-screen recommendation before the inventory table).
- Approval authorizes one scoped commit only.
- Push offered once after commit, naming remotes.
- Evidence rule (durable claims cite the proving query).
- Custody-from-git rule + gitignore-aware commit contract.
- Fresh-eyes reframed as consistency-not-truth + external-claims question.
- Windows Python probe order + Store-stub detection.
- Cwd-independent Step 0 (`git -C`, ls-remote).
- Manifest schema shipped beside discover.py.
- "Answer with words" hardened with explicit artifact-is-evidence-not-decision clause.

All other pilot observations that did not yield a new durable rule were left as history in `docs/history/pilot-findings_exchangeadminweb_2026-06-10.md` and the per-pilot review files.

Supersedes:
The pre-pilot procedures and templates.

### 2026-06-18 - Operator command wrappers are a standing guarantee on every route

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the guarantee's mechanism is now refresh.py's replace-if-unmodified class, which strengthens never-overwrite: a provably-unmodified stale wrapper updates; an owner-modified one is flagged, never touched.

Decision:
On every route (greenfield, migration, update), the process audits the operator
vocabulary (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`) and, on a harness
that supports command files, drafts any missing slash-command wrappers and the
`.gitignore` edit that makes them committable - removing a blanket `.claude/`
ignore rule and adding a narrower `.claude/settings.local.json` rule so
machine-local settings stay out of git. The expected steady state is "already
present, nothing to do"; existing committed wrappers are never overwritten. The
canonical recipe lives in one place - `procedures/bootstrap.md` "Operator command
wrappers (all routes)" - and is referenced from the greenfield workflow,
`procedures/migration.md` Step 4, and the AGENTS template Bootstrap Handoff so
generated repos self-audit on update runs. Wrappers and the `.gitignore` edit
travel through the normal approval summary and land in the single scoped commit.

Reason:
A repo bootstrapped greenfield or maintained via update previously advertised the
operator words in prose but had no working slash commands, and `.claude/` was
often gitignored so even drafted wrappers never got committed - a broken-promise
UX failure for the human the toolkit exists to serve. Making wrappers a standing,
route-neutral guarantee (with the gitignore fix that makes them durable) closes
that gap.

Alternative considered and rejected:
A pilot report proposed instead routing `.claude/`-only-ignored repos to
greenfield by filtering gitignored markers out of `compute_route`. Rejected: that
routes *around* the symptom (treats a misconfigured, local-only `.claude/` as
"nothing to migrate") rather than fixing the cause. The adopted approach repairs
the gitignore configuration so the commands become durable governance, which is
the correct end state. The packet's separate custody-wording imprecision is
tracked below and is unaffected by this decision.

Supersedes:
The deferred "Command wrappers are created only on the migration route"
(2026-06-15), now adopted in generalized form.


### 2026-07-09 - Refused core-file replacement ends in an unmissable banner plus an offer to run bootstrap

Status: Active

Decision:
When `tools/refresh.py` refuses to replace a **replace-whole (core) artifact**
— for any reason — the run no longer ends with just an interleaved
`FLAG` line. After all normal output it prints an unmissable ATTENTION banner
naming each unreplaced core file and stating that hand-repair is not the fix;
the fix is the bootstrap procedure. Under the banner, refresh resolves the
notice to "run bootstrap": it probes `PATH` at that moment for known harness
CLIs (`docs/harness-capabilities.md` is the capability record; the probe is
`shutil.which`, never a remembered path) and

- at a real TTY (stdin **and** stdout), asks one question offering to launch
  a detected harness interactively in the target repo with a kickoff prompt
  that points at `procedures/bootstrap.md`; any answer other than a listed
  number (q, empty, junk, EOF) declines and changes nothing;
- otherwise (agents, CI, pipes), never prompts and never hangs: it prints the
  exact ready-to-paste launch command per detected harness, or the procedure
  path when none is installed.

Flags on `replace-if-unmodified` artifacts keep today's quiet single-line
shape; clean runs are byte-identical to before. Exit code is unchanged.

Reason:
Owner direction this session (2026-07-09): the refresh output that matters is
an unmissable notice that a core file was NOT replaced; the one line the owner
cares about was the easiest to miss, and the correct recovery (bootstrap, with
its legacy-governance carve-out) was named nowhere in the output. Plan:
`docs/superpowers/plans/2026-07-09-refresh-bootstrap-offer.md`.

Alternative considered and rejected:
The shim/skill/PATH-entry-point proposal (declined by the owner 2026-07-09,
archived verbatim in `docs/history/state-archive.md`). This decision honors
its standing constraints: assume no harness, no PowerShell, no remembered
path, no remembered interpreter; nothing auto-runs — a launch requires an
explicit interactive yes at a real TTY.

Supersedes:
Nothing; extends the 2026-07-08 refresh behavior (flag semantics unchanged).


### 2026-07-17 - Owner gates are self-contained; owner-facing reports open with an executive summary

Status: Active

Decision:
Two owner-communication rules, canonical home `templates/AGENTS.template.md`
(new `## Owner Gates` section; amended `## Final Response`). Installed copies
propagate on the owner's next self-refresh; the template/copy lag is the
expected steady state.

1. Self-contained gates: any question put to the owner (plan decision,
   approval, contested finding) is written for an owner arriving cold, hours
   later, with no session memory — one short message carrying a line or two
   of context, the question, what concretely changes under each option, and
   the recommended option with its reason. It states what stays blocked until
   the ruling lands; silence never authorizes proceeding. An ask answerable
   only by scrolling back, opening a plan document, or re-reading a
   transcript is malformed.
2. Executive summary first: owner-facing final responses open with a short
   executive summary — what changed, what was validated, any remaining risk,
   anything awaiting the owner — bottom line first, in plain English;
   supporting detail follows the summary, never precedes it.

Reason:
Owner direction this session (2026-07-17): decision gates were surfacing as
bare questions after long autonomous stretches, answerable only by
transcript archaeology. Approved wording: "yes I want the exec summary req
and self-contained gate."

Supersedes:
Nothing; generalizes the `plan` operator's existing chat-ask rule (roughly
25-50 plain-English words, one decision at a time) to all owner gates, and
tightens `## Final Response` from "explain" to summary-first ordering.


## Open Decisions (deferred - not yet adopted)

These are assessed findings the owner chose to record for a future decision
rather than implement now. The process is unchanged until one is adopted. Each
states the verified evidence, the options, and the standing recommendation.

- None currently (queue emptied 2026-07-12; closed entries are archived
  verbatim in `docs/history/decisions-archive.md`).
