# Harvest Sweep (run in the bootstrap repo)

Purpose: fold harvested governance rules into the generic templates. Run only
when the owner asks.

Skepticism is the default. An idea earns adoption only if it would have
prevented a specific, citable mistake and the templates do not already cover
it. When in doubt, skip - the owner relies on this filter, not on agent
enthusiasm. Adopting a weak idea pollutes every future bootstrap; skipping a
good one costs nothing, because the report stays where it is.

## How

1. Sync the harvest dropbox before reading it. Its path is in this repo's
   untracked `harvest.config.json`; if that file is absent, there is no dropbox
   on this machine. When it is present, freshen the dropbox from its remote the
   same way Step 0 syncs this toolkit — `git -C <dropbox> ls-remote --exit-code
   <remote> HEAD` for liveness, then `git -C <dropbox> fetch` and `merge
   --ff-only` — because the dropbox's canonical contents are its git history, not
   one checkout; a working copy behind its remote omits pushed reports with no
   signal. If the dropbox is offline, has no remote, or has diverged, proceed but
   state plainly that the harvest view is local-only and unverified rather than
   asserting "no unprocessed reports." Then read the new files in the dropbox.
   Also scan any repo paths the owner names for fallback `.agents/harvest.md`
   files. All cross-repo reading is read-only; the dropbox is the one place this
   session may write outside this repo, and every dropbox write (the
   move-to-`processed/` step) happens on the post-sync tree.
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

## Bug reports

The dropbox also holds bug reports under its `bugs/` folder (filed per
`procedures/file-bug-report.md`). These are defects in this product, not
governance rules, so they are triaged rather than folded into templates:

1. Read the `bugs/` files on the same post-sync tree. Skip any already logged in
   `harvest/processed.md`.
2. For each, confirm the defect still reproduces against current `HEAD` (a report
   may predate a fix). Give the owner a per-report verdict in plain English —
   still-open / already-fixed / fix-now — citing the check that decided it.
3. A "fix-now" verdict is a separate scoped code change under the normal
   plan/approval contract; the sweep itself does not fix code.
4. When a report is handled (fixed, or confirmed obsolete), log one line in
   `harvest/processed.md` and move the file into the dropbox's `processed/`
   subfolder — the same disposition as a handled rules report.
