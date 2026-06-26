# AGENTS.md portability boundary: governance-only, enforced

**Status:** Implemented 2026-06-25 (layers 1–3 landed; see
`docs/superpowers/plans/2026-06-25-agents-portability-boundary.md` for the plan,
the layer-2 validation evidence, and the framing correction below).
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

**The test allows the toolkit's own standard paths.** A reference to a governance
path that travels with the toolkit — `.agents/state.md`, `.agents/decisions.md`,
`procedures/bootstrap.md`, an operator name — *is* portable: it is true in every
bootstrapped repo, so it passes. What fails is a path/name/fact unique to *this* repo:
a concrete application source path (`src/api/handlers/auth.py`), the repo's own
project name, its specific verification command, a restatement of its current state.
Refined test: a line is repo-specific (and misplaced) if it names something true only
of this one repo; it is governance (and allowed) if it is true of any repo the toolkit
governs, including references to the toolkit's own standard `.agents/`/`procedures/`
layout.

The toolkit's own `templates/AGENTS.template.md` is the portable artifact by
construction; this rule makes that property explicit and required of every generated
`AGENTS.md`, not just the template.

## The write-authority rule

Portability governs *what content* belongs in `AGENTS.md`. A second, complementary
rule governs *when it may be written at all*:

> **`AGENTS.md` is written only by a bootstrap or update run, through the approval
> gate.** The sanctioned writers are exactly two, both gated: (1) a greenfield/
> migration bootstrap run that drafts the initial `AGENTS.md`, and (2) the update
> route that *reconciles* a stale `AGENTS.md` against the current template
> (`procedures/bootstrap.md`). Both pass through the approval summary and land in one
> scoped commit. Outside such a run, no agent edits `AGENTS.md` — a repo-specific fact
> discovered mid-task goes to `.agents/`, not into governance. An `AGENTS.md` edit
> proposed outside a bootstrap/update run is out of bounds, to be questioned, not
> performed.

This pairs with portability: even content that *would* be portable does not get
hand-edited into `AGENTS.md` during ordinary work; it enters only through the gated
drafting/reconciliation path. The two rules together close both halves — wrong content
*and* wrong moment.

## Enforcement — three layers, by harness capability

> **Framing correction (2026-06-25, from validation evidence).** This section
> originally called layers 1+3 the "backbone" and layer 2 a deferred "bonus." Live
> validation inverted the emphasis and the plan reframed it: **layer 1 (invariant
> text) is the primary, proven steerer** — across three escalating baits, Sonnet and
> GLM read the rule and routed the repo-specific fact to `.agents/` *before* ever
> reaching for `AGENTS.md`, so the hook never had to fire. **Layer 3 (`drift` audit)
> is the necessary backstop** — the only layer that catches what 1 and 2 let through
> (a model can read the layer-2 reminder and rationalize past it; one did). **Layer 2
> (the hook) is a real but advisory in-the-moment nudge** — it fires, is model-visible,
> is non-blocking, and was observed to make a model self-revert a leak once; but it
> raises the odds of self-correction, it does not guarantee it, and must never be
> described or relied on as a gate. All three ship. Read the layer descriptions below
> with that correction in mind.

The rule is a content judgment (is *this line* portable?), which no mechanical gate
can make — only the model reading the rule can. So enforcement is layered: a portable
text rule everywhere, an advisory pre-edit nudge where the harness supports one, and an
after-the-fact audit as the cross-harness backstop.

The harness capabilities below were established 2026-06-25 by querying each harness's
own CLI headless (`codex`/`grok`/`agy`) plus the known Claude Code behavior, then
**confirmed by live validation** (the layer-2 hook fires, is model-visible, and is
non-blocking on Codex and on a non-Anthropic model via Claude Code; Codex has no
scriptless path matcher, so the shipped hook is a stdlib-Python script). See the plan's
Evidence section.

| Layer | Mechanism | Claude Code | Codex | Grok | agy |
|---|---|---|---|---|---|
| 1. Rule | invariant text in `AGENTS.md` (every harness injects it) | ✅ | ✅ | ✅ | ✅ |
| 2. Pre-edit guard | non-blocking reminder on `AGENTS.md` edit (tripwire) | ✅ | ✅ | ❌ | ❌ |
| 3. Audit | `drift` operator finds + relocates leaks | ✅ | ✅ | ✅ | ✅ |

### Layer 1 — the invariant (portable backbone, all harnesses)

Add the boundary rule above as a Universal Invariant in
`templates/AGENTS.template.md`, and bump `templateVersion` (structural template
change → the update route reconciles stale targets). This is the only layer that
works on every harness, because every harness injects `AGENTS.md`/Rules content into
context. It is the backbone; layers 2–3 reinforce it.

### Layer 2 — pre-edit guard hook (Claude Code + Codex only)

A `PreToolUse`-style hook that fires when the agent is about to write/edit a file
whose path is `AGENTS.md`, and injects a **non-blocking, model-visible reminder** of
both boundary rules. It does **not** hard-block: a bootstrap/update run's edit is
legitimate, and a content judgment cannot be made by a path matcher anyway. Given the
write-authority rule, the hook's real job is a **tripwire** — most `AGENTS.md` edits
outside a bootstrap/update run should not be happening, so the reminder is "you are
editing AGENTS.md: this is governance-only and portable, and is normally written only
by a gated bootstrap/update run — confirm this is one." It catches both a content leak
and an out-of-band edit *as they are attempted*, where layer 3 only catches them
after.

- **Claude Code**: a `PreToolUse` hook (the repo already ships per-harness hook
  templates under `templates/hooks/<harness>/` for the re-ground hook; this is a
  second hook in the same slot).
- **Codex**: a `PreToolUse` hook in `.codex/hooks.json` or `.codex/config.toml`,
  matching `apply_patch|Edit|Write`, parsing the target path, returning the reminder
  via **`additionalContext`** (non-blocking). `permissionDecision: "deny"` is the
  blocking mode and is **not** used here. Confirmed against Codex's own hooks
  documentation (https://developers.openai.com/codex/hooks) by a Codex self-review of
  this spec, 2026-06-25.
- **Grok, agy**: no pre-edit interception exists. Documented as unavailable; these
  harnesses rely on layers 1 + 3 only. Revisit if their harnesses gain the capability.

Both hooks are **trust-gated** and **inert until trusted** (same caveat as the
existing re-ground hook); the install/trust discipline is the one already documented
in `procedures/bootstrap.md` "Hook install & trust." The reminder text must be terse
— it fires on every `AGENTS.md` edit, so verbosity becomes noise. **Until the
follow-on spec validates each hook in a live trusted workspace, the layer-2 behavior
is a dependency/assumption, not a proven fact** (the repo's evidence rule).

### Layer 3 — `drift` operator audit (cross-harness backstop)

Extend the `drift` operator definition (`AGENTS.md` Operator Requests, and the
template) to make `AGENTS.md` portability and write-authority explicit drift targets:
scan `AGENTS.md` for repo-specific leakage and flag each as drift to relocate into
`.agents/` with a pointer left behind. This is the load-bearing layer for Grok and agy
(their only enforcement beyond the rule text) and a backstop everywhere.

Acceptance examples (so reviewers do not disagree on "leakage"):

- **Flag (repo-specific, relocate):** a concrete application source path
  (`src/api/auth.py:42`); the repo's own project name used as a fact; a specific
  verification command (`pytest tests/api -k auth`); a sentence restating current
  state or the decisions queue that `state.md`/`decisions.md` owns.
- **Allow (portable governance):** references to the toolkit's standard layout
  (`.agents/state.md`, `procedures/bootstrap.md`); operator names (`drift`, `handoff`);
  invariant prose; a pointer *to* `.agents/` ("see `.agents/state.md` for current
  state"). A pointer names where a repo-specific fact lives without copying it.

The mechanizable subset (concrete paths / repo-name occurrences in `AGENTS.md`) is a
candidate check for the already-queued `governance-lint` playbook (Open Decision,
2026-06-22) — noted, not built here.

## Scope of changes

- **Add** the portability invariant **and the write-authority invariant** to
  `templates/AGENTS.template.md` Universal Invariants; **bump** `templateVersion`.
- **Extend** the `drift` operator wording in `templates/AGENTS.template.md` to name
  `AGENTS.md` portability and write-authority as drift targets, with the accept/flag
  acceptance examples.
- This repo's own `AGENTS.md` is **not** edited here (frozen instance; updated only by
  a deliberate self-application run — same handling as the 2026-06-24 and 2026-06-25
  stall-not-length decisions).
- Verification is **required** (template content `discover.py` copies): `python3 -m
  unittest discover -s tests -v` plus `git diff --check`, plus a functional check that
  `discover.extract_template_version` reads the bumped stamp.

## Follow-on (separate specs, not this one)

- **Layer-2 pre-edit guard hooks** (Claude Code + Codex): a separate spec. Concerns
  the backbone does not carry — validating each hook in a live trusted workspace, the
  trust-gate/noise tradeoff, a second hook template per harness. The backbone (layers
  1 + 3) ships independently and is useful on its own.
- **Cleanup reconciliation for existing bad `AGENTS.md`**: a separate process to
  detect and repair already-bootstrapped repos whose `AGENTS.md` carries
  repo-specifics — relocating the leaked content into `.agents/` and leaving pointers,
  through the gated update-route reconciliation. This spec defines the *rule* and the
  *forward* enforcement; retroactive cleanup of existing offenders is its own design
  (it intersects the 2026-06-22 update-route reconciliation machinery).

## Non-goals

- No hard *block* of `AGENTS.md` edits — the edit is legitimate; the goal is to keep
  its *content* portable, a judgment only the model makes.
- No reliance on any one harness's gate as the rule's enforcement — the cross-harness
  rule (layer 1) is the primary enforcement; the layer-2 hook is an advisory nudge
  where available, never the thing relied upon.
- Not re-litigating the `state.md`↔`decisions.md` duplication (that is the existing
  anti-enumeration invariant; this spec is about `AGENTS.md`↔`.agents/`).

## Open questions for planning

1. ~~Verify the Codex `PreToolUse` hook syntax.~~ **Resolved & validated live
   (2026-06-25).** Codex `PreToolUse`, matcher `apply_patch|Edit|Write`, target path
   in `tool_input.command` (the patch body), non-blocking reminder via
   `hookSpecificOutput.additionalContext`, exit 0. Confirmed against Codex's own hooks
   docs and exercised in a live run. Codex has **no** scriptless path matcher (matcher
   is tool-name only), so the shipped tripwire is a stdlib-Python script, not an
   inline echo.
2. ~~Exact `drift`-operator wording.~~ **Resolved.** Lands as implemented: lead with
   the portability *test*, accept/flag examples as illustration, not an enumerated
   leak list. See the `drift` bullet in `templates/AGENTS.template.md`.
3. **Still deferred.** Whether the mechanizable path/name scan lands in
   `governance-lint` (Open Decision, 2026-06-22) or stays an agent-judgment `drift`
   step. Not built here; the `drift` step is agent-judgment for now.
