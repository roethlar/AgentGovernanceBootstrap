# Synchronous Review Handoff Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the async sentinel-based `reviewloop` playbook with a synchronous `/review <agent>` flow where the coding agent dispatches a named reviewer harness headless, parses a structured fail-closed verdict, records it durably, and acts under owner-gated merge.

**Architecture:** This is a docs/templates change to a portable governance toolkit. Two artifacts change: (1) `templates/playbooks/reviewloop.md` is rewritten to the synchronous shape; (2) a new `.claude/commands/review.md` slash-command wrapper points at the playbook (mirroring the existing operator wrappers). `tools/discover.py` copies `templates/` verbatim, so the rewritten playbook ships to target repos with no code change. `review` deliberately does **not** join `OPERATOR_WORDS` (decision below).

**Tech Stack:** Markdown (playbook + wrapper); Python `unittest` for the no-regression gate; git.

## Global Constraints

- The authoritative design is `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`. Every task implements that spec; do not re-derive its decisions.
- `templates/playbooks/reviewloop.md` is content `discover.py` copies into target repos (user-facing generated guidance). Verification is **required**, not optional: `python3 -m unittest discover -s tests -v` plus `git diff --check`.
- Harness knowledge is **never** a human-maintained table and **never** a committed help-text parser. The playbook ships the *probe-and-verify procedure*; the agent derives incantations live.
- The reviewer verdict contract is **structured JSON + inner-schema parse + fail-closed** (parse miss / bad exit / SHA mismatch → NOT accepted; re-prompt once, then contested). A parse miss never becomes a silent accept.
- The reviewer's guard proof runs in **its own git worktree** at the head SHA; it never mutates the coder's tree.
- The reviewed diff is pinned to explicit **base + head SHAs**, not a moving `main..branch` range.
- One canonical location per truth; pointers over duplication; preserve owner-gating of merge/push/history-rewrite throughout.
- This is a docs-only change set (no `tools/discover.py` logic change, no new test of script behavior). Commit each task as it lands.

## Decision: `review` does NOT join `OPERATOR_WORDS`

`OPERATOR_WORDS` in `tools/discover.py:275` gates whether a target repo's `AGENTS.md` advertises the **governance** operator vocabulary (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`); a target missing one is flagged stale and reconciled on the update route. `review` is a **playbook** operator — `/review <agent>` invokes a playbook exactly as `playbook reviewloop` does — not a governance operator that every `AGENTS.md` must name. Adding it to `OPERATOR_WORDS` would force every target `AGENTS.md` to mention `review` or be reported stale, which is wrong, and would compound the already-deferred `playbook <name>` false-positive (`.agents/state.md`). Therefore `review` ships as a playbook + a Claude Code wrapper only; `OPERATOR_WORDS` and the staleness machinery are untouched. This removes the spec's open question 2 from scope.

## File Structure

- **Rewrite** `templates/playbooks/reviewloop.md` — the synchronous playbook (single responsibility: define the `/review <agent>` loop end to end). Supersedes commit `498c056`.
- **Create** `.claude/commands/review.md` — thin Claude Code slash-command wrapper, pointer-only (mirrors `.claude/commands/playbook.md`).
- **No change** to `tools/discover.py`, `tests/`, `AGENTS.md` operator list, or other templates.

Verification (run once, after both content tasks land — there is no per-file test to write since this is prose in a copied template):
- `python3 -m unittest discover -s tests -v` — required no-regression gate on the copied tree.
- `git diff --check` — whitespace/conflict-marker check.
- Manual checklist (Task 3) — the semantic review of the rewritten playbook.

---

### Task 1: Rewrite `templates/playbooks/reviewloop.md` to the synchronous shape

**Files:**
- Modify (full rewrite): `templates/playbooks/reviewloop.md`

**Interfaces:**
- Consumes: the design spec (Global Constraints). The existing playbook's *kept* discipline (atomic unit, intake/triage, guard proof, contested path, owner-gating, status index, per-finding doc).
- Produces: the playbook content that Task 2's wrapper points at, and that Task 3 verifies. Defines these names the wrapper and any reader rely on: the operator phrase **`review <agent>`**; the verdict JSON keys **`verdict` (accepted|reopened|invalid), `guard_confirmed`, `reviewed_sha`, `base_sha`, `comments`**; the optional cache path **`.agents/review/harnesses.local.json`**.

- [ ] **Step 1: Confirm the spec is the source of content**

Run: `sed -n '40,160p' docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`
Expected: the Design section (Roles, Entry point, Mechanism steps 1–5, Per-harness isolation, removed/kept lists). This is the content to render into playbook form.

- [ ] **Step 2: Rewrite the playbook**

Replace the entire file with the synchronous playbook. It MUST contain, in order:

1. **Title + intro** — `# Playbook: synchronous cross-harness review (\`review\`)`; one paragraph: coder = current harness, reviewer = a named foreign harness dispatched headless one-shot per finding; defers to `AGENTS.md`/`.agents/`; invariants win on conflict.
2. **What this loop is for** — converge on correct (not merely changed) code; reviewer-inflation and author-capitulation as the two failure halves; route correctness through verification, not agreement. (Carry over from the current playbook's framing — it is *kept*.)
3. **Atomic unit** — one finding ↔ one branch ↔ one verdict. (Note: ↔ one *sentinel* is dropped; there is no sentinel.)
4. **Governance alignment** — keep the dedup-pointer Status bullet verbatim ("pointer doc points; it does not keep a second copy of an enumeration another doc owns"); keep owner-gated-merge bullet; keep "disagreement is a recorded verdict, never a silent veto"; keep capabilities-not-harness-names bullet.
5. **Operator** — `review <agent>` is the harness-neutral entry; in Claude Code it is `/review <agent>` (tab-completable); on another harness the owner speaks it. Synchronous by construction — there is no quick/wait toggle and no Strict/Faster WIP mode (the coder blocks on each review).
6. **Deriving the reviewer incantation (probe-and-verify)** — the 4-step procedure from the spec: presence (`command -v`), surface (`--help`/`--version`), drill one level if ambiguous, bounded smoke-test (timeout; non-interactive/TUI detection; run in a real git repo; treat a launch refusal as a flag to adjust). State that probing is bounded to `--help`/`--version`/a trivial smoke prompt. State the optional self-correcting gitignored cache `.agents/review/harnesses.local.json` (advisory, not source of truth; not human-authored).
7. **Per-finding flow** — render spec Mechanism steps 1–5 as numbered playbook steps:
   - finish fix on `fix/<id>-<slug>` (intake/triage + guard proof already done);
   - dispatch reviewer headless one-shot in the harness JSON output mode, passing explicit base SHA (merge-base at dispatch) + head SHA; reviewer reads code from the shared workspace and runs its guard proof in **its own `git worktree`** at the head SHA, never the coder's tree;
   - **verdict contract** with the JSON schema block and the fail-closed rule (re-prompt once, then contested);
   - **record** into the finding doc `## Reviewer comments`: harness name+version, reviewed/base SHA, `guard_confirmed`, verdict, UTC timestamp, comments; flip Status; state whether the record is committed;
   - **act**: accepted → owner-gated merge; reopened → fix-ups on the same branch, re-run `review <agent>`; invalid → `.agents/review/<id>.contested.md`, route to owner.
8. **Intake and triage gate** — carry over verbatim from the current playbook (evidence / predicted observable failure / justified severity → ADMITTED or DECLINED; empty findings table is valid; DECLINED reasons written down).
9. **Per-finding record template** — the finding-doc markdown skeleton, kept, with **Guard proof** and **Reviewer comments** sections; drop sentinel references.
10. **Status index** — kept as the human scoreboard (legend incl. `[!]`/`[-]`; `state.md` points, does not copy the table). Drop the sentinel-watcher framing.
11. **Anti-patterns + Calibration anti-patterns** — keep, minus sentinel-specific entries ("Skipping the sentinel", "watcher watches sentinels"); add: **Accepting on a parse miss** (fail-closed: a missing/!schema verdict is NOT an accept); **Reviewer mutating the coder's tree** (guard proof belongs in the reviewer's own worktree).
12. **Knobs** — keep single-agent mode (one mind both hats; still write DECLINED/Contested down) and adjudicator; **remove** the async-only knobs (multiple coders, multiple reviewers, persistent-reviewer watch).

Do NOT include: `ready/` sentinels, the `mv`-into-place atomic write, the polling watcher / wake mechanism, sentinel JSON schemas, `results/<id>.verified.json`/`.reopened.md` file protocol.

- [ ] **Step 3: Whitespace check**

Run: `git diff --check`
Expected: no output (clean).

- [ ] **Step 4: Commit**

```bash
git add templates/playbooks/reviewloop.md
git commit -m "$(cat <<'MSG'
docs(playbooks): rewrite reviewloop as synchronous /review <agent>

Replace the async sentinel/watcher loop with a synchronous flow: the coder
dispatches a named reviewer harness headless one-shot per finding, derives the
incantation live by probing, parses a structured fail-closed JSON verdict,
records it (harness+version, base/head SHA, guard_confirmed, verdict, ts) into
the finding doc, and acts under owner-gated merge. Reviewer guard proof runs in
its own worktree against a pinned base SHA. Implements
docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
MSG
)"
```

---

### Task 2: Add the `.claude/commands/review.md` slash-command wrapper

**Files:**
- Create: `.claude/commands/review.md`
- Reference: `.claude/commands/playbook.md` (pattern to mirror)

**Interfaces:**
- Consumes: the playbook from Task 1 (the wrapper points at it; the `review <agent>` operator phrase and the playbook path must match what Task 1 produced).
- Produces: the Claude Code front door `/review <agent>`.

- [ ] **Step 1: Write the wrapper**

Create `.claude/commands/review.md` with pointer-only content (no logic duplicated from the playbook):

```markdown
Run the `review` playbook operator: read
`.agents/playbooks/reviewloop.md` and follow it to review the current finding
with the agent named in your request (e.g. `/review codex`, `/review grok`,
`/review agy`). The named agent is the reviewer harness; it is dispatched
headless and one-shot per the playbook. If the playbook does not exist in this
repo, say so rather than guessing. The playbook is the authoritative
definition; this file is only a pointer.
```

- [ ] **Step 2: Whitespace check**

Run: `git diff --check`
Expected: no output (clean).

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/review.md
git commit -m "$(cat <<'MSG'
feat(commands): add /review <agent> wrapper pointing at the reviewloop playbook

Thin Claude Code slash-command front door for the synchronous review operator,
mirroring the existing operator wrappers. Pointer-only; the playbook owns the
semantics. review deliberately stays out of OPERATOR_WORDS (it is a playbook
operator, not a governance one).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
MSG
)"
```

---

### Task 3: Verify (required gate + manual checklist) and update state

**Files:**
- Modify: `.agents/state.md` (record the landed change + the deferred follow-up)

**Interfaces:**
- Consumes: the committed Task 1 + Task 2 artifacts.
- Produces: green verification evidence and an updated current-state entry point.

- [ ] **Step 1: Run the required no-regression gate**

Run: `python3 -m unittest discover -s tests -v 2>&1 | tail -5`
Expected: `OK` (the suite tests discovery behavior, not playbook prose; it must stay green because the file lives under the copied `templates/` tree). If it fails, STOP — a docs rewrite must not change discovery behavior; investigate before proceeding.

- [ ] **Step 2: Run the manual checklist**

Confirm in `templates/playbooks/reviewloop.md`:
- `grep -c "second copy of an enumeration" templates/playbooks/reviewloop.md` → `1` (dedup phrasing preserved).
- `grep -nE "ready/|sentinel|watcher|\.verified\.json" templates/playbooks/reviewloop.md` → no output (async machinery fully removed).
- `grep -n "guard_confirmed\|reviewed_sha\|base_sha\|fail" templates/playbooks/reviewloop.md` → verdict contract + fail-closed rule present.
- `grep -n "own .git worktree\|own worktree\|its own worktree" templates/playbooks/reviewloop.md` → guard-proof isolation present.
- `grep -n "owner-gated\|owner go\|owner-approved" templates/playbooks/reviewloop.md` → owner-gating intact.
- Status legend still lists `[!]` and `[-]`; no status symbol used without a legend entry.

Fix any miss by editing the playbook, then re-run Step 1 + Step 3 before committing Step 5.

- [ ] **Step 3: Whitespace check**

Run: `git diff --check`
Expected: no output.

- [ ] **Step 4: Update `.agents/state.md`**

Add a `## Now` bullet (absolute date 2026-06-25) recording that `reviewloop` was rewritten to the synchronous `/review <agent>` design (cite the spec) and the `/review` wrapper was added; and a `## Next` bullet noting the deferred follow-up: **if** `review` is ever surfaced as a governance operator, the `OPERATOR_WORDS`/`playbook <name>` staleness collision must be resolved first. Do not duplicate counts the decisions doc owns; point, don't copy.

- [ ] **Step 5: Commit**

```bash
git add .agents/state.md
git commit -m "$(cat <<'MSG'
docs(state): record synchronous review-handoff landing and deferred follow-up

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
MSG
)"
```

---

## Self-Review

**Spec coverage:**
- Roles (coder=current harness, reviewer=named foreign harness) → Task 1 Step 2 (1).
- Single `review <agent>` operator, synchronous, no quick/wait → Task 1 (5), Task 2.
- Probe-and-verify incantation derivation, bounded → Task 1 (6).
- Optional gitignored cache, not human-authored → Task 1 (6).
- Per-finding dispatch, pinned base/head SHA → Task 1 (7).
- Guard-proof worktree isolation → Task 1 (7), anti-patterns (11), checklist Task 3.
- Structured fail-closed JSON verdict contract → Task 1 (7), anti-patterns (11), checklist Task 3.
- Enriched durable record → Task 1 (7).
- Removed async machinery → Task 1 Step 2 exclusion list, checklist Task 3.
- Kept discipline (intake/triage, contested, owner-gating, status index) → Task 1 (8–12).
- Rewrite-not-coexist; `.claude/commands/review.md` wrapper → Tasks 1, 2.
- `OPERATOR_WORDS` question → resolved in the Decision section (not added); Task 3 records the deferred condition.
- Required verification → Task 3.
- Declined items (human-config-primary, Faster mode) → already recorded in the spec; not re-litigated here.

**Placeholder scan:** Task 1 Step 2 is a content spec (12 enumerated required sections with exact names/keys), not a "fill in details" — the engineer renders the named spec into playbook prose. No TBD/TODO. The wrapper (Task 2) and the verdict keys are given as literal text.

**Type consistency:** verdict keys (`verdict`/`guard_confirmed`/`reviewed_sha`/`base_sha`/`comments`), the operator phrase `review <agent>`, the playbook path `.agents/playbooks/reviewloop.md`, and the cache path `.agents/review/harnesses.local.json` are used identically across Tasks 1–3 and match the spec.

**Note for the executor:** Task 1 is a prose rewrite, not codegen, so its "test" is the Task 3 required gate + manual checklist rather than a unit test (there is no script behavior to assert — adding one would be vacuous). This is the correct verification per the repo's docs-in-copied-template policy.
