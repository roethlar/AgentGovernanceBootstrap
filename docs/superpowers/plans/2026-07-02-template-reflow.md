# Reflow AGENTS.template.md (drop hard line-wraps) + T1 hook-trust trim

Status: Approved by owner 2026-07-02 (explicit go on the measured proposal).
Slices below; commit map filled as they land.

## Why this plan exists

The 2026-07-01 verbatim-template decision removed every consumer of the
template's hard line-wrapping in target repos: the installed `AGENTS.md` is
never hand-edited, never hunk-diffed (reconciliation is byte-compare +
replace-whole), and is read raw by models, which are indifferent to line
width. The wrapping's only remaining cost is tokens: each wrapped
continuation line spends a newline + indent on every session of every
governed repo.

Measured 2026-07-02 with the token-counting API (`count_tokens`,
`claude-opus-4-8` — the current Opus/Fable tokenizer):

- wrapped `templates/AGENTS.template.md`: 3,873 tokens
- reflowed equivalent (owner-produced test file, verified byte-identical
  after whitespace normalization): 3,700 tokens
- saving: **173 tokens, −4.5%**, lossless

Accepted cost, owner-weighed: future template edits in this toolkit repo
produce paragraph-blob diffs (the template source is the one place the file
is still hand-edited).

The bump also executes **T1** from the 2026-07-01 verbosity-sweep report
(recorded in `.agents/state.md`): trim the Session Startup hook-trust item by
~30 words, cutting rationale clauses while keeping the behavioral contract
(gated hooks exist; say what they do; trust only on explicit go, only your
own harness; never run another harness's commands or bypass the gate).

## Scope

- `templates/AGENTS.template.md` only. **Not** `repo-guidance.template.md`
  or `procedures/*` (both hand-edited in target repos or here; wrapping keeps
  their diffs reviewable). **Not** this repo's own `AGENTS.md` — it is
  replaced by the pending `/update-governance` run (verbatim-template plan
  slice 5), which will install the new bytes through the sanctioned path.
- Formatting rule going forward (recorded in the 2026-07-02 decision):
  template body text is one line per paragraph / bullet; future edits do not
  re-wrap.

## Slices

- S1 (docs): this plan + decision entry in `.agents/decisions.md`.
  Verification: `git diff --check`. — commit: (fill)
- S2 (code): replace `templates/AGENTS.template.md` with the reflowed text;
  apply the T1 hook-trust trim; bump `templateVersion` to `2026-07-02.1`
  (dotted sub-version keeps the same-day-collision test guard meaningful);
  delete the scratch `templates/Reflowed AGENTS.template.md`.
  Verification: `python3 -m unittest discover -s tests -v`. — commit: (fill)
- S3 (docs): update `.agents/state.md` (slice-5 note: the run installs the
  reflowed `2026-07-02.1` bytes); fill this commit map.
  Verification: `git diff --check`. — commit: (fill)

## T1 wording

Before (~83 words):

> Hook trust: this repo may ship session-start / post-compaction re-ground
> hooks. Many harnesses keep committed hooks inert until the workspace is
> trusted on this machine — a one-time, uncommittable step. If your harness
> gates hooks and they are untrusted, say what they do and run the trust step
> only on an explicit go, only for the harness you are actually in (ask the
> human if unsure). Never run another harness's config or trust commands, and
> never bypass the gate.

After (~57 words):

> Hook trust: this repo may ship re-ground hooks that some harnesses keep
> inert until the workspace is trusted on this machine. If your harness gates
> hooks, say what they do and run the trust step only on an explicit go, only
> for the harness you are in; never run another harness's trust commands, and
> never bypass the gate.

## Non-goals

- No wording changes beyond T1 (the reflow is lossless by construction; the
  whitespace-normalized diff against the current template must stay empty
  except for the T1 passage and the stamp).
- No changes to the remaining verbosity-sweep findings (B*, M*, P*) — those
  still await owner IDs.
