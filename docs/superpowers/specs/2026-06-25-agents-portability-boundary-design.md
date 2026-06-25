# AGENTS.md portability boundary: governance-only, enforced

**Status:** Design, awaiting owner review
**Date:** 2026-06-25

## Problem

`AGENTS.md` is meant to be governance — portable process, invariants, and operator
definitions that ship to any repo the toolkit bootstraps. In practice, real
bootstrapped repos accumulate **repo-specific content** in `AGENTS.md` (concrete file
paths, the repo's own name, project facts, restatements of current state). That
content is true only of one repo, so a copied `AGENTS.md` is wrong elsewhere, and the
file drifts the moment the repo-specific fact changes. The `.agents/` layer
(`state.md`, `decisions.md`, `repo-map.json`) already exists to hold repo-specific
durable truth; `AGENTS.md` should point at it, never restate it.

The repo already has adjacent invariants (one-canonical-location, prefer-pointers, a
summary doesn't keep a second copy of an enumeration another doc owns), but none
states the `AGENTS.md`↔`.agents/` boundary as a single portable test, and nothing
enforces it at the moment an agent edits `AGENTS.md`.

## The boundary rule (portability test)

> **`AGENTS.md` is governance only — it must be portable.** Every line must survive
> being copied into an unrelated repo unchanged. Process, invariants, and operator
> definitions qualify. Anything true only of *this* repo — its current state,
> decisions, verification commands, file paths, project facts — does not, and lives in
> `.agents/` (`state.md`, `decisions.md`, `repo-map.json`). `AGENTS.md` *points* to
> those ("see `.agents/state.md`"); it never restates their content. If a line would
> be false or meaningless in another repo, it is misplaced — move it to `.agents/` and
> leave a pointer.

This is a falsifiable test an agent applies in the moment: *would this line still be
true and useful in an unrelated repo?* If not, it is repo-specific.

The toolkit's own `templates/AGENTS.template.md` is the portable artifact by
construction; this rule makes that property explicit and required of every generated
`AGENTS.md`, not just the template.

## Enforcement — three layers, by harness capability

The rule is a content judgment (is *this line* portable?), which no mechanical gate
can make — only the model reading the rule can. So enforcement is layered: a portable
text rule everywhere, a hard pre-edit guard where the harness supports one, and an
after-the-fact audit as the cross-harness backstop.

The harness capabilities below were established 2026-06-25 by querying each harness's
own CLI headless (`codex`/`grok`/`agy`) plus the known Claude Code behavior. They are
self-reports; the Codex hook syntax in particular must be verified against Codex's
own docs before a `.codex/` hook template ships (see open questions).

| Layer | Mechanism | Claude Code | Codex | Grok | agy |
|---|---|---|---|---|---|
| 1. Rule | invariant text in `AGENTS.md` (every harness injects it) | ✅ | ✅ | ✅ | ✅ |
| 2. Pre-edit guard | block + reiterate on `AGENTS.md` edit | ✅ | ⚠️ partial | ❌ | ❌ |
| 3. Audit | `drift` operator finds + relocates leaks | ✅ | ✅ | ✅ | ✅ |

### Layer 1 — the invariant (portable backbone, all harnesses)

Add the boundary rule above as a Universal Invariant in
`templates/AGENTS.template.md`, and bump `templateVersion` (structural template
change → the update route reconciles stale targets). This is the only layer that
works on every harness, because every harness injects `AGENTS.md`/Rules content into
context. It is the backbone; layers 2–3 reinforce it.

### Layer 2 — pre-edit guard hook (Claude Code + Codex only)

A `PreToolUse`-style hook that fires when the agent is about to write/edit a file
whose path is `AGENTS.md`, and injects a model-visible reminder of the boundary rule
(it does not hard-block — the edit is legitimate; it reiterates the test at the moment
of temptation, which is where leaks are written). This catches drift *as it is
created*, where layer 3 only catches it after.

- **Claude Code**: a `PreToolUse` hook (the repo already ships per-harness hook
  templates under `templates/hooks/<harness>/` for the re-ground hook; this is a
  second hook in the same slot).
- **Codex**: `PreToolUse` in `.codex/config.toml` / `hooks.json`, matching
  `apply_patch|Edit|Write`, parsing the target path, returning a reason as additional
  context (Codex supports `permissionDecision: "deny"` + reason; we use the
  reason/context, not a hard deny).
- **Grok, agy**: no pre-edit interception exists. Documented as unavailable; these
  harnesses rely on layers 1 + 3 only. Revisit if their harnesses gain the capability.

Both hooks are **trust-gated** and **inert until trusted** (same caveat as the
existing re-ground hook); the install/trust discipline is the one already documented
in `procedures/bootstrap.md` "Hook install & trust." The reminder text must be terse
— it fires on every `AGENTS.md` edit, so verbosity becomes noise.

### Layer 3 — `drift` operator audit (cross-harness backstop)

Extend the `drift` operator definition (`AGENTS.md` Operator Requests, and the
template) to make `AGENTS.md` portability an explicit drift target: scan `AGENTS.md`
for repo-specific leakage — concrete non-`.agents/` file paths, the repo's own name,
restatements of `state.md`/`decisions.md` content — and flag each as drift to relocate
into `.agents/` with a pointer left behind. This is the load-bearing layer for Grok
and agy (their only enforcement beyond the rule text) and a backstop everywhere.

The mechanizable subset (concrete paths / repo-name occurrences in `AGENTS.md`) is a
candidate check for the already-queued `governance-lint` playbook (Open Decision,
2026-06-22) — noted, not built here.

## Scope of changes

- **Add** the portability invariant to `templates/AGENTS.template.md` Universal
  Invariants; **bump** `templateVersion`.
- **Extend** the `drift` operator wording in `templates/AGENTS.template.md` (and this
  repo's `AGENTS.md` only via deliberate self-application, per the frozen-instance
  rule) to name `AGENTS.md` portability as a drift target.
- This repo's own `AGENTS.md` is **not** edited here (frozen instance; updated only by
  a deliberate self-application run — same handling as the 2026-06-24 and 2026-06-25
  stall-not-length decisions).
- Verification is **required** (template content `discover.py` copies): `python3 -m
  unittest discover -s tests -v` plus `git diff --check`, plus a functional check that
  `discover.extract_template_version` reads the bumped stamp.

## Follow-on (separate spec, not this one)

The **layer-2 pre-edit guard hooks** (Claude Code + Codex) are a separate spec. They
carry concerns the backbone does not: verifying the Codex hook syntax against Codex's
docs, the trust-gate/noise tradeoff, and a second hook template per harness. The
backbone (layers 1 + 3) ships independently and is useful on its own.

## Non-goals

- No hard *block* of `AGENTS.md` edits — the edit is legitimate; the goal is to keep
  its *content* portable, a judgment only the model makes.
- No reliance on any one harness's gate as the rule's enforcement — the cross-harness
  rule is the invariant; hooks are a bonus where available.
- Not re-litigating the `state.md`↔`decisions.md` duplication (that is the existing
  anti-enumeration invariant; this spec is about `AGENTS.md`↔`.agents/`).

## Open questions for planning

1. Verify the Codex `PreToolUse` hook syntax against Codex's own documentation before
   shipping a `.codex/` hook template (self-report says
   https://developers.openai.com/codex/hooks).
2. Exact `drift`-operator wording: how prescriptive to make the "repo-specific
   leakage" definition without it rotting (portability test vs. an enumerated list of
   leak types).
3. Whether the mechanizable path/name scan lands in `governance-lint` (Open Decision)
   or stays an agent-judgment `drift` step for now.
