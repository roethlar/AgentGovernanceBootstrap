# Strict Converge-To-Shipped Refresh + Review Playbook Split

Status: APPROVED 2026-07-16 — owner go 2026-07-16; owner rulings recorded
verbatim in `.agents/decisions.md` (two 2026-07-16 entries). Slices land in
order, one commit each, suite green after each.

## Problem

1. `tools/refresh.py` treats an installed artifact that matches no shipped
   version as "owner-modified; left untouched". The owner ruling (2026-07-16
   decisions entry) establishes that no legitimate owner-modified state
   exists downstream: the owner never edits installed governance in place;
   every change flows through the toolkit and propagates by refresh. Any
   divergence is therefore drift — regardless of author — and today refresh
   both misattributes it ("owner-modified") and accommodates it (flag, never
   overwrite). Field incident: a governed repo's installed review playbook
   was edited in place by an agent (Powershell-Token-Killer commit
   `4f99fd5`); refresh would have reported that as owner work and left it.
2. Nothing shipped tells a downstream agent not to edit installed toolkit
   files. The don't-edit invariant in `templates/AGENTS.template.md` covers
   only `AGENTS.md`; playbooks/skills/wrappers land in `.agents/` and
   `.claude/`, exactly where agents are told durable work goes.
3. The single review playbook hardwires one review framing (verify a finding
   against its record). The owner wants two named flavors, chosen per
   invocation: `codereview` (conformance) and `openreview` (goal-first,
   unprimed).

## Owner rulings (operative rules; verbatim wording in `.agents/decisions.md`)

- Installed governance is toolkit-owned everywhere. Divergence from the
  shipped set is always drift; refresh restores it (report + restore), never
  accommodates it. Out-of-compliance docs are never "harmless".
- Prevention layers ship: generalized don't-edit invariant, per-file
  provenance marker, blocking Claude Code pre-edit hook.
- Review playbook splits into `codereview` and `openreview`; the owner
  invokes them by name; no auto-selection heuristic ships.

## Design A — strict converge refresh (`tools/refresh.py`)

Class rename: `replace-if-unmodified` → `replace` (the old name becomes a
lie once modified copies are replaced). Update `_KNOWN_CLASSES`, every
`class` value in `tools/shipped-set.json`, the manifest `comment`, the
module docstring, `docs/design.md`, `docs/usage.md`, and
`templates/commands/claude/update-governance.md` (whose FLAG wording
currently promises owner-modified files are never overwritten).

New `classify()` semantics:

- `replace`: missing → install; stem-equal to current → current; matches a
  formerly-shipped version (and not current-equivalent, M1 guard unchanged)
  → update; anything else → **restore**: converge to current bytes, report
  as drift.
- `replace-whole` (`AGENTS.md`): missing/current/formerly branches
  unchanged. The "anything else" branch forks on git evidence: if any
  historical blob of the target path matches a known shipped hash
  (`candidate_hashes(blob) ∩ (formerly ∪ candidate_hashes(current))`), the
  repo was governed and this is drift → **restore** + report; if no
  historical version ever matched, it is a foreign governance file → keep
  today's flag + ATTENTION banner + bootstrap offer (a migration, not a
  refresh). Helper `_ever_shipped(target_repo, rel, known)`: `git log
  --format=%H -- <rel>`, dedupe blob ids via `git rev-parse <sha>:<rel>`,
  read each unique blob once (`git cat-file blob`), bounded — runs only when
  a replace-whole target diverges.
- `retired`: missing → skip; matches formerly → remove; anything else →
  **remove anyway** + drift report (was: flag "remove by hand"). This
  includes the generated-JSON entries with empty `formerly` —
  `.agents/repo-map.json` / `.agents/artifact-manifest.json` are now <!-- plan-lint: allow (retired targets, deliberately named) -->
  machine-removed, not flagged; update the manifest comment and
  `tests/test_templates.py::test_retired_hook_class_and_json_layer_present`
  accordingly.

Drift reporting: `Plan` gains `restore` (target, source) and per-target
drift notes. Report lines carry provenance — the last ≤3 commits touching
the path (`git log -3 --format=%h %s -- <path>`), e.g.
`restored: <target> (DRIFT: matched no shipped version; recent: abc1234 subj | ...)`
and `removed: <target> (DRIFT: matched no shipped version; recent: ...)`.
The scoped commit message includes these lines via `summarize()`.

Safety unchanged and now load-bearing: restores/removes are touched paths,
so `dirty_conflicts()` refuses to run over an uncommitted diverged file
(exit 3, nothing changed) — machine-restore only ever replaces committed
content, recoverable from git history. `build_record`/`verify_record` gain
the `restores` field (plan-json/apply schema; add to the field loop).

Test changes (`tests/test_refresh.py`; all fixtures hermetic temp repos):

- Flip `test_owner_modified_artifact_is_flagged_not_overwritten` →
  diverged `replace` artifact is restored to current, stdout carries
  `DRIFT` + the introducing commit subject.
- Flip `test_modified_retired_artifact_is_flagged_kept` → removed + DRIFT.
- Flip `test_second_trailing_newline_still_flags` → restored via the
  restore branch (never reported as a plain update; M1 report honesty).
- `test_formerly_containing_current_hash_does_not_widen_boundary` and
  `RealManifestEquivalenceTests` → assert classification lands in
  `plan.restore`, not `plan.update` / `plan.flags`.
- Keep `test_foreign_agents_md_is_flagged_never_replaced` (fixture has no
  governed history); add `test_hand_edited_agents_md_in_governed_repo_is_restored`
  (commit a formerly-shipped AGENTS.md, then commit a hand-edit → restore +
  DRIFT, no banner).
- Add: uncommitted diverged artifact → exit 3, file untouched.
- Add: retired generated file (empty formerly) with arbitrary content →
  removed + DRIFT.
- Guard proofs: revert the `classify()`/report change, confirm the flipped
  and new tests fail, restore, confirm green.

## Design B — prevention layers

1. Invariant (`templates/AGENTS.template.md`, Universal Invariants; replaces
   the existing `AGENTS.md`-only don't-edit bullet; single line, portable):

   > `AGENTS.md` and every other artifact installed by governance refresh —
   > playbooks, skills, command wrappers, harness shims, hook settings — are
   > toolkit-owned: no agent edit and no out-of-band edit is legitimate, and
   > refresh restores any divergence to the shipped set. A proposed edit to
   > an installed copy is out of bounds — question it, route the change to
   > the owner for the toolkit, do not perform it. Durable repo-specific
   > rules go to `.agents/repo-guidance.md` and facts to the other
   > `.agents/` files.

   (Written as ONE physical line in the template — no hard wraps.)
   Same-commit maintenance: append the outgoing template's nhash to its
   `formerly` in `tools/shipped-set.json`.

2. Provenance marker: first line (after YAML frontmatter where present) of
   every shipped markdown artifact EXCEPT `AGENTS.template.md` (carries the
   invariant itself) and the shims (token cost every session; must stay
   exactly `@AGENTS.md` per `tests/test_templates.py`):

   `<!-- Installed by governance refresh; do not edit. Any change here is drift and is restored on the next refresh. Route changes through the toolkit owner. -->`

   Applies to `templates/playbooks/*.md`, `templates/commands/claude/*.md`,
   `templates/skills/shared/*/SKILL.md`. Add a structural test in
   `tests/test_templates.py` asserting the marker line is present in each
   (root-parameterized so its guard proof can run on a temp fixture).
   Same-commit maintenance: append each edited source's outgoing nhash to
   its `formerly`.

3. Blocking hook (Claude Code only — the sole harness with verified blocking
   PreToolUse, `docs/harness-capabilities.md`):
   - New shipped artifact `templates/hooks/claude/protect-governance.py` →
     target `.claude/hooks/protect-governance.py`, class `replace`. Stdlib
     Python; reads the hook JSON from stdin; extracts
     `tool_input.file_path` (or `notebook_path`); resolves it relative to
     `CLAUDE_PROJECT_DIR` (fallback: cwd); if the repo-relative path is in
     the protected set, prints a one-line governance message to stderr and
     exits 2 (blocking); otherwise exit 0. Any internal error → exit 0
     (fail-open; never breaks editing). The protected set is the shipped
     target list hardcoded in the script; a new test asserts it equals the
     manifest's targets minus the exempt shims — the manifest and script
     stay in lockstep or the suite goes red.
   - Shims (`CLAUDE.md`, `GEMINI.md`) ARE protected (they are shipped
     targets; strict ruling covers them).
   - `templates/hooks/claude/settings.json` gains a `PreToolUse` entry,
     matcher `Edit|Write|MultiEdit|NotebookEdit`, command an interpreter
     chain that preserves the exit code (no `a || b` chaining — exit 2 must
     not trigger the fallback): a single `sh`-compatible `if command -v
     python3 … elif command -v py … else exit 0` line over
     `"${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-governance.py"`. No
     baked absolute paths. Known limitation, documented in
     `docs/harness-capabilities.md`: hosts without a working python are
     fail-open — the hook is defense in depth; the strict refresh and the
     invariant text are the primary layers.
   - Update `tests/test_templates.py::ShippedHooks` (settings now has two
     hook events; re-ground command byte-locked as before) and add
     subprocess tests piping fixture JSON into the script: protected path →
     exit 2 + message; unprotected path → exit 0; garbage stdin → exit 0.
   - Live verify-once check (bounded): temp git repo with the hook
     installed; headless `claude -p` instructed to edit `AGENTS.md`; expect
     the edit blocked. Record the observation (positive or trust-gated
     negative) with date in `docs/harness-capabilities.md`. The
     PreToolUse-blocking mechanism itself is already verified there;
     shipping does not gate on this check succeeding headless, only on the
     unit tests.

## Design C — review playbook split

- `templates/playbooks/codereview.md`: the current reviewloop content with
  the operator renamed `codereview <agent>`, the provenance marker added,
  and a short framing note: this loop verifies specific findings against
  their records (plan-conformance is intentional here); for unprimed
  whole-change judgment use `openreview`.
- `templates/playbooks/openreview.md` (new): goal-first whole-change review.
  Contract:
  - The substantive prompt is exactly:
    **"Is the code as implemented the best way to achieve the goal?"**
    Neutral by construction: the dispatch carries only mechanical
    coordinates — repo location, pinned base SHA + head SHA (merge-base
    rule as in codereview), permission to inspect the repo to discover the
    goal, disposable-worktree isolation, side-effect boundaries, and the
    verdict schema. No plan summary, no areas-to-inspect, no risk
    checklist, no suggested findings, no prior reviewer conclusions, no
    claimed invariants. Plans and finding records remain repository
    evidence the reviewer may discover, not a rubric the caller argues
    from. A clean "yes" is as valid as a well-supported "no".
  - Unit of work: the whole change `base..head` — not per-finding.
  - Verdict envelope (fail-closed, orchestrator computes acceptance, same
    parse rules as codereview):
    `{"verdict":"clean|findings","reviewed_sha":"<head>","base_sha":"<base>",
    "findings":[{"title":…,"evidence":"file:line …","predicted_failure":…,
    "severity":"CRITICAL|HIGH|MEDIUM|LOW","better_approach":…}]}`
    — SHAs must echo the dispatched values; `findings` empty only with
    `clean`.
  - Downstream: returned findings enter intake/triage and the per-finding
    machinery **per the codereview playbook** (pointer, not a copy).
    Reviewer-incantation probing: pointer to codereview's probe-and-verify
    section.
  - Anti-patterns: plan-conformance priming (preloading a checklist,
    suspected risks, preferred mutations, or expected findings turns
    independent review into confirmation); manufacturing findings; treating
    "clean" as a failed pass.
  - One selection note, no heuristic machinery: codereview's rubric suits
    conformance checks and weaker reviewer models; openreview rewards
    stronger reviewers and design-heavy changes; the owner chooses by name.
- Wrappers/skills: add `templates/commands/claude/codereview.md`,
  `templates/commands/claude/openreview.md`,
  `templates/skills/shared/codereview/SKILL.md`,
  `templates/skills/shared/openreview/SKILL.md` (same pointer shape as the
  current review wrapper/skill, marker included); delete
  `templates/commands/claude/review.md`, <!-- plan-lint: allow -->
  `templates/skills/shared/review/SKILL.md`, and <!-- plan-lint: allow -->
  `templates/playbooks/reviewloop.md`. <!-- plan-lint: allow -->
  (`tests/test_templates.py::test_shared_skill_set_mirrors_the_wrapper_set`
  keeps both sides symmetric.)
- `tools/shipped-set.json`: add the six new artifacts (class `replace`,
  empty `formerly`); move to `retired`: `.agents/playbooks/reviewloop.md`
  (its three existing formerly hashes + the outgoing current nhash),
  `.claude/commands/review.md` and `.agents/skills/review/SKILL.md` (each:
  the outgoing current nhash).
- Sweep: `README.md` reviewloop mention; `.agents/repo-guidance.md` earned-
  practice line (repo-owned record; update to name the two playbooks; keep
  the codex-stdin dispatch fact).
- This repo's own installed copies (`AGENTS.md`, `.agents/playbooks/`,
  `.claude/commands/`, `.agents/skills/`, `.claude/settings.json`) are NOT
  touched — self-refresh is owner-only (2026-07-10 decision); installed lag
  is the expected steady state. Ordering note for the owner's next fleet
  refresh: Powershell-Token-Killer's edited reviewloop copy is upstreamed
  by this plan (openreview), so its retirement there loses nothing.

## Slices (one commit each; suite green after each)

1. Design A: refresh strict converge + class rename + manifest comment +
   tests + `docs/design.md` / `docs/usage.md` / update-governance wrapper
   rewording (+ its formerly append).
2. Design B1: the generalized invariant in `templates/AGENTS.template.md`
   (+ formerly append).
3. Design B2: provenance markers on shipped markdown artifacts + structural
   test (+ formerly appends for every edited source).
4. Design B3: blocking hook script + settings PreToolUse + shipped-set entry
   + tests + live check + `docs/harness-capabilities.md` record.
5. Design C: playbook split + wrappers/skills + shipped-set adds/retires +
   README + repo-guidance sweep.
6. Close: flip the two 2026-07-16 decisions entries to Adopted and archive
   them per the lifecycle (canonical homes: refresh.py behavior + manifest
   comment; the template invariant; the two playbooks); set this plan's
   Status to CLOSED with the commit map; update `.agents/state.md`.

## Verification

- `python3 -m unittest discover -s tests -v` after every slice (Windows:
  `py -3 -m unittest discover -s tests -v` from Git Bash).
- Plan-touching commits: `python3 -m unittest tests.test_plan_lint -v`.
- New/flipped tests get guard proofs (revert the change on a throwaway
  basis, confirm red, restore, confirm green) — hermetic fixtures only.
- Hook: unit tests via fixture stdin; bounded live `claude -p` check with
  the result recorded either way.
- Docs-only slices: `git diff --check`.
