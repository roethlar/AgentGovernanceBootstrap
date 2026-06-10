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
authoritative-but-invisible, and (b) drives the real rule into the file the agent always loads and
retires the contradicting memory — all as drafts for approval.

## The flow this implements
1. Owner runs the script in a repo.
2. Owner opens an agent in the repo and says "read the onboarding guide and follow it."
3. Agent follows the guide.
4. Agent produces the governance docs in a `governance-drafts/` folder.
5. Agent shows a plain-English summary with questions and a go / no-go recommendation.
6. Go → drafts move into the repo proper, then the owner gives work commands.
   No-go → agent interviews the owner in plain English about the gaps; owner fills what they can.

## Build in two phases
- **Phase 1 (build now):** the setup script (Component A), the onboarding guide it scaffolds
  (B), the entry-point guide template (C), the command files (D).
- **Phase 2 (build after Phase 1 is approved):** the recurring check (E). This is the only piece
  that catches *future* drift without the owner doing anything; Phase 1 fixes the present state.

---

## Component A — the bootstrap script (PowerShell)
One script the owner runs in a repo. Two jobs. Non-destructive: it never overwrites an existing
file and never changes code.

**A1 — Gather & audit (the important half).** Read the **filesystem directly, not git** — this is
the whole point: gitignored/untracked files must be visible, because that is exactly what hid the
constitution. Scan for governance-relevant files and agent memory:
- Filename patterns (case-insensitive): `constitution`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
  `.cursorrules`, `.windsurfrules`, `copilot-instructions`, and anything containing `governance`,
  `policy`, `standards`, `conventions`, `charter`, `spec`, `rules`; plus everything under `docs/`.
- Agent memory: `.serena/`, `.gemini/`, and files matching `*memory*` or `feedback_*`.
- For each hit, record: full path; **git-tracked? yes/no**; **referenced from the entry-point guide?
  yes/no** (grep the AGENTS.md/CLAUDE.md for the filename); rough size.
- Flag two classes loudly: **invisible authority** = looks authoritative AND (untracked OR
  unreferenced); **possible contradiction** = two or more sources that look like rule sources.
- Output two files into `governance-drafts/`: `audit.md` (plain-English, for the owner) and
  `audit.json` (a simple list, for the agent in step 3 to consume).
- *Acceptance:* run on a repo containing a gitignored `ProjectConstitution.md` not referenced by
  `CLAUDE.md` → it appears in `audit.md` flagged "invisible authority."

**A2 — Scaffold tooling (inert, safe to write on run).** Write into the repo, skipping anything
that already exists: the onboarding guide (Component B), the command files (Component D). If an
entry-point guide already exists (`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`), do NOT touch it — write the
kit's guide template (Component C) to `governance-drafts/agent-guide.kit.md` for the agent to merge.
Print one closing line: the single sentence the owner says to an agent next (step 2).

*Note on the draft boundary:* the script writes only inert tooling (instructions and command
definitions). All governance **content** — the state file, the reconciled rules, which memory to
retire — is produced by the agent into `governance-drafts/` and requires the owner's go before it
moves into the repo.

## Component B — the onboarding guide (what the agent reads in steps 3–5)
A short markdown file the script scaffolds. It instructs the agent to, in order:
1. Read `governance-drafts/audit.json` and `audit.md`.
2. Establish ONE entry-point guide (`AGENTS.md` or `CLAUDE.md`) as the single front door, with the
   rule: nothing is authoritative unless this file references it. Fold the **real rules into the
   entry-point file itself** when they are short and easy to get wrong (e.g. the versioning rule);
   use a reference only for large or rarely-needed docs. For any authoritative file that is
   untracked/gitignored, propose tracking it, or flag it for the owner to decide. Where sources
   contradict, propose ONE reconciled version and retire/redirect the others — never leave two.
3. Retire or correct any stale memory that contradicts a tracked rule.
4. Write a short `.agents/state.md` from the **actual code**: what the project is, what's done,
   what's next, the real build/test commands, how to exercise the real thing. Compress any long
   journals into it and move the originals to `archive/`.
5. Put all of the above as proposed changes in `governance-drafts/` (mirroring final paths). Show
   the owner ONE plain-English summary that opens with a verdict (Approve / Approve after edits /
   Do not approve yet), lists assumptions and questions, and risk-labels open items Low/Med/High.
   Wait. Do not move anything into the repo until the owner says go.
6. On no-go, interview the owner in plain English about the flagged gaps and revise the drafts.

The guide must state: the owner does not read code; talk in plain English; never ask
code-expertise questions — frame choices as a goal, a cost, or a risk.

## Component C — entry-point guide template (`AGENTS.md`)
Short. Contents:
- **Mission:** turn a plain-English request into working, verified changes that fit the repo;
  don't expand scope without asking; explain in plain language.
- **Source of truth / precedence:** the repo is the memory, not chat or tool-local memory; read
  `.agents/state.md` and `.agents/decisions.md` first; what actually ran > code > docs > a guess;
  re-read a file before acting on a remembered rule; when sources disagree, flag it.
- **Authority rule:** nothing is a rule unless this file references it; easy-to-miss rules are
  written in this file directly, not one hop away.
- **Scope contract:** before going past the literal request, sort it — ask first (state it as a
  goal + cost in plain words) / take a reversible safe default and say so / name the risk in plain
  words. Never expand silently; never hand the owner raw mechanism.
- **Done means:** you ran it AND `.agents/state.md` now reflects reality. Every claim about the
  repo carries a `file:line`; state plainly what you did not verify.

## Component D — command files
Scaffold these as the owner's plain-English command vocabulary (one short file each):
`/task` (work the next item end to end, then report what you did, didn't do, and observed; update
state), `/catchup` (where things stand), `/check` (run the real tests locally, plain-English
pass/fail — no cloud/CI), `/drift` (compare docs/memory vs code, report which is wrong, change
nothing until approved), `/decision`, `/plan`, `/handoff`, `/contextcheck` (gap report on whether
the repo has enough for an agent to be productive).

## Component E — recurring check (Phase 2)
The same gather/audit logic as A1, runnable on its own so it catches drift introduced *after*
setup, without the owner invoking anything. Two delivery options, build whichever the owner picks:
a local pre-commit hook that blocks a commit when a touched rule/version is inconsistent or a new
authoritative file is untracked/unreferenced; and/or a scheduled local run that emails/writes a
report. Keep it local — no cloud services.

---

## Hard constraints (do not violate)
- Read the **filesystem, not git**, for the audit — gitignored files must be seen.
- **Non-destructive:** never overwrite an existing file; never change code during setup.
- **PowerShell**, runnable on Windows; readable by a non-developer.
- **Plain English everywhere** the owner reads; no code, diffs, or logs surfaced to the owner.
- **Draft → review → approve:** governance content lands in `governance-drafts/` and moves only on
  the owner's go.
- Rules that are easy to get wrong live **in** the always-loaded entry-point file, not behind a pointer.

## Out of scope (binding — do not build)
Cloud CI or branch protection; an "acceptance grader" that judges whether code is correct;
per-harness adapter generators; apply/rollback machinery beyond moving approved drafts into the
repo; any attempt to *semantically understand* arbitrary rules (the audit flags by filename
pattern + tracked/referenced status only). Do not add features not listed above.

## Honest limit (state this to the owner; do not paper over it)
Phase 1 makes the rules correct, single, tracked, and placed in the file the agent always loads,
and the audit catches the invisible-authority case by scanning the filesystem. It does **not**
guarantee an agent obeys on every future auto-task — only Phase 2, which runs without the agent,
makes a rule unavoidable rather than merely available, and even that is bounded. The owner's
standing backstops remain: spot-check one `file:line`, and keep changes small and reversible.
