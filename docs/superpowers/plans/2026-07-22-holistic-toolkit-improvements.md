# Holistic Toolkit Improvement: Ten Verified Sites

Status: OPEN — drafted 2026-07-22 from the owner-commissioned multi-agent
review. The owner approved the ten-site assessment and ordered it saved
(owner words, 2026-07-22: "good. save plans for all of these."). That
approval covers this document, not implementation: per owner ruling R1
below, each site's decisions go to the owner one at a time in plain
English, and a site becomes implementable only after its own explicit go
is recorded here (per-site status lines below) or in `.agents/decisions.md`.

Owner rulings, second pass (2026-07-22, verbatim: "1-5 yes, 6 no, 7 yes,
8 what?, 9-10 yes. gemini shim can go."): Sites 1–5, 7, 9, 10 are
APPROVED for implementation; Site 3 lands the recommended
probe-plus-terminal-stop branch; Site 4's sign-off on relabeling owner
attestations is given. Site 6 as drafted is REJECTED and replaced by the
owner's tunable communication-level spec (recorded under Site 6). Site 8
is PENDING — the owner asked for a plainer explanation before ruling.
GEMINI shim: retire (Site 10). ExchangeAdminWeb ran-or-redate: still
awaiting the owner. Implementation of approved sites is dispatched to
Opus 4.8 agents, one site at a time, one finding per commit; each site
appends its implemented commit list under its heading.

## Provenance

Produced 2026-07-22 by a 60-agent review (eight parallel lenses over the
whole repo, dedupe, per-finding adversarial verification, completeness
critic with a follow-up round): 39 findings CONFIRMED with verbatim quotes
checked at HEAD `881e63b`, 6 downgraded WEAK, 0 refuted outright. Incident
receipts used throughout: GitHub issues #5–#8 (field reports from governed
repos), and the 2026-07-22 batch-implementation incident — ten unapproved
commits editing fleet templates were pushed and then owner-ordered
reverted; the remote was reset to `881e63b`, and the reverted work is
preserved only in the local tag `backup-2026-07-22-governance-edits`.

## Owner rulings (2026-07-22)

Issued by the owner during the 2026-07-22 incident review. Recorded here
so they survive; landing them in `.agents/decisions.md` and the template
is itself Site 1 / 5 / 6 work.

- R1. GitHub issues are ADDRESSED by asking the owner about each, one at a
  time, with decisive options; nothing is implemented without a clear
  explicit go. This generalizes: every site below follows the same rule.
- R2. While any queue holds work, never end a response without naming the
  next work item and a concrete proposed action; a bare "x is blocked on
  y" is unacceptable.
- R3. `.agents/state.md` and the governance files exist for agents and for
  humans doing forensics; agents keep them current as part of the work;
  that upkeep is never gated on a human.
- R4. Prefer removing or rewording lines that failed over adding new
  lines; additions need an incident receipt and should displace at least
  their own weight.
- R5. All owner-facing explanation is plain English, no devops jargon,
  decisions one at a time. The owner does not have a devops background.

## How to work this plan

- One site at a time; within a site, one finding per commit (Git Safety).
- Before touching a site, put its "Decision for the owner" to the owner as
  an Owner Gates ask; record the ruling (a dated line under the site
  heading, plus `.agents/decisions.md` where durable).
- Directions below are the adversarially-verified fix directions — treat
  them as the default proposal, not as pre-approval.
- `reopens:` flags name settled decisions a direction would amend; the ask
  to the owner must say so in plain English.
- Verification per `.agents/repo-guidance.md` (Verification); interpreter
  caveats per `.agents/machines.md`. Template edits change `templates/`
  only; installed copies converge at the owner's next self-refresh
  (owner-only, settled 2026-07-10).

---

## Site 1 — Authorization: close the holes that allowed the 2026-07-22 incident

Problem: the plan gate exempts "docs"; in this repo the product is
markdown, so every product change escapes planning. "Approved" guidance is
never defined as owner-approved. The issue queue has no recorded working
process.

- `templates/AGENTS.template.md:8` — quote: "No code change without an
  approved plan; docs and other non-code edits don't need one (e.g. a
  README)." Harm: ten unapproved fleet-template commits self-classified as
  docs; `.agents/repo-guidance.md` already runs the full suite for
  `templates/` changes, contradicting the file-type reading. Direction:
  reword in place to a ship-effect test — "docs and other edits that
  change nothing the repo ships don't need one (a README)" — keeping the
  when-unsure backstop. Subtractive, portable.
- `.agents/repo-guidance.md:13` — quote: "Feedback arrives as GitHub
  issues on this repo". Harm: the only issue-queue line says where
  feedback arrives, nothing about how it is worked; "fix them" was read as
  standing batch authority. Direction: extend the existing sentence —
  each issue is put to the owner one at a time as an Owner Gates ask and
  acted on only on an explicit per-item go — plus a `.agents/decisions.md`
  entry recording R1 with the incident as receipt.
- `templates/AGENTS.template.md:26` — quote: "approved plans and guidance
  are evidence for intent." Harm: nothing says approved by whom; a rule an
  agent authors into the repo immediately outranks everything but a live
  human request (the F3 self-licensing pattern; also issue #5's channel).
  Direction: qualify as owner-approved, and add that guidance authored
  during the current effort authorizes nothing in that effort — covering
  Source Of Truth item 2 (`.agents/repo-guidance.md`) as well.

Decision for the owner: adopt the ship-effect plan gate, the one-sentence
issue process, and the owner-approved qualifier — three small rewordings,
presented separately.

Implemented 2026-07-22: 380e81d reword plan gate to a ship-effect test;
d9c10d7 record the issue-queue working process (repo-guidance sentence +
R1 decisions entry); cc6fea2 qualify approved guidance as owner-approved
and non-self-licensing.

## Site 2 — Issue #5: plug the three shadow-rule channels

Problem: process rules can escape governance three ways — saved outside
the repo as "preferences", written into `.agents/repo-guidance.md` as
competing practices, or injected from harness memory that nothing audits.

- `templates/AGENTS.template.md:22` — quote: "reserve out-of-repo stores
  for genuinely cross-project facts (owner identity, preferences)." Harm:
  issue #5's incident filed redispatch-skipping rules as owner
  preferences; they auto-inject every session and survive refresh.
  Direction: delete ", preferences". Companion touch-up:
  `docs/harness-capabilities.md:63` rewords to "cross-repo owner identity
  facts" so its sentence stays grammatical. reopens: tightens the
  2026-06-15 exemplar wording, does not reverse it.
- `templates/AGENTS.template.md:17` — quote: "It extends this file and
  never overrides it — flag any genuine conflict." Harm: the
  never-overrides boundary names only AGENTS.md, so an "earned practice"
  in repo-guidance overrode installed playbook semantics (issue #5).
  Direction: reword so repo-guidance never overrides AGENTS.md or any
  refresh-installed artifact; sync the parallel parenthetical at line 43;
  phrase so owner-ruled invocation restrictions (like this repo's
  owner-only self-refresh) remain legitimate when-to-invoke policy.
- `templates/AGENTS.template.md:56` — quote: "The guidance files
  themselves — `AGENTS.md` and `.agents/*` — are in scope as drift
  targets". Harm: nothing ever audits harness-injected memory; the rogue
  rule persisted until a manual owner ruling. Direction: reword the scope
  clause to include any out-of-repo memory the harness injects into
  sessions (inert where none exists; cross-harness plain text).
- `templates/AGENTS.template.md:56` (drift outcome for installed copies) —
  harm: drift says fix the lower-authority source; on three of four
  harnesses nothing blocks an agent "fixing" the installed AGENTS.md
  itself, which the toolkit-owned invariant forbids and refresh silently
  undoes. Direction: reword drift's fix clause by ownership — installed
  copies are report-and-route, never edited; only repo-owned files are
  fixed in place.

Decision for the owner: approve the one-word deletion and the three
rewordings — presented separately; the first is the cheapest and highest
value.

## Site 3 — Issue #6: reviewer dispatch must prove capability and stop on denial

Problem: a reviewer transport is qualified by a trivial chat reply, not by
proof the actual reviewer can read the repo and run a command; and a
permission denial licenses unlimited workarounds. Field cost: 9,378,752
tokens, 291 requests, no verdict (issue #6, Vela).

- `templates/playbooks/codereview.md:117` — quote: "Run the candidate
  incantation with a trivial prompt (e.g. `<agent> exec "say OK"`) …
  Treat a launch refusal as a flag to adjust, not a dead end." Harm: the
  say-OK probe passed while the reviewer child could not run the guard;
  "not a dead end" licensed 291 requests of variants against one missing
  capability. Direction: probe must prove a repo read plus one allowlisted
  command through the same child path that carries the real review; a
  repeated permission/tool denial is terminal after one fresh-process
  retry — record it, report the transport unsupported, stop. Note for the
  ask: a PENDING owner proposal (2026-07-18, state archive) would collapse
  the probe machinery entirely; present both branches together since one
  may moot the other.
- `templates/playbooks/codereview.md` (fallback-grade halt) — harm: on a
  harness whose frontier tier is fallback-grade, a missing guard proof
  matches two contradictory rules (halt-to-owner vs return-to-coder under
  amended T3); two agents diverge mechanically. Direction: delete the
  "— T1–T5 alike —" appositive, which is stale against amended T3.

Decision for the owner: choose capability-probe-plus-terminal-stop, the
2026-07-18 collapse proposal, or both; then the one-line T3 fix.

## Site 4 — Evidence: stop recording say-so as verified fact

Problem: an escape clause lets a conversational owner statement upgrade an
unverified claim about external-system behavior into recorded fact; issue
#6's 9.4M-token spiral traces to exactly one such recording.

- `templates/AGENTS.template.md:23` — quote: "Label
  inferred-but-unverified facts as assumptions until repo evidence or
  explicit human approval supports them." Harm: under this wording,
  recording the owner's "yes it can" (MCP grant propagation) as confirmed
  fact was compliant; it was false on Claude Code 2.1.214. Direction:
  delete "or explicit human approval" — the neighboring "explicit human
  intent" clause still lets owner words settle decisions and preferences;
  they no longer settle external-system facts.
- `.agents/decisions.md:98` (2026-07-18 entry) — quote: "owner further
  confirmed MCP-as-server carries the grant in its registration args
  ("yes it can")". Direction: dated amendment downgrading that clause to a
  falsified assumption citing issue #6 and Claude Code 2.1.214; delete the
  matching equivalence claim from the codereview playbook's
  Self-permissioning section. reopens: amends the provenance clause only;
  the launch-scoped-grant ruling stands.
- `docs/harness-capabilities.md` (lines 40, 43, 57) — harm:
  "owner-attested" is outside the file's own observed/assumed/historical
  taxonomy — the same evidence class as "yes it can". Direction: reword
  those parentheticals to "assumed — owner-attested <date>, no probe";
  outcomes recorded from them stand.

Decision for the owner: approve deleting the escape clause; approve the
amendment relabeling your prior attestations as assumptions (this
corrects records built on your words — it needs your explicit sign-off).

## Site 5 — Issues #7/#8: ungate routine bookkeeping and completion reports

Problem: keeping the state record current requires an owner-invoked
operator, and an owner's "it's done" mid-workflow was treated as needing a
ritual "go". Both were ruled on 2026-07-22 (R3; and the owner filed issue
#8); neither ruling is recorded.

- `templates/AGENTS.template.md:52/55/56` — harm: the only state.md write
  paths named live inside owner-invoked operators (issue #7's exact
  failure: a falsified entry could only be fixed by asking). Direction:
  land the R3 decisions entry, then reword line 25 in place — state.md is
  kept current by the working agent as work lands, never owner-gated;
  handoff/drift keep their deliberate-pass roles.
- `templates/AGENTS.template.md:7` — quote: "act only on an explicit
  instruction or go." Harm: issue #8 — completion report treated as
  informational; ritual "go" demanded. The same day showed the opposite
  failure (continuation stretched into batch authority), so the fix must
  thread both. Direction: reword the sentence's report clause — an owner's
  completion report inside an approved, already-scoped workflow is the go
  for the next step that workflow already defines; new scope, changed
  risk, and separately gated actions still stop. Net length flat.
  reopens: qualifies the 2026-06-10 answer-with-words hardening for
  completion reports only.

Decision for the owner: approve the R3 recording plus reword, and the
issue-#8 reword — two asks.

## Site 6 — Owner communication: tunable per-repo communication level

REPLACED 2026-07-22 by owner ruling (verbatim): "this needs to be tunable
like the push policy. 1-5, 1 being eli5, 2 plain english one at a time,
3 normal user, 4-5 devops/jargon".

Replacement spec: communication style becomes a per-repo tunable exactly
like the push policy — a small repo-owned policy file (`.agents/`
alongside `push-policy.md`, seeded the same way the push policy is
seeded, with the same kind of machine-readable marker line) carrying a
level 1–5: 1 = explain like I'm five; 2 = plain English, one decision at
a time; 3 = normal user; 4–5 = devops shorthand and jargon acceptable.
Level definitions live in the policy file itself. Template/bootstrap
default: level 3 (normal user). This repo's file: level 2 (matches the
owner's standing instruction here). The Owner Gates structural contract
(context, the question, what changes under each option, recommendation)
is level-independent; the 25–50-word plain-English styling in the plan
operator becomes a pointer to the communication level. Level-independent
riders landing with this site because they are settled rulings about
content rather than style: the 2026-07-17 summary-first Final Response
amendment (decided, never landed) and R2 (never end on a bare blocker;
name the next item and proposed action).

Original drafted content (superseded, kept for the findings' evidence):

Problem: plain-English/one-decision-at-a-time binds only plan decisions;
the final-summary rule you approved 2026-07-17 was never actually landed.

- `templates/AGENTS.template.md:58 vs 63` — harm: the 2026-07-17 decision
  claims the chat-ask rule generalized to all owner gates, but Owner Gates
  never got it — non-plan asks could legally be jargon batches (they were,
  2026-07-22). Direction: move the full statement (keeping the 25–50-word
  spec) into Owner Gates; shrink the plan bullet to a pointer. Net
  smaller. reopens: relocates the canonical home recorded by the
  2026-07-10 plan-contract decision; amend it.
- `templates/AGENTS.template.md:83` — quote: "Explain what changed, what
  was validated, and any remaining risk in plain English." Harm: the
  2026-07-17 decision (item 2) ordered a summary-first Final Response
  including anything awaiting the owner; the commit claiming that
  amendment never touched this line. R2 also has no durable home, so a
  bare-blocker ending fully satisfies the current text. Direction: reword
  this one line to the approved 2026-07-17 shape plus R2's
  next-item-with-proposed-action requirement; record R2 in
  `.agents/decisions.md`.

Decision for the owner: two rewordings, both implementing rulings you
already made; confirm and they land.

## Site 7 — Dead weight: cut ~5 KB with zero semantic loss

Problem: the fleet pays per session for text that is duplicated or only
ever used on demand.

- `templates/AGENTS.template.md:56` — the drift bullet's 1,035-byte
  state-hygiene checklist (8.4% of the file) runs only when the owner says
  drift, but loads every session fleet-wide; the shipped drift skill and
  wrapper are pure pointers. Direction: relocate the checklist verbatim to
  a new `templates/playbooks/drift.md` (read at invoke time via the
  existing cross-harness playbook mechanism); the bullet keeps one
  sentence plus a pointer. Saves ~850 bytes per session per repo.
  reopens: the 2026-07-11 push-status decision names this line as its
  change site; wording relocates verbatim.
- `templates/playbooks/codereview.md:578–596` — the Calibration
  anti-patterns section (1,186 bytes) restates rules stated earlier in the
  same file (inflation, capitulation, severity, churn, convergence).
  Direction: delete the section.
- `templates/playbooks/codereview.md:54–83` — the Governance alignment
  section (2,085 bytes) re-teaches AGENTS.md invariants loaded every
  session (merge gating stated four times across the file). Direction:
  delete the restating bullets; fold the one playbook-specific clause
  (example commands are illustrative) into the first example site.
- `templates/playbooks/openreview.md:102–110` — ~650 bytes duplicate
  codereview's verdict-extraction prose that openreview elsewhere calls
  canonical. Direction: replace with a one-line pointer; keep openreview's
  own schema and fail-closed set.

Adjacent WEAK items (real but need care, not blanket deletion): the
"smallest guidance set" line (owner-ruled inoperative, but its content is
affirmed by a 2026-07-12 ruling — reword, don't delete), the Universal
Invariants opener, and the Source Of Truth closing sentence.

Decision for the owner: approve the relocation and the three deletions —
four independent cuts, ~5 KB total.

## Site 8 — Stale operator surface: three-quarters of users get wrong instructions

PENDING 2026-07-22 — owner ruling deferred ("8 what?"); a plainer
explanation goes to the owner before any of this site lands. Standing
recommendation for the force-phrase pick: reserve the word "frontier" so
the old spoken phrase keeps working and can never collide with a
nickname.

Problem: the 2026-07-19 model-map rework updated the Claude Code wrappers
but not the shared skills and playbook text every other harness reads.

- `templates/skills/shared/codereview/SKILL.md:3` — still teaches
  "codereview <agent>"; the wrapper and the shared review alias carry
  "codereview <harness> <nickname> <effort>" with map resolution. On
  codex/grok/agy the old grammar dispatches with unpinned models — the
  exact disease the map cures. Direction: carry the wrapper's current text;
  one canonical body per wrapper/skill pair, the other a pointer; fix the
  playbook's stale intro grammar (lines 18, 87–99). A lockstep pair test
  is proposable but reopens the 2026-07-08 prose-pin retirement — flag it.
- `templates/playbooks/codereview.md` (owner force phrase) — "codereview
  codex frontier" no longer parses under the new grammar (frontier lands
  in the nickname slot and blocks loud). Direction: owner picks the new
  force spelling (owner-spoken phrase — one plain-English decision), then
  the tier-effort text is reworded as defaults-when-effort-omitted.
- `templates/playbooks/harness-update.md` — claims map edits "reach
  governed repos on their next refresh"; the map is not in the shipped
  set — dispatch fetches it live from the raw master link. Direction:
  reword the clause to match the fetch contract.
- `README.md` — enumerates three playbooks; four ship. Direction: delete
  the enumeration, point at `tools/shipped-set.json` which the README
  already names as the manifest.

Decision for the owner: the force-phrase spelling is yours; the other
three are factual corrections — confirm and they land.

## Site 9 — Refresh hardening: four mechanical gaps

Problem: the update program trusts by construction things that have
already nearly failed.

- `tools/refresh.py` (validate_manifest) — a path listed in both
  artifacts and retired passes validation; installs write first, removes
  unlink after — the shipped file is deleted and the deletion committed
  fleet-wide. The 2026-07-19 un-retirement was a live near-miss of exactly
  this class. Direction: fold retired targets into the same duplicate-set
  so overlap exits 4 before any write.
- `tools/shipped-set.json` (formerly[] upkeep) — the outgoing-hash
  maintenance rule is applied by hand; one forgotten append misreports
  every fleet repo at that version as drifted, or worse for AGENTS.md.
  Direction: a test walks per-source git history and asserts
  membership-or-append; skip on shallow clones. reopens: none — this is
  structural, not prose-pin, but flag the adjacency when proposing.
- `tools/refresh.py` (apply_plan) — only RuntimeError is caught; an
  OSError mid-loop leaves some paths rewritten and unstaged, and the next
  run classifies them current and never commits them. Direction: catch
  OSError alike, or post-apply verify staged set covers touched paths;
  exempt the stage-only bootstrap flow.
- `tools/refresh.py` (foreign-core FLAG) — a repo that refused its
  AGENTS.md replacement still exits 0; scripts cannot distinguish
  converged from ungoverned. Direction: distinct nonzero exit (e.g. 5)
  when core flags are non-empty; document the exit table; fix the stale
  preflight comment.

Decision for the owner: these are code changes requiring plan-gated
approval — approve as one slice sequence or per-fix.

## Site 10 — Records and procedures agents ground on

Problem: the reading-order and startup surfaces contain falsified or
unreachable facts; two procedures contradict their own steps.

- `templates/AGENTS.template.md:38` — Session Startup points every
  governed repo at `docs/harness-capabilities.md`, which ships in no
  governed repo; also says one hook where two ship. Direction: reword to
  "governance hooks (Claude Code only)"; drop the dead pointer. Net
  shorter.
- `docs/design.md:97` — the Current state sentence is stale three ways
  (hook count, three-harness skills surface, falsified unverified-claim).
  Direction: delete the factual inventory; the harness-capabilities
  pointer already precedes it; keep the design-rationale parenthetical.
- `templates/shims/GEMINI.template.md` — ships fleet-wide with no
  recorded positive check on any gemini-family harness, against README's
  shipped-only-where-verified claim and the 2026-07-08 adapters ruling.
  Owner ruled 2026-07-22: retire ("gemini shim can go") — move it to the
  shipped set's retired list with its outgoing hashes per the maintenance
  rule; it re-enters only on a recorded positive live check.
- `.agents/decisions.md:660` (2026-06-28 entry, Active) — directs
  implementers at artifacts retired 2026-07-08 (the pre-edit tripwire and
  a retired repo-map file). Direction: dated amendment blockquote naming <!-- plan-lint: allow -->
  the surviving substrate (refresh byte-verify + the protect hook).
- `procedures/bootstrap.md:11` (header) vs Step 4 — header bans pre-gate
  target writes; Step 4 and verification.md require writes under
  `.bootstrap-tmp/`. Direction: reword the header clause to "nothing
  tracked in the target changes" and name the scratch dir as sanctioned.
- `procedures/bootstrap.md` Step 7 (dogfood run) — has the agent run
  refresh against the toolkit repo itself, colliding with the owner-only
  self-refresh rule. Direction: reword the scoping parenthetical so a
  dogfood run stops at the approval summary when resident governance
  reserves self-refresh to the owner.
- `procedures/verification.md` step 1 — brands the expected carve-out FLAG
  a defect, looping a cold rehearsal agent. Direction: rehearse carve-out
  commit 1 in the throwaway clone before the refresh step.
- `.agents/repo-guidance.md:41` — the recorded verification command fails
  on stock macOS (python3 is 3.9.6, floor is 3.10). Direction: subtractive
  reword pointing at bootstrap's probe order; machines.md keeps the
  machine facts.
- `.github/ISSUE_TEMPLATE/toolkit-defect.md:20` — Source field never
  captures the toolkit commit; one filed issue is already untriageable for
  it. Direction: reword the field to demand repo-and-toolkit commits; the
  toolkit sha is recoverable from any governed repo's last governance
  refresh commit.
- `.agents/state.md:45` — the ExchangeAdminWeb deferral date (2026-07-20)
  lapsed with no recorded resolution. Direction: one owner ask — ran or
  re-deferred; rotate or re-date accordingly. HELD: still awaiting the
  owner's answer as of 2026-07-22; implement nothing for this item until
  it lands.
- `.agents/state.md:33` — records the 2026-07-10 self-refresh as latest;
  five later refreshes supersede it. Direction: rotate the superseded
  lines to the state archive at the next drift/handoff; git owns refresh
  dates.

Decision for the owner: mostly factual corrections; the GEMINI shim
(retire vs verify) and the ExchangeAdminWeb date are genuine owner calls.

---

## Downgraded (WEAK) findings — recorded so they are not re-litigated

- "Smallest guidance set" line: owner called it inoperative, but a
  2026-07-12 ruling affirms its content — needs a reword ask, not
  deletion.
- Universal Invariants opener: near-content-free, but tied to the
  2026-06-21 re-ground design — check before cutting.
- Source Of Truth closing sentence: partially redundant with the
  flag-conflicts invariant; resolution procedure is not duplicated.
- "Specific over generic" (line 27): confirmed as issue #5's laundering
  path, but the proposed rewrite gutted a settled 2026-07-04 decision
  without flagging it — any fix must be re-derived with the reopens named.
- Provenance banner reads "toolkit-owned" at the template source path,
  literally false there — no incident; below threshold.
- catchup's "Make no changes" gates state upkeep during catchup — tension
  with R3 but the gate lasts one round-trip; below threshold.
