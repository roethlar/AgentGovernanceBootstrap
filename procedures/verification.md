# Fresh-Eyes Verification

Purpose: prove the drafted guidance works for an agent with zero context - the
exact situation it exists for. Run after drafting, before the approval summary.
Required for migration runs; recommended for substantial greenfield runs.

## How

1. Start a fresh agent context with no knowledge of this session (a subagent
   with a clean context, or a new session). Do not summarize the migration for
   it - that would defeat the test.
2. Give it only this prompt:

   "Read the draft guidance under .bootstrap-tmp/drafts/ in this repo as if those
   files were at their final paths (drafts/AGENTS.md is AGENTS.md, drafts/.agents/
   is .agents/). Using only those files plus the repo itself, answer: (1) What is
   this project? (2) What is true right now - active work, blockers? (3) What
   should happen next? (4) How are code changes verified before completion?
   (5) Which file would you update at the end of a work session, and how would
   you record a new durable decision? Answer concisely. If any answer is not
   discoverable from the files, say MISSING and name what you needed."

3. Grade the answers yourself against the drafts. Any MISSING, wrong, or
   guessed answer is a defect in the drafts, not in the fresh agent.
4. Fix the drafts, then re-run the test once with another fresh context.
5. Record the outcome as one plain-English sentence for the approval summary,
   for example: "A fresh agent given only the new files correctly answered what
   the project is, what is in progress, what comes next, and how changes are
   verified." If the second run still has defects, say so honestly and list them
   as risks in the approval summary instead of hiding them.
