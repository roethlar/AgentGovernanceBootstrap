# The process

A complete, plain-English way to direct AI coding agents — for an owner who directs the work
and does not read code. It keeps the project's knowledge in the repo, keeps agents on task,
makes their work reviewable in plain words, and is honest about what it can't do.

This is the whole thing in one package. It replaces the two earlier partial downloads.

## What you type
The word is all you remember; everything technical lives in the files an agent reads.

- `/task` — work the next task end to end, then report what you did, didn't do, and observed.
- `/catchup` — where does this project stand right now?
- `/check` — run the real tests here and tell me pass/fail in plain English.
- `/drift` — do the docs still match the code? Fix what doesn't.
- `/decision <what>` — write a decision down so it's not lost.
- `/plan <what>` — draft a short plan.
- `/handoff` — save where we are so the next session continues without this chat.
- `/contextcheck` — does this repo have enough for an agent to be productive? Get a gap report.

## What lives in the repo (the memory)
- `AGENTS.md` — the contract every agent follows. The heart of it: ask first before going
  beyond what you asked (in terms you can judge), the repo is the source of truth, and "done"
  means the agent ran the thing and told you what it saw.
- `.agents/state.md` — where things stand now. One short file; the first thing an agent reads.
- `.agents/decisions.md` — durable decisions, newest first.

## How to install it
Hand the single instruction in `INSTALL.md` to an agent. For a new repo it sets everything up.
For an existing one it merges with what's already there (without leaving duplicate rules), runs
`/contextcheck`, fills in the state file from the actual project, and shows you a plain-English
summary before it commits anything.

## What this replaces
Retire the bespoke discovery tool, the manifest, the harness adapters, and the freshness engine.
A first-draft `AGENTS.md` comes from your agent's built-in `/init`; this process is the rest.
No cloud, no pull requests, no accounts, no logs to read.

## What it does — and honestly doesn't
It makes agent work **unsurprising and recoverable**, not **guaranteed correct**.

- It closes the gap that makes an agent feel *less* trustworthy than a human coder: it flags
  before it expands, keeps continuity in the repo instead of in a chat, asks in terms you can
  judge, and proves work by running it. That part is real and it's most of your frustration.
- It does **not** guarantee the code is right — that still rests on the tests and the real runs.
  It can't catch the case where an agent is confidently wrong and doesn't flag it. The net for
  that is reversibility plus tests that run against reality, so such a mistake is caught and
  undone rather than shipped.
- Trust grows from the agent's reports matching what it actually did, over many cycles — the way
  you come to trust a reliable colleague, not the way you trust something you built yourself.
  The process earns that over time; this document doesn't grant it.

`/contextcheck` finds gaps an agent can *see*; nothing can certify a repo has "enough." Run it
with two different agents and watch for disagreement — disagreement is a real gap, agreement
proves nothing.
