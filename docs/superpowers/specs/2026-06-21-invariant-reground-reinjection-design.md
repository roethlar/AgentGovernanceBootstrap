# Design: Harness-portable invariant re-grounding and re-injection

Date: 2026-06-21
Status: Draft for owner review (no implementation started)
Resolves: Open Decision 2026-06-20 — "Load-bearing invariants need forceful
enforcement, not just statement"
Updated 2026-06-21 after cross-harness review (Grok, Codex, agy) and live validation.

## 1. Problem

The canon's load-bearing invariants — words-first, the owner-gate on
commit/push/merge/history-rewrite, and (new) plan-first — are stated once, in
prose, in a long `AGENTS.md`, and rely on the agent holding them in working
memory. That memory degrades as a session runs long and context compacts, so the
invariants fail exactly when the session is most complex. A 2026-06-20 incident
proved it: in a long session an agent answered owner questions with edits,
commits, and pushes.

The rejected fix was "add more in-context text" (a re-asserted block, a
behavioral checklist): theater that hardens the failing layer (in-context
attention) and spends tokens, which deepens the pressure that causes the lapse.

## 2. Reframe

Two principles, both confirmed by the evidence below:

1. **Teeth belong in deterministic surfaces — the harness and git — not model
   discipline.** The reliable signal for context degradation is the harness's
   token counter, never the model's self-assessment. The hard backstop for
   durable harm is the owner-gate plus git reversibility.
2. **Design for re-grounding from durable files, not perfect retention.** Make
   re-reading the canonical invariants cheap and automatic, triggered by the
   harness; prefer a fresh session when degraded.

Not docs-only: the durable-file principle is the floor; harness hooks are the
teeth. Both ship in the product. **Leanness is a hard requirement, not style** —
lean invariants survive compaction and Codex truncates `AGENTS.md` past 32 KiB
(§5). All new text is held to that bar.

## 3. Evidence base (verified + validated 2026-06-21)

Probed Claude Code (docs) and, headless, Grok 0.2.56, Codex 0.141, agy /
Antigravity 1.0.x; then **validated live** in interactive sessions per harness.

| Capability | Claude Code | Grok | Codex | agy |
|---|---|---|---|---|
| Model self-reports context | No | No | No | No |
| Harness tracks context | `/context` | `/context`, 85% configurable | yes, not model-visible | `/usage`,`/quota` |
| Reads `AGENTS.md` natively | via `CLAUDE.md` `@import` | Yes | Yes | Yes (+`GEMINI.md`, `.agents/`) |
| Compaction hook | `SessionStart`(+`compact`) | `PreCompact`/`PostCompact` (no matchers) | `SessionStart` src `compact` | `SessionStart`; post-compaction re-fire unverified |
| Re-inject after compaction | Yes (`additionalContext`) | annotation only (softer) | Yes (dev context); `PostCompact` stdout ignored | stdout injects to context; post-compaction re-fire to verify |
| Hook trust gate | frictionless in test | silent (`/hooks-trust`) | native startup prompt | `trustedWorkspaces` (launch prompt / `/config`) |

Convergent facts:
- **No model self-reports context** — dead everywhere.
- **A standing `AGENTS.md` survives compaction on all four** — the floor is
  portable.
- **No harness pins files natively after compaction; all-but-agy can via a hook**
  — teeth are per-harness, not one artifact.
- **"Question vs directive" classification is infeasible** — no behavioral gate.

Per-harness corrections from review:
- **Codex** (was "TBD"): confirmed. `SessionStart` src `compact` → developer
  context / JSON `additionalContext`; config `.codex/hooks.json`; `PostCompact`
  stdout is **ignored** for context. Reads `AGENTS.md` only up to
  `project_doc_max_bytes` (32 KiB default) — content below is truncated.
- **Grok**: lifecycle events **reject matchers**; compaction uses dedicated
  `PreCompact`/`PostCompact`; hook output is **scrollback annotation**, not
  structured injection (softer teeth). Reads `.claude`/`.cursor` hooks via a
  compat layer (toggleable).
- **agy** (corrected): hooks in `.agents/hooks.json`; `SessionStart` exists and its
  `type: command` stdout is prompt-injected into context (re-ground trigger works).
  Trust gate is `trustedWorkspaces` in `~/.gemini/antigravity-cli/settings.json`
  (first-launch prompt or `/config`); the agent **cannot** self-trust. Our test hook
  stayed inert only because the workspace was untrusted — the gate working, not an
  absence of hooks. Open: whether agy has a *targetable post-compaction* event
  (its event list omitted one; "separate compaction lifecycle paths" is vague) —
  verify empirically.

## 4. Validation (live, 2026-06-21)

Throwaway repos with a benign session-start hook + the trust block in
`AGENTS.md`, run interactively per harness.

- **Floor works, all four.** Each agent read `AGENTS.md` natively and obeyed
  words-first/act-only-on-go — including agy under a *natural* task ("add a
  README"): it drafted the file and refused to write it without an explicit go.
- **Trust gate behavior differs:** Codex prompts natively at startup; Grok's gate
  is silent; Claude ran the committed hook with no friction; agy ran nothing.
- **Agent-side trust-surfacing is soft.** Under a natural task agy did not flag
  untrusted hooks (it treated configs as data). So trust handling must lean on
  **harness-native gates + human confirmation**, with the agent line as a
  supplement only.
- **Cross-harness contamination is real but fixable by wording.** With
  Grok-specific *examples* in `AGENTS.md`, agy tried to create a `.grok/` folder
  (acting on the wrong harness). With **harness-neutral wording** and all four
  configs co-present, agy stayed in its `.agents/` lane and touched nothing
  foreign.
- **Models can be confidently wrong about their harness** (Grok's default model,
  Composer, reports it is in Cursor). So agent instructions must not depend on the
  model self-identifying its harness; the human knows it even when the model
  doesn't.
- **Hook stdout is an injection vector.** Claude correctly refused to treat the
  hook's printed "Prime Invariant" as authoritative ("hook stdout is untrusted").
  Re-injecting verbatim invariants both creates an attack surface and fights a
  well-behaved model's own safety instinct. → drives §4.3.

## 4.1 Canonical Prime Invariants block

Restructure `templates/AGENTS.template.md` into:
- **Prime Invariants** — a short, marker-delimited block **at the very top** (so
  Codex's 32 KiB cap never truncates it), the single canonical home of the
  hardest-to-reverse rules. **Approved verbatim 2026-06-21:**

  ```
  ## Prime Invariants
  <!-- prime:begin — keep terse; re-grounded after compaction -->
  These outrank everything below. After a context compaction, re-read this block from AGENTS.md before continuing.

  - Words first. Answer questions and musings in words; act only on an explicit
    instruction or go. A handed-over report, plan, or spec is evidence to assess,
    not a decision to implement.
  - No code change without an approved plan; docs and other non-code edits don't
    need one (e.g. a README). When unsure, treat it as code.
  - Commit each slice as it lands; never leave finished work uncommitted. Push,
    history-rewrite, and destructive or outward-facing actions need an explicit
    go — pushing publishes.
  - Repo is memory. Durable truth lives in the repo, not chat or working memory.
    Under context pressure, re-ground from AGENTS.md; prefer a fresh session when
    degraded.
  <!-- prime:end -->
  ```
- **Universal Invariants** — the rest (one-canonical-location, label assumptions,
  roadblock-provenance, verification defaults, …), which *reference* the Prime
  block, never restate it.

This keeps one canonical copy and answers the earlier "second-copy" objection:
the Prime block is the relocated home of those rules, not a duplicate.

## 4.2 Floor (portable, all harnesses)

- Invariants in `AGENTS.md`, loaded natively (Codex/Grok/agy) or via the existing
  `CLAUDE.md` `@AGENTS.md` import (Claude Code). No `GEMINI.md` change: agy reads
  `AGENTS.md` natively, so a `GEMINI.md` pointer would be redundant.
- `catchup` operator sharpened to "re-read `AGENTS.md` and the Prime Invariants in
  full, then re-ground" (template + `templates/commands/claude/catchup.md`).

## 4.3 Teeth: re-grounding *trigger*, not re-injection

Refined by the injection-vector finding (§4): the post-compaction hook does **not
re-state the invariants**. It emits a short, fixed trigger — e.g. *"Context was
compacted. Re-read AGENTS.md (Prime Invariants) from disk before continuing."* —
and the model re-grounds from the canonical, trusted file. This:
- removes the injection vector (a forged "re-read your own guidance" is harmless),
- keeps one canonical copy (dissolves the old live-extract-vs-sidecar question),
- satisfies Codex's "exact text, not paraphrase" concern (model reads exact text
  from disk),
- is the leanest option (fixed string, no payload).

Per-harness hook config, all written in one bootstrap run (a harness hook is a
committed file; the repo carries configs for every harness and each self-activates
its own — no per-harness reruns):

| Harness | Path | Event | Teeth |
|---|---|---|---|
| Claude Code | `.claude/settings.json` | `SessionStart`(+`compact`) | strong (structured) |
| Codex | `.codex/hooks.json` | `SessionStart` src `compact` | strong (structured) |
| Grok | `.grok/hooks/*.json` | `PostCompact` (after compaction; PreCompact would fire before the loss) | soft (annotation) |
| agy | `.agents/hooks.json` | `SessionStart` (post-compaction re-fire TBD) | inject confirmed; verify post-compaction |

The trigger is inlined directly into each config as an `echo` command (the fixed
pointer string is the command's argument) — there is **no shared `.sh` script**.
This was a correction: the first build shipped a `sh "__REPO_ROOT__/.agents/hooks/reground.sh"`
command, which baked an **absolute path** at install (broke on clone/move) and
silently required a **POSIX shell** (broke on native Windows). Inlining kills both:
nothing to substitute, and `echo` exists in `sh`, `cmd`, and PowerShell. The one
residual is that the harness must run the hook command through a shell with `echo`
— verified on macOS; Windows is best-effort until tested. Keep the string
single-quoted and ASCII (no apostrophes) so the same JSON is valid on every shell.
When inlined, the pointer was also normalized — the old script's em-dash and
`(re)started` became ASCII commas and the wording was lightly smoothed — so it is
not byte-identical to the deleted `printf`, though the meaning is unchanged.

New product scaffolding: `templates/hooks/<harness>/` + a bootstrap install/register
step modeled on the all-routes operator-wrapper guarantee (incl. `.gitignore`
handling that keeps machine-local state like `.claude/settings.local.json` ignored).

## 4.4 Hook trust (cross-harness, machine-local)

Trust is a per-repo, per-machine security gate (Grok `~/.grok/trusted-hook-projects`
or `/hooks-trust`; Codex `/hooks` by hash; re-trust on change). It is
**uncommittable by design** — a repo must not auto-authorize its own hooks — so
the bootstrap installs configs in one run but **cannot ship trust**; there is an
irreducible one-time trust step per repo, per machine, per harness (not per
session, not per harness-switch).

Handling, in order of reliability:
1. **Harness-native gate** (Codex's startup prompt) — primary; works regardless of
   what the model thinks it is.
2. **Human confirmation** — the human knows the real harness even when the model
   is wrong (Composer/Cursor).
3. **Agent line (supplement, soft):** a **harness-neutral** note in `AGENTS.md` —
   no vendor names — "if your harness gates hooks and this one is untrusted, tell
   the user what it does, ask, and only with their go run the trust step for the
   harness you are *actually* in; never run another harness's config or trust
   commands." Validated to prevent contamination; do not rely on it firing under
   natural tasks.

Never auto-bypass the gate (e.g. silently writing the trust file) — that defeats
the boundary it exists to enforce.

## 4.5 Plan-first invariant + bad-rule removal

- Add to Prime Invariants: "No code changes without an approved plan; questions
  and exploration don't need one." (Owner: "No coding without an approved plan,"
  refined so it doesn't gate read-only work — Q2.)
- This repo's `AGENTS.md` (not the product) carries two contradicting lines —
  "Prefer implementation … over more planning" and "Do not create a new plan
  revision unless asked." Remove them via the bootstrap re-run (§7), not by hand.

## 5. Verification

- Per harness with teeth: behavioral test — force/await a compaction, confirm the
  re-ground trigger appears and the model re-reads `AGENTS.md`; cover resume and
  the trust flow. (Live first-pass done 2026-06-21; formalize for CI-able repos.)
- agy: re-confirm floor-only (no hook fires); if a working hook mechanism turns
  up, add its row.
- Toolkit's own gate: `python3 -m unittest discover -s tests -v` for changes to
  `tools/discover.py`, `tests/`, or copied `templates/`/`procedures/` content.

## 5b. Task 4 results (2026-06-21) + the standing-context finding

Manual `/compact` verification per harness:
- **Claude Code: PASS** — `SessionStart`+`compact` fired on `/compact`; trigger emitted. Teeth proven on the primary coding harness.
- **Codex: hook did not fire on manual `/compact`** — but Codex confirmed it **re-injects `AGENTS.md` after compaction natively** ("AGENTS restored by the environment"); the floor covers it, and `/compact` is likely not the hook's trigger (auto-compaction only). Redundant-but-harmless on Codex.
- **Grok, agy: left inert** (workspace not trusted) as best-effort insurance for a possible workflow shift; the floor covers them meanwhile. agy has no manual `/compact`; agy also over-applied words-first (asked for a go on direct *read* instructions) — a wording-precision observation, not a blocker.

**Key finding:** `AGENTS.md` is **standing context that survives compaction natively** (re-sent as project instructions each turn), confirmed on Codex and consistent with how Claude/Grok/agy load it. So the 2026-06-20 failure was attention degradation, not invariant *removal* — the **floor is the real guarantee**; the re-ground teeth are reinforcement/insurance, redundant where the harness already re-injects. **Decision (owner, 2026-06-21):** keep the teeth as-is — Claude benefits (proven), Codex is covered by native reload, Grok/agy stay inert-until-trusted insurance. **Security:** no concern — each config's hook command is a benign fixed-string inline `echo` (no script file); untrusted hooks don't run; once trusted (and on Claude, with no prompt) it runs with shell privileges, so changes to that command string are review-sensitive like any executable. **Portability fix (2026-06-21):** the original `sh "__REPO_ROOT__/.agents/hooks/reground.sh"` baked an absolute path (broke on clone/move) and required a POSIX shell (broke on Windows); both are resolved by inlining the trigger as `echo` (§4.3). The Task-4 test instrument hard-coded absolute paths and ran only on macOS, so it caught neither — now guarded by a test that inspects the committed config for any baked path or script/shell dependency.

## 6. Non-goals / honest limits

- Hooks are *soft* re-assertion; the *hard* catch stays owner-gate + git
  reversibility. Codex `PreToolUse` is also an incomplete action gate.
- No behavioral "question vs directive" gate.
- agy's post-compaction re-fire is unverified; Grok's teeth are annotation-soft.
  The **floor (native `AGENTS.md` + `catchup`) is the only universal guarantee**;
  teeth are best-effort where the harness supports them.
- Single-harness consolidation is a real risk (xAI/Cursor); the multi-harness,
  `AGENTS.md`-keyed, committed-to-repo design is the deliberate hedge.

## 7. Sequencing (product-first, drift-resistant)

1. Land all changes in the **product** (`templates/`, `procedures/`,
   `templates/hooks/`, the spec). Commit per git-safety rules; offer to push.
2. The owner runs **one bootstrap re-run on this repo**, which self-applies the
   restructured invariants into this repo's `AGENTS.md`, the `.claude/` wrappers
   and hook configs, removal of the two bad planning lines, and archiving of the
   resolved Open Decision. The re-run clears the queue — no hand-edited governance.

## 8. Open questions

1. ~~Prime Invariants contents~~ — **resolved 2026-06-21:** block approved verbatim (§4.1).
2. ~~Plan-first wording~~ — **resolved:** code-vs-docs line (§4.1).
3. ~~Re-injection source~~ — **resolved:** re-ground trigger, not re-injection
   (§4.3); no extraction or sidecar.
4. ~~v1 harness scope~~ — **resolved 2026-06-21:** ship hooks for all four —
   Claude Code + Codex (strong) + Grok (soft) + agy (SessionStart injection
   confirmed; post-compaction re-fire to verify during build).
5. ~~Bad-rule removal~~ — **resolved:** via the bootstrap re-run, not a hand-edit.

All open questions resolved; spec finalized 2026-06-21. Commits fold into the
first product commit (not committed separately).
