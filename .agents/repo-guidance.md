# Repo-Specific Guidance

## Mission Detail

AgentGovernanceBootstrap is the development source for Bixi, the public
governance toolkit. Entry points: `tools/new-project`, `tools/refresh.py`,
and `tools/publish`. Product guidance ships from `procedures/` and
`templates/`; `tools/shipped-set.json` owns the installed set.

The owner plans to make this development repo private.
Feedback arrives on Bixi's public issues. Assess each issue here and obtain
its own implementation go; a general “fix them” is not batch authority.
Fixes reach Bixi through publish. Guidance must help fresh sessions produce
validated work without conversation history.

## Reading Order

Start with AGENTS.md and state.md. Then read task-relevant sources:
`README.md`, `docs/usage.md`, `docs/design.md`, and the affected
procedures, templates, tools and tests. Read
`docs/harness-capabilities.md` for adapter or reviewer transport work.

`docs/history/` and `docs/superpowers/` are provenance unless state.md
identifies an active plan or the owner requests historical review.

## Verification

Use the Python 3.10+ interpreter resolved by bootstrap Step 1's probe order;
machine paths live in `.agents/machines.md`. On Windows prefer `py -3`;
reject Store stubs and below-floor interpreters. Test subprocesses inherit
the invoking interpreter.

Run affected tests after code or behavioral guidance changes; run the full
suite before publication or when changes cross test boundaries:

```bash
<probed-python> -m unittest discover -s tests
```

Documentation-only changes require `git diff --check`. Plan edits also run
`<probed-python> -m unittest discover -s tests -p test_plan_lint.py`.
Reuse passing checks on unchanged code. Capture routine output; report
failures or the concise result.

## Remotes & Sync

- Canonical: `https://github.com/roethlar/AgentGovernanceBootstrap.git`.
  Canon propagates through GitHub pushes.
- Trusted LAN fetch fallback: `http://q:3000/michael/AgentGovernanceBootstrap.git`.
  Expected mirror lag is not a conflict; the mirror is not authoritative.
- Public product: `https://github.com/roethlar/Bixi.git`. Release with
  `tools/publish`; batch releases rather than publishing each fix.
  That tool records its checkout path in `.agents/machines.md`.
- Push policy: `.agents/push-policy.md`.

## Earned Practices

- The AGENTS template stays one line per paragraph/bullet. Its token count
  must not grow: additions displace less valuable wording. Measure with
  the same tokenizer before and after; preserve rule-change provenance.
- Work compact-but-equivalent: targeted reads, scoped searches, no rereading
  unchanged files. A discretionary output filter is lossy; never install
  one as an automatic command-rewrite hook.
- Agents change toolkit sources, never this repo's installed governance,
  by hand or through any toolkit tool. Self-refresh is owner-only.
  Installed copies may lag; do not repair that lag.
  The owner runs `<probed-python> <product-clone>/tools/refresh.py <this-repo>`
  from the Bixi clone, after publishing if necessary. This repo's refresh
  script refuses self-targeting without an override; that guard stays.
- Do not add per-turn instruction injections.
- Finish objective fixes and bookkeeping within approved scope without
  ceremonial re-approval. Ask for unresolved choices only. Write plan
  documents only when the owner invokes `plan`.
- Reviewer dispatch follows the shipped review playbooks. For codex,
  pipe prompts through stdin; the argv prompt form has hung.
