# Plan: Push Policy — per-repo file + standardized options

Date: 2026-06-27  
Status: Draft — awaiting owner approval

## What and why

The Prime Invariants blanket push-needs-explicit-go rule causes a staleness
trap: commits that live only locally make the remote silently out of date,
directly undercutting the "durable truth lives on the remote" invariant.
The fix is a per-repo push policy file (`.agents/push-policy.md`) that the
Prime Invariants delegate to, with a standardized option set and a default of
explicit-go. Each repo's policy is declared once; the bootstrap process asks
the human at approval time.

Decided: option (a) from the 2026-06-26 Open Decision, sharpened: no
blast-radius tiering in the template — the template just points to the policy
file. The options are standardized so the bootstrap process can present them
mechanically.

## Standardized push policy options

| ID | Policy text (canonical, written verbatim into `.agents/push-policy.md`) |
|----|-------------------------------------------------------------------------|
| 1 — `always` | Always push after every commit. |
| 2 — `operators` | Push automatically after operator-invoked commits (handoff, decision, drift, plan); ask for all others. |
| 3 — `docs` | Push automatically after docs/state-only commits; ask for code or tool changes. |
| 4 — `ask` | Always ask before pushing. *(default)* |

The file contains exactly one of these lines (plus an optional comment naming
the option ID) and nothing else. The bootstrap process writes it; agents read
it and follow it literally.

## Changes — one commit per slice

### Slice 1: `templates/push-policy.template.md` (new file)

New template file. Content:

```
<!-- push-policy: ask -->
Always ask before pushing.
```

The comment is machine-readable by `discover.py` (future); the prose is what
agents read. Default is option 4 (`ask`).

### Slice 2: `templates/AGENTS.template.md` — Prime Invariants push clause

Replace:

> Commit each slice as it lands; never leave finished work uncommitted. Push,
> history-rewrite, and destructive or outward-facing actions need an explicit
> go — pushing publishes.

With:

> Commit each slice as it lands; never leave finished work uncommitted.
> History-rewrite and destructive or outward-facing actions always need an
> explicit go. Push policy: see `.agents/push-policy.md`.

Bump `templateVersion`: `2026-06-25.2` → `2026-06-27`.

### Slice 3: `templates/approval-summary.template.md` — Push Policy section

Add a **Push Policy** section between "Files Proposed For Approval" and "Risks,
Limitations, Or Open Questions":

```
## Push Policy

<State the push policy that will be written to `.agents/push-policy.md`.
Default is option 4 (ask). If the owner named a different option at approval
time, record it here. Options:
  1 — always: Always push after every commit.
  2 — operators: Push automatically after operator-invoked commits (handoff,
      decision, drift, plan); ask for all others.
  3 — docs: Push automatically after docs/state-only commits; ask for code
      or tool changes.
  4 — ask: Always ask before pushing. (default)
Present this as: "Push policy will be set to: [option]. Change? (1/2/3/4, or
Enter to accept default)">
```

Also update the closing note on line 79 of the current template:

Replace:
> Nothing is pushed; pushing remains the owner's action.

With:
> Nothing is pushed yet; the push policy written by this run governs all
> subsequent commits.

### Slice 4: `procedures/bootstrap.md` — approval step push wording

In Step 10, replace:

> Never push unprompted: after committing, ask once, in one line, whether to
> push - naming the repo's remotes when there is more than one - and push only
> what the owner names.

With:

> After committing, consult `.agents/push-policy.md`. If policy is `always`,
> push immediately (naming the remote). If policy is `operators` and this
> commit is operator-invoked, push immediately. Otherwise ask once, in one
> line, naming the repo's remotes when there is more than one.

### Slice 5: `.agents/decisions.md` — close Open Decision

Move the 2026-06-26 Open Decision to Adopted. Record:
- Decision: option (a), implemented as a per-repo `.agents/push-policy.md`
  with four standardized options; default is `ask`; template delegates to
  the file
- `templateVersion` bumped to 2026-06-27
- This repo's policy set by self-application (dogfood run), not direct edit

### Slice 6: dogfood — bootstrap this repo

Run the bootstrap update route on this repo. The approval summary will include
the push policy question; owner selects option 1 (`always`). This writes
`.agents/push-policy.md` to this repo with "Always push after every commit."
and commits it through the normal approval flow.

This is the only way `.agents/push-policy.md` lands in this repo — not a
direct edit.

## Verification

- `python3 -m unittest discover -s tests -v` after slices 1–4 (template and
  procedure changes touch content the tests may cover).
- Revert-the-fix discipline: if any test guards `templateVersion`, confirm it
  fails before the bump and passes after.
- Slice 5 (decisions.md): `git diff --check`.
- Slice 6 (dogfood): the approval summary is the verification.

## Commit order

Slices 1–5 are product changes; commit each separately in order.
Slice 6 is a separate bootstrap session (a self-application run of the updated
product), producing its own scoped commit.

## Out of scope

- `discover.py` reading the `push-policy` comment (future, not this plan)
- Update-route reconciliation of existing bootstrapped repos (they keep
  whatever push behavior they have until their next update run, which will
  draft the file and ask)
- `file-to-dropbox.md` push gate (that is a different repo; its gate stays)
