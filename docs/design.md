# Design

Bixi keeps durable project knowledge in the repository and binds agent work
to explicit owner authority. This development repo is the source; the
public release is Bixi. Operative rules live in the shipped
`templates/AGENTS.template.md` and `templates/playbooks/`.

## Ownership and authority

`AGENTS.md` is portable and refresh-governed. Repo-specific guidance and
records live under `.agents/`; the more specific rule wins. Harness files
adapt discovery and invocation only. Keep each rule in one home; other
surfaces point to it.

**No shipped rule without provenance.** Add or change a rule only with a
decision entry citing its earning incident or owner ruling. Once the rule
has an operative home, archive its rationale verbatim. The template's
token ceiling lives in `.agents/repo-guidance.md`.

## Bootstrap and refresh

`procedures/setup.md` creates initial project guidance.
`procedures/bootstrap.md` discovers an existing repo, reconciles its
governance, drafts repo-owned files and presents one approval summary.
The legacy carve-out requires two announced commits; the standard route
uses one. `procedures/verification.md` checks discoverability and
consistency; external claims need separate evidence.

`tools/refresh.py` owns deterministic installation.
`tools/shipped-set.json` defines sources, destinations, replacement and
retirement rules, historical hashes and repo-owned seeds. Dirty target
paths refuse; known versions update; committed drift is restored with
provenance. Foreign governance follows the documented replacement or
migration route. Plan/apply checks guard the approved snapshot.
Bootstrap drafts judgment files, never hand-copies shipped artifacts.

Refresh commits installation; it does not certify task completion.
Agent implementation follows the git playbook's branch setup and closeout.
Verification, integration and branch deletion stay pending until satisfied.

## Harness adapters

Adapters ship only after a live mechanism check.
`docs/harness-capabilities.md` records dated, version-scoped evidence and
labeled assumptions. The compaction hook re-grounds supported harnesses;
the edit guard protects installed artifacts. Neither replaces the
constitution or refresh reconciliation.

Wrappers and skills point to canonical procedures. Review transport,
permissions, pins and provenance live in the codereview playbook;
openreview changes the question and verdict schema.

## Feedback and freshness

Confirmed defects and incident-earned rules go to Bixi's public issues
with explicit filing authority and redacted evidence. Templates live in
`.github/ISSUE_TEMPLATE/`; procedures carry the filing steps.

Git owns freshness. Check remote refs before trusting recorded state;
unreachable remotes get a caveat. Publishing propagates approved toolkit
changes. Historical plans and decisions are provenance, not a second
current rulebook.
