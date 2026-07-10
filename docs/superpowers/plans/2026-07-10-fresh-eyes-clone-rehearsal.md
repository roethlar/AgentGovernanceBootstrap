# fresh-eyes verification: throwaway-clone rehearsal as the default form

Status: DRAFT 2026-07-10 — awaiting owner approval; no implementation
authorized. Drafted on owner instruction ("make whatever plans are needed to
address anything new", 2026-07-10).

## Why this plan exists

Two independent defects in the current fresh-eyes form
(`procedures/verification.md`, "How"):

1. **GitHub issue #3** (2026-07-09, BlitAdmin_UIs evidence): the fresh agent
   reads drafts under `.bootstrap-tmp/drafts/` "as if those files were at
   their final paths". The drafted `.agents` content sits in a dot-named
   subdirectory (`drafts/.agents/`), which default directory listings omit,
   so a fresh agent on a dotfile-hiding harness graded the entire drafted
   set MISSING while the files existed on disk — a false-fail costing the
   one permitted re-run. In the live incident, the re-run pointed at a
   throwaway clone with drafts at final paths answered all six questions
   correctly.
2. **Holistic review finding H6** (untracked review, GPT-5.6-Sol,
   2026-07-09; verified against the procedures 2026-07-10): the prompt
   tells the reviewer "drafts/AGENTS.md is AGENTS.md", but no such draft
   exists in the defined flow — bootstrap Step 4 explicitly never drafts the
   shipped `AGENTS.md` (`tools/refresh.py` is its single installer). The
   required check therefore never inspects the constitution that will
   actually be installed, and on a migration the harness may auto-load the
   old resident `AGENTS.md` into the fresh agent's context, contaminating
   the check with the governance being replaced.

The same change fixes both: run the check in a throwaway clone that looks
like the post-bootstrap repo — real paths (no "as if" mapping, no dot-hidden
drafts staging area) and the real installed constitution (refresh actually
run), which also rehearses the install itself, including refresh's
validation, FLAG lines, and lint, before the owner ever approves.

## Design

Rewrite `procedures/verification.md` "How" so the default form is:

1. Clone the target repo to a throwaway directory (`git clone <target>
   <scratch>`; local clone, no network). On a migration, apply the prepared
   supersession banners in the clone.
2. Run `<probed-python> <toolkit>/tools/refresh.py --stage-only <scratch>`
   to install the shipped set there — the real `AGENTS.md`, shims, skills,
   wrappers. Surface any FLAG line: a flag in the rehearsal is a bootstrap
   defect to resolve before the approval summary, not noise.
3. Copy the judgment drafts from `.bootstrap-tmp/drafts/` to their final
   paths in the clone.
4. Start the fresh agent IN the clone with the existing six-question prompt,
   minus the "as if at final paths" mapping — the agent reads the repo as
   any future agent would. Grading, the one-rerun rule, and the
   plain-English result sentence stay as they are.
5. The clone is scratch: never committed, never pushed, deleted after
   grading (its staged index is discarded with it).

Fallback form (when the harness genuinely cannot make a clone or run
Python): the current drafts-in-place reading, amended with an explicit
warning that `drafts/.agents/` is dot-named and hidden from default
listings — the prompt must instruct the agent to enumerate it explicitly.
The recorded result must name which form ran.

`procedures/bootstrap.md` Step 5.2 keeps pointing at
`procedures/verification.md`; its one-line description is checked for
wording that assumes the drafts-only form and adjusted if needed.

## Slices

1. Rewrite `procedures/verification.md` (default clone form, fallback form,
   prompt update); align bootstrap Step 5.2 wording. Docs-only.
2. Bookkeeping: note issue #3 ready to close (owner go for `gh issue
   close`); state rotation if the summary references it.

## Verification

Docs-only change: `git diff --check`. Behavioral bite proof (manual, before
closing issue #3): drive one bootstrap rehearsal in a scratch repo per the
new form and confirm a fresh agent finds the `.agents` files and the
installed `AGENTS.md`; the false-fail incident's failure mode (MISSING on
existing drafts) cannot recur since no dot-hidden staging dir is read.

## Non-goals and risks

- The scope warning ("discoverability and consistency, NOT a fact check")
  is untouched.
- Fresh-eyes independence (same-model-vs-foreign-model, chat-context
  isolation — the rest of review H6) stays an open design question for the
  owner; this plan fixes what the reviewer reads, not who the reviewer is.
- The clone form costs a local `git clone` plus one refresh run per
  bootstrap — seconds on repos of the fleet's size; large repos can use
  `--depth 1`... a shallow local clone is still a real tree, acceptable.
- Running refresh in the clone before owner approval mutates only the
  scratch clone, never the target; the wording must say so explicitly so
  the nothing-changes-before-approval promise stays narrow and true
  (review M12's boundary point, adopted here for the clone).

Provenance: GitHub issue #3 (2026-07-09, BlitAdmin_UIs live false-fail and
successful clone-form re-run); untracked holistic review H6 (2026-07-09),
verified against `procedures/verification.md` and `procedures/bootstrap.md`
Step 4, 2026-07-10; owner instruction 2026-07-10 to draft plans for the new
findings.
