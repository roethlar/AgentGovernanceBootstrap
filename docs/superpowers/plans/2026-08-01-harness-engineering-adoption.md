# Plan: harness-engineering adoption — enforcement, standing authority, and feedback upgrades

Status: DRAFT 2026-08-01 — scope set by owner ruling 2026-08-01: six
phases plus an optional kimi probe, carried as one plan. No
implementation is authorized yet. Each phase starts on its own owner
go, and each phase's open rulings are listed inside it; work proceeds
only behind the rulings it has.
Reviewed: openreview codex (gpt-5.6-sol @ xhigh, competitive) over
`8bb748a..1dd3788`: **acceptable_with_changes**. Material changes
awaiting per-item owner rulings: (1) define which gates a standing
grant may waive and which are non-waivable; (2) capture rescues
durably at occurrence, catchup classifies rather than reconstructs;
(3) lightweight-plan slice lists are copied into `.agents/state.md`
before implementation; (4) parse codex `apply_patch` targets from
`tool_input` in `protect-governance.py` (it reads only
`file_path`/`notebook_path` today — fails open on codex);
(5) trust ACTION fires on install and update, naming project trust,
`features.hooks`, and per-handler re-trust. MC6 (Verification section
named another machine's interpreter) adopted by owner ruling
2026-08-01 and applied — the section now carries the portable
`<probed-python>` probe order.
Transport note: `capability_ok` false — the reviewer attempted the
allowlisted plan-lint command and reported the proof unmet, while
repo-read capability is evidenced by its line-precise citations;
outcome accepted salvage-first per owner ruling 2026-08-01
(formatting/compliance deviations are notes, never discards). Two
HIGH findings ride material changes 1 and 4; findings enter the
codereview intake gate only on per-item owner go.

## Provenance and problem

Source material: OpenAI's harness-engineering report (Ryan Lopopolo,
2026-02-11, openai.com/index/harness-engineering) — a five-month
agent-only build whose durable lessons overlap this toolkit's existing
design (repo as system of record, short entry file, plans as
artifacts) and diverge where the toolkit is thin. Evaluated against
this repo, the genuine gaps are:

1. **No autonomy ladder.** Gates are identical on day 1 and day 500 of
   a governed repo. `.agents/push-policy.md` proves the pattern for
   exactly one action class (push); no mechanism lets an owner durably
   grant or revoke pre-approval for any other class of work.
2. **No failure-to-capability ratchet.** When an agent needs a human
   rescue, nothing prompts converting the rescue into a durable rule,
   guard, or tool. The report's discipline — "what capability is
   missing, and how do we make it both legible and enforceable" — has
   no trigger point in the toolkit.
3. **Thin plan contract.** `templates/playbooks/plan.md` (23 lines)
   has no weight tiers, no per-slice done conditions, no progress or
   decision log, no closure lifecycle — all of which this repo itself
   practices (see any closed plan in `docs/superpowers/plans/`) but
   does not ship.
4. **Only the obedience half of the guard rule.** `AGENTS.md` forbids
   circumventing guards of unestablished provenance but never states
   the authoring half: persistent rule violations get promoted from
   prose to mechanical guards, and a guard's message states its
   provenance and the fix.
5. **Enforcement underuses its delivery vehicle.** Refresh installs
   hooks and uses that power for one rule on one harness
   (`protect-governance.py`, Claude Code). Codex hooks are now
   verified viable (see Constraints).
6. **The template is a compressed rulebook, not a map.** Same length
   as the report's table-of-contents file, opposite shape: every line
   an imperative of equal weight.

## Constraints (repo evidence — read before any phase)

- **Token-neutral template.** Additions to
  `templates/AGENTS.template.md` displace existing wording; the file's
  token cost never grows (2026-07-28 decision). Phases 1, 4, and 6
  each need an owner-ruled displacement target.
- **Hook enforcement is Claude Code + codex only.**
  `docs/harness-capabilities.md` (2026-08-01 ledger entries): codex
  0.146.0 fires repo-local `.codex/hooks.json` (Claude-compatible
  schema) in exec mode behind three gates — `[features] hooks = true`,
  a `[projects]` trust entry, per-handler hash trust (`/hooks` pinning
  or `--dangerously-bypass-hook-trust`). Blocking works **only** via
  stdout JSON `permissionDecision: "deny"`; exit 2 logs
  `PreToolUse Failed` and the tool proceeds. grok/agy hook configs are
  retired/unverified; kimi is unprobed. Prose therefore stays the
  primary enforcement layer everywhere; hooks are defense in depth.
- **codex does not process `@` imports** (capability record):
  guidance moved out of `AGENTS.md` into referenced files downgrades
  on codex from injected to directed-read. Phase 6 must weigh every
  move against this.
- **Verify-once gate.** A harness adapter ships only after a live
  check on that harness confirms the mechanism fires; every outcome is
  recorded in `docs/harness-capabilities.md` with its date.
- **Shipped-set maintenance.** Any change to a shipped source file
  appends the outgoing normalized hash to its `formerly[]` in
  `tools/shipped-set.json` in the same commit. New repo-owned policy
  files use the `seeded[]` class (install if absent, otherwise never
  touched), like `.agents/push-policy.md`.
- **Owner harness priority** (capability record header, 2026-08-01):
  Claude Code and codex are the enforcement targets; kimi > grok > agy
  follow, none vital.

## Phase 1 — standing authority (autonomy ladder)

Generalize the push-policy pattern into recorded, revocable grants of
pre-approved work.

Design:

- New template `templates/standing-authority.template.md`, seeded to
  `.agents/standing-authority.md` via a `seeded[]` entry in
  `tools/shipped-set.json` (action text: "seeded (repo-owned from now
  on); record owner grants here"). Ships empty of grants: a header
  explaining semantics plus a `## Grants` section containing "none
  recorded".
- Grant semantics (stated in the template header): each grant is
  owner-written or owner-dictated, dated, and names a class of work
  that no longer needs a per-item ask (example shape: "docs-typo
  fixes: no plan needed, commit per slice, 2026-08-01"). A grant is
  read literally and narrowly; anything not plainly inside a grant
  keeps the default gates. Revocation is deletion or a dated
  revocation line. Push authority stays in `.agents/push-policy.md` —
  one canonical location; grants must not restate it.
- `templates/AGENTS.template.md`: the no-code-change-without-a-plan
  invariant gains recognition of recorded grants — the plan gate reads
  "without an approved plan or a recorded grant in
  `.agents/standing-authority.md`" (final wording is an owner
  ruling). The standard-layout pointer is portable, same class as the
  existing push-policy pointer.
- `procedures/bootstrap.md` / `procedures/setup.md`: mention the
  seeded file where the push policy's seeding is described (verify
  exact touch points at implementation; keep to one line each).
- Tests: extend the seeded-file coverage in `tests/` (the
  push-policy seed tests, e.g. `SeedTests`) to the new file; add a
  template pin tying the invariant wording to the seeded target path.

Open rulings (owner, at implementation): (a) exact invariant wording
and its token-neutral displacement target; (b) the template's example
grant shape.

Done condition: refresh on a bare fixture repo seeds the file;
refresh on a repo with an edited copy never touches it (both
test-proven); suite green; template word count not above its
pre-phase count.

## Phase 2 — rescue capture in `catchup`

The failure-to-capability ratchet, riding the existing hygiene sweep.

Design — `templates/playbooks/catchup.md`:

- Add one bullet to "## Hygiene sweep": since the last catchup, scan
  `.agents/state.md` and the git log for work that needed a human
  rescue — an owner correction, a manual fix of agent output, a
  stalled loop a human unblocked. For each, name the missing
  capability, rule, or guard that would have prevented it, and carry
  it into the report as a proposed decision or earned-practice
  candidate. Record nothing without the owner's go.
- Extend "## Report": the report names rescue findings (or "no
  rescues") alongside the existing tidy line.

Playbooks load at invoke time; the token-neutral rule binds only the
template body, so this is additive. Wrapper/skill descriptions
(`templates/commands/claude/catchup.md`,
`templates/skills/shared/catchup/SKILL.md`) are unchanged — the verb's
meaning is the same. `formerly[]` append for the playbook.

Open rulings: none beyond the phase go.

Done condition: playbook carries the bullet and report line; a
structural pin in `tests/test_templates.py` holds a load-bearing
fragment (e.g. the literal "rescue"); suite green.

## Phase 3 — plan playbook: weight tiers and done conditions

Ship what this repo already practices.

Design — `templates/playbooks/plan.md` additions (playbook, so
additive; keep the existing four paragraphs):

- **Two plan weights.** Lightweight: small bounded changes — the plan
  can be a short section in `.agents/state.md` or the chat-approved
  slice list, no document required. Execution plan: broad or
  multi-slice work — a durable dated document in the repo's plan
  location, with the properties below. The agent proposes the weight;
  the owner's go on the plan fixes it.
- **Done conditions.** Every slice of an execution plan names its
  verifiable done condition — a test moving red to green, a command's
  output, a probe outcome — checkable by a cold agent without the
  drafting context.
- **Progress and decision log.** An execution plan carries its own
  status: rulings received (dated, with the owner's wording), slices
  landed (with commits), and open questions. The Status line closes
  with a dated closure marker and verification results when work
  lands.
- **Closure.** A plan whose work has landed is closed in the same
  motion as the landing's paperwork; a superseded plan says what
  supersedes it.

Note for the drafter: this repo's own plan lint
(`tests/test_plan_lint.py`) enforces the Status-line convention
locally; the playbook states the convention portably without naming
this repo's lint.

Open rulings: none beyond the phase go.

Done condition: playbook carries both tiers, the done-condition rule,
and the log/closure sections; structural pin on load-bearing fragments
("done condition", "execution plan"); suite green.

## Phase 4 — guard-promotion wording

The authoring half of the roadblock rule, in the template.

Design — `templates/AGENTS.template.md`, Universal Invariants: the
roadblock bullet (or an adjacent line — owner ruling) gains the
promotion ladder: guidance an agent keeps violating is a candidate
for promotion to a mechanical guard (test, lint, hook), routed as a
proposed decision; a guard added under this rule states, in its own
failure message, what it protects and what to do instead — which is
what makes the obedience half cheap to obey. Wording must pass the
portability test (true in an unrelated repo) and be paid for by a
displacement target.

Open rulings: (a) final wording and displacement target (owner);
(b) whether the promotion sentence lives in the roadblock bullet or
stands alone.

Done condition: template carries the promotion rule at or below the
pre-phase word count; existing template pins green; suite green.

## Phase 5 — hook hardening (Claude Code + codex)

Ship the codex guard; extend Claude Code defense in depth. Every
sub-item passes the verify-once gate before shipping, with outcomes
recorded in `docs/harness-capabilities.md`.

### 5a — deny-shape unification of `protect-governance.py`

`templates/hooks/claude/protect-governance.py` currently blocks via
exit 2. Codex requires the JSON `permissionDecision: "deny"` shape.
Two candidate designs, chosen by probe at implementation:

1. **Single output:** emit the JSON deny with exit 0 everywhere —
   valid on codex (verified 2026-08-01) and documented for Claude
   Code; requires a live Claude Code re-probe before shipping
   (the current positive, 2026-07-16, covers exit-2 only).
2. **Branch on harness:** Claude Code sets `CLAUDE_PROJECT_DIR`;
   codex does not. Keep exit-2 under `CLAUDE_PROJECT_DIR`, emit JSON
   otherwise. No re-probe of the Claude path needed.

Prefer 1 if the probe passes (one code path); fall back to 2.

### 5b — codex adapter artifacts

- Revived shipped artifact `templates/hooks/codex/hooks.json` <!-- plan-lint: allow -->
  (a path retired in `0af5d31` when the unverified tripwire era
  closed), target `.codex/hooks.json`, class `replace`: a
  `PreToolUse` entry running the same `protect-governance.py`
  (installed once at `.claude/hooks/protect-governance.py`; the codex
  config references that path — one canonical script). The target is
  currently in `tools/shipped-set.json` `retired[]` with four
  historical hashes: move the entry to `artifacts[]` and keep every
  historical hash in its `formerly[]`, so formerly-shipped deployed
  copies update cleanly instead of reporting drift (a target may not
  appear in both lists — manifest validation enforces it). Interpreter selection reuses the
  viability-probed `py -3` / `python3` / `python` chain from
  `templates/hooks/claude/settings.json`; probe how codex executes
  hook `command` strings on Windows (`commandWindows` exists in the
  schema) before fixing the final command shape.
- Trust UX: refresh cannot and must not edit user-level config. The
  refresh report gains an ACTION line for the codex hook install:
  one-time interactive `/hooks` trust in that repo, plus the
  user-level `[features] hooks = true` requirement. Wording lives
  with the artifact entry; `procedures/bootstrap.md` notes it where
  hooks are described. The `AGENTS.md` session-startup provision
  (trust step only on explicit go) already covers agent behavior.
- SessionStart re-ground is **not** shipped for codex — the harness
  re-reads `AGENTS.md` natively (capability record, 2026-07-08).

### 5c — Claude Code Stop-hook nudge (candidate)

A Stop hook that checks `git status --porcelain` for tracked
modifications at session stop and, when dirty, blocks once with a
reason instructing commit-or-report (respecting `stop_hook_active` to
prevent loops). Enforces the commit-each-slice invariant as defense
in depth. Requires a live Stop-hook probe (never probed here) and an
owner ruling on shipping at all — a forced continuation is the most
intrusive hook class.

Open rulings: (a) 5a design choice ratification after probes;
(b) 5c ship/no-ship; (c) the ACTION-line wording.

Done condition: codex probe in a fixture repo shows the installed
hook blocking an `AGENTS.md` edit via `apply_patch` with the JSON
deny (and Claude Code still blocking via its shipped path); refresh
installs `.codex/hooks.json` on a fixture and reports the ACTION
line (test-proven); ledger entries recorded; suite green.

## Phase 6 — map-shaped template trim (conservative, last)

Method, not a wording list — every concrete move is its own owner
ruling at implementation:

1. Inventory `templates/AGENTS.template.md` for lines whose full
   detail is needed only at a specific moment (verb invocation,
   git operation, final response) and already lives, or could live,
   in an invoke-time artifact (playbook, skill).
2. For each candidate, test against the codex directed-read
   constraint: a hard invariant whose violation is silent or
   irreversible stays inline; procedural detail with a natural
   invoke-time home may move.
3. Put candidates to the owner one at a time with the projected token
   change; apply approved moves; net template token count must fall
   or hold.
4. Closing this phase with "no safe moves found" is an acceptable
   outcome and is recorded as such.

Runs only after phases 1–5 land, since they alter the very sections
under review.

Done condition: per-move rulings recorded; template pins and suite
green; final word count at or below the phase-start count.

## Phase 7 (optional) — kimi capability probe

Cheap, standalone, any time: probe the kimi CLI on the dev machine —
version; governance load vector (`AGENTS.md`? `CLAUDE.md` shim
needed? headless flag differences); repo-skill discovery from
`.agents/skills/`; any hook surface. Record every outcome, positive
or negative, in `docs/harness-capabilities.md` (which currently marks
kimi unprobed). No adapter ships from this phase; any positive
findings feed a future ask.

Done condition: capability record carries dated kimi entries for the
four questions above.

## Ordering and commit shape

Phases run 1 → 2 → 3 → 4 → 5 → 6; phase 7 floats. One phase at a
time, each on its own owner go; within a phase, one slice per commit,
suite green per slice, `formerly[]` appends ride the commit that
changes the shipped file. This plan's Status line accrues rulings and
landings as they happen.

## Verification

Interpreter: resolve `<probed-python>` by the probe order in
`procedures/bootstrap.md` Step 1 (floor 3.10); the executing machine's
resolved command and required environment are recorded in
`.agents/machines.md` — read that file, do not assume another
machine's entry (MC6, adopted by owner ruling 2026-08-01).

1. `<probed-python> -m unittest discover -s tests -v` after each
   slice.
2. Guard proof for every new structural pin: revert the paired edit,
   pin fails, restore, green.
3. Live probes for phase 5 per the verify-once gate, outcomes into
   `docs/harness-capabilities.md`.
4. `git diff --check`; this file:
   `<probed-python> -m unittest tests.test_plan_lint -v`.

## Rollout boundary

Landing in this repo changes what ships, not what is installed
anywhere: this repo's installed copies lag until the owner's
self-refresh from the product clone, and Bixi receives changes only
on the owner's `publish` word. Neither action is authorized by this
plan. Codex hook trust in governed repos is a per-repo owner action
that no tool automates.
