# Install — hand this to an agent

Copy everything between the lines to an agent working in the target repo.

------------------------------------------------------------
Install this process kit into this repo, and follow the kit's own scope contract while you do it:
show me a plain-English summary of what you added, changed, and removed before you commit, and
change nothing beyond these steps.

1. Copy the `.claude/commands/` files into the repo.

2. Agent guide: if the repo has no agent guide, add `AGENTS.md` from the kit. If it already has an
   `AGENTS.md` or `CLAUDE.md`, MERGE the kit's guide into it — keep the repo's real specifics, fold
   in the scope contract and the "done means you ran it" rule, and where a similar rule already
   exists (e.g. a plan-first / scope rule), reconcile into ONE rule. Do not leave two overlapping
   versions. Report the merge in plain words.

3. Memory: add `.agents/state.md` and `.agents/decisions.md` from the kit if absent. Then FILL IN
   `.agents/state.md` by reading the actual project — current state, what's next, and the real
   build and test commands. If the repo has long journals or scattered status docs, compress their
   current truth into `state.md` and move the old files into an `archive/` folder (don't delete
   history). Show me the filled-in state for approval.

4. Run `/contextcheck` and show me the gap report.

Don't write feature code during install. This is setup only.
------------------------------------------------------------
