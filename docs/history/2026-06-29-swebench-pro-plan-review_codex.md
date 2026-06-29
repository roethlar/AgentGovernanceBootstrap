# Codex review — SWE-bench Pro governance integration plan (2026-06-29)

Independent review by `codex exec -s read-only` of
`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md` (incl. the
2026-06-29 empirical update) + `.agents/state.md`. Raw reviewer output; evidence to assess,
not decisions. Design recommendations require owner sign-off.

---

Reading additional input from stdin...
OpenAI Codex v0.142.4
--------
workdir: /home/michael/dev/AgentGovernanceBootstrap
model: gpt-5.5
provider: headroom
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 019f1399-f2a2-7100-b7e4-f44fd5273e15
--------
user
You are a skeptical senior experiment reviewer. Read docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md (especially the '2026-06-29 empirical update' section) and .agents/state.md. CONTEXT: this experiment measures whether repo governance artifacts (an AGENTS.md prose arm; a prose+hooks arm; vs a none arm) causally help a coding harness+model (Claude Code, codex, etc., via subscription) solve SWE-bench Pro bug instances, scored in per-instance Docker containers on an amd64 Linux box. Give a rigorous, CONCRETE critique, prioritized highest-impact first: (1) experimental-design soundness + threats to validity; (2) metric design given PASS_TO_PASS is empty for ~64% of sampled instances; (3) the 'floor' risk — will the agent resolve enough mid-band instances to detect an effect, and how to de-risk; (4) the capability-spectrum idea (weak agy/grok vs strong codex/claude); (5) statistical power for ~20-40 instances x 3 arms with binary outcomes; (6) confounds from injecting governance files into arbitrary OSS repos that never had them; (7) what is missing or likely wrong. Be specific, cite plan sections. Do NOT write any files.
codex
I’ll read the experiment plan and current state first, then anchor the critique to specific sections and lines without touching the workspace.
exec
/usr/bin/zsh -lc 'nl -ba .agents/state.md' in /home/michael/dev/AgentGovernanceBootstrap
exec
/usr/bin/zsh -lc 'nl -ba docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md' in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
     1	# Agent State
     2	
     3	This file is the first place future agents should read for current repo state. Keep it
     4	short and update it when important repo facts change.
     5	
     6	## Now
     7	
     8	- AgentGovernanceBootstrap is the source for the portable governance/bootstrap process.
     9	- It supplies `tools/discover.py`, the procedures in `procedures/`, drafting templates in `templates/`, and supporting docs.
    10	- The toolkit supports three routes (greenfield, migration, update) and has been pilot-validated on external repos (roon-controller, vela, Blit) plus self.
    11	- Governance for this repo itself is in `AGENTS.md` (Prime Invariants, universal and repo-specific rules, operator vocabulary, and pointers) plus this `.agents/` layout (state and decisions).
    12	- 2026-06-21: this repo's own governance was brought current with the product it ships (it had intentionally lagged since 2026-06-20). The self-application added a `CLAUDE.md` shim (`@AGENTS.md`), committed `.claude/commands/` wrappers for the full operator set (`catchup`, `handoff`, `drift`, `decision`, `plan`, `playbook`), and a committed `.claude/settings.json` re-ground hook (fires on context compaction, points back to AGENTS.md). `AGENTS.md` was rewritten to the product shape: a `## Prime Invariants` block, a `## Universal Invariants` section, `## Operator Requests`, a `## Session Startup` trust note, and an updated `## Bootstrap Handoff` that audits wrappers and re-ground hooks. (`.claude/settings.local.json` stays machine-local and untracked.)
    13	- 2026-06-21: the load-bearing-invariant enforcement work landed and is recorded as Adopted — a lean Prime Invariants block plus per-harness re-ground hooks (`templates/hooks/<harness>/`) that fire on compaction, with tests and a design spec (`docs/superpowers/specs/2026-06-21-invariant-reground-reinjection-design.md`). This resolved the last item that had been deferred to this re-run.
    14	- 2026-06-22: closed the update-route template-reconciliation gap. `AGENTS.md` files now carry a `<!-- templateVersion -->` stamp; discovery records an `agentsTemplate` manifest block (current/target version, `reconcileRecommended`, `missingSections`) and, on the update route, the toolkit reconciles a stale or unstamped `AGENTS.md` to the current template before running the wrapper/hook guarantees. Wrapper/hook guidance treats a missing target section as a staleness signal to reconcile, not a cue to narrow the artifact. See the 2026-06-22 decision in `.agents/decisions.md`.
    15	- 2026-06-22: trimmed the per-session guidance tax. A density audit showed prose compression saves only ~2.7% (the guidance is dense, not padded), so instead the `## Bootstrap Handoff` section was collapsed to a conditional pointer to the synced `.bootstrap-tmp/procedures/bootstrap.md` (~600 tokens/session off `AGENTS.md`; the procedure is now the single canonical home for the handoff/reconciliation/wrapper-guard logic), and the token-efficiency invariant now encourages `rtk` as a discretionary per-command proxy (not an auto-rewrite hook) plus compact-but-equivalent working. See the 2026-06-22 decision in `.agents/decisions.md`.
    16	- 2026-06-22: the `agent-harvest` dropbox now also stores bug reports (defects in this product) under a `bugs/` folder. Agents auto-write a report from `templates/bug-report.template.md` and file it via the canonical recipe `procedures/file-bug-report.md` (gh-api preferred, clone fallback, in-repo last resort), publishing only on an explicit owner go; the harvest sweep triages `bugs/`. See the 2026-06-22 decision in `.agents/decisions.md`. The `agent-harvest` repo gained a `bugs/` folder and a README section to match.
    17	- 2026-06-22: unified the two dropbox-write paths. The transport mechanics now live in one shared recipe, `procedures/file-to-dropbox.md`, used by both harvest reports (`migration.md` Step 8) and bug reports (`file-bug-report.md`). Harvest submissions gained the no-clone `gh api` transport and lost their former standing auto-push: every dropbox publish now asks for an explicit owner go. The `gh api` PUT/DELETE path was verified end-to-end against `roethlar/agent-harvest`.
    18	- `.agents/decisions.md` owns the live decision queue (Active entries plus the `## Open Decisions` queue); closed entries are rotated verbatim into `docs/history/decisions-archive.md` per the status-based archiving rule. See that file for the current open/active set rather than echoing a count here.
    19	- 2026-06-25: rewrote the `reviewloop` playbook template (`templates/playbooks/reviewloop.md`) from the async sentinel/watcher design to a synchronous `review <agent>` flow, and added the `.claude/commands/review.md` wrapper. The coder (current harness) dispatches a named reviewer harness (codex/agy/grok/subagent) headless and one-shot per finding, deriving the headless incantation live by probing (no human-maintained table), parses a structured fail-closed JSON verdict (`{verdict, guard_confirmed, reviewed_sha, base_sha, comments}`), records it into the finding doc, and acts under owner-gated merge. The reviewer's guard proof runs in its own git worktree against a pinned base SHA. Design and the cross-harness review that hardened it: `docs/superpowers/specs/2026-06-25-synchronous-review-handoff-design.md`; plan: `docs/superpowers/plans/2026-06-25-synchronous-review-handoff.md`. `review` is a playbook operator, intentionally kept out of `OPERATOR_WORDS`.
    20	- 2026-06-25: added the **stall-not-length** Universal Invariant to `templates/AGENTS.template.md` (iterative processes escalate on a cycle that banks no verifiable progress, never on duration; long converging runs are not capped), `templateVersion` bumped to 2026-06-25. Adopted — see the 2026-06-25 entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance).
    21	- 2026-06-25: implemented the **AGENTS.md governance boundary** (portable + write-authority) in three layers. Two Universal Invariants in `templates/AGENTS.template.md` (portability copy-test; written-only-by-gated-bootstrap/update); the `drift` operator now names AGENTS.md portability/write-authority as drift targets; and an advisory, non-blocking `PreToolUse` pre-edit tripwire (one stdlib-Python `agents-md-tripwire.py` shared by the Claude Code + Codex hook configs) ships under `templates/hooks/`. `templateVersion` 2026-06-25 → 2026-06-25.2 (same-day second structural change). Layer 2 was validated live before building (fires/visible/non-blocking on Codex and on GLM via Claude Code; self-revert seen once); evidence reframed the spec to L1-primary / L3-backstop / L2-advisory. `TestHookTemplates` was reworked from shape-banning to a portability principle so script hooks pass without per-category exceptions. Adopted — see the 2026-06-25 boundary entry in `.agents/decisions.md`. This repo's own `AGENTS.md` is not edited (frozen instance). Spec: `docs/superpowers/specs/2026-06-25-agents-portability-boundary-design.md`; plan: `docs/superpowers/plans/2026-06-25-agents-portability-boundary.md`.
    22	- 2026-06-25: wrote the **AGENTS.md retroactive-cleanup follow-on spec** (`docs/superpowers/specs/2026-06-25-agents-cleanup-via-update-route-design.md`) — design only, awaiting owner review then a `plan`. Decision recorded in it: cleanup is the update-route reconciliation *extended*, not a parallel flow. Key design move (owner insight): detect leaks as **surplus over the portable template** — the structural inverse of `missingSections` (which flags what the target *lacks*; surplus flags what it *has beyond baseline*), so a leaky-but-current, structurally-complete `AGENTS.md` still triggers, and non-path leaks (prose, restated state, the repo's name) are caught where a regex would miss them. Discovery computes surplus structurally; the agent sorts each surplus item into allowed-repo-specific vs leak (surplus ≠ leak: the Current State pointer, Active Sources list are legitimate surplus). Relocation rule (owner-settled): move leaks into `.agents/` with **no per-fact pointer** — keep only the existing structural pointers; rare exception when a governance rule's meaning references a repo-specific detail.
    23	- 2026-06-27: **push policy is now repo-specific, delegated to `.agents/push-policy.md`.** The Prime Invariant push clause in `templates/AGENTS.template.md` no longer carries a blanket push-needs-go rule; it reads "History-rewrite and destructive or outward-facing actions always need an explicit go. Push policy: see `.agents/push-policy.md`." A new `templates/push-policy.template.md` ships the default (`ask`); `templates/approval-summary.template.md` gained a Push Policy section that presents four standardized options (1 always / 2 operators / 3 docs / 4 ask) and must ask the human at approval time (do not pre-fill from the decisions log); `procedures/bootstrap.md` Step 10 consults the policy file after committing. `templateVersion` bumped to `2026-06-27.1`. Adopted — see 2026-06-27 push-policy decision in `.agents/decisions.md`.
    24	- 2026-06-27: **this repo's own governance brought current via a dogfood / self-application run** (the deferred frozen-instance reconciliations all landed in one scoped commit `b844c72`): `AGENTS.md` reconciled `2026-06-22` → `2026-06-27.1` (push clause now delegates to push-policy; stall-not-length invariant; both governance-boundary invariants; sharpened drift/playbook operators; Session Startup mentions the tripwire), `.agents/push-policy.md` created set to **`always`** (every commit here pushes immediately), and the advisory AGENTS.md pre-edit tripwire installed (`.claude/settings.json` PreToolUse block + `.claude/agents-md-tripwire.py`, byte-identical to the shipped template). Repo-specific leaks left in place — their relocation is the separate owner-gated cleanup spec.
    25	- 2026-06-27: **dogfood / self-application named as a case of the update route** — `procedures/bootstrap.md` now states that running the toolkit against itself is an in-place update run and a missing `.bootstrap-tmp/` at kickoff is the normal start, never a stop. Docs handrail only, no `compute_route()` detection. Adopted — see 2026-06-27 dogfood decision in `.agents/decisions.md`. Earned by two fresh sessions stopping to ask "is there anything to do here" on the canonical kickoff line.
    26	- 2026-06-27: **`drift` cleanup of `.agents/decisions.md`** — two adopted entries that were parked in `## Open Decisions` (push-needs-explicit-go, and `run_git` fails open / Adopted 2026-06-23) moved **verbatim** to `docs/history/decisions-archive.md` per the archive rule; the push-policy decision relocated from Open into `## Decisions` as Active (its stale "must be created by running the update route" line corrected — the dogfood run already created it, set to `always`). The Open queue is now exactly nine genuine `Open:` items, no adopted/active mixed in.
    27	- 2026-06-27: all work this session pushed to GitHub (`origin/master` at `1c4fb50`); the gitea mirror follows downstream (observed lagging earlier in the session; catches up). Per the `always` push policy, commits here push immediately rather than awaiting a per-instance go. (This handoff's own commit lands on top and is pushed next; a state line cannot name its own not-yet-created hash.)
    28	
    29	## Next
    30	
    31	- 2026-06-29 **Keystone recon DONE — one remaining GATE: a sanctioned way to launch the
    32	  autonomous agent.** Proven on netwatch-01: the host `claude` (native amd64 ELF v2.1.195) binary
    33	  + `~/.claude/.credentials.json`, MOUNTED into an instance container, run **headless with
    34	  subscription auth and NO API key** (a "reply PONG" test returned PONG; claude auto-wrote
    35	  `~/.claude.json`, no onboarding block). Containers have node18 + working network (api.anthropic.com
    36	  reachable) + the repo at `/app` checked out at base_commit. **Scoring contract mapped** from
    37	  `swe_bench_pro_eval.py:114-126`: entryscript does `cd /app` → `git reset --hard base` →
    38	  `git checkout base` → `git apply /workspace/patch.diff` → then overlays gold test files (ONLY the
    39	  LAST line of `before_repo_set_cmd`) → runs run_script + parser. ⇒ the agent must submit a
    40	  **SOURCE-ONLY diff vs base_commit**; P1 strips test files (scoring overlays gold tests regardless,
    41	  but stripping blocks test-gaming).
    42	  **GATE (needs owner):** the eval's core is an unsupervised, permission-bypassed coding agent run
    43	  in-container. This Claude Code session's auto-mode classifier blocks the agent (me) from spawning
    44	  `claude -p --permission-mode bypassPermissions` ([Create Unsafe Agents]) — a legitimate guard;
    45	  do NOT evade it (no hiding the spawn inside a wrapper script). Sanctioned options: (1) owner adds
    46	  a scoped Bash permission rule allowing the eval's bypass-agent invocation, so this session can
    47	  develop+run it autonomously; (2) owner runs the eval driver themselves; (3) run the eval in a
    48	  non-auto-mode session.
    49	  **UPDATE 2026-06-29 (capability fully proven; only the sanction remains):** in-container claude
    50	  refuses bypass as ROOT, but runs fine as the image's non-root `node` user (uid 1000) — credential
    51	  copied to `/home/node/.claude/`, `/app` chowned to node. A trivial bypass edit
    52	  (`AGENT_PROOF.txt`) succeeded → the headless autonomous-edit capability works end to end. BUT the
    53	  classifier then blocked the REAL autonomous source-editing run, explicitly reading the owner's
    54	  "invoke … to run tests or review plans" grant as NOT covering an unsupervised bypass source-editing
    55	  agent. So the eval's core still needs an explicit sanctioned launch: (1) owner adds a Bash
    56	  permission rule (e.g. allow `docker exec`) so this session drives it; (2) owner runs the driver
    57	  themselves (spawns happen in their process, not via this session's classifier); or (3) non-auto-mode
    58	  session. Do NOT add such a rule to repo/owner settings unilaterally — it is a security-relevant
    59	  roadblock; owner decides. Everything UP TO the agent spawn is buildable/validatable now using the
    60	  gold patch as a stand-in agent (plain git/scorer calls, not gated).
    61	  **VALIDATED 2026-06-29:** capture round-trip works — gold applied into `/app` as a stand-in agent
    62	  output, captured a SOURCE-ONLY diff via `git add -A && git diff --staged -- . ':(exclude)<testfiles>'`,
    63	  fed to the scorer as a mock prediction → resolved=true. So container-working-tree → source-only
    64	  capture → scorer is proven; only the sanctioned autonomous agent spawn remains. (Note: after
    65	  chowning `/app` to node, root git needs `git config --global --add safe.directory /app`.)
    66	
    67	- 2026-06-29 **Gold-resolvability sweep (3 instances/repo, 33 total): 33/33 ≈ 100% resolvable.**
    68	  One openlibrary instance scored false on the first parallel pass but resolved on isolated retry
    69	  (6 PASSED) — so the dataset's gold patches are clean on this substrate; no instance needed
    70	  exclusion in this sample.
    71	  **CRITICAL methodological finding — transient infra failure under parallelism:** at
    72	  `--num_workers=4`, heavy containers occasionally produce **NO output at all** (the instance
    73	  output dir has the workspace but no `gold_output.json` / no stdout/stderr logs), which the scorer
    74	  counts as `resolved=false`. This is DISTINGUISHABLE from a real test failure (empty/absent output
    75	  vs. `gold_output.json` present with FAILED tests) and is RETRYABLE. **P1 MUST: (a) detect the
    76	  "no output produced" case and retry it, (b) never count an infra-empty run as an agent failure,
    77	  (c) keep parallelism modest for heavy repos (Go/webclients images are 5–12 GB).** Counting a
    78	  transient infra flake as the agent failing would silently corrupt the governance-effect measurement.
    79	
    80	- 2026-06-29 **P0 DONE — substrate PROVEN on the amd64 Linux box; the blocker below is CLEARED.**
    81	  Box: `netwatch-01` (CachyOS, x86_64, native amd64 — no QEMU), Docker engine active, system
    82	  `python3` is **3.14** (parses the tests), SWE-bench Pro checkout is at
    83	  **`/home/michael/dev/SWE-bench_Pro-os`** on this box (NOT the Mac `/Users/...` path the block
    84	  below names). P0 gold round-trip on instance
    85	  `instance_NodeBB__NodeBB-04998908ba6721d64eba79ae3b65a351dcfbc5b5-vnan`: gold patch scores
    86	  **resolved=true** (300 PASSED/0 FAILED, clean `--redo` container run ~11s); empty-patch negative
    87	  control scores **resolved=false** — so the metric genuinely discriminates. Artifacts in session
    88	  scratchpad, not committed.
    89	
    90	- 2026-06-29 **Multi-repo gold round-trip: 11/11 PASS — substrate generalizes across ALL 11 repos**
    91	  (one instance each: NodeBB, qutebrowser, ansible, openlibrary, element-web, navidrome, teleport,
    92	  vuls, flipt, tutanota, webclients; JS/Python/Go/TS). Every gold patch scores resolved=true with
    93	  non-vacuous PASSED counts (each ≥ its F2P+P2P). Done via a reusable adapter
    94	  (`scratchpad/adapter.py`, the P1 seed) that encodes the two gotchas below.
    95	  **Finding (metric design):** `PASS_TO_PASS` is EMPTY for 7 of the 11 sampled instances
    96	  (element-web, navidrome, teleport, vuls, flipt, tutanota, webclients) — so the planned SecPass
    97	  dimension is frequently absent and `joint_pass` collapses to FuncPass there. The plan's
    98	  FuncPass∧SecPass framing must account for SecPass being empty on many instances.
    99	  **Disk sizing (corrected):** on-disk image footprint is **1.6 GB (ansible) → 12 GB (webclients),
   100	  avg ~4.4 GB**; 11 images = 48 GB on disk; 367 GB free. NOTE the earlier "807 MiB" was the
   101	  *compressed pull* size, not on-disk — NodeBB is 3.18 GB unpacked. A ~20-instance subset is
   102	  roughly 50–130 GB on disk depending on repo mix (not "<20GB").
   103	
   104	  **Adapter gotchas the P1 instance-adapter MUST encode** (the shipped `swe_bench_pro_eval.py` was
   105	  written for the leaderboard CSV; our jsonl trips two real mismatches — worked around by deriving
   106	  a per-instance sample file, NOT by editing the third-party script):
   107	  (1) **case** — jsonl has `FAIL_TO_PASS`/`PASS_TO_PASS`, scorer reads lowercase
   108	  `fail_to_pass`/`pass_to_pass`; must alias. (2) **type** — scorer does `eval(field)` expecting a
   109	  *string*, but in the jsonl `FAIL_TO_PASS` is a native JSON **list** while `PASS_TO_PASS` is a
   110	  **string** (inconsistent source data); coerce both to string form (survives the pandas
   111	  `read_json` round-trip). Operational: `run_scripts/` (1000 dirs) is present and `instance_id`
   112	  matches dir names exactly; image = `get_dockerhub_image_uri(uid, 'jefzda', repo)`; **always pass
   113	  `--redo`** or the per-instance output cache silently reuses a stale run.
   114	
   115	  **Next:** architecture decision, then P1 adapter, P2 subset selection.
   116	  **CORRECTION (owner, 2026-06-29): there are NO API keys in this eval.** The subject under test is
   117	  a **(harness + model)** pair authenticated by a **subscription login** (e.g. Claude Code on a
   118	  Claude subscription, Codex on a ChatGPT subscription) — not API access to a model. So "Option A
   119	  needs API keys" was wrong; Option A's only setup cost is doing the harness's **subscription login
   120	  on netwatch-01**. (Assumption pending owner confirmation, not yet a settled decision: the agent
   121	  should run *inside* the instance container so it can run tests/verify while solving — both because
   122	  the containers are amd64-only/native here and because governance is largely verification
   123	  discipline; that points to running the harness here = Option A.)
   124	
   125	- 2026-06-29 **HANDOFF (superseded by the P0 entry above for substrate status; pivot context still
   126	  valid). Eval workstream pivoted to SWE-bench Pro.** Read the P0 entry first, then the two plans
   127	  named below.
   128	
   129	  **Where we are:** the governance-efficacy eval's *measurement instrument* is fully built and
   130	  pushed (Phase 0 hardening + the Phase-1 fixture/arms machinery — see the dated entries below).
   131	  But the **synthetic-fixture approach is DEAD**: the frontier-calibration run (Slice F) showed
   132	  Claude clean-passes all 5 hand-built fixtures 10/10 and GPT-5 the same on the 2 it finished —
   133	  zero naive traps, every fixture drops as "too easy" (a model can't invent a bug that stumps
   134	  itself). That result is the whole reason for the pivot; do not retry synthetic fixtures.
   135	
   136	  **The pivot (owner-directed):** use **ScaleAI SWE-bench Pro** as the fixture source. Full local
   137	  checkout at **`/Users/michael/Dev/SWE-bench_Pro-os`** (731 real instances in
   138	  `helper_code/sweap_eval_full_v2.jsonl`, 11 repos, multi-language, frontier-resistant). Mapping:
   139	  **FAIL_TO_PASS = our FuncPass, PASS_TO_PASS = our SecPass/regression guard**, so our existing
   140	  **`joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS`** metric and invalid-trial accounting apply
   141	  unchanged. Their `swe_bench_pro_eval.py` is a pure function `(predictions.json, sample) →
   142	  resolved` that scores a patch inside a per-instance Docker image — agent and scorer are
   143	  decoupled by a predictions-JSON file boundary. Integration plan (DRAFT, pre-codex-review):
   144	  **`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`** (pipeline,
   145	  phases P0–P3, open decisions G1–G5). Background + why-the-synthetic-approach-died:
   146	  **`docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`** (its SWE-bench Pro
   147	  addendum supersedes it; the crafting loop is the documented fallback only).
   148	
   149	  **THE BLOCKER — CLEARED 2026-06-29 (see P0 entry above).** It was: SWE-bench Pro instance images
   150	  are **amd64-only** and their **test runtimes segfault under Rosetta/QEMU on Apple Silicon**
   151	  (verified: `python3 --version` segfaulted inside `jefzda/sweap-images:ansible...` on the Mac).
   152	  Resolution: the eval now runs on the amd64 Linux box `netwatch-01` where images run natively;
   153	  P0 gold round-trip passed there. The Mac Colima path is abandoned for scoring.
   154	
   155	  **Public images:** `jefzda/sweap-images` on Docker Hub (the metadata jsonl points at a *private*
   156	  ScaleAI ECR; ignore that). Derive the pull tag with `helper_code/image_uri.get_dockerhub_image_uri(
   157	  instance_id, 'jefzda', repo)` (it truncates tags >128 chars). Score with
   158	  `swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
   159	  --dockerhub_username jefzda --use_local_docker`.
   160	
   161	  **NEXT ACTIONS on the Linux box (in order):**
   162	  1. **P0 — gold round-trip (no governance yet):** on the amd64 box with Docker, pull ONE instance
   163	     image, run `swe_bench_pro_eval.py` on that instance's **gold `patch`** (shipped in the jsonl)
   164	     and confirm it scores **resolved**. This proves the substrate before producing any agent patch.
   165	  2. Decide the architecture (open in the plan): **Option A** = agent runs + scores all on the box;
   166	     **Option B** = governed agent runs on the Mac (our harness/hooks/keys already work), patches
   167	     copied to the box which only scores. Option B needs local `git clone <repo>@base_commit` for the
   168	     agent's workspace; Option A needs model API keys + our harness on the box.
   169	  3. Then P1 (instance adapter + clean patch capture — exclude governance overlay/sentinels from the
   170	     diff), P2 (subset selection: ungoverned FAIL_TO_PASS probe, keep ~20 mid-band instances across
   171	     diverse repos), P3 (the none/prose/prose-hooks factorial). Codex-review the integration plan to
   172	     convergence before building (the workstream's standing discipline).
   173	
   174	  **Biggest risk to watch (in the plan):** floor mirror of the earlier ceiling — SWE-bench Pro is
   175	  HARD, so a one-shot Claude-Code/codex driver may resolve ~0 ungoverned, leaving no room to show
   176	  improvement. Subset selection (mid-range ungoverned rate) guards this; if even mid-band instances
   177	  resolve at ~0 the driver (G3) needs a real agentic loop before the factorial.
   178	
   179	  **What's reusable as-is:** governance profiles (`evals/governance_profiles/`: none,
   180	  current-template, hook-gate, hook-guard, prose-hooks), `joint_pass`+invalid accounting in
   181	  `evals/aggregate.py`, the claude/codex drivers in `tools/drivers.py`, `evals/calibrate.py`
   182	  (its classify/Wilson logic still scores an ungoverned probe). **Retire/ignore for SWE-bench Pro:**
   183	  the 5 synthetic fixtures, `--check-discrimination`, the calibration *band* gate as a fixture
   184	  source. **Test interpreter: homebrew `python3` (3.14)** — system 3.9 can't parse the tests.
   185	  All eval work pushed to `origin/master` (last: SWE-bench Pro integration plan draft).
   186	
   187	- 2026-06-28: **active research workstream — governance-efficacy measurement (`evals/`).** A
   188	  validated, three-times-externally-reviewed experiment plan to measure whether (and which)
   189	  governance components causally help coding agents, lives at **`evals/TEST-PLAN.md`** — start at
   190	  its **§15 "Resume here"** for status, the built harness, model hosts, gotchas. Screening
   191	  findings in `evals/RESULTS-*.md` (frontier models ceiling; security prose ≈ placebo; hooks
   192	  transfer, prose is model-capped). This is a measurement effort *about* the toolkit, separate
   193	  from the toolkit's product backlog below.
   194	- 2026-06-28: **Phase 0 (harness hardening) is COMPLETE and pushed** (master 2bcf6ae..747078b).
   195	  Owner suspended per-slice go for this eval workstream; plan was codex-reviewed to convergence
   196	  (3 passes) first. Seven slices, each committed + mutation-proven + pushed (push policy `always`):
   197	  S1 changed_files fix (overlay before trial-base) + profile collision guard; S2 strip
   198	  pre-existing governance (deletion-safe subset, narrower than discover's detection list);
   199	  S3 driver telemetry (tokens/cost/tool_calls) + transcript redaction to a **gitignored**
   200	  `evals/results/transcripts/`; S4 hook telemetry (present/supported_by_driver/fired via an
   201	  **external** sentinel) + new `hook-smoke` profile; S5 `profile_tokens`; S6 result
   202	  `schema_version`=2 + aggregator telemetry columns & mixed-schema flag. Plan +
   203	  S7 live-smoke evidence: `docs/superpowers/plans/2026-06-28-phase0-harness-hardening.md`.
   204	  **Test interpreter note:** the suite needs **homebrew `python3` (3.14)** — the system
   205	  `/usr/bin/python3` (3.9) cannot parse the tests' `X | None` annotations. 104 tests green.
   206	  Four clean baseline fixture repos prepped under `../test_ground/` (blit_v2, headroom,
   207	  qbit-mobile, rtk — governance stripped, fresh `git init`, no remotes).
   208	  **Model-host note:** drive local models via the **on-host ollama (`localhost:11434`)** —
   209	  local set is `qwen3.6:35b-mlx`, `gemma4:31b-mlx`, `ornith:35b`,
   210	  `north-mini-code-1.0:mlx-mxfp8`. The remote `10.1.10.221` ("Q") is a different host
   211	  serving mostly `:cloud` models and is **not** the local-model source. S7 smoke was
   212	  validated on the local `qwen3.6:35b-mlx` (FuncPass + live hook firing).
   213	  **Next: Phase 1** (build the real-repo fixture set from those repos, calibrate, freeze) —
   214	  per TEST-PLAN §10. Phase 1 is approvable once fixture manifests + metric defs exist; the
   215	  open owner decisions in TEST-PLAN §12 (tier, repos, H6 approval arm, proportionality rule)
   216	  still gate the *screening* runs, not fixture construction.
   217	- The `.agents/decisions.md` "Open Decisions" section is the authoritative queue for deferred/owner-approved-but-unimplemented items; consult it for what is awaiting a plan. Do not echo its count or contents here (anti-enumeration invariant) — read the section.
   218	- **Decided 2026-06-28 — collapse the `update` route into `migration`.** Resolves the former self-contradictory `Open: bootstrap.config.json` fork (the owner chose to dissolve it, not pick (a)/(b)); that Open entry is archived verbatim in `docs/history/decisions-archive.md`, and `bootstrap.config.json` is dropped from the documented layout. The decision is recorded in `.agents/decisions.md` (2026-06-28); the implementation **plan is drafted at `docs/superpowers/plans/2026-06-28-collapse-update-route.md`** (six slices: discover.py+tests, the two procedures, README, the AGENTS template, and Open-entry rewording) and **awaits an owner go to implement** — no code touched yet. Key design point captured in the plan: the `update` route *fork* is removed but the stale-`AGENTS.md` reconciliation is *retained* (re-homed as a conditional in the migration route, gated by `agentsTemplate.reconcileRecommended`, not by a route name). Until the plan lands, the code still has three routes (the "Now" three-route line above is current and correct).
   219	- Possible queue trim (owner hunch, unconfirmed): the `Open: route/verification probes match literal package.json` (monorepo subdir) item is gated on a precondition — whether subdir-scoped bootstrap is a supported mode. If it is not, close as not-applicable rather than fix. Resolving that precondition may drop it from the queue.
   220	- Run harvest sweeps in this repo only on explicit owner request as harvest reports and bug reports accumulate in the dropbox (or fallback).
   221	- Deferred: fix the `tools/discover.py` `operator:playbook` false positive (probe matches bare `` `playbook` `` but the operator is written `` `playbook <name>` ``, so the update route over-reports `reconcileRecommended`). The bug was filed to the `agent-harvest` dropbox on 2026-06-22; the fix (discover.py + a test using the realistic `` `playbook <name>` `` shape) is a separate scoped change awaiting owner go.
   222	- Support for small/local models remains best-effort: agents should use the fallback flow (run discovery manually then `Read .bootstrap-tmp/START-HERE.md and follow it.`) together with a plugin-free harness profile.
   223	- The harvest digest script is deferred until report volume justifies the work (see the 2026-06-09 spec).
   224	- Cross-harness re-ground efficacy/schema for Codex/Grok/agy is tracked in the 2026-06-21 spec (Q6) and is not blocking.
   225	- 2026-06-25: the **AGENTS.md governance boundary** (all three layers) is implemented and Adopted (see "Now" and the 2026-06-25 boundary decision). The **retroactive-cleanup follow-on is now specced** (see "Now" above) and **awaits owner review, then a `plan`**. Its three open questions for the plan: (1) signal shape — a separate `cleanupRecommended` vs. folding into `reconcileRecommended` (leaning separate); (2) sequencing — does the surplus computation ship inside the queued `governance-lint` playbook (Open Decision, 2026-06-22) or as a standalone discovery field, given `governance-lint` is approved-but-unbuilt (don't couple two unbuilt pieces); (3) within-section match granularity — how precisely a reworded target bullet must match its template counterpart before the remainder counts as surplus (lean toward over-reporting; the agent confirms, and a missed leak is the unsafe failure).
   226	- 2026-06-27: **push-policy work is complete** (decision adopted, product changed, this repo dogfooded to `always`). The plan is at `docs/superpowers/plans/2026-06-27-push-policy.md`. Out of scope and not done: `discover.py` reading the `push-policy` marker; update-route reconciliation of *already-bootstrapped* foreign repos (they draft the file and ask on their next update run). No follow-up owed unless those are wanted.
   227	- Deferred: the synchronous `review <agent>` operator ships as a playbook + Claude Code wrapper only. If it is ever promoted to a governance operator advertised in every `AGENTS.md`, the `OPERATOR_WORDS` staleness probe must first be reconciled with the existing deferred `operator:playbook` false positive (above) — adding `review` there would compound it. Not blocking; documented so the promotion is a deliberate step.
   228	- Playbook process note: dispatching `codex` as a reviewer needs the prompt piped via **stdin** (`codex exec --skip-git-repo-check < prompt`), not as a positional arg — the argv form hung on stdin and timed out during the 2026-06-25 boundary-spec review. Worth folding into `templates/playbooks/reviewloop.md` when next touched.
   229	
   230	## Blockers
   231	
   232	None recorded.
   233	
   234	## Verification
   235	
   236	- Changes that touch `tools/discover.py`, `tests/`, or any content under `templates/` or `procedures/` that the discover script copies into target repos: run `python3 -m unittest discover -s tests -v`.
   237	- Documentation-only changes (no effect on setup, commands, runtime behavior, generated files, or user-visible behavior): run `git diff --check`.
   238	- See `AGENTS.md` Verification section and `.agents/repo-map.json` for the policy that applies to future agents.
   239	
   240	## Active Sources
   241	
   242	- `AGENTS.md`
   243	- `.agents/state.md`
   244	- `.agents/decisions.md`
   245	- `README.md`
   246	- `docs/usage.md`
   247	- `docs/design.md`
   248	- `docs/superpowers/specs/2026-06-09-existing-governance-migration-design.md`
   249	- `tools/discover.py`
   250	- `procedures/*.md`
   251	- `templates/*`
   252	
   253	## Unrecorded Repo Memory
   254	
   255	None known.

 succeeded in 0ms:
     1	# SWE-bench Pro × governance integration
     2	
     3	Status: DRAFT 2026-06-29, pre-codex-review. Supersedes the synthetic-fixture and
     4	bug-crafting approaches for fixture-sourcing (see
     5	`2026-06-29-adversarial-bugcrafting-loop.md` addendum). No code yet.
     6	
     7	## Empirical update — 2026-06-29 (validated facts; supersedes stale substrate/P0 text below)
     8	
     9	Substrate work ran on the amd64 Linux box `netwatch-01` (NOT the Mac/Colima setup in
    10	"Execution substrate" below — that section is stale; Apple-Silicon amd64-emulation risk is
    11	MOOT here, images run native). Live authority: `.agents/state.md`.
    12	
    13	- **P0 DONE + generalized.** Gold round-trip passes; empty-patch negative control fails
    14	  (metric discriminates). Generalizes 11/11 repos. Gold-resolvability sweep 33/33 ≈ 100%
    15	  (one transient flake, resolved on retry) — gold patches are clean here, so ~all instances
    16	  are usable. ("No code yet" / P0-pending text below is superseded.)
    17	- **Disk sizing (real):** on-disk image footprint 1.6–12 GB each, avg ~4.4 GB (NOT multi-TB
    18	  per image). A 20–40 instance subset ≈ 90–180 GB; 320+ GB free. Subset still wise, numbers
    19	  far smaller than the plan assumed.
    20	- **Integration-contract gotchas the adapter MUST encode:** the shipped scorer targets the
    21	  leaderboard CSV; our jsonl trips two real mismatches — (1) it reads lowercase
    22	  `fail_to_pass`/`pass_to_pass` (jsonl has uppercase); (2) it `eval()`s those expecting a
    23	  *string*, but jsonl `FAIL_TO_PASS` is a list and `PASS_TO_PASS` a string — coerce both to
    24	  string. Predictions accept `model_patch` OR `patch`; always pass `--redo` (per-instance
    25	  output cache silently reuses stale runs).
    26	- **Patch-capture VALIDATED (and bigger than the plan said):** capture = source-only
    27	  `git diff --staged` vs base, EXCLUDING (a) governance overlay/sentinels AND (b) **test
    28	  files** — the scorer overlays gold test files itself (only the LAST line of
    29	  `before_repo_set_cmd`), applied AFTER the agent patch, so agent test edits must be stripped
    30	  (prevents test-gaming). Round-trip proven: gold applied into `/app`, captured, scored resolved.
    31	- **Metric caveat (affects the primary metric):** `PASS_TO_PASS` is EMPTY for 7 of 11 sampled
    32	  instances → `joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS` collapses to FAIL_TO_PASS for those.
    33	  The FuncPass∧SecPass framing must handle frequently-empty SecPass.
    34	- **Transient infra-failure mode (must handle):** at `--num_workers=4`, heavy 5–12 GB
    35	  containers occasionally produce NO output (absent `gold_output.json`) → scored false.
    36	  DISTINGUISHABLE (absent output vs tests-ran-and-failed) and RETRYABLE; retry it, never count
    37	  it as an agent failure.
    38	- **Agent-run mechanism (proven):** host `claude` native binary + subscription credential
    39	  mounted into the instance container, run headless as the non-root `node` user (root refused),
    40	  no API key. Subject = harness+model via SUBSCRIPTION, not API keys.
    41	- **NEW GATE (open):** launching the unsupervised bypass-permissions agent — the eval's core —
    42	  is blocked by the running session's safety classifier; needs an owner-sanctioned launch path
    43	  (settings permission rule / owner-run driver / non-auto-mode).
    44	- **NEW design lever (owner):** harnesses span capability — agy/grok (weaker) vs codex/claude
    45	  (stronger). Weaker agents plausibly have more headroom for governance to help; consider
    46	  spanning capability deliberately rather than a single primary frontier (revisits G1).
    47	
    48	## Goal
    49	
    50	Measure whether our governance product (prose / hooks / both) makes a frontier agent
    51	reliably better at **real, hard, frontier-resistant** software tasks — using ScaleAI
    52	SWE-bench Pro (`/Users/michael/Dev/SWE-bench_Pro-os`, 1000 instances, 11 repos) as the
    53	fixture source instead of synthetic bugs that frontier models trivially solved.
    54	
    55	Primary metric unchanged: **joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS** (their scorer's
    56	two dimensions ARE our FuncPass ∧ SecPass). A governance arm "wins" by raising the
    57	fraction of instances resolved (both the target test passes AND no regression).
    58	
    59	## The integration contract (verified by reading swe_bench_pro_eval.py)
    60	
    61	Their eval is a pure function over a **predictions file**:
    62	`swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
    63	--output_dir <out> [--use_local_docker]`. The predictions JSON is
    64	`[{instance_id, model_patch}]` (they ship `gold_patches.json` as the reference shape).
    65	For each instance it: builds/pulls the instance Docker image, resets to `base_commit`,
    66	applies `model_patch`, runs the test command, scores FAIL_TO_PASS + PASS_TO_PASS.
    67	
    68	**Decoupling:** the agent that produces the patch is entirely separate from the scorer.
    69	Governance lives 100% in patch *production*; the scorer never sees our harness.
    70	
    71	## Pipeline (file boundary between our side and theirs)
    72	
    73	```
    74	PER (instance, arm):
    75	  1. scaffold instance repo at base_commit            (our harness: scaffold)
    76	  2. overlay governance profile (none/prose/hook-*)   (our harness: overlay_profile)
    77	  3. run our driver (claude/codex) on the problem     (our harness: drivers + hooks)
    78	  4. capture the agent's diff vs base_commit          -> patch text
    79	COLLATE per arm:
    80	  5. write predictions_<arm>.json = [{instance_id, model_patch}]
    81	SCORE (their harness):
    82	  6. swe_bench_pro_eval.py --patch_path predictions_<arm>.json ... --use_local_docker
    83	ANALYZE (our side):
    84	  7. join their resolved results back per arm; joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS;
    85	     reuse invalid-trial accounting (protected-file edits, inert hooks) + telemetry.
    86	```
    87	
    88	The patch-capture in step 4 is `git diff` against `base_commit` in the agent's
    89	workspace, EXCLUDING the overlaid governance files and any hook sentinel (those are
    90	environment, not the agent's fix — same exclusion logic as our changed_files work).
    91	
    92	## What we keep / build / retire
    93	
    94	- **Keep:** governance profiles (none, current-template, hook-gate, hook-guard,
    95	  prose-hooks); joint_pass; invalid-trial accounting; transcript/telemetry capture;
    96	  the claude/codex drivers.
    97	- **Build:** an instance adapter (SWE-bench-Pro instance metadata -> our scaffold +
    98	  a problem prompt for the driver), the patch-capture + predictions-writer, and a thin
    99	  wrapper that shells their `swe_bench_pro_eval.py` and ingests its output.
   100	- **Retire:** synthetic fixtures, `--check-discrimination`, the calibration band,
   101	  the bug-crafting loop. (Left in the repo/history; not used.)
   102	
   103	## Execution substrate (Docker confirmed installing)
   104	
   105	- Hardware: M4 Max, 16 cores, 48GB, 566GB free — ample for a SUBSET. Colima with
   106	  `--cpu 8 --memory 24 --disk 200`.
   107	- **Not all 1000** — image storage alone is multi-TB. Subset of ~20–40 instances.
   108	- **Arch check (open risk):** some base images may be `linux/amd64` (the ansible base
   109	  is dated 2022). Those run under emulation on Apple Silicon — slow, occasionally
   110	  flaky. Step 0 of execution: probe candidate instances' image arch and prefer
   111	  arm64-clean repos for the subset; pass `--platform` explicitly where needed.
   112	
   113	## Subset selection (replaces the calibration gate, on real tasks)
   114	
   115	The calibration question is unchanged but now answered on real tasks: pick instances
   116	where the target model's **ungoverned FAIL_TO_PASS rate is mid-range** — solvable
   117	enough that the agent engages, hard enough that it often fails — so governance has room.
   118	- Probe: run the target model under `none` on a candidate pool (n≈3–5 each), keep
   119	  instances whose ungoverned resolve rate is, say, 20–70%.
   120	- Diversity: 3–4 repos, mixed languages, spanning the difficulty band. ~20 survivors.
   121	- This is real spend but bounded (pool × small n under one arm).
   122	
   123	## Open decisions
   124	
   125	- **G1. Target model(s).** Lean: one primary (cheap-ish frontier — a Claude model or
   126	  GPT-5 codex) for subset selection + the factorial; optionally replicate the headline
   127	  delta on a second. (Owner already chose "both Claude + GPT-5 as arms" for the prior
   128	  plan — carry forward unless cost says otherwise.)
   129	- **G2. Agent scaffold.** Lean: OUR claude/codex drivers + governance overlay (keeps
   130	  the hooks/arms we built; closest to the Cursor↔Claude-Code question). NOT their
   131	  SWE-Agent (our Claude-Code hooks don't ride in it). Risk: our simple one-shot driver
   132	  may resolve far fewer instances than a real agent loop — may need a minimal
   133	  agentic loop (read/edit/run-tests) for the agent to stand a chance on long-horizon
   134	  tasks. This is the biggest unknown; see G3.
   135	- **G3. Driver capability.** SWE-bench Pro is LONG-HORIZON; a single `claude -p` call
   136	  likely resolves very little. Options: (a) rely on Claude Code's own agentic loop
   137	  (it already reads/edits/runs commands within one `-p` invocation) — probably
   138	  sufficient and is the realistic "Claude Code" product; (b) build a minimal
   139	  multi-turn loop. Lean (a) — it is the actual product being measured.
   140	- **G4. n and arms for the real run.** With ~20 instances × 5 arms × n, cost is real.
   141	  Lean: start none vs prose vs prose-hooks (3 arms) on the subset at n=3, expand to the
   142	  full 5 arms only if a signal appears.
   143	- **G5. Network during agent run.** Their scorer can `--block_network`; the agent run
   144	  (dependency install, etc.) may need network. Decide per phase (agent: network on;
   145	  scoring: their default).
   146	
   147	## Risks
   148	
   149	1. **Floor risk (mirror of the ceiling problem):** SWE-bench Pro is HARD; a one-shot
   150	   Claude-Code driver may resolve ~0 under `none`, leaving no room to show improvement
   151	   in the other direction. The subset-selection band (G,  mid-range ungoverned rate)
   152	   guards against this — but if even mid-range instances resolve at ~0, the driver
   153	   (G3) is too weak and must be strengthened before the factorial.
   154	2. **Image arch / build cost:** amd64 emulation could make runs slow/flaky; mitigated
   155	   by arm64-preferred subset.
   156	3. **Patch-capture fidelity:** the diff must exclude governance overlay + sentinels or
   157	   the patch won't apply cleanly in their clean-base container (it would carry AGENTS.md
   158	   etc.). Reuse the changed_files exclusion logic; test that a captured patch applies in
   159	   a fresh checkout.
   160	4. **Their harness assumptions:** confirm predictions JSON schema + sample schema by
   161	   round-tripping `gold_patches.json` through the scorer first (a gold patch must score
   162	   resolved) BEFORE trusting our patches — a cheap correctness anchor.
   163	
   164	## Phased plan (each gated, codex-reviewed)
   165	
   166	- **P0 — substrate up + gold round-trip.** Colima running; pull/build ONE instance
   167	  image; run their scorer on that instance's gold patch and confirm it scores resolved.
   168	  Proves the scorer works locally before we produce any patch. (No governance yet.)
   169	- **P1 — instance adapter + patch capture.** Map a SWE-bench Pro instance to our
   170	  scaffold + problem prompt; run our driver under `none`; capture a clean patch; write
   171	  predictions JSON; score it. Confirm end-to-end on 1–2 instances.
   172	- **P2 — subset selection.** Ungoverned probe over a candidate pool; freeze ~20 mid-band
   173	  instances across diverse repos (arch-checked).
   174	- **P3 — factorial.** none / prose / prose-hooks (G4) over the frozen subset; joint_pass;
   175	  invalid accounting; report deltas with CIs. Expand arms/n if signal.
   176	
   177	## Verification
   178	
   179	- P0 gold round-trip is the substrate correctness anchor.
   180	- P1 patch-applies-in-fresh-checkout test (hermetic-ish: a captured patch must apply on
   181	  a clean base commit).
   182	- Adapter/capture/predictions-writer unit-tested with a fake driver (no model, no
   183	  Docker) for the file-shape contract; the Docker scoring is the live/integration part.
   184	- joint_pass + invalid accounting already tested (Slice C).

codex
The plan has several malformed or stale passages, so I’m going to pull the relevant sections in smaller chunks with line numbers to avoid misquoting it.
exec
/usr/bin/zsh -lc "sed -n '71,150p' docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md | nl -ba -v71" in /home/michael/dev/AgentGovernanceBootstrap
exec
/usr/bin/zsh -lc "sed -n '151,230p' docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md | nl -ba -v151" in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
    71	## Pipeline (file boundary between our side and theirs)
    72	
    73	```
    74	PER (instance, arm):
    75	  1. scaffold instance repo at base_commit            (our harness: scaffold)
    76	  2. overlay governance profile (none/prose/hook-*)   (our harness: overlay_profile)
    77	  3. run our driver (claude/codex) on the problem     (our harness: drivers + hooks)
    78	  4. capture the agent's diff vs base_commit          -> patch text
    79	COLLATE per arm:
    80	  5. write predictions_<arm>.json = [{instance_id, model_patch}]
    81	SCORE (their harness):
    82	  6. swe_bench_pro_eval.py --patch_path predictions_<arm>.json ... --use_local_docker
    83	ANALYZE (our side):
    84	  7. join their resolved results back per arm; joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS;
    85	     reuse invalid-trial accounting (protected-file edits, inert hooks) + telemetry.
    86	```
    87	
    88	The patch-capture in step 4 is `git diff` against `base_commit` in the agent's
    89	workspace, EXCLUDING the overlaid governance files and any hook sentinel (those are
    90	environment, not the agent's fix — same exclusion logic as our changed_files work).
    91	
    92	## What we keep / build / retire
    93	
    94	- **Keep:** governance profiles (none, current-template, hook-gate, hook-guard,
    95	  prose-hooks); joint_pass; invalid-trial accounting; transcript/telemetry capture;
    96	  the claude/codex drivers.
    97	- **Build:** an instance adapter (SWE-bench-Pro instance metadata -> our scaffold +
    98	  a problem prompt for the driver), the patch-capture + predictions-writer, and a thin
    99	  wrapper that shells their `swe_bench_pro_eval.py` and ingests its output.
   100	- **Retire:** synthetic fixtures, `--check-discrimination`, the calibration band,
   101	  the bug-crafting loop. (Left in the repo/history; not used.)
   102	
   103	## Execution substrate (Docker confirmed installing)
   104	
   105	- Hardware: M4 Max, 16 cores, 48GB, 566GB free — ample for a SUBSET. Colima with
   106	  `--cpu 8 --memory 24 --disk 200`.
   107	- **Not all 1000** — image storage alone is multi-TB. Subset of ~20–40 instances.
   108	- **Arch check (open risk):** some base images may be `linux/amd64` (the ansible base
   109	  is dated 2022). Those run under emulation on Apple Silicon — slow, occasionally
   110	  flaky. Step 0 of execution: probe candidate instances' image arch and prefer
   111	  arm64-clean repos for the subset; pass `--platform` explicitly where needed.
   112	
   113	## Subset selection (replaces the calibration gate, on real tasks)
   114	
   115	The calibration question is unchanged but now answered on real tasks: pick instances
   116	where the target model's **ungoverned FAIL_TO_PASS rate is mid-range** — solvable
   117	enough that the agent engages, hard enough that it often fails — so governance has room.
   118	- Probe: run the target model under `none` on a candidate pool (n≈3–5 each), keep
   119	  instances whose ungoverned resolve rate is, say, 20–70%.
   120	- Diversity: 3–4 repos, mixed languages, spanning the difficulty band. ~20 survivors.
   121	- This is real spend but bounded (pool × small n under one arm).
   122	
   123	## Open decisions
   124	
   125	- **G1. Target model(s).** Lean: one primary (cheap-ish frontier — a Claude model or
   126	  GPT-5 codex) for subset selection + the factorial; optionally replicate the headline
   127	  delta on a second. (Owner already chose "both Claude + GPT-5 as arms" for the prior
   128	  plan — carry forward unless cost says otherwise.)
   129	- **G2. Agent scaffold.** Lean: OUR claude/codex drivers + governance overlay (keeps
   130	  the hooks/arms we built; closest to the Cursor↔Claude-Code question). NOT their
   131	  SWE-Agent (our Claude-Code hooks don't ride in it). Risk: our simple one-shot driver
   132	  may resolve far fewer instances than a real agent loop — may need a minimal
   133	  agentic loop (read/edit/run-tests) for the agent to stand a chance on long-horizon
   134	  tasks. This is the biggest unknown; see G3.
   135	- **G3. Driver capability.** SWE-bench Pro is LONG-HORIZON; a single `claude -p` call
   136	  likely resolves very little. Options: (a) rely on Claude Code's own agentic loop
   137	  (it already reads/edits/runs commands within one `-p` invocation) — probably
   138	  sufficient and is the realistic "Claude Code" product; (b) build a minimal
   139	  multi-turn loop. Lean (a) — it is the actual product being measured.
   140	- **G4. n and arms for the real run.** With ~20 instances × 5 arms × n, cost is real.
   141	  Lean: start none vs prose vs prose-hooks (3 arms) on the subset at n=3, expand to the
   142	  full 5 arms only if a signal appears.
   143	- **G5. Network during agent run.** Their scorer can `--block_network`; the agent run
   144	  (dependency install, etc.) may need network. Decide per phase (agent: network on;
   145	  scoring: their default).
   146	
   147	## Risks
   148	
   149	1. **Floor risk (mirror of the ceiling problem):** SWE-bench Pro is HARD; a one-shot
   150	   Claude-Code driver may resolve ~0 under `none`, leaving no room to show improvement

 succeeded in 0ms:
   151	   in the other direction. The subset-selection band (G,  mid-range ungoverned rate)
   152	   guards against this — but if even mid-range instances resolve at ~0, the driver
   153	   (G3) is too weak and must be strengthened before the factorial.
   154	2. **Image arch / build cost:** amd64 emulation could make runs slow/flaky; mitigated
   155	   by arm64-preferred subset.
   156	3. **Patch-capture fidelity:** the diff must exclude governance overlay + sentinels or
   157	   the patch won't apply cleanly in their clean-base container (it would carry AGENTS.md
   158	   etc.). Reuse the changed_files exclusion logic; test that a captured patch applies in
   159	   a fresh checkout.
   160	4. **Their harness assumptions:** confirm predictions JSON schema + sample schema by
   161	   round-tripping `gold_patches.json` through the scorer first (a gold patch must score
   162	   resolved) BEFORE trusting our patches — a cheap correctness anchor.
   163	
   164	## Phased plan (each gated, codex-reviewed)
   165	
   166	- **P0 — substrate up + gold round-trip.** Colima running; pull/build ONE instance
   167	  image; run their scorer on that instance's gold patch and confirm it scores resolved.
   168	  Proves the scorer works locally before we produce any patch. (No governance yet.)
   169	- **P1 — instance adapter + patch capture.** Map a SWE-bench Pro instance to our
   170	  scaffold + problem prompt; run our driver under `none`; capture a clean patch; write
   171	  predictions JSON; score it. Confirm end-to-end on 1–2 instances.
   172	- **P2 — subset selection.** Ungoverned probe over a candidate pool; freeze ~20 mid-band
   173	  instances across diverse repos (arch-checked).
   174	- **P3 — factorial.** none / prose / prose-hooks (G4) over the frozen subset; joint_pass;
   175	  invalid accounting; report deltas with CIs. Expand arms/n if signal.
   176	
   177	## Verification
   178	
   179	- P0 gold round-trip is the substrate correctness anchor.
   180	- P1 patch-applies-in-fresh-checkout test (hermetic-ish: a captured patch must apply on
   181	  a clean base commit).
   182	- Adapter/capture/predictions-writer unit-tested with a fake driver (no model, no
   183	  Docker) for the file-shape contract; the Docker scoring is the live/integration part.
   184	- joint_pass + invalid accounting already tested (Slice C).

exec
/usr/bin/zsh -lc "sed -n '1,70p' docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md | nl -ba -v1" in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
     1	# SWE-bench Pro × governance integration
     2	
     3	Status: DRAFT 2026-06-29, pre-codex-review. Supersedes the synthetic-fixture and
     4	bug-crafting approaches for fixture-sourcing (see
     5	`2026-06-29-adversarial-bugcrafting-loop.md` addendum). No code yet.
     6	
     7	## Empirical update — 2026-06-29 (validated facts; supersedes stale substrate/P0 text below)
     8	
     9	Substrate work ran on the amd64 Linux box `netwatch-01` (NOT the Mac/Colima setup in
    10	"Execution substrate" below — that section is stale; Apple-Silicon amd64-emulation risk is
    11	MOOT here, images run native). Live authority: `.agents/state.md`.
    12	
    13	- **P0 DONE + generalized.** Gold round-trip passes; empty-patch negative control fails
    14	  (metric discriminates). Generalizes 11/11 repos. Gold-resolvability sweep 33/33 ≈ 100%
    15	  (one transient flake, resolved on retry) — gold patches are clean here, so ~all instances
    16	  are usable. ("No code yet" / P0-pending text below is superseded.)
    17	- **Disk sizing (real):** on-disk image footprint 1.6–12 GB each, avg ~4.4 GB (NOT multi-TB
    18	  per image). A 20–40 instance subset ≈ 90–180 GB; 320+ GB free. Subset still wise, numbers
    19	  far smaller than the plan assumed.
    20	- **Integration-contract gotchas the adapter MUST encode:** the shipped scorer targets the
    21	  leaderboard CSV; our jsonl trips two real mismatches — (1) it reads lowercase
    22	  `fail_to_pass`/`pass_to_pass` (jsonl has uppercase); (2) it `eval()`s those expecting a
    23	  *string*, but jsonl `FAIL_TO_PASS` is a list and `PASS_TO_PASS` a string — coerce both to
    24	  string. Predictions accept `model_patch` OR `patch`; always pass `--redo` (per-instance
    25	  output cache silently reuses stale runs).
    26	- **Patch-capture VALIDATED (and bigger than the plan said):** capture = source-only
    27	  `git diff --staged` vs base, EXCLUDING (a) governance overlay/sentinels AND (b) **test
    28	  files** — the scorer overlays gold test files itself (only the LAST line of
    29	  `before_repo_set_cmd`), applied AFTER the agent patch, so agent test edits must be stripped
    30	  (prevents test-gaming). Round-trip proven: gold applied into `/app`, captured, scored resolved.
    31	- **Metric caveat (affects the primary metric):** `PASS_TO_PASS` is EMPTY for 7 of 11 sampled
    32	  instances → `joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS` collapses to FAIL_TO_PASS for those.
    33	  The FuncPass∧SecPass framing must handle frequently-empty SecPass.
    34	- **Transient infra-failure mode (must handle):** at `--num_workers=4`, heavy 5–12 GB
    35	  containers occasionally produce NO output (absent `gold_output.json`) → scored false.
    36	  DISTINGUISHABLE (absent output vs tests-ran-and-failed) and RETRYABLE; retry it, never count
    37	  it as an agent failure.
    38	- **Agent-run mechanism (proven):** host `claude` native binary + subscription credential
    39	  mounted into the instance container, run headless as the non-root `node` user (root refused),
    40	  no API key. Subject = harness+model via SUBSCRIPTION, not API keys.
    41	- **NEW GATE (open):** launching the unsupervised bypass-permissions agent — the eval's core —
    42	  is blocked by the running session's safety classifier; needs an owner-sanctioned launch path
    43	  (settings permission rule / owner-run driver / non-auto-mode).
    44	- **NEW design lever (owner):** harnesses span capability — agy/grok (weaker) vs codex/claude
    45	  (stronger). Weaker agents plausibly have more headroom for governance to help; consider
    46	  spanning capability deliberately rather than a single primary frontier (revisits G1).
    47	
    48	## Goal
    49	
    50	Measure whether our governance product (prose / hooks / both) makes a frontier agent
    51	reliably better at **real, hard, frontier-resistant** software tasks — using ScaleAI
    52	SWE-bench Pro (`/Users/michael/Dev/SWE-bench_Pro-os`, 1000 instances, 11 repos) as the
    53	fixture source instead of synthetic bugs that frontier models trivially solved.
    54	
    55	Primary metric unchanged: **joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS** (their scorer's
    56	two dimensions ARE our FuncPass ∧ SecPass). A governance arm "wins" by raising the
    57	fraction of instances resolved (both the target test passes AND no regression).
    58	
    59	## The integration contract (verified by reading swe_bench_pro_eval.py)
    60	
    61	Their eval is a pure function over a **predictions file**:
    62	`swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
    63	--output_dir <out> [--use_local_docker]`. The predictions JSON is
    64	`[{instance_id, model_patch}]` (they ship `gold_patches.json` as the reference shape).
    65	For each instance it: builds/pulls the instance Docker image, resets to `base_commit`,
    66	applies `model_patch`, runs the test command, scores FAIL_TO_PASS + PASS_TO_PASS.
    67	
    68	**Decoupling:** the agent that produces the patch is entirely separate from the scorer.
    69	Governance lives 100% in patch *production*; the scorer never sees our harness.
    70	

exec
/usr/bin/zsh -lc "sed -n '29,125p' .agents/state.md | nl -ba -v29" in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
    29	## Next
    30	
    31	- 2026-06-29 **Keystone recon DONE — one remaining GATE: a sanctioned way to launch the
    32	  autonomous agent.** Proven on netwatch-01: the host `claude` (native amd64 ELF v2.1.195) binary
    33	  + `~/.claude/.credentials.json`, MOUNTED into an instance container, run **headless with
    34	  subscription auth and NO API key** (a "reply PONG" test returned PONG; claude auto-wrote
    35	  `~/.claude.json`, no onboarding block). Containers have node18 + working network (api.anthropic.com
    36	  reachable) + the repo at `/app` checked out at base_commit. **Scoring contract mapped** from
    37	  `swe_bench_pro_eval.py:114-126`: entryscript does `cd /app` → `git reset --hard base` →
    38	  `git checkout base` → `git apply /workspace/patch.diff` → then overlays gold test files (ONLY the
    39	  LAST line of `before_repo_set_cmd`) → runs run_script + parser. ⇒ the agent must submit a
    40	  **SOURCE-ONLY diff vs base_commit**; P1 strips test files (scoring overlays gold tests regardless,
    41	  but stripping blocks test-gaming).
    42	  **GATE (needs owner):** the eval's core is an unsupervised, permission-bypassed coding agent run
    43	  in-container. This Claude Code session's auto-mode classifier blocks the agent (me) from spawning
    44	  `claude -p --permission-mode bypassPermissions` ([Create Unsafe Agents]) — a legitimate guard;
    45	  do NOT evade it (no hiding the spawn inside a wrapper script). Sanctioned options: (1) owner adds
    46	  a scoped Bash permission rule allowing the eval's bypass-agent invocation, so this session can
    47	  develop+run it autonomously; (2) owner runs the eval driver themselves; (3) run the eval in a
    48	  non-auto-mode session.
    49	  **UPDATE 2026-06-29 (capability fully proven; only the sanction remains):** in-container claude
    50	  refuses bypass as ROOT, but runs fine as the image's non-root `node` user (uid 1000) — credential
    51	  copied to `/home/node/.claude/`, `/app` chowned to node. A trivial bypass edit
    52	  (`AGENT_PROOF.txt`) succeeded → the headless autonomous-edit capability works end to end. BUT the
    53	  classifier then blocked the REAL autonomous source-editing run, explicitly reading the owner's
    54	  "invoke … to run tests or review plans" grant as NOT covering an unsupervised bypass source-editing
    55	  agent. So the eval's core still needs an explicit sanctioned launch: (1) owner adds a Bash
    56	  permission rule (e.g. allow `docker exec`) so this session drives it; (2) owner runs the driver
    57	  themselves (spawns happen in their process, not via this session's classifier); or (3) non-auto-mode
    58	  session. Do NOT add such a rule to repo/owner settings unilaterally — it is a security-relevant
    59	  roadblock; owner decides. Everything UP TO the agent spawn is buildable/validatable now using the
    60	  gold patch as a stand-in agent (plain git/scorer calls, not gated).
    61	  **VALIDATED 2026-06-29:** capture round-trip works — gold applied into `/app` as a stand-in agent
    62	  output, captured a SOURCE-ONLY diff via `git add -A && git diff --staged -- . ':(exclude)<testfiles>'`,
    63	  fed to the scorer as a mock prediction → resolved=true. So container-working-tree → source-only
    64	  capture → scorer is proven; only the sanctioned autonomous agent spawn remains. (Note: after
    65	  chowning `/app` to node, root git needs `git config --global --add safe.directory /app`.)
    66	
    67	- 2026-06-29 **Gold-resolvability sweep (3 instances/repo, 33 total): 33/33 ≈ 100% resolvable.**
    68	  One openlibrary instance scored false on the first parallel pass but resolved on isolated retry
    69	  (6 PASSED) — so the dataset's gold patches are clean on this substrate; no instance needed
    70	  exclusion in this sample.
    71	  **CRITICAL methodological finding — transient infra failure under parallelism:** at
    72	  `--num_workers=4`, heavy containers occasionally produce **NO output at all** (the instance
    73	  output dir has the workspace but no `gold_output.json` / no stdout/stderr logs), which the scorer
    74	  counts as `resolved=false`. This is DISTINGUISHABLE from a real test failure (empty/absent output
    75	  vs. `gold_output.json` present with FAILED tests) and is RETRYABLE. **P1 MUST: (a) detect the
    76	  "no output produced" case and retry it, (b) never count an infra-empty run as an agent failure,
    77	  (c) keep parallelism modest for heavy repos (Go/webclients images are 5–12 GB).** Counting a
    78	  transient infra flake as the agent failing would silently corrupt the governance-effect measurement.
    79	
    80	- 2026-06-29 **P0 DONE — substrate PROVEN on the amd64 Linux box; the blocker below is CLEARED.**
    81	  Box: `netwatch-01` (CachyOS, x86_64, native amd64 — no QEMU), Docker engine active, system
    82	  `python3` is **3.14** (parses the tests), SWE-bench Pro checkout is at
    83	  **`/home/michael/dev/SWE-bench_Pro-os`** on this box (NOT the Mac `/Users/...` path the block
    84	  below names). P0 gold round-trip on instance
    85	  `instance_NodeBB__NodeBB-04998908ba6721d64eba79ae3b65a351dcfbc5b5-vnan`: gold patch scores
    86	  **resolved=true** (300 PASSED/0 FAILED, clean `--redo` container run ~11s); empty-patch negative
    87	  control scores **resolved=false** — so the metric genuinely discriminates. Artifacts in session
    88	  scratchpad, not committed.
    89	
    90	- 2026-06-29 **Multi-repo gold round-trip: 11/11 PASS — substrate generalizes across ALL 11 repos**
    91	  (one instance each: NodeBB, qutebrowser, ansible, openlibrary, element-web, navidrome, teleport,
    92	  vuls, flipt, tutanota, webclients; JS/Python/Go/TS). Every gold patch scores resolved=true with
    93	  non-vacuous PASSED counts (each ≥ its F2P+P2P). Done via a reusable adapter
    94	  (`scratchpad/adapter.py`, the P1 seed) that encodes the two gotchas below.
    95	  **Finding (metric design):** `PASS_TO_PASS` is EMPTY for 7 of the 11 sampled instances
    96	  (element-web, navidrome, teleport, vuls, flipt, tutanota, webclients) — so the planned SecPass
    97	  dimension is frequently absent and `joint_pass` collapses to FuncPass there. The plan's
    98	  FuncPass∧SecPass framing must account for SecPass being empty on many instances.
    99	  **Disk sizing (corrected):** on-disk image footprint is **1.6 GB (ansible) → 12 GB (webclients),
   100	  avg ~4.4 GB**; 11 images = 48 GB on disk; 367 GB free. NOTE the earlier "807 MiB" was the
   101	  *compressed pull* size, not on-disk — NodeBB is 3.18 GB unpacked. A ~20-instance subset is
   102	  roughly 50–130 GB on disk depending on repo mix (not "<20GB").
   103	
   104	  **Adapter gotchas the P1 instance-adapter MUST encode** (the shipped `swe_bench_pro_eval.py` was
   105	  written for the leaderboard CSV; our jsonl trips two real mismatches — worked around by deriving
   106	  a per-instance sample file, NOT by editing the third-party script):
   107	  (1) **case** — jsonl has `FAIL_TO_PASS`/`PASS_TO_PASS`, scorer reads lowercase
   108	  `fail_to_pass`/`pass_to_pass`; must alias. (2) **type** — scorer does `eval(field)` expecting a
   109	  *string*, but in the jsonl `FAIL_TO_PASS` is a native JSON **list** while `PASS_TO_PASS` is a
   110	  **string** (inconsistent source data); coerce both to string form (survives the pandas
   111	  `read_json` round-trip). Operational: `run_scripts/` (1000 dirs) is present and `instance_id`
   112	  matches dir names exactly; image = `get_dockerhub_image_uri(uid, 'jefzda', repo)`; **always pass
   113	  `--redo`** or the per-instance output cache silently reuses a stale run.
   114	
   115	  **Next:** architecture decision, then P1 adapter, P2 subset selection.
   116	  **CORRECTION (owner, 2026-06-29): there are NO API keys in this eval.** The subject under test is
   117	  a **(harness + model)** pair authenticated by a **subscription login** (e.g. Claude Code on a
   118	  Claude subscription, Codex on a ChatGPT subscription) — not API access to a model. So "Option A
   119	  needs API keys" was wrong; Option A's only setup cost is doing the harness's **subscription login
   120	  on netwatch-01**. (Assumption pending owner confirmation, not yet a settled decision: the agent
   121	  should run *inside* the instance container so it can run tests/verify while solving — both because
   122	  the containers are amd64-only/native here and because governance is largely verification
   123	  discipline; that points to running the harness here = Option A.)
   124	
   125	- 2026-06-29 **HANDOFF (superseded by the P0 entry above for substrate status; pivot context still

codex
I have enough to assess the core design. I’m checking the older state handoff only to separate stale plan text from the currently validated facts.
exec
/usr/bin/zsh -lc "sed -n '125,184p' .agents/state.md | nl -ba -v125" in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
   125	- 2026-06-29 **HANDOFF (superseded by the P0 entry above for substrate status; pivot context still
   126	  valid). Eval workstream pivoted to SWE-bench Pro.** Read the P0 entry first, then the two plans
   127	  named below.
   128	
   129	  **Where we are:** the governance-efficacy eval's *measurement instrument* is fully built and
   130	  pushed (Phase 0 hardening + the Phase-1 fixture/arms machinery — see the dated entries below).
   131	  But the **synthetic-fixture approach is DEAD**: the frontier-calibration run (Slice F) showed
   132	  Claude clean-passes all 5 hand-built fixtures 10/10 and GPT-5 the same on the 2 it finished —
   133	  zero naive traps, every fixture drops as "too easy" (a model can't invent a bug that stumps
   134	  itself). That result is the whole reason for the pivot; do not retry synthetic fixtures.
   135	
   136	  **The pivot (owner-directed):** use **ScaleAI SWE-bench Pro** as the fixture source. Full local
   137	  checkout at **`/Users/michael/Dev/SWE-bench_Pro-os`** (731 real instances in
   138	  `helper_code/sweap_eval_full_v2.jsonl`, 11 repos, multi-language, frontier-resistant). Mapping:
   139	  **FAIL_TO_PASS = our FuncPass, PASS_TO_PASS = our SecPass/regression guard**, so our existing
   140	  **`joint_pass = FAIL_TO_PASS ∧ PASS_TO_PASS`** metric and invalid-trial accounting apply
   141	  unchanged. Their `swe_bench_pro_eval.py` is a pure function `(predictions.json, sample) →
   142	  resolved` that scores a patch inside a per-instance Docker image — agent and scorer are
   143	  decoupled by a predictions-JSON file boundary. Integration plan (DRAFT, pre-codex-review):
   144	  **`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`** (pipeline,
   145	  phases P0–P3, open decisions G1–G5). Background + why-the-synthetic-approach-died:
   146	  **`docs/superpowers/plans/2026-06-29-adversarial-bugcrafting-loop.md`** (its SWE-bench Pro
   147	  addendum supersedes it; the crafting loop is the documented fallback only).
   148	
   149	  **THE BLOCKER — CLEARED 2026-06-29 (see P0 entry above).** It was: SWE-bench Pro instance images
   150	  are **amd64-only** and their **test runtimes segfault under Rosetta/QEMU on Apple Silicon**
   151	  (verified: `python3 --version` segfaulted inside `jefzda/sweap-images:ansible...` on the Mac).
   152	  Resolution: the eval now runs on the amd64 Linux box `netwatch-01` where images run natively;
   153	  P0 gold round-trip passed there. The Mac Colima path is abandoned for scoring.
   154	
   155	  **Public images:** `jefzda/sweap-images` on Docker Hub (the metadata jsonl points at a *private*
   156	  ScaleAI ECR; ignore that). Derive the pull tag with `helper_code/image_uri.get_dockerhub_image_uri(
   157	  instance_id, 'jefzda', repo)` (it truncates tags >128 chars). Score with
   158	  `swe_bench_pro_eval.py --raw_sample_path <subset.jsonl> --patch_path <predictions.json>
   159	  --dockerhub_username jefzda --use_local_docker`.
   160	
   161	  **NEXT ACTIONS on the Linux box (in order):**
   162	  1. **P0 — gold round-trip (no governance yet):** on the amd64 box with Docker, pull ONE instance
   163	     image, run `swe_bench_pro_eval.py` on that instance's **gold `patch`** (shipped in the jsonl)
   164	     and confirm it scores **resolved**. This proves the substrate before producing any agent patch.
   165	  2. Decide the architecture (open in the plan): **Option A** = agent runs + scores all on the box;
   166	     **Option B** = governed agent runs on the Mac (our harness/hooks/keys already work), patches
   167	     copied to the box which only scores. Option B needs local `git clone <repo>@base_commit` for the
   168	     agent's workspace; Option A needs model API keys + our harness on the box.
   169	  3. Then P1 (instance adapter + clean patch capture — exclude governance overlay/sentinels from the
   170	     diff), P2 (subset selection: ungoverned FAIL_TO_PASS probe, keep ~20 mid-band instances across
   171	     diverse repos), P3 (the none/prose/prose-hooks factorial). Codex-review the integration plan to
   172	     convergence before building (the workstream's standing discipline).
   173	
   174	  **Biggest risk to watch (in the plan):** floor mirror of the earlier ceiling — SWE-bench Pro is
   175	  HARD, so a one-shot Claude-Code/codex driver may resolve ~0 ungoverned, leaving no room to show
   176	  improvement. Subset selection (mid-range ungoverned rate) guards this; if even mid-band instances
   177	  resolve at ~0 the driver (G3) needs a real agentic loop before the factorial.
   178	
   179	  **What's reusable as-is:** governance profiles (`evals/governance_profiles/`: none,
   180	  current-template, hook-gate, hook-guard, prose-hooks), `joint_pass`+invalid accounting in
   181	  `evals/aggregate.py`, the claude/codex drivers in `tools/drivers.py`, `evals/calibrate.py`
   182	  (its classify/Wilson logic still scores an ungoverned probe). **Retire/ignore for SWE-bench Pro:**
   183	  the 5 synthetic fixtures, `--check-discrimination`, the calibration *band* gate as a fixture
   184	  source. **Test interpreter: homebrew `python3` (3.14)** — system 3.9 can't parse the tests.

exec
/usr/bin/zsh -lc 'git status --short' in /home/michael/dev/AgentGovernanceBootstrap
 succeeded in 0ms:
codex
I read both files and did not write anything.

**Highest-Impact Critique**

1. The core causal design is under-specified. The plan says every `(instance, arm)` gets scaffolded, overlaid, run, patched, and scored ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:71>)), but it does not define randomization, arm order, fresh homes/configs, resource caps, retry rules, or analysis unit. Without those, subscription-model drift, rate limits, local CLI state, model nondeterminism, and Docker load can masquerade as governance effects. Run all arms for an instance as a randomized block, isolate per-run home/config/cache except credentials, record CLI/model versions, and analyze paired by instance.

2. The subset-selection rule is likely biased. The plan proposes selecting instances where ungoverned `FAIL_TO_PASS` rate is 20-70% from only `n≈3-5` probes ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:113>)). That conditions on noisy baseline outcomes and selects for regression-to-mean. Also, selection uses `FAIL_TO_PASS`, while the stated primary metric is joint resolved. Select on official `resolved`, or explicitly make the estimand “mid-band F2P instances,” and do not reuse screening runs as confirmatory evidence.

3. The `PASS_TO_PASS` emptiness breaks the advertised metric interpretation. The empirical update says `PASS_TO_PASS` is empty in 7/11 sampled repos/instances and `joint_pass` collapses to `FAIL_TO_PASS` there ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:31>), [state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:95>)). So this is not generally measuring `FuncPass ∧ SecPass`; for most sampled instances it is only “bug tests pass.” Keep official `resolved` as primary if desired, but report P2P-empty and P2P-nonempty strata separately. If regression-safety is central, require a meaningful fraction of nonempty `PASS_TO_PASS` instances.

4. Floor risk remains the main existential risk. The plan recognizes SWE-bench Pro may yield ~0 solves with a one-shot driver ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:149>), [state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:174>)), but the proposed guard is too weak. Before factorial, run a floor pilot with the strongest intended harness, inside the real container, with the final time/tool budget. Gate P3 on observed baseline solves: e.g. at least 5-8 ungoverned resolved successes in the frozen-size equivalent. If not, improve the driver before testing governance.

5. The statistical power is poor for 20-40 instances × 3 arms. With binary outcomes, 20-40 paired instances can only detect large effects unless treatment flips many of the exact same baseline failures. Independent-proportion intuition: detecting 30 percentage points needs roughly 40-ish per arm; detecting 20 points needs roughly 90-100 per arm. Paired analysis helps, but only discordant instances matter. Predeclare one primary contrast, probably `prose-hooks` vs `none`, and treat other contrasts as exploratory unless you increase N or repeat trials.

6. Invalid-trial accounting can bias the causal estimate. The plan says invalid trials include protected-file edits, inert hooks, and telemetry ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:84>)). Infra-empty runs should be retried/excluded arm-blind, as the state correctly notes ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:71>)). But post-treatment failures such as hook blocks, governance-file edits, or inert treatment delivery should not simply disappear from the primary denominator. Use intention-to-treat as primary; per-protocol can be secondary.

7. Capability-spectrum work is exploratory unless sharply separated. The empirical update suggests weaker `agy/grok` may have more headroom and stronger `codex/claude` may be frontier targets ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:44>)). That is plausible but not guaranteed: weak agents may also be less able to read, follow, or exploit governance. Use a capability pilot to choose one primary harness with nonzero-but-not-ceiling baseline. If you test multiple harnesses, analyze governance × harness interaction and do not pool them.

8. Injecting governance into arbitrary OSS repos is a major external-validity confound. The treatment is not just “governance”; it changes prompt-visible files, root repo instructions, hook behavior, token load, and possibly command permissions. Some repos may already have guidance files. Some harnesses auto-read `AGENTS.md`; others may not. The result will estimate “synthetic injected governance under this harness,” not necessarily “real maintained repo governance.” Add a placebo-prose arm with comparable token/context load, scan for existing governance files, and define whether generated repo-specific facts are allowed treatment information.

9. The plan document itself is too stale/malformed to build from safely. It says “No code yet” despite P0 being done ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:3>)), still names the Mac path and 1000 instances ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:50>)), and retains stale Colima/arm64 risk text ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:154>)). Also, `.agents/state.md` says there is an owner gate for launching the actual autonomous agent ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:42>)) but later says “Blockers: None recorded” ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:230>)). That inconsistency should be fixed before implementation.

Concrete minimum before P3: freeze the estimand, use official `resolved` as primary, stratify P2P-empty, run an arm-blind retry policy for infra-empty, randomize paired arm order per instance, isolate harness state, predeclare one primary contrast, and require a floor pilot demonstrating enough ungoverned solves to make an effect observable.
tokens used
59,711
I read both files and did not write anything.

**Highest-Impact Critique**

1. The core causal design is under-specified. The plan says every `(instance, arm)` gets scaffolded, overlaid, run, patched, and scored ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:71>)), but it does not define randomization, arm order, fresh homes/configs, resource caps, retry rules, or analysis unit. Without those, subscription-model drift, rate limits, local CLI state, model nondeterminism, and Docker load can masquerade as governance effects. Run all arms for an instance as a randomized block, isolate per-run home/config/cache except credentials, record CLI/model versions, and analyze paired by instance.

2. The subset-selection rule is likely biased. The plan proposes selecting instances where ungoverned `FAIL_TO_PASS` rate is 20-70% from only `n≈3-5` probes ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:113>)). That conditions on noisy baseline outcomes and selects for regression-to-mean. Also, selection uses `FAIL_TO_PASS`, while the stated primary metric is joint resolved. Select on official `resolved`, or explicitly make the estimand “mid-band F2P instances,” and do not reuse screening runs as confirmatory evidence.

3. The `PASS_TO_PASS` emptiness breaks the advertised metric interpretation. The empirical update says `PASS_TO_PASS` is empty in 7/11 sampled repos/instances and `joint_pass` collapses to `FAIL_TO_PASS` there ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:31>), [state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:95>)). So this is not generally measuring `FuncPass ∧ SecPass`; for most sampled instances it is only “bug tests pass.” Keep official `resolved` as primary if desired, but report P2P-empty and P2P-nonempty strata separately. If regression-safety is central, require a meaningful fraction of nonempty `PASS_TO_PASS` instances.

4. Floor risk remains the main existential risk. The plan recognizes SWE-bench Pro may yield ~0 solves with a one-shot driver ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:149>), [state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:174>)), but the proposed guard is too weak. Before factorial, run a floor pilot with the strongest intended harness, inside the real container, with the final time/tool budget. Gate P3 on observed baseline solves: e.g. at least 5-8 ungoverned resolved successes in the frozen-size equivalent. If not, improve the driver before testing governance.

5. The statistical power is poor for 20-40 instances × 3 arms. With binary outcomes, 20-40 paired instances can only detect large effects unless treatment flips many of the exact same baseline failures. Independent-proportion intuition: detecting 30 percentage points needs roughly 40-ish per arm; detecting 20 points needs roughly 90-100 per arm. Paired analysis helps, but only discordant instances matter. Predeclare one primary contrast, probably `prose-hooks` vs `none`, and treat other contrasts as exploratory unless you increase N or repeat trials.

6. Invalid-trial accounting can bias the causal estimate. The plan says invalid trials include protected-file edits, inert hooks, and telemetry ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:84>)). Infra-empty runs should be retried/excluded arm-blind, as the state correctly notes ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:71>)). But post-treatment failures such as hook blocks, governance-file edits, or inert treatment delivery should not simply disappear from the primary denominator. Use intention-to-treat as primary; per-protocol can be secondary.

7. Capability-spectrum work is exploratory unless sharply separated. The empirical update suggests weaker `agy/grok` may have more headroom and stronger `codex/claude` may be frontier targets ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:44>)). That is plausible but not guaranteed: weak agents may also be less able to read, follow, or exploit governance. Use a capability pilot to choose one primary harness with nonzero-but-not-ceiling baseline. If you test multiple harnesses, analyze governance × harness interaction and do not pool them.

8. Injecting governance into arbitrary OSS repos is a major external-validity confound. The treatment is not just “governance”; it changes prompt-visible files, root repo instructions, hook behavior, token load, and possibly command permissions. Some repos may already have guidance files. Some harnesses auto-read `AGENTS.md`; others may not. The result will estimate “synthetic injected governance under this harness,” not necessarily “real maintained repo governance.” Add a placebo-prose arm with comparable token/context load, scan for existing governance files, and define whether generated repo-specific facts are allowed treatment information.

9. The plan document itself is too stale/malformed to build from safely. It says “No code yet” despite P0 being done ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:3>)), still names the Mac path and 1000 instances ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:50>)), and retains stale Colima/arm64 risk text ([plan](</home/michael/dev/AgentGovernanceBootstrap/docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md:154>)). Also, `.agents/state.md` says there is an owner gate for launching the actual autonomous agent ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:42>)) but later says “Blockers: None recorded” ([state](</home/michael/dev/AgentGovernanceBootstrap/.agents/state.md:230>)). That inconsistency should be fixed before implementation.

Concrete minimum before P3: freeze the estimand, use official `resolved` as primary, stratify P2P-empty, run an arm-blind retry policy for infra-empty, randomize paired arm order per instance, isolate harness state, predeclare one primary contrast, and require a floor pilot demonstrating enough ungoverned solves to make an effect observable.
