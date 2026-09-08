# Agent Decisions

Current rulings and constraints live here. Earlier evidence:
[decisions archive](../docs/history/decisions-archive.md).

## Decisions

### 2026-09-08 — Remove token-waste mechanisms

The owner authorized fixing the repo-wide waste audit while preserving
working behavior, forbidding unsolicited additions and self-reviews, and
retaining the AGENTS token ceiling. This supersedes prior mandatory review
schemas, format retries, automatic effort/escalation, duplicate proof runs
and paperwork. Canonical behavior: templates/playbooks/codereview.md and
openreview.md. Use every readable valid response; further model calls must
resolve material uncertainty. Preserve named reviewers, permissions, pins,
substantive evidence, synchronous finding flow and repo branch policy.

Review slice: 222 tests passed; removed four tests pinning superseded
review schemas/routing prose. Implementation continues in .agents/state.md;
publication follows the remaining changes and checks.

Governance slice removes automatic catchup agents, mandatory fresh-agent
rehearsals, repeated answers/approvals, empty forms and duplicate inventories.
Legacy replacement uses the existing force plan/apply path in one commit.
These source procedures supersede their former rituals; installed copies
remain owner-managed. AGENTS: 770→711 o200k / 768→710 cl100k tokens.
Template checks: 37 passed; two tests enforcing automatic cleanup delegation
were removed. Other changes remain in progress.

Runner/test slice: refresh plans pin affected inputs instead of unrelated
HEAD/dirty state, stdout plans parse directly, historical notes stay quiet,
noninteractive setup reuses its caller, and publication resumes failed
pushes. Git fixtures are isolated; readable plan status and proportional
verification replace formatting gates. Outgoing hashes are automated by
tools/record-history.py. Final suite: 223 passed; diff check passed.
Regression tests demonstrated the prior unnecessary plan refusal, failed
publish retry and mixed JSON output, then passed with their fixes.
Shipped Markdown: 18,641→8,911 o200k tokens. All adapter/seed/retirement
targets are preserved. Earlier evidence is archived verbatim.
