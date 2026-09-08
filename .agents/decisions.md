# Agent Decisions

Keep open rulings and constraints without another operative home here.
Archive settled rationale verbatim after its rule lands in guidance or
verified product behavior. Historical provenance:
[decisions archive](../docs/history/decisions-archive.md).

## Decisions

### 2026-09-08 — Completion includes integration and cleanup; governance is consolidated

Status: Active

The owner approved the holistic rewrite: shorten the AGENTS template
within its existing token budget; carry completion through merge and
branch deletion; resolve authority and approval contradictions; reduce
review-playbook repetition; make adapters canonical pointers; tighten
reviewer permissions and snapshot isolation; archive historical records.

Evidence: the request required no completion before merge and branch
deletion, then explicitly retained the template token ceiling. The
subsequent audit at `b966ac4` found codereview's checked row still awaiting
merge, conflicting authority wording, duplicated refresh instructions,
a wildcard Git grant labeled restricted, and stale installation-lag claims.
The owner's “go” authorized this scoped rewrite; it did not authorize a
release, self-refresh, or an unnamed history rewrite.

Canonical homes:
- `templates/AGENTS.template.md`: compact authority, completion and safety.
- `templates/playbooks/git.md`: integration-branch resolution, work-branch
  setup and closeout; initial creation establishes main. Read-only steps
  may finish while implementation remains pending.
- Review playbooks: preserved dispatch/triage/verdict contracts, pinned
  worktree inspection, restricted launch grants, and pending/complete states.
- Adapter procedures: each command/skill points to a shipped playbook;
  refresh and the operator menu now each have one home.
- State/decision templates and this repo's guidance: live records,
  canonical pointers, existing authorization and token discipline.

Supersedes the old completion-at-verification convention, the duplicate
authority/dispatch wording, and repeated approval of already-authorized
steps. Merge and deletion still require authority naming those actions.
Historical entries moved below the archive pointer remain verbatim;
unresolved constraints remain here.

Verification: Python 3.14, `-m unittest discover -s tests -v`: 226 tests
passed. Four discriminating structural
proofs fail against old/broken fixture sources and pass after restoration:
reviewer permissions, completion states, shared refresh routing, and
shipped adapter targets. Token measurement with the same tiktoken encodings:
`o200k_base` 914 → 770; `cl100k_base` 913 → 768. These are token counts,
not word-count estimates. Measured with tiktoken 0.14.0; across all template
and procedure Markdown, `o200k_base` falls 29,736 → 18,715 tokens.
Playbooks fall 15,230 → 7,134; command/skill adapters 4,093 → 1,735.
All 52 original decisions remain verbatim in the live file or archive;
47 were rotated. Installed governance targets were not modified.

### 2026-07-25 — A configurable setting nothing reads is retired, not repaired

Status: Active

Decision: the owner-communication level (1–5) is retired outright — the
policy file, its template, its bootstrap seeding, its approval-summary
question, its refresh preflight, and the register deferrals in
`templates/AGENTS.template.md` and the plan playbook. Owner wording
(2026-07-25), verbatim: "scrap the whole comms thing. this is example 'if
it's not being used, it's not worth keeping'".

Evidence: the level was set to 2 in this repo and governed no response.
`templates/AGENTS.template.md` carried a one-line pointer ("Register
follows the repo's communication level") to a file nothing loads, so the
definitions were never in context at the moment of writing. Demonstrated
2026-07-25: an entire session ran at roughly level 4 length under a level 2
setting, and the level entered consideration only when the owner raised it.

Generalized rule this establishes: a setting is only worth keeping when
something reads it at the moment it applies. Guidance one indirection away
from its point of use does not bind — put the rule in text already loaded,
or do not add the rule. When a configurable knob is found unread, the
default response is deletion, not a louder pointer.

Supersedes the 2026-07-22 tunable-level decision and the 2026-07-12
named-profile design before it; both are archived in
`docs/history/decisions-archive.md`. Two attempts at per-repo
communication tuning, neither ever load-bearing. Plan:
`docs/superpowers/plans/2026-07-25-retire-comms-policy.md`.

### 2026-07-12 — Draft-all harness artifacts stands; "smallest guidance set" means no token bloat, not fewer support files

Status: Active

Decision: bootstrap keeps drafting the operator wrappers, shims, and other
harness support files for every harness the toolkit ships templates for, in
every repo — no evidence-of-use gating, no "optional / not-evidenced"
labeling in the approval summary. The smallest-guidance-set invariant in
`templates/AGENTS.template.md` governs guidance content — do not add token
cost that every session pays — not the presence of harness support files.
Owner ruling (2026-07-12), verbatim: "no, all harnesses every time. minimal
means don't add token bloat anywhere. it doesn't mean drop important files
because you think I won't need them."

Closes: the 2026-06-23 Open finding on "all routes" harness-artifact
drafting vs the smallest-guidance-set invariant (archived verbatim in
`docs/history/decisions-archive.md`) — resolved as no contradiction: the
two rules govern different things. Consistent with the 2026-06-18
standing-guarantee decision and the 2026-07-03 playbooks decision
(unconditional, deterministic installation).

> Amended 2026-07-23: the mechanism is refresh, not bootstrap drafting —
> every refresh run converges the repo to the full shipped set,
> unconditionally (bootstrap drafts only the per-repo judgment files;
> `procedures/bootstrap.md:147-149`). The ruling's substance is
> unchanged. The token-bloat gloss stays toolkit-local deliberately:
> installed files are toolkit-owned, so a downstream agent cannot act on
> the misreading. Noted by the decisions-as-claims audit (F5).

### 2026-07-10 — Release posture: perfect privately first, release widely later

Status: Active

Decision: the toolkit is being vetted and perfected in the owner's own
workflows first; wide release is the eventual goal, not the current state.
Owner wording (2026-07-10), verbatim: "Once this is vetted and perfected in
my workflows we can release it widely." Consequence: release-engineering
work (versioned releases, changelogs, license, CI matrices, signed tags —
external-review finding M6) is DEFERRED until the wide-release decision,
not declined; nothing in the product assumes external users until then.
This refines the personal-toolkit framing behind the 2026-07-10
mirror-trust ruling (recorded in
`docs/superpowers/plans/2026-07-10-refresh-trust-boundary-hardening.md`).

> Amended 2026-07-30: the license item is lifted out of the deferred set —
> Bixi has been public since the 2026-07-24 first publish and is the
> public feedback inbox, so it can no longer wait for the wide-release
> decision. MIT license, ruled 2026-07-30 (entry below). The rest of the
> deferred set (versioned releases, changelogs, CI matrices, signed tags)
> stays deferred.

### 2026-07-08 — Zero-based consolidation: every product piece justifies its existence or leaves

Status: Active (implemented same day; plan with eight-round codex review
trail: `docs/superpowers/plans/2026-07-08-zero-based-consolidation.md`;
owner approval 2026-07-08).

The owner commissioned a zero-based review — every piece justifies itself on
the incident ledger and a five-repo field audit (Blit_v2, vela,
Powershell-Token-Killer, ai-rpg-engine, ExchangeAdminWeb; evidence anchors in
the plan) or is removed/replaced. The field audits established that the core
loop works (handoffs demonstrably resumed across sessions and machines,
decisions and pauses honored, reviewloop caught real pre-ship bugs) and that
the recurring failures cluster where no operator or write rule existed.

What changed, and what each change supersedes or amends:

- **Steady-state refresh is `tools/refresh.py`** — pull-based, per-repo, no
  registry: reconcile-to-shipped-set (`tools/shipped-set.json`) with
  newline-normalized matching, `replace-whole` for `AGENTS.md` gated on a
  known-template match, `replace-if-unmodified` for shims/wrappers/playbooks/
  hook settings (missing ⇒ install; matches a formerly-shipped version ⇒
  update; else flag, never overwrite), a `retired` list so toolkit-side
  removal actually propagates (empty formerly-hashes = always flag, never
  machine-delete — protects generated files), gitignore-aware committability
  with the blanket adapter-dir repair, dirty-tree refusal scoped to its own
  targets, `--stage-only` for the bootstrap single-commit contract, and the
  toolkit sha in the commit message as provenance. Rationale on record: sync-
  to-exact-set is the documented agent failure mode (the 2026-07-01 dogfood
  "content already current" miss; wrappers narrowed to fit stale files;
  deletions resurrecting). This supersedes the mechanical half of the
  agent-run refresh flow, the 2026-06-22 templateVersion-stamp decision (the
  stamp is removed; byte-compare + commit-message provenance replace it), and
  strengthens the 2026-06-18 never-overwrite rule (`replace-if-unmodified`:
  byte-match against formerly-shipped versions proves non-modification, so
  provably-unmodified stale artifacts now update instead of rotting). The
  2026-07-03 playbooks decision is **preserved in full** (unconditional
  install; target-repo deletion still reinstalls; opt-out = remove the
  template from the toolkit — which now actually propagates).
- **Discovery is a live checklist, not a script** — `tools/discover.py` and
  its manifest/schema/golden machinery deleted (three of the seven ledger
  bugs were its own defects; a frontier agent re-derives its outputs).
  Salvaged knowledge lives in `procedures/bootstrap.md`: the Windows
  Store-stub probe order, ignore-aware governance detection, the
  CI-executability rule. Supersedes the script half of the 2026-06-09/10
  kickoff decision; the single-session kickoff, Step 0 sync, and evidence
  rule stand. The `.bootstrap-tmp` handoff pack dies with its generator; the
  self-ignored `drafts/` custody convention survives in the procedure. <!-- lint: allow (procedure convention, not a repo path) -->
- **The JSON layer is retired** — `repo-map.json` / `artifact-manifest.json`
  templates deleted; both on the retired list (flag-only). Field evidence:
  frozen and wrong in every audited repo while the prose files stayed
  accurate; custody is proven live by git at the approval gate. The
  verification command's single canonical home is
  `.agents/repo-guidance.md` (Verification). Amends the 2026-06-09
  standard-layout decision (layout no longer includes the JSON files).
- **Hooks narrowed to the Claude compaction re-ground behind a per-harness
  verify-once gate** — the sole shipped hook; the AGENTS.md pre-edit
  tripwire is retired everywhere (advisory; per-edit process spawn; silently
  inert on stock Windows for weeks with no degradation — the strongest
  not-load-bearing evidence on record; the write boundary is now refresh's
  byte-verify-and-repair), as are the never-verified grok/agy configs and
  the codex config (session_start registered but never observed firing —
  2026-07-08 live check negative). Ledger + structural rationale (a
  compaction failure can only be mitigated from outside the context):
  `docs/harness-capabilities.md`, the durable per-harness capability record.
  Amends the 2026-06-21 per-harness re-ground decision (per-harness retained,
  now evidence-gated); supersedes L2 of the 2026-06-25 boundary decision (L1
  prose stays, L3 is refresh repair); moots the 2026-07-02 hook-interpreter
  decision (the survivor is a plain echo). Codex/gemini/grok adapters and
  non-Claude wrappers re-enter only on a recorded positive live check.
- **Feedback is GitHub issues on this repo** (public; hard no-PII/secrets
  redaction rule in the issue templates; agents file only on an explicit
  owner go; offline fallback = in-repo note). Supersedes the transport half
  of the 2026-06-09 harvest decision and the 2026-06-22 dropbox/bug-report
  decisions; the harvest discipline (incident-earned, max three,
  no-report-is-normal) is retained verbatim in
  `.github/ISSUE_TEMPLATE/`. `docs/history/harvest-processed-archive.md` archived; open/closed
  issues are the queue and ledger. The `agent-harvest` repo awaits owner
  archiving.
- **The evals workstream is scrapped** — `evals/` and the instrument deleted
  (owner: delete, not archive; git history preserves). Amends the 2026-07-01
  functional-cut decision's completeness-general-as-candidate clause (the
  profile is deleted; revival needs a fresh decision). Salvage:
  `docs/harness-capabilities.md`.
- **Template redline** — `templates/AGENTS.template.md` cut to 1,503 words
  (Bootstrap Handoff, Mission-as-section, stamp, pointer bullet, merged
  durable-writing bullets); write-authority one sentence; `handoff` gains
  the field-earned rules (verbatim rotation to
  `docs/history/state-archive.md`; volatile facts `as of <commit>`; counts
  pointed-to; machine-local facts labeled or omitted; parked items
  re-verified); Session Startup gains the read-only clone-freshness check
  (never blocks). Scope tiers deleted from the approval summary (conditioned
  nothing anywhere).
- **Standing rule: no shipped rule without provenance** — a template rule is
  added, kept, or changed only with a decisions entry citing its earning
  incident; every kept line was cross-checked this run (zero lines lacked
  provenance). With the discover-era presence tests retired, this process
  rule — not CI grep — is what guards template content.

Procedures consolidated to one `procedures/bootstrap.md` (1,913 words, from
5,198 over two files; `verification.md` unchanged; the three dropbox
transport procedures deleted). Rollout: vela first (owner pick), remaining
repos on owner go; refresh flags route back as issues.

> Amended 2026-07-23 (decisions-as-claims audit, F11): two mechanism
> sentences in this entry are stale — since the 2026-07-16 strict-converge
> ruling (archived at `docs/history/decisions-archive.md:2203`),
> "replace-if-unmodified … else flag, never overwrite" reads as `replace`:
> a divergent artifact is reported as drift with its introducing commits
> and restored, and retired-list files are removed with a drift report
> (git history preserving them). "Empty formerly-hashes = always flag,
> never machine-delete" is likewise superseded.


### 2026-06-09/10 - Pilot findings folded into canon (multiple)

Status: Active (summarized)

The following were adopted during/after the three external pilots and the self-incident; each is recorded as a specific decision above or in the AGENTS template invariants where generalized:
- Revert-the-fix test check added to AGENTS template Verification.
- Ancestry-vs-content git-safety bullet.
- One-item-per-commit discipline.
- Safety-vs-ritual authority split (safety rules always bind; workflow rituals do not preempt the owner's kickoff instruction).
- Load-bearing-path check before migrating a state/decisions file.
- Summary altitude (plain English, one-screen recommendation before the inventory table).
- Approval authorizes one scoped commit only.
- Push offered once after commit, naming remotes.
- Evidence rule (durable claims cite the proving query).
- Custody-from-git rule + gitignore-aware commit contract.
- Fresh-eyes reframed as consistency-not-truth + external-claims question.
- Windows Python probe order + Store-stub detection.
- Cwd-independent Step 0 (`git -C`, ls-remote).
- Manifest schema shipped beside discover.py. (Retired 2026-07-08: discover.py and its manifest/schema machinery were deleted in the zero-based consolidation; the schema survives only as `docs/history/artifact-manifest.md`. Noted 2026-07-23 by the decisions-as-claims audit, F2.)
- "Answer with words" hardened with explicit artifact-is-evidence-not-decision clause.

All other pilot observations that did not yield a new durable rule were left as history in `docs/history/pilot-findings_exchangeadminweb_2026-06-10.md` and the per-pilot review files.

Supersedes:
The pre-pilot procedures and templates.

## Open Decisions (deferred - not yet adopted)

These are assessed findings the owner chose to record for a future decision
rather than implement now. The process is unchanged until one is adopted. Each
states the verified evidence, the options, and the standing recommendation.

- None currently (queue emptied 2026-07-12; closed entries are archived
  verbatim in `docs/history/decisions-archive.md`).
