# Plan: retire the owner-communication level

Status: Approved (owner ruling 2026-07-25) — scrap the comms mechanism
entirely. "If it's not being used, it's not worth keeping."

## Why

The level was set to 2 in this repo and never governed a single response.
`templates/AGENTS.template.md` carries a one-line pointer ("Register follows
the repo's communication level (`.agents/comms-policy.md`)") and nothing
loads that file, so the definitions were never in context at the moment of
writing. A rule one indirection away from its point of use does not bind.
Demonstrated 2026-07-25: output ran at roughly level 4 length under a level 2
setting for an entire session, and the level only entered consideration when
the owner raised it.

The 2026-07-22 decision that introduced it is superseded by this one.

## Removal set

Shipped sources (the manifest MAINTENANCE RULE applies — append the
outgoing version's nhash to `formerly[]` in the same commit):

- `templates/AGENTS.template.md` — the register clause in `## Final
  Response`; the sentence keeps its summary-first contract and loses only
  the deferral.
- `templates/playbooks/plan.md` — the register deferral in the
  owner-decisions paragraph.

Non-shipped toolkit sources:

- `templates/comms-policy.template.md` — deleted.
- `templates/approval-summary.template.md` — the Owner Communication
  question and `.agents/comms-policy.md` in the committed-drafts list.
- `templates/repo-guidance.template.md` — the comms-level mention.
- `procedures/bootstrap.md` — Step 4 item 5 (seeding) and its renumbering.
- `procedures/setup.md` — the three references (drafts list, seeded files,
  the level question).

Tooling:

- `tools/shipped-set.json` — drop the `.agents/comms-policy.md` entry from
  `seeded[]`; `.agents/push-policy.md` stays, it is used.
- `tools/refresh.py` — the comms-marker preflight and its docstring mention.
- `tests/test_refresh.py` — the two comms marker preflight tests.
- `tests/test_templates.py` — `comms-policy.template.md` in the expected
  template list.

Repo records:

- `.agents/comms-policy.md` — deleted.
- `.agents/decisions.md` — record this ruling; the 2026-07-22 comms entry
  and its amendments become Superseded and archive verbatim to
  `docs/history/decisions-archive.md` per the archive rule. The 2026-07-25
  seeded-files entry is amended: it now covers push-policy only.
- `.agents/state.md`, `README.md`, `docs/usage.md`, `docs/design.md` — drop
  the comms references added or carried there.

Left alone: closed plan documents under `docs/superpowers/plans/` and
`docs/history/decisions-archive.md`. They are historical records of what was
decided at the time; rewriting them would falsify the archive.

## Implementation

One commit per group, in this order: templates (shipped, with `formerly[]`
appends), procedures, tooling + tests, records + docs, then the file
deletions folded into their owning commits.

The `seeded[]` mechanism itself stays — it was built 2026-07-25 for both
policy files and remains correct for `push-policy.md`. Only the comms entry
leaves. `PruneEmptyDirTests` and `SeedTests` both keep passing; `SeedTests`
uses its own fixture manifest and is unaffected.

## Verification

`<probed-python> -m unittest discover -s tests -v`, `git diff --check`,
`tools/refresh.py . --lint-only`. After the shipped-template edits, confirm
the `formerly[]` append is present by re-running the suite — the manifest
history test fails loudly on an omitted outgoing hash.
