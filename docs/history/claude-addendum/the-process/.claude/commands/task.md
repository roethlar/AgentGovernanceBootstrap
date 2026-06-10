---
description: Work the next task end to end and report back in plain English.
argument-hint: [optional - which task; else take the next from the state/plan]
---
1. Read `.agents/state.md` and any active plan FIRST $ARGUMENTS. Don't reconstruct state from anything else. If you can't tell what's next, ask.
2. Scope contract (see `AGENTS.md`): if doing this well needs anything beyond the literal request, sort it before proceeding — ask first / take the safe default and say so / name the risk in plain words.
3. Do the work.
4. Done means you RAN it: build it, run the tests, and exercise the actual change against reality. For anything that can't be verified here (live service, another OS, hardware), say so and don't claim it works.
5. Report in plain English: what you did, what you deliberately did NOT touch and why, what you OBSERVED when you ran it, anything you're unsure of, anything done beyond the ask. No code, no logs.
6. Update `.agents/state.md` so the next session starts oriented.
