# Phase 0 — eval harness hardening

Status: **IMPLEMENTED 2026-06-28** (S1–S7 landed, commits 2bcf6ae..on master).
Scope: code + tests under `tools/`, `evals/`, `tests/`. No model/treatment runs.
Plan owner reference: `evals/TEST-PLAN.md` §10 (Phase 0 list), §15 (resume).

## S7 live-smoke result (2026-06-28, reported not recorded)

Driver `ollama:glm-5.2:cloud` via the `:8788` Anthropic-compatible proxy, fixture
`py_duration_parser`, three profiles. (The local `qwen3.6:27b-mlx` returned empty
completions and was not used; the cloud model worked cleanly.) All three trials
FuncPassed and validated the new telemetry end-to-end:

| profile | func | changed_files | tokens | cost | hooks present/sup/fired | profile_tokens |
|---|---|---|---|---|---|---|
| none | pass | `[duration.py]` | 432104 | 2.199 | F / T / None | 0 |
| hook-smoke | pass | `[duration.py]` | 739484 | — | **T / T / T** | 71 |
| current-template | pass | `[duration.py]` | 445934 | 2.268 | F / — / None | 3396 |

Confirmed live: S1 — overlaid governance (`AGENTS.md`/`CLAUDE.md`/`.claude/settings.json`)
never appears in `changed_files`; S2 — strip clean; S3 — real `--output-format json`
usage parsed (tokens/cost), raw streams redacted, transcript in the **gitignored**
tree (`git check-ignore` ✓); S4 — the hook-smoke `.claude` hook actually **fired**
against live Claude Code (`hooks_fired=True`) and the external sentinel stayed out of
`changed_files`. Smoke result JSONs + transcripts were deleted afterward (Phase 0
produces no treatment data).

Phase 0 makes the harness produce trustworthy per-trial telemetry *before* any
decision-grade runs. Each slice is independently committed and unit-tested
(mutation-proven where a new test guards a behavior change), per the repo's
verification rule.

## Why now

The screening runs were exploratory. Before Phase 1 freezes a fixture set and
Phase 2 collects data, the instrument must (a) not contaminate the clean
baseline, (b) attribute changes to the agent correctly, and (c) capture enough
per-trial signal (cost, tool calls, hook firing) that a governance effect can be
read and audited rather than inferred.

## Revision note (2026-06-28, post-codex-review)

Two adversarial codex passes. Round 1: 10 findings (verdict REVISE), all folded
in. Round 2 (on the revised plan): all 10 confirmed RESOLVED, plus three new
findings — R2-#1 (BLOCKER: raw stdout would still leak into the *tracked* result
JSON despite the gitignored transcript file → explicit redaction step + test),
R2-#2 (strip must use a deletion-safe *subset*, not the full detection list, since
the latter includes generic docs a product repo may ship), R2-#3 (the live smoke
needs a hook-installing profile to exercise `hooks_fired==true`). All three folded
in. Each finding was verified against the actual code before acceptance, not taken
on the reviewer's word. Material changes from round 1: Each was verified against the actual code before
acceptance, not taken on the reviewer's word. Material changes: slices reordered
so governance-strip runs *before* patches (was a sequencing bug); a profile
collision guard added to S1; the S2 strip reuses `discover.py`'s existing
`GOVERNANCE_MARKER_PATTERNS` classifier instead of a fresh denylist; transcripts
moved out of `evals/results/` (a documented policy violation) to a gitignored
tree; the hook sentinel moved outside the worktree (it would have re-introduced
the very S1 contamination this plan fixes); `hooks_active` split into
present/supported/fired; parser fixtures checked in; and a result-schema version
added so legacy results never silently mix with Phase-2 telemetry.

## Canonical trial pipeline (pinned)

`score_fixture` must execute in exactly this order; several findings below turn
on it:

```
scaffold
  → strip pre-existing governance        (S2; before any patch)
  → apply test patch / solution patch    (oracle/gold only)
  → overlay governance profile           (S1; with collision guard)
  → isolate_history  → commit trial-base (governance now IN the baseline)
  → setup steps
  → driver (agent edits; changed_files measured here)
  → verify  → hidden test
  → post-run telemetry harvest (transcript/tokens/hooks_fired, from OUTSIDE worktree)
```

## Slices (one commit each)

### S1 — changed_files / tamper artifact fix + profile collision guard  *(the named Sec-10 bug)*

**Defect.** `score_fixture` overlays the governance profile *after*
`isolate_history` commits `trial-base` (run_fixture.py:315–316). The overlaid
files are untracked at agent time, so `drivers._changed_files`
(`git status --porcelain`, drivers.py:56) reports them as agent edits. This
inflates `changed_files`, corrupts "did the agent touch governance", and is a
latent false-tamper source.

**Fix.** Overlay the profile *before* `isolate_history`, so governance is part of
the `trial-base` baseline the diff is measured against. Governance is
environment, not agent work; the agent still cannot crib (no source history
survives re-init). `profile_files`/`profile_hash` come from the returned overlaid
list and are order-independent.

**Collision guard (codex #1).** Committing overlay into trial-base could let a
malformed profile silently overwrite a product or test file — the new baseline
would then hide that mutation from `changed_files`. Before overlaying, assert each
profile destination path is either (a) not already present in the workdir, or
(b) in the governance set stripped by S2. A profile that would overwrite a
surviving product/test file raises `ValueError` (fail-closed). `_safe_dest`
already blocks path escape; this adds an overwrite check.

**Test (mutation-proven).** Driven oracle fixture under a profile overlaying a
known file (`current-template` → `AGENTS.md`): assert `AGENTS.md` is **not** in
`driver.changed_files` and a file the fake driver edits **is**. Revert the
ordering → test fails. Separate test: a synthetic profile whose dest collides
with an existing product file raises `ValueError`. Mutation on a throwaway copy
per the hermetic-mutation rule.

### S2 — strip pre-existing governance, reusing the discover.py classifier  *(clean-baseline guarantee)*

**Goal.** A `none`-profile trial must start from a repo with *no* agent
governance, regardless of what the source repo carried — the harness must not
depend on hand-cleaning.

**Fix (codex #2, #3, R2-#2).** Strip immediately after scaffold and **before** any
test/solution patch (so an injected fixture file can never be deleted by the
strip; and if a fixture's declared `test_paths`/`solution_paths` intersect the
governance set, fail loudly unless the manifest explicitly opts in).

*Deletion-safe subset, not the whole detection list (R2-#2, SHOULD-FIX).*
`discover.GOVERNANCE_MARKER_PATTERNS` (discover.py:73) is a *detection* list and
is broader than what is safe to **delete**: it includes generic doc names —
`state.md`, `docs/state.md`, `decisions.md`, `docs/decisions.md`, `devlog.md`,
`review.md`, `.review/*`, `docs/agent/*` — that a product repo could legitimately
ship as its own documentation. Deleting those would corrupt a fixture. So the
strip set is an explicitly enumerated **deletion-safe subset**: the unambiguous
agent-instruction artifacts only — `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
`.cursorrules`, `.cursor/rules/*`, `.aider*`, `.claude/*`, `.antigravitycli/*`,
and `.github/copilot-instructions.md`. This subset is a named constant in the eval
code, each entry justified in a comment, with a pointer to
`GOVERNANCE_MARKER_PATTERNS` noting that the detection list is intentionally a
superset (we detect more than we delete). The generic-doc markers are *detected*
(reported) but never auto-deleted; a fixture that truly needs one stripped names
it via `manifest["strip_governance"]` (explicit opt-in), and any path can be
preserved via `manifest["keep_governance"]`.

The classifier matches *governance* (instructions to the agent), never product
code: it is path/glob-based on known governance locations, so headroom's
`providers/claude/*.py` and rtk's `hooks/claude/*` (product) are untouched.
Record `stripped_governance_files` in the result. A fixture may keep a
governance-named path that is genuinely its subject via
`manifest["keep_governance"]` (exact relpaths).

**Test.** Synthetic source repo with `AGENTS.md`, `.github/copilot-instructions.md`,
`.claude/settings.json`, product files `providers/claude/x.py` +
`hooks/claude/run.sh`, **and** a generic doc `docs/state.md`: assert the three
deletion-safe governance items are gone, both product files remain, and
`docs/state.md` **also remains** (detected-but-not-deleted — guards the
detection-superset / deletion-subset distinction). Assert `stripped_governance_files`
lists exactly the three deleted. Second test: `none`-profile scaffold leaves zero
*deletion-safe-subset* matches (assert-clean). Third: `keep_governance` preserves
a named path; `strip_governance` deletes a named generic-doc path that the subset
would otherwise spare. Mutation: disable strip → assert-clean fails; mutation:
widen the subset to the full detection list → the `docs/state.md`-survives
assertion fails.

### S3 — driver telemetry capture (transcript + tool-calls + cost + tokens)

**Goal.** Each driver result carries, where obtainable: a captured transcript,
tool-call count, token usage, and cost. Today drivers return only
`{driver, exit, duration_sec, changed_files, error_tail}`.

**Approach (codex #5, #6, #9, R2-#1).**
- *Storage ownership.* `score_fixture` (not the driver) owns transcript storage —
  the driver returns raw stdout/stderr in its result dict; `score_fixture`, which
  knows `id`/`profile`/`run_id`, writes the transcript file and records its path +
  byte length. (The current driver contract at run_fixture.py:333 passes no
  profile/run_id, so a driver cannot name the file itself.)
- *Raw-field redaction (R2-#1, BLOCKER).* After writing the transcript file,
  `score_fixture` must **delete the raw stdout/stderr keys from the driver dict**
  before that dict is recorded. Otherwise the gitignored transcript file is moot:
  `run_trials.py:46` and `run_fixture.py:421` serialize the whole result dict into
  a *tracked* `evals/results/*.json`, which would then carry the same
  transcript/source/secret-bearing text. The recorded JSON keeps only
  `transcript_path` + `transcript_bytes` + parsed telemetry (`tool_calls`,
  `tokens`, `cost`) and the short `error_tail`, never the full raw streams.
- *Location.* Transcripts go to a **gitignored** `evals/results/transcripts/`
  (new `.gitignore` entry — repo currently has none for evals; `evals/README.md`
  states results hold scores/SHAs, *not* repo contents or transcripts, so writing
  trial code under a tracked path would violate stated policy and risk committing
  source/prompts/secrets). The slice adds the `.gitignore` line and a README note.
- *Parsers.* A shared finalize helper extracts `tool_calls`/`tokens`/`cost` per
  harness (Claude `--output-format json` / stream-json usage; codex/grok from
  stdout). Unavailable field → explicit `null` (absence is data).

**Test (codex #9, R2-#1).** Checked-in sample stdout / stream-json fixtures for
claude/codex/grok under `tests/golden/driver_output/`; unit-test each parser
extracts the right tool_calls/tokens/cost. Plus a `score_fixture`-level test (fake
driver returning canned raw stdout) asserting the transcript file is written under
the gitignored tree, the result records `transcript_path` + `transcript_bytes`,
and — the redaction guard — that the **recorded result dict contains no raw
stdout/stderr key** (the canned secret string must not appear anywhere in the
serialized JSON). Mutation: skip the redaction → that assertion fails. Live
validation is S7, not the only guard.

### S4 — hook telemetry: present / supported / fired

**Goal.** For hook-installing profiles (the mechanism screening flagged as the one
that transfers), record hook state per trial.

**Approach (codex #4, #8).** Three explicit fields, not one ambiguous
`hooks_active`:
- `hooks_present` — derived structurally from `profile_files` (overlay included a
  `.claude/settings.json` / hook script). Cheap, exact, no runtime.
- `hooks_supported_by_driver` — whether the driver's harness honors that hook kind
  (Claude Code yes; codex/grok per their own hook support). Avoids reporting an
  inert hook as active on a harness that ignores it.
- `hooks_fired` — best-effort, from a sentinel the hook writes **outside the trial
  worktree** (e.g. `$AGB_HOOK_SENTINEL` pointing at a temp path `score_fixture`
  creates and reads). Writing the sentinel *inside* the workdir would reappear in
  `driver.changed_files` and re-create the S1 contamination — so the sentinel is
  deliberately external. `null` when no firing signal exists.

**Test.** Profile with a hook overlay → `hooks_present` true; `none` → false. A
fake driver that writes the external sentinel → `hooks_fired` true, and a
regression assertion that the sentinel path never appears in
`driver.changed_files`. Mutation: drop the present-derivation → assertion fails.

### S5 — token-accounted proportionate-governance injection

**Goal.** Sec-10's "proportionate-governance injection with token accounting":
record per-trial the governance token weight injected, so a FuncPass collapse can
be checked against governance heaviness (the screening confound).

**Approach.** Add `profile_tokens` to the result — a transparent, dependency-free
estimate (documented heuristic, not a tokenizer) over the overlaid governance
bytes. For cross-profile *proportionality*, a consistent estimate suffices; billed
cost comes from S3's per-harness usage where available.

**Test.** `none` → `profile_tokens == 0`; `current-template` → positive count
matching the heuristic. Mutation: hardcode 0 → current-template assertion fails.

### S6 — aggregate.py consumes new telemetry + result schema version

**Goal (codex #7, #10).** The new fields are useless if the aggregator ignores
them and dangerous if legacy results mix with Phase-2 telemetry silently.

**Approach.**
- Add `schema_version` to every result `score_fixture` writes; bump it this slice.
- `aggregate.py` gains per-(fixture,profile) summaries: transcript-present count,
  token/cost/tool-call availability counts, `hooks_present`/`supported`/`fired`
  counts, mean `profile_tokens`, and — critically — a **missing-telemetry / mixed-
  schema count** so a table that blends old and new records says so out loud
  rather than averaging across incomparable rows.

**Test.** `aggregate` over a mixed list (one legacy record with no
`schema_version`, one current) reports the correct mixed-schema count and does not
crash on absent fields; new-telemetry columns populate from the current record.
Mutation: drop the missing-count → the mixed-list assertion fails.

### S7 — smoke: one live driven trial end-to-end

Not a unit test (needs a model) — a documented manual smoke: drive **one** cheap
local ollama model on **one** oracle fixture under three profiles: `none`,
`current-template`, and a small **hook-installing smoke profile** added for this
slice (overlays a trivial `.claude/settings.json` whose hook writes the external
`hooks_fired` sentinel). The prose profiles (`none`/`current-template`) overlay no
hook, so they can only exercise `hooks_fired==false/null`; the hook profile is
what exercises `hooks_fired==true` (R2-#3 — without it the firing path is never
hit live). Confirm: real-output parsers (S3) populate tool_calls/tokens/cost or
explicit null; transcript lands in the gitignored tree and the recorded JSON
carries no raw streams; `hooks_present`/`fired` correct across the three;
`changed_files` clean of governance (incl. the sentinel); aggregator renders the
new columns. Reported in the final response + handoff, **not** recorded as trial
data (Phase 0 produces no treatment data). The smoke profile is committed (it is a
test artifact, not treatment data).

## Verification (every code slice)

```
python3 -m unittest discover -s tests -v
```

Plus the mutation proof per slice (revert the fix on a throwaway copy, watch the
new test fail, restore). S7 is the one manual smoke; its output is reported, not
recorded as a trial result.

## Out of scope (explicitly)

- No Phase 1 fixture construction, no fixture freeze, no treatment runs.
- No new governance profiles.
- The deferred `discover.py operator:playbook` false positive (separate item).
- Per-harness usage-parsing completeness beyond the checked-in sample fixtures
  (S3) + one live call (S7); hardening every CLI output format is iterative and
  not Phase-0-blocking.
- Retrofitting `schema_version` onto historical `evals/results/*.json`; legacy
  records are reported as mixed-schema, not rewritten.

## Settled review questions

- **Strip classifier (was open Q1):** an explicitly enumerated **deletion-safe
  subset** of unambiguous agent-instruction artifacts (named eval constant,
  pointer to `discover.GOVERNANCE_MARKER_PATTERNS` noting detection is a deliberate
  superset). Generic docs are detected but not auto-deleted; per-fixture
  `keep_governance`/`strip_governance` overrides. Settled by codex #2 + R2-#2.
- **Transcript retention (was open Q2):** gitignored `evals/results/transcripts/`,
  path+bytes recorded in the result. Settled by codex #6 (tracked path violated
  stated policy).
- **Hook firing (was open Q3):** external sentinel, never inside the worktree.
  Settled by codex #4 (in-worktree sentinel re-creates the S1 bug).
