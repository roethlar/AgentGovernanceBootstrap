# Governance Toolkit v2 — greenfield draft

**Status: draft. This tree does not govern this repo.** The live toolkit remains
`tools/` + `procedures/` + `templates/` at the repo root; v2 is a from-scratch rebuild
of the same mission, proposed for owner review.

## The spirit, restated

Repositories maintained by LLM coding agents need three things no model tier
provides: durable memory across sessions, owner authority over irreversible acts, and
drift control across agents and harnesses. v1 delivers these. It also delivers, in
every session's prompt, a quantity of procedural coaching that capable models don't
need and that measurably competes with their judgment. v2 keeps the law and deletes
the coaching.

## Design principles

1. **The prompt is a budget.** The always-loaded constitution is capped at 400 words,
   the repo context file at 700 — enforced mechanically by the checker, so every new
   rule must evict a weaker one. v1 grew to ~2,300 always-loaded words because nothing
   pushed back; v2 makes bloat a build failure.
2. **Law, not coaching.** Rules state *what* binds, never *how* to comply. No worked
   examples, no numeric thresholds, no restating a rule in two strengths. A capable
   agent supplies the how; a repo that runs weaker agents adds playbooks for them.
3. **Prose for judgment, code for checks.** v1 put judgment in code (749 lines of
   discovery Python) and checking in prose (exhortations not to hand-edit). v2
   inverts: the installing agent *is* the discovery tool (`procedures/install.md` is a
   prompt, not a program), and the only code is a small verifier (`tools/check.py`) —
   checksums, budgets, dead pointers.
4. **Progressive disclosure.** Always loaded: the constitution. Per-repo: one context
   file. On demand: playbooks and operators. Only during install/refresh: procedures.
   v1 carried bootstrap-handoff instructions in every session of every governed repo
   to serve an event that happens twice a year; v2 installs zero bootstrap residue.
5. **Gate on risk, not category.** v1's "no code change without an approved plan"
   gates a typo fix and a rewrite identically. v2 gates on reversibility and blast
   radius: reversible-in-repo-and-verified proceeds; destructive, outward-facing,
   history-rewriting, governance-touching, or scope-growing asks first. **This is the
   one deliberate policy change** — everything else is compression, this is a
   different trade, and adopting it is an owner decision.
6. **Drift detection is mechanical.** v1 shipped a one-harness tripwire hook that
   reminds on edit attempts. v2 freezes checksums of upstream-owned files into
   `.agents/governance.json`; `check.py` catches any hand-edit after the fact, on any
   harness, and the refresh procedure refuses to overwrite unreconciled drift.

## What v2 keeps from v1, verbatim in spirit

Words-first. Repo-is-memory with commit-as-you-go. The append-only decisions ledger.
Prove-the-guard verification (a test must fail with its fix reverted). Roadblock
provenance. Stall-not-duration escalation. Flag-conflicts-never-pick. Upstream-owned
core replaced whole through a gated run. The compaction re-ground hook. The operator
vocabulary (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`).

## Layout

    AGENTS.md                        constitution (≤400 words, upstream-owned)
    templates/context.md             mission + map + verify + norms (≤700 words, repo-owned)
    templates/state.md               the handoff (overwrite freely)
    templates/decisions.md           append-only ledger
    templates/playbooks/operators.md operator definitions (loaded on demand)
    procedures/install.md            bootstrap-as-prompt; agent discovers, owner gates
    procedures/refresh.md            replace-whole update with drift reconciliation
    tools/check.py                   the verifier; installed as .agents/check.py
    adapters/                        harness plumbing only (Claude compaction hook)

Installed footprint in a target repo: `AGENTS.md`, `.agents/{context,state,
decisions}.md`, `.agents/check.py`, `.agents/governance.json`,
`.agents/playbooks/operators.md`, optional adapter. Roughly 350 always-loaded words
where v1 loads ~2,300.

## What v1 has that v2 deliberately lacks

- `discover.py` and its fixture suite — replaced by agent judgment plus a verifier.
- Route-specific procedures (25K bootstrap.md, migration.md, harvest.md, shims,
  inventory/approval/manifest templates) — install.md subsumes fresh-install and
  migration in one page; harvest becomes an ordinary `decision` operator use.
- The Prime/Universal invariant split — one Law list, each rule stated once.
- The tripwire hook — superseded by checksum verification (see principle 6).
- Numeric coaching (stall thresholds, portability test essays) — the rule remains,
  the tutorial doesn't.

## Honest risks

- **Weak-agent floor.** v1's redundancy and coaching are armor for weak models. v2
  assumes Fable/Opus-class agents; a repo routinely running weaker ones should add a
  coaching playbook rather than re-bloat the constitution.
- **Rule 2 grants more autonomy.** The risk gate trusts the agent to classify
  reversibility honestly. If that trust is premature, restoring v1's plan gate is a
  one-line context.md norm ("all code changes gate on an approved plan").
- **Unproven.** v1's shape is battle-tested across real repos; v2 has been dogfooded
  only against itself. Pilot on one low-stakes repo before any canon switch.
