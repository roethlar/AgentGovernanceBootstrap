# Discovery Manifest Schema

Field-by-field reference for `repo-discovery-manifest.json`, written by
`discover.py`. Read this instead of guessing key names. All file paths are
repo-root-relative POSIX strings. Every marker list is a mechanical
name-match: a lead to verify, never a fact to record in durable guidance.

- `generatedAt` (string): ISO-8601 UTC timestamp of the discovery run.
- `validated_against` (object): snapshot identity for drafts -
  `commit` (string or null) and `date` (`YYYY-MM-DD`).
- `repo` (object): `root` (absolute path of the scanned repo) and `scope`
  (`"."`, or the subdirectory discovery was pointed at).
- `git` (object):
  - `isGitRepository` (bool).
  - `branch` (string or null): current branch from `git rev-parse
    --abbrev-ref HEAD`.
  - `commit` (string or null): current `HEAD` sha.
  - `status` (array of strings): raw `git status --short` lines. The packet's
    "Dirty entries" count is this array's length.
- `coverage` (object): `status` (`"complete"` or `"truncated"`),
  `candidateCount` (files seen), `includedCount` (suggested reads kept),
  `cap` (truncation threshold).
- `route` (string): `"greenfield"` (no existing governance) or `"migration"`
  (any existing governance, including a repo already on the standard layout —
  the single-route collapse, 2026-06-28).
- `agentsTemplate` (object): whether the target's `AGENTS.md` is behind the
  current template. Drives the migration route's reconciliation branch.
  - `currentVersion` (string or null): the `<!-- templateVersion: ... -->`
    stamp in the toolkit's `templates/AGENTS.template.md`. Bump this stamp
    whenever the template's structural contract changes (sections, the Prime
    Invariants block, the operator set). A forgotten bump is backstopped by
    `missingSections`.
  - `targetVersion` (string or null): the same stamp read from the target
    repo's `AGENTS.md`; null when absent (the file predates versioned
    templates).
  - `reconcileRecommended` (bool): true on the `migration` route when
    `targetVersion` differs from `currentVersion` (including when absent) or
    the section probe found missing structure. The reconciliation branch
    updates `AGENTS.md` to the current template before the operator-wrapper
    and hook guarantees run. Always false on greenfield, which drafts
    `AGENTS.md` fresh.
  - `missingSections` (array of strings): mechanical probe of the target
    `AGENTS.md`, populated only on the `migration` route - tokens like
    `"prime-invariants-block"` and `"operator:playbook"` for structure the
    file lacks. A lead for reconciliation, never a durable fact.
- `bootstrapRepoPath` (string): bootstrap repo the pack was copied from.
- `harvestRepoPath` (string or null): owner's machine-local harvest dropbox,
  if configured.
- `projectMarkers` (array of paths): build/project files by name-match.
- `ciMarkers` (array of paths): CI files in provider-executable locations
  only (`.github/workflows/`, root `.gitlab-ci.yml`, root
  `azure-pipelines.yml`). Location alone still does not prove CI runs -
  check branch triggers and provider settings before recording CI as a fact.
- `suspectedMisplacedCi` (array of paths): CI-named files in locations no
  provider executes (for example a root-level `ci.yml`). Treat as inactive
  unless proven otherwise.
- `ciBranchMismatches` (array of objects): heuristic scan of `branches:`
  filters in the files above; each entry has `path`, `branches` (the trigger
  list found), and `currentBranch`. A listed file likely never runs on the
  current branch. Absence of an entry is not proof CI runs.
- `agentMarkers` (array of paths): harness/agent control files by name-match.
- `governanceMarkers` (array of paths): governance-system files by
  name-match; these drive `route`.
- `verificationCandidates` (array of objects): `command` and `source`
  (where it was found). Mechanical and unconfirmed.
- `likelySensitivePaths` (array of objects): `path`, `source`, `reason`.
  Flagged by name only; never suggested for reading.
- `suggestedReadPaths` (array of paths): what the drafting agent should read
  directly from the repo.
- `excludedSuggestedReadPaths` (array of objects): `path`, `reason` - marker
  paths withheld from the read list (sensitive, ignored, or directories).
- `trackedFiles`, `untrackedFiles`, `ignoredFiles` (arrays of paths): git
  custody at scan time, from `git ls-files`, `git ls-files --others
  --exclude-standard`, and `git status --ignored --short` respectively.
  `ignoredFiles` may list a directory (for example `.claude/`) rather than
  each file inside it. Use these (or live `git check-ignore`) to set
  `custody` values - never path convention. A directory shown here is not a
  custody verdict for new child paths: git collapses both a directly-ignored
  directory and one whose current children are each ignored to the same `dir/`
  entry, so run `git check-ignore` on the exact final path before deciding it.
