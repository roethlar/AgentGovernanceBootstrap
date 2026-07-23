# Decisions-as-claims audit — re-run of the holistic review with the correct charter

Status: IN EXECUTION 2026-07-23 — Pass 1 and Pass 2 complete; findings
landed in `docs/superpowers/plans/2026-07-23-audit-findings.md` (41
entries audited: 16 HOLDS, 20 HOLDS-UNENFORCED, 2 HOLDS-UNSHIPPED,
2 STALE, 1 CONTRADICTED; architecture verdict: incremental surgery).
STALE/CONTRADICTED verdicts route to the owner one at a time (R1);
Fix Queue items F4+ land only behind a per-item owner go.

## Why this plan exists

The 2026-07-22 holistic review
(`docs/superpowers/plans/2026-07-22-holistic-toolkit-improvements.md`)
was run as a compliance audit: every `Status: Active` entry in
`.agents/decisions.md` was treated as an axiom, and the review only
surfaced defects consistent with existing rulings. That filter silently
discards any finding that requires questioning a ruling. Proof it missed
real defects, all found by the owner afterward:

- The shipped handoff text never told agents to commit the records it
  writes, and the rule that would have caught it (2026-07-22
  paperwork-follows-work) existed only in this repo's local decisions
  file — a rule that never shipped governed nobody. Fixed in `680bac9`
  and `ad5145f`.
- The handoff procedure lives as a ~120-word bullet in
  `templates/AGENTS.template.md`, loaded every session by every agent,
  though it runs once at session end — while the `drift` bullet already
  demonstrates the correct shape (one dispatch line; procedure in a
  playbook read at invoke time). The placement was never questioned
  because a ruling was read as settling it.
- The section-level dedup rule (2026-06-24) is enforced by nothing; a
  redundant re-enumeration shipped and the owner had to catch it.

Each is an instance of a *class* the review never enumerated. This plan
is the re-run with rulings as inputs to verify, not constraints.

## Repo facts the auditor needs (verify before relying)

- `.agents/decisions.md` — live rulings under `## Decisions` (headers
  `### YYYY-MM-DD — title`), plus `## Open Decisions (deferred)`.
  Archived entries: `docs/history/decisions-archive.md`.
- `templates/` — the shipped artifact set, installed into governed repos
  by `tools/refresh.py` per `tools/shipped-set.json`. MAINTENANCE RULE:
  any change to a shipped source appends the outgoing file hash to that
  artifact's `formerly[]` list in the manifest.
- Tests: `/opt/homebrew/bin/python3.14 -m unittest discover -s tests -p
  "test_*.py"` (161 passing at plan time). Suite must stay green.
- Reviewer dispatch exists (tiered routing D1–D3, 2026-07-17 ruling;
  fleet model map `.agents/model-map.json`): bulk reading can be
  dispatched to non-Claude reviewers to spare the owner's Claude budget.
  Use it for the per-ruling evidence passes; reserve the interactive
  session for adjudication.
- Binding process rules: words-first; one item behind an explicit owner
  go (R1); never end on a bare blocker (R2); records kept current as
  work lands (R3); plan docs are agent-facing and cold-implementable;
  owner decisions are presented in chat one at a time with problem,
  change, cost, recommendation.

## Charter

### Pass 1 — per-ruling audit (dispatchable)

Enumerate every entry in `## Decisions` and `## Open Decisions`. For
each, answer four questions from repo evidence, not from the ruling's
own prose:

1. EVIDENCE — does the current repo still support the ruling? Cite
   files/commits, or mark stale.
2. SHIPPED — if the rule is meant to govern downstream agents, does it
   exist in a shipped artifact (`templates/`), or only in this repo's
   local prose? Local-only behavioral rules govern nobody.
3. ENFORCED — does any test or tool fail when the rule is violated, or
   is it prose? Name the test, or mark unenforced.
4. TODAY — designing today without this ruling, what would you build?
   If different, state the difference in one sentence.

Verdict per ruling, one of: `HOLDS`, `HOLDS-UNSHIPPED`,
`HOLDS-UNENFORCED`, `STALE`, `CONTRADICTED`.

### Pass 2 — cross-cutting audits (the classes Pass 1 instances feed)

- SHIPPED/LOCAL GAP: table of every behavioral ruling vs. its shipped
  carrier. Every `HOLDS-UNSHIPPED` is a defect: propose the template
  change that ships it.
- PROSE/ENFORCED GAP: table of shipped rules vs. enforcing test. Every
  `HOLDS-UNENFORCED` gets a proposed test or an explicit
  not-worth-testing note with reason.
- LOAD-TIME vs USE-TIME: for every section and operator bullet of
  `templates/AGENTS.template.md`, classify: needed every session, or
  only at invoke time? Invoke-time content moves to a playbook with a
  one-line dispatch stub (the `drift` shape). Known candidates, not yet
  ruled on: `handoff` (flagged 2026-07-23), `plan`, `codereview`, the
  `/git` family.
- ARCHITECTURE VERDICT: after both passes, one page: does the evidence
  support incremental surgery, or a rebuild? If rebuild, the Pass 1/2
  tables are the requirements baseline; do not propose a rebuild on any
  other basis.

## Output contract

- Findings accumulate in
  `docs/superpowers/plans/2026-07-23-audit-findings.md`: one block per
  ruling with the four answers, verdict, and proposed action. Written
  for a cold agent; no chat references.
- `STALE` and `CONTRADICTED` verdicts go to the owner one at a time,
  each as: problem, proposed change, cost/risk, recommendation. Silence
  authorizes nothing.
- `HOLDS-UNSHIPPED` / `HOLDS-UNENFORCED` fixes are new scope: queue
  them; land only behind a per-item owner go.
- Bookkeeping (this plan's status line, findings file, decisions
  entries for adopted rulings) commits and pushes as work lands — no
  owner ask (2026-07-22 and 2026-07-23 rulings).

## Explicit non-goals

- No greenfield spec unless the ARCHITECTURE VERDICT step concludes
  rebuild AND the owner rules for it.
- No edits to refresh-installed copies in governed repos; all fixes go
  through `templates/` + `tools/shipped-set.json`.
- Do not re-litigate the three defects in "Why this plan exists"; they
  are fixed and serve as calibration examples of the classes.
