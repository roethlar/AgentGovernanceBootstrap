# Review Economy: Tiered Reviewer Routing + Repair-Delta Re-Review

Status: DRAFT 2026-07-17 — awaiting owner approval. Two cross-vendor
review rounds run 2026-07-17, both triaged in "Plan review" below:
round 1 grok 0.2.102 (pinned `grok-4.5`, headless CLI, 10 findings, all
admitted); round 2 codex via MCP server (owner restored credits and
registered `codex mcp-server`; 10 findings, all admitted — two of them
defects introduced by round-1 fixes). All revisions folded into this
draft. The codex round also motivated the "Invocation transport"
subsection; the owner then validated the reverse direction
(`claude mcp serve` called from codex, registered in the owner's global
codex config), making MCP the preferred transport both ways.

## Problem

The review playbooks govern review *semantics* but leave model routing
ambient. `codereview` states its tightly framed per-finding conformance
task suits weaker reviewer models; `openreview` states its unprimed open
question rewards stronger reviewers. Nothing enforces either claim, and
nothing records which model tier actually reviewed anything. By this
repo's own standard — if it isn't recorded, it didn't happen — reviewer
strength is currently unrecorded state. The practical consequences:

- The most capable (most expensive) model gets used for every round of
  every review, including tightly framed conformance checks the playbook
  itself says do not need it.
- A reopened finding replays the full review over the original
  merge-base and head, re-paying for rediscovery of code that did not
  change, when the only open question is whether the repair closed the
  specific failure.
- Transport smoke tests can consume a premium call even when the harness
  version and profile are unchanged since the last probe.

Origin: external review commissioned by the owner (GPT-5.6, 2026-07-17),
delivered outside the repo. Its diagnosis is admitted; its cost
arithmetic is directional only (API price ratios do not map to
subscription quota weights) and is deliberately NOT carried into this
plan as fact.

## Decisions (owner gates)

- **D1 — default tiers per playbook.** **In discussion** — an earlier
  "adopted as amended" stamp here was premature and is retracted.
  Owner directives so far (2026-07-17): two-tier structure and
  per-playbook defaults stand (`codereview` → standard, `openreview` →
  frontier); opus 4.8 joins **standard** (on par with sonnet 5);
  **Luna is dropped** — the transport role that briefly sheltered it
  is deleted (see transcript rule); effort belongs in any capability
  comparison (fable-low judged weaker and costlier than sonnet-max —
  tentative); keep the scheme simple. Effort pins ruled and confirmed
  (owner, 2026-07-17, superseding the same-day draft mapping): effort
  binds to **tier**, never to arrival path — `codereview` standard
  runs **high**; `codereview` frontier runs **xhigh** whether reached
  by escalation or owner force (an owner-forced frontier dispatch is
  the owner saying "this is hard", which is the xhigh case);
  `openreview` pins **max**. The monotonic ladder high < xhigh < max
  tracks review depth. openreview@max has no escalation headroom by
  design: a contested openreview round resolves by owner
  adjudication, never a stronger dispatch — above max sits the owner.
  D4 is dissolved (see below). Frontier pins ruled (owner,
  2026-07-17): Claude → **claude-sonnet-5**; OpenAI → **gpt-5.6-sol**.
  Grok and Gemini have no competitive frontier model; their frontier
  slots carry **fallback-grade** pins — **grok-4.5** and
  **gemini-3.1-pro** — so the two-tier structure stays total on every
  harness, but a fallback-grade frontier verdict is not
  frontier-grade adjudication and the tiers entry says so via the
  frontier `grade` field; frontier routing on fallback-grade
  harnesses halts to the owner (ruled 2026-07-17, see Escalation
  triggers). Fable
  is out of frontier contention (already judged weaker and costlier
  than sonnet-max). Sonnet-5 serving as Claude frontier while
  opus 4.8 ≈ sonnet 5 sits in standard is legitimate under pair
  semantics: tier identity includes effort, so frontier @xhigh and
  standard @high differentiate even where model strength is on par.
  Standard pins ruled (owner, 2026-07-17), closing the routing table:
  Claude standard = **sonnet-5** — single-model harness until opus-5
  releases; that release is a re-confirmation event under the
  once-per-harness-version rule, no automation. OpenAI standard =
  **gpt-5.6-terra**. Grok = single-model **grok-4.5** in both slots,
  effort-differentiated (standard@high / frontier@xhigh). Gemini
  (agy) = **gemini-3.5-flash @ high** standard (flash ships low /
  medium / high only) and **gemini-3.1-pro @ high** frontier — the
  owner's exact levels: no xhigh pair exists on this harness, so
  Gemini's fallback frontier deviates from frontier→xhigh by harness
  limitation, and the owner-confirmed pair is authoritative where the
  ladder's level is not exposed. D1 is closed; no routing decisions
  remain open.
- **D2 — reopen auto-escalation.** Any reopened finding escalates one
  tier on redispatch. Recommendation: adopt — it is the cheapest defense
  against a standard-tier reviewer mis-judging its own reopened work,
  and repair-delta scoping (below) keeps the escalated call small.
- **D3 — archive the commissioning review.** Copy the GPT-5.6 review
  into `docs/history/` for provenance (it currently lives outside the
  repo at a machine-local path). Recommendation: adopt.
- **D4 — xhigh selector.** Dissolved (owner, 2026-07-17): xhigh
  binds to the frontier tier itself (see D1), so no selector —
  phrase, path list, or heuristic — exists or is needed. Escalation
  *is* the selector: complexity earns xhigh by defeating the
  standard reviewer, not by prediction. Recorded so it is not
  reopened.

## Design

### Tier semantics are committed; model names are not

The playbooks own the *meaning* of two reviewer tiers. A tier resolves
to a single owner-confirmed **(model, effort) pair** per harness —
effort is part of tier identity, because capability ordering holds only
for configured pairs, never bare model names (owner ruling 2026-07-17:
opus 4.8 ≈ sonnet 5, so a flagship name may sit in standard; fable at
low effort is judged weaker and costlier than sonnet at max):

- **standard** — the owner-confirmed best-value pair; sufficient for
  tightly framed conformance verdicts.
- **frontier** — an owner-confirmed pair strictly stronger than
  standard *as configured*; required for unprimed judgment and for
  escalated findings.

Effort is tier-bound within each playbook (owner, 2026-07-17):
`codereview` dispatches standard at high and frontier at xhigh —
regardless of whether frontier was reached by escalation or owner
force — and `openreview` dispatches its frontier pair at max. No
other effort levels are reachable from either playbook. One carve-out
(owner, 2026-07-17): where a harness does not expose the ruled level,
the owner-confirmed pair is authoritative — Gemini's fallback
frontier runs gemini-3.1-pro @ high because no xhigh exists there.

The closed routing table (all pins owner-ruled 2026-07-17; cells
without a confirmed pair block fail-closed per the rule above):

| Harness      | codereview standard    | codereview frontier (grade)      | openreview        |
|--------------|------------------------|----------------------------------|-------------------|
| Claude       | sonnet-5 @ high        | sonnet-5 @ xhigh (competitive)   | sonnet-5 @ max    |
| OpenAI       | gpt-5.6-terra @ high   | gpt-5.6-sol @ xhigh (competitive)| gpt-5.6-sol @ max |
| Grok         | grok-4.5 @ high        | grok-4.5 @ xhigh (fallback)      | unconfirmed       |
| Gemini (agy) | gemini-3.5-flash @ high| gemini-3.1-pro @ high (fallback) | unconfirmed       |

Claude re-confirms on opus-5 release (standing
once-per-harness-version mechanism; no automation).
The `tiers` block each playbook commits carries that playbook's
confirmed pairs.

There are exactly two tiers, only tiers issue verdicts, and there is
**no third role**. The former transport role (a cheapest-model slot for
envelope pings) is deleted (owner, 2026-07-17): transport failures are
pre-inference — a rotted flag, dead server, or retired pin errors out
before any model consumes tokens — so a routine ping is recurring cost
insuring against failures that are already nearly free, and the one
risk it did guard (silent misrouting) is closed for free by the
transcript rule below. Grok R8/R9's "mechanical extraction" economy
class stays dropped — no work of any kind routes to economy models.

Committed templates never name concrete model IDs — model names rot, and
rot in an installed artifact is drift. Resolution of tier → today's
model ID + effort flag lives in the version-keyed machine-local cache
`.agents/review/harnesses.local.json`, extended with a `tiers` block per
harness. This cache is **not currently gitignored** (codex C9 —
verified: `git check-ignore` misses it); slice 2 adds the `.gitignore`
entry `.agents/review/*.local.json` in the same commit that first
defines the schema, before any cache write. This reconciles the
capability record's "pin models explicitly" rule with the anti-rot
rule: pinning happens at invocation time from the local file, never in
committed text.

Cache schema and tier resolution (codex C5) — slice 2 commits this
exact shape into the playbook text:

    "tiers": {
      "standard":  {"model": "<id>", "effort": "<level>", "flags": ["..."], "confirmed": "<harness version>"},
      "frontier":  {"model": "<id>", "effort": "<level>", "flags": ["..."], "confirmed": "<harness version>", "grade": "<competitive|fallback>"}
    }

`grade` is owner-declared at confirmation, frontier-only:
`competitive` (Claude, OpenAI) or `fallback` (Grok, Gemini). It is
machine-visible at dispatch time and drives the fallback-harness halt
rule under Escalation triggers below.

The probe *proposes* the tier→(model, effort) mapping; the **owner
confirms it once per harness version**, and the confirmation is
recorded in the entry. Tier strength is an owner judgment, not a probe
inference — neither "stronger" nor "best value" is resolvable from
`--help` output. Fail-closed: a dispatch whose tier has no confirmed
entry blocks and asks the owner; nothing guesses. A single-model
harness may still differentiate tiers by effort; only when both pairs
are identical does it record the same pair under both verdict tiers
explicitly.

### Probe extension + provenance

The existing probe-and-verify flow ("Deriving the reviewer incantation",
`codereview` playbook) additionally discovers the model-selection and
effort flags, verifies the pinned model resolves, and records the
resolved model ID in the cache. Every finding record gains one line:

    Reviewer: <harness> / <resolved model id> / <effort> / <tier>
      [escalated: <ordered list of ALL matched trigger ids>]

The `escalated:` value is the ordered, comma-separated list of every
trigger that matched (e.g. `escalated: T1,T2,T5`), not one arbitrarily
chosen ID — the risk table's "every routing decision is recorded"
promise requires all of them (codex C10). An owner force appears as its
own entry, first: `escalated: owner`. A frontier-ceiling reopen appends
`(ceiling)` to the T5 entry.

**Transcript rule (owner, 2026-07-17 — replaces the deleted transport
role):** the `Reviewer:` line is copied from the invocation transcript
— the MCP result envelope or CLI JSON stream — never from the
reviewer's prose. **A review with no transcript is not a review**: an
unreachable server, failed call, or absent transcript metadata means
the dispatch failed, whatever text came back. Dispatch is a direct
tool call, so no model sits in the router seat to improvise around a
dead server; this closes the recorded misroute incident (probe,
2026-07-17: claude server down, model-in-the-loop satisfied the task
via an unrelated registered server) mechanically, on every call, at
zero cost.

Cache validity (grok R4, corrected by codex C6; ping deleted by owner
2026-07-17): a cache hit on unchanged harness version + profile skips
the *full* probe, and there is **no per-session ping** — validation is
entirely lazy. Each tier's pin is validated, envelope and pin together,
on its **first real dispatch** of the session: a model-not-found,
connection, or equivalent error invalidates that cache entry, forces a
re-probe, and retries the dispatch once. Model IDs retire without
harness version bumps (recorded precedent: the `grok-build` retirement
in `docs/harness-capabilities.md`), so the cache never becomes the
sole unverified pin.

### Invocation transport: MCP where verified, CLI otherwise

Two transports exist for dispatching a reviewer harness, and the
incantation cache entry records which one is active per harness.
**`mcp` is preferred wherever a verified registration exists; `cli` is
the universal fallback.** The preference is not about cost capture — it
is structural:

- **Thread continuity is the repair-delta mechanism natively.** A
  redispatch is a follow-up message in the conversation of the reviewer
  that predicted the failure: only the repair packet is sent, the
  original context is already in-thread, and provider-side cached-input
  pricing makes the continued thread cheaper than a cold re-prime.
- **Parameterized invocation retires flag-drift maintenance.** Model,
  sandbox, and approval policy travel as structured fields instead of
  version-churning CLI flags — less surface for the probe machinery.
- **No shell-quoting layer.** Prompts travel as JSON strings; the
  recorded PowerShell/UTF-8 quoting failure class disappears.

The route is verified in **both directions** on this machine
(2026-07-17): codex dispatched as reviewer via `codex mcp-server`
(round-2 review of this plan, threadId follow-ups), and claude
dispatched via `claude mcp serve` — validated by the owner and
registered in the owner's global codex config. Cross-vendor review of
claude-authored work by codex, and codex-authored work by claude, both
run MCP-first.

Probe-and-verify covers both transports identically and lazily: an
`mcp` entry is validated exactly like a `cli` one — by its first real
dispatch, under the invalidation rule above. MCP registration
(including permission scoping for `claude mcp serve`) is machine-local
user config — consistent with the machine-local cache philosophy;
committed text names transports, never server registrations.

Recorded envelope-probe facts (codex-cli 0.144.5, 2026-07-17), so the
next probe does not rediscover them:

- Per-call registration works without config mutation:
  `-c 'mcp_servers.claude.command="claude"'`
  `-c 'mcp_servers.claude.args=["mcp","serve"]'`. Tool discovery
  succeeded on the first attempt (~19k tokens on `gpt-5.6-luna`, low
  effort).
- Headless tool calls through `claude mcp serve` are gated by the
  permission engine's elicitation round-trip; a codex caller at
  `approval: never` cancels it (`user cancelled MCP tool call`) —
  **fail-closed**, resolved by permission scoping in the registration,
  not by prompt text.
- With the claude server down, a model told to use it silently
  satisfied the probe task through an unrelated registered MCP server —
  an artifact of putting a model in the router seat during the probe.
  Production dispatch is a direct tool call with no room to improvise;
  the transcript rule (provenance section) closes this mechanically.
- Known-bad incantations: `--allowedTools` prepended to the
  `mcp serve` args kills the server at handshake;
  `-c 'mcp_servers.<name>.enabled=false'` with a quoted server name
  corrupts config merging ("invalid transport").

Effort binding on the MCP route (observed on this machine, codex-cli
0.144.5, 2026-07-17): effort is set at **conversation creation**,
never mid-thread. The codex MCP `codex` tool takes `model` and
`config` (including `model_reasoning_effort`) as structured fields on
the initial call; the `codex-reply` follow-up carries no model or
config fields and inherits the thread's pair. For `claude mcp serve`,
model and effort are launch properties of the per-call registration
(the `-c mcp_servers.claude.*` incantation above) — chosen per
dispatch, fixed for that server session. Consequence: a redispatch
that keeps the pinned (model, effort) pair rides the in-thread
repair-delta at cached-input prices; any effort or tier change — a T5
escalation, an xhigh bump — necessarily opens a fresh conversation at
cold-prime cost, which the fresh-session rule for escalations already
mandates. Effort is therefore a dispatch-boundary decision: the pair
is picked before the thread starts, never adjusted inside it.
Owner accepted 2026-07-17: escalation = new conversation, always;
the re-prime is the price of fresh eyes, paid on any transport that
honors the fresh-session rule. Mid-thread effort nudges on an
existing conversation are rejected as anchored escalation.

### Escalation triggers (codereview only; openreview is frontier by D1)

Mechanical triggers are evaluated deterministically from the diff before
any reviewer runs; judgment triggers come from the standard-tier round.
Any trigger routes the finding's review (or re-review) to frontier:

- **T1 (mechanical, pre-review):** the diff touches a sensitive path.
  Matching is executable, not semantic (codex C3): changed paths are
  tested against git-pathspec globs. The playbook ships default globs
  (e.g. `**/auth*`, `**/secret*`, `**/*credential*`, `**/crypto*`,
  `**/migrations/**`, `**/schema*`, `**/*.proto`, `**/wire/**`,
  `**/serializ*`); the canonical per-repo override is the committed
  file `.agents/review/sensitive-paths` with **replace** semantics
  (present ⇒ it is the whole list). Glob matching is approximate by
  construction; the owner override below is the recourse, and no
  per-session invention occurs (grok R6).
- **T2 (mechanical, pre-dispatch — relabeled per codex C8):** the
  finding record's exact committed field `**Severity**:` reads CRITICAL
  or HIGH (impact line required, per the existing severity gate). The
  severity was recorded when the finding was raised, so T2 is a
  deterministic pre-dispatch check — such findings route straight to
  frontier without consuming a standard round. T2 never reads the
  redispatch verdict envelope, whose schema is unchanged and carries no
  severity (grok R2).
- **T3 (mechanical, orchestrator-evaluated — narrowed per codex C2):**
  the guard proof artifact is missing, its verification command exits
  nonzero, or one orchestrator-run repeat disagrees with the recorded
  result (flake). These checks run outside any reviewer, so no verdict
  schema field is needed. Proof-*quality* judgment (ambiguous,
  manual-only) is not T3: a reviewer who distrusts a proof issues the
  existing `reopened` verdict, which escalates via T5.
- **T4 (mechanical, post-repair — narrowed per codex C4):** exact
  path-set comparison of the repair commits against the declared file
  set snapshotted in the repair record. Expansion beyond it does **not**
  silently trigger a replay — it halts the round and routes to the
  owner as contested, preserving the committed declared-files contract.
  "Approach drift" is judgment, not T4: it reaches the reviewer, who
  reopens (→ T5) or the owner. Full replay happens only on an explicit
  owner ask.
- **T5 (mechanical, D2):** any reopened finding escalates one tier on
  redispatch — ceiling at frontier, **within the harness the owner
  named** (codex C7: `codereview <agent>` is an operator contract; no
  trigger silently consumes another provider's quota). If the prior
  round was already frontier, the reopen re-dispatches frontier in a
  fresh session of the same harness and records `escalated: T5
  (ceiling)`. Switching provider requires an explicit owner dispatch.
  No third tier is invented and no false escalation line is written
  (grok R10).

Owner override (grok R7): the operator phrase `codereview <agent>
frontier` forces frontier for that dispatch and is recorded as
`escalated: owner`. This is the documented mechanism behind the "owner
can always invoke frontier" mitigation — no cache hand-editing.

Fallback-grade harnesses (owner, 2026-07-17): where the confirmed
frontier entry carries `"grade": "fallback"` (Grok, Gemini), any
trigger that would route to frontier — T1–T5 alike — instead halts
the finding as contested to the owner. Escalation must buy a strictly
stronger adjudicator; a fallback frontier is the same class at more
effort, so auto-dispatching it would be escalation theater. At the
halt the owner either accepts the fallback dispatch (recorded
`escalated: <triggers> (fallback accepted: owner)`) or re-dispatches
on a competitive-frontier harness via the existing owner phrase —
provider switching stays owner-only (C7) and no new machinery is
invented.

Contested findings (coder and reviewer still disagree after one round)
remain **owner-adjudicated** — the committed contract (`codereview.md`:
contested records "awaiting owner adjudication"; the adjudicator role
is optional) stands, and this plan's own out-of-scope line forbids
automating owner decisions (codex C1 — the prior draft silently
auto-dispatched an arbiter). What the plan adds is only the *offer*:
when a third harness has a verified `harnesses.local.json` entry on
this machine (probe-and-verify completed, not merely mentioned in
`docs/harness-capabilities.md` — grok R5), the contested record names
it as an available adjudicator. Dispatching it takes an explicit owner
go. The standing rule that the author never adjudicates its own work is
unchanged.

### Repair-delta re-review

The per-finding redispatch packet becomes: finding ID + original finding
text + the repair diff + the verification command + the guard proof.
Redispatch pin mechanics (grok R3): `base` = the head SHA the finding
was raised against (pre-repair head), `head` = current branch head; the
orchestrator computes the repair diff from those pins and pipes it to
the reviewer — the reviewer does not rediscover scope from SHAs. The
guard proof still executes against the full current head (the worktree
procedure is unchanged); only the *review mandate* narrows. This
explicitly amends the dispatch contract for redispatch rounds in the
playbook text — it is not a silent departure from the committed
base/head contract. The re-reviewer's mandate is to confirm the
specific predicted failure is closed and no adjacent regression exists
in the touched surface — NOT to re-review the whole branch. Full replay
happens only on an explicit owner ask — including after a T4 halt (T4
routes to the owner; it never replays on its own). `openreview` remains
the whole-change instrument and is untouched.

### Recorded cost facts (owner-supplied, 2026-07-17)

The cost ratios that justify tiering are recorded owner statements, not
measurements — better evidence than any n=1 dogfood round:

- Anthropic (Max-plan token budget): **fable = 2× opus = 4× sonnet** —
  at like-for-like effort; effort multiplies real cost, and the owner
  judges fable-low both costlier and weaker than sonnet-max.
- Capability parity (owner judgment): **opus 4.8 ≈ sonnet 5** — both
  standard-tier candidates.
- OpenAI: **GPT 5.6 Sol at $30/1M output tokens**, costlier than 5.6
  Terra and Luna; intra-OpenAI ratios unrecorded — routing treats
  Terra as the standard-tier candidate and Sol as frontier. **Luna is
  unrouted** — no role exists for it.

No measured round is required and no transport constraint follows from
cost capture. The dogfood for this plan is the per-finding `codereview`
redispatch round still pending from 2026-07-16 (state `## Now`), run
under the new routing on an owner go; it validates routing behavior
(triggers, provenance, cache) — it carries no measurement mandate.

## Slices

1. **Playbook text** — `templates/playbooks/codereview.md`: tier
   semantics, escalation triggers T1–T5 (T1 default globs +
   `.agents/review/sensitive-paths` override), repair-delta redispatch
   packet, contested-record adjudicator *offer* (verified third harness
   named; dispatch is owner-only). `templates/playbooks/openreview.md`:
   one-line frontier-tier pin. No wrapper/skill changes (thin pointers).
2. **Probe + cache + provenance** — `harnesses.local.json` `tiers`
   schema with owner-confirmed pins and transport field (`mcp`/`cli`),
   the `.gitignore` entry `.agents/review/*.local.json` in the same
   commit that first defines the schema, probe steps for model/effort
   flag discovery, per-tier first-dispatch validation, `Reviewer:` line
   (all matched triggers, copied from the invocation transcript) in
   the finding record and review index.
3. **Tests** — `tests/test_templates.py`: playbooks carry tier
   semantics; curated-denylist lint that committed playbooks name no
   concrete model IDs (denylist maintained beside the capability
   record's model facts).
4. **Record + dogfood** — decisions recorded verbatim (D1–D3), state
   updated, D3 archive copy, then the dogfood round (owner go); close
   with commit map.

## Risks

- **Under-escalation by the standard reviewer** (the weak model decides
  whether the strong one is needed). Mitigated: after the codex round
  all five triggers are mechanical — no reviewer self-rating gates
  escalation, and a reviewer who merely distrusts a repair still
  escalates via the `reopened` verdict (T5); the owner can always
  invoke frontier explicitly; every routing decision is recorded with
  all matched triggers, so drift is auditable.
- **Delta review misses cross-cutting regressions.** Mitigated: a T4
  path-set mismatch halts the delta round for owner adjudication (full
  replay on owner order); `openreview` remains available for
  whole-change judgment; the delta mandate includes the touched
  surface, not just changed lines.
- **Flag churn across harness versions.** Mitigated: the cache is
  version-keyed and re-probed on mismatch — the existing incantation
  mechanism, extended, not a new one.
- **Unrecorded intra-OpenAI cost ratios.** Mitigated: the recorded
  owner ratios cover the Anthropic side and Sol's absolute price;
  Terra routes standard and Luna is unrouted, so the unknown
  ratio cannot cause a frontier-priced dispatch.

## Out of scope

- The owner's playbook-by-name selection ruling — tier routing operates
  *within* a playbook and does not touch it.
- Any change to `openreview`'s mandate or *effective* strength. The
  one-line frontier pin in slice 1 **codifies** current practice
  (openreview already runs on the strongest profile); it does not alter
  what the instrument does (grok R1 — resolves the earlier
  contradiction between this bullet and slice 1).
- Automating any owner decision; new harness requirements; cost claims.

## Plan review (grok, 2026-07-17)

Cross-vendor review: grok 0.2.102, pinned `grok-4.5`, headless one-shot,
structured JSON findings. Verdict as returned: "Do not implement as
written: resolve the openreview touch/strength contradiction and T2's
schema mismatch first; several HIGH routing/cache/arbiter gaps will
otherwise force ad-hoc behavior at dogfood time." All 10 findings
admitted and folded into this draft:

| id | sev | finding (compressed) | disposition |
|----|-----|----------------------|-------------|
| R1 | CRITICAL | Plan both forbids and schedules an openreview edit | Out of scope reworded: pin codifies, does not change |
| R2 | CRITICAL | T2 read severity from a verdict schema that has none | T2 rebound to finding record `Severity:` field |
| R3 | HIGH | Redispatch base/head pins and diff ownership unspecified | Pin mechanics defined; orchestrator computes diff; guard proof stays full-head |
| R4 | HIGH | Cache hit skipped smoke entirely → cache becomes sole pin; model IDs retire without version bumps (grok-build precedent) | Lazy validation: each tier's first real dispatch validates its pin; invalid pin → re-probe + one retry (ping deleted, owner 2026-07-17) |
| R5 | HIGH | "Third provider where configured" had no concrete test | Defined: verified local incantation-cache entry |
| R6 | HIGH | T1 sensitive-path classifier had no shipped class list | Default list in playbook text; committed per-repo override |
| R7 | MEDIUM | No documented owner phrase to force frontier | `codereview <agent> frontier` → `escalated: owner` |
| R8 | MEDIUM | Economy "mechanical extraction" unverified by any probe | Dropped; no economy role of any kind (transport role also deleted, owner 2026-07-17) |
| R9 | MEDIUM | Economy class unrepresentable in two-tier schema | Moot by deletion: no economy work is routed anywhere; two verdict tiers only |
| R10 | MEDIUM | T5 had no ceiling above frontier | Ceiling defined; `escalated: T5 (ceiling)` provenance |

## Plan review round 2 (codex, 2026-07-17)

Second cross-vendor round after the grok revisions, dispatched through
the newly registered `codex mcp-server` (owner-restored credits;
model/sandbox pinned per call). 10 findings (2 CRITICAL, 4 HIGH,
4 MEDIUM) — all admitted and folded into this draft. The two CRITICALs
are defects *introduced by round-1 fixes*, which is itself the argument
for cross-vendor rounds:

| id | sev | finding (compressed) | disposition |
|----|-----|----------------------|-------------|
| C1 | CRITICAL | R5 fix auto-dispatched an arbiter — contradicts the committed contested contract and this plan's own "no automating owner decisions" line | Contested stays owner-adjudicated; verified third harness is named as an *offer* only |
| C6 | CRITICAL | R4 fix validated the wrong pin: transport ping proves nothing about verdict-tier model IDs | Ping deleted outright (owner 2026-07-17); every tier validated on first real dispatch, invalid pin → re-probe + one retry |
| C2 | HIGH | T3 "judgment" needed proof-quality fields the verdict schema doesn't have | T3 narrowed to mechanical orchestrator checks; proof distrust routes via `reopened` → T5 |
| C3 | HIGH | T1 "classes" were semantic, not executable | Git-pathspec globs shipped; committed `.agents/review/sensitive-paths` override, replace semantics |
| C4 | HIGH | T4 silent full replay discarded the declared-files contract | T4 halts round as contested to owner; approach drift is reviewer/owner judgment, not T4 |
| C5 | HIGH | `tiers` cache schema unspecified; "strongest available" unresolvable from `--help` | Exact schema committed; owner confirms tier→(model, effort) once per harness version; fail-closed |
| C7 | MEDIUM | T5 escalation could silently switch providers and consume unbudgeted quota | Escalation bound to the owner-named harness; provider switch is owner-only |
| C8 | MEDIUM | T2 labeled judgment but reads a committed field deterministically | Relabeled mechanical pre-dispatch; CRITICAL/HIGH findings route straight to frontier |
| C9 | MEDIUM | Cache described as gitignored but `git check-ignore` misses it | `.gitignore` entry added in the same commit that defines the schema, before any write |
| C10 | MEDIUM | Provenance recorded one trigger ID when several matched | `escalated:` records the ordered list of all matched triggers |

Raw findings from both rounds retained at the review scratch paths for
the owner's inspection until plan close.

## Notes

Template-side change: this repo's installed copies lag until the owner's
next self-refresh (owner-only), per the standing convergence rule.
