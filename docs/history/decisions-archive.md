# Agent Decisions — Archive

This file is the provenance log for decisions that are no longer in force as
live rules: entries that have been **Adopted** (their rule now lives in its
canonical home — a template, procedure, or the active `.agents/decisions.md`
Decisions section) or **Superseded**. Wording is preserved verbatim; nothing is
summarized or dropped. The live decisions doc is `.agents/decisions.md`.

These entries were rotated out of `.agents/decisions.md` on 2026-06-21 when the
repo's own governance was brought current with the product, per the
status-based decisions-archiving rule (`templates/decisions.template.md`). They
originated as the "Open Decisions" queue; all were adopted by 2026-06-21.

---

## Open Decisions (deferred - not yet adopted)

These are assessed findings the owner chose to record for a future decision
rather than implement now. The process is unchanged until one is adopted. Each
states the verified evidence, the options, and the standing recommendation.

### 2026-06-15 - Command wrappers are created only on the migration route

Status: Adopted 2026-06-18 (see "Operator command wrappers are a standing
guarantee on every route" in Decisions above). The finding below is retained as
the rationale that led to it.

Finding:
The operator vocabulary (`catchup`, `handoff`, `drift`, `decision`, `plan`) is
defined in the universal `templates/AGENTS.template.md` "Operator Requests"
section, so every bootstrapped repo advertises these words. The harness command
wrappers that make them work as slash commands (for Claude Code,
`.claude/commands/<name>.md`) are created in exactly one place: `migration.md`
Step 4.2. The greenfield workflow in `bootstrap.md` creates only the harness
shim, not wrappers; the update route delegates to the repo's own Bootstrap
Handoff rule (template steps 1-11), which never mentions wrappers. Result: a
repo bootstrapped greenfield or maintained via update carries the vocabulary in
prose but has no working commands. The operator words still function as
plain-language requests on every route; the missing piece is the slash-command
affordance, not process authority.

Evidence (Vela update-route pilot, 2026-06-15): manifest `route: update`; Vela's
`AGENTS.md` defines the operator words but no `.claude/commands/` directory
exists; `/catchup` returned "Unknown command." Greenfield Step 5 confirmed to
create only the shim.

Options:
- Adopt: frame it as "every route audits and drafts thin harness command
  wrappers when the harness supports command files," not "always create
  `.claude/commands/` on all routes." Each route decides each wrapper's custody
  with an exact-path `git check-ignore` (see the ignored-directory decision
  below). Move the canonical wrapper recipe out of `migration.md` Step 4.2 to a
  route-neutral home both greenfield, migration, and update flows actually reach
  (a short shared section in `bootstrap.md`, or the AGENTS template), and
  reference it from each route. Sub-question: the update route delegates to the
  repo's generated `AGENTS.md` Bootstrap Handoff; a `bootstrap.md` Step 3 hook
  alone suffices for run behavior because every run re-syncs and re-reads
  `bootstrap.md`, but adding a wrapper-audit step to the AGENTS template's
  Bootstrap Handoff would make generated repos self-contained (at the cost of
  more text in every target `AGENTS.md`) - decide whether that defense-in-depth
  is worth it.
- Leave: accept that operator words work as prose behavior even without slash
  commands, and treat wrappers as migration-only.

Recommendation: adopt the route-neutral, harness-conditional, centralized
version; the toolkit's own migration route treats wrappers as a deliverable, and
the inconsistency is a citable broken-promise UX failure. (Refined 2026-06-15
per a GPT 5.5 review: conditional/centralized framing, prose-vs-affordance
clarification, update-route template sub-question.)

### 2026-06-15 - Packet over-claims custody for a directory git collapsed to ignored

Status: Adopted 2026-06-20. `tools/discover.py` `mark_ignored` now renders a
collapsed ignored directory with neutral wording (it describes the current entry,
not a custody verdict for future child paths; run `git check-ignore` on the exact
final path), keeping "gitignored - local-only; cannot be committed as-is" only for
directly-ignored individual files. `tools/manifest-schema.md` gained a matching
one-line reinforcement, and `tests/test_discover.py` now covers both case A (rule
on the directory) and case B (rule on a child, where `git check-ignore <dir>`
exits 1). The finding below is retained for the rationale that led to it.

Finding:
When a directory contains only ignored files and no tracked files, `git status
--ignored --short` collapses it to a single `!! dir/` entry. `tools/discover.py`
records that directory in `ignoredFiles`, and the packet's `mark_ignored`
renders it as "(gitignored - local-only; cannot be committed as-is)". That is a
blanket custody verdict the collapse does not support: the collapsed directory
entry alone does not prove whether a future child path is committable.

Evidence (Vela pilot, 2026-06-15): manifest `ignoredFiles: ['.claude/']` and the
packet said `.claude/` "cannot be committed as-is", yet `.gitignore` has no
`.claude` rule; `.claude/` held only `settings.local.json`, which is ignored by
the machine-global `~/.config/git/ignore` rule `**/.claude/settings.local.json`,
so git collapsed the directory. `git check-ignore .claude/commands/catchup.md`
exits 1 (committable). Note: the Vela report blamed "a false mechanical match,"
but discovery's ignore detection is a real `git status --ignored` query, not a
name-match - the corrected cause is the directory-collapse over-claim.

Important: do not assert that new tracked files can always be added. A directory
git reports as ignored can arise two ways that `git status --ignored` collapses
to the identical `!! dir/`: (A) a rule directly ignores the directory (e.g.
`.claude/` in `.gitignore`), in which case children inherit the ignore and a new
child is NOT committable without narrowing/overriding the rule; (B) the directory
contains only individually-ignored files but no rule matches the directory itself
(Vela's case - `git check-ignore .claude/` exits 1), in which case a
non-matching new child IS committable. The packet must not pick a side.

Options:
- Adopt (lighter, recommended): in `discover.py`, branch `mark_ignored` on
  whether the entry is a directory; for a directory, use neutral wording such as
  "a directory git reports as ignored - this describes the current entry/contents,
  not a custody verdict for every future child path; run `git check-ignore` on
  the exact final path before deciding custody," keeping "gitignored - local-only;
  cannot be committed as-is" only for directly-ignored files. Add reproducing
  tests covering BOTH case A (rule on the directory) and case B (rule on a child,
  via repo `.gitignore` or `.git/info/exclude`) to prove the packet no longer
  over-claims, plus a one-line evidence-rule reinforcement that a parent
  directory shown ignored is not a custody verdict on new child paths. This is a
  packet wording + test fix, not a manifest redesign; the schema already notes
  `ignoredFiles` may list a directory (manifest-schema.md:53).
- Adopt (deeper): change discovery to expand the collapsed directory into
  per-file ignored entries (e.g. `git status --ignored=matching`); rejected as
  primary because it churns the golden manifests for little additional benefit.
- Leave: rely on agents always running `git check-ignore` on the exact final
  path (already required by the custody steps) and treat the packet line as a
  known imprecision.

Recommendation: adopt the lighter fix; this is the third report to trip over
`.claude/` custody and the wording change is low-risk. (Refined 2026-06-15 per a
GPT 5.5 review: corrected the over-strong "new files can still be added" wording
to neutral case-A/case-B wording; test must cover both cases.)

### Adoption order note (updated 2026-06-18)

The command-wrapper fix was adopted 2026-06-18 ahead of the ignored-directory
wording fix. The original sequencing assumed wrapper generation would have to
*decide the custody* of an ignored `.claude/commands/*` and so needed the
custody-wording fix first. The adopted wrapper approach instead *repairs the
gitignore* so `.claude/` command files are committable, which sidesteps the
directory-ignore custody ambiguity rather than depending on it. The
ignored-directory packet-wording fix below remains open and worth doing on its
own merits (the packet can still over-claim custody for other collapsed-ignored
directories), but is no longer a prerequisite for anything.

### 2026-06-15 - Harvest dropbox is read without syncing from its remote

Status: Adopted 2026-06-20. `procedures/harvest.md` Step 1 now requires a
freshness sync of the dropbox from its remote (Step-0 discipline: `git -C
<dropbox>`, `ls-remote` liveness, `--ff-only`) before reading, and proceeds with a
local-only/unverified flag rather than asserting "no unprocessed reports" when the
dropbox is offline, remoteless, or diverged. The sync wording is intentionally
generic (no hardcoded remote): `harvest.config.json` was absent on the
implementing machine, so the dropbox's concrete remote could not be confirmed —
to be verified the next time a dropbox is configured. The template `catchup`
operator was left unchanged because it does not read the dropbox. The finding
below is retained for the rationale that led to it.

Finding:
The harvest consume flow reads the local working copy of the dropbox repo with no
git sync first. `procedures/harvest.md` Step 1 says only "Read new files in the
harvest dropbox repo" - no fetch, `ls-remote`, or `--ff-only` pull. The only
git-sync discipline in the canon ("Cwd-independent Step 0 sync") is scoped to the
bootstrap toolkit's own remotes and says nothing about the dropbox, and the
`catchup` operator definition in `templates/AGENTS.template.md` does not mention
the dropbox at all. Reading a working tree and asserting "no unprocessed reports"
is unsound independent of how many machines exist: the dropbox's canonical
contents are its git history, not one checkout, so a working copy behind its
remote omits reports without any signal. This is the Evidence rule (cite the
query proving a claim is currently active) applied to another repo's state; a
directory listing is not that proof. Reports are delivered by push
(`procedures/migration.md` Step 3), so a working copy missing recently pushed
reports is the expected case, not an edge case.

Evidence (2026-06-15): `procedures/harvest.md` Step 1 contains no sync step. A
catchup reported "no unprocessed harvest reports" from a bare directory listing
of the dropbox (path from `harvest.config.json`) with no fetch or pull. No
existing rule required pulling the dropbox first, so this is a gap, not a rule
violation.

Options:
- Adopt: before reading the dropbox - in `harvest.md` Step 1 and anywhere a
  catchup or status report consumes it - require a freshness sync of the dropbox
  from its remote, mirroring the Step 0 toolkit-sync discipline (`git -C
  <dropbox>`, `ls-remote --exit-code` liveness, `--ff-only`); if the dropbox is
  offline, has no remote, or has diverged, proceed but state plainly that the
  harvest view is local-only and unverified rather than asserting completeness.
  Keep all dropbox writes (the move-to-`processed/` step) on the post-sync tree.
- Leave: accept that harvest state reported without a sync is local-only and rely
  on the owner remembering to pull before a sweep.

Recommendation: adopt; this is a correctness/evidence gap, not a convenience
sync. Fix scope is the product (`procedures/harvest.md`, plus the `catchup`
operator behavior and/or Evidence rule wording in
`templates/AGENTS.template.md`), not this repo's own local governance. Confirm
the dropbox's remote configuration when the fix is implemented.

### 2026-06-15 - Git Safety is silent on history rewrite and commit-structure choice

Status: Adopted 2026-06-20. The invariant now lives in the `templates/AGENTS.template.md`
"Git Safety" section, with aligning clauses in `procedures/bootstrap.md` (Step 10),
`procedures/migration.md` (Step 5), and this repo's own `AGENTS.md` Working Rules.
The finding below is retained for the rationale that led to it.

Finding:
The shipped `templates/AGENTS.template.md` "Git Safety" section says nothing about
amend, rebase, squash, or rewriting history, and nothing about who decides commit
structure. Its only commit-shaping rule is "address exactly one item per commit
and commit each before starting the next." Under that, an agent can rewrite an
existing commit or fold two items into one by amending without violating any rule.
Choosing to amend or restructure a commit is an owner-level process decision - the
same class as the artifact-is-evidence-not-decision and answer-with-words rules -
and history rewrite is hard to reverse once pushed, but the git invariants name no
such limit.

Evidence (2026-06-15): `templates/AGENTS.template.md` Git Safety (lines ~137-150)
contains only the ancestry-vs-content rule and the one-item-per-commit rule, with
no mention of amend/rebase/squash or commit-structure authority. An agent
instructed to remove a file amended an existing commit instead of adding a new
one, rewriting history without being asked - the act-without-asking pattern the
words-first rule targets, which the git section did not cover.

Options:
- Adopt: add a Git Safety invariant to the AGENTS template such as "Do not rewrite
  history (amend, rebase, squash, force-push) or decide commit structure without
  explicit owner approval; default to a new commit per fix," and align the
  bootstrap/migration commit contract so the owner's approval authorizes the
  scoped commit, not a later rewrite of it. Mirror the same line into this repo's
  own root `AGENTS.md` for consistency.
- Leave: rely on the words-first / artifact-is-evidence rules to cover commit
  rewriting implicitly, accepting that the git section names no such limit.

Recommendation: adopt; history rewrite is exactly the kind of hard-to-reverse,
owner-only process choice the rest of the canon is explicit about. Fix scope is
the product (`templates/AGENTS.template.md` Git Safety, plus the commit contract
in `procedures/bootstrap.md` / `procedures/migration.md`), with an optional
matching line in this repo's own `AGENTS.md`.

### 2026-06-15 - Summaries restate authoritative counts and enumerations

Status: Adopted 2026-06-20 (product only). `templates/AGENTS.template.md` gained a
Universal Invariant: a summary/pointer names where a fact lives and does not keep a
second copy of a count or enumeration another doc owns, pointing to the source
instead. The `state.md` "Next" instance the finding cited is already resolved -
this repo's `.agents/state.md` already points to the decisions doc without
restating a number or per-item list - so no self-application change was needed. The
finding below is retained for the rationale that led to it.

Finding:
A summary or pointer doc that restates a fact another doc owns - a count, or an
enumeration of items maintained elsewhere - is a drift generator. The copy and
the source diverge whenever the source changes without a lockstep edit to the
summary, and the result is a conflict a reader cannot resolve from the docs
alone (the count says one thing, the authoritative list says another, and no rule
declares which wins). Current instance: `.agents/state.md` "Next" restates both
the number and the list of open decisions, which `.agents/decisions.md` "Open
Decisions" owns.

Fix:
A summary/pointer names where a fact lives and does not duplicate counts or
enumerations of facts another doc owns. Concretely, `.agents/state.md` "Next"
references the `.agents/decisions.md` "Open Decisions" section with no number and
no per-item list. Generalize the rule into the canon so every bootstrapped repo
inherits it: a pointer doc points; it does not maintain a second copy of an
authoritative count or list. This is the same drift class as the `drift`
operator's "fix the lower-authority source" - state.md is the lower-authority
pointer, decisions.md is the source.

Scope:
This repo's local governance (`.agents/state.md` wording), plus a canon change to
encode the principle (`templates/AGENTS.template.md`, near the Operator Requests
or state-doc guidance). No change made now.

### 2026-06-15 - Do not circumvent roadblocks without established provenance

Status: Adopted 2026-06-20. The invariant now lives in the `templates/AGENTS.template.md`
"Universal Invariants" section, with a matching bullet in this repo's own `AGENTS.md`
Working Rules. The finding below is retained for the rationale that led to it.

Finding:
A roadblock - a failing test, an assertion or guard, a lint or type error, a
`.gitignore` rule or one of its exceptions, a refusal or permission denial, a
config that forbids an action, a thrown exception, a CI gate - exists until
proven otherwise for a reason that may not be visible at the point it is hit. The
canon forbids specific instances of routing around one (the revert-the-fix /
vacuous-test rule in the Verification section; the ban on silent `git add -f` in
the gitignore commit contract) but states no general principle, so an agent that
cannot see why a roadblock exists can remove, disable, override, or bypass it to
make the obstruction go away without first establishing whether it is
load-bearing.

Fix:
Add an invariant: do not circumvent a roadblock whose provenance is not
established. Before removing, disabling, overriding, or bypassing one, inspect the
code and docs - history, comments, related decisions, the rule's origin -
thoroughly enough to validate that it is not load-bearing and that circumventing
it is appropriate. If that validation cannot be reached, treat the roadblock as
legitimate and stop or ask rather than routing around it. The default is that the
roadblock is correct until proven otherwise; "make the error go away" is not a
basis for removing it.

Scope:
The product (`templates/AGENTS.template.md` invariants, generalizing the existing
point-rules), with an optional matching line in this repo's own `AGENTS.md`. No
change made now.

### 2026-06-15 - Project-specific memory must live in the repo, not in any agent-local store

Status: Adopted 2026-06-20 (product only). `templates/AGENTS.template.md` gained a
harness-agnostic Universal Invariant: agent-local/harness-local memory stores are
not durable memory; project-specific durable knowledge is persisted into the
repo's governance, and any out-of-repo store is reserved for cross-project facts.
No procedure pointed agents at an agent-local store, so none needed correction.
The optional matching line in this repo's own `AGENTS.md` is left to the bootstrap
re-run, per the owner (2026-06-20). The finding below is retained for the
rationale that led to it.

Finding:
Many agent harnesses provide a machine-local, per-project memory store outside the
repo - for example Claude Code's `~/.claude/projects/<project>/memory/`, and the
equivalent local memory or state stores in other coding agents such as Codex or
Gemini. Project-specific durable knowledge written to any such store does not live
in the repo: it is not versioned with the code, does not travel across machines,
and is invisible to other agents, other tools, and the governance process that
reads `AGENTS.md`, `.agents/state.md`, and `.agents/decisions.md`. The canon does
not direct agents where project memory belongs, so an agent following its
harness's default memory mechanism - whichever harness it is - parks
project-specific facts in a location the process cannot use.

Fix:
Add a harness-agnostic invariant: project-specific durable knowledge is persisted
into the repo's governance (`.agents/state.md`, `.agents/decisions.md`,
`AGENTS.md`, or a dedicated repo memory doc), where it is versioned and
discoverable by every session, agent, and machine. Any agent-local or
harness-local memory store, regardless of which model or CLI provides it, is
reserved for genuinely cross-project facts (owner identity, preferences) and is
not the home for project-specific memory. Phrase the rule by behavior, not by one
vendor's path, and encode it in the canon so every bootstrapped repo directs
agents of any harness accordingly.

Scope:
The product (`templates/AGENTS.template.md`, and any procedure that tells agents
where to record durable knowledge), with an optional matching line in this repo's
own `AGENTS.md`. No change made now.

### 2026-06-15 - Toolkit remote topology: GitHub is canonical, gitea is a mirror

Status: Adopted 2026-06-20. Canon now models GitHub as the canonical remote and
the LAN gitea remote as a mirror of it — reframed in `procedures/bootstrap.md`
Step 0, the "Single-session kickoff" and "Cwd-independent Step 0 sync" decisions
above, and this repo's own `AGENTS.md`. The repo's own remotes were re-pointed the
same day (origin → GitHub, gitea → secondary mirror). The finding below is
retained for the rationale that led to it.

Finding:
The canon models the toolkit's two remotes as co-equal canonical sources with the
gitea LAN remote as "primary": `procedures/bootstrap.md` Step 0 lists both URLs as
"the canonical copies" and flags divergence when "the two remotes disagree with
each other"; the "Single-session kickoff" decision says "two canonical remotes
(gitea LAN primary + GitHub)"; the "Cwd-independent Step 0 sync" decision flags
when "the two canonical remotes disagree"; and `AGENTS.md` names gitea
`http://q:3000/michael/AgentGovernanceBootstrap.git` as "(primary)" and tells
agents to "offer once to push, naming both." In fact GitHub
(`https://github.com/roethlar/AgentGovernanceBootstrap.git`) is the single source
of truth and the gitea LAN remote is a mirror of GitHub. The co-equal model is
wrong in four ways: (a) "primary = gitea" inverts authority; (b) "two remotes
disagree -> flag" treats an expected stale mirror as a genuine conflict; (c)
fast-forwarding to the newest fetched head can advance to a stale gitea head when
the mirror lags; (d) "push to both" is wrong for a mirror - the push target is the
source (GitHub) and the mirror updates downstream.

Fix:
Reframe the topology in the canon: GitHub is canonical; the gitea LAN remote is a
mirror used only as a fast fetch source when reachable. Authority resolves to
GitHub on any divergence (a lagging mirror is expected, not a flag-worthy
disagreement), freshness is judged against GitHub, and push offers target GitHub
only. Keep gitea as an optional labeled mirror for fetch speed.

Scope:
The product (`procedures/bootstrap.md` Step 0, the "Single-session kickoff" and
"Cwd-independent Step 0 sync" decisions, and this repo's own `AGENTS.md`
canon-propagation note). No change made now.

### 2026-06-20 - Wrapper generation is gated on the bootstrapping harness, not committed on every route

Status: Adopted 2026-06-20 (product only). Wrapper drafting is decoupled from the
bootstrapping harness: a new `templates/commands/claude/` set holds the five
pointer wrappers, `procedures/bootstrap.md`'s "Operator command wrappers" section
now drafts them from that template set for every shipped harness regardless of
which harness runs the bootstrap (skipping only if no template exists for any
harness), and `templates/AGENTS.template.md` step 10 reframes the wrappers as
committed repo artifacts. This repo's own wrappers and an Operator Requests
section in its `AGENTS.md` are intentionally NOT added here - this repo carries a
stale older bootstrap application, to be brought current by re-running the
bootstrap, per the owner (2026-06-20). The finding below is retained for the
rationale that led to it.

Finding:
The "Operator command wrappers (all routes)" guarantee gates whether the
portable command wrappers get drafted at all on whether the harness *running the
bootstrap right now* supports command files. A harness with no command-file
mechanism skips the section entirely. But the wrappers
(`.claude/commands/{catchup,handoff,drift,decision,plan}.md`) are one-paragraph
pointers into the committed `AGENTS.md` — repo-portable artifacts, not
harness-local state, in the same class as `AGENTS.md` itself, which is committed
regardless of which harness wrote it. So an agent bootstrapping under a
native-`AGENTS.md`-reader harness (Codex-family and newer tools, which are
exactly the ones likely to have no command-file mechanism) produces no wrappers,
and a later session under Claude Code finds no slash commands — the same
broken-promise UX the 2026-06-18 standing-guarantee decision set out to close,
re-triggered by which harness ran the bootstrap rather than by route.

Note on the trigger: the literal skip condition in the canon is "the harness you
are running in has no command-file mechanism," not the phrase "reads `AGENTS.md`
natively." That phrase belongs to the *shim* steps (a separate artifact). In
practice the two coincide — native-reader harnesses are the ones without command
files — so the gap lands where the finding says, but the proving text is the
command-file gate, not the shim's native-reader clause.

Evidence (2026-06-20, current canon):
- `procedures/bootstrap.md:124-127` (wrapper section, step 1): "if yours has no
  command-file mechanism, skip this section and rely on the words working as
  plain-language requests."
- `procedures/bootstrap.md:184-191` (greenfield step 5): drafts the shim only for
  non-native harnesses, then runs the wrapper section — so under a native-reader
  harness with no command files, neither is produced.
- `procedures/migration.md:92-101` (Step 4): same structure — shim is
  native-conditional, wrapper section runs after.
- `templates/AGENTS.template.md:69-77` (Bootstrap Handoff step 10): drafts
  wrappers only "on a harness that supports command files."
- `templates/shims/` ships `CLAUDE.template.md` and `GEMINI.template.md` shims but
  NO command-wrapper templates; wrappers are drafted "from self-knowledge," which
  only happens when a command-file harness runs the bootstrap.
- This repo has no `.claude/` directory: even the canonical toolkit carries the
  operator words in prose with no committed wrappers.

Mitigation that already exists (relevant to the Leave option): the guarantee is
standing and runs on the update route too, so the first time a command-file
harness (Claude Code) runs any route on the repo it will draft the missing
wrappers. The gap is therefore transient — it closes on the first
Claude-Code-run — but the harm window (a Claude Code user hitting "Unknown
command" before that run) is exactly the Vela-pilot failure mode, and it is
avoidable because the Claude Code wrapper format is known and fixed, so the
toolkit can author the files blind without running in that harness.

Options:
- Adopt (recommended): decouple wrapper drafting from the bootstrapping harness.
  Commit the wrappers for every harness the toolkit ships a wrapper template for,
  on every route, the same way `AGENTS.md` is committed regardless of authoring
  harness. Concretely: add committed wrapper templates (e.g. under
  `templates/commands/`) and draft them unconditionally; narrow the step-1 skip to
  "skip only if the toolkit ships no wrapper template for any harness," keeping
  the genuinely harness-local pieces (the shim, `settings.local.json`)
  conditional.
- Leave: accept that wrappers are created only when a command-file harness runs a
  route, and rely on the standing update-route audit to backfill them on the
  first Claude-Code-run, accepting the broken-promise window until then.

Recommendation: adopt. Wrappers are portable repo artifacts; gating their
existence on the bootstrapping harness reproduces the broken-promise UX the
2026-06-18 decision was meant to eliminate, and the fix is cheap because the
wrapper format is a known shipped template. Scope is the product
(`procedures/bootstrap.md` wrapper section + greenfield step 5,
`procedures/migration.md` Step 4, `templates/AGENTS.template.md` step 10, and a
new `templates/commands/` wrapper-template set), plus committing this repo's own
wrappers so the canonical toolkit stops modeling the gap.

### 2026-06-20 - Governance payload token cost grows unboundedly; compact decisions.md structurally

Status: Adopted 2026-06-20 (product only). `templates/decisions.template.md` now
directs the decisions doc to keep only what is in force or still open and to move
closed entries (superseded, or settled-and-kept-only-for-rationale) verbatim into a
`docs/history/` archive in the same change, with one pointer at the top - no
per-entry stubs. The trigger is status-based (a decision settling), replacing the
vague size-threshold idea. This repo's own `decisions.md` archiving (this session's
Adopted entries) happens when the bootstrap is re-run under the new rule, per the
owner (2026-06-20). The finding below is retained for the rationale that led to it.

Finding:
The governance docs the process loads — `AGENTS.md`, `.agents/state.md`,
`.agents/decisions.md`, `.agents/repo-map.json`, `.agents/artifact-manifest.json`
— total ~54 KB ≈ ~10-13.5k tokens as of 2026-06-20. `decisions.md` alone is
~39 KB ≈ ~9-10k tokens (73% of the payload) and grows monotonically: every
deferred finding and every adopted decision appends to it and nothing prunes or
archives. The per-turn cost depends on the harness (one that auto-injects
`AGENTS.md`/`CLAUDE.md` pays ~1.5k tokens/turn for `AGENTS.md` only), but the
full set is paid at every kickoff and every `catchup`/`handoff` that reads the
whole decisions file — a cost that rises with each entry. This finding is itself
an instance of the cost it describes.

Evidence (2026-06-20, `wc -c`): `decisions.md` 39,486 B, `AGENTS.md` 6,802 B,
`state.md` 3,877 B, `repo-map.json` 2,943 B, `artifact-manifest.json` 1,165 B;
total 54,273 B. Token estimate ≈ bytes/4 ≈ 13.5k, or words×1.3 ≈ 10k. No root
`CLAUDE.md` exists; `.agents/` files are read on demand in at least the Claude
Code harness.

Options:
- Adopt (structural archiving, recommended): rotate adopted/superseded decisions
  out of the hot `decisions.md` into `docs/history/` (e.g. a dated
  `decisions-archive.md`), leaving the hot file as Active + Open Decisions only,
  with a one-line pointer to the archive. Preserves exact wording (no lossy
  summarization), bounds the hot-file size, and matches the repo's existing "bank
  predecessor material in `docs/history/`" pattern. Generalize into canon so every
  bootstrapped repo's `decisions.md` self-rotates past a size threshold.
- Adopt (lighter): document the budget and steer `catchup`/`handoff` to read
  `state.md` plus only the Open Decisions section, not the full adopted history,
  unless asked.
- Leave: accept unbounded growth; owner prunes manually.
- Reject (lossy compaction — rtk `read`/`summary`, LLM summarization): strips the
  exact wording the Evidence rule and one-canonical-location principle depend on;
  not appropriate for authoritative canon. See the rtk-wrapping item below for the
  same lossy-filtering caution applied to command output.

Recommendation: adopt structural archiving — the only compaction that respects
"exact wording is the product." Scope: this repo's own `decisions.md` plus a canon
rule in `templates/AGENTS.template.md` (decisions-doc guidance).

### 2026-06-20 - Recommend (not require) wrapping shell commands in a token-filtering proxy when available

Status: Adopted 2026-06-20. `templates/AGENTS.template.md` Universal Invariants
gained a soft, Evidence-rule-subordinate recommendation: prefer a token-filtering
command proxy (e.g. `rtk`) for routine, high-volume, low-stakes output, but run
unfiltered whenever the filtered form might drop context that matters or that will
be cited as evidence; if unsure, do not filter. Named by capability, not brand. The
finding below is retained for the rationale that led to it.

Finding:
A token-filtering command proxy (e.g. `rtk`) compacts `ls`/`tree`/`git`/`grep`/
test/log output before it reaches the model, which can materially cut tokens spent
on tool output. But routing every command through it risks stripping context the
model actually needs — a condensed diff that drops the one line that mattered,
masked env values, summarized test output hiding a stack trace. Canon currently
says nothing about token-economical tool use.

Evidence (2026-06-20): `rtk` 0.42.4 present at `/usr/bin/rtk`; subcommands include
`ls`/`tree`/`read`/`git`/`grep`/`diff`/`test`/`log`/`json` with
"token-optimized"/"ultra-condensed" filtering. Its own description: "filter and
summarize system outputs before they reach your LLM context" — lossy by design.

Options:
- Adopt (recommend, conditional, recommended): add an optional efficiency line to
  `templates/AGENTS.template.md` — when a token-filtering command proxy is
  available, prefer it for routine, high-volume, low-stakes output (directory
  listings, build/test runs, log tails); it is a recommendation, never a
  requirement; and when the filtered form might drop context that matters —
  verifying exact output, reading authoritative content, anything feeding a durable
  claim under the Evidence rule — run the command unfiltered. Default to caution:
  if unsure whether filtering is lossy for this use, don't filter. Name the
  capability, not the brand (rtk as the example), per the harness-agnostic style.
- Leave: say nothing; let each agent/harness decide.

Recommendation: adopt as a soft recommendation with the err-on-caution carve-out,
explicitly subordinate to the Evidence rule (never filter the output you will cite
as proof). Scope: product (`templates/AGENTS.template.md`), harness-agnostic
wording.

### 2026-06-20 - Resolve git presence as the earliest bootstrap step, before discovery

Status: Adopted 2026-06-20. `procedures/bootstrap.md` Step 1 now confirms `.git/`
presence before running discovery: a missing repo is resolved via the owner-gated
`git init` question up front (approve -> `git init` then discover; decline ->
proceed under the no-version-control path), instead of surfacing "not a git
repository" only at the approval stage. The "If the target is not a git
repository" section is reframed as early-detection with discovery as the backstop.
`migration.md` needs no change (it is entered only after discovery routes an
already-governed, hence git, repo, and the Step 1 check precedes the route split so
it covers all routes); the template needs none (this is a bootstrap-process
concern, not generated-repo guidance). The finding below is retained for the
rationale that led to it.

Finding:
git is a hard requirement for the toolkit — custody probes, the commit contract,
and the whole governance flow assume a repo. Today a non-git target is detected
late: `discover.py` runs to completion on the non-git tree, lists every file as
untracked, and the owner first sees "Not a git repository" plus the owner-gated
`git init` question only at the approval stage. The agent goes through discovery
and drafting before the missing-git fact surfaces — wasted motion for a hard
prerequisite, and the failure mode that prompted this item ("go through the
motions, then mention it wasn't a git repo at the end").

Evidence (2026-06-20):
- `procedures/bootstrap.md:228-238` — the "If the target is not a git repository"
  handling is a standalone section near the end of the file, carrying the
  owner-gate (line 235: "Never run `git init` unprompted. Ask the owner"; line
  238: init only on approval). It is not positioned as an early step in the
  kickoff flow.
- `tools/discover.py:395-398` — on a non-git target the script runs anyway, lists
  everything as untracked, and the packet notes `git init` "is the owner's
  decision."

Chosen approach (owner, 2026-06-20): keep the existing owner-gate — do NOT
auto-init (the gate guards against the tool being pointed at the wrong directory
or a subfolder inside an existing repo) — but move the check to the earliest point
in the bootstrap, before `discover.py` runs. As soon as the agent observes no
`.git/` in the target, it asks the owner-gated init question there; on approval it
runs `git init` and proceeds to discovery; on refusal it stops rather than running
discovery on a non-git tree. This preserves the wrong-directory safety the gate
provides while removing the run-discovery-then-surface-it-late waste.

Options:
- Adopt (recommended, ask-early): add an early git-presence step to the bootstrap
  flow (before discovery) that detects a missing `.git/`, asks the owner-gated
  init question at that point, and only runs `discover.py` once git presence is
  resolved. Reposition the existing "If the target is not a git repository"
  content as that early gate. Mirror into `migration.md` if its flow has the same
  ordering. Keep `discover.py`'s non-git packet text as a safety net for the rare
  case discovery is run anyway.
- Rejected (auto-init): create `.git` without asking — reverses the owner-gate;
  declined by the owner on 2026-06-20 because the wrong-directory / nested-repo
  risk outweighs the convenience.
- Leave: accept that non-git is surfaced only at the approval stage.

Recommendation: adopt the ask-early option (owner-chosen). Scope: product
(`procedures/bootstrap.md` step ordering plus its existing non-git section,
`procedures/migration.md` if its ordering matches, and the
`templates/AGENTS.template.md` Session Startup / Bootstrap Handoff if agents should
be told to confirm git presence first). This is a procedure/ordering change;
`discover.py`'s non-git fallback stays as-is.

### 2026-06-20 - Decisions template under-models the Open-queue / Adopted pattern

Status: Adopted 2026-06-20. `templates/decisions.template.md` now teaches the full
lifecycle: a `## Decision lifecycle` section defining Open -> Active / Adopted ->
Superseded -> archived, an `Adopted YYYY-MM-DD` status listed alongside `Active |
Superseded` in the entry-format comment, and an `## Open Decisions (deferred - not
yet adopted)` section with its own Finding/Evidence/Options/Recommendation comment
modeled on this repo's own usage. The finding below is retained for the rationale
that led to it.

Finding:
`templates/decisions.template.md` models a decisions doc with only `Status: Active
| Superseded` and a single `## Decisions` section. But this repo's own
`.agents/decisions.md` - the canonical example - evolved a richer structure the
template never teaches: an `## Open Decisions` queue for assessed-but-deferred
findings, and an `Adopted` status for queue items whose rule has moved into the
canon. A repo bootstrapped from the current template gets no guidance on the
queue/Adopted lifecycle, so the toolkit's most-used decision workflow is
undocumented in the product. This also leaves the just-added archiving rule
referencing closed/settled states the template does not define.

Evidence (2026-06-20):
- `templates/decisions.template.md` - the entry-format comment lists only
  `Status: Active | Superseded`; no Open queue, no `Adopted` status.
- `.agents/decisions.md` - uses an `## Open Decisions` (deferred) section and
  `Status: Adopted YYYY-MM-DD` entries throughout (this whole session's work).

Options:
- Adopt: extend the decisions template to model the queue and the `Adopted` status
  - add an open/deferred section, document the lifecycle (Open -> Adopted, rule
  moves to its canonical home, entry archived per the archiving rule), and list
  `Adopted` alongside `Active | Superseded`.
- Leave: keep the template minimal and treat the queue/Adopted pattern as a local
  elaboration this repo happens to use.

Recommendation: adopt - the queue/Adopted lifecycle is load-bearing in practice and
pairs directly with the archiving rule. Scope: product
(`templates/decisions.template.md`), harness-agnostic. Surfaced 2026-06-20 while
adopting the token-cost archiving rule.

### 2026-06-20 - Revise the two-agent review-loop doc into a governance-compatible playbook (reviewloop.md)

Status: Adopted 2026-06-20. The owner's external two-agent review-loop runbook is now
shipped as `templates/playbooks/reviewloop.md` (a reusable playbook template; the new
`templates/playbooks/` directory is established here and copied into target repos by
`tools/discover.py`'s existing `templates/` copytree). The four conflicts were
reconciled: (1) the autonomous main-branch merge is now owner-gated by default (accept
is a verdict, not merge authority; hand off a `merge-<id>` branch or leave the branch
for an owner-approved merge; auto-merge is an opt-in knob requiring standing owner
authorization); (2) the parallel root `REVIEW.md` / `.review/` canon is replaced by
`.agents/review/` nested under the governance root, with the status index at
`.agents/review/index.md` that `.agents/state.md` points to rather than duplicating;
(3) the hardcoded cargo/npm suite is replaced by deferral to the repo's observed
verification command, suites as illustrative examples; (4) named subagents and the
specific Monitor tool are reframed as capabilities with no-special-capability
fallbacks. The aligned parts (one-branch-per-finding, `Fix <id>` per-item commits,
atomic unit, no broad sweeps, sentinel audit trail) are kept, and repo-specific
examples are genericized to placeholders. `procedures/bootstrap.md` greenfield step 4
points at the shipped playbook set. The finding below is retained for the rationale
that led to it.

Finding:
An external doc (the owner's `/tmp/SETUP.md`, a ~390-line portable two-agent
coder/reviewer review-loop runbook) predates this repo and conflicts with current
governance in several places. It fits the playbook concept the canon already
defines (`.agents/playbooks/*`), but cannot be filed as-is: it must be revised to
reconcile the conflicts and genericized, then placed per the playbook convention
and renamed `reviewloop.md` ("two-agent-review" is too verbose).

Conflicts to reconcile (evidence, against current canon):
- Autonomous merge to master. The doc has the reviewer fast-forward-merge accepted
  branches into master (lines ~132, ~365: "Auto-merge ... reviewer can
  fast-forward merge on accept"). Conflicts with the one-scoped-commit /
  push-offer-once / owner-gated discipline and the Git Safety invariant - an agent
  should not merge to master without owner approval. Revise to owner-gated merge
  (or a handed-off `merge-<id>` branch) as the default.
- Parallel status canon. The doc adds a root `REVIEW.md` status index and a
  `.review/` channel, overlapping `.agents/state.md` as the single discoverable
  current-state entry point and the "no parallel canon" rule (decisions.md
  2026-06-09). Revise so the loop's status nests under or references the
  `.agents/` layout instead of competing with it.
- Hardcoded verification. The doc prescribes fixed validation suites (cargo/npm,
  lines ~89-95); canon says run the repo's observed automated verification. Revise
  to defer to the verification rule, suites as examples only.
- Harness-specific assumptions. Named subagents (security-engineer, etc.) and a
  specific Monitor tool (lines ~261-264, Step 5). Revise to harness-agnostic,
  name-by-capability wording with best-effort fallbacks.
- Aligned, keep: one-branch-per-finding plus `Fix <id>` commits already match the
  one-item-per-commit discipline; worktree use is fine.

Options:
- Adopt: revise the doc to reconcile the conflicts, genericize repo-specific bits
  to placeholders, rename to `reviewloop.md`, and place it per the playbook
  convention (`.agents/playbooks/reviewloop.md`; or `templates/playbooks/` if the
  toolkit ships it as a reusable playbook - see the playbook-mechanism items).
  Source is the owner's `/tmp/SETUP.md`.
- Leave: keep the doc external and out of the repo.

Recommendation: adopt the revision. Scope: a new playbook doc plus the conflict
reconciliations; the playbook home is already defined in the Source of Truth
(`.agents/playbooks/*`), and it pairs with the playbook-invocation operator if that
is adopted. Surfaced 2026-06-20.

### 2026-06-20 - Add a playbook invocation operator (and optionally ship reusable playbook templates)

Status: Adopted 2026-06-20. A `playbook <name>` operator now lives in
`templates/AGENTS.template.md` Operator Requests ("read `.agents/playbooks/<name>.md`
and follow it"), with a `templates/commands/claude/playbook.md` pointer wrapper reusing
the harness-independent wrapper machinery. The operator word is wired into every
wrapper-audit enumeration so the wrapper is drafted on all routes:
`templates/AGENTS.template.md` Bootstrap Handoff step 10, `procedures/bootstrap.md`
"Operator command wrappers", `procedures/migration.md` Step 4, and the trigger
vocabulary in `docs/design.md`. The optional shipping of reusable playbook templates
under `templates/playbooks/` is handled with the review-loop playbook (its own queue
entry), which establishes that directory. The finding below is retained for the
rationale that led to it.

Finding:
Playbooks are a first-class concept in the canon - the Source of Truth lists
`.agents/playbooks/*` as approved durable guidance, and `docs/design.md` names
"area-specific playbooks, or review workflow files" as the use case - but there is
no invocation mechanism. Nothing tells an agent to load and follow a named
playbook: the operator vocabulary (`catchup`, `handoff`, `drift`, `decision`,
`plan`) has no `playbook` member, so a repo can carry playbooks with no standard
way to trigger them. Playbooks have a home but no door.

Evidence (2026-06-20):
- `templates/AGENTS.template.md` - Source of Truth lists `.agents/playbooks/*` as
  approved guidance; Operator Requests defines the five operator words but no
  playbook trigger.
- `docs/design.md:175` - names "area-specific playbooks, or review workflow files"
  as a canonical playbook use.
- No `.agents/playbooks/` invocation convention exists anywhere in the canon.

Options:
- Adopt: add a `playbook` operator to Operator Requests - "`playbook <name>`: read
  `.agents/playbooks/<name>.md` and follow it" - plus a
  `templates/commands/claude/playbook.md` wrapper, reusing the harness-independent
  wrapper machinery adopted 2026-06-20. Optionally extend to shipping reusable
  playbook templates under `templates/playbooks/` so the toolkit can offer canned
  playbooks (the reviewloop doc would be the first), instead of every repo drafting
  playbooks from scratch.
- Leave: keep playbooks as passively-listed guidance with no standard trigger.

Recommendation: adopt the operator - the home already exists; only the trigger is
missing, and it is the same shape as the existing operator words. The
`templates/playbooks/` shipping is a smaller optional extension that pairs with the
reviewloop-revision item. Scope: product (`templates/AGENTS.template.md` Operator
Requests + Source of Truth note, `templates/commands/claude/playbook.md`, and
optionally a `templates/playbooks/` set).

### 2026-06-20 - Load-bearing invariants need forceful enforcement, not just statement

Status: Adopted 2026-06-21. The mechanism chosen is the one the 2026-06-20
"prime invariants" and "harness hook" options pointed at, designed and shipped on
2026-06-21: a lean `## Prime Invariants` block (`prime:begin`/`prime:end`) at the
top of `templates/AGENTS.template.md` holding the 3-4 hardest-to-reverse rules so
they survive compaction, plus per-harness re-grounding hook configs under
`templates/hooks/<harness>/` that fire on context compaction and prompt a re-read
of AGENTS.md, installed on every route and surfaced (never auto-granted) for
trust. `procedures/bootstrap.md` and `templates/AGENTS.template.md` Bootstrap
Handoff gained the hook-install/trust steps; `tests/` guard the hook config and
the canonical trigger; the design is recorded in
`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`. The
earlier behavioral "question vs directive" gate was rejected as infeasible. The
finding below is retained for the rationale that led to it.

Finding:
The canon's most load-bearing invariants - answer-with-words, words-first, and the
owner-gate on commits/pushes/merges/history-rewrite - are stated once, in prose, in
a long `AGENTS.md`/template, and rely entirely on the agent holding them in working
memory. That memory degrades as a session runs long and context compacts, so the
invariants fail precisely when the session is most complex - when they matter most.
There is no enforcement surface: nothing re-asserts the critical rules and nothing
gates the actions they govern. The canon leans entirely on "the agent will
remember," with no repetition and no structural gate. A rule that can be silently
skipped under load is a governance weakness, not only an agent error.

Evidence (2026-06-20): in this long, context-heavy session the agent skipped the
answer-with-words invariant twice - responding to owner questions with file edits,
commits, and pushes instead of words. The rule was present and binding the whole
time; it was dropped under context pressure, not unknown.

Options (specifics to be decided later):
- A tiny "prime invariants" subset: extract the 3-5 hardest-to-reverse rules
  (answer questions with words; no file change / commit / push / merge /
  history-rewrite without an explicit go) into a short, separable block kept brief
  enough to survive compaction, and re-asserted at checkpoints - after a context
  compaction, at each operator invocation, and immediately before any commit.
  Brevity plus repetition is what makes a rule stick when a long doc does not.
- A behavioral pre-action gate: before editing in response to a message, classify
  it - a question or anything ambiguous means answer in words first; only an
  explicit change-instruction authorizes acting - run as a checklist, not a buried
  sentence.
- Harness-level enforcement where available: a hook on Edit/Write/commit that warns
  or blocks when the triggering turn was a question. Strongest, but harness-specific,
  so the harness-agnostic canon would phrase it as a "where supported" recommendation.
- Some combination of the above.

Related: keeping the hot governance lean (the status-based decisions-archiving rule
adopted 2026-06-20) reduces the context pressure that drops invariants - a
complementary mitigation, not a substitute.

Recommendation: adopt some forceful-enforcement mechanism; the specific design is
deferred to a later decision. Scope: product (`templates/AGENTS.template.md`
invariants structure, plus optionally a harness-hook recommendation and/or
operator-checkpoint behavior). Surfaced 2026-06-20 by an in-session failure of the
answer-with-words rule.

### Open: reassess the general push-needs-explicit-go rule (local-only commits are a staleness trap)

Status: Adopted 2026-06-27 (see "push policy delegated to `.agents/push-policy.md`;
four standardized options; default: ask" in `.agents/decisions.md` Decisions). The
finding below is retained verbatim as the rationale that led to it; it was rotated
out of the live Open Decisions queue on 2026-06-27 once adopted.

Surfaced 2026-06-26 by the owner. The Prime Invariant "Push... need an explicit
go — pushing publishes" treats every push as an outward-facing action requiring a
per-instance go. That rule optimizes for one real risk (a push to a *public*
canonical remote is exposure that is hard to retract) but imposes a cost that has
bitten the owner repeatedly: commits that live only locally leave the canonical
remote silently behind, and a later session (or the owner) assumes a repo is
up to date when it is not. That directly undercuts the governance goal the repo
otherwise enforces — durable truth lives on the canonical remote, not in a local
commit. The `handoff` operator is the sharpest case: a handoff records resumable
state for the next session, yet under the current rule its commit can sit unpushed,
so the "resume point" is invisible to a fresh clone or another machine.

Tension to resolve (this is why it is a decision, not a silent fix): the two pulls
are genuine and both are in the governance. (1) "Pushing publishes" — a real
caution for a public remote and for irreversible/outward actions. (2) "Repo is
memory; durable truth on the remote" — local-only commits are a silent-staleness
trap. The current blanket rule serves (1) at the cost of (2).

Evidence: the Prime Invariants block in `AGENTS.md` and
`templates/AGENTS.template.md` (the push-go clause); the Git Safety section; the
repeated handoff loose-end this session where each handoff commit needed a
separate explicit push. Owner reports out-of-sync repos assumed current as the
recurring real-world cost.

Options: (a) **tier by blast radius** — push-by-default for low-risk
governance/docs/state commits (handoff, decision, drift, state updates, docs),
retain explicit-go for code, history-rewrite, force-push, and other
destructive/outward actions; (b) **handoff-only carve-out** — `handoff` pushes its
own commit automatically (running handoff is the go), everything else unchanged
(narrow, but leaves the general staleness cost for non-handoff governance commits);
(c) **make push a named final step of handoff** that always offers (keeps
per-instance go, just stops it being an afterthought); (d) leave the blanket rule
as-is and accept the staleness cost. This is a **Prime-Invariant-level** change for
(a)/(b), so adoption must edit `templates/AGENTS.template.md` (and bump
`templateVersion`), with this repo's frozen `AGENTS.md` updated only by a
self-application run.

Recommendation: (a). It resolves the tension at the right seam — the push-go rule's
real value is on irreversible/outward/destructive actions, which is where it should
stay; governance/docs/state commits are low-blast-radius and are exactly the
durable truth that most needs to be on the remote. (b)/(c) only patch the handoff
symptom and leave the general cost. Open sub-question for the plan: define the
"low-risk" tier precisely (by path? by operator? by commit-type?) so the rule is
mechanically clear, not a judgment call each time.

### Open: `run_git` fails open — git errors are indistinguishable from empty results

Status: Adopted 2026-06-23. Option (a) landed in `tools/discover.py`: a new
`_git_exec()` returns `(executed, returncode, lines, stderr)`; `run_git()` keeps
its lines-or-`[]` contract for callers where a non-zero is a legitimate negative;
`get_git_root()` now raises when git cannot be executed at all (instead of
silently taking the non-git branch); and `discover()` routes the inventory
commands through a checked runner that records unexpected failures into the new
manifest fields `git.errors` and `git.degraded`, with a matching WARNING in the
review packet so an empty inventory cannot read as a clean repo. Guarded by
`tests/test_discover.py::TestGitFailureSurfaced` (revert-proof: corrupts `.git/index`
so `ls-files`/`status` fail while the repo is still detected as git). The text
below is retained as the rationale until archived.

Evidence: `tools/discover.py` `run_git()` returns `[]` on `OSError` and on any
non-zero return code, so a missing git, an unsafe-directory refusal, a corrupt
index, or a permission denial collapses to the same empty result a genuinely
clean repo produces. The HEAD / branch / ls-files / status callers cannot tell
"nothing to report" from "git failed." Discovery output is cited as evidence for
governance drafting (the 2026-06-10 evidence rule), so a silently-empty git
result can become false evidence of a clean or empty repo.

Options: (a) make `run_git` fail loud — distinguish command failure from empty
output (e.g. return a sentinel / raise on non-zero), and have callers surface the
failure in the manifest rather than emitting a clean inventory; (b) leave as-is.

Recommendation: (a). This is a correctness fix squarely in service of the
existing evidence rule, not new surface. No design fork — implement directly
after recording. Prove the guard with the revert-the-fix test (a probe that
fails when `run_git` swallows an error).

---

### Open: `bootstrap.config.json` is documented layout but unshipped, and the update route depends on it

Status: Resolved 2026-06-28 — superseded by the "Collapse the update route into
migration; route detection is not load-bearing" decision in
`.agents/decisions.md`. That decision chose neither option (a) nor (b) but
dissolved the fork: the `update` route collapses into `migration`, the
`update`-vs-`migration` "is this ours" detection is eliminated, and
`bootstrap.config.json` is dropped from the documented layout (the `AGENTS.md`
`templateVersion` stamp covers the only real provenance need). The 2026-06-23
reframe below — "the question may be better framed as whether to collapse the
update route into migration" — is the framing that was adopted. Original entry
retained verbatim below.

Evidence: `README.md` lists `.agents/bootstrap.config.json` in the canonical
`.agents/` layout, but no template ships it and this toolkit's own `.agents/`
does not contain it. `tools/discover.py` `compute_route()` treats the presence of
`.agents/state.md` OR `.agents/bootstrap.config.json` as proof of toolkit
ownership and returns the `update` route, which then triggers AGENTS.md template
reconciliation (`procedures/bootstrap.md` Step 3). `state.md` is a generic name a
foreign governance system could also use, so a non-toolkit repo can be misrouted
into update/reconciliation; the only unambiguous toolkit marker would be the
config file, which does not exist.

Options: (a) define `bootstrap.config.json` (a provenance/version marker),
template it, populate it in this repo, and make it the authoritative update-route
marker — `state.md` alone becomes a weaker signal; (b) drop
`bootstrap.config.json` from the documented layout and tighten the update-route
test another way (e.g. require a toolkit-stamped `AGENTS.md`); (c) leave as-is.

Recommendation: decide between (a) and (b) before any code — this is a genuine
design fork. (a) gives a clean provenance marker and a place for the toolkit
version, at the cost of a new required artifact on every bootstrapped repo. (b)
is less surface. Either way it removes the false-positive route. Pairs with the
`run_git` fix as the two grounded `discover.py` issues from the reviews.

Owner decision 2026-06-22: option (a). Define `bootstrap.config.json` (a
provenance / toolkit-version marker), ship a template for it, populate it in this
repo, and make it the authoritative update-route ownership marker; `state.md`
alone stops being sufficient proof of toolkit ownership. Still Open: not yet
implemented. Next step is a `plan` for the file shape, the template, and the
`compute_route()` change.

Update 2026-06-23: owner chose not to decide this now — it stays Open, with no
priority judgment (an earlier note here called it "deprioritized"; that was the
agent's word, not the owner's). Owner did state a governing principle: the
bootstrap process should be thorough every time, and duration matters less than
thoroughness. Lead from discussion, not a decision: the route only selects which
procedure starts and every route converges behind the approval summary, so
detecting "is this ours" affects speed more than thoroughness, and both candidate
ownership signals (a `bootstrap.config.json` marker or a `templateVersion`-stamped
`AGENTS.md`) are weak as provenance — so the question may be better framed as
whether to collapse the update route into migration (cf. the 2026-06-22 "update
route reconciles a stale AGENTS.md" decision) than as shipping a routing marker.
No next step is committed yet; this supersedes the "next step is a plan" line
above.

---

### 2026-07-01 — AGENTS.md is the verbatim template, wholesale-replaced on update; repo-specifics live in one designated `.agents/` file

Status: Closed 2026-07-02 (Adopted 2026-07-01) — product implementation
landed 2026-07-01 (plan with commit map:
`docs/superpowers/plans/2026-07-01-agents-md-verbatim-template.md`): template
pointer section + `templates/repo-guidance.template.md` + shim imports;
`discover.py` `byteIdentical` carries `reconcileRecommended`; procedures
reconcile by replacement with the repo-guidance carve-out on both routes.
This repo's own carve-out landed 2026-07-02 via the `/update-governance`
dogfood run (commit 35b5436) — the end-to-end validation passed: discovery
flagged the mixed-content file, the carve-out + verbatim replacement went
through the approval gate, and the installed `AGENTS.md` is byte-identical
to the template. Settled with it (owner, same day): the repo
file is **extends-only** — no override path, no citation machinery (token
bloat); a genuine conflict is a defect (either the repo rule is stale or the
template rule was not universal and must be cut from the product). The
**universality test** — "if a repo could legitimately override it, it does
not belong in the template" — is the admission bar for template content; the
same-day removal of the rtk/token-efficiency bullet was its first
application. Text below retained as rationale.

Decision: In every bootstrapped repo — this toolkit included — `AGENTS.md` is
**byte-identical to the shipped `templates/AGENTS.template.md`**. All
repo-specific guidance (mission detail, active sources, verification
specifics, earned rule variants, remotes/push facts) lives in one designated
repo-specific file under `.agents/` that a template-owned pointer names.
Consequences:

- **Update = wholesale replacement.** A refresh run replaces `AGENTS.md` with
  the current template and touches nothing in `.agents/`. No carry-forward
  judgment, no hunk-walking, no stamp reasoning.
- **Drift detection = byte-compare.** Discovery compares the target's
  `AGENTS.md` against the current template; any difference recommends
  reconciliation. The `templateVersion` stamp becomes informational — the
  byte-compare is the load-bearing signal and is judgment-free.
- **Repo content enters `AGENTS.md` never.** First bootstrap/migration carves
  existing repo-specific guidance into the designated `.agents/` file; the
  portability sweep becomes that carve-out, run once, mechanical thereafter.

Earned by the 2026-07-01 incident chain, which showed the mixed-content design
fails twice over: (1) the dogfood self-application run stamped this repo's
`AGENTS.md` `2026-07-01.2` while seven pre-condensation template passages
remained — the stamp + structural-probe signals cannot see wording drift, and
a wrong stamp write self-seals (every later run reads "current"); (2) the
correction was then applied outside the sanctioned write path (`f697bf9`),
violating write-authority — mixed content invites exactly such judgment
edits. Separating template from repo content removes the judgment from the
loop entirely: the same mechanism-over-prose conclusion the eval workstream
reached for model guidance, applied to our own procedures.

Relationship: operationalizes the 2026-06-25 governance-boundary decision,
which recorded the portable/repo-specific *boundary* but not the
wholesale-replaceability rationale or the designated-file mechanism (the
owner's intent, stated at the time, had not been captured — this entry closes
that gap). Supersedes the 2026-06-25 scope-guard deferral of "retroactive
cleanup of already-bootstrapped repos" for any repo that refreshes (the
replacement run performs the cleanup), and supersedes this repo's own
`AGENTS.md` self-exemption parenthetical (removed when the file is replaced).
Simplifies, does not remove, the 2026-06-22 `templateVersion` machinery (the
stamp stays for reporting; byte-compare carries the decision). The 2026-07-01
portability-sweep rule (earlier entry, this file) is refined from
"relocate line-by-line during reconciliation" to "carve out once at first
migration; thereafter the file is replaced whole."

### Open: route/verification probes match literal `package.json` against repo-relative paths (monorepo subdir miss)

Status: Closed 2026-07-03 as not-applicable — the precondition resolved
against: subdir-scoped bootstrap is not a supported mode (see the 2026-07-03
"Subdir-scoped bootstrap is not a supported mode" decision in
`.agents/decisions.md`). The probe mismatch only bites on a subdir-scoped
run, which no supported path produces; no code change. Original entry
retained verbatim below.

Evidence: `tools/discover.py` tests membership of the literal `"package.json"` in
the path set, but paths are stored repo-relative (`relative_to(repo_root)`), so a
subdir-scoped run on e.g. `packages/api/` yields `packages/api/package.json`,
which never matches — silently losing verification-command detection for the
scoped case.

Precondition: confirm whether subdir-scoped bootstrap is a supported mode. If it
is not a real path, this does not bite and should be closed as not-applicable
rather than fixed.

Recommendation: resolve the precondition first. If scoped runs are supported,
match by basename / suffix instead of literal full-path membership. Lower
priority than the two above.

---

Rotated 2026-07-03: the following same-day entry was superseded within hours by
"Playbooks install unconditionally on every run, like wrappers and hooks" in
`.agents/decisions.md` — the no-discretion principle survived; the owner-question
mechanism did not. Wording preserved verbatim.

### 2026-07-03 — Playbook installation is an owner choice at the approval gate, never agent discretion

Status: Superseded 2026-07-03 (same day) by "Playbooks install unconditionally
on every run, like wrappers and hooks" in `.agents/decisions.md`.

Decision: whether a target repo receives any shipped playbook (e.g.
`templates/playbooks/reviewloop.md`) is decided by the owner at the approval
gate, never by the agent. The prior rule — "playbooks only if the scope tier
justifies them" / "install one when the repo's work calls for it" — delegated
the install decision to agent judgment about the repo's future needs, which
the model cannot assess (owner directive, 2026-07-03: nothing about which
durable artifacts a repo receives is up to the model's discretion).
`templates/approval-summary.template.md` gains a Playbooks section that lists
every playbook template shipped under `.bootstrap-tmp/templates/playbooks/`
with a one-line purpose and asks the owner at approval time which to install;
the default is none, and the agent may not pre-select or infer the answer from
the scope tier, the decisions log, or other context — the owner's approval-time
reply is the only valid source. Owner-selected playbooks are installed into
`.agents/playbooks/<name>.md` and join the single scoped commit; the scope
tier remains a stated recommendation in the summary but no longer carries the
playbook decision.

Earned by a live gap (2026-07-03): the reviewloop playbook was silently absent
from a bootstrapped repo (Powershell-Token-Killer) because the run's agent
judged the scope tier did not justify it — the owner had no visibility that a
shipped playbook existed to decline. Mirrors the Push Policy precedent
(2026-06-27): a repo-specific choice is presented as standardized options at
the gate and answered by the owner, not inferred.

Supersedes: the "playbooks only if the scope tier justifies them" clauses in
`procedures/bootstrap.md` Step 4 and `procedures/migration.md` Step 2 item 6,
and the tier-gated playbook wording in `docs/design.md` Guidance Scope. The
2026-06-09 layout decision's "optional playbooks" stands — playbooks remain
optional; what changes is who decides.
