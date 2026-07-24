# Owner-facing surface redesign — install, update, vocabulary, guidance

Status: IN DESIGN 2026-07-23 — staged plan, pending owner decisions D1–D5
(one at a time, in chat per the plan contract). No implementation without
an explicit per-stage owner go. F5 of the 2026-07-23 audit findings is
parked: its wording depends on D3.

## Why this plan exists (owner direction, 2026-07-23)

The toolkit's machinery verified green in the 2026-07-23 decisions-as-claims
audit, but the owner's experience of it is broken in one consistent way:
the product was built agent-inward and the owner is the one using it.
Owner-stated evidence (verbatim unless noted):

- "there needs to be a lower friction way to apply this toolkit to a blank
  folder/repo" — the bootstrap procedure is a 1,900-word agent checklist,
  not a thing the owner runs.
- "a more coherent way to push updates … we once had an update-governance
  command? but it's unclear why there are multiples" — three names
  (`bootstrap.md`, `tools/refresh.py`, `update-governance`) for one owner
  intent: get current.
- "refresh.py spawns an agent harness when some things are true. I don't
  know what those are, or when to expect it" — the 2026-07-09 banner/offer
  fires a surprise at the moment of maximum confusion.
- "drift as a command is nonsensical. why call it the thing it prevents?
  when does someone use it?"
- "catchup and handoff are all I use outside of trying to use review, and
  I think I'm missing functionality. there's no guidance. there's no
  governance help. theres no installer."
- Stage 1 was specified by the owner: "I need something like 'new project'
  or 'setup repo' that does git init, puts all the governance in place,
  spawns a harness, agent asks me a couple of questions, and then I have a
  working project in-progress." Scope: "that's stage 1. the rest of what I
  complained about needs to be built as well."

Diagnosis (standing, per the 2026-07-23 discussion): the toolkit needs an
owner-facing surface — a few verbs matching owner intents — with the
existing machinery demoted behind it. The machinery mostly stays; the
surface is what gets built.

## Existing machinery this plan reuses (do not rebuild)

- `tools/refresh.py`: reconcile-to-shipped-set engine — install-missing,
  update-formerly-shipped, restore-drift, remove-retired, gitignore
  repair, one scoped commit, `--stage-only`, `--plan-json`, push-policy
  preflight, exit codes (2 refusal, 4 policy, 5 foreign-core flag),
  `detect_harnesses` (PATH probe via `shutil.which`, seeded from
  `docs/harness-capabilities.md`), TTY-gated one-question harness offer
  (`offer_bootstrap`, declines on q/empty/junk/EOF, never prompts
  non-TTY), `non_tty_commands` (paste-able launch lines).
- `procedures/bootstrap.md`: the judgment half — discovery checklist,
  Windows Python probe order, CI rule, evidence rule, inventory for
  migration runs, approval gate, one-scoped-commit contract.
- `templates/approval-summary.template.md`: the two owner questions
  (push policy, comms level), ask-never-prefill, the scoped-commit
  authorization text, the fresh-eyes line.
- Shipped vocabulary: `catchup`, `handoff`, `codereview`/`review`,
  `openreview`, `drift`, `decision`, `plan`, `playbook`,
  `update-governance`, `git`.

## Stage 1 — `new-project` (real installer)

Owner flow: run one command in a blank folder; it does `git init` and
installs the governance set; it launches a detected agent harness in the
folder; the agent asks a couple of questions and finishes setup; the
owner has a working project with a first commit.

Design:

1. New toolkit script `tools/new-project.py` (stdlib-only, mirrors
   refresh.py's interpreter floor and `git -C` discipline), behind the
   executable launcher `tools/new-project` (D1). Invocation:
   `new-project <path> [hint]` (D2a) — creates `<path>` if needed,
   `git init` there, installs the governance set, launches the detected
   harness with `<hint>` priming its kickoff prompt. Documented in
   `README.md` as the one-line install.
2. Mechanical phase (no agent, no questions): create the target dir;
   refuse a non-empty dir that already contains governance (point at
   `tools/refresh.py` instead); `git init` if no `.git`;
   invoke refresh.py's reconcile (`--stage-only`) against the target to
   install the shipped set uncommitted.
3. Agent phase: probe PATH for a known harness (reuse
   `detect_harnesses`); at a real TTY ask one question to launch it in
   the target with a kickoff prompt that points at the setup procedure
   (below); non-TTY or decline prints the exact paste-able launch line.
   This is the refresh.py banner/offer machinery relocated to the one
   context where spawning is the owner's explicit expectation.
4. Setup procedure (new `procedures/setup.md`, slimmed from
   `bootstrap.md`): the agent drafts the judgment files
   (`.agents/state.md`, `decisions.md`, `repo-guidance.md`,
   `push-policy.md`, `comms-policy.md`), asks the owner exactly the D2
   question set, commits the judgment drafts + the staged shipped set as
   ONE scoped commit, and reports the working state. `bootstrap.md`
   remains the migration/inventory procedure for repos with existing
   governance; `setup.md` is the greenfield path and is much shorter.

## Stage 2 — coherent update

1. `tools/refresh.py` never spawns anything: the TTY harness offer is
   removed (relocated to `new-project.py` in Stage 1). The foreign-core
   banner stays and its resolution line changes from "run bootstrap" to
   the setup procedure path / `new-project.py` line. Exit code 5 and the
   quiet-run properties are unchanged.
2. `update-governance` is the single owner-facing update verb; its
   wrapper text already describes the run. It gains a plain-English
   "what just happened" summary requirement (what was installed,
   updated, restored, removed — one line each, from the script's own
   output record).
3. Multiples collapse by documentation, not deletion: README names
   `new-project` (first time) and `update-governance` (after that) as
   the only two governance commands an owner needs; `refresh.py` and
   `bootstrap.md` are documented as machinery behind them.

## Stage 3 — vocabulary and guidance

1. Owner-facing verb set (everything else is machinery): `catchup`,
   `handoff`, `review`/`codereview`, `openreview`, `git`, plus
   `new-project` and `update-governance` from Stages 1–2. D4 decides
   the fate of `drift` (rename to an intent-shaped word, fold its
   state-hygiene pass into `handoff`/`update-governance`, or keep) and
   whether `decision`/`plan`/`playbook` stay owner-visible.
2. Guidance: a shipped `help` command + skill answering "what can I
   say?" with the owner verb list in one plain line per verb (what it
   does, when to say it). This is the missing "governance help."
3. AGENTS.template.md operator section reflects the final verb set
   (one-line bullets, dispatch shape per the audit's load-time finding
   F12 — handoff/plan procedure text moves to playbooks if D4 keeps
   those verbs).

## Decisions for the owner (one at a time, chat)

- D1 — Stage 1 name and invocation. **RULED 2026-07-23:** name is
  `new-project`; the owner must never see or think about a Python
  interpreter. Invocation is an executable launcher
  `tools/new-project` (POSIX shell) that locates a working Python
  (≥3.10, per the repo's documented probe order and floor) and execs
  `tools/new-project.py` with it — a bad or missing interpreter is the
  launcher's problem, reported in plain words, never the owner's. A
  Windows launcher (`.cmd`) is deferred until real demand (owner ruling:
  no current need); the launcher is the only documented entry line in
  `README.md`.
- D2 — the setup question set. **RULED 2026-07-23:** three questions,
  no more: **what are we building** (blank folder only; when a hint was
  given on the command line the agent confirms it instead of asking),
  **push policy**, **communication level**. Verification stays
  detected-not-asked (the agent proposes once code exists, the owner
  corrects only if wrong).
- D2a — invocation shape (ruled with D2): `new-project <path> [hint]`
  — creates `<path>` if needed, `git init`, installs the governance
  set, launches the detected harness in it, and primes the agent's
  kickoff prompt with `<hint>` so the setup conversation opens with a
  confirmation, not an interrogation.
- D3 — Stage 2 shape: confirm refresh.py loses the spawn offer (banner
  points at setup instead) and `update-governance` is the single update
  verb. Recommendation: yes.
- D4 — vocabulary: `drift` rename/fold/keep; `decision`/`plan`/
  `playbook` visibility; the `help` verb. Recommendation: fold `drift`'s
  hygiene into `handoff` and retire the word fleet-wide (installed
  copies removed via the retired list); keep `decision`/`plan`/
  `playbook` as agent-level (they cost nothing per the audit's
  load-time table); add `help`.
- D5 — build order. Recommendation: Stage 1 → Stage 2 → Stage 3, each
  landing behind its own go, suite green per stage.

## Explicit non-goals

- No rebuild of refresh.py's reconcile engine, the shipped-set manifest,
  or the protect-governance hook — audit-verified machinery.
- No change to the review playbooks beyond what the 2026-07-23 dispatch
  ruling already landed.
- No hosted/web installer, no package-manager distribution.
- The 2026-07-23 audit Fix Queue continues independently (F4 landed;
  F5 parked on D3; F6+ behind per-item owner go).

## Verification

Per stage: the repo suite (`/opt/homebrew/bin/python3.14 -m unittest
discover -s tests -p "test_*.py"`) stays green; new script behavior
lands with tests first (new-project: init/idempotence/refusal cases,
offer TTY gates; refresh: banner text change, no-offer regression).
Stage 1 guard proof: run `new-project.py` into a throwaway dir, launch
nothing, and verify the staged tree + the paste-able launch line; then a
full live run behind the owner's go. `formerly[]` maintenance-rule
hashes ride every shipped-file change.
