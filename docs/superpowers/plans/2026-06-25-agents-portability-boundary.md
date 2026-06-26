# Plan: AGENTS.md portability + write-authority boundary (three layers)

**Status:** Draft, awaiting owner approval to implement
**Date:** 2026-06-25
**Spec:** `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`

## What this plan covers

All three enforcement layers from the spec, in one plan — because the layer-2
hook was validated before planning (see Evidence), removing the reason the spec
split it off. The spec's "layers 1+3 are the backbone, layer 2 is a deferred
bonus" framing is **superseded by the evidence** and reframed here (see Reframe).

Out of scope (still separate follow-on specs, unchanged): retroactive cleanup of
already-bootstrapped repos with non-portable `AGENTS.md`.

## Evidence (layer-2 validation, 2026-06-25)

Validated in a throwaway `~/Dev/testrepo` (now discarded) with the real hook
shapes. Success bar set by owner: **fires + visible + non-blocking.**

- **Mechanism proven** on Codex and on a non-Anthropic open model (GLM-5.2 via
  Claude Code): the `PreToolUse` hook fires on an `AGENTS.md` edit, injects a
  model-visible reminder carrying a unique token (`AGENTS-TRIPWIRE-7F3A`) via
  `hookSpecificOutput.additionalContext`, and does **not** block (exit 0). Both
  harnesses' models quoted the token back verbatim; edits proceeded.
- **Divert observed once:** GLM wrote a non-portable line into `AGENTS.md`, the
  hook fired, and the model read the notice, recognized the leak, and
  **self-reverted**. This is the only run where the tripwire changed an outcome.
- **Layer 1 alone steered every capable model:** across three escalating baits,
  Sonnet and GLM read the invariant text and routed the repo-specific path to
  `.agents/` *before ever attempting an `AGENTS.md` edit* — so the hook never
  fired. One run even named the tripwire it never triggered.
- **Caveat, load-bearing:** the hook is **advisory, not a gate.** The same GLM
  that self-reverted in one run also rationalized past the identical notice in
  another (an explicit-instruction typo edit). Efficacy is model-judgment-
  dependent, never mechanical.

## Reframe (drift between spec and evidence — fold into spec as a plan step)

The spec calls layers 1+3 the backbone and layer 2 a bonus. The evidence inverts
the emphasis:

- **Layer 1 (invariant text) is the primary, proven steerer** — sufficient for
  capable models unaided.
- **Layer 3 (`drift` audit) is the necessary backstop** — the only layer that
  catches what 1 and 2 let through (e.g. the rationalized-past leak).
- **Layer 2 (hook) is a real-but-advisory in-the-moment nudge** — raises the odds
  of self-correction; must not be described or relied on as a guarantee/gate.

All three ship. The plan step below updates the spec's framing to match.

## Edit sites (all in `templates/AGENTS.template.md` unless noted)

Concrete line anchors verified 2026-06-25:

- Universal Invariants list ends at template line ~86 (after the `rtk` bullet,
  before `## Bootstrap Handoff` at line 88). New invariants append here.
- `drift` operator bullet: template lines 130–133.
- `templateVersion` stamp: template line 2. Read by
  `tools/discover.py:extract_template_version` (line 278), consumed by the
  `agentsTemplate` manifest block (line ~295). Tests in `tests/test_discover.py`.
- This repo's own `AGENTS.md` is a **frozen instance — not edited** (same handling
  as the 2026-06-25 stall-not-length decision).

## Slices (one commit each, per Git Safety)

### Slice 1 — Layer 1: portability + write-authority invariants
- Append two Universal Invariants to `templates/AGENTS.template.md` after the
  `rtk` bullet:
  1. **Portability:** AGENTS.md is governance-only and must survive being copied
     into an unrelated repo unchanged; repo-specific facts (paths, names, state,
     verification commands) live in `.agents/`, AGENTS.md points to them. Lead
     with the falsifiable test ("would this line be true and useful in an
     unrelated repo?"). Include the carve-out: references to the toolkit's own
     standard layout (`.agents/state.md`, `procedures/bootstrap.md`, operator
     names) are portable and allowed.
  2. **Write-authority:** AGENTS.md is written only by a gated bootstrap or update
     run; outside such a run a repo-specific fact discovered mid-task goes to
     `.agents/`, not into governance.
- Keep terse (these inject every session).

### Slice 2 — Layer 1: bump templateVersion + prove discovery reads it
- Bump the `<!-- templateVersion: -->` stamp (line 2) to the new date.
- Verification: `python3 -m unittest discover -s tests -v` + a functional check
  that `extract_template_version` returns the bumped value. If no test currently
  asserts a specific stamp value, add one and prove it bites (revert-the-bump →
  test fails). Per AGENTS.md, a new test must be shown to guard its change.

### Slice 3 — Layer 3: extend the `drift` operator wording
- Extend the `drift` bullet (lines 130–133) to name `AGENTS.md` portability and
  write-authority as explicit drift targets. Per spec open-question 2: lead with
  the portability **test** as the durable rule; carry the accept/flag examples as
  *illustration*, not an enumerated leak list that rots.
  - **Flag (relocate):** concrete app source paths, the repo's own name as a fact,
    a specific verification command, sentences restating state/decisions another
    doc owns.
  - **Allow:** toolkit-standard layout refs, operator names, invariant prose,
    pointers *to* `.agents/`.

### Slice 4 — Layer 2: hook templates (Claude Code + Codex)

**Design correction (found during planning, supersedes the spike's hook shape).**
The spike validated a *bash script* that reads stdin and branches on the path. But
the toolkit's existing re-ground hooks are deliberately **inline `echo`, no external
script, no baked path** (`procedures/bootstrap.md` Hook section) — a load-bearing
portability contract (same file on every OS; `echo` exists in sh/cmd/PowerShell).
A bash-script hook would break that. Two facts resolved it:

- **Claude Code supports a scriptless path-scoped hook.** A `PreToolUse` handler
  with `if: "Edit(AGENTS.md)"` (plus a parallel `Write(AGENTS.md)` handler — the
  `if` field holds exactly one rule, no `|`) fires only on AGENTS.md, so the
  command stays a plain inline `echo`. **No script** — stays fully within the
  existing hook discipline. (Confirmed against CC hooks docs, 2026-06-25.)
- **Python 3 (stdlib) is already a hard toolkit prerequisite** (README/usage.md;
  `discover.py`). So *if* a harness needs a script to path-branch, it is a
  **stdlib-python** script (not bash) — zero new dependency, inherits the
  documented Windows handling (`py -3`/`python3`). Never bash.

Shape (decided 2026-06-25): **one stdlib-python tripwire script, both harnesses
point at it.** Codex has no scriptless path matcher (matcher is tool-name only,
confirmed against Codex hooks docs 2026-06-25), so a script is required there
regardless; CC *could* use a scriptless `if: "Edit(AGENTS.md)"` inline echo but
deliberately shares the one script instead — less surface, one mechanism, and it
is the exact form the spike validated as model-visible (script + stdin +
`hookSpecificOutput.additionalContext`). Owner decision: single python script.

  - **The script** (stdlib only, `#!/usr/bin/env python3`, Windows via the
    documented `py -3`/`python3` story): read the one JSON object on stdin, check
    **both** `tool_input.file_path` (CC's Edit/Write) **and** `tool_input.command`
    (Codex's apply_patch patch body) for an `AGENTS.md` target; if matched, print
    `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext":
    "<reminder>"}}` and exit 0; otherwise print nothing, exit 0. Never
    `permissionDecision: deny`, never exit 2 (both block). This merges the two
    half-scripts the spike already validated.
  - **Claude Code:** `templates/hooks/claude/settings.json` gains a `PreToolUse`
    block, matcher `Edit|Write|MultiEdit`, command invokes the python script.
    Merges alongside the existing `SessionStart` re-ground hook (bootstrap.md
    requires merge, not replace).
  - **Codex:** `templates/hooks/codex/hooks.json` gains a `PreToolUse` block,
    matcher `apply_patch|Edit|Write`, command invokes the same python script
    (resolved from git root, per Codex docs).
  - **Script location:** ship under `templates/hooks/<harness>/` mirroring the
    target path each harness expects; the bootstrap procedure copies it like the
    other hook configs. (One canonical script body, copied per-harness — keep the
    two copies identical, or house one shared script both configs reference;
    settle in implementation, prefer one body.)
- **Validation status:** the script + `additionalContext` form *is* the spike-
  validated, token-confirmed-visible form on both Codex and CC-via-GLM. No new
  unvalidated delivery path is introduced by this decision (this is why it was
  chosen over CC-inline).
- Reminder text: terse (fires on every AGENTS.md edit), states both rules, asks
  the model to confirm this is a bootstrap/update run before proceeding. (The
  `AGENTS-TRIPWIRE-7F3A` token was a test artifact — **not** shipped.) Single-
  quoted `echo`: keep ASCII, no apostrophes (bootstrap.md hook-quoting rule).
- Wire into the bootstrap procedure's hook install/trust guarantees the same way
  the re-ground hook is (trust-gated, inert until trusted). The Hook section of
  `procedures/bootstrap.md` currently says "the hook command is an inline `echo`
  with no path to substitute and no shell script to install" — that line now needs
  to admit a second, path-scoped pre-edit hook (and the python fallback if Codex
  needs it). Update it.
- Grok/agy: layers 1+3 only (no pre-edit interception). Edge cases, not chased.
- **Framing in all docs:** advisory tripwire, not a gate (per Reframe + evidence).
- Grok/agy: documented as layers 1+3 only (no pre-edit interception). Edge cases,
  not chased.

### Slice 5 — Reframe the spec
- Update `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`
  to mark layer 2 **validated** (cite this plan's Evidence) and correct the
  backbone/bonus framing to L1-primary / L3-backstop / L2-advisory. Resolve spec
  open-question 1 (Codex syntax — confirmed by live test). Note open-question 3
  (governance-lint vs. drift-judgment) stays deferred.

## Verification (required — template content discover.py copies)

- `python3 -m unittest discover -s tests -v`
- `git diff --check`
- Functional: `extract_template_version` reads the bumped stamp (Slice 2).
- The hook scripts were validated live during the spike; re-running that live
  validation is **not** part of this plan's automation (the shapes are fixed).
  Note in the final response that live re-validation was not re-run.

## Open questions for owner before implementing

1. Confirm folding all three layers into this one plan (vs. spec's split). The
   evidence supports it; flagging because it overrides the spec's structure.
2. Slice 4 (hook templates) is the only slice that adds shipping artifacts on the
   strength of a throwaway-repo validation. Acceptable, or hold Slice 4 for its
   own commit-and-verify pass after 1–3 land?
3. Decision record: owner chose "fold evidence into the plan, defer the standalone
   decision." Confirm no separate `.agents/decisions.md` entry is wanted, or add
   one when the plan lands.
