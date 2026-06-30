# Adopt the edit-failure refocus hook + completeness prose into the product

Status: DRAFT v2 2026-06-30 — codex-reviewed (2 blockers + 3 should-fix folded). Not approved, no code. Plan only.
Scope: add two artifacts to the **product** (the toolkit's `templates/` + `procedures/`
that bootstrap *other* repos). Explicitly **not** this repo's own `AGENTS.md`/`.agents/`.

## Why this plan exists

Owner decision (2026-06-30): model testing is closed (expensive, diminishing returns).
Two artifacts produced during it are adopted and should ship in the product:

1. A **Claude Code `PostToolUseFailure` hook** that, when an edit fails, injects a system
   reminder so the model re-applies its *complete* intended change instead of silently
   dropping logic on the re-author.
2. The **`completeness-general` guidance** ("Making code changes") — fix the underlying
   defect everywhere it occurs, and nowhere else.

## Evidence (so the adoption is informed, not assumed)

These are adopted as **deliberate judgment calls**, not proven wins. What the experiments
actually showed:

- **Prose (`completeness-general`):** valid result only on a weak local model (qwen):
  helped where the incomplete-patch failure mode genuinely occurs (`py_vault_twopath`
  0/3 → 2/3) but **hurt once** on a ceiling fixture (`go_topk` 3/3 → 2/3). On strong
  subscription harnesses it was **null**: grok flips were run-to-run variance (same-scope
  patches); Sonnet 5 failed a hard instance and B produced a same-10-file patch that still
  failed. Strong harnesses already emit broad-coverage patches — they don't make the
  error this prose targets. So: low-cost, real on weak models, no measured benefit (and a
  small harm risk) on strong ones.
- **Hook:** **untested.** Adopted on *mechanism plausibility*, not measurement. The
  failure mode it targets is real and specific (the papers' worst case: edit rejected →
  re-author → silently drop logic; refined by owner: the drop is a model **attention**
  lapse at re-author, which Cursor's apply-model architecture never triggers). The hook
  capability is verified against current Claude Code docs (`PostToolUseFailure` fires on a
  failed tool call; `additionalContext` injects a system reminder, ≤10k chars). Whether it
  *recovers* dropped logic is unmeasured — see "Future validation."

This honesty must survive into whatever durable note the implementation leaves; do not let
the product imply either artifact is a measured win.

## Artifact 1 — the edit-failure refocus hook (Claude Code)

**The injected message (settled with codex):**
> The edit failed. Address the cause, then retry the full intended change without dropping
> or simplifying any part.

**Where it goes** (mirrors the existing tripwire hook pattern):
- `templates/hooks/claude/settings.json` — add a `PostToolUseFailure` entry under `hooks`,
  matcher `Edit|Write|MultiEdit`, invoking a script (mirror the tripwire's
  `PreToolUse` → `agents-md-tripwire.py` shape).
- `templates/hooks/claude/edit-refocus.py` (new) — emits the static `additionalContext`
  JSON, exits 0 (advisory, never blocks), portable invocation (`python3`, no absolute
  paths), exactly like `agents-md-tripwire.py`.

**Harness scope — Claude Code only (for now).** `PostToolUseFailure` is a Claude Code
event. The bootstrap drafts every shipped harness's hook directory into a target repo
regardless of which harness runs the bootstrap (`procedures/bootstrap.md` "Hook install &
trust", ~L196/L219), so target repos still receive the `.claude/` profile — Codex/Grok/Agy
simply get **no equivalent failure hook**, since their configs have no such event. Codex has
`apply_patch`/edit tooling and may have an analogous event; grok/agy unknown. **Open
decision H1:** ship Claude only now, or also research codex/grok/agy failure-hook
equivalents this pass. Recommend Claude only; file the others as follow-up.

**Install:** automatic. `discover.py` copies `templates/hooks/` wholesale into
`.bootstrap-tmp/templates/hooks/`; `procedures/bootstrap.md` drafts
`.claude/settings.json` + adjacent scripts. Adding files under `templates/hooks/claude/`
requires **no** new install step — only a settings.json merge note already covered by the
existing "merge with existing settings" guidance.

**Tests:** extend `tests/test_discover.py`:
- Add a `PostToolUseFailure` row to the hook schema asserting the Claude config carries the
  event + matcher; assert `edit-refocus.py` is present, adjacent, and portable (no
  `/home/`-or-`/Users/`, `python3` invocation) — mirror
  `test_hook_configs_present_copied_and_portable` (L443).
- **Behaviorally execute the script** (mirror `test_tripwire_hook_present_advisory_and_portable`,
  L491): run `edit-refocus.py`, assert exit 0, output is valid JSON with
  `hookSpecificOutput.hookEventName == "PostToolUseFailure"` and a non-empty
  `additionalContext`, and **no blocking fields** (advisory only).
- Prove the test guards the change (revert the settings entry → test fails → restore).

## Artifact 2 — the completeness guidance (placement is the real decision)

**The settled wording (`completeness-general`, 3 bullets):** "When fixing a problem, fix
the underlying defect, not just the place you first noticed it… apply the fix everywhere
the same cause genuinely applies, and nowhere else… verify every place the same cause
could occur was fixed or ruled out."

**The relevant invariant** (`templates/AGENTS.template.md:87`): **AGENTS.md is governance
only and must be portable** — the test is "would this line be true and useful in any repo?"
It *admits* process, invariants, and operator definitions that pass; it excludes repo-specific
content (paths, the repo's name, verification commands, state). Two corrections to my first
draft: (a) this invariant's prose is **not** unit-tested — `tests/test_discover.py` covers hook
portability and AGENTS template versioning/reconciliation, not the governance-only text, so
calling it "tested" overclaims; it's enforced by review and the `drift` operator. (b) There is
**no `_parts/` snippet mechanism** in the product (that's eval-only).

The completeness wording *passes* the portability test, so it is **not forbidden** from
AGENTS.md. G1 is therefore a genuine **tradeoff, not a prohibition** — **Open decision G1
(owner picks):**

- **Option A — new Universal Invariant line in `AGENTS.template.md`.** The wording passes the
  portability test, and the Universal Invariants already hold quality-discipline rules (verify
  before claiming done; don't circumvent roadblocks), so a condensed completeness/restraint
  invariant fits in *kind* — it is permitted, not a stretch. Pros: lands directly in the agent's
  read context (where it had effect in the eval); no new file or install step. Cons: **condenses
  the 3-bullet wording into invariant form** (no longer the verbatim "prose we settled on"); adds
  a line to the core governance (minimalism cost); needs a `templateVersion` bump (shared with B).
- **Option B — separate guidance file + pointer.** New `templates/code-guidance.template.md`
  installed to `.agents/code-guidance.md`, plus a one-line pointer from `AGENTS.template.md`
  (a pointer is governance-legal, like the existing `.agents/state.md` references). **Install
  must be wired on all three routes or the pointer dangles** — `discover.py` copies `templates/`
  wholesale, but nothing drafts a new top-level template into a target repo unless the route
  procedures say to: add the draft step to the greenfield list (`procedures/bootstrap.md` ~L279),
  the migration list (`procedures/migration.md` ~L45), and the update/reconciliation path. Pros:
  preserves the **exact** wording; optional/removable; honors minimalism. Cons: **weaker** (a
  pointed-to file is only as effective as the agent reading it; the eval effect came from the
  prose being *inline*); and the pointer edit to `AGENTS.template.md` **still needs a
  `templateVersion` bump**.

**Version bump applies to both (codex blocker):** either option edits `AGENTS.template.md`
(A adds an invariant, B adds a pointer), so **both require a `templateVersion` bump** (L2) —
otherwise update-route repos already stamped current won't reconcile and will miss the change
(`tools/discover.py:278`; `tests/test_discover.py:619`).

**Recommendation:** Option B if preserving the exact wording and minimalism matter most;
Option A if in-context effectiveness matters most and the owner accepts condensing to invariant
form. Given the evidence is weak and minimalism is prized, I lean **B** — on a tradeoff, not
because A is forbidden — and flag that B may neuter the (already small) effect. Owner decides
before any code.

## Concrete edit sites (verify exact lines at implementation)

| File | Change |
|---|---|
| `templates/hooks/claude/settings.json` | + `PostToolUseFailure` hook entry (matcher `Edit|Write|MultiEdit`) |
| `templates/hooks/claude/edit-refocus.py` | new script emitting the `additionalContext` JSON |
| `tests/test_discover.py` (~L436–511) | + schema row & presence/portability assertions for the new hook |
| **G1=A:** `templates/AGENTS.template.md` | + condensed completeness invariant; **bump `templateVersion` (L2)** |
| **G1=B (all 3 routes):** new `templates/code-guidance.template.md`; draft step in `procedures/bootstrap.md` (greenfield ~L279) **and** `procedures/migration.md` (~L45) **and** the update/reconcile path; pointer in `AGENTS.template.md` + **bump `templateVersion` (L2)** | ship exact wording to `.agents/code-guidance.md` |

## Future validation (not blocking adoption; owner-gated, costs credits)

The hook is unmeasured. A clean test exists if wanted later: instrument the
rejection→re-author cycle (count edits rejected then re-authored, diff the re-author
against the prior attempt for dropped hunks), run a harness with/without the hook on
instances that trigger it, measure dropped-hunk rate and FuncPass. Out of scope here.

## Non-goals

- No change to this repo's own `AGENTS.md`/`.agents/` (owner: product, not this repo).
- No re-opening model testing.
- No verbatim-`tool_input` re-injection hook variant — that needs the `PostToolUseFailure`
  payload to carry the failed edit content (unconfirmed); the static generic message ships
  now, verbatim re-injection is a future enhancement (Open decision H2).
- No codex/grok/agy failure-hook port this pass (H1).

## Verification (when implemented)

`python3 -m unittest discover -s tests -v` (this is the repo's gate for
`tools/discover.py`, `tests/`, and `templates/`/`procedures/` content). Prove each new
test guards its change by temporary revert. Docs/template-only portions that don't alter
generated behavior still ride the same suite because they touch `templates/`.

## Open decisions (owner)

- **G1:** prose placement — A (invariant in AGENTS.template.md, condensed) vs B (separate
  `.agents/` file + pointer, exact wording). *Recommend B.*
- **H1:** hook harness scope — Claude only now (recommend) vs also research codex/grok/agy.
- **H2:** static generic message now (settled) vs pursue verbatim `tool_input` re-injection
  (needs payload-schema confirmation) as a follow-up.

## Review trail

- **codex round-1** (read-only, verified against the repo): VERDICT **REVISE**, all folded into
  this v2. Two **blockers**: (1) the `templateVersion` bump applies to **both** G1 options (B
  also edits `AGENTS.template.md` via the pointer), not just A; (2) Option B install must be
  wired on **all three routes** (greenfield/migration/update) or the pointer dangles —
  `discover.py` copies `templates/` but route procedures must draft the new top-level file.
  Three **should-fix**: G1 was over-framed as a governance *prohibition* (Option A is permitted;
  it's a tradeoff); "governance invariant is tested" overclaimed (the prose isn't unit-tested);
  the hook test must **execute** the script, not just check config. One **nit**: harness phrasing
  (target repos do receive the `.claude/` profile; only the failure *event* is Claude-specific).
  codex **confirmed** the `PostToolUseFailure` + `additionalContext` mechanism is correct against
  current Claude Code docs.
