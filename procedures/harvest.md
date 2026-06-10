# Harvest Sweep (run in the bootstrap repo)

Purpose: fold harvested governance rules into the generic templates. Run only
when the owner asks.

Skepticism is the default. An idea earns adoption only if it would have
prevented a specific, citable mistake and the templates do not already cover
it. When in doubt, skip - the owner relies on this filter, not on agent
enthusiasm. Adopting a weak idea pollutes every future bootstrap; skipping a
good one costs nothing, because the report stays where it is.

## How

1. Read new files in the harvest dropbox repo (its path is in this repo's
   untracked `harvest.config.json`; if that file is absent, there is no
   dropbox on this machine). Also scan any repo paths the owner names for
   fallback `.agents/harvest.md` files. All cross-repo reading is read-only;
   the dropbox is the one place this session may write outside this repo.
2. Skip reports already logged in `harvest/processed.md`. Reject reports that
   do not follow the template's required headings - list each rejected file
   by name; never drop anything silently.
3. For each idea, give a verdict - adopt / adapt / skip, default skip - with
   one plain-English sentence of reasoning.
4. Present all verdicts to the owner in plain English. The owner decides per
   idea.
5. Apply approved edits to `templates/` or `procedures/`. Append one line per
   handled report to `harvest/processed.md` in the same change. In the
   dropbox, move handled files into a `processed/` subfolder.
6. Run this repo's smoke tests if any script changed; template and procedure
   edits are docs-only and need a read-through, not a test run.
