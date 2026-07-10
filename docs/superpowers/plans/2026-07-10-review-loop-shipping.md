# reviewloop: ship the review entry point; harden acceptance; scope its claims

Status: CLOSED 2026-07-10 — landed on owner approval, verbatim: "Do the
plans for the rest as well." Commit map: slice 1 shipped skill + wrapper
`77bbf60` (wrapper byte-identical to the dogfood copy, which classifies
current on the next refresh); slice 2 acceptance hardening + probe-scoped
claims + branch scoping `7295d19` (outgoing playbook hash was already in
`formerly[]`); slice 3 capability-ledger claim discipline in the commit
carrying this line (legend added; the stale "shipped hook stands" prose
reconciled with the 2026-07-09 agy retirement). Suite 103/103.

## Why this plan exists

Remaining verified findings from the 2026-07-09 external holistic review
(restated so this plan is self-contained), the review-loop cluster:

1. **The advertised entry point does not ship (review H8).**
   `templates/playbooks/reviewloop.md` advertises a `review <agent>`
   operator and a `/review` wrapper, but the shipped manifest carries only
   the playbook — no shared skill, no wrapper. The dogfood repo's own
   `.claude/commands/review.md` masks the gap: every other governed repo
   gets a playbook that names an entry point it does not have.
2. **Acceptance trusts reviewer-authored fields (review H8).** The verdict
   envelope is fail-closed in spirit, but the playbook does not require
   the orchestrator to verify `guard_confirmed == true` or that the
   reviewed base/head SHAs equal the invocation's before accepting.
3. **Portability claims outrun evidence (review H8/M3).** The playbook
   says any headless agent that returns structured JSON can participate;
   the capability ledger (`docs/harness-capabilities.md`) mixes
   last-observed, assumed, and historical claims without labels, so a
   stale claim reads as current support.
4. **Branch-policy tension (review H8).** The playbook hard-requires
   per-finding branches while the portable `AGENTS.md` says branch use is
   repository policy — recorded as an open conflict.

## Design

**Ship the entry point.** New shipped artifacts, added to
`tools/shipped-set.json` (`formerly: []`, new files):
- `templates/skills/shared/review/SKILL.md` →
  `.agents/skills/review/SKILL.md`: pointer skill — "run the `reviewloop`
  playbook (`.agents/playbooks/reviewloop.md`) with the named reviewer
  agent; the playbook is the authoritative workflow."
- `templates/commands/claude/review.md` → `.claude/commands/review.md`:
  one-paragraph wrapper with the same pointer. Base its text on the
  dogfood copy at `.claude/commands/review.md`, trimmed to a pure pointer;
  after this ships, the dogfood copy is owned by the manifest like every
  other wrapper (its current bytes join `formerly[]` if they differ from
  the shipped text, so the owner's next refresh reconciles it rather than
  flagging it).

**Harden acceptance.** In `templates/playbooks/reviewloop.md`: the
orchestrator — never the reviewer — computes acceptance, and a verdict is
accepted only when the reviewer's reported base and head SHAs equal the
invocation's pinned SHAs AND `guard_confirmed` is literally true; any
missing or mismatched field is a failed round (fail-closed), never a pass.

**Scope the claims.** Same file: replace "any headless agent that can
return structured JSON" with the probe contract — participation is
whatever the live probe (already the playbook's step 1) verifies on this
machine today; named harnesses are examples, not guarantees.
`docs/harness-capabilities.md` gets a labeling pass: every claim carries
one of `observed <date, version, command>` / `assumed` / `historical`;
recovery-command tables state they are launch shapes, not proof of
installation.

**Resolve the branch tension.** Same file: per-finding branches are
declared the loop's INTERNAL mechanics (its atomic unit and guard-proof
isolation), explicitly not a repository branch policy; whether the repo
uses branches elsewhere stays repository policy per `AGENTS.md`. This
closes the recorded conflict by scoping, not by weakening either text.

## Slices (one commit each)

1. New skill + wrapper templates, manifest entries, dogfood-copy hash
   reconciliation; suite (structural template tests) green.
2. Playbook edits: acceptance hardening, probe-scoped claims, branch
   scoping. Manifest `formerly[]` gains the outgoing playbook hash.
3. `docs/harness-capabilities.md` labeling pass (docs-only).

## Verification

Full suite per `.agents/repo-guidance.md` (Verification) for slices 1–2
(templates and manifest change); `git diff --check` for slice 3. The
shipped skill/wrapper land in governed repos via the owner's next refresh
loop; a live reviewloop round is the field bite proof and is NOT run by
this plan (dispatching reviewers costs owner-visible tokens).

## Non-goals and risks

- No change to the reviewer dispatch contract (`codex exec` + stdin
  stands per the 2026-07-09 evaluation in `.agents/decisions.md`).
- No new operator vocabulary in `AGENTS.md`: `review` remains a playbook
  invocation, discoverable through the shipped skill.
- This repo's installed copies lag until the owner's refresh (owner-only
  rule); the dogfood wrapper keeps working meanwhile.
- Risk: repos whose owners hand-edited the playbook get FLAG lines
  instead of updates on refresh — correct behavior, worth expecting in
  the refresh output.
