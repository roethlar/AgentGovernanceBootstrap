# Content-First Discovery & Gitignore Reconciliation — Design

- Date: 2026-06-24
- Status: **Proposed** (awaiting owner approval; no code written yet)
- Supersedes/refines: the deferred incident_june routing fix; generalizes the
  2026-06-18 "repair the gitignore" decision; aligns with the 2026-06-10
  gitignore-aware custody decision.
- Revision: 2026-06-24 — incorporated an external (GPT) review: split findings
  and actions by *actual* custody (untracked ≠ ignored; `.gitignore` cannot
  untrack a committed file); labeled local-only as a tradeoff, not an equivalent
  install; added hard traversal exclusions; moved tests to travel per slice.

## 1. Motivation

`tools/discover.py` decides what governance a repo has by reading the repo
*through git's ignore lens*: its file inventory comes entirely from
`git ls-files` / `git status --ignored`, and routing keys off whatever those
report. But **correcting a wrong `.gitignore` is part of this toolkit's job**
(2026-06-18). A process that exists to fix the git config cannot treat the
current git config as the authority for what governance exists — that is
circular, and it makes the tool blind to the exact misconfiguration it is meant
to catch:

- A repo that wrongly gitignores its real `.claude/` command wrappers reads as
  "no governance" (or, worse, the wrappers vanish into git's collapsed `.claude/`
  entry and are never seen).
- A machine-local `.claude/settings.local.json` that is correctly ignored reads
  as "existing governance," sending a brand-new repo down the migration path
  with nothing to migrate (the incident_june bug).

Both are symptoms of the same root cause: **git's current state is the patient,
not the doctor.** Discovery must determine what governance exists, and what
custody things *should* have, from on-disk content — and then surface the
git-config mismatches as findings for the human to decide.

Owner mandate (2026-06-24): the discovery and bootstrap process must be
**thorough and complete** — "new repo, old repo, someone else's repo" must all
work, 100% of the time; anything left out or missed is a bug. **Efficiency and
speed are explicitly not requirements. Completeness is.** It must scan for any
language and anything else that needs to be accounted for in governance.

## 2. Goals

1. Determine governance and desired custody from **on-disk content, independent
   of git's ignore state**. Git custody is recorded as a per-path *attribute*,
   never the filter for what counts as governance.
2. **Reconcile `.gitignore` in both directions**, as human-reviewed findings,
   with the action chosen by the file's *actual* custody (see §4):
   - governance/source wrongly **ignored** → propose un-ignore + commit;
   - junk **untracked & un-ignored** → propose an ignore rule;
   - junk already **committed** → propose `git rm --cached` + ignore rule;
   - a **committed secret** → escalate (in history; rotate/scrub, not just ignore).
3. **Language-agnostic completeness** via an extensible category catalog; adding
   an ecosystem is adding data, not code.
4. **Human decides every finding.** Keeping vital governance paths ignored is a
   legitimate owner choice that yields a **local-only governance install** — an
   offered, accepted outcome. Per 2026-06-18 the *recommended* end state is
   durable, committed wrappers; so the packet presents local-only honestly as a
   **portability / rule-exception tradeoff** (the wrappers will not travel to
   other machines or agents, weakening the operator-command guarantee), not as an
   equivalent successful install. The toolkit offers and records the choice; it
   never makes it for future users.
5. Preserve existing strengths: custody-aware commit contract (no silent
   `git add -f`), fail-loud git-error surfacing (`git.errors`/`git.degraded`),
   sensitive-file detection, CI/verification detection.

## 3. Non-goals

- Auto-editing `.gitignore`, running `git rm --cached`, or committing anything
  without explicit owner approval through the normal approval summary.
- Resolving the separate update-vs-migration "is this repo our own prior work"
  ownership question (the `bootstrap.config.json` open item). Content-first
  detection makes its markers more honest, but that decision stays out of scope
  here.
- Rewriting git history to purge an already-committed secret. We detect and
  escalate; the scrub itself is an owner action with its own tooling.
- Enforcing any particular ignore policy or overriding owner intent.
- Performance/efficiency tuning. A complete-but-slow scan is acceptable.

## 4. Core model: desired-custody reconciliation

Every discovered path is tagged with one or more **categories**; each category
declares a **desired custody**. Discovery independently records each path's
**actual** git custody — `tracked`, `untracked` (in the tree, not added, not
ignored), or `ignored` (git actively excludes it); everything is `untracked` in
a non-git repo. A finding is the *pair* (desired, actual), and the action
depends on both — because `.gitignore` only affects untracked files and cannot
untrack something already committed.

The full matrix (only mismatches are findings):

| Category (desired custody) | Actual: `tracked` | Actual: `untracked` | Actual: `ignored` |
|---|---|---|---|
| governance / source / config / lockfiles (`tracked`) | OK | `untrackedCandidate` (advisory) | **`wronglyIgnored`** → propose un-ignore + commit, or owner accepts local-only (labeled tradeoff) |
| caches / build / deps / compiled / logs / coverage (`ignored`) | **`trackedJunk`** → `git rm --cached` (untrack, keep on disk) + ignore rule | **`shouldBeIgnored`** → add ignore rule | OK |
| secrets (`ignored` + alert) | **`committedSecret`** → escalate: in history, recommend rotation/scrub; ignore-forward alone is insufficient | **`shouldBeIgnored`** + sensitivity alert | OK (still surfaced as sensitive) |
| editor / OS / intent-dependent (`review`) | **`review`** | **`review`** | **`review`** |

Notes on the corrected classes:

- **`wronglyIgnored`** requires actual custody = `ignored` (git is actively
  excluding a tracked-desired path). It is *not* triggered by merely untracked
  files — an ordinary new, uncommitted source/config file is normal work, not a
  `.gitignore` defect.
- **`untrackedCandidate`** (desired `tracked`, actual `untracked`) is advisory
  and low-signal. It is meaningful chiefly for governance/config artifacts the
  process itself is staging (handled by the normal copy+commit flow); for
  arbitrary untracked source it is suppressed by default to avoid noise.
- **`trackedJunk`** and **`committedSecret`** exist because adding a `.gitignore`
  rule does nothing to an already-tracked file. Untracking needs
  `git rm --cached` (keeps the file on disk); a committed secret additionally
  needs a rotation/history-scrub alert because the value is already in history.
- **`review`** is never auto-resolved; it is surfaced for an owner call.

This is the robust generalization the owner asked for: **one reconciliation
engine, a data catalog of categories, a per-(desired×actual) action, and a human
decision on each mismatch.**

## 5. Enumeration rework

- **Walk the filesystem for truth.** Enumerate real paths on disk rather than
  trusting git's report. This eliminates the git-collapse blind spot (git
  collapses a fully-ignored directory to a single `dir/` entry, hiding its
  contents); we now see what is actually inside an ignored `.claude/`.
- **Custody as an attribute.** For a git repo, annotate each path's custody by
  querying git (`git ls-files`, `git check-ignore`, `git status`). Custody never
  filters governance detection; it only feeds the reconciliation.
- **Detect-and-prune known artifact directories.** When the walk reaches a
  catalog-known dependency/build dir (e.g. `node_modules/`, `.venv/`,
  `target/`), record the directory as a single node (with its category and
  custody) and do **not** recurse into it. Completeness without pathological
  walks — a completeness decision, not an efficiency one.
- **Hard traversal exclusions & safety (must be defined before coding).** The
  raw walk needs explicit rules that the current git-based inventory got for
  free:
  - skip `.git/` (today implicit; the non-git branch already excludes it at
    `discover.py:638-641`);
  - skip `.bootstrap-tmp/` (today via `strip_scratch`, `discover.py:223-225`);
  - **do not descend into a nested repository / submodule** (a child directory
    containing its own `.git`): record it as a boundary node and stop — its
    governance and ignore state are its own concern, not this repo's;
  - **do not follow symlinks** (avoid cycles and walking outside the repo root);
    record the link itself.
- **Preserve fail-loud git behavior.** The recent `run_git` work surfaces git
  failures into `git.errors` / `git.degraded`; the reworked enumeration must keep
  an empty/failed git result from masquerading as a clean repo.

## 6. The category catalog (completeness core)

A data-driven, extensible table. Each row:

```
{ id, patterns[], desiredCustody, rationale, findingLabel, ecosystem? }
```

Seed categories (representative, not exhaustive — the catalog is the artifact we
grow):

- **governance/agentic** → `tracked`: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
  `.agents/**`, `.claude/commands/**`, committed `.claude/settings.json`, hook
  configs, `.cursor/**`, `.cursorrules`, `.aider*`, other harness dirs.
- **machine-local harness state** → `ignored`: `.claude/settings.local.json` and
  the per-machine state files of other harnesses.
- **source/config/lockfiles** → `tracked`: lockfiles (`package-lock.json`,
  `Cargo.lock` for apps, `poetry.lock`, `go.sum`), build manifests, `.env.example`.
- **caches/build/deps/compiled** → `ignored`, sourced for *any language* from the
  community `github/gitignore` template corpus, distilled into the catalog:
  - Python: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `.pytest_cache/`,
    `.mypy_cache/`, `.ruff_cache/`, `*.egg-info/`, `build/`, `dist/`
  - Node/JS: `node_modules/`, `dist/`, `.next/`, `.nuxt/`, `coverage/`
  - Rust: `target/`
  - JVM (Gradle/Maven): `build/`, `.gradle/`, `target/`
  - Go: compiled bins, `vendor/` (policy-dependent → may be `review`)
  - .NET: `bin/`, `obj/`
  - C/C++: `*.o`, `*.so`, `*.a`, `*.out`
  - Ruby/PHP/Swift/Elixir/Haskell/…: their standard derived dirs
  - General: `*.log`, `.cache/`, `tmp/`, `*.tmp`
- **secrets/sensitive** → `ignored` + alert: extends existing
  `SENSITIVE_GLOBS` / `SENSITIVE_REGEXES` (`.env`, `*.pem`, key material).
- **editor/OS cruft** → `review`: `.DS_Store`, `Thumbs.db`, `.idea/`, `.vscode/`
  (often intentionally committed → human decides).

Completeness strategy: the `caches/build/deps` rows are mined from
`github/gitignore` (covers essentially every ecosystem) during implementation,
then maintained as data. "Scan for any language" = the catalog spans languages;
adding one is one row.

## 7. `.gitignore` reconciliation

- Parse the repo's `.gitignore` (root), nested `.gitignore` files, and account
  for git's global excludes, so findings reflect what git will actually do.
  (Depth is open decision **D2** below.)
- For each category, compare desired custody against actual git custody and emit
  the finding/action from the §4 matrix. Each finding carries: `path`,
  `category`, `currentCustody`, `desiredCustody`, `findingClass`,
  `suggestedAction`, `rationale`.

## 8. Outputs

- **Manifest**: add `gitignoreFindings`, keyed by class:
  `{ wronglyIgnored[], shouldBeIgnored[], trackedJunk[], committedSecrets[],
  untrackedCandidates[], review[] }`, plus per-path `categories`. Keep existing
  fields.
- **Review packet / approval summary**: a new **"Gitignore Reconciliation"**
  section, plain English, grouping findings by class, each with an explicit owner
  decision and the action implied by its custody (add-ignore vs `git rm --cached`
  vs un-ignore+commit vs rotate-secret). Where governance paths are proposed for
  un-ignoring, state the **local-only governance install** alternative *and* its
  portability/rule-exception tradeoff (§2.4), so the owner chooses with the cost
  visible; durable committed wrappers are named as the recommended default.
- **Routing**: `compute_route` consumes content-detected governance markers
  (custody-independent), so an ignored machine-local file no longer flips a fresh
  repo to migration, and an ignored real wrapper is still detected (and raised as
  a `wronglyIgnored` finding) instead of vanishing.

## 9. Backward compatibility

- The enumeration change alters manifests; the golden fixtures
  (`tests/...golden`) will be regenerated and reviewed.
- The incident_june fixture (`.claude/settings.local.json` only) now routes
  greenfield with no governance, and produces no finding because the file is
  already correctly ignored.
- A fixture with an *ignored* `.claude/commands/*.md` now routes migration **and**
  raises a `wronglyIgnored` finding (the 2026-06-18 case, handled correctly).
- A committed `.claude/commands/*.md` still routes migration (unchanged).
- A committed build dir or `.env` now raises `trackedJunk` / `committedSecret`
  respectively — new findings that did not exist before.

## 10. Verification

- Tests travel **with each behavior slice** (see §11), not deferred to the end.
  Explicit cases for: each finding class in the §4 matrix; the incident_june and
  2026-06-18 cases as opposite outcomes of the same engine;
  untracked-source-is-not-a-finding; `trackedJunk` vs `shouldBeIgnored`
  divergence; committed-secret escalation. Revert-proof each behavioral guard
  (revert the fix, confirm the test fails, restore).
- Manual smoke: run the reworked discovery against this repo and 1–2 real
  external repos (e.g. headroom, roon-controller) and eyeball the findings for
  false positives/negatives.
- `python3 -m unittest discover -s tests -v` is the gate.

## 11. Commit slicing (one item per commit; tests travel with their slice)

1. Category catalog as data, **with unit tests for the catalog/classifier** (no
   enumeration change yet).
2. Filesystem-truth enumeration + custody-as-attribute + traversal exclusions
   (`.git/`, `.bootstrap-tmp/`, submodules, symlinks), **with its own tests** and
   preserved fail-loud git behavior.
3. Desired-custody reconciliation engine + manifest `gitignoreFindings`, **with
   per-class tests** (incl. untracked-source-is-not-a-finding, `trackedJunk`,
   `committedSecret`).
4. `compute_route` consumes content markers; incident_june/2026-06-18 cases,
   **with their tests**.
5. Review-packet + approval-summary "Gitignore Reconciliation" section +
   local-only tradeoff wording, **with packet tests**.
6. Procedure references (`bootstrap.md`, `migration.md`) to the findings + the
   local-only outcome.
7. Regenerate golden manifests (mechanical churn consolidated here, since the
   manifest shape settles across the earlier slices).

## 12. Open design decisions (owner input requested)

- **D1 — junk corpus basis.** Base the `shouldBeIgnored` catalog on the
  `github/gitignore` template repo (community-maintained, ~every ecosystem),
  distilled into our data table. *Recommend yes.*
- **D2 — `.gitignore` parsing depth.** Root-only vs root + nested `.gitignore`
  + global-excludes awareness. Completeness argues for the fuller form.
  *Recommend nested + global-aware.*
- **D3 — ambiguous categories.** Editor/OS configs (`.vscode/`, `.idea/`) are
  surfaced as `review` findings, never auto-classified as junk. *Recommend yes.*
- **D4 — scope boundary.** Keep the update-vs-migration "is this ours" ownership
  question out of this plan. *Recommend yes (separate open item).*

## 13. Relationship to existing canon

- **Generalizes** the 2026-06-18 "repair the gitignore" decision from the
  wrappers-only case to all categories, via one reconciliation engine; keeps its
  "durable committed wrappers are the correct end state" stance by labeling
  local-only as a tradeoff rather than an equal outcome.
- **Aligns** with the 2026-06-10 gitignore-aware custody decision: respect owner
  intent, never silent `git add -f`, custody proven by git query.
- **Closes** the incident_june bug as a special case of the general engine.
- **Adjacent** to open items #1 (`bootstrap.config.json` ownership marker) and
  #3 (monorepo subdir path matching); neither is resolved here.

## 14. On approval

Record a decision in `.agents/decisions.md` capturing the architectural shift
(content-first discovery; desired-custody reconciliation split by actual custody;
local-only install as an offered-but-labeled tradeoff), then implement per the
commit slicing above.
