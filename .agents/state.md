# Agent State

This file is the first place future agents should read for current repo state. Keep it
short and update it when important repo facts change.

## Now

- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
- Governance for this repo itself is in `AGENTS.md` (Prime Invariants, universal and repo-specific rules, operator vocabulary, and pointers) plus this `.agents/` layout (state and decisions).
- 2026-06-21: this repo's own governance was brought current with the product it ships (it had intentionally lagged since 2026-06-20). The self-application added a `CLAUDE.md` shim (`@AGENTS.md`), committed `.claude/commands/` wrappers for the full operator set (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`), and a committed `.claude/settings.json` re-ground hook (fires on context compaction, points back to AGENTS.md). `AGENTS.md` was rewritten to the product shape: a `## Prime Invariants` block, a `## Universal Invariants` section, `## Operator Requests`, a `## Session Startup` trust note, and an updated `## Bootstrap Handoff` that audits wrappers and re-ground hooks. (`.claude/settings.local.json` stays machine-local and untracked.)
- 2026-06-21: the load-bearing-invariant enforcement work landed and is recorded as Adopted — a lean Prime Invariants block plus per-harness re-ground hooks (`templates/hooks/<harness>/`) that fire on compaction, with tests and a design spec (`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`). This resolved the last item that had been deferred to this re-run.
- 2026-06-22: closed the update-route template-reconciliation gap. `AGENTS.md` files now carry a `<!-- templateVersion -->` stamp; discovery records an `agentsTemplate` manifest block (current/target version, `reconcileRecommended`, `missingSections`) and, on the update route, the toolkit reconciles a stale or unstamped `AGENTS.md` to the current template before running the wrapper/hook guarantees. Wrapper/hook guidance treats a missing target section as a staleness signal to reconcile, not a cue to narrow the artifact. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: trimmed the per-session guidance tax. A density audit showed prose compression saves only ~2.7% (the guidance is dense, not padded), so instead the `## Bootstrap Handoff` section was collapsed to a conditional pointer to the synced `.bootstrap-tmp/procedures/bootstrap.md` (~600 tokens/session off `AGENTS.md`; the procedure is now the single canonical home for the handoff/reconciliation/wrapper-guard logic), and the token-efficiency invariant now encourages `rtk` as a discretionary per-command proxy (not an auto-rewrite hook) plus compact-but-equivalent working. See the 2026-06-22 decision in `.agents/decisions.md`.
- 2026-06-22: the `agent-harvest` dropbox now also stores bug reports (defects in this product) under a `bugs/` folder. Agents auto-write a report from `templates/bug-report.template.md` and file it via the canonical recipe `procedures/file-bug-report.md` (gh-api preferred, clone fallback, in-repo last resort), publishing only on an explicit owner go; the harvest sweep triages `bugs/`. See the 2026-06-22 decision in `.agents/decisions.md`. The `agent-harvest` repo gained a `bugs/` folder and a README section to match.
- 2026-06-22: unified the two dropbox-write paths. The transport mechanics now live in one shared recipe, `procedures/file-to-dropbox.md`, used by both harvest reports (`migration.md` Step 8) and bug reports (`file-bug-report.md`). Harvest submissions gained the no-clone `gh api` transport and lost their former standing auto-push: every dropbox publish now asks for an explicit owner go. The `gh api` PUT/DELETE path was verified end-to-end against `roethlar/agent-harvest`.
- `.agents/decisions.md` owns the live decision queue (Active entries plus the `## Open Decisions` queue); closed entries are rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule. See that file for the current open/active set rather than echoing a count here.
- 2026-06-25: rewrote the `reviewloop` playbook template (`templates/playbooks/reviewloop.md`) from the async sentinel/watcher design to a synchronous `review <agent>` flow, and added the `.claude/commands/review.md` wrapper. The coder (current harness) dispatches a named reviewer harness (codex/agy/grok/subagent) headless and one-shot per finding, deriving the headless incantation live by probing (no human-maintained table), parses a structured fail-closed JSON verdict (`{verdict, guard_confirmed, reviewed_sha, base_sha, comments}`), records it into the finding doc, and acts under owner-gated merge. The reviewer's guard proof runs in its own git worktree against a pinned base SHA. Design and the cross-harness review that hardened it: `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`; plan: `docs/superpowers/plans/2026-06-25-synchronous-review-handoff.md`. `review` is a playbook operator, intentionally kept out of `OPERATOR_WORDS`.
- 2026-06-25: added the **stall-not-length** Universal Invariant to `templates/AGENTS.template.md` (iterative processes escalate on a cycle that banks no verifiable progress, never on duration; long converging runs are not capped), `templateVersion` bumped to 2026-06-25. Adopted — see the 2026-06-25 entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance).
- 2026-06-25: implemented the **AGENTS.md governance boundary** (portable + write-authority) in three layers. Two Universal Invariants in `templates/AGENTS.template.md` (portability copy-test; written-only-by-gated-bootstrap/update); the `drift` operator now names AGENTS.md portability/write-authority as drift targets; and an advisory, non-blocking `PreToolUse` pre-edit tripwire (one stdlib-Python `agents-md-tripwire.py` shared by the Claude Code + Codex hook configs) ships under `templates/hooks/`. `templateVersion` 2026-06-25 → 2026-06-25.2 (same-day second structural change). Layer 2 was validated live before building (fires/visible/non-blocking on Codex and on GLM via Claude Code; self-revert seen once); evidence reframed the spec to L1-primary / L3-backstop / L2-advisory. `TestHookTemplates` was reworked from shape-banning to a portability principle so script hooks pass without per-category exceptions. Adopted — see the 2026-06-25 boundary entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance). Spec: `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`.
- 2026-06-25: wrote the **AGENTS.md retroactive-cleanup follow-on spec** (`docs/superpowers/specs/2026-06-25-agents-cleanup-via-update-route-design.md`) — design only, awaiting owner review then a `plan`. Decision recorded in it: cleanup is the update-route reconciliation *extended*, not a parallel flow. Key design move (owner insight): detect leaks as **surplus over the portable template** — the structural inverse of `missingSections` (which flags what the target *lacks*; surplus flags what it *has beyond baseline*), so a leaky-but-current, structurally-complete `AGENTS.md` still triggers, and non-path leaks (prose, restated state, the repo's name) are caught where a regex would miss them. Discovery computes surplus structurally; the agent sorts each surplus item into allowed-repo-specific vs leak (surplus ≠ leak: the Current State pointer, Active Sources list are legitimate surplus). Relocation rule (owner-settled): move leaks into `.agents/` with **no per-fact pointer** — keep only the existing structural pointers; rare exception when a governance rule's meaning references a repo-specific detail.
- 2026-06-27: **push policy is now repo-specific, delegated to `.agents/push-policy.md`.** The Prime Invariant push clause in `templates/AGENTS.template.md` no longer carries a blanket push-needs-go rule; it reads "History-rewrite and destructive or outward-facing actions always need an explicit go. Push policy: see `.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the default (`ask`); `templates/approval-summary.template.md` gained a Push Policy section that presents four standardized options (1 always / 2 operators / 3 docs / 4 ask) and must ask the human at approval time (do not pre-fill from the decisions log); `procedures/bootstrap.md` Step 10 consults the policy file after committing. `templateVersion` bumped to `2026-06-27.1`. Adopted — see 2026-06-27 push-policy decision in `.agents/decisions.md`.
- 2026-06-27: **this repo's own governance brought current via a dogfood / self-application run** (the deferred frozen-instance reconciliations all landed in one scoped commit `b844c72`): `AGENTS.md` reconciled `2026-06-22` → `2026-06-27.1` (push clause now delegates to push-policy; stall-not-length invariant; both governance-boundary invariants; sharpened drift/playbook operators; Session Startup mentions the tripwire), `.agents/push-policy.md` created set to **`always`** (every commit here pushes immediately), and the advisory AGENTS.md pre-edit tripwire installed (`.claude/settings.json` PreToolUse block + `.claude/agents-md-tripwire.py`, byte-identical to the shipped template). Repo-specific leaks left in place — their relocation is the separate owner-gated cleanup spec.
- 2026-06-27: **dogfood / self-application named as a case of the update route** — `procedures/bootstrap.md` now states that running the toolkit against itself is an in-place update run and a missing `.bootstrap-tmp/` at kickoff is the normal start, never a stop. Docs handrail only, no `compute_route()` detection. Adopted — see 2026-06-27 dogfood decision in `.agents/decisions.md`. Earned by two fresh sessions stopping to ask "is there anything to do here" on the canonical kickoff line.
- 2026-06-27: **`drift` cleanup of `.agents/decisions.md`** — two adopted entries that were parked in `## Open Decisions` (push-needs-explicit-go, and `run_git` fails open / Adopted 2026-06-23) moved **verbatim** to `docs/history/decisions-archive.md` per the archive rule; the push-policy decision relocated from Open into `## Decisions` as Active (its stale "must be created by running the update route" line corrected — the dogfood run already created it, set to `always`). The Open queue is now exactly nine genuine `Open:` items, no adopted/active mixed in.
- 2026-06-27: all work this session pushed to GitHub (`origin/master` at `1c4fb50`); the gitea mirror follows downstream (observed lagging earlier in the session; catches up). Per the `always` push policy, commits here push immediately rather than awaiting a per-instance go. (This handoff's own commit lands on top and is pushed next; a state line cannot name its own not-yet-created hash.)

## Next

- 2026-06-29 **Ungoverned baseline probe DONE → Option A confirmed; 10-instance
  failure band in hand.** Ran the leak-free ungoverned arm (Claude Code, subscription
  auth, in-container as non-root `agent`, re-init anti-leak scrub) over a 20-instance
  complex+regression-rich sample. **Resolved 10/20 (50%)** — a usable headroom band
  (not the ~80% ceiling that killed the easy sample). **All 20 produced genuine
  non-empty source patches: 0 empty/infra failures, 0 non-`ok` statuses**, so the 10
  non-resolves are real agent failures, not measurement noise. Full result table +
  the 10 failure-band instance IDs (the candidate set for the governed factorial):
  `evals/swebench-pro/probe-2026-06-29-ungoverned-baseline.md`. Failures by repo:
  NodeBB ×3, openlibrary ×3, ansible ×2, qutebrowser ×1, element-web ×1. **NEXT:**
  before the factorial, apply the reviewers' must-fixes (pre-registered analysis +
  power/MDE; length-matched PLACEBO prose arm; F2P/P2P reported separately; re-measure
  the band with replicates so the confirmatory set isn't a single-n=20 regression-to-mean;
  ONE harness). Then the governed none/prose/prose-hooks factorial over the band.
  (Probe driver is still scratch; formalizing into `evals/` with arg-list hardening
  remains the deferred engineering step.)
  **Owner decisions (2026-06-29):** confirmatory harness = **Claude Code only** (codex
  a possible later add only if Claude motivates it and marginal cost is small;
  grok/agy testing-only); arms = **4-arm with placebo** (none / placebo-prose /
  real-prose / prose+hooks). **Pre-registration drafted** (the reviewers' gate):
  `evals/swebench-pro/PRE-REGISTRATION.md` — within-instance paired design, F2P/P2P
  reported separately, mixed-effects logistic with 3 pre-specified contrasts (prose−none,
  hooks−prose, prose−placebo), Holm multiplicity. **IMMEDIATE NEXT (modest compute,
  no further gate needed): the SIZING PILOT** — 4 arms × R=3 over ~8–12 band instances
  to estimate discordance + replicate variance, which sets R, the confirmatory N, and
  the replicated-rate selection band. Subset selection re-measures the band with
  replicates (regression-to-mean guard) before the confirmatory set is frozen.
  **RUNNING (this session, 2026-06-29):** sizing pilot launched detached — 8 instances
  (4 baseline-failed + 4 baseline-resolved, 5 repos) × 4 arms × 3 reps = 96 cells.
  Driver `arms4.py` validated by a 1-instance×4-arm smoke (all arms inject; governance
  EXCLUDED from capture — 0 leakage; prose_hooks tripwire fired 8×; scorer
  discriminates; scorer-drop infra-retry added). Results land at scratch
  `…/scratchpad/pilot8_out/scores.json` + `arms4_runmeta.json` (session-local — on
  completion COPY the per-arm rates + discordance into `evals/swebench-pro/` and commit,
  else lost to a fresh session). KEYSTONES (in PRE-REGISTRATION): governance loads only
  via CLAUDE.md (bare AGENTS.md inert; `@AGENTS.md` import works); hooks fire headless
  under bypassPermissions (no trust step) but re-ground needs compaction, so
  prose+hooks≈prose under one-shot.

- 2026-06-29 **Leak fix validated + baseline confirmed GENUINE (not leakage).** Anti-leak scrub =
  re-init the agent workspace's git (`rm -rf .git && git init && git add -A && commit -m base`) so
  the gold fix leaves zero trace (bulletproof; ref-deletion+gc left it in a cruft pack, `git fsck
  --unreachable` still surfaced it — re-init is the robust fix). Ansible re-test with history wiped:
  STILL resolves, tests still run → (a) re-init doesn't break the build, (b) ansible's solve was
  genuine independent work, not the suspected leak. ⇒ the ~80% ungoverned baseline is a REAL ceiling,
  confirming the need for harder instances. **Candidate pool for option A:** 92 instances that are
  complex (gold ≥3 files) AND regression-rich (PASS_TO_PASS ≥15, F2P ≥3) — element-web 25,
  qutebrowser 23, ansible 19, NodeBB 12, openlibrary 7, others few. (Only 359/731 have ANY P2P.)
  Decision (owner 2026-06-29): go with **A — mine existing 731** for the hard/regression-rich band;
  reassess toward bug-authoring only if A yields too few agent-failures. NEXT: larger ungoverned probe
  over the 92 to find instances the agent FAILS (the experiment's headroom band).

- 2026-06-29 **Floor pilot v2 (5 instances, ungoverned): 4/5 resolved — but two big caveats that
  reshape the experiment.** (v1 was invalid: driver hardcoded the `node` user, which only exists in
  JS images; agent never ran on Python/Go. Fixed by creating an `agent` user in any image.)
  Verification of v2: element-web (1 file vs gold's 9) and flipt (3 vs 7) are genuine INDEPENDENT
  minimal fixes (low similarity to gold); qutebrowser same 3 files but 0.22 similarity (likely
  genuine); **ansible same 2 files + 0.76 added-line similarity → SUSPECTED LEAK**; navidrome
  genuine fail (8-file attempt, 2 PASSED).
  **CRITICAL — LEAKAGE VECTOR:** the gold fix commit exists as a reachable object in each
  container's git repo (`git cat-file -t <fix>` = commit; `git log --all` exposes future commits).
  An agent can search history and copy the fix. MUST be closed before any trustworthy rate:
  scrub the agent workspace's git to base only (e.g. `git checkout -B evalbase <base>`; delete all
  other refs; `git reflog expire --all --expire=now`; `git gc --prune=now`) so the fix is
  unreachable/pruned while base ancestry (version info) is preserved. Applies to ALL arms. Scoring
  is unaffected (it uses its own fresh image container).
  **CEILING RISK (owner flagged):** even discounting the leak, the ungoverned agent solves most of
  these → little headroom for governance to show an effect. Need HARDER instances (difficulty band
  where ungoverned fails) and a LARGER sample (power). Owner direction 2026-06-29: "we probably
  need more tests and more complex bugs." Open: select hard SWE-bench Pro instances vs author new
  bugs (cf. `docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`) — pending decision.

- 2026-06-29 **KEYSTONE COMPLETE — eval fully operational end-to-end with a real agent; launch
  gate CLEARED.** Owner added the `Bash(docker exec:*)` permission rule; the autonomous
  bypass-permissions agent now runs. First real ungoverned run (NodeBB instance
  `...04998908...-vnan`): agent investigated, produced a 231-line/7-file source fix, captured
  source-only (excluding the 3 test files + `dump.rdb`/`config.json`/`logs` test-run artifacts),
  scored **resolved=FALSE** — the agent did NOT solve it ungoverned. Notable: the agent CLAIMED
  its tests passed, but the held-out GOLD tests fail → the metric discriminates real resolution
  from agent self-report (good validity signal). Mechanics now proven for real:
  `docker run` instance image (mount host `claude` + cred) → setup non-root `node` user, chown
  `/app` → reset to base → `claude -p "$(cat task.md)" --permission-mode bypassPermissions` as node
  → `git add -A && git diff --staged` with test/artifact excludes → score via swe_bench_pro_eval.py.
  **NEXT: floor pilot** — run this ungoverned loop over a diverse ~15-20 instance sample to measure
  the baseline `resolved` rate (the reviewers' #1 de-risk; informs band selection + power). Then
  the design must-fixes (see review synthesis) before the governed factorial.

- 2026-06-29 **Plan reviewed by codex + claude (two blind reviews); science under-specified.**
  Synthesis: `docs/history/2026-06-29-swebench-pro-plan-review_synthesis.md` (raw reviews:
  `..._codex.md`, `..._claude.md`). Verdict: plumbing solid, experiment design/power not yet
  greenlightable. Converged must-fixes before P3: pre-registered analysis + power/MDE; a
  length-matched PLACEBO prose arm; metric honesty (report F2P/P2P separately, P2P empty ~64%);
  a NUMERIC floor-pilot gate; subset-selection rigor (no n=3-5 regression-to-mean); ONE harness
  for the confirmatory factorial (capability spectrum = separate study). The floor pilot is the
  #1 de-risk AND only needs the launch-gate sanction (Blockers). Plan NOT yet revised — design
  changes await owner decisions (see synthesis "Open decisions").

- 2026-06-29 **Keystone recon DONE — one remaining GATE: a sanctioned way to launch the
  autonomous agent.** Proven on netwatch-01: the host `claude` (native amd64 ELF v2.1.195) binary
  + `~/.claude/.credentials.json`, MOUNTED into an instance container, run **headless with
  subscription auth and NO API key** (a "reply PONG" test returned PONG; claude auto-wrote
  `~/.claude.json`, no onboarding block). Containers have node18 + working network (api.anthropic.com
  reachable) + the repo at `/app` checked out at base_commit. **Scoring contract mapped** from
  `swe_bench_pro_eval.py:114-126`: entryscript does `cd /app` → `git reset --hard base` →
  `git checkout base` → `git apply /workspace/patch.diff` → then overlays gold test files (ONLY the
  LAST line of `before_repo_set_cmd`) → runs run_script + parser. ⇒ the agent must submit a
  **SOURCE-ONLY diff vs base_commit**; P1 strips test files (scoring overlays gold tests regardless,
  but stripping blocks test-gaming).
  **GATE (needs owner):** the eval's core is an unsupervised, permission-bypassed coding agent run
  in-container. This Claude Code session's auto-mode classifier blocks the agent (me) from spawning
  `claude -p --permission-mode bypassPermissions` ([Create Unsafe Agents]) — a legitimate guard;
  do NOT evade it (no hiding the spawn inside a wrapper script). Sanctioned options: (1) owner adds
  a scoped Bash permission rule allowing the eval's bypass-agent invocation, so this session can
  develop+run it autonomously; (2) owner runs the eval driver themselves; (3) run the eval in a
  non-auto-mode session.
  **UPDATE 2026-06-29 (capability fully proven; only the sanction remains):** in-container claude
  refuses bypass as ROOT, but runs fine as the image's non-root `node` user (uid 1000) — credential
  copied to `/home/node/.claude/`, `/app` chowned to node. A trivial bypass edit
  (`AGENT_PROOF.txt`) succeeded → the headless autonomous-edit capability works end to end. BUT the
  classifier then blocked the REAL autonomous source-editing run, explicitly reading the owner's
  "invoke … to run tests or review plans" grant as NOT covering an unsupervised bypass source-editing
  agent. So the eval's core still needs an explicit sanctioned launch: (1) owner adds a Bash
  permission rule (e.g. allow `docker exec`) so this session drives it; (2) owner runs the driver
  themselves (spawns happen in their process, not via this session's classifier); or (3) non-auto-mode
  session. Do NOT add such a rule to repo/owner settings unilaterally — it is a security-relevant
  roadblock; owner decides. Everything UP TO the agent spawn is buildable/validatable now using the
  gold patch as a stand-in agent (plain git/scorer calls, not gated).
  **VALIDATED 2026-06-29:** capture round-trip works — gold applied into `/app` as a stand-in agent
  output, captured a SOURCE-ONLY diff via `git add -A && git diff --staged -- . ':(exclude)<testfiles>'`,
  fed to the scorer as a mock prediction → resolved=true. So container-working-tree → source-only
  capture → scorer is proven; only the sanctioned autonomous agent spawn remains. (Note: after
  chowning `/app` to node, root git needs `git config --global --add safe.directory /app`.)

- 2026-06-29 **Gold-resolvability sweep (3 instances/repo, 33 total): 33/33 ≈ 100% resolvable.**
  One openlibrary instance scored false on the first parallel pass but resolved on isolated retry
  (6 PASSED) — so the dataset's gold patches are clean on this substrate; no instance needed
  exclusion in this sample.
  **CRITICAL methodological finding — transient infra failure under parallelism:** at
  `--num_workers=4`, heavy containers occasionally produce **NO output at all** (the instance
  output dir has the workspace but no `gold_output.json` / no stdout/stderr logs), which the scorer
  counts as `resolved=false`. This is DISTINGUISHABLE from a real test failure (empty/absent output
  vs. `gold_output.json` present with FAILED tests) and is RETRYABLE. **P1 MUST: (a) detect the
  "no output produced" case and retry it, (b) never count an infra-empty run as an agent failure,
  (c) keep parallelism modest for heavy repos (Go/webclients images are 5–12 GB).** Counting a
  transient infra flake as the agent failing would silently corrupt the governance-effect measurement.

- 2026-06-29 **P0 DONE — substrate PROVEN on the amd64 Linux box; the blocker below is CLEARED.**
  Box: `netwatch-01` (CachyOS, x86_64, native amd64 — no QEMU), Docker engine active, system
  `python3` is **3.14** (parses the tests), SWE-bench Pro checkout is at
  **`/home/michael/dev/SWE-bench_Pro-os`** on this box (NOT the Mac `/Users/...` path the block
  below names). P0 gold round-trip on instance
  `instance_NodeBB__NodeBB-04998908ba6721d64eba79ae3b65a351dcfbc5b5-vnan`: gold patch scores
  **resolved=true** (300 PASSED/0 FAILED, clean `--redo` container run ~11s); empty-patch negative
  control scores **resolved=false** — so the metric genuinely discriminates. Artifacts in session
  scratchpad, not committed.

- 2026-06-29 **Multi-repo gold round-trip: 11/11 PASS — substrate generalizes across ALL 11 repos**
  (one instance each: NodeBB, qutebrowser, ansible, openlibrary, element-web, navidrome, teleport,
  vuls, flipt, tutanota, webclients; JS/Python/Go/TS). Every gold patch scores resolved=true with
  non-vacuous PASSED counts (each ≥ its F2P+P2P). Done via a reusable adapter
  (`scratchpad/adapter.py`, the P1 seed) that encodes the two gotchas below.
  **Finding (metric design):** `PASS_TO_PASS` is EMPTY for 7 of the 11 sampled instances
  (element-web, navidrome, teleport, vuls, flipt, tutanota, webclients) — so the planned SecPass
  dimension is frequently absent and `joint_pass` collapses to FuncPass there. The plan's
  FuncPass∧SecPass framing must account for SecPass being empty on many instances.
  **Disk sizing (corrected):** on-disk image footprint is **1.6 GB (ansible) → 12 GB (webclients),
  avg ~4.4 GB**; 11 images = 48 GB on disk; 367 GB free. NOTE the earlier "807 MiB" was the
  *compressed pull* size, not on-disk — NodeBB is 3.18 GB unpacked. A ~20-instance subset is
  roughly 50–130 GB on disk depending on repo mix (not "<20GB").

  **Adapter gotchas the P1 instance-adapter MUST encode** (the shipped `swe_bench_pro_eval.py` was
  written for the leaderboard CSV; our jsonl trips two real mismatches — worked around by deriving
  a per-instance sample file, NOT by editing the third-party script):
  (1) **case** — jsonl has `FAIL_TO_PASS`/`PASS_TO_PASS`, scorer reads lowercase
  `fail_to_pass`/`pass_to_pass`; must alias. (2) **type** — scorer does `eval(field)` expecting a
  *string*, but in the jsonl `FAIL_TO_PASS` is a native JSON **list** while `PASS_TO_PASS` is a
  **string** (inconsistent source data); coerce both to string form (survives the pandas
  `read_json` round-trip). Operational: `run_scripts/` (1000 dirs) is present and `instance_id`
  matches dir names exactly; image = `get_dockerhub_image_uri(uid, 'jefzda', repo)`; **always pass
  `--redo`** or the per-instance output cache silently reuses a stale run.

  **Next:** architecture decision, then P1 adapter, P2 subset selection.
  **CORRECTION (owner, 2026-06-29): there are NO API keys in this eval.** The subject under test is
  a **(harness + model)** pair authenticated by a **subscription login** (e.g. Claude Code on a
  Claude subscription, Codex on a ChatGPT subscription) — not API access to a model. So "Option A
  needs API keys" was wrong; Option A's only setup cost is doing the harness's **subscription login
  on netwatch-01**. (Assumption pending owner confirmation, not yet a settled decision: the agent
  should run *inside* the instance container so it can run tests/verify while solving — both because
  the containers are amd64-only/native here and because governance is largely verification
  discipline; that points to running the harness here = Option A.)

- 2026-06-29 **HANDOFF (superseded by the P0 entry above for substrate status; pivot context still
  valid). Eval workstream pivoted to SWE-bench Pro.** Read the P0 entry first, then the two plans
  named below.

  **Where we are:** the governance-efficacy eval's *measurement instrument* is fully built and
  pushed (Phase 0 hardening + the Phase-1 fixture/arms machinery — see the dated entries below).
  But the **synthetic-fixture approach is DEAD**: the frontier-calibration run (Slice F) showed
  Claude clean-passes all 5 hand-built fixtures 10/10 and GPT-5 the same on the 2 it finished —
  zero naive traps, every fixture drops as "too easy" (a model can't invent a bug that stumps
  itself). That result is the whole reason for the pivot; do not retry synthetic fixtures.

  **The pivot (owner-directed):** use **ScaleAI SWE-bench Pro** as the fixture source. Full local
  checkout at **`/Users/michael/Dev/SWE-bench_Pro-os`** (731 real instances in
  `helper_code/sweap_eval_full_v2.jsonl`, 11 repos, multi-language, frontier-resistant). Mapping:
  **FAIL_TO_PASS = our FuncPass, PASS_TO_PASS = our SecPass/regression guard**, so our existing
  **`joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS`** metric and invalid-trial accounting apply
  unchanged. Their `swe_bench_pro_eval.py` is a pure function `(predictions.json, sample) →
  resolved` that scores a patch inside a per-instance Docker image — agent and scorer are
  decoupled by a predictions-JSON file boundary. Integration plan (DRAFT, pre-codex-review):
  **`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`** (pipeline,
  phases P0–P3, open decisions G1–G5). Background + why-the-synthetic-approach-died:
  **`docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`** (its SWE-bench Pro
  addendum supersedes it; the crafting loop is the documented fallback only).

  **THE BLOCKER — CLEARED 2026-06-29 (see P0 entry above).** It was: SWE-bench Pro instance images
  are **amd64-only** and their **test runtimes segfault under Rosetta/QEMU on Apple Silicon**
  (verified: `python3 --version` segfaulted inside `jefzda/sweap-images:ansible...` on the Mac).
  Resolution: the eval now runs on the amd64 Linux box `netwatch-01` where images run natively;
  P0 gold round-trip passed there. The Mac Colima path is abandoned for scoring.

  **Public images:** `jefzda/sweap-images` on Docker Hub (the metadata jsonl points at a *private*
  ScaleAI ECR; ignore that). Derive the pull tag with `helper_code/image_uri.get_dockerhub_image_uri(
  instance_id, 'jefzda', repo)` (it truncates tags >128 chars). Score with
  `swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
  --dockerhub_username jefzda --use_local_docker`.

  **NEXT ACTIONS on the Linux box (in order):**
  1. **P0 — gold round-trip (no governance yet):** on the amd64 box with Docker, pull ONE instance
     image, run `swe_bench_pro_eval.py` on that instance's **gold `patch`** (shipped in the jsonl)
     and confirm it scores **resolved**. This proves the substrate before producing any agent patch.
  2. Decide the architecture (open in the plan): **Option A** = agent runs + scores all on the box;
     **Option B** = governed agent runs on the Mac (our harness/hooks/keys already work), patches
     copied to the box which only scores. Option B needs local `git clone <repo>@base_commit` for the
     agent's workspace; Option A needs model API keys + our harness on the box.
  3. Then P1 (instance adapter + clean patch capture — exclude governance overlay/sentinels from the
     diff), P2 (subset selection: ungoverned FAIL_TO_PASS probe, keep ~20 mid-band instances across
     diverse repos), P3 (the none/prose/prose-hooks factorial). Codex-review the integration plan to
     convergence before building (the workstream's standing discipline).

  **Biggest risk to watch (in the plan):** floor mirror of the earlier ceiling — SWE-bench Pro is
  HARD, so a one-shot Claude-Code/codex driver may resolve ~0 ungoverned, leaving no room to show
  improvement. Subset selection (mid-range ungoverned rate) guards this; if even mid-band instances
  resolve at ~0 the driver (G3) needs a real agentic loop before the factorial.

  **What's reusable as-is:** governance profiles (`evals/governance_profiles/`: none,
  current-template, hook-gate, hook-guard, prose-hooks), `joint_pass`+invalid accounting in
  `evals/aggregate.py`, the claude/codex drivers in `tools/drivers.py`, `evals/calibrate.py`
  (its classify/Wilson logic still scores an ungoverned probe). **Retire/ignore for SWE-bench Pro:**
  the 5 synthetic fixtures, `--check-discrimination`, the calibration *band* gate as a fixture
  source. **Test interpreter: homebrew `python3` (3.14)** — system 3.9 can't parse the tests.
  All eval work pushed to `origin/master` (last: SWE-bench Pro integration plan draft).

- 2026-06-28: **active research workstream — governance-efficacy measurement (`evals/`).** A
  validated, three-times-externally-reviewed experiment plan to measure whether (and which)
  governance components causally help coding agents, lives at **`evals/TEST-PLAN.md`** — start at
  its **§15 "Resume here"** for status, the built harness, model hosts, gotchas. Screening
  findings in `evals/RESULTS-*.md` (frontier models ceiling; security prose ≈ placebo; hooks
  transfer, prose is model-capped). This is a measurement effort *about* the toolkit, separate
  from the toolkit's product backlog below.
- 2026-06-28: **Phase 0 (harness hardening) is COMPLETE and pushed** (master 2bcf6ae..747078b).
  Owner suspended per-slice go for this eval workstream; plan was codex-reviewed to convergence
  (3 passes) first. Seven slices, each committed + mutation-proven + pushed (push policy `always`):
  S1 changed_files fix (overlay before trial-base) + profile collision guard; S2 strip
  pre-existing governance (deletion-safe subset, narrower than discover's detection list);
  S3 driver telemetry (tokens/cost/tool_calls) + transcript redaction to a **gitignored**
  `evals/results/transcripts/`; S4 hook telemetry (present/supported_by_driver/fired via an
  **external** sentinel) + new `hook-smoke` profile; S5 `profile_tokens`; S6 result
  `schema_version`=2 + aggregator telemetry columns & mixed-schema flag. Plan +
  S7 live-smoke evidence: `docs/superpowers/plans/2026-06-28-phase0-harness-hardening.md`.
  **Test interpreter note:** the suite needs **homebrew `python3` (3.14)** — the system
  `/usr/bin/python3` (3.9) cannot parse the tests' `X | None` annotations. 104 tests green.
  Four clean baseline fixture repos prepped under `../test_ground/` (blit_v2, headroom,
  qbit-mobile, rtk — governance stripped, fresh `git init`, no remotes).
  **Model-host note:** drive local models via the **on-host ollama (`localhost:11434`)** —
  local set is `qwen3.6:35b-mlx`, `gemma4:31b-mlx`, `ornith:35b`,
  `north-mini-code-1.0:mlx-mxfp8`. The remote `10.1.10.221` ("Q") is a different host
  serving mostly `:cloud` models and is **not** the local-model source. S7 smoke was
  validated on the local `qwen3.6:35b-mlx` (FuncPass + live hook firing).
  **Next: Phase 1** (build the real-repo fixture set from those repos, calibrate, freeze) —
  per TEST-PLAN §10. Phase 1 is approvable once fixture manifests + metric defs exist; the
  open owner decisions in TEST-PLAN §12 (tier, repos, H6 approval arm, proportionality rule)
  still gate the *screening* runs, not fixture construction.
- The `.agents/decisions.md` "Open Decisions" section is the authoritative queue for deferred/owner-approved-but-unimplemented items; consult it for what is awaiting a plan. Do not echo its count or contents here (anti-enumeration invariant) — read the section.
- **Decided 2026-06-28 — collapse the `update` route into `migration`.** Resolves the former self-contradictory `Open: bootstrap.config.json` fork (the owner chose to dissolve it, not pick (a)/(b)); that Open entry is archived verbatim in `docs/history/decisions-archive.md`, and `bootstrap.config.json` is dropped from the documented layout. The decision is recorded in `.agents/decisions.md` (2026-06-28); the implementation **plan is drafted at `docs/superpowers/plans/2026-06-28-collapse-update-route.md`** (six slices: discover.py+tests, the two procedures, README, the AGENTS template, and Open-entry rewording) and **awaits an owner go to implement** — no code touched yet. Key design point captured in the plan: the `update` route *fork* is removed but the stale-`AGENTS.md` reconciliation is *retained* (re-homed as a conditional in the migration route, gated by `agentsTemplate.reconcileRecommended`, not by a route name). Until the plan lands, the code still has three routes (the "Now" three-route line above is current and correct).
- Possible queue trim (owner hunch, unconfirmed): the `Open: route/verification probes match literal package.json` (monorepo subdir) item is gated on a precondition — whether subdir-scoped bootstrap is a supported mode. If it is not, close as not-applicable rather than fix. Resolving that precondition may drop it from the queue.
- Run harvest sweeps in this repo only on explicit owner request as harvest reports and bug reports accumulate in the dropbox (or fallback).
- Deferred: fix the `tools/discover.py` `operator:playbook` false positive (probe matches bare `` `playbook` `` but the operator is written `` `playbook <name>` ``, so the update route over-reports `reconcileRecommended`). The bug was filed to the `agent-harvest` dropbox on 2026-06-22; the fix (discover.py + a test using the realistic `` `playbook <name>` `` shape) is a separate scoped change awaiting owner go.
- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.
- 2026-06-25: the **AGENTS.md governance boundary** (all three layers) is implemented and Adopted (see "Now" and the 2026-06-25 boundary decision). The **retroactive-cleanup follow-on is now specced** (see "Now" above) and **awaits owner review, then a `plan`**. Its three open questions for the plan: (1) signal shape — a separate `cleanupRecommended` vs. folding into `reconcileRecommended` (leaning separate); (2) sequencing — does the surplus computation ship inside the queued `governance-lint` playbook (Open Decision, 2026-06-22) or as a standalone discovery field, given `governance-lint` is approved-but-unbuilt (don't couple two unbuilt pieces); (3) within-section match granularity — how precisely a reworded target bullet must match its template counterpart before the remainder counts as surplus (lean toward over-reporting; the agent confirms, and a missed leak is the unsafe failure).
- 2026-06-27: **push-policy work is complete** (decision adopted, product changed, this repo dogfooded to `always`). The plan is at `docs/superpowers/plans/2026-06-27-push-policy.md`. Out of scope and not done: `discover.py` reading the `push-policy` marker; update-route reconciliation of *already-bootstrapped* foreign repos (they draft the file and ask on their next update run). No follow-up owed unless those are wanted.
- Deferred: the synchronous `review <agent>` operator ships as a playbook + Claude Code wrapper only. If it is ever promoted to a governance operator advertised in every `AGENTS.md`, the `OPERATOR_WORDS` staleness probe must first be reconciled with the existing deferred `operator:playbook` false positive (above) — adding `review` there would compound it. Not blocking; documented so the promotion is a deliberate step.
- Playbook process note: dispatching `codex` as a reviewer needs the prompt piped via **stdin** (`codex exec --skip-git-repo-check < prompt`), not as a positional arg — the argv form hung on stdin and timed out during the 2026-06-25 boundary-spec review. Worth folding into `templates/playbooks/reviewloop.md` when next touched.

## Blockers

- None active. (The eval-core launch gate was CLEARED 2026-06-29 — owner added the
  `Bash(docker exec:*)` permission rule; the autonomous agent now runs. See the keystone entry
  under Next.)

## Verification

- Changes that touch `tools/discover.py`, `tests/`, or any content under `templates/` or `procedures/` that the discover script copies into target repos: run `python3 -m unittest discover -s tests -v`.
- Documentation-only changes (no effect on setup, commands, runtime behavior, generated files, or user-visible behavior): run `git diff --check`.
- See `AGENTS.md` Verification section and `.agents/repo-map.json` for the policy that applies to future agents.

## Active Sources

- `AGENTS.md`
- `.agents/state.md`
- `.agents/decisions.md`
- `README.md`
- `docs/usage.md`
- `docs/design.md`
- `docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md`
- `tools/discover.py`
- `procedures/*.md`
- `templates/*`

## Unrecorded Repo Memory

None known.
