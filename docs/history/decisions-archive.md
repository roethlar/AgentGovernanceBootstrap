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

### Open: the authority/scope boundary has no stated precedence over the content-quality invariants

Evidence: The Prime Invariants (`templates/AGENTS.template.md:8-18`) require
"act only on an explicit instruction," and `procedures/bootstrap.md` Step 0 makes
the toolkit repo read-only except for the sync, but the content-quality invariants
— "Keep one canonical location… Prefer pointers over duplicating"
(`templates/AGENTS.template.md:46-47`), the `decision`/`drift` operators that write
canonical files, and `procedures/migration.md`'s fold-into-canon guidance — carry
no scope-of-authorization qualifier, and no cross-section precedence statement
reconciles the two. Earned by a real reproduced incident: during a 2026-06-23
`headroom` dogfood run the agent appended 19 lines to *this* repo's own
`.agents/decisions.md` (an unauthorized write to canonical governance, in a
different repo than the one under bootstrap), justified by "augment canonical
entry, don't duplicate"; `git diff` showed `.agents/decisions.md | 19 +++` against
an otherwise-clean tree and the edit was reverted with `git restore`. The agent
had, one message earlier, itself articulated the read-only guardrail and still
failed to bind it — so the gap is structural (no precedence rule, no checkpoint),
not a one-off lapse. Source: `bugs/headroom-authority-boundary-overreach-2026-06-23.md`.

Options: (a) add an explicit precedence rule to the Prime Invariants (echoed in
`bootstrap.md`): the authority/scope boundary outranks every content-quality
principle; an agent may never edit a canonical or tracked governance artifact (and
never any file in the toolkit repo beyond the Step 0 sync) without an explicit
instruction naming the file or edit; "fold into canonical home / don't duplicate"
applies only within the repo scope the session is authorized to write, and only on
an explicit go; a finding that belongs in a file the session may not write goes
only into the sanctioned scratch/report outputs. (b) leave as-is.

Recommendation: (a). It hardens a load-bearing authority invariant against a
reproduced failure and changes prose, not code. Because it edits the Prime
Invariants — the highest-authority block — record it for an explicit owner
decision rather than treating this standing recommendation as the go. Prove the
bite with a re-run scenario: an agent that finds a matching canonical entry and is
told "drop the scratch file in X" must produce only the cross-reference, never an
edit to the canonical file. Relationship: extends the 2026-06-10
"answer-with-words / artifact-is-evidence-not-decision" decisions with a precedence
rule against the content-quality invariants. Affected files:
`templates/AGENTS.template.md` (Prime Invariants), `procedures/bootstrap.md`
(Step 0 read-only echo), `procedures/migration.md` (bound the fold/augment-into-canon
guidance by authorization scope).

### Open: a `governance-lint` self-audit playbook (mechanical checks only)

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): its named substrate (repo-map.json `guidance_paths`/`validated_against`, discover.py helpers) was deleted; if ever built it walks `.agents/` live. Owner disposition pending: close as obsolete or re-scope.

Evidence: `AGENTS.md` advertises `.agents/playbooks/*` as an authority slot and a
`playbook <name>` operator. The toolkit already ships a playbook template
(`templates/playbooks/reviewloop.md`, a two-agent review loop installable into a
target repo), but this repo's own `.agents/playbooks/` directory does not yet
exist — so governance-lint would be the first playbook authored as a self-audit,
not the first use of the mechanism. (Amended 2026-07-03: `reviewloop.md` now
installs on any refresh/dogfood run per the playbooks decision, so
governance-lint would not necessarily be the first playbook *installed* here;
it remains the first self-audit playbook authored.)
Three doc-health checks are mechanizable
against existing structures: (1) **state freshness** — `.agents/repo-map.json`
carries a structured `validated_against: {commit, date}`; compare it against the
git log for `.agents/` to flag a state doc that has drifted past its last
validation; (2) **pointer/section/stamp resolution** — cross-references are
backtick-wrapped paths (regex-extractable, `Path.exists()`-checkable),
`repo-map.json.guidance_paths` supplies the golden file list to walk, and
`discover.py` already has `extract_template_version()` for the stamp; (3) dead
backtick-path links fall out of (2). `discover.py` exposes reusable helpers
(`run_git`, `match_paths`, `extract_template_version`), so the core is ~150 lines.
Evidence-citation sufficiency and prose-reference resolution are explicitly NOT
mechanizable (they need semantic judgment) and stay the `drift` operator's job.

Options: (a) build a standalone `.agents/playbooks/governance-lint.md` (+ a small
Python checker) covering freshness + pointer/section/stamp resolution, run
on-demand and recommended by the migration route's reconciliation branch — not a
blocking gate; (b) fold the mechanical freshness check into the existing `drift`
operator without a new playbook; (c) YAGNI — leave it.

Recommendation: (a), with evidence-citation checking declared an explicit
non-goal. It fills the already-advertised, currently-empty playbook slot rather
than adding new surface; it stays agent-driven (a playbook the agent runs, not a
script gate); and it makes the `validated_against` freshness signal — which
nothing currently checks despite guarding the "discoverable current-state entry
point" invariant — actually load-bearing. The narrow form (freshness +
pointer/stamp) is not YAGNI; the broad "audit governance health" form Grok
originally proposed would be.

Owner decision 2026-06-22: option (a) — standalone
`.agents/playbooks/governance-lint.md` plus a small checker, run on-demand and
recommended (not gated) by the migration route's reconciliation branch
(reworded 2026-07-01 per the adopted route collapse); evidence-citation
sufficiency stays an explicit non-goal (the `drift` operator's job). Still
Open: not yet implemented. Next step is a `plan` for the checker.

> Adopted 2026-07-08 (owner: "build it", always-on): the lint lives in
> `tools/refresh.py` (`lint_governance`), running unconditionally on every
> refresh — read-only LINT report lines for dead path references in
> `AGENTS.md`/`.agents/*.md` prose and closed decisions awaiting archive;
> never blocks, never edits. Re-scoped from the original playbook shape:
> its named substrate (repo-map.json fields, discover.py helpers) was
> deleted by the 2026-07-08 consolidation, and a check nobody triggers
> rots — riding the refresh touchpoint is the field-audit lesson. The
> structural-conformance half of the original idea is refresh.py's core
> function. Guard-proven tests in tests/test_refresh.py.

### 2026-07-04 — Specific-over-generic precedence: explicit boundaries and no-discretion rules outrank generic defaults

Status: Adopted 2026-07-04 (rule lives in `templates/AGENTS.template.md`
`## Universal Invariants`, stamp `2026-07-04.1`; presence-guarded by
`test_universal_invariants_rank_specific_over_generic` in
`tests/test_discover.py`).

Decision: an explicit authority or scope boundary, or a rule or decision whose
wording removes discretion for the case it names ("unconditional", "no per-run
choice", "deterministic"), outranks every generic default for that case —
flag-conflicts, one-canonical-location, smallest-guidance-set included. Agents
apply it as written and do not reopen the settled case as a conflict or
approval question against surrounding repo state such as git history; generic
defaults govern only questions no more specific rule has already resolved.

Earned by the second reproduction of the same missing-precedence defect shape:

- 2026-06-23 (`bugs/headroom-authority-boundary-overreach-2026-06-23.md` in
  the `agent-harvest` dropbox): the "fold into canonical home" content-quality
  instinct overrode the read-only authority boundary — an agent in a headroom
  dogfood run wrote 19 unauthorized lines into this repo's
  `.agents/decisions.md`. Recorded then as the narrower Open finding "the
  authority/scope boundary has no stated precedence over the content-quality
  invariants", whose recommended fix was scoped to that one pair.
- 2026-07-04
  (`bugs/AgentGovernanceBootstrap-flag-conflicts-invariant-no-precedence-over-nondiscretionary-decisions-2026-07-04.md`,
  which supersedes the same run's earlier wiring-gap report): a
  `/update-governance` run read the 2026-07-03 unconditional-playbook-install
  decision, quoted its no-discretion language verbatim, and still raised the
  reinstall of a recently-reverted playbook as an approval-summary question by
  invoking the generic flag-conflicts invariant against git history —
  reproducing the exact behavior that decision forbids.

The recurrence between a different pair of rules shows the gap is between rule
*classes*, not one pair, so the fix is the general precedence rule above (the
bug report's proposed fix; owner fix instruction 2026-07-04). This broadens
and adopts the 2026-06-23 Open finding rather than adding a third, narrower
entry; that finding is archived verbatim in
`docs/history/decisions-archive.md` in this same change.

Deliberately not implemented: the original finding's procedure-level echoes (a
read-only echo in `procedures/bootstrap.md` Step 0, an authorization-scope
bound on `procedures/migration.md`'s fold-into-canon guidance). The Universal
Invariant is the single full statement (2026-06-24 dedup decision); procedure
echoes are future hardening only if the invariant alone proves insufficient in
a reproduced incident. Outstanding bite proof, per the bug report: a re-run of
the reinstall scenario (a shipped playbook missing after a recent deliberate
revert) must draft the reinstall as a plain fact citing the 2026-07-03
decision, with no question raised — checkable on the next refresh/dogfood run.
The presence test guards the text, not the behavior.

Relationship: supplies the precedence backbone the 2026-06-10
answer-with-words / artifact-is-evidence decisions and the 2026-07-03
playbooks decision assumed; refines, does not weaken, the flag-conflicts
Universal Invariant (document-vs-document disagreements are still flagged —
the default now yields only where a more specific rule has settled the exact
case). Structural template change, so the stamp bumps `2026-07-02.1` →
`2026-07-04.1` per the 2026-06-22 reconciliation machinery. This repo's own
`AGENTS.md` stays a frozen instance, reconciled by the next self-application
run.

> Archived 2026-07-08 (sweep): Adopted; the invariant lives in templates/AGENTS.template.md.

### 2026-07-02 — Shipped hook commands: `py -3 || python3` fallback chain; Windows scope is Git Bash

Status: Adopted 2026-07-02

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): mooted — the sole surviving shipped hook is a plain inline echo; no shipped hook invokes an interpreter. (plan with commit map:
`docs/superpowers/plans/2026-07-02-hook-python3-windows-fallback.md`; rule
lives in the hook templates, the strengthened tripwire test, and the
bootstrap procedure's hook-install step).

Decision: shipped hook commands that invoke Python use the interpreter
fallback chain `py -3 <script> 2>/dev/null || python3 <script>` — never bare
`python3` — mirroring the bootstrap procedure's Step 1 probe order. On
Windows the supported execution path is Git Bash (owner, 2026-07-02: Git for
Windows is already a Claude Code requirement, so PowerShell-only Windows
hosts are out of scope for hook commands). Claude Code hook commands
reference the project root as braced `${CLAUDE_PROJECT_DIR}` (substituted by
the harness itself, shell-independent), not unbraced shell expansion.

Rationale: harvest bug
`bugs/ExchangeAdminWeb-hook-python3-discovery-2026-07-02.md`
(roethlar/agent-harvest) — on stock Windows, `python3` on PATH is a Microsoft
Store stub, so the AGENTS.md tripwire ran the stub and was silently inert;
the discovery probe was hardened against this exact pitfall
(`procedures/bootstrap.md` Step 1) but the hook templates were not. Harness
facts per Claude Code hooks docs (checked 2026-07-02): Windows shell-form
hooks run in Git Bash if installed, else PowerShell; no OS-conditional hook
mechanism exists, so one committed command string must serve all machines.

> Archived 2026-07-08 (sweep): mooted by the 2026-07-08 consolidation — the sole shipped hook is a plain echo.

### 2026-07-02 — AGENTS.template.md ships reflowed: no hard line-wraps; future template edits preserve this

Status: Adopted 2026-07-02 (plan with commit map:
`docs/superpowers/plans/2026-07-02-template-reflow.md`), stamp `2026-07-02.1`.

Decision: the body of `templates/AGENTS.template.md` is written one line per
paragraph or bullet — no hard line-wrapping. Future template edits preserve
this format; re-wrapping is a regression. Scope is the verbatim-installed
template only: `repo-guidance.template.md`, shims, and `procedures/*` stay
wrapped (they are hand-edited in target repos or in this repo, where wrapped
lines keep diffs reviewable).

Rationale: the 2026-07-01 verbatim-template decision removed every consumer
of wrapping in target repos — the installed `AGENTS.md` is never hand-edited,
reconciles by byte-compare + replace-whole (no hunk diffs), and is read raw
by models. Wrapping's only remaining effect is a per-session token tax: each
wrapped continuation line spends a newline plus indent. Measured 2026-07-02
via the token-counting API (`claude-opus-4-8` tokenizer): 3,873 → 3,700
tokens, a lossless −4.5% per session in every governed repo. Accepted cost:
template-source diffs in this toolkit repo become paragraph-blob diffs.
Consistent with the 2026-06-22 rejection of word-level compression (~2.7%):
that trade risked meaning for tokens and was declined; this one changes no
words.

The same version bump executes T1 of the 2026-07-01 verbosity-sweep report
(Session Startup hook-trust trim, ~26 words of rationale clauses; behavioral
contract unchanged) — owner go 2026-07-02 covered folding it in, so the
governed fleet reconciles once, not twice. The remaining sweep findings stay
pending owner IDs.

> Archived 2026-07-08 (sweep): Adopted; the no-re-wrap rule is restated in .agents/repo-guidance.md (Earned Practices).

### 2026-07-01 — Governance refresh entry point; portability sweep in reconciliation; Python 3.9 floor

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the update-governance wrapper now invokes `tools/refresh.py` (the mechanical refresh); the bootstrap procedure remains the judgment path. The 3.9 floor stands and now covers refresh.py. (implemented same day; plan:
`docs/superpowers/plans/2026-07-01-route-collapse-refresh-and-portability-sweep.md`).

Three durable rules landed alongside the route-collapse adoption (see the
Adopted 2026-06-28 entry below):

- **`update-governance` is a wrapper-only entry point** shipped at
  `templates/commands/claude/update-governance.md`: verify the canonical
  remote, shallow-clone fresh to scratch, follow the synced
  `procedures/bootstrap.md`. It is not an `AGENTS.md` operator and adds no
  write authority — every change still passes the approval gate. The wrapper
  guarantee is keyed to the shipped template directory
  (`templates/commands/<harness>/`), not to the operator vocabulary, so
  non-operator wrappers join it without editing governance. The toolkit repo
  itself receives the wrapper only via a dogfood self-application run (owner
  pick, 2026-07-01) — that run doubles as the end-to-end test of the flow.
- **The reconciliation branch runs a portability sweep** (full statement:
  `procedures/migration.md` Step 2): every carried-forward `AGENTS.md` line
  faces the portability test; repo-specifics relocate to `.agents/` with
  pointers, through the same approval summary. This implements, for every
  refresh run, the retroactive cleanup the 2026-06-25 boundary decision
  deferred; a dedicated one-shot cleanup pass is no longer needed for repos
  that refresh. Mid-task relocation remains the `drift` operator's job.
- **Python 3.9 is the supported floor** for the toolkit's product code
  (README / docs/usage.md); below-floor probes fall through to versioned
  interpreter names (`procedures/bootstrap.md` step 3). Earned by a real
  incident: `tests/test_run_fixture.py` used PEP 604 syntax, failed to import
  on the macOS system 3.9, and silently hid 84 tests behind one import error
  (fixed 2026-07-01, commit ad7e9e8).

Also fixed under the same plan: the `operator:playbook` probe false positive
(bug filed 2026-06-22) — the probe now word-boundary-matches, guarded by a test
that the shipped template self-reports zero missing sections.

> Archived 2026-07-08 (sweep): superseded/re-homed by the 2026-07-08 consolidation — wrapper invokes tools/refresh.py, the carve-out lives in procedures/bootstrap.md, the 3.9 floor in README/docs/usage.md.

### 2026-07-01 — Functional cut of the product template; completeness prose deferred entirely

Status: Active (implemented same day; `templateVersion` 2026-07-01.1).

Decision: `templates/AGENTS.template.md` underwent a **functional cut** — every
clause classified as behavioral contract, fact/pointer, or definition was kept
(surviving claims keep full-sentence wording); rationale clauses, worked
examples, and same-altitude duplication were removed. The largest single change
applies the 2026-06-24 dedup decision: the `drift` operator no longer restates
the portability test and its Flag/Allow lists — it points to the
governance-boundary invariants, which keep the single full statement. Session
Startup was reduced to its two load-bearing steps (read state before changes;
hook trust). Result: 13,355 → 10,623 bytes, 1,993 → 1,587 words (−20%),
roughly 600–700 tokens saved per session in every bootstrapped repo.
Owner signed off a full per-claim accounting with an explicit drop list at the
approval gate; plan and drop list:
`docs/superpowers/plans/2026-07-01-guidance-condensation.md`.

Also settled: **`completeness-general` prose is deferred entirely** — not
shipped in any form (not even opt-in). Eval evidence: weak-model-only benefit,
one ceiling harm, null on strong harnesses. The profile remains in
`evals/governance_profiles/` as a candidate; any future ship is a fresh owner
decision. This closes the former G1/G2 question from the 2026-06-30
hook-and-prose plan.

Earned by the closed eval workstream's conclusion (guidance prose is
placebo-to-harmful on strong models; the per-session size of the injected
template is a recurring tax) and by the owner's 2026-06-30 direction to make
the existing guidance more token-efficient. Notably, the cut found **no
capability-exhortation prose in the template** — the removed mass was rationale
and duplication — consistent with the 2026-06-22 density audit.

Relationship: complements, does not supersede, 2026-06-22 (word-level
compression stays rejected; this cut removes whole non-normative clauses, never
squeezes surviving wording) and applies 2026-06-24 (one full statement,
pointers elsewhere) inside the template. Exercises the 2026-06-22/25.2 stamp
machinery (dotted sub-version, enforced by test). Scope: template only —
`procedures/` condensation was explicitly deferred (owner pick S1) and needs
its own plan; this repo's own `AGENTS.md` is a frozen instance reconciled only
by a future self-application run.

> Archived 2026-07-08 (sweep): Adopted (template since redlined further by the consolidation); the completeness-general profile was deleted with the evals scrap.

### 2026-06-28 — Collapse the update route into migration; route detection is not load-bearing

Status: Adopted 2026-07-01.

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): carried further — the two procedures are consolidated into one `procedures/bootstrap.md` with the migration inventory as a conditional step; mechanical reconciliation moved to refresh.py. Implemented per
`docs/superpowers/plans/2026-07-01-route-collapse-refresh-and-portability-sweep.md`:
`compute_route()` is single-route (commit 07ceb09), the reconciliation branch
lives in `procedures/bootstrap.md` Step 3 with `procedures/migration.md` naming
the already-canonical and dogfood cases, and `bootstrap.config.json` left the
documented layout (README, design doc, repo-map template) with `templateVersion`
bumped to 2026-07-01.2 (commit a48790d). Text below retained as rationale until
archived.

Decision: The `update` route collapses into the `migration` route. One route
then handles every repo that already has governance — a foreign governance
system to inventory, an already-toolkit-bootstrapped repo, or this toolkit's own
self/dogfood run — with the `<!-- templateVersion -->` reconciliation of a stale
or unstamped `AGENTS.md` (the 2026-06-22 decision) retained as a branch *within*
that single route, not removed. `greenfield` (a repo with no existing governance)
stays a distinct route; whether it too should fold is explicitly **not** part of
this decision. What is eliminated is the `update`-vs-`migration` "is this repo
already ours" determination in `compute_route()` — that detection was never
load-bearing.

Reason: every route converges behind the same approval-summary gate and produces
the same vetted output, so route selection only ever affected *speed*, never
correctness or safety. A misroute's worst case is "ran the slightly heavier
procedure," not a wrong result. Both candidate ownership signals — the presence
of `.agents/state.md` (a generic name a foreign system could also use) and a
`bootstrap.config.json` marker — are weak as provenance. The owner principle on
record (thorough every time; duration matters less than thoroughness) favors one
thorough path over two paths plus a fragile detector. This also drops
`bootstrap.config.json` from the documented `.agents/` layout in `README.md`:
nothing ships it, and the `AGENTS.md` `templateVersion` stamp already covers the
only real provenance need.

Considered and rejected: (a) ship `bootstrap.config.json` as a provenance/version
marker — adds a new required artifact on every bootstrapped repo and a second
version-of-truth source that drifts from the `templateVersion` stamp the moment
one is edited without the other, against the smallest-guidance-set invariant and
the 2026-06-28 harness-neutral / no-redundant-provenance direction; (b) keep two
routes but switch the update marker to the `templateVersion` stamp — zero new
files, but still treats "is this ours" detection as load-bearing for no
correctness gain. The fork is dissolved rather than answered.

Accepted cost: an already-bootstrapped or dogfood run now does the unified
route's inventory pass over files already in canonical layout (verdict "leave /
already-canonical") — slightly more ceremony than `update`'s reconcile-only path,
converging correctly at the same gate, consistent with thorough-every-time.

Scope / deferral: implementation is owner-gated code/procedure work needing a
separate `plan`, and touches `tools/discover.py` `compute_route()` (drop the
`update` branch), the procedure merge (`procedures/bootstrap.md` +
`procedures/migration.md` into one route, folding in the `templateVersion`
reconciliation branch and the dogfood-in-place lens), `README.md` (drop
`bootstrap.config.json` from the documented layout),
`templates/AGENTS.template.md` Bootstrap Handoff / any "update route" wording,
and the several Open entries that name "the update route" (the monorepo-subdir
probe, committed-wrapper staleness, the `governance-lint` update-route
recommendation) reworded to the single route in that plan. The `templateVersion`
reconciliation machinery is retained — it moves into the single route, it is not
dropped.

Relationship: resolves the `Open: bootstrap.config.json` fork (archived verbatim
in `docs/history/decisions-archive.md` in this same change) and answers its
2026-06-23 reframe — "the question may be better framed as whether to collapse
the update route into migration" — in the affirmative. Exercises, does not
supersede, the 2026-06-22 update-route `templateVersion` reconciliation decision
(that step is folded into the single route). Amends the 2026-06-27
dogfood/self-application decision's "takes the existing `update` route" wording:
the dogfood case becomes a named in-place case of the single route (run the one
procedure in-place; a missing `.bootstrap-tmp/` at kickoff is still the normal
start); that decision otherwise stays Active and its anti-stop handrail is, if
anything, more necessary because the unified route inherits migration's
foreign-target framing.

Earned by the 2026-06-23 reframe of the `bootstrap.config.json` Open Decision and
this session's analysis confirming detection only affects speed and a new marker
file fights the recent harness-neutral direction. Owner decided 2026-06-28.

> Archived 2026-07-08 (sweep): Adopted; carried further by the consolidation (single procedure, mechanical refresh).

### 2026-06-27 — Dogfood / self-application is a named case of the update route (docs handrail, no detection mechanism)

Status: Active, as amended by the 2026-06-28 collapse (Adopted 2026-07-01): the
dogfood case is now a named in-place case of the single `migration` route; the
"update route" wording below is the pre-collapse record. The anti-stop handrail
is unchanged.

Decision: Running the bootstrap procedure against this toolkit repo itself is a
**dogfood / self-application run**. It takes the existing `update` route and runs
**in-place** — there is no foreign target, the absence of `.bootstrap-tmp/` at
kickoff is the normal start (Step 1 discovery creates it), and the agent follows
`procedures/bootstrap.md` top to bottom with the approval summary as the single
gate. `procedures/bootstrap.md` names this case explicitly so an agent does not
read its "you are in a target repo" framing as "this procedure is not for here."
No `compute_route()` change, no manifest detection flag, no enforcement: the fix
is documentation only — a lens and a nudge. The route logic and what `update`
produces are unchanged.

Earned by a reproduced incident (2026-06-27): two capable sessions in a row, run
with the canonical kickoff line `Read ./procedures/bootstrap.md and follow it.`
from inside the toolkit repo, read the procedure's target-repo framing plus the
missing `.bootstrap-tmp/` as "nothing to bootstrap here" and stopped to ask the
owner instead of running discovery. Earlier runs (and an earlier run the same day)
had improvised past the framing and reached the update route correctly, so the
self-application case worked only by agent intuition, never by an explicit
instruction. Naming the case removes the ambiguity without disturbing the
behavior that has always worked.

Considered and rejected: a `selfApplication` detection flag in `compute_route()`
(by git-root identity or remote URL). Rejected because agents have reliably
understood "this repo is both the product and the target" without a mechanism;
adding detection risks breaking that intuition to fix a case a docs handrail
already covers.

Relationship: complements the 2026-06-22 update-route reconciliation decision
(this run exercises that route against the toolkit's own `AGENTS.md`); does not
change route selection.

> Archived 2026-07-08 (sweep): Adopted-elsewhere — the consolidated procedures/bootstrap.md names the self-application case in its intro.

### 2026-06-22 - Bug reports are filed to the agent-harvest dropbox under `bugs/`

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): superseded — defects are filed as GitHub issues on this repo (`.github/ISSUE_TEMPLATE/toolkit-defect.md`), owner-gated, redacted; the dropbox transport is retired.

Decision: The shared `agent-harvest` dropbox (canonical on GitHub at
`roethlar/agent-harvest`) stores not only harvested governance rules but also bug
reports for defects in the AgentGovernanceBootstrap product itself — its code or
its procedures — under a `bugs/` folder, kept separate from the top-level rules
mailbox. When a run (dogfood here or a foreign target-repo session) confirms a
defect, the agent auto-writes a structured report from
`templates/bug-report.template.md` and files it per the canonical recipe
`procedures/file-bug-report.md`: preferred no-clone write via `gh api` to GitHub,
clone-and-commit fallback, and an in-repo `.agents/bug-reports/` last resort when
the dropbox is unreachable. Writing the report is automatic; any publish (the
`gh api` write or a clone push) requires an explicit owner go, per the
pushing-publishes invariant. Bug files are append-only. The harvest sweep
(`procedures/harvest.md`) reads `bugs/` and triages each report (still-open /
already-fixed / fix-now) rather than folding it into a template; a fix is a
separate scoped change.

Earned by a real incident: the 2026-06-22 dogfood run found a false positive in
`tools/discover.py` (the `operator:playbook` probe matched a bare `` `playbook` ``
while the operator is written `` `playbook <name>` ``, so it was always reported
missing and wrongly recommended reconciling a current `AGENTS.md`). There was no
durable home for that finding, because the dropbox README scoped the mailbox to
rules only. This decision closes that gap.

Relationship: extends the harvest dropbox's role (the 2026-06-11 harvest mailbox
conventions) to a second artifact class; does not change the rules-harvest gating,
naming, or template.

Follow-up (same day): the dropbox-write mechanics were factored into a single
shared transport recipe, `procedures/file-to-dropbox.md`, used by both the harvest
report path (`procedures/migration.md` Step 8) and the bug report path
(`procedures/file-bug-report.md`). This gave the harvest path the no-clone
`gh api` transport it lacked and retired its former standing auto-push: every
publish to the dropbox now asks for an explicit owner go, consistent for both
artifact classes. The `gh api` PUT path was verified end-to-end against
`roethlar/agent-harvest` on 2026-06-22.

> Archived 2026-07-08 (sweep): Status corrected to Superseded by the 2026-07-08 consolidation — defects are GitHub issues (.github/ISSUE_TEMPLATE/toolkit-defect.md).

### 2026-06-09 - Harvest is minimal, gated, dropbox-first

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): transport superseded — harvest rules are filed as GitHub issues (`.github/ISSUE_TEMPLATE/harvest-rule.md`); the discipline (incident-earned, max three, no-report-is-normal, owner-gated publish) is retained verbatim there.

Decision:
During a migration the agent may (rarely) record generalizable governance rules in a harvest report, under strict limits: expected outcome is no report; an idea qualifies only if earned by a real citable incident, not already covered by templates, useful to other repos, and at most three ideas total; never a "nothing found" file. Delivery: write append-only as a new dated file in the `agent-harvest` dropbox via the shared transport recipe (`procedures/file-to-dropbox.md`), which any session may publish to only with an explicit owner go; otherwise fall back to `.agents/harvest.md` in the target. Harvest reports are never delivered into the canonical bootstrap repo itself. (Supersedes the earlier "standing authorization" auto-push: as of 2026-06-22 every dropbox publish — harvest report or bug report — asks before pushing, so the two paths share one transport and one gate.)

Reason:
Prevents over-eager padding and keeps the shared canon clean. A separate sweep session (owner-initiated only) in this repo judges new reports skeptically and logs outcomes in `harvest/processed.md`.

Supersedes:
Earlier ideas of richer or automatic harvesting.

> Archived 2026-07-08 (sweep): Status corrected to Superseded in transport by the 2026-07-08 consolidation; the harvest discipline lives verbatim in .github/ISSUE_TEMPLATE/harvest-rule.md.

### 2026-06-09/10 - Single-session kickoff with Python discovery; self-healing freshness

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): the discovery script is retired; discovery is a live checklist in the consolidated procedure. The single-session kickoff, Step 0 sync, and self-healing freshness principles stand.

Decision:
The agent runs discovery (`tools/discover.py`) as Step 1 inside the kickoff session. The script is kept because it guarantees completeness on large repos without model-dependent laziness. A stale or missing manifest causes automatic re-run (self-healing). The only refusal case is a sandboxed environment that literally cannot execute the script. Every bootstrap run begins with a cwd-independent sync of the bootstrap toolkit from GitHub (the canonical remote), using the LAN gitea mirror as a faster fetch source when reachable, via `git -C`, `ls-remote` liveness, and `--ff-only` merge to GitHub's head; offline or diverged clones proceed with a plain-English flag and never block.

Reason:
One prompt ("Read <path>/procedures/bootstrap.md and follow it.") is sufficient. Two-stage (human runs script first) remains only as documented fallback. Freshness must come from git, not time or filenames.

Supersedes:
The earlier two-stage-only flow and any reliance on shell cwd.

> Archived 2026-07-08 (sweep): the script half is superseded (live-checklist discovery); the kickoff and Step 0 sync principles live in procedures/bootstrap.md.

### 2026-06-22 - Update route reconciles a stale AGENTS.md; templateVersion stamp detects drift

Status: Active

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): superseded — the stamp is removed; refresh.py's newline-normalized compare against known template versions carries the decision, and the refresh commit message records the toolkit sha as provenance.

Decision:
Bootstrapped repos carry a `<!-- templateVersion: YYYY-MM-DD -->` stamp at the
top of `AGENTS.md`, mirroring the stamp in the toolkit's
`templates/AGENTS.template.md`. Discovery records an `agentsTemplate` block in the
manifest (`currentVersion`, `targetVersion`, `reconcileRecommended`,
`missingSections`): it compares the target's stamp against the toolkit's and, on
the update route, probes the target `AGENTS.md` for missing structure (the Prime
Invariants block, the operator set). The update route (`procedures/bootstrap.md`
Step 3) reconciles a stale or unstamped `AGENTS.md` to the current template -
reusing the `procedures/migration.md` Step 2 discipline (carry earned rules
forward, migrate the rule not its stale examples, verify migrated facts) - before
running the operator-wrapper and hook guarantees. The wrapper/hook guidance treats
a missing target section as a staleness signal to reconcile, never a cue to narrow
the artifact to fit the stale file. Bump the stamp when the template's structural
contract changes; a forgotten bump is backstopped by the missing-sections probe.

Reason:
The update route previously delegated straight to the target's own
(older-template) bootstrap-handoff rule and never reconciled `AGENTS.md`, so the
all-routes wrapper/hook guarantees - drawn from the current templates - pointed at
sections (Prime Invariants, `playbook`) a stale file lacked. With no instruction
to upgrade the source, an agent narrowed the wrappers to fit the stale file,
degrading the toolkit's own canon. This closes the gap: detect drift mechanically,
reconcile the source.

Supersedes:
Refines the 2026-06-18 "generated repos self-audit on update runs" assumption,
which held only when `AGENTS.md` was already at the current template version; that
decision stays Active for the wrapper guarantee itself.

> Archived 2026-07-08 (sweep): Status corrected to Superseded by the 2026-07-08 consolidation — refresh.py's normalized compare + commit-message provenance replaced the stamp.

### 2026-06-22 - Trim the per-session guidance tax: Bootstrap Handoff pointer; rtk discretionary, not a hook

Status: Active, as amended 2026-07-01 (owner directive, two steps): the
template's token-efficiency bullet is removed from the product entirely — no
`rtk` reference and no generic replacement — guarded by a test that the
shipped template contains no `rtk` mention. The discretionary-not-a-hook
stance below remains this repo's own recorded practice (a repo-guidance fact,
not product text). The Bootstrap Handoff pointer clause is unaffected.

Decision:
`CLAUDE.md` `@`-imports the whole `AGENTS.md` every session, so `AGENTS.md` length
is a recurring per-session cost. A density audit found prose compression yields only
~2.7% savings once every normative claim must survive (the guidance is dense with
load-bearing rules, not padded), so we do NOT compress wording. Instead: (1) the
`## Bootstrap Handoff` section - only actionable when `.bootstrap-tmp/` exists, and a
near-duplicate of the synced `procedures/bootstrap.md` - is collapsed to a short
conditional pointer to `.bootstrap-tmp/START-HERE.md` + `procedures/bootstrap.md`,
making the procedure the single canonical home and cutting ~600 tokens/session;
(2) the token-efficiency invariant encourages `rtk` (https://github.com/rtk-ai/rtk)
as a discretionary per-command proxy and forbids its auto-rewrite hook, which would
compress every Bash call and remove the agent's access to raw output when it matters;
it generalizes to compact-but-equivalent working (targeted reads, scoped searches, no
re-reads).

Reason:
Reduce recurring context cost without losing semantic content. Update routing is
unaffected - `compute_route()` keys off the `.agents/` layout markers, not the
section's presence.

Supersedes:
Nothing. Complements the 2026-06-22 update-route reconciliation decision: the
reconciliation and wrapper-guard logic now lives solely in `procedures/bootstrap.md`,
no longer duplicated in the template's Bootstrap Handoff section.

> Archived 2026-07-08 (sweep): superseded — the Bootstrap Handoff section was removed entirely by the consolidation; the discretionary-filter practice lives in .agents/repo-guidance.md (Earned Practices).

### 2026-06-25 - Stall-not-length: iterative processes escalate on stalled progress, never on duration

Status: Adopted 2026-06-25. The invariant landed as a bullet in
`templates/AGENTS.template.md` `## Universal Invariants` ("Escalate an iterative
process on stalled progress, never on duration…"), with `templateVersion` bumped
2026-06-22 → 2026-06-25 so the update route reconciles stale targets. This repo's
own `AGENTS.md` is intentionally NOT edited here: it is a frozen instance brought
current only by a deliberate self-application run (same handling as the 2026-06-24
deduplication decision), so the missing bullet there is expected, not drift. The
text below is retained as the rationale until archived.

Decision (design settled 2026-06-25, five points the owner approved):
A new Universal Invariant governs every iterative agent process — a loop, a
multi-finding sweep, a long autonomous run. The escalation trigger is **stall, not
length**: a process must surface to a human when it completes a cycle that banks no
**verifiable progress**, and length/duration is *never itself* the trigger. A run
that closes a verified delta each cycle is healthy at any duration (the invariant
must not break Fable/ultracode-style long autonomous runs); a process that loops
without banking a delta is the failure, however briefly it has run.

1. **Home.** One full statement as a bullet in `## Universal Invariants` of
   `templates/AGENTS.template.md`; mirrored to this repo's `AGENTS.md` only by the
   normal self-application; pointers, not copies, anywhere else.
2. **"Verifiable progress" defined by evidence class, not metric.** A cycle banks
   progress when it produces a new observable delta — a test moving red→green, a
   finding closed with guard proof, a build/type error resolved, a committed slice.
   A cycle producing none of these is a stall. (Same evidence family as the
   vacuous-test and drift rules: "cycle with no observable delta" at the loop level.)
3. **Trigger by consecutive stalled cycles, threshold by agent judgment with a small
   stated default (~2-3), not a hardcoded N.** Hardcoding a count invites the same
   false-positive brittleness the synchronous-review work spent effort avoiding; the
   agent states the threshold it is using.
4. **Mechanical consequence.** Adding a Universal Invariant is a structural template
   change, so bump `<!-- templateVersion -->` in `templates/AGENTS.template.md` so the
   update route reconciles stale target `AGENTS.md` files (the 2026-06-22 stamp
   machinery working as designed).
5. **Scope guard is part of the wording.** The invariant explicitly states that
   length/duration is never the trigger and names the long-autonomous-run case, so no
   future agent reads it as a turn cap.

Reason: serves the repo's overarching mission — improve agentic coding for humans,
token-efficiently — by killing non-converging runs early (the largest avoidable token
sink) without capping productive long ones. It extends the repo's evidence-over-
assertion vocabulary (drift = "diverged from truth"; vacuous-test = "change with no
observable delta") to a new axis: runaway = "process that will not terminate
productively."

Relationship: complements, does not supersede, the 2026-06-24 section-level
deduplication decision (one full statement, pointers elsewhere) and the 2026-06-22
`templateVersion` reconciliation decision. Considered and rejected: a duration/turn
cap (e.g. "stop after N turns") — it strangles the long converging runs that are an
existence proof the duration is not the failure mode.

Next step: a `plan` for the exact invariant sentence(s), the `templateVersion` bump,
and verification (`python3 -m unittest discover -s tests -v` for the template/stamp
touch; the revert-the-fix discipline if a test guards the stamp).

> Archived 2026-07-08 (sweep): Adopted; the invariant lives in templates/AGENTS.template.md.

### 2026-06-25 - AGENTS.md governance boundary: portable + write-authority, enforced in three layers

Status: Adopted 2026-06-25.

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): L2 (the advisory tripwire) is retired on ledger evidence (silently inert on stock Windows, nothing degraded); L1 (the invariants) stands; L3 is now refresh.py's byte-verify-and-repair. The two boundary invariants landed as bullets in
`templates/AGENTS.template.md` `## Universal Invariants` (portability — "would this
line survive being copied unchanged into an unrelated repo?"; and write-authority —
"AGENTS.md is written only by a gated bootstrap or update run"); the `drift` operator
in the same template now names AGENTS.md portability/write-authority as explicit drift
targets; and a `PreToolUse` pre-edit tripwire (advisory, non-blocking, one stdlib-
Python script `agents-md-tripwire.py` shared by the Claude Code and Codex hook
configs) ships under `templates/hooks/`. `templateVersion` bumped 2026-06-25 →
2026-06-25.2 (a same-day second structural change; the bare date could not
distinguish it, and the section-probe backstop does not see new bullets within an
existing section, so the sub-version is the only reconciliation signal). This repo's
own `AGENTS.md` is intentionally NOT edited here — a frozen instance brought current
only by a deliberate self-application run (same handling as the stall-not-length and
2026-06-24 deduplication decisions). Design spec:
`docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan and
evidence: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`. The text
below is retained as the rationale until archived.

Decision: `AGENTS.md` is governance only and must be portable — every line must
survive being copied unchanged into an unrelated repo; repo-specific facts (paths, the
repo's own name, current state, verification commands) live in `.agents/`, and
`AGENTS.md` points to them rather than restating them. Complementarily, `AGENTS.md` is
written only by the two gated writers (a greenfield/migration bootstrap draft, or the
update-route reconciliation), never hand-edited mid-task. The two rules close both
wrong-content and wrong-moment. Enforcement is three layers by harness capability:
(1) the invariant text, injected on every harness; (2) the advisory pre-edit tripwire
hook, Claude Code + Codex only (Grok/agy have no pre-edit interception); (3) the
`drift` operator audit, cross-harness.

Layer emphasis (corrected from the spec's original framing by live validation,
2026-06-25): **layer 1 is the primary, proven steerer** — across three escalating
baits, capable models (Sonnet, GLM) read the invariant and routed the repo-specific
fact to `.agents/` before ever reaching for `AGENTS.md`, so the hook never had to
fire. **Layer 3 is the necessary backstop** — the only layer that catches what 1 and
2 let through; a model can read the layer-2 reminder and rationalize past it, and one
did. **Layer 2 is a real but advisory nudge** — validated to fire, be model-visible
(token echoed back), and stay non-blocking on Codex and on a non-Anthropic open model
(GLM) via Claude Code, and observed to make a model self-revert a leak once; it raises
the odds of self-correction but is never a gate. Validation was run in a throwaway
repo (now discarded); the shipped script+`additionalContext` form is the exact form
validated. Hook shape: Codex has no scriptless path matcher (matcher is tool-name
only), so a script is required there; one stdlib-Python script (Python 3 is already
the toolkit's baseline — no new dependency) serves both harnesses.

A secondary correctness finding landed with this work: the hook-template portability
test (`TestHookTemplates`) had encoded the *re-ground hook's* shape ("inline echo
only; no `.sh`; no `git rev-parse`") as if it were the portability rule itself — an
is/ought conflation that would force a per-category exception for every new hook kind.
It was reworked to assert the portability *principle* (no machine-specific/`/Users/`
baked path; `git rev-parse --show-toplevel` and `$CLAUDE_PROJECT_DIR` are portable and
allowed) over every hook command, with the re-ground command still byte-locked across
harnesses, plus dedicated tripwire guards (present+advisory+portable; fires-on-
AGENTS.md-only/never-blocks; script-identical-across-harnesses). All new guards were
proven to bite via hermetic mutation (temp copy, tracked files untouched).

Scope guard: this spec defines the *rule* and *forward* enforcement. Two pieces are
split to their own future specs and are NOT done here — retroactive cleanup of
already-bootstrapped repos whose `AGENTS.md` already carries repo-specifics, and
whether the mechanizable path/name scan folds into the queued `governance-lint`
playbook (Open Decision, 2026-06-22) versus staying an agent-judgment `drift` step.

Relationship: complements the one-canonical-location / prefer-pointers and
anti-enumeration invariants (this names the `AGENTS.md`↔`.agents/` boundary as a
single portable test); complements, does not supersede, the 2026-06-22
`templateVersion` reconciliation decision (whose stamp machinery this exercises, and
which the sub-version extends for the same-day case). Considered and rejected: a hard
*block* on AGENTS.md edits — the edit can be legitimate (a bootstrap/update run), and
portability is a content judgment only the model makes, so the hook is advisory by
design.

> Archived 2026-07-08 (sweep): Adopted as amended — L1 invariants live in the template, L3 is refresh.py repair, L2 (tripwire) retired.

### Open: hook-merge strategy is underspecified in the procedure

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): mooted — hooks are no longer agent-merged; refresh.py installs the single shipped settings file replace-if-unmodified and flags anything owner-modified. Recommend closing at next sweep.

Evidence: `procedures/bootstrap.md` "Hook install & trust" says to merge the
re-ground hook into an existing config "rather than replacing the file" and to
"stop and ask" if a safe merge is not possible, but specifies no merge algorithm
— for `.claude/settings.json`, which also holds permissions, env, and model
settings, "safe merge" carries undocumented weight.

Options: (a) add a concrete merge rule to the procedure — the hook lives under a
known key, preserve all sibling keys, append to the relevant hook array, and
stop-and-ask only on structural ambiguity; (b) leave the judgment to the agent.

Recommendation: (a). Docs-only change to one procedure section; no plan required
under the invariants. Reduces an ambiguous agent judgment to a stated rule.

> Archived 2026-07-08 (sweep): mooted — hooks are no longer agent-merged; refresh.py installs replace-if-unmodified and flags owner-modified files.

### Open: committed operator wrappers are skipped without a staleness check

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): resolved — replace-if-unmodified updates a wrapper that byte-matches any formerly-shipped version and flags owner-modified ones. Recommend closing at next sweep.

Evidence: `procedures/bootstrap.md` step 4 of "Operator command wrappers" does a
binary exist-and-committed → change-nothing, with no version/staleness check —
even though the 2026-06-22 update-route decision added `templateVersion` stamping
and reconciliation for `AGENTS.md`. The same staleness logic was not extended to
the command wrappers, so a repo can carry current `AGENTS.md` guidance behind
outdated wrappers and the migration route's reconciliation branch will not
notice. (Reworded 2026-07-01 to the single route per the adopted 2026-06-28
collapse; substance unchanged.)

Options: (a) extend version-aware reconciliation to wrappers in the migration
route's reconciliation branch — detect a wrapper that predates the current
template and propose an update through the normal approval summary, never a
silent overwrite; (b) leave wrappers as exist→skip.

Recommendation: (a), scoped narrowly to wrapper reconciliation in that branch,
following the existing `AGENTS.md` reconciliation precedent. Consistency fix for
work already shipped, not new surface.

> Archived 2026-07-08 (sweep): resolved — replace-if-unmodified updates provably-unmodified stale wrappers and flags modified ones.

### Open: a fast-update route/command for docs-only refreshes without a full update or migration

> Amended 2026-07-08 (zero-based consolidation — see the 2026-07-08 entry): resolved — `tools/refresh.py` is exactly this: the mechanical refresh path, seconds, no agent ceremony. Recommend closing at next sweep.

Evidence: discovery currently computes two routes — `greenfield` and
`migration` (the former `update` route was collapsed into `migration`,
Adopted 2026-07-01; `compute_route()` returns `"migration" if
governance_markers else "greenfield"`, `tools/discover.py:253-259`). Every
already-governed repo therefore takes the one heavy path: full discovery, an
inventory/reconciliation pass, the fresh-eyes check, and the approval summary
(`procedures/bootstrap.md` Step 3; `procedures/migration.md`). There is no
lightweight path for the common case of "just refresh the docs" — updating
`README.md`, `docs/*`, or other non-governance prose — without paying for the
whole reconciliation ceremony. Owner (2026-07-06): "we need a fast-update
option to update docs without doing a full update or migration." Naming is
open ("route? command? option? no fucking clue what you want to call it").

Open questions for the design (not yet decided):
- **Shape** — a third `compute_route()` route, a standalone operator/command
  wrapper (like `update-governance`), or a documented fast-path *mode* within
  the existing route. Note the standing repo lean that route *detection* is not
  load-bearing (2026-06-28 collapse, Adopted 2026-07-01), which argues against a
  new detected route and toward a command/mode.
- **Scope boundary** — what "docs" means precisely, and how the fast path
  refuses (or escalates) when a requested change touches governance
  (`AGENTS.md`, `.agents/*`, templates, `discover.py`) rather than plain docs.
  The docs-only verification carve-out already exists as a concept
  (`git diff --check` vs. the full test suite) and could anchor the boundary.
- **Gate** — whether a docs-only fast path still routes through the approval
  summary or uses a lighter confirmation, given the smaller blast radius.

Recommendation: none yet — recorded for a future decision, then a `plan`. The
most likely fit given the no-load-bearing-detection stance is a command/mode
rather than a fourth detected route, but that is a design call for the owner.

> Archived 2026-07-08 (sweep): resolved — tools/refresh.py is the mechanical fast path.

### 2026-07-10 — Plan linter for leakage and bloat

Status: Adopted 2026-07-10 — landed `279d25d`; canonical home
`tests/test_plan_lint.py` + the repo-guidance Verification line.

Decision: this repo's test suite gains a lint over still-open plan
documents in `docs/superpowers/plans/` that fails on conversational
leakage phrases, on backtick references to repo paths that git history
shows were deleted, and on extreme length. Closed plans and all plans
dated before 2026-07-10 (the plan-contract date) are exempt history. The
selected design is a test-suite check, NOT an extension of the refresh
lint: the same-day rule making refresh owner-only in this repo means
agents never trigger refresh here, while the suite is the touchpoint
agents hit before every change. This supersedes the standing
recommendation previously recorded in this entry (extend
`lint_governance()` in `tools/refresh.py`). The verification rule in
`.agents/repo-guidance.md` gains a matching line so changes under the
plans directory run the plan lint, closing the gap where a docs-only plan
edit verified by `git diff --check` alone would never meet the linter.

Owner-approved wording (2026-07-10), verbatim: "Add a check to this
repo's test suite that reads still-open plan documents and fails when one
contains chat leakage (phrases like 'this session', references to files
that don't exist) or is extremely long. Agents run these tests before
every change, so a leaky plan gets caught before it lands. Occasional
false alarms possible." Owner reply, verbatim: "plan that, review with
codex. this is a major pain point for me. do it right."

Provenance of the pain point: a fleet scan (2026-07-10, four read-only
agents over 37 directories under the owner's dev root) found "this
session" in at least 15 real plan documents across six repos, several
already marked Implemented. The core standard — implementable by a cold,
less-capable agent — cannot be linted and stays a review judgment.

> Archived 2026-07-10: Adopted — landed `279d25d`; six-round external
> review (codex, REVISE ×5 → APPROVE) recorded in the plan, CLOSED:
> `docs/superpowers/plans/2026-07-10-plan-lint-suite.md`.

### 2026-07-09 — `handoff` is a fast save-my-place snapshot; the doc-cleanup pass moves to `drift`

Status: Adopted 2026-07-10 — landed `741f846`; the rules live in the
`handoff`/`drift` operator bullets of `templates/AGENTS.template.md`, with
machine-specific facts in the tracked `.agents/machines.md` (per-machine
headings, dated; owner design 2026-07-10, recorded verbatim in
`docs/superpowers/plans/2026-07-10-handoff-snapshot-and-machine-local-state.md`,
which also resolves GitHub issue #2).

Decision: the `handoff` operator is redefined as a **fast session snapshot**,
bounded to seconds — the thing the owner runs to stop a session and resume it
later. The slow documentation-hygiene work currently bundled into `handoff`
moves to the existing **`drift`** operator; no new operator vocabulary is
added. Owner direction (2026-07-09): "handoff as a trigger for doc cleanup is
wrong. handoff is what I run when I want to stop a session so I can pick it up
later, not something that can run for more than 30 seconds." Owner chose to
fold the cleanup into `drift` rather than mint a new operator.

The split, concretely:

- **`handoff` (fast)** keeps only: write `## Now` / `## Next` so the next
  session resumes without chat context, note the in-flight work and next
  action, stop. No archive rotation, no re-verification sweep, no re-anchoring
  of volatile facts as a mandatory step. Seconds, not minutes.
- **`drift` (deliberate)** absorbs the hygiene rules currently in the
  `handoff` bullet: rotate landed/superseded `## Now` entries verbatim to
  `docs/history/state-archive.md`; re-verify the recorded basis of every
  parked/blocked item and move falsified ones to `## Blockers` with new
  evidence; re-anchor or drop volatile facts (`as of <commit>`); reduce copied
  counts/enumerations to pointers; label or omit machine-local facts. These
  are all species of "reconcile a doc against repo evidence," which is already
  `drift`'s charter.

Current wording being changed (quoted so the plan edits the right text):

- `templates/AGENTS.template.md` `handoff` bullet — the full "Prune as you
  write: rotate landed or superseded entries verbatim … move anything
  falsified into `## Blockers` with the new evidence" clause is what moves out.
- `templates/AGENTS.template.md` `drift` bullet — gains the rotation /
  re-verification / re-anchoring responsibilities (as the deliberate cleanup
  pass), keeping its existing doc-vs-evidence reconciliation charter.

Implementation surface for the plan (product files; this repo's own
`AGENTS.md` is refreshed from the template, not hand-edited):

- `templates/AGENTS.template.md` (both operator bullets).
- `templates/skills/shared/handoff/SKILL.md` and
  `templates/skills/shared/drift/SKILL.md` (pointer skills; the
  `description` frontmatter and body reference the operator's scope and must
  track the new split).
- `templates/commands/claude/handoff.md` (wrapper prose).
- `templates/approval-summary.template.md` (mentions `handoff`; check whether
  the reference assumes the old cleanup scope).
- Any `handoff`/`drift` reference in `procedures/*.md`.

Reason: the two jobs were conflated. "Save my place" must be zero-latency and
is run frequently; "tidy the durable docs" is slow, occasional, and
deliberate. Bundling the second into the first defeats the purpose of the
first — the owner cannot fire `handoff` and walk away if it triggers an
archive-rotation-and-re-verification pass. This session's own `handoff` run
(2026-07-09, commit `56f7cff`) demonstrated the cost: it read the archive,
grepped `decisions.md`, and verified commits before it could write — minutes,
not the seconds the operator is supposed to take.

Relationship: the hygiene rules being relocated are the field-earned handoff
rules added by the 2026-07-08 zero-based consolidation (template redline);
this decision does not delete them, it re-homes them under `drift`. The
one-canonical-location and smallest-guidance-set invariants are preserved (the
rules keep exactly one home, now `drift`). No conflict with the 2026-06-28
harness-neutral / pure-adapter decision: the skills remain pointers to the
`AGENTS.md` operator definitions.

Alternatives considered and rejected (owner, 2026-07-09): (a) a new dedicated
`tidy`/`prune` operator — rejected in favor of fewer operators to learn;
(c) drop the mandated cleanup entirely — rejected (leaves `## Now` to
accumulate stale entries with nothing obligated to prune them). The
machine-local wording in the drift bullet was superseded before landing by
the 2026-07-10 owner design (tracked `.agents/machines.md`).

> Archived 2026-07-10: Adopted — landed `741f846` per
> `docs/superpowers/plans/2026-07-10-handoff-snapshot-and-machine-local-state.md`
> (CLOSED). Decision text verbatim; only the Status line reflects adoption.

The following Open-queue entry and its introducing paragraph are moved here
verbatim from `.agents/decisions.md`:

The following was recorded 2026-07-06 on the owner's explicit instruction
("just add these as open items") as one of two owner-surfaced product gaps; the
other (the fast-update docs-refresh path) was adopted 2026-07-08 as
`tools/refresh.py` via the zero-based consolidation and is archived verbatim in
`docs/history/decisions-archive.md`.

### Open: the `reviewloop` playbook hard-requires git branches; it should not

Evidence: `templates/playbooks/reviewloop.md` makes a per-finding git branch a
load-bearing requirement of the loop, not a repo-configurable choice. The atomic
unit is stated as "**one finding ↔ one branch ↔ one verdict**" (`:38`); the
per-finding flow opens with "Finish the fix on a per-finding branch
`fix/<id>-<slug>`" (`:124`); the reviewer dispatch pins "the reviewed branch
**head SHA**" and merge-base (`:127-130`); accepted/reopened/invalid actions are
all phrased in branch terms (`:156-163`); and both the finding-doc template
(`**Branch**:`, `:211`) and the status index (a `Branch` column, `:270-273`)
bake a branch in. This collides with this repo's own 2026-06-10
"One-item-per-commit discipline" decision, which settled that "**Whether work
happens on a branch is repo policy, not this rule**" — the playbook removes the
per-repo discretion that decision reserves. Owner (2026-07-06): the playbook
"demands git branches. it should not."

Options: (a) re-express the atomic unit as "one finding ↔ one reviewable
change ↔ one verdict" and make the branch one *permitted* isolation mechanism
among others (branch, worktree, or a single commit on the working branch),
deferring the choice to repo policy the way the commit-discipline decision does;
the pinned base/head SHA contract (which needs only two commits, not a branch)
and the reviewer's own disposable worktree stay unchanged. (b) keep branches as
the documented default but add an explicit "no-branch" knob. (c) leave as-is.

Recommendation: (a) — it aligns the playbook with the repo's existing
branch-is-repo-policy decision and keeps the actual review discipline (pinned
SHAs, guard proof, recorded fail-closed verdict) intact, since none of it
depends on a branch existing. Playbook-template change only; no `discover.py`
surface. A `plan` should confirm the SHA-pinning and worktree language survives
the rewording before implementation.

> Archived 2026-07-12: Adopted 2026-07-10 — resolved by the review-loop-shipping
> plan (`docs/superpowers/plans/2026-07-10-review-loop-shipping.md`, CLOSED,
> owner-approved), slice 2 landed in `7295d19`: `templates/playbooks/reviewloop.md`
> now scopes per-finding branches as the loop's internal mechanics (its atomic
> unit and guard-proof isolation), explicitly not repository branch policy —
> whether the repo uses branches for other work stays repo policy, preserving
> the discretion the 2026-06-10 one-item-per-commit decision reserves. Note the
> landed resolution differs from this entry's recommendation (a): the collision
> was resolved by scoping the branch to the loop's internals, not by making it
> one permitted mechanism among others. Entry text verbatim; the line-number
> citations describe the playbook as it stood 2026-07-06.

The following Open-queue entry is moved here verbatim from
`.agents/decisions.md` (from the 2026-06-22 external-review batch):

### Open: greenfield fresh-eyes test is agent-judged "optional", at a point the repo distrusts agent judgment

Evidence: `procedures/bootstrap.md` greenfield step 8 makes the fresh-eyes test
"optional ... recommended whenever the drafts are substantial"; migration
(`procedures/migration.md` Step 6) requires it. The greenfield wording leans on
the agent to judge "substantial," whereas the 2026-06-10 fresh-eyes decision and
the repo's broader stance distrust agent self-assessment.

Options: (a) make the greenfield fresh-eyes test mandatory unless the run is a
genuine no-op (no drafted changes); (b) keep "optional/recommended"; (c) some
middle threshold tied to an objective signal (e.g. any new `.agents/` file
drafted).

Recommendation: a one-line judgment call for the owner. (a) removes the
agent-judged escape hatch cheaply; (c) is a compromise. Low effort either way.

> Archived 2026-07-12: Declined — owner ruling 2026-07-12, verbatim: "no,
> waste of tokens." The greenfield fresh-eyes wording stays
> "optional ... recommended" (option (b)); the process is unchanged. Entry
> text verbatim; its `procedures/migration.md` citation describes the
> pre-consolidation procedure set.

The following Open-queue entry and its introducing batch paragraph are moved
here verbatim from `.agents/decisions.md`:

The following were assessed on 2026-06-23 from bug reports filed to the
`agent-harvest` dropbox during a `headroom` (chopratejas/headroom) dogfood
migration run, read against current repo evidence. They are appended at the end of
the queue; the implementation sequence of the items above is unchanged. (The
batch's authority/scope-boundary precedence finding was broadened into the
general specific-over-generic precedence rule and adopted 2026-07-04 — see that
decision; the original entry is archived verbatim.)

### Open: "all routes" harness-artifact drafting contradicts the smallest-guidance-set invariant

Evidence: `procedures/bootstrap.md` "Operator command wrappers (all routes)"
(`:156`, `:159`) and "Hook install & trust (all routes)" (`:192-193`) instruct
drafting wrappers/hooks for every harness the toolkit ships a template for, "even
when the harness you are running in has no command-file mechanism," while
`templates/AGENTS.template.md:61` states "Prefer the smallest durable guidance set
that fits the repo. Over-documentation is a drift risk." No section reconciles the
two, so an agent following the draft-all instruction literally produces governance
files for harnesses a repo shows no evidence of using. In practice the bite is
small for wrappers (the toolkit currently ships wrapper templates only for Claude
Code, `:158`) but real for hooks (it ships claude/codex/grok/agents configs,
`:200-201`). Severity low — unused files / mild over-documentation, no incorrect
behavior or data loss. Source:
`bugs/headroom-harness-artifact-overproduction-2026-06-23.md`. <!-- lint: allow (file in the external agent-harvest repo) -->

Options: (a) reconcile explicitly: keep the draft-all portability default but add a
sentence to both "all routes" sections pointing at the smallest-set invariant, and
have the approval-summary step sort harness artifacts the repo shows no usage
evidence for into a clearly-labeled "optional / not-evidenced" bucket the owner can
drop. (b) make non-evidenced harness artifacts opt-in (draft only for harnesses
with repo evidence; note the rest as available). (c) leave as-is and treat
draft-all as the intended portability stance.

Recommendation: (a). Docs-only reconciliation across `procedures/bootstrap.md`
(the two "all routes" sections), `procedures/migration.md` (Step 4), and
`templates/approval-summary.template.md` (the optional/not-evidenced bucket); it
preserves the portability rationale while removing the literal contradiction. Lower
priority than the medium-severity authority gap above. This intersects the
2026-06-18 "operator command wrappers are a standing guarantee on every route"
decision (which stays Active): the reconciliation must not weaken the wrapper
guarantee, only label non-evidenced artifacts as optional in the summary.

> Archived 2026-07-12: Closed by the Active decision "Draft-all harness
> artifacts stands; 'smallest guidance set' means no token bloat, not fewer
> support files" (2026-07-12, `.agents/decisions.md`) — owner ruled option
> (c), no contradiction: the invariant governs guidance token cost, not the
> presence of harness support files. Entry text verbatim.

The following Open-queue entry and its introducing batch paragraph (the last
of the 2026-06-22 batch) are moved here verbatim from `.agents/decisions.md`:

The following were assessed on 2026-06-22 from three external repo
reviews (DeepSeek, GPT-5.5, Grok) read against current repo evidence. The
reviews' other suggestions were rejected as scope-inflating or already covered
and are not recorded. Recommendation order below is the suggested implementation
sequence. (The batch's monorepo-subdir probe finding was closed 2026-07-03 as
not-applicable — see that decision above and the archive.)

### Open: foreign-model governance validation

Owner needs a way for a *different* model to validate that a repo's governance
works (the in-bootstrap fresh-eyes test only ever runs the same model that drafted
the guidance). Not yet designed or decided — surfaced 2026-06-22, undecided.

> Archived 2026-07-12: Declined — owner ruling 2026-07-12, verbatim: "no,
> won't always have multiple models available." No design work follows; the
> in-bootstrap fresh-eyes test (same model, consistency-not-truth) remains
> the only governance check. Entry text verbatim.

The following entry is moved here verbatim from `.agents/decisions.md`:

### 2026-07-10 — Per-repo tuning for verbosity and technical level

Status: Open

Finding: owner idea (2026-07-10), verbatim: "A tuning option for
verbosity/tech level per repo would probably be a good addition." The plan
contract fixed the owner-facing register globally (plain English, roughly
25-50 words per decision); a per-repo knob would calibrate agent output —
verbosity, technical register, jargon tolerance — to each repo's audience.

Options assessed: (a) an owner-communication section scaffolded by
`templates/repo-guidance.template.md` (fields like verbosity level,
technical register, jargon allowed), read at session start — repo-guidance
is per-repo by design and refresh never touches it, so no new file class;
(b) a parameter inside the AGENTS template — infeasible, the template is
installed verbatim and byte-verified, parameters would break replace-whole
matching; (c) decline.

Standing recommendation: (a). Needs a plan on owner go; not scheduled.

> Update 2026-07-12: owner go for option (a), verbatim: "agreed, go". Plan
> drafted: `docs/superpowers/plans/2026-07-12-owner-communication-tuning.md`
> (DRAFT — implementation blocked on one owner decision, recorded there:
> approval-gate question vs silent defaults). Entry stays Open until the
> plan lands, then flips to Adopted per slice 3.

> Archived 2026-07-12: Adopted 2026-07-12 — landed per
> `docs/superpowers/plans/2026-07-12-owner-communication-tuning.md` (CLOSED;
> owner design wording recorded verbatim in its Status line): a single
> owner-chosen `Profile:` line, five named profiles. The rule's canonical
> home is the Owner Communication section of
> `templates/repo-guidance.template.md`; the five-profile menu's home is
> `templates/approval-summary.template.md`; `procedures/bootstrap.md` asks
> at the approval gate. Entry text verbatim.

### 2026-07-16 — Installed governance is toolkit-owned everywhere; divergence is always drift; refresh converges to the shipped set

Status: Active (implementation plan:
`docs/superpowers/plans/2026-07-16-strict-converge-and-review-split.md`)

Decision: no legitimate "owner-modified" state exists for installed
governance artifacts in governed repos. The owner never edits installed
copies in place; every change is made in the toolkit and propagates by
refresh. Any installed artifact that matches no shipped version is
therefore drift — whoever wrote it — and `tools/refresh.py` restores it to
the shipped set (drift is reported with the introducing commits, then
corrected; retired artifacts are removed even when modified; uncommitted
divergence still hits the dirty-tree refusal, so nothing uncommitted is
ever machine-destroyed). The flag-and-keep ("owner-modified; left
untouched") semantics are superseded. Lag — an installed copy matching an
older shipped version — remains the expected steady state between
refreshes and simply updates. Prevention ships alongside correction: the
don't-edit invariant in `templates/AGENTS.template.md` generalizes from
`AGENTS.md` to every refresh-installed artifact, shipped markdown
artifacts carry a one-line provenance marker, and a blocking Claude Code
pre-edit hook covers the one harness with verified blocking hooks.

Owner wording (2026-07-16), verbatim: "we need to stop governance drift
before we can rely on governance to stop code / docs drift. P1." And: "I
will NEVER make an out-of-band edit to a gov. doc in a repo. I own the
toolkit. if I need to make a change, it will need to be global, justified,
and intentional. I will make the change here and push it to all repos when
I refresh them. I will not be a source of drift anymore than I will allow
an agen to be. I will also not accept 'eh, just leave it. it's harmless'
for out-of-compliance docs. NO, not harmless. fodder for bad agent
decisions. I'm routinely managing 5-10 concurrent agents. I will miss
things if the rules are lax."

Earned by a field incident (2026-07, Powershell-Token-Killer commit
4f99fd5): an agent edited the installed review playbook in place after an
owner remark; refresh's classification would have attributed that drift to
the owner and left it standing, and no shipped rule forbade the edit — the
don't-edit invariant covered only `AGENTS.md`, and the broader rule lived
only in this repo's own guidance, which never ships.

Supersedes: the flag-and-keep clause of the 2026-07-08 consolidation's
replace-if-unmodified/retired classes (the rest of that entry stands);
amends the 2026-07-03 playbooks decision's closing clause ("never-overwrite
protects owner-modified playbooks") — no protected modified state exists.

### 2026-07-16 — Review playbook split: codereview (conformance) and openreview (goal-first), owner-invoked by name

Status: Active (implementation plan:
`docs/superpowers/plans/2026-07-16-strict-converge-and-review-split.md`)

Decision: the single cross-harness review playbook splits into two, each
invoked by the owner by name; no auto-selection heuristic ships. codereview
keeps the existing per-finding conformance loop (verify a fix against its
finding record — priming on the record is intentional there). openreview is
a whole-change review dispatched with exactly one substantive question —
"Is the code as implemented the best way to achieve the goal?" — plus
mechanical coordinates only (repo, pinned base/head SHAs, worktree
isolation, verdict schema); no plan summary, checklist, or prior findings.
Findings an openreview pass returns enter the codereview intake/triage
machinery.

Owner wording (2026-07-16), verbatim: "the key is that Mythos level models
like you work better with less constraint, so the review loop goes from
'does the code match the plan' narrowly to 'does the code accomplish the
goal in the best way possible' more broadly. that won't always be the best
route to take, so we need codified flavors of review." And: "how about we
ditch the one rule and split it into two: codereview and openreview, and I
call them when I want them?"

Provenance: the goal-first framing was field-authored in
Powershell-Token-Killer (commit 4f99fd5) and is upstreamed by this
decision; its per-model hardcoding ("when the reviewer is Claude") is not
adopted — flavor is chosen by invocation name, never by model detection.
The reviewloop playbook, its wrapper, and its skill retire from the
shipped set.

> Archived 2026-07-16: both entries Adopted 2026-07-16 — landed per
> the CLOSED plan docs/superpowers/plans/2026-07-16-strict-converge-and-review-split.md.
> Canonical homes: the strict-converge behavior lives in tools/refresh.py and the
> tools/shipped-set.json manifest comment, the generalized dont-edit invariant in
> templates/AGENTS.template.md, the provenance markers and blocking hook in the
> shipped templates; the review flavors live in templates/playbooks/codereview.md
> and templates/playbooks/openreview.md. Entry text verbatim above.
