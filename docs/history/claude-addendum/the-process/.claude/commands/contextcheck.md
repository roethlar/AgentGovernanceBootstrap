---
description: Check whether THIS repo has enough context for an agent to be productive. Produces a gap report — fixes nothing.
argument-hint: [optional - a module/task to focus on, e.g. "the conference room module"]
---
Check whether this repo contains enough information for a competent agent to work productively $ARGUMENTS — WITHOUT any outside chat history or access to the person who built it. FIND and FLAG gaps; never fill them. Don't write code. Don't present a guess as a fact. If you don't know, that is the finding.

Three passes, then one report.

**Pass 1 — Orient from the repo only.** In brief plain English: what is this, what does the relevant part do and is *supposed* to do, and how do you build/run/test it? Then list every question you could NOT answer from the repo, and every point where you had to assume. Be specific.

**Pass 2 — Try to run it.** Using only what the repo documents, build it, run the tests, start the app. Report what worked and what failed. Anything that fails for missing setup/config/credentials/services is a concrete gap — list each and what was missing. Don't invent credentials or connect to anything you shouldn't.

**Pass 3 — Task dry-run (only if a module/task was named).** Produce a PLAN for it plus the questions you'd need answered first — plain English, no code. If the plan is full of "assuming X" or "I'd need to check how Y works," say so; that vagueness is the gap.

**The report — sort every gap into exactly these four buckets:**
1. **Present** — what the repo already gives you (brief).
2. **Missing, owner can likely answer** — questions to ask so the answers get written into the repo.
3. **Missing, environmental** — can't live in the repo (credentials, a live tenant, hardware). Note what's needed and whether the repo says how to get it or run without it.
4. **Missing, possibly unrecorded** — intent/behavior written down nowhere. Flag as risk.

End with one sentence: productive as-is / productive after the owner answers bucket 2 / not productive until something is resolved.

This report finds gaps you can SEE. It cannot find context missing where you wrongly think you understand. Where you felt confident, flag anything you're only moderately sure of.
