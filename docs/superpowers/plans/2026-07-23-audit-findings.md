# 2026-07-23 decisions-as-claims audit — findings

Status: Pass 1 and Pass 2 complete. STALE and CONTRADICTED verdicts route to the owner one at a time (problem, proposed change, cost/risk, recommendation); silence authorizes nothing. HOLDS-UNSHIPPED / HOLDS-UNENFORCED fixes are queued in the Fix Queue section and land only behind a per-item owner go. No implementation has landed from this file.

Method: re-run of the 2026-07-22 holistic review with rulings as claims, per `docs/superpowers/plans/2026-07-23-decisions-as-claims-audit.md`. Every entry under `## Decisions` in `.agents/decisions.md` was audited against current repo evidence (file contents, tests, git history), not against the ruling's own prose; "Landed:" and "Canonical home:" claims were verified, not trusted. The `## Open Decisions` queue is empty ("queue emptied 2026-07-12", `.agents/decisions.md:1259`), so no open entries were audited. Baseline at audit time: 161/161 tests green (`/opt/homebrew/bin/python3.14 -m unittest discover -s tests -p "test_*.py"`). Archived entries in `docs/history/decisions-archive.md` were out of scope.

Verdict totals across 41 audited entries: HOLDS 16, HOLDS-UNENFORCED 20, HOLDS-UNSHIPPED 2, STALE 2, CONTRADICTED 1.

Enforcement baseline for the blocks below: the repo's hard enforcement guards *artifact integrity*, not *agent behavior* — `templates/hooks/claude/protect-governance.py` blocks edits to installed artifacts (kept in lockstep with the manifest by `tests/test_templates.py::test_protected_set_matches_the_shipped_targets`), and `tools/refresh.py` converges governed repos to the shipped set. Prose-pin phrase tests were deliberately retired 2026-07-08 (`tests/test_templates.py:4-6`: "template content is governed by the no-rule-without-provenance discipline, not CI grep"). HOLDS-UNENFORCED on a behavioral rule therefore means "prose-governed by deliberate design," not an automatic defect; the PROSE/ENFORCED table in Pass 2 calls out only the gaps worth new tooling.

## Pass 1 — per-ruling blocks

### 2026-07-23 — A handoff ends by committing its own records
- EVIDENCE: Holds. `templates/AGENTS.template.md:55` ends the handoff bullet with the bookkeeping-commit sentence; landed in `680bac9`, tightened in `ad5145f`. Caveat: this repo's installed `AGENTS.md:55` lacks the sentence — the documented owner-self-refresh lag (`.agents/repo-guidance.md:81-89`), not drift.
- SHIPPED: Yes — replace-whole into downstream `AGENTS.md` via `tools/shipped-set.json`.
- ENFORCED: Unenforced; nothing detects an uncommitted handoff record.
- TODAY: Same — the record only functions through git, so the commit is part of the save.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: no code change; owner self-refresh at leisure.

### 2026-07-22 — Paperwork follows technical work
- EVIDENCE: Partially. "Applied same day: issues #5–#8 closed" matches fix commits at HEAD (`a80a2c7`, `17980c1`, `7883891`, `aefb080`). But grep of `templates/` for `paperwork|tracker|bookkeeping|close the issue` finds only the handoff sentence (`templates/AGENTS.template.md:55`); the general rule — close tracker issues, sync state, no owner ask for completion bookkeeping — exists only in `.agents/decisions.md:64-86`.
- SHIPPED: Only its handoff consequence ships (the 2026-07-23 ruling itself records that the paperwork ruling "lived only in this repo's decisions file, which downstream agents never see"). The general form is local-only prose.
- ENFORCED: Unenforced.
- TODAY: Same rule, but ship the generalized clause ("closing the record of already-approved, verified work needs no fresh ask") once, not only its handoff instance.
- VERDICT: HOLDS-UNSHIPPED. PROPOSED: add one generalized completion-bookkeeping clause to `templates/AGENTS.template.md`, or amend the entry to record deliberate local scope (F4).

### 2026-07-22 — Owner communication is a per-repo tunable level (1–5)
- EVIDENCE: Holds; all "Landed" claims verified. `templates/comms-policy.template.md:1` carries `<!-- comms-level: 3 -->` with the five level definitions; this repo's `.agents/comms-policy.md:1` is level 2. Seeding `procedures/bootstrap.md:174`; ask-never-prefill `templates/approval-summary.template.md:57-58,116`; named-profile section removed from `templates/repo-guidance.template.md`; register deferral at `templates/AGENTS.template.md:58,83`. Commits `933512e`, `17fb23f`, `d4db44a`.
- SHIPPED: Yes — deliberately not in `shipped-set.json`, mirroring the push-policy precedent (bootstrap-seeded, repo-owned thereafter). Minor doc gap: `tools/refresh.py:33-34`'s repo-owned list omits `comms-policy.md`.
- ENFORCED: Unenforced; nothing parses the marker (zero `comms` hits in `tools/`/`tests/`; contrast the push-policy preflight at `tools/refresh.py:745`).
- TODAY: Same design; add a marker-format lint mirroring the push-policy preflight.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: marker lint + docstring fix (F10).

### 2026-07-22 — A response never ends on a bare blocker (R2)
- EVIDENCE: Holds. `templates/AGENTS.template.md:83` carries the next-item + proposed-action rule; the same change (`8a61c72`) reworded Final Response to open summary-first, as claimed.
- SHIPPED: Yes, in `## Final Response`. ENFORCED: Unenforced — a response-shape rule no test can catch.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: none; accept as prose governance (no cheap mechanical check exists).

### 2026-07-22 — Issue-queue items one at a time behind an explicit owner go (R1)
- EVIDENCE: Holds locally. `.agents/repo-guidance.md:14-16` carries the per-item Owner Gates ask rule; receipt artifacts verified (tag `backup-2026-07-22-governance-edits`, commit `881e63b`).
- SHIPPED: Local by design for the issue-queue core. The claimed generalization is half-shipped: `templates/AGENTS.template.md:78` carries the one-item-per-commit half; the per-item-owner-go half lives only in local prose.
- ENFORCED: Unenforced.
- TODAY: Same split; ship the per-item-go half only if the fleet runs owner-gated queues too.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: none required; optionally note the owner-go half is intentionally unshipped.

### 2026-07-22 — State and governance files kept current by the working agent (R3)
- EVIDENCE: Holds. `templates/AGENTS.template.md:25` carries the kept-current-as-work-lands wording; commit `17980c1` matches the "Landed" claim exactly.
- SHIPPED: Yes, in Universal Invariants. ENFORCED: Unenforced for the behavior (refresh's state.md lint only flags dead paths, `tests/test_refresh.py:814`).
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: none; accept as prose governance.

### 2026-07-22 — Owner completion report is the go for the next defined step (issue #8)
- EVIDENCE: Holds; both "Landed" claims verified. `templates/AGENTS.template.md:7` carries the completion-report clause with the three stops (commit `a80a2c7`); the dated amendment on the 2026-06-10 answer-with-words entry exists at `.agents/decisions.md:1020`.
- SHIPPED: Yes, in Prime Invariants. ENFORCED: Unenforced.
- TODAY: Same — it threads both incident failure modes (ritual-go demand vs. stretched batch authority).
- VERDICT: HOLDS-UNENFORCED. PROPOSED: none; accept as prose governance.

### 2026-07-19 — Model slugs get one committed home: fleet-global `.agents/model-map.json`
- EVIDENCE: Supported. `.agents/model-map.json` exists and matches the ruled seeds (`sol`→`gpt-5.6-sol`, `terra`→`gpt-5.6-terra`, v1). Shipped mechanics: `templates/playbooks/codereview.md:259-314` (map section, fetch contract, grammar), `templates/playbooks/harness-update.md:7-9` (sole write path), `templates/commands/claude/review.md:6-9` (pure alias, F6). Commits `dac2c2c`, `1dcea6a`, `d412438`, `d989054`. Two wrinkles: (a) the shipped cache schema at `codereview.md:147-152` still carries `"model": "<id>"` per tier and L245-246 still resolves a tier from the machine-local cache, contradicting L267-270 (slug text reads from the map); (b) the live gitignored `.agents/review/harnesses.local.json` still pins slugs and predates the ruling.
- SHIPPED: Rule text yes. The map file itself is not in `shipped-set.json`; by design it distributes via the documented raw-`master` fetch in shipped playbook text.
- ENFORCED: Yes — `tests/test_model_map.py::test_committed_map_passes_fetch_contract`, `::test_committed_map_within_size_cap`, `tests/test_templates.py::test_shipped_template_text_names_no_concrete_model_ids` (denylist at `docs/harness-capabilities.md:105-118`), `::test_codereview_carries_tier_semantics`. Runtime nickname resolution is agent-prose — deliberately no standalone resolver (owner sizing, recorded in the test docstring).
- TODAY: Same design. VERDICT: HOLDS. PROPOSED: reconcile the leftover `"model": "<id>"` cache-schema text and stale local-cache slugs with the map amendment (F7).

### 2026-07-18 — Reviewer dispatch is self-permissioning
- EVIDENCE: Supported, including the retraction. "Self-permissioning launch" stands at `templates/playbooks/codereview.md:191-200` with the `--allowedTools` grant; the falsified cli↔mcp equivalence sentence is verifiably deleted (commit `b35247e`). `templates/playbooks/openreview.md:60-64` points to it as canonical; probe step 3 runs the smoke test with the same grant; step 4 makes tool denial terminal (issue #6, `7f80a71`).
- SHIPPED: Yes. ENFORCED: No test references the section or the `--allowedTools` line; nothing fails if the rule rots out of the template.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: structural pin in `tests/test_templates.py` (F9).

### 2026-07-17 — Review economy: tiered reviewer routing (D1–D3); D4 dissolved
- EVIDENCE: Supported. `templates/playbooks/codereview.md` carries exactly two tiers with effort-bound identity (L221-243), fail-closed cache resolution (L245-252), competitive/fallback grade (L254-257), triggers T1–T5 (L316+), the fallback-grade halt (L368-372), repair-delta redispatch (L447), adjudicator offer (L443-445). `templates/playbooks/openreview.md:66-79` pins frontier@max with owner-adjudication-above-max. No xhigh selector exists anywhere, consistent with D4's dissolution.
- SHIPPED: Yes — mechanics shipped model-free; pins correctly live only in the gitignored cache and the decision log (that separation is the ruling).
- ENFORCED: Structurally — `test_codereview_carries_tier_semantics`, `test_openreview_routes_frontier_via_codereview_tiers`, denylist lint. Runtime routing behavior is prose-governed, by nature.
- TODAY: Same two-tier scheme. VERDICT: HOLDS. PROPOSED: —

### 2026-07-16 — `/git` operator family ships in the toolkit
- EVIDENCE: Fully supported. `templates/playbooks/git.md` carries all four operations (L14-17), plain-English delegation contract (L28-31), ask-before-irreversible one question at a time (L37-41), never rewrite history (L42-44), push executes on invocation (L64-70), deterministic URL-host classification (L53-60). Wrapper `templates/commands/claude/git.md` and skill `templates/skills/shared/git/SKILL.md` defer to the playbook.
- SHIPPED: Yes — all three artifacts in `tools/shipped-set.json`.
- ENFORCED: Existence only (artifact-source and wrapper/skill-mirror tests); nothing fails if the delegation-contract text is gutted.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: accept prose-only, or pin 2–3 load-bearing clauses (ask-before-irreversible, no-history-rewrite).

### 2026-07-12 — Draft-all harness artifacts stands; "smallest guidance set" means no token bloat
- EVIDENCE: Substance holds; mechanism wording is stale. The ruling says "bootstrap keeps drafting the operator wrappers, shims…", but `procedures/bootstrap.md:147-149` (commit `a576b17`, four days before the ruling) says bootstrap drafts only the judgment artifacts — refresh.py is the shipped set's single installer. The protected outcome persists structurally: refresh installs the entire set with no evidence-of-use gating; `templates/approval-summary.template.md:61-67` lists the shipped set as one flat committed group.
- SHIPPED: The gloss is not. "Minimal means no token bloat, not fewer support files" appears nowhere under `templates/`; the bare invariant ships at `templates/AGENTS.template.md:28` without the disambiguation. Mitigating: installed files are toolkit-owned (`AGENTS.template.md:32`), so a downstream agent misreading the invariant cannot act on it.
- ENFORCED: The all-harnesses outcome, yes, by construction (`test_installs_full_set_into_bare_repo_and_commits`); the gloss is unenforced prose.
- TODAY: Same substance via refresh-install rather than bootstrap drafting.
- VERDICT: HOLDS-UNSHIPPED. PROPOSED: amend the entry's mechanism wording; ship the one-line gloss beside the invariant or record it as deliberately local (F5).

### 2026-07-11 — Push status is never recorded in state files
- EVIDENCE: Fully supported; the 2026-07-22 relocation amendment is accurate. The rule lives verbatim in `templates/playbooks/drift.md:12` and `templates/state.template.md:8-10`; the `drift` bullet at `templates/AGENTS.template.md:56` keeps only its first sentence plus a playbook pointer. This repo's `.agents/state.md` records no push status.
- SHIPPED: Yes, twice (drift playbook + state template). ENFORCED: No test greps for the wording; nothing fails if an agent writes a push-state line.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: none required; optional drift-time lint for push-state patterns.

### 2026-07-10 — Release posture: perfect privately first, release widely later
- EVIDENCE: Supported. `README.md:3` still opens "A **personal** governance toolkit"; no LICENSE, CHANGELOG, version tags, or CI workflows; `.github/` holds only issue templates; `.agents/state.md:27-28` records release engineering (M6) deferred by this ruling.
- SHIPPED: N/A — strategy ruling about this repo. ENFORCED: N/A — posture statement.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: —

### 2026-07-10 — Agents never update this repo's own governance while working on the toolkit
- EVIDENCE: Supported and recently reinforced. `.agents/repo-guidance.md:81-89` carries the rewritten rule; the incident commit `65a8543` exists; commit `4794a56` (2026-07-23) added the dogfood stop to `procedures/bootstrap.md:14-17`.
- SHIPPED: Correctly local (binds only agents working on the toolkit); the downstream sibling ships as the toolkit-owned invariant (`templates/AGENTS.template.md:32`).
- ENFORCED: Partially. The edit path is blocked on Claude Code (`protect-governance.py` exits 2 on edits to all 33 installed targets; `test_edit_of_protected_target_is_blocked`). But the ruling's named hazard — an agent *running* `tools/refresh.py` via Bash — has no guard: the hook covers edit tools only, refresh.py has no self-target refusal, no test simulates a self-refresh, and non-Claude harnesses block nothing.
- TODAY: Same rule plus a hard guard — refresh.py should refuse when the target is the toolkit repo itself.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: self-target refusal in `tools/refresh.py` + regression test (F6) — the highest-value enforcement gap this audit found.

### 2026-07-10 — Plan contract: agent-facing plan documents; owner decisions in chat
- EVIDENCE: Supported; the 2026-07-22 comms-level amendment is accurate in every particular. Canonical home `templates/AGENTS.template.md:58` carries the full contract with register deferred to `.agents/comms-policy.md`; this repo's level 2 reproduces the original register. `templates/commands/claude/plan.md` and the plan skill point at AGENTS.md.
- SHIPPED: Yes. ENFORCED: Partially, locally — `tests/test_plan_lint.py` lints this repo's post-2026-07-10 non-closed plans for chat-leakage phrases, stale path refs, and bloat (`::test_corpus_clean` runs it on the real corpus); the lint does not ship, and the chat-ask half is untestable prose by nature.
- TODAY: Same split; the per-repo comms level is a strict improvement over a fixed word count. VERDICT: HOLDS. PROPOSED: —

### 2026-07-09 — Codex 0.144 new surface evaluated; `codex exec`+stdin dispatch retained
- EVIDENCE: Half holds, half falsified. The probe-driven core persists (`templates/playbooks/codereview.md:80-127` derives the incantation live; stdin fact holds at `docs/harness-capabilities.md:124`). The referenced contract home `.agents/playbooks/reviewloop.md` <!-- plan-lint: allow (deleted file named as historical evidence) --> no longer exists (split 2026-07-16) but its content carried over. However, the recorded "`codex mcp-server` not adopted" conclusion is contradicted by current repo state: shipped `codereview.md:170-174` makes `mcp` the *preferred* transport where verified — citing as an advantage the exact statefulness the evaluation counted against it ("thread continuity gives the repair-delta natively" vs. the evaluation's "stateful … one-shot per finding" objection); the verdict-envelope objection is resolved at L215 ("the MCP result envelope"); the live cache records codex on `"transport": "mcp"` at 0.144.5. The MCP preference entered in `ec7b62e` (2026-07-17); no decision entry amends the 2026-07-09 evaluation, which still reads "retained unchanged".
- SHIPPED: N/A as an evaluation, but the shipped design now runs opposite to the entry's recorded conclusion. ENFORCED: Unenforced, appropriately for an evaluation record.
- TODAY: Evaluate, adopt `codex mcp-server` for the sandbox boundary and thread continuity, keep `codex exec`+stdin as the probed cli fallback — which is what the repo in fact did eight days later without telling the decision log.
- VERDICT: CONTRADICTED. PROPOSED: append a dated amendment recording the 2026-07-17 adoption (`ec7b62e`; cache at 0.144.5) so the log does not assert a retention the fleet no longer practices (F3, owner item).

### 2026-07-09 — Dead-path lint is git-aware; no allowlists anywhere
- EVIDENCE: Fully supported. `tools/refresh.py:405-419` (`_deletion_commit`, cached, fails toward loud); NOTE vs LINT at 456-458, 789-790; commit `e9e04b4` matches the claimed scope. `LINT_EXEMPT_PATHS` (384-390) holds only expected-absent-by-design paths; no per-repo/global allowlist mechanism exists. The per-line `lint: allow` escape (442-444) was added a day after the ruling (`7074f6b`) — an in-line marker, not a path allowlist; never-tracked mentions stay loud.
- SHIPPED: Yes — encoded in refresh.py. ENFORCED: Yes — `test_lint_notes_git_vouched_deletion_instead_of_warning`, `test_lint_notes_deleted_directory_mentioned_with_trailing_slash`, `test_lint_flags_dead_path_reference`, `test_lint_allow_marker_suppresses_same_line_only`, dogfood baseline `test_this_repos_agents_files_have_zero_warn_findings`.
- TODAY: Same design. VERDICT: HOLDS. PROPOSED: —

### 2026-07-08 — Zero-based consolidation
- EVIDENCE: Substance holds; two mechanism sentences are stale. Verified: discovery is a live checklist (`procedures/bootstrap.md:86`, salvaged probe order, ignore-aware detection, CI rule); the discover script and its machinery are gone; JSON layer retired (`shipped-set.json:425-434`); hooks narrowed to the Claude compaction re-ground; feedback = GitHub issues (`README.md:59-63`, `.github/ISSUE_TEMPLATE/`); evals scrapped (`git ls-files evals/` empty); redline real; playbooks preserved. Stale within the entry: "replace-if-unmodified … else flag, never overwrite" and "empty formerly-hashes = always flag, never machine-delete" were superseded by the 2026-07-16 strict-converge ruling (archived `docs/history/decisions-archive.md:2203`; restore-with-drift at `refresh.py:335-337`, retired machine-removal at 338-344), with no amendment pointer on the entry. Stale comment at `tests/test_templates.py:94-95` says "never machine-deleted" while `test_retired_generated_file_any_content_is_removed` asserts removal.
- SHIPPED: Yes. ENFORCED: Yes — `test_retired_hook_class_and_json_layer_present`, `test_shipped_hooks_are_the_verified_set`, ~70 refresh behavior tests. The no-rule-without-provenance rule is deliberately unenforced.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: "> Amended 2026-07-16" pointer (flag→restore; retired machine-deletes with drift report) + fix the stale test comment (F11).

### 2026-07-03 — Playbooks install unconditionally on every run
- EVIDENCE: Core holds. Five playbooks are ordinary `"replace"` artifacts; `classify()` installs any missing artifact with no prompt or tier logic; deletion ⇒ reinstall; opt-out = remove from toolkit (precedent: reviewloop). One stale clause: "Never-overwrite protects owner-modified playbooks" — since 2026-07-16 strict converge, an owner-modified playbook is drift-restored; the entry's amendment note covers 2026-07-08 only.
- SHIPPED: Yes. ENFORCED: Mechanism-level — `test_installs_full_set_into_bare_repo_and_commits`, `test_committed_foreign_agents_deletion_installs_and_commits`.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: 2026-07-16 amendment pointer (never-overwrite replaced by restore-with-drift-report) (F11).

### 2026-07-03 — Subdir-scoped bootstrap is not a supported mode
- EVIDENCE: Fully supported and hardened into the tool. `worktree_root_error` (`tools/refresh.py:123-137`) refuses non-git targets, bare repos, and nested subdirectories before any mutation; `procedures/bootstrap.md:69` checks for `.git/`; the discover-era literal-`package.json` probe is gone. The deferred don't-own-the-root scenario stays compatible (a subtree that is its own git root is accepted).
- SHIPPED: Yes. ENFORCED: Yes — `test_nested_directory_is_refused`, `test_bare_repo_is_refused`, `test_non_git_target_is_refused`.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: —

### 2026-07-09 — Refused core-file replacement ends in banner plus bootstrap offer
- EVIDENCE: Core holds exactly as ruled; two later amendments lack pointers in the entry. Banner `banner_block` (`refresh.py:612-620`); `detect_harnesses` probes PATH via `shutil.which` (598-601); TTY gate requires stdin AND stdout (869); one-question offer declines on q/empty/junk/EOF (655-675); non-TTY prints ready-to-paste commands (642-652). Stale: "Exit code is unchanged" — core-flagged runs now exit 5 (added 2026-07-23, `63db061`); the banner's trigger narrowed from refusal "for any reason" to foreign files only (2026-07-16 restores divergent-but-once-governed core files instead).
- SHIPPED: Yes. ENFORCED: Yes — `test_foreign_core_file_prints_banner_and_commands`, `test_clean_run_prints_no_banner`, `test_non_core_drift_prints_no_banner`, `test_offer_launches_chosen_harness_with_prompt`, `test_offer_declines_on_q_empty_junk_and_eof`, `test_non_tty_commands_without_harness_points_at_procedure`.
- TODAY: Same; the exit-5 refinement is strictly better. VERDICT: HOLDS. PROPOSED: amendment pointer: exit code now 5 (2026-07-23); banner fires on foreign-core flags only (2026-07-16) (F11).

### 2026-06-28 — Durable truth lives only in harness-neutral files; harness files are pure adapters
- EVIDENCE: Supported; the 2026-07-22 amendment is accurate. Both retired mechanisms sit in the `shipped-set.json` retired list; the surviving substrate works as claimed (`refresh.py:335-337` restores divergent adapters; `protect-governance.py:20-54` blocks edits including `CLAUDE.md`; the shim is literally `@AGENTS.md`, `templates/shims/CLAUDE.template.md:1`). Corollary check: `.agents/repo-facts.jsonl` was declined, never built — never committed, no template; the only record is an inline `lint: allow` annotation (`.agents/decisions.md:816`). Thin provenance: no dedicated entry records the decline.
- SHIPPED: The declarative principle text is not in `templates/`, but its operational content ships (`templates/AGENTS.template.md:31-32` portability test + toolkit-owned invariant) plus the shipped shim bytes themselves.
- ENFORCED: Yes, structurally — `test_shims_are_single_pointer_lines`, `test_edit_of_protected_target_is_blocked`, `test_protected_set_matches_the_shipped_targets`, `test_diverged_artifact_is_restored_with_drift_report`, `test_hand_edited_agents_md_in_governed_repo_is_restored`.
- TODAY: Same design. VERDICT: HOLDS. PROPOSED: optional — record the repo-facts.jsonl decline as a dated amendment line (F13).

### 2026-06-27 — Push policy delegated to `.agents/push-policy.md`; four options; default ask
- EVIDENCE: Supported. The Prime-Invariants clause is verbatim at `templates/AGENTS.template.md:9`; `templates/push-policy.template.md:1-2` ships the `ask` default; `templates/approval-summary.template.md:91-102` presents the four options with must-ask-never-prefill; the option set is still four (fifth `manual` option declined 2026-07-11). Two stale details: the post-commit consult is at `procedures/bootstrap.md` Step 7 item 4 (L257-260), not "Step 10"; the `templateVersion` machinery was superseded by byte-compare 2026-07-08.
- SHIPPED: Yes — pointer clause in byte-verified AGENTS.md; the template and approval-summary presentation are bootstrap-time artifacts (installed policy is repo-owned, `refresh.py:33-34`).
- ENFORCED: Partially — `test_empty_push_policy_fails_before_any_write` (exits 4 on empty/malformed policy); every run prints the active policy line. Nothing pins the four options or the behavioral "ask before pushing".
- TODAY: Same. VERDICT: HOLDS. PROPOSED: optional — fix the "Step 10" citation (F13).

### 2026-06-24 — Section-level rule deduplication
- EVIDENCE: Supported; all three named targets are verifiably fixed in current product files (flag-conflicts: one full statement at `templates/AGENTS.template.md:26`, Source Of Truth L48 is pointer-plus-terse-application; docs-only carve-out: one full statement at L71, approval summary now points; the migration procedure named as the third target no longer exists). The ruling's scope note (this repo's AGENTS.md a "frozen instance") is outdated — it is now a refresh-installed replace-whole artifact — but non-load-bearing.
- SHIPPED: The underlying invariant ships at `templates/AGENTS.template.md:24`; the dedup discipline itself is a toolkit-authoring rule whose product (the deduplicated template) ships.
- ENFORCED: Unenforced. No test or tool detects a duplicated rule statement; reintroducing one fails nothing — the exact gap the audit plan's third calibration example names.
- TODAY: Same rule, and the toolkit now has lint infrastructure it lacked in June 2026 — wire a duplication check into it.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: structural dedup check so a reintroduced second full statement fails CI (F8).

### 2026-06-09 — Standard `.agents/` layout for all bootstrapped repos
- EVIDENCE: Supported as amended. The 2026-07-08 amendment is accurate (repo-map/artifact-manifest retired, zero live references; verification's home is `.agents/repo-guidance.md`); the 2026-07-03 playbook amendment holds (five playbooks ship as `replace`). The layout has since grown two members the amended text does not name — `push-policy.md` (2026-06-27) and `comms-policy.md` (2026-07-22) — reflected in `templates/approval-summary.template.md:52-58` and `README.md:13-17`. Migration-into-layout via inventory verdicts survives at `procedures/bootstrap.md:119-141` + `templates/governance-inventory.template.md`.
- SHIPPED: Yes, embodied in the template set, `shipped-set.json`, and the byte-verified AGENTS.md pointers.
- ENFORCED: Asymmetric. The refresh-owned half is fully enforced (`test_installs_full_set_into_bare_repo_and_commits`, the `test_retired_*` family, `test_every_artifact_source_exists`); the repo-owned `.agents/*.md` half has no presence check — convergence there is procedure-only via bootstrap.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: optional — amend the member list to include push-policy.md and comms-policy.md (F13).

### 2026-06-18 — Operator command wrappers are a standing guarantee on every route
- EVIDENCE: Supported, now mechanical — but the standing 2026-07-08 amendment is itself one generation stale. The guarantee holds: all 12 wrappers are `replace` artifacts (missing ⇒ install; the set grew beyond the ruled six); the `.gitignore` repair survives exactly as ruled, executed by refresh (`shipped-set.json:455-462`; `refresh.py:348-372,570-576`). Staleness: (a) the amendment's `replace-if-unmodified` name and "owner-modified is flagged, never touched" semantics were superseded 2026-07-16 — an owner-modified wrapper is now reported as drift and restored; (b) every prose cross-reference in the original text is dead (no wrappers recipe section in bootstrap.md; the migration procedure deleted; the template's Bootstrap Handoff section cut 2026-07-08).
- SHIPPED: Wrappers and gitignore repair ship as artifacts/behavior; the guarantee-rule prose no longer needs to ship — the installer realizes it.
- ENFORCED: Yes, strongly — `test_wrapper_set_covers_operators_and_update_governance`, `test_shared_skill_set_mirrors_the_wrapper_set`, `test_every_wrapper_playbook_and_skill_carries_the_marker`, `test_installs_full_set_into_bare_repo_and_commits`, `test_blanket_adapter_ignore_is_repaired_and_committed`.
- TODAY: Same structural answer. VERDICT: HOLDS. PROPOSED: dated amendment noting the `replace-if-unmodified` → `replace` rename and strict-converge semantics (F11).

### 2026-06-10 — Evidence rule for all durable claims
- EVIDENCE: Canonical home `procedures/bootstrap.md:28-33` (near-verbatim); reinforced by `procedures/verification.md:8-15`, fresh-eyes question 6, and `templates/approval-summary.template.md:40-44`. Shipped echo in generalized form: `templates/AGENTS.template.md:23` ("Label inferred-but-unverified facts as assumptions").
- SHIPPED: Only the diluted label-assumptions form ships; the full cite-the-proving-query rule is a bootstrap-workflow rule and `procedures/` is its legitimate home.
- ENFORCED: No (fresh-eyes q6 is an agent-run process check). TODAY: Same rule.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: none; procedure home is correct.

### 2026-06-10 — Gitignore-aware commit contract and custody queries
- EVIDENCE: `procedures/bootstrap.md:199-207`; `approval-summary.template.md:48-50,69-75,80`; mechanically embodied in `refresh.py:36-45,349-355`. One stale clause: custody is no longer recorded in artifact manifests — the manifest was retired 2026-07-08; custody is now proven live at the approval gate.
- SHIPPED: Bootstrap-procedure internal; refresh.py carries the enforced half for the shipped set.
- ENFORCED: Yes for the refresh half — `test_blanket_adapter_ignore_is_repaired_and_committed`, `test_unrecognized_ignore_rule_flags_and_skips`, `test_ignored_untracked_retired_file_refuses_not_deletes`.
- TODAY: Same design. VERDICT: HOLDS. PROPOSED: amend the entry to note the manifest-custody clause was superseded 2026-07-08 (F13).

### 2026-06-10 — One-scoped-commit + push-offer-once discipline
- EVIDENCE: `procedures/bootstrap.md:227-234` (one scoped commit, never `add -A`), `:257-260` (push once, naming remotes — now routed through `.agents/push-policy.md`, default `ask` = the original rule); `approval-summary.template.md:77-89`; `refresh.py:42-45` ("one scoped commit … Neither mode pushes"). The legacy carve-out route's two announced commits (`bootstrap.md:236-253`) is a refinement, not a contradiction.
- SHIPPED: The steady-state half ships (`AGENTS.template.md:9`); the bootstrap single-commit contract is procedure-side.
- ENFORCED: Yes for refresh's own commit — `test_staged_set_gap_refuses_commit`, `test_pre_staged_unrelated_file_stays_out_of_the_commit`, `test_apply_stage_only_stages_without_commit`.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: —

### 2026-06-10 — Answer-with-words rule hardened; artifact-is-evidence-not-decision
- EVIDENCE: Ships verbatim as the first Prime Invariant (`templates/AGENTS.template.md:7`), with the 2026-07-22 issue-#8 qualification folded into that line; also `procedures/bootstrap.md:20-27,34-36`; amendment entry at `.agents/decisions.md:190-215`.
- SHIPPED: Yes, amendment included. ENFORCED: No; behavioral rule.
- TODAY: Same rule, one entry (see the duplicate entry below).
- VERDICT: HOLDS-UNENFORCED. PROPOSED: deduplicate with the "Artifact is evidence" entry (F13).

### 2026-06-10 — PowerShell helper retired
- EVIDENCE: Half true. `docs/history/agent-bootstrap-discover.ps1` exists as the archival record. But the entry's forward sentence — "All active work uses the Python `tools/discover.py`" — is false: `tools/discover.py` <!-- plan-lint: allow (deleted file named as the defect being recorded) --> was deleted in the 2026-07-08 zero-based consolidation, replaced by the live checklist (`procedures/bootstrap.md:86-88`); no live doc outside history archives references it.
- SHIPPED: N/A (toolkit-local history entry). ENFORCED: N/A.
- TODAY: "PowerShell retired to history; discovery is the live checklist in procedures/bootstrap.md Step 2; refresh.py is the only shipped tool."
- VERDICT: STALE. PROPOSED: append a 2026-07-08 amendment line: the discover script itself deleted in the zero-based consolidation; discovery is now the procedure checklist (F1, owner item).

### 2026-06-10 — Fresh-eyes verification as consistency-not-truth check
- EVIDENCE: `procedures/verification.md:8-15` (explicit scope warning), grading rule `:58-62`, recording rule `:66-73`; `approval-summary.template.md:137-146` ("Never present this test as proof"); six questions intact at `verification.md:46-56`.
- SHIPPED: Bootstrap-procedure internal — legitimate home. ENFORCED: No.
- TODAY: Same framing. VERDICT: HOLDS-UNENFORCED. PROPOSED: none.

### 2026-06-10 — Windows Python probe order and Store-stub detection
- EVIDENCE: Verbatim in `procedures/bootstrap.md:76-84` (with a later 3.10 floor); explicitly salvaged in the 2026-07-08 consolidation; steady-state echo in `templates/commands/claude/update-governance.md:12-13` and the shipped hook's interpreter fallback (`templates/hooks/claude/settings.json:9`).
- SHIPPED: Full rule is procedure-internal; only the platform-branch invocation ships. ENFORCED: No — the functional probe tests died with the discover test module 2026-07-08.
- TODAY: Same probe order; App Execution Alias stubs persist. VERDICT: HOLDS-UNENFORCED. PROPOSED: none.

### 2026-06-10 — Cwd-independent Step 0 sync (`git -C`)
- EVIDENCE: `procedures/bootstrap.md:47-65` (git `-C` mandate, ls-remote liveness, proceed-and-flag, gitea lag expected, never merge/rebase the toolkit); refresh.py runs the same discipline (`refresh.py:110,144`).
- SHIPPED: Procedure-side; the shipped update-governance wrapper delegates sync to refresh.py.
- ENFORCED: For the tool path, yes — `test_offline_sync_proceeds_with_flag`.
- TODAY: Same. VERDICT: HOLDS. PROPOSED: —

### 2026-06-10 — CI markers are provider-executable only + branch match required
- EVIDENCE: The durable rule survives verbatim as the "CI rule" in `procedures/bootstrap.md:105-110` and fresh-eyes q6 (`verification.md:52-54`). The entry's machinery sentence is dead: `suspectedMisplacedCi`/`ciBranchMismatches` were discover-packet fields — they exist now only in this entry and a history file.
- SHIPPED: No shipped artifact carries it; bootstrap-procedure internal — correct home for a discovery-time rule. ENFORCED: No.
- TODAY: Same rule, minus the packet field names.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: amend the entry: mark the packet-fields sentence historical (machinery deleted 2026-07-08); rule lives at `procedures/bootstrap.md:105-110` (F13).

### 2026-06-10 — Git-safety: ancestry vs content verification
- EVIDENCE: Ships verbatim in `templates/AGENTS.template.md:77`; reinforced in `templates/playbooks/git.md:106-109` and `:30`.
- SHIPPED: Yes, twice. ENFORCED: No.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: none.

### 2026-06-10 — One-item-per-commit discipline (batch sweeps owner-only)
- EVIDENCE: Ships verbatim in `templates/AGENTS.template.md:78`; cited by `templates/playbooks/codereview.md:50`; reinforced by the 2026-07-22 R1 ruling.
- SHIPPED: Yes. ENFORCED: No.
- TODAY: Same. VERDICT: HOLDS-UNENFORCED. PROPOSED: none.

### 2026-06-10 — Artifact (defect report / plan / spec) is evidence, not decision
- EVIDENCE: Same canonical text as the answer-with-words entry (`templates/AGENTS.template.md:7`; `procedures/bootstrap.md:24-27`). The two entries are the same rule recorded twice the same day — identical decision clause, identical "supersedes the softer wording" rationale. No divergence; both resolve to the single shipped invariant, which now also carries the 2026-07-22 qualification.
- SHIPPED: Yes (same line as answer-with-words). ENFORCED: No.
- TODAY: One entry, not two.
- VERDICT: HOLDS-UNENFORCED. PROPOSED: annotate this entry as merged into / duplicate of the answer-with-words entry (F13).

### 2026-06-09/10 — Pilot findings folded into canon (multiple)
- EVIDENCE: Bullet-by-bullet verification: revert-the-fix ✓ (`AGENTS.template.md:70`); ancestry-vs-content ✓ (`:77`); one-item-per-commit ✓ (`:78`); safety-vs-ritual ✓ (`procedures/bootstrap.md:111-117`); load-bearing-path check ✓ (`:131-135`); summary altitude ✓ (`approval-summary.template.md:3-6`); one scoped commit ✓ (`bootstrap.md:227-234`); push-once ✓ (`:257-260`); evidence rule ✓ (`:28-33`); custody-from-git ✓ (`approval-summary.template.md:48`); fresh-eyes ✓ (`verification.md:8-15`); Windows probe ✓ (`bootstrap.md:76-84`); `git -C` Step 0 ✓ (`:47-65`); answer-with-words ✓ (`AGENTS.template.md:7`). One dead bullet: "Manifest schema shipped beside discover.py" — the schema/manifest machinery was deleted 2026-07-08; the schema survives only as `docs/history/artifact-manifest.md`.
- SHIPPED: Mixed by bullet, as itemized — the correct split. ENFORCED: Only the bullets refresh.py carries.
- TODAY: Keep the fold-in summary; strike or annotate the dead bullet.
- VERDICT: STALE. PROPOSED: annotate the manifest-schema bullet with its 2026-07-08 retirement (one line); all other bullets verified live (F2, owner item).

## Pass 2 — cross-cutting audits

### SHIPPED/LOCAL gap table

Every behavioral ruling vs. its shipped carrier. "Shipped" = text present in a file under `templates/` that reaches governed repos (refresh-installed or bootstrap-drafted). Audit rule: every HOLDS-UNSHIPPED is a defect.

| Ruling | Behavioral rule | Shipped carrier | Gap |
|---|---|---|---|
| 2026-07-22 paperwork | Completion bookkeeping (close issue, sync state) needs no fresh ask | Only its handoff instance ships (`AGENTS.template.md:55`) | DEFECT — general form local-only (F4) |
| 2026-07-12 draft-all gloss | "Minimal = no token bloat, not fewer support files" | None; bare invariant at `AGENTS.template.md:28` | DEFECT — gloss local-only (F5) |
| 2026-07-22 R1 generalization | Queue items one at a time behind explicit owner go | Commit-granularity half ships (`AGENTS.template.md:78`); owner-go half local | Local by design (repo-scoped queue); note only |
| 2026-07-22 R2 / R3 / issue-#8 / 2026-07-17 gates / 2026-07-23 handoff | Response-shape, state-currency, completion-report, gate-form rules | All ship in `AGENTS.template.md` | None |
| 2026-07-18 self-permissioning / 2026-07-17 tiers / 2026-07-19 model map / 2026-07-16 /git | Reviewer-dispatch rules | All ship in playbooks | None |
| 2026-06-10 procedure rules (evidence, custody, scoped commit, fresh-eyes, probe order, Step 0, CI markers) | Bootstrap-workflow rules | `procedures/` (toolkit-side) is the legitimate home; steady-state halves ship | None — procedure-internal by design |
| 2026-06-28 harness-neutral | Pure-adapter rule | Operational content ships (`AGENTS.template.md:31-32`); declarative text does not | None — structurally enforced instead |

Both defects get a proposed template change in the Fix Queue. Note the pattern: both are rulings whose shipped consequence was landed only for the incident instance that motivated them — the same class as the audit plan's first calibration example.

### PROSE/ENFORCED gap table

Shipped rules vs. enforcing test. Baseline: prose-pin tests were deliberately retired 2026-07-08, so "unenforced prose" is the default state, not automatically a defect. Only gaps worth new tooling get a proposed test; everything else carries an explicit not-worth-testing note.

| Shipped rule | Enforcing test | Assessment |
|---|---|---|
| 2026-07-10 never-self-govern (edit path) | `protect-governance.py` + `test_edit_of_protected_target_is_blocked` | Enforced on Claude Code edit tools only |
| 2026-07-10 never-self-govern (run path) | None — refresh.py has no self-target refusal | GAP — F6 (self-target refusal + test). The 2026-07-10 incident (`65a8543`) was a run, not an edit; the hole that produced the ruling is still open |
| 2026-06-24 section-level dedup | None | GAP — F8 (structural dedup check). The plan's third calibration defect shipped under exactly this hole |
| 2026-07-18 self-permissioning | None | GAP — F9 (structural pin in test_templates.py); cheap, pins a rule with a falsified-assumption history |
| 2026-07-22 comms-policy marker | None (contrast: push-policy preflight, `refresh.py:745`) | GAP — F10 (marker-format lint + docstring fix); cheap parity with push-policy |
| 2026-07-16 /git delegation contract | Existence tests only | NOT-WORTH-TESTING beyond optional 2–3 clause pins: prose for a human-facing dialog; mirror tests already guard the artifact set |
| 2026-07-11 never-record-push-status | None | NOT-WORTH-TESTING: a state-file content grep would false-positive on the rule's own text; the drift playbook already instructs deletion on sight |
| 2026-07-22 R2 / R3 / 2026-07-17 gates / 2026-07-22 issue-#8 / 2026-06-10 behavioral rules | None | NOT-WORTH-TESTING: agent response-shape rules; no mechanical check exists at this altitude. Deliberate prose governance |
| 2026-07-22 R1 owner-go half | None | NOT-WORTH-TESTING: local process rule about owner interaction |
| 2026-06-09 layout repo-owned half | None (refresh never touches repo-owned files) | NOT-WORTH-TESTING as refresh behavior; presence is bootstrap-procedure scope |
| All tool-encoded rulings (dead-path lint, strict converge, subdir refusal, banner/offer, playbooks install, wrappers guarantee, model map, push-policy parse, scoped commit, gitignore custody) | Named tests in the Pass 1 blocks | Enforced |

### LOAD-TIME vs USE-TIME: `templates/AGENTS.template.md`

Every section and operator bullet classified. Load-time = needed every session; use-time = only at invoke time (move to a playbook with a one-line dispatch stub — the `drift` shape at `AGENTS.template.md:56`). Template total: 1,947 words (`wc -w`), up from the 1,503-word 2026-07-08 redline.

| Section / bullet | ~Words | Class | Disposition |
|---|---|---|---|
| Prime Invariants | 150 | load-time | Keep — re-grounded after compaction |
| Repo-Specific Guidance | 75 | load-time | Keep — pointer + import |
| Universal Invariants | 620 | load-time | Keep — durable behavioral rules |
| Session Startup | 120 | load-time | Keep — runs every session |
| Source Of Truth | 75 | load-time | Keep |
| Operator `catchup` | 55 | use-time, already minimal | Keep — near dispatch-scale |
| Operator `handoff` | 170 | use-time — session-end only | MOVE to `.agents/playbooks/handoff.md`, one-line stub (F12). Plan's flagged candidate, confirmed |
| Operator `drift` | 70 | already correct shape | Keep — the pattern to replicate |
| Operator `decision` | 20 | minimal | Keep |
| Operator `plan` | 130 | use-time — plan-drafting only | MOVE to `.agents/playbooks/plan.md`, one-line stub (F12). Plan's candidate, confirmed |
| Operator `playbook <name>` | 50 | dispatch | Keep |
| Owner Gates | 105 | load-time | Keep — governs every owner ask |
| Verification | 160 | load-time | Keep — rules consulted during work |
| Git Safety | 130 | load-time | Keep — safety invariants |
| Final Response | 80 | load-time | Keep |

The plan's other candidates are already resolved by current structure: `codereview`, `openreview`, `review`, the `/git` family, `harness-update`, `update-governance` have no operator bullet in AGENTS.md at all — they already cost zero per-session tokens, shipped as skill + wrapper + playbook only.

Net effect of the two moves: ~300 words (~15%) leave the per-session file; the handoff and plan skills already point at AGENTS.md and would point at the new playbooks instead. Fix Queue item F12.

### ARCHITECTURE VERDICT

Incremental surgery. The evidence does not support a rebuild.

- 36 of 41 audited rulings hold in substance (16 HOLDS + 20 HOLDS-UNENFORCED, where unenforced is mostly deliberate design). The corpus of live rulings is overwhelmingly accurate about what the repo does.
- Every defect found is localized and individually repairable: 2 STALE one-sentence amendments, 1 CONTRADICTED amendment (a later adoption never recorded), 2 unshipped glosses, 4 missing amendment pointers, 1 template self-inconsistency (model-map cache schema), 1 unguarded run path (self-refresh), 2 movable template bullets, 3 cheap lint/test additions.
- No structural failure class recurs. The two recurring *paperwork* shapes — incident-instance shipped but general rule not, and later rulings landed without amendment pointers on the entries they qualify — are process habits, fixable by the queued amendments and (if the owner adopts it) one standing rule, not by re-architecture.
- The load-time budget is healthy: one 15% trim available, no systematic bloat.
- Test infrastructure is strong where the design chose to have it (tool behavior, artifact integrity) and deliberately absent where it did not (behavioral prose); the audit found no case where that choice was wrong except the gaps itemized above.

Had the verdict been rebuild, the Pass 1/2 tables above are the requirements baseline. It is not; do not propose one on any other basis.

## Fix Queue

Each item lands only behind a per-item owner go; one item per commit. F1–F3 (the routed STALE/CONTRADICTED verdicts) go to the owner one at a time with problem / proposed change / cost-risk / recommendation.

- F1 (STALE) Amend the 2026-06-10 PowerShell entry: the discover script was deleted 2026-07-08; discovery is the bootstrap.md live checklist. **LANDED 2026-07-23** (owner go; amendment appended to the entry).
- F2 (STALE) Amend the 2026-06-09/10 pilot fold-in: annotate the manifest-schema bullet with its 2026-07-08 retirement. **LANDED 2026-07-23** (owner go; bullet annotated in place).
- F3 (CONTRADICTED) Amend the 2026-07-09 Codex evaluation: record that `codex mcp-server` was adopted as the preferred transport 2026-07-17 (`ec7b62e`).
- F4 (HOLDS-UNSHIPPED) Paperwork rule: add one generalized completion-bookkeeping clause to `templates/AGENTS.template.md`, or amend the entry to record deliberate local scope.
- F5 (HOLDS-UNSHIPPED) Draft-all: amend the entry's mechanism wording (refresh installs, not bootstrap drafting); ship the one-line gloss beside the invariant or record it as deliberately local.
- F6 (enforcement) refresh.py self-target refusal (target = toolkit clone ⇒ refuse) + regression test. Highest-value gap.
- F7 (template defect) Reconcile `templates/playbooks/codereview.md` cache schema (L147-152, 245-246) with the model-map section (L267-270); reconcile stale slugs in `.agents/review/harnesses.local.json`.
- F8 (enforcement) Structural dedup check for `AGENTS.template.md` (in `lint_governance` or a test pinning known duplicate pairs).
- F9 (enforcement) Structural pin: codereview.md carries "Self-permissioning launch" + the `--allowedTools` line.
- F10 (enforcement) comms-policy marker-format lint + add comms-policy.md to refresh.py's repo-owned docstring list.
- F11 (paperwork) Amendment pointers on the 2026-07-08, 2026-07-03 (playbooks), 2026-07-09 (banner), and 2026-06-18 entries re: 2026-07-16 strict converge and 2026-07-23 exit 5; fix the stale comment at `tests/test_templates.py:94-95`.
- F12 (load-time) Move the `handoff` and `plan` operator bullets' procedure text to playbooks with one-line dispatch stubs (the `drift` shape); repoint the two skills; ~300-word per-session saving. The `formerly[]` maintenance rule applies to the template change.
- F13 (minor annotations, each a separate item) repo-facts.jsonl decline line; 2026-06-27 "Step 10" citation fix; 2026-06-09 layout member list; 2026-06-10 CI-markers packet-fields sentence marked historical; duplicate-entry annotation (artifact-is-evidence merged into answer-with-words); 2026-06-10 custody-clause supersession note.
