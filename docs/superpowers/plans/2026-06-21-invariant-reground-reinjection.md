# Invariant Re-grounding & Re-injection Implementation Plan

> **Superseded in part (2026-06-21, commit `548e03d`):** the hook mechanism below — a shared `templates/hooks/reground.sh` invoked as `sh "__REPO_ROOT__/.agents/hooks/reground.sh"` — shipped two portability bugs: it baked an **absolute path** at install (broke on clone/move) and required a **POSIX shell** (broke on native Windows). The script was deleted and its fixed pointer **inlined into each config as an `echo` command** (no path to substitute, no shell script). Wherever this plan says `reground.sh`, `__REPO_ROOT__`, or `sh "…"`, read the inline-`echo` form instead. See spec §4.3 and §5b for the fix and the test-instrument lesson. The rest of the plan (Prime Invariants block, trust step, all-routes install) stands as built.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add harness-portable re-grounding of governance invariants — a canonical Prime Invariants block in `AGENTS.template.md` plus per-harness hooks that re-trigger a re-read after context compaction — to the AgentGovernanceBootstrap product.

**Architecture:** The product is templates + procedures + a `discover.py` that `shutil.copytree`s `templates/` and `procedures/` wholesale into a target repo's `.bootstrap-tmp/`. New work is content, not new Python: restructure `templates/AGENTS.template.md`, add `templates/hooks/<harness>/` configs + one shared `reground.sh` trigger script, and add an all-routes bootstrap step that installs/registers the hooks and surfaces the (machine-local, uncommittable) trust step. The re-injection hook emits a fixed *pointer* to re-read `AGENTS.md` from disk — never the invariants verbatim — so authority stays with the canonical file and a forged hook payload is harmless.

**Tech Stack:** Markdown templates, JSON hook configs, POSIX `sh`, Python 3 stdlib `unittest` (`tests/test_discover.py` + `tests/fixtures.py`).

**Spec:** `docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`

## Global Constraints

- **Keep all governance text terse** — lean invariants survive compaction; Codex truncates `AGENTS.md` past `project_doc_max_bytes` (32 KiB default), so the Prime block must stay at the very top.
- **One canonical location** — the Prime Invariants live only in the `AGENTS.template.md` block; nothing restates them. The re-ground hook points at that file, it does not copy it.
- **Hooks are per-harness committed files; trust is per-machine and uncommittable** — never auto-grant trust; the bootstrap surfaces the step.
- **Trust/hook guidance in `AGENTS.md` is harness-neutral** — no vendor names in the shared file (vendor specifics caused cross-harness contamination in testing).
- **Verification:** for any change to `templates/`, `procedures/`, `tools/discover.py`, or `tests/`, run `python3 -m unittest discover -s tests -v`. For docs-only prose, also `git diff --check`.
- **Per-harness hook schemas are verified at build time** against each harness's own docs/`--help`; the configs below are the best-known starting point, corrected by the behavioral test in Task 4.
- **This is product-only.** Do not edit this repo's own `AGENTS.md` / `.agents/`; those are brought current later by a single bootstrap re-run.

---

## File Structure

- `templates/AGENTS.template.md` (modify) — Prime Invariants block (top, marker-delimited); Universal Invariants reference it; `catchup` operator sharpened; harness-neutral hook-trust + re-ground note; Bootstrap Handoff gains a hook-audit step.
- `templates/commands/claude/catchup.md` (modify) — pointer text sharpened to "re-read Prime Invariants in full + re-ground".
- `templates/hooks/reground.sh` (create) — prints the fixed re-ground trigger.
- `templates/hooks/claude/settings.json` (create) — Claude Code `SessionStart`/`compact` hook.
- `templates/hooks/codex/hooks.json` (create) — Codex `SessionStart` source `compact`.
- `templates/hooks/grok/hooks/reground.json` (create) — Grok `PreCompact`/`PostCompact`.
- `templates/hooks/agy/hooks.json` (create) — agy `SessionStart` (post-compaction re-fire to verify).
- `procedures/bootstrap.md`, `procedures/migration.md` (modify) — all-routes "Hook install & trust" step.
- `tests/test_discover.py` (modify) — assert Prime markers + hook templates present and copied.

---

### Task 1: Restructure `templates/AGENTS.template.md` (invariants + operators + trust note)

**Files:**
- Modify: `templates/AGENTS.template.md`
- Modify: `templates/commands/claude/catchup.md`
- Test: `tests/test_discover.py`

**Interfaces:**
- Produces: the marker-delimited block `<!-- prime:begin … --> … <!-- prime:end -->` inside `AGENTS.template.md`, at file top. Task 2's `reground.sh` names this block; Task 3's install step copies it.

- [ ] **Step 1: Write the failing test** — append to `tests/test_discover.py`:

```python
class TestPrimeInvariantsTemplate(unittest.TestCase):
    def test_prime_block_present_and_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            tmpl = (repo / ".bootstrap-tmp" / "templates"
                    / "AGENTS.template.md").read_text(encoding="utf-8")
        self.assertIn("<!-- prime:begin", tmpl)
        self.assertIn("<!-- prime:end -->", tmpl)
        head = tmpl[:tmpl.index("<!-- prime:end -->")]
        for phrase in ("Words first.",
                       "No code change without an approved plan",
                       "Commit each slice as it lands",
                       "re-ground from AGENTS.md"):
            self.assertIn(phrase, head)
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python3 -m unittest tests.test_discover.TestPrimeInvariantsTemplate -v`
Expected: FAIL (`<!-- prime:begin` not found).

- [ ] **Step 3: Add the Prime Invariants block at the very top of the document body** of `templates/AGENTS.template.md` (immediately after the `# Agent Guidance` heading, before `## Mission`), verbatim as approved:

```
## Prime Invariants
<!-- prime:begin — keep terse; re-grounded after compaction -->
These outrank everything below. After a context compaction, re-read this block from AGENTS.md before continuing.

- Words first. Answer questions and musings in words; act only on an explicit
  instruction or go. A handed-over report, plan, or spec is evidence to assess,
  not a decision to implement.
- No code change without an approved plan; docs and other non-code edits don't
  (e.g. a README). When unsure, treat it as code.
- Commit each slice as it lands; never leave finished work uncommitted. Push,
  history-rewrite, and destructive or outward-facing actions need an explicit
  go — pushing publishes.
- Repo is memory. Durable truth lives in the repo, not chat or working memory.
  Under context pressure, re-ground from AGENTS.md; prefer a fresh session when
  degraded.
<!-- prime:end -->
```

- [ ] **Step 4: De-duplicate the existing `## Universal Invariants`** so it does not restate the four Prime rules. Replace the current "Answer human's questions words…" bullet with a one-line pointer: `- The Prime Invariants above are the hardest-to-reverse rules; this section adds the rest.` Keep the remaining Universal bullets (durable memory detail, one-canonical-location, roadblock-provenance, verification defaults, etc.) but delete any that merely repeat a Prime rule (the words-first bullet and any standalone "commit/push" bullet now owned by Prime).

- [ ] **Step 5: Sharpen the `catchup` operator** in the "Operator Requests" / "Source Of Truth" operator list of `templates/AGENTS.template.md`. Replace the `catchup` line with:

```
- `catchup`: re-read `AGENTS.md` (the Prime Invariants in full), `.agents/state.md`,
  and active repo docs; summarize current state, next action, blockers, and one
  proposed first action. Make no changes until the human responds.
```

- [ ] **Step 6: Add a harness-neutral "Hook trust & re-grounding" note** to the `## Session Startup` section of `templates/AGENTS.template.md`:

```
- This repo may ship session-start / post-compaction hooks that re-ground you by
  re-reading AGENTS.md. Many harnesses keep committed hooks inert until the
  workspace is trusted on this machine — a one-time, uncommittable security step.
  If your harness gates hooks and they are untrusted, say what they do, ask, and
  only with an explicit go run the trust step for the harness you are actually in
  (ask the human if unsure). Never run another harness's config or trust commands,
  and never bypass the gate.
```

- [ ] **Step 7: Update the catchup wrapper** `templates/commands/claude/catchup.md` — change "re-read `AGENTS.md`, `.agents/state.md`, and the active repo docs" to "re-read `AGENTS.md` (the Prime Invariants in full), `.agents/state.md`, and the active repo docs". Leave the rest.

- [ ] **Step 8: Run the test and the suite**

Run: `python3 -m unittest tests.test_discover.TestPrimeInvariantsTemplate -v && python3 -m unittest discover -s tests -v && git diff --check`
Expected: PASS; no whitespace errors.

- [ ] **Step 9: Commit** (folds in the spec doc per owner)

```bash
git add templates/AGENTS.template.md templates/commands/claude/catchup.md tests/test_discover.py docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md
git commit -m "feat(templates): add Prime Invariants block + harness-neutral re-ground/trust note"
```

---

### Task 2: Hook templates (`templates/hooks/`)

**Files:**
- Create: `templates/hooks/reground.sh`
- Create: `templates/hooks/claude/settings.json`
- Create: `templates/hooks/codex/hooks.json`
- Create: `templates/hooks/grok/hooks/reground.json`
- Create: `templates/hooks/agy/hooks.json`
- Test: `tests/test_discover.py`

**Interfaces:**
- Consumes: the `prime:*` markers from Task 1 (the trigger tells the agent to re-read that block).
- Produces: configs that each invoke `sh "__REPO_ROOT__/.agents/hooks/reground.sh"`. The literal token `__REPO_ROOT__` is substituted with the target repo's absolute path by Task 3's install step.

- [ ] **Step 1: Write the failing test** — append to `tests/test_discover.py`:

```python
class TestHookTemplates(unittest.TestCase):
    def test_hook_templates_present_and_copied(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = fixtures.make_greenfield_repo(Path(tmp) / "repo")
            fixtures.run_discover(repo)
            hooks = repo / ".bootstrap-tmp" / "templates" / "hooks"
            rels = ("reground.sh", "claude/settings.json", "codex/hooks.json",
                    "grok/hooks/reground.json", "agy/hooks.json")
            for rel in rels:
                self.assertTrue((hooks / rel).is_file(), rel)
            for rel in rels[1:]:
                self.assertIn("reground.sh",
                              (hooks / rel).read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run it to confirm it fails**

Run: `python3 -m unittest tests.test_discover.TestHookTemplates -v`
Expected: FAIL (`templates/hooks/reground.sh` missing).

- [ ] **Step 3: Create `templates/hooks/reground.sh`**

```sh
#!/bin/sh
# Re-ground trigger. A harness runs this from a session-start / post-compaction
# hook; its stdout is injected into the agent's context. It deliberately does NOT
# restate the invariants — hook stdout is untrusted, and a forged copy would be an
# injection vector. It points the agent at the canonical file instead.
printf '%s\n' "Context was compacted or the session (re)started. Before continuing, re-read AGENTS.md from disk — especially the Prime Invariants block. Treat AGENTS.md, not this message, as authoritative."
```

- [ ] **Step 4: Create the four hook configs.** Each is the best-known schema for its harness (Task 4 verifies/corrects against live behavior).

`templates/hooks/claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "compact",
        "hooks": [ { "type": "command", "command": "sh \"__REPO_ROOT__/.agents/hooks/reground.sh\"" } ] }
    ]
  }
}
```

`templates/hooks/codex/hooks.json`:
```json
{
  "hooks": {
    "SessionStart": [
      { "matcher": "compact",
        "hooks": [ { "type": "command", "command": "sh \"__REPO_ROOT__/.agents/hooks/reground.sh\"" } ] }
    ]
  }
}
```

`templates/hooks/grok/hooks/reground.json`:
```json
{
  "hooks": {
    "PostCompact": [
      { "hooks": [ { "type": "command", "command": "sh \"__REPO_ROOT__/.agents/hooks/reground.sh\"" } ] }
    ]
  }
}
```

`templates/hooks/agy/hooks.json`:
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "sh \"__REPO_ROOT__/.agents/hooks/reground.sh\"" } ] }
    ]
  }
}
```

- [ ] **Step 5: Run the test and the suite**

Run: `python3 -m unittest tests.test_discover.TestHookTemplates -v && python3 -m unittest discover -s tests -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add templates/hooks tests/test_discover.py
git commit -m "feat(templates): add per-harness re-ground hook configs + shared trigger"
```

---

### Task 3: All-routes "Hook install & trust" bootstrap step

**Files:**
- Modify: `procedures/bootstrap.md`
- Modify: `procedures/migration.md`
- Modify: `templates/AGENTS.template.md` (Bootstrap Handoff hook-audit step)

**Interfaces:**
- Consumes: `templates/hooks/*` from Task 2 (source of the configs to install) and the `__REPO_ROOT__` token (substituted at install).
- Produces: prose instructions; no new code symbols.

- [ ] **Step 1: Add a "Hook install & trust (all routes)" section to `procedures/bootstrap.md`**, modeled on the existing "Operator command wrappers (all routes)" guarantee. It must instruct the agent to:
  1. For each harness the toolkit ships a `templates/hooks/<harness>/` set for, draft the target-repo files under `.bootstrap-tmp/drafts/` mirroring final paths: `.agents/hooks/reground.sh` (from `templates/hooks/reground.sh`) and each harness config at its real path (`.claude/settings.json`, `.codex/hooks.json`, `.grok/hooks/reground.json`, `.agents/hooks.json`), substituting the literal `__REPO_ROOT__` with the target repo's absolute root path.
  2. Make them committable: run `git check-ignore` on each final path; if an ignore rule covers it, propose a narrowed `.gitignore` edit (never `git add -f`), exactly as the wrapper guarantee does.
  3. Record post-commit custody in the artifact manifest, proven by `git check-ignore` / `git ls-files`.
  4. **Surface trust, never grant it:** state that committed hooks are inert until the workspace is trusted on this machine, that trust is machine-local and uncommittable, and give the harness-neutral instruction (the agent runs the trust step for the harness it is actually in, only on an explicit go). Do not write to any `~/`-level trust store automatically.
  5. Record "hooks already present, nothing to do" when they exist and are committed; never overwrite existing hook content.

- [ ] **Step 2: Add the same section to `procedures/migration.md`** (so migration/update routes install hooks too), pointing to the bootstrap.md section rather than duplicating it: `Run the "Hook install & trust (all routes)" guarantee from bootstrap.md.`

- [ ] **Step 3: Add a hook-audit step to the Bootstrap Handoff list in `templates/AGENTS.template.md`** (so update-route repos self-heal), after the operator-wrapper audit step:

```
- Audit re-ground hooks: if `templates/hooks/<harness>/` sets exist in the toolkit
  but the target repo lacks the corresponding committed hook files
  (`.agents/hooks/reground.sh` + per-harness config), draft them as above. Surface
  the one-time, machine-local trust step; never grant trust automatically.
```

- [ ] **Step 4: Verify prose + suite**

Run: `python3 -m unittest discover -s tests -v && git diff --check`
Expected: PASS; no whitespace errors. Re-read the spec §4.3–§4.4 and confirm each requirement maps to text just written.

- [ ] **Step 5: Commit**

```bash
git add procedures/bootstrap.md procedures/migration.md templates/AGENTS.template.md
git commit -m "feat(procedures): install re-ground hooks on all routes + surface trust step"
```

---

### Task 4: Per-harness behavioral verification (OWNER-DRIVEN, interactive)

**Not a subagent task** — it needs the live harnesses and the human in the loop. Run it after Tasks 1–3 land. No big context seed required: use each harness's **manual `/compact`**, which fires the same compaction hooks as auto-compaction.

**Files:**
- Test: throwaway scratch repos (no repo files changed); record results in the spec's §5.

**Interfaces:**
- Consumes: the installed hook files (Task 2 content + Task 3 install semantics).

- [ ] **Step 1: Build a scratch target repo** with `.agents/hooks/reground.sh` and the four configs installed (absolute path substituted for `__REPO_ROOT__`), mirroring the validation repos already used.

- [ ] **Step 2: Per harness, run the behavioral test:** open the repo, **trust** the workspace via that harness's own step (Claude `trustedDirectories`/`/hooks`; Codex `/hooks`; Grok `/hooks-trust`; agy `trustedWorkspaces` via `/config`), then run **`/compact`** and confirm the re-ground trigger text appears in context afterward. Seeding a full context window is a fallback only if a harness lacks manual compact and its `SessionStart` does not re-fire post-compaction.

- [ ] **Step 3: For any harness whose config schema is wrong** (hook does not fire after trust), correct the config in `templates/hooks/<harness>/` against that harness's docs/`--help`, re-run, and re-commit the fix (per-harness, one commit each).

- [ ] **Step 4: Resolve the agy open item** — determine whether agy re-fires `SessionStart` (or a dedicated compaction event) after a compaction. If it does not, record agy as session-start/resume re-grounding only (no post-compaction teeth) in the spec §3 and §4.3; do not claim a capability that did not fire.

- [ ] **Step 5: Record outcomes** in `docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md` §5 (which harnesses fire post-compaction, any schema corrections). Commit:

```bash
git add docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md templates/hooks
git commit -m "test: record per-harness re-ground hook behavioral results"
```

---

## Self-Review

**Spec coverage:**
- §4.1 Prime block + Universal referencing → Task 1 (Steps 3–4). ✓
- §4.2 floor: native load + `catchup` sharpening → Task 1 (Steps 5, 7). ✓ (`CLAUDE.md @AGENTS.md` already exists; no `GEMINI.md` change — correct, nothing to do.)
- §4.3 re-ground *trigger* (not re-injection) + per-harness configs + one-run install → Task 2 + Task 3 (Step 1). ✓
- §4.4 trust: harness-neutral, surfaced not granted → Task 1 (Step 6) + Task 3 (Step 1.4, Step 3). ✓
- §4.5 plan-first + git policy in the block → Task 1 (Step 3, approved block). Removal of this repo's two bad lines is **out of scope** (happens in the later bootstrap re-run, per §7) — correctly not a task here. ✓
- §5 verification → Task 4. ✓
- 32 KiB cap / Prime-at-top → Task 1 (Step 3 places it at file top). ✓

**Placeholder scan:** `__REPO_ROOT__` is a deliberate substitution token defined in Task 2 Interfaces and substituted in Task 3 Step 1.1 — not a lazy placeholder. Per-harness schema uncertainty is handled by an explicit verification task (Task 4), not a TODO. No "add error handling"-style gaps.

**Type/name consistency:** the marker strings (`<!-- prime:begin`, `<!-- prime:end -->`), the script path (`.agents/hooks/reground.sh`), the token (`__REPO_ROOT__`), and the harness config paths are identical across Tasks 1–3 and the tests.

**Note on TDD adaptation:** this is a templates/procedures content change with a thin code surface, so Tasks 1–2 use real presence/copy assertions in the existing `unittest` harness; Task 3 is prose verified by the suite + `git diff --check` + spec re-read; Task 4 is behavioral (the genuine test of the hooks). This matches the repo's own verification rule.
