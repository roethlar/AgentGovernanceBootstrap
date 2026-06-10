# Repo Governance Setup — brief for an agent

Hand this to an AI agent working in one of your repos. It sets governance up correctly, and it
finds the specific broken setup that makes agents confidently do the wrong thing while following
the instructions they can see.

The owner directs in plain English and does not read code. Talk in plain English. Never ask
code-expertise questions — offer choices as a goal, a cost, or a risk.

## Rule 0 — draft, don't apply

Do everything below as proposed changes in a `governance-drafts/` folder. Then give the owner one
plain-English summary with a clear verdict and wait for a yes. Nothing touches tracked files until
the owner approves. (If the repo already has a drafts/review flow, use it instead.)

## Step 1 — Audit the authority (do this first)

Find every file OR auto-loaded memory in or around this repo that states a rule, standard, or "how
things must be done": agent guides (`AGENTS.md`, `CLAUDE.md`, etc.), anything in `docs/`, any
constitution / spec / standards file, and any agent memory that loads automatically.

For each one, report in plain English:

* Is it tracked in git, or is it gitignored / untracked (so it exists only on this machine)?
* Is it referenced from the single guide the agent auto-loads each session?
* Does it contradict any other rule source?

Flag loudly: anything authoritative that is **gitignored or untracked** — it cannot govern a
cloned agent, so it is invisible to everyone but the owner on one machine — and any two sources
that **disagree**. This inverted hierarchy (the real rule living somewhere nothing points to, while
a stale or partial source is the one that loads) is the failure that makes an agent get it wrong
while obeying everything it can see.

## Step 2 — One entry point; authority by reference only

Make the auto-loaded guide (`AGENTS.md` or `CLAUDE.md`) the single front door, with one rule:
**nothing is authoritative unless this file points to it; anything it doesn't reference is not a rule.**

* Add references from the entry point to every doc that should be authoritative.
* For anything authoritative that's gitignored/untracked, propose tracking it — or flag it for the
owner to decide. A governance doc that isn't in the repo governs no one but the owner.
* Where two sources contradict, propose ONE reconciled version and retire or redirect the other.
Never leave two.

## Step 3 — The state file (so a cold agent gets oriented)

Write one short `.agents/state.md` from the ACTUAL code: what the project is, what's done, what's
next, the real build and test commands, and how to exercise the real thing. This is the first thing
any agent reads. Keep it short. If long journals or scattered status docs exist, compress their
current truth into this file and move the old ones into `archive/` (don't delete history).

## Step 4 — The behavior contract (add to the entry point)

* Ask before going beyond the literal request — as a goal, a cost, or a risk, never raw mechanism.
Never expand scope silently.
* "Done" means you ran it AND the state file now reflects reality — not when you believe it's right.
* Every claim about the repo carries a `file:line`. State plainly what you did NOT verify.
* Re-read a file before acting on a remembered rule; memory goes stale.

## What this does — and the one thing it can't

This makes invisible and contradictory authority impossible going forward, and gets every agent
oriented from one trustworthy place. It does NOT prove the agent is right about the code. Two cheap
checks catch that, and they're the owner's, because the agent can't be relied on to flag its own gap:

* Pick one claim that has a `file:line` and say "show me that line." A reconstructed claim collapses.
* Keep changes small and reversible, so a confident-wrong change is cheap to undo, not a disaster to prevent.

