# State archive

Landed or superseded `.agents/state.md` entries, rotated here verbatim at
handoff per the state-rotation rule (first applied 2026-07-08). Newest
rotation first; entries are never edited after rotation.

## Rotated 2026-07-08 — closed eval workstream's `## Next` history

(Superseded by the CURRENT FOCUS block of 2026-07-02: model testing and
end-to-end trials are closed; the evals workstream's files were deleted
from the tree 2026-07-08 — full record in git history.)

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
  **PILOT RAN, but prose/hooks arms are INVALID (flagged 2026-06-30).** The sizing pilot
  completed (8 instances × 4 arms × 3 reps = 96 cells) and its results are committed at
  `evals/swebench-pro/opus-pilot-results.md` — BUT `arms4.py` injected the full
  `current-template` AGENTS.md as the prose arm, which the plan (Addendum b) deliberately
  excludes. The prose / `prose+hooks` columns are wrong-arm junk (and the hooks were
  re-ground/tripwire, not the `hook-gate`/`hook-guard` the plan specifies); `none` /
  placebo and the band-selection lesson stand. `PRE-REGISTRATION.md` §3 is corrected; the
  driver prototype still encodes the wrong arm (warned in its README). **Re-run the sizing
  pilot with `task-prose` / `task-prose-hooks` before reading any prose/hooks result.**
  KEYSTONES (in PRE-REGISTRATION): governance loads only via CLAUDE.md (bare AGENTS.md
  inert; `@AGENTS.md` import works); the arms' hooks — `hook-guard` (PreToolUse) and
  `hook-gate` (Stop) — DO fire in one-shot runs (the re-ground hook, which needs
  compaction, is not a test arm).
  **ROUTING (owner-decided 2026-06-29):** in-container agents route through the owner's
  **headroom** token-compression proxy (`ANTHROPIC_BASE_URL=http://10.1.10.221:8787`,
  passed via `docker exec -e`; PONG-verified through the proxy). Validity-safe and the
  more faithful subject: headroom compresses ONLY the newest user msg + latest tool
  result and NEVER mutates the system prompt — and Claude Code delivers CLAUDE.md/
  @AGENTS.md governance via the system prompt, so the treatment is uncompressed;
  compression is uniform across arms (constant factor, contrast preserved) and is a
  compressor not a response-cache (replicates stay independent). The first pilot launch
  was direct-to-Anthropic and was KILLED + relaunched so all 96 cells share one routing
  path (mixed routing would confound). Absolute rates reflect claude+headroom (the
  owner's real setup), which is intended.
  **CODEX secondary harness — keystones validated, but first pilot INVALID
  (2026-06-29).** Codex runs headless in-container via its native musl binary
  (`@openai/codex-linux-x64/.../bin/codex exec --dangerously-bypass-approvals-and-sandbox
  --dangerously-bypass-hook-trust --skip-git-repo-check -C /app`, prompt via stdin),
  subscription auth (`~/.codex/auth.json`, no API key), model gpt-5.5 at xhigh via the
  same headroom provider (`config.toml`). Validated: PONG, native binary, and codex
  loads `/app/AGENTS.md` natively (so governance injects as AGENTS.md directly, no
  CLAUDE.md shim; placebo = AGENTS.md-sized irrelevant prose). Driver
  `arms4_codex.py` (capture-vs-base + retry + preflight PONG). The 96-cell pilot
  COMPLETED but is unusable: **codex hit ITS OWN usage limit mid-run** (resets
  ~10:45 PM) → 69/96 empty (≈57 usage-limit + 12 proxy-blip neterr), only 27 real
  attempts, 0 resolved across all arms (not interpretable). LESSONS: (1) gpt-5.5 xhigh
  is far too token-heavy for a 96-cell window — chunk codex runs or lower effort;
  (2) the driver's invalid-cell detector must add the usage-limit signature
  ("hit your usage limit") as a distinct QUOTA-invalid flag, not counted as agent
  failure. Both Claude and codex caps were exhausted 2026-06-29; owner added Claude
  usage credits.

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
