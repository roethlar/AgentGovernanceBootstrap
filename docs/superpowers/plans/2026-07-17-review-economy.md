# Review Economy: Tiered Reviewer Routing + Repair-Delta Re-Review

Status: DRAFT 2026-07-17 — awaiting owner approval. Cross-vendor plan
review run 2026-07-17: grok 0.2.102, pinned `grok-4.5`, structured
output (owner is out of codex credits). 10 findings (2 CRITICAL, 4
HIGH, 4 MEDIUM) — all admitted; every revision is folded into this
draft. Triage record in "Plan review" below.

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

- **D1 — default tiers per playbook.** `codereview` defaults to the
  **standard** tier; `openreview` defaults to the **frontier** tier.
  This changes default review strength, so it needs an owner ruling.
  Recommendation: adopt — it is what the playbooks' own text already
  claims about reviewer suitability.
- **D2 — reopen auto-escalation.** Any reopened finding escalates one
  tier on redispatch. Recommendation: adopt — it is the cheapest defense
  against a standard-tier reviewer mis-judging its own reopened work,
  and repair-delta scoping (below) keeps the escalated call small.
- **D3 — archive the commissioning review.** Copy the GPT-5.6 review
  into `docs/history/` for provenance (it currently lives outside the
  repo at a machine-local path). Recommendation: adopt.

## Design

### Tier semantics are committed; model names are not

The playbooks own the *meaning* of two reviewer tiers:

- **standard** — the harness's capable non-flagship profile; sufficient
  for tightly framed conformance verdicts.
- **frontier** — the harness's strongest available profile; required for
  unprimed judgment and for escalated findings.

There are exactly two tiers, and only tiers issue verdicts. The cache
additionally holds one non-tier role, **transport** — the cheapest
verified profile, used exclusively for transport/envelope checks. It is
not a tier, never issues verdicts, and is not covered by tier semantics
(grok R8/R9: "mechanical extraction" is dropped — no probe verifies
extraction competence, so nothing routes extraction to economy models).

Committed templates never name concrete model IDs — model names rot, and
rot in an installed artifact is drift. Resolution of tier → today's
model ID + effort flag lives in the existing gitignored, version-keyed
machine-local cache `.agents/review/harnesses.local.json`, extended with
a `tiers` block per harness. This reconciles the capability record's
"pin models explicitly" rule with the anti-rot rule: pinning happens at
invocation time from the local file, never in committed text.

### Probe extension + provenance

The existing probe-and-verify flow ("Deriving the reviewer incantation",
`codereview` playbook) additionally discovers the model-selection and
effort flags, verifies the pinned model resolves, and records the
resolved model ID in the cache. Every finding record gains one line:

    Reviewer: <harness> / <resolved model id> / <effort> / <tier>
      [escalated: <trigger id> | owner | <trigger id> (ceiling)]

Cache validity (grok R4): a cache hit on unchanged harness version +
profile skips the *full* probe, but every session's first dispatch per
harness still runs one cheap transport ping against the pinned model ID
(transport role, never a frontier call). A model-not-found or
equivalent error invalidates the cache entry and forces a re-probe —
model IDs retire without harness version bumps (recorded precedent: the
`grok-build` retirement in `docs/harness-capabilities.md`). The
gitignored cache therefore never becomes the sole unverified pin.

### Escalation triggers (codereview only; openreview is frontier by D1)

Mechanical triggers are evaluated deterministically from the diff before
any reviewer runs; judgment triggers come from the standard-tier round.
Any trigger routes the finding's review (or re-review) to frontier:

- **T1 (mechanical, pre-review):** the diff touches sensitive-path
  classes per the default class list shipped in the playbook text —
  authn/authz, secrets and credential material, crypto, persistence
  schema/migrations, concurrency primitives, protocol/serialization
  compatibility. A repo may override with a committed per-repo list;
  absent one, the default applies. No per-session invention (grok R6).
- **T2 (judgment):** the finding record's `Severity:` field is CRITICAL
  or HIGH (impact line required, per the existing severity gate). T2
  binds to the finding record — a field that already exists in the
  committed finding format — never to the redispatch verdict envelope,
  whose schema (`verdict`/`guard_confirmed`/comments) is unchanged by
  this plan and carries no severity (grok R2).
- **T3 (judgment):** the repair proof is missing, ambiguous,
  manual-only, or flaky — cannot distinguish fixed from reverted.
- **T4 (mechanical, post-repair):** the repair expands beyond the
  originally declared files or approach. T4 also voids delta scoping —
  full replay.
- **T5 (mechanical, D2):** any reopened finding escalates one tier on
  redispatch — ceiling at frontier. If the prior round was already
  frontier, the reopen re-dispatches frontier in a fresh session (a
  different provider where one is verified available) and the
  provenance line records `escalated: T5 (ceiling)`. No third tier is
  invented and no false escalation line is written (grok R10).

Owner override (grok R7): the operator phrase `codereview <agent>
frontier` forces frontier for that dispatch and is recorded as
`escalated: owner`. This is the documented mechanism behind the "owner
can always invoke frontier" mitigation — no cache hand-editing.

Contested findings (coder and reviewer still disagree after one round)
go to the existing arbiter. Third-provider availability is a concrete
test (grok R5): a verified `harnesses.local.json` entry for a third
harness on this machine (probe-and-verify completed, not merely
mentioned in `docs/harness-capabilities.md`). If present, the arbiter
runs there; else a frontier profile of a non-author provider. The
standing rule that the author never adjudicates its own work is
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
happens only on T4 or an explicit owner ask. `openreview` remains the
whole-change instrument and is untouched.

### Measurement before cost claims

No cost ratios are committed anywhere. The dogfood for this plan is the
per-finding `codereview` redispatch round still pending from 2026-07-16
(state `## Now`), run under the new routing on an owner go; actual
per-round consumption is recorded in this plan's Status line at close.

## Slices

1. **Playbook text** — `templates/playbooks/codereview.md`: tier
   semantics, escalation triggers T1–T5, repair-delta redispatch packet,
   arbiter third-provider preference. `templates/playbooks/openreview.md`:
   one-line frontier-tier pin. No wrapper/skill changes (thin pointers).
2. **Probe + cache + provenance** — `harnesses.local.json` `tiers`
   schema, probe steps for model/effort flag discovery, `Reviewer:` line
   in the finding record and review index.
3. **Tests** — `tests/test_templates.py`: playbooks carry tier
   semantics; curated-denylist lint that committed playbooks name no
   concrete model IDs (denylist maintained beside the capability
   record's model facts).
4. **Record + dogfood** — decisions recorded verbatim (D1–D3), state
   updated, D3 archive copy, then the measured dogfood round (owner go);
   close with commit map.

## Risks

- **Under-escalation by the standard reviewer** (the weak model decides
  whether the strong one is needed). Mitigated: T1/T4/T5 are mechanical
  and cannot be under-rated; the owner can always invoke frontier
  explicitly; every routing decision is recorded, so drift is auditable.
- **Delta review misses cross-cutting regressions.** Mitigated: T4
  voids delta scoping; `openreview` remains available for whole-change
  judgment; the delta mandate includes the touched surface, not just
  changed lines.
- **Flag churn across harness versions.** Mitigated: the cache is
  version-keyed and re-probed on mismatch — the existing incantation
  mechanism, extended, not a new one.
- **Unknown subscription quota weights.** Mitigated: measurement in the
  dogfood; no committed claims.

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
| R4 | HIGH | Cache hit skipped smoke entirely → cache becomes sole pin; model IDs retire without version bumps (grok-build precedent) | Per-session transport ping; invalid-model error invalidates cache |
| R5 | HIGH | "Third provider where configured" had no concrete test | Defined: verified local incantation-cache entry |
| R6 | HIGH | T1 sensitive-path classifier had no shipped class list | Default list in playbook text; committed per-repo override |
| R7 | MEDIUM | No documented owner phrase to force frontier | `codereview <agent> frontier` → `escalated: owner` |
| R8 | MEDIUM | Economy "mechanical extraction" unverified by any probe | Dropped; transport role is transport-only |
| R9 | MEDIUM | Economy class unrepresentable in two-tier schema | Named non-tier `transport` role; two verdict tiers unchanged |
| R10 | MEDIUM | T5 had no ceiling above frontier | Ceiling defined; `escalated: T5 (ceiling)` provenance |

Raw findings JSON retained at the review scratch path for the owner's
inspection until plan close.

## Notes

Template-side change: this repo's installed copies lag until the owner's
next self-refresh (owner-only), per the standing convergence rule.
