# Condense the product guidance (functional cut)

Status: DRAFT — awaits owner approval. No template/procedure/code touched yet.
Scope: the **product** (`templates/AGENTS.template.md` first; procedures are an
owner scope pick, S1). Explicitly **not** this repo's own `AGENTS.md` (frozen
instance; reconciled only by a later deliberate self-application run, per the
established 2026-06-24/25 pattern).

## Why this plan exists

Owner direction (2026-06-30, recorded in
`evals/swebench-pro/PLAN-funcpass-2026-06-30.md` §"owner direction" and
`.agents/state.md` CURRENT FOCUS): the shipped guidance is too large — it is
`@`-imported into every session of every bootstrapped repo, so its length is a
recurring per-session token tax — and the closed eval workstream showed that a
whole functional class of guidance prose does not pay for itself on strong
harnesses. The direction is a **functional cut**: keep behavioral contracts,
facts, and pointers; drop capability-exhortation and rationale prose.

This is a different axis from the two prior efficiency decisions, both of which
stand unchanged:

- **2026-06-22 (word-level compression rejected, ~2.7%):** that audit required
  *every normative claim to survive* and only squeezed wording. This cut does
  not squeeze wording — surviving claims keep clear full-sentence form. It
  removes whole *non-normative* clauses and whole *non-paying* claims.
- **2026-06-24 (section-level dedup):** one full statement per rule, pointers
  elsewhere. This cut applies that decision to duplication the template still
  carries (see candidate list).

## Evidence for the cut classes

- **Capability exhortation is placebo-to-harmful on strong models.** Eval
  conclusions (`evals/swebench-pro/PLAN-funcpass-2026-06-30.md`): completeness
  prose helped only a weak local model on a fixture built to need it, was null
  on strong subscription harnesses (grok 9-bug with/without; Sonnet), and hurt
  once on a ceiling fixture. The strong-harness gap is a mechanism (attention at
  edit-failure/re-author), not missing knowledge — prose cannot close it, and
  the hook that targeted the mechanism was dropped 2026-07-01
  (`docs/superpowers/plans/2026-06-30-product-completeness-hook-and-prose.md`
  §Outcome).
- **Rationale already has a durable home.** The decision lifecycle keeps every
  rule's why in `.agents/decisions.md` / `docs/history/decisions-archive.md`.
  Rationale clauses inside the injected template are a second copy paid for on
  every session.
- **Behavioral contracts are the class that works.** They encode owner intent a
  model cannot self-derive (words-first, plan gate, commit/push discipline,
  write-authority) — these are not exhortation and are kept.

## Method — classification rubric, applied per clause

Each clause of the template is classified and dispositioned:

| Class | Test | Disposition |
|---|---|---|
| Behavioral contract | Constrains behavior the owner could not otherwise rely on (authority, gating, git safety, write-authority, roadblock restraint) | **Keep**, one full statement, terse |
| Fact / pointer | Names where truth lives (`.agents/*`, push policy, verification entry point) | **Keep** |
| Definition | Operator vocabulary, lifecycle terms | **Keep** |
| Rationale / meta-commentary | Explains *why* a rule exists, cross-names other rules, second worked example | **Cut** — the why lives in decisions.md/archive |
| Capability exhortation | Steers model competence (thoroughness, completeness, quality) rather than authority/process | **Cut** — eval evidence above |
| Duplication | Same rule stated in full twice across the set | **Pointer-ize** (2026-06-24) |

Hard rule for the approval gate: **every normative claim in the current template
is accounted for** — kept, pointer-ized, or on an explicit drop list the owner
signs off. Nothing disappears silently.

## Candidate cuts (verified against the raw file at implementation)

Identified from a structural pass; the implementation re-reads the raw template
(this pass was read through a lossy token filter, per the token-efficiency
invariant's escape hatch):

1. **Drift operator ↔ portability invariant duplication.** The operator entry
   restates the portability test plus flag/allow examples the Universal
   Invariant already states in full. Invariant keeps the full statement; the
   operator entry points to it. (2026-06-24 precedent; largest single win.)
2. **Stall-not-length bullet.** Keep trigger, evidence-class definition,
   threshold-with-default, and the length-is-never-the-trigger scope guard; cut
   the cross-reference commentary ("the loop-level form of the vacuous-change
   and drift rules…").
3. **Harness-local-memory bullet.** Keep the rule and the persist-into-repo
   instruction; cut the mechanism explanation (not versioned / doesn't travel /
   invisible — that is rationale).
4. **Anti-enumeration bullet.** Keep the rule; cut the worked example and the
   drift-mechanics rationale clause.
5. **Roadblock bullet.** Keep the rule and the recognition list (the enumeration
   is load-bearing for recognition); cut the trailing rationale sentence.
6. **Governance-boundary invariants (portability + write-authority).** Keep both
   rules and the copy-test; trim parenthetical meta ("the two rules together
   close both wrong-content and wrong-moment") and redundant examples.
7. **Bootstrap Handoff / Session Startup.** Minor trims only; the Handoff
   section was already collapsed to a pointer in 2026-06-22.

Not candidates (kept as-is in kind): Prime Invariants block (already terse,
probed by discovery), operator definitions, Verification section (operative
contract), Git Safety (contracts earned by incidents).

## Structural constraints (must survive the cut)

- `<!-- prime:begin -->` / `<!-- prime:end -->` markers and the Prime
  Invariants block (`tools/discover.py:303-304` probes it).
- All six backtick-wrapped operator words (`tools/discover.py:275`, including
  the known `` `playbook <name>` `` matching bug — do not change the wrapping
  shape).
- `<!-- templateVersion -->` stamp, **bumped to `2026-07-01`** so the update
  route reconciles already-stamped-current target repos to the condensed text
  (`tools/discover.py:282`; same propagation reasoning as the 2026-06-25.2
  bump). Without the bump, stamped-current repos never receive the cut.
- Test suite green: `python3 -m unittest discover -s tests -v`. Any test
  content adjusted for the cut is mutation-proven (hermetic temp copy).

## Deliverable at the approval gate

Before the template commit, the owner sees:

1. A per-claim accounting table: every current normative claim → kept /
   pointer-ized / **dropped** (the drop list is the sign-off surface).
2. Measured before/after byte and approximate token counts.
3. The full condensed template text.

## Slices (one scoped commit each, push policy `always`)

1. This plan doc (drafted now).
2. `templates/AGENTS.template.md` functional cut + `templateVersion` bump +
   suite green. Lands only after the owner approves the accounting table.
3. Decision entry in `.agents/decisions.md` recording the adopted cut (and its
   relationship to 2026-06-22/24), plus `.agents/state.md` update.
4. (Only if S1 = yes) procedures pass, separately planned sizing — not started
   under this plan without an explicit go.

## Non-goals

- No word-level compression of surviving claims (2026-06-22 stands).
- No edit to this repo's own `AGENTS.md` (frozen instance; a follow-up
  self-application run reconciles it after the template lands — owner-gated).
- No shipping of `completeness-general` prose in this pass (see G2); the
  profile stays in `evals/governance_profiles/` as the candidate artifact.
- No reopening of model testing or the dropped edit-failure hook.
- `test_ground/AGENTS_*.md` compaction attempts are scratch/trash: not a
  source, never sent to a model.

## Open decisions (owner)

- **S1 — scope:** template only this pass (**recommend**: it is the per-session
  cost; procedures are per-run cost and 23.6 KB `bootstrap.md` deserves its own
  sizing) vs. also procedures now.
- **S2 — approval surface:** full per-claim accounting table at the gate
  (**recommend**: cheap, and the drop list is exactly what needs owner eyes) vs.
  summary-level approval.
- **G2 — completeness-general:** defer entirely (**recommend**: adding an
  exhortation artifact in the same pass that removes exhortation is incoherent
  unless clearly opt-in; the eval evidence is weak-model-only) vs. ship now as
  an opt-in optional template offered in the approval summary.

## Verification

- Slice 2: `python3 -m unittest discover -s tests -v`; mutation-prove any
  adjusted test guards.
- Doc-only slices: `git diff --check`.
