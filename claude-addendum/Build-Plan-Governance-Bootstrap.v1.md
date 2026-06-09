# Build Plan — Repo Governance Bootstrap

A build brief for a fresh agent. It assumes no prior conversation. Build exactly this; the
"Out of scope" section is binding — do not add to it.

## Purpose
Give a non-developer owner (who runs PowerShell and does not read code) a one-command way to set
up agent governance in a repo, and to catch the specific failure where the authoritative rule
lives somewhere an agent never sees.

**The failure this exists to prevent (north-star test case):** an agent made a wrong version bump
because the correct rule lived in a *gitignored, untracked, unreferenced* `ProjectConstitution.md`,
while an auto-loaded stale memory stated a narrower wrong rule. The agent followed what it could
see and was wrong. The build is correct if, run on such a repo, it (a) flags that constitution as
authoritative-but-invisible, and (b) drives the real rule into the canonical entry point and
proposes retiring the contradicting memory — all as drafts for approval.

## The flow this implements
1. Owner runs the script in a repo. It writes only a `governance-drafts/` folder.
2. Owner opens an agent in the repo and says "read the onboarding guide in governance-drafts and follow it."
3. Agent follows the guide.
4. Agent produces the governance docs as proposed changes inside `governance-drafts/`.
5. Agent shows a plain-English summary with questions and a go / no-go recommendation.
6. Go → approved files move from `governance-drafts/` into their final paths, then the owner gives
   work commands. No-go → agent interviews the owner in plain English about the gaps; owner fills
   what they can.

## Build in two phases
- **Phase 1 (build now):** the setup script (Component A), the onboarding guide it scaffolds (B),
  the canonical entry-point template (C), the workflow command files (D).
- **Phase 2 (build after Phase 1 is approved):** the recurring check (E). This is the only piece
  that catches *future* drift without the owner doing anything; Phase 1 fixes the present state.

---

## Component A — the bootstrap script (PowerShell)
Build:

```text
tools/Initialize-RepoGovernance.ps1
```

Usage:

```powershell
.\tools\Initialize-RepoGovernance.ps1 -RepoPath <path>
```

`-RepoPath` defaults to the current directory.

One script the owner runs in a repo. It writes **only** into `governance-drafts/` on first run —
nothing anywhere else, no code changes, no files in the repo proper. Two jobs.

**A1 — Gather & audit (the important half).** **Enumerate files from the filesystem, not from
`git ls-files`** — ignored and untracked files must be included, because that is exactly what hid
the constitution. **Then use git only to classify** each hit as tracked, untracked, or ignored.
Scan for governance-relevant files and agent memory:
- Filename patterns (case-insensitive): `constitution`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
  `.cursorrules`, `.windsurfrules`, `copilot-instructions`, and anything containing `governance`,
  `policy`, `standards`, `conventions`, `charter`, `spec`, `rules`; plus everything under `docs/`.
- Agent memory: `.serena/`, `.gemini/`, and files matching `*memory*` or `feedback_*`.
- For each hit, record: full path; **git classification (tracked / untracked / ignored /
  not_git_repo)**; **referenced from `AGENTS.md`? yes/no** (grep the canonical entry point for the
  filename); size.
- Git classification meanings:
  - `tracked` = present in `git ls-files`
  - `ignored` = matched by `git check-ignore`
  - `untracked` = neither tracked nor ignored
  - `not_git_repo` = the target directory is not inside a Git repository, so custody guarantees
    are unavailable
- If `AGENTS.md` does not exist, `referenced_from_agents` is `false` for every governance hit.
- Flag two classes loudly: **invisible authority** = looks authoritative AND (untracked, ignored,
  OR unreferenced); **possible contradiction** = two or more sources that look like rule sources.
- Output into `governance-drafts/`: `audit.md` (plain-English, for the owner) and `audit.json`
  (a simple list, for the agent in step 3 to consume).
- *Acceptance:* run on a repo containing a gitignored `ProjectConstitution.md` not referenced by
  `AGENTS.md` → it appears in `audit.md` flagged "invisible authority."

**A2 — Scaffold proposed tooling (into drafts only).** Write the proposed tooling into
`governance-drafts/`, mirroring the paths it will eventually occupy: the onboarding guide
(Component B), the canonical entry-point template (Component C), the workflow command files
(Component D, under `.agents/commands/`), and `.agents/state.md` + `.agents/decisions.md`
templates. **Write nothing outside `governance-drafts/`.** Print one closing line: the single
sentence the owner says to an agent next (step 2).

Required draft layout:

```text
governance-drafts/
  audit.md
  audit.json
  ONBOARDING.md
  proposed/
    AGENTS.md
    .agents/
      state.md
      decisions.md
      commands/
        task.md
        catchup.md
        check.md
        drift.md
        decision.md
        plan.md
        handoff.md
        contextcheck.md
```

*Apply on approval:* moving approved files from `governance-drafts/` to their final paths is a
post-approval step — done by the agent, or by a tiny companion apply script if the owner prefers.
Do not build rollback machinery beyond that move.

## Component B — the onboarding guide (what the agent reads in steps 3–5)
A short markdown file the script scaffolds into `governance-drafts/`. It instructs the agent to,
in order:
1. Read `governance-drafts/audit.json` and `audit.md`.
2. Establish **`AGENTS.md` as the canonical entry point**. If the repo has harness-specific guide
   files (`CLAUDE.md`, `GEMINI.md`, etc.), make each a **thin pointer to `AGENTS.md`** — do NOT
   merge everything into a harness-specific file. Rule: nothing is authoritative unless `AGENTS.md`
   references it. Fold the **real rules into `AGENTS.md` itself** when they are short and easy to
   get wrong (e.g. the versioning rule); use a reference only for large or rarely-needed docs. For
   any authoritative file that is untracked/ignored, propose tracking it, or flag it for the owner
   to decide. Where sources contradict, propose ONE reconciled version and retire/redirect the
   others — never leave two.
3. For any stale memory that contradicts a tracked rule: **propose its retirement or correction in
   the drafts and WAIT for approval. Do not edit or delete local/ignored memory files before the
   owner approves.**
4. Write a short `.agents/state.md` from the **actual code**: what the project is, what's done,
   what's next, the real build/test commands, how to exercise the real thing. Compress any long
   journals into it and propose moving the originals to `archive/`.
5. Put all of the above as proposed changes in `governance-drafts/` (mirroring final paths). Show
   the owner ONE plain-English summary that opens with a verdict (Approve / Approve after edits /
   Do not approve yet), lists assumptions and questions, and risk-labels open items Low/Med/High.
   Wait. Move nothing into the repo until the owner says go.
6. On no-go, interview the owner in plain English about the flagged gaps and revise the drafts.

The guide must state: the owner does not read code; talk in plain English; never ask
code-expertise questions — frame choices as a goal, a cost, or a risk.

Owner-facing summaries are plain English. Machine-readable outputs such as `audit.json`, and
developer diagnostics such as PowerShell errors, may be structured or technical when needed.

## Component C — canonical entry-point template (`AGENTS.md`)
Short. Contents:
- **Mission:** turn a plain-English request into working, verified changes that fit the repo;
  don't expand scope without asking; explain in plain language.
- **Source of truth / precedence:** the repo is the memory, not chat or tool-local memory; read
  `.agents/state.md` and `.agents/decisions.md` first; what actually ran > code > docs > a guess;
  re-read a file before acting on a remembered rule; when sources disagree, flag it.
- **Authority rule:** `AGENTS.md` is canonical; harness-specific files are thin pointers to it.
  Nothing is a rule unless `AGENTS.md` references it; easy-to-miss rules are written in `AGENTS.md`
  directly, not one hop away.
- **Scope contract:** before going past the literal request, sort it — ask first (state it as a
  goal + cost in plain words) / take a reversible safe default and say so / name the risk in plain
  words. Never expand silently; never hand the owner raw mechanism.
- **Done means:** you ran it, AND — *only when current state, next work, blockers, or verification
  commands changed* — `.agents/state.md` is updated to match. Don't rewrite state after every task.
  Every claim about the repo carries a `file:line`; state plainly what you did not verify.

## Component D — workflow command files
The **canonical** workflow files are tracked Markdown under **`.agents/commands/`** (e.g.
`.agents/commands/task.md`, `catchup.md`, …) so they work regardless of harness and survive in the
repo. Harness command files (e.g. `.claude/commands/*`) are **optional conveniences that point to**
the canonical files — never the only copy, since `.claude/` is often ignored and some harnesses
load none of it. Provide one short file each for:
`task` (work the next item end to end, then report what you did, didn't do, and observed; update
state per the rule above), `catchup` (where things stand), `check` (run the real tests locally,
plain-English pass/fail — no cloud/CI), `drift` (compare docs/memory vs code, report which is
wrong, change nothing until approved), `decision`, `plan`, `handoff`, `contextcheck` (gap report on
whether the repo has enough for an agent to be productive).

## Component E — recurring check (Phase 2)
The same gather/audit logic as A1, runnable on its own so it catches drift introduced *after*
setup, without the owner invoking anything. Two delivery options, build whichever the owner picks:
a local pre-commit hook that blocks a commit when a touched rule/version is inconsistent or a new
authoritative file is untracked/unreferenced; and/or a scheduled local run that writes a report.
Keep it local — no cloud services.

---

## Hard constraints (do not violate)
- **Enumerate the filesystem** (including ignored/untracked) for the audit; **use git only to
  classify** each file as tracked/untracked/ignored.
- **`AGENTS.md` is canonical;** harness-specific guides are thin pointers to it. Never merge
  everything into a harness-specific file.
- **Canonical workflow/command files are tracked** under `.agents/`; harness command dirs are
  optional pointers only.
- **Non-destructive:** the script writes only `governance-drafts/` on first run; nothing reaches
  the repo proper until approval moves it; never change code during setup.
- **PowerShell**, runnable on Windows; readable by a non-developer.
- **Plain English everywhere** the owner reads; no code, diffs, or logs surfaced to the owner.
- Rules that are easy to get wrong live **in** `AGENTS.md`, not behind a pointer.
- The agent **proposes** memory retirement in drafts and waits; it does not touch local memory
  before approval.

## Out of scope (binding — do not build)
Cloud CI or branch protection; an "acceptance grader" that judges whether code is correct;
per-harness adapter generators; apply/rollback machinery beyond moving approved drafts into place;
any attempt to *semantically understand* arbitrary rules (the audit flags by filename pattern +
git-classification + referenced status only). Do not add features not listed above.

## Phase 1 acceptance checks

Build the smallest practical test fixture or documented manual test for the north-star failure:

```text
test-fixtures/invisible-authority/
  .gitignore
  CLAUDE.md
  docs/ProjectConstitution.md
```

Fixture setup:

- `.gitignore` ignores `docs/ProjectConstitution.md`.
- `CLAUDE.md` contains a visible but narrower or stale rule.
- `docs/ProjectConstitution.md` contains the broader correct rule.
- There is no `AGENTS.md`.

Expected result:

- `ProjectConstitution.md` appears in `governance-drafts/audit.md`.
- It is flagged as invisible authority.
- Its git classification is `ignored`.
- Its `referenced_from_agents` value is `false`.
- The generated onboarding guide directs the agent to propose canonical `AGENTS.md` guidance in
  `governance-drafts/proposed/`, not to edit the repo directly.

## Honest limit (state this to the owner; do not paper over it)
Phase 1 makes the rules correct, single, tracked, and placed in the canonical file, and the audit
catches the invisible-authority case by enumerating the filesystem. It does **not** guarantee an
agent obeys on every future auto-task — only Phase 2, which runs without the agent, makes a rule
unavoidable rather than merely available, and even that is bounded. The owner's standing backstops
remain: spot-check one `file:line`, and keep changes small and reversible.
