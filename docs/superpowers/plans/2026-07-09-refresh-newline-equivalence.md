# refresh.py: trailing-newline equivalence in artifact matching + shims ship with a final newline (issue #1)

Status: DONE 2026-07-09 (owner approved same day). Commit map: slice 1 =
`0151f5b` (comparator equivalence + five tests, guard-proven: the old
comparator fails all four positive tests), slice 2 = `05e6c1e` (shim final
newlines + shipped-source newline invariant, red→green proven), slice 3 =
the docs/bookkeeping commit carrying this Status. Suite 41 green; post-fix
self-refresh of this repo: "nothing to do - repo is current" as predicted.
Issue #1 comment/close still awaits an explicit owner go. This plan
implemented issue #1's fixes 1 and 2 (fix 3 deliberately not adopted — see
Non-goals).

## Why this plan exists

GitHub issue #1 (owner-filed 2026-07-09): `tools/refresh.py` flags artifacts
as owner-modified when the only difference from canonical is a trailing final
newline, and a FLAG never self-heals — every refresh re-flags until a human
deletes the file and re-runs. Three occurrences of the class are on record:

- Powershell-Token-Killer refresh 2026-07-09 (toolkit `ce0db15`): `CLAUDE.md`
  = `@AGENTS.md` + LF (11 bytes) flagged against the 10-byte canonical;
  cleared only by the delete-and-rerun dance (`03d9162` → `719c200` there).
- ai-rpg-engine rollout 2026-07-08: "CLAUDE.md normalized — it differed only
  by a trailing newline" (hand-fix at the leaf).
- This repo's own `CLAUDE.md`, same day: normalized in `b9a867c` after the
  first live lint caught it.

Verified mechanism (2026-07-09, this session):

- `norm()` (`tools/refresh.py:57`) normalizes CRLF→LF only; it never touches
  a trailing final newline. A newline-only-different target misses the
  current match (`:126`), misses `formerly` (`:128`), and lands in the
  terminal `"owner-modified; left untouched"` branch (`:138`).
- Exactly two shipped sources lack a final newline —
  `templates/shims/CLAUDE.template.md` and `GEMINI.template.md` (all 17
  others end with `\n`), so the drift pressure from insert-final-newline
  tooling bites precisely on the shims.
- Hash confirmation: both shims' `formerly` lists contain
  `918b1c90…` = sha256 of the *current* 10-byte content, but the LF
  variant (`336cc4fb…` = sha256 of `@AGENTS.md` + LF) is recorded nowhere —
  which is exactly why PTK's file matched nothing.

Correction to the issue as filed: the CRLF half of the claimed class is
already handled by `norm()`; only the trailing-final-newline case produces
the false FLAG.

## Design decision: equivalence at compare time, never a hash-scheme migration

Two ways to implement the issue's fix 1; the choice matters because
`shipped-set.json` carries ~60 recorded `formerly` hashes (42 on `AGENTS.md`
alone) all computed under the current `nhash`:

- **(a) Rejected — change `norm()` to also strip a trailing newline.** That
  silently invalidates every recorded hash whose historical bytes ended with
  `\n` (nearly all), breaking stale-artifact updates and retired-file
  removal everywhere. Repairing it means regenerating every hash from git
  history, and any recorded hash that can't be matched back to a historical
  blob is unrecoverable.
- **(b) Chosen — keep `nhash`/`norm` and the recorded hashes untouched;
  match against a two-candidate hash set of the target.** Define
  `E(x)` = `norm(x)` with at most one trailing `\n` stripped (the
  equivalence stem). A target `t` matches a recorded hash `h` iff
  `h ∈ { sha256(E(t)), sha256(E(t) + b"\n") }` — this covers every
  historical byte-form `H` equivalent to `t`, because `norm(H)` is by
  construction either `E(H)` or `E(H) + b"\n"`. The current-template check
  becomes plain stem equality, `E(t) == E(src)`. Every existing
  `formerly` entry stays valid; the maintenance rule in the
  `shipped-set.json` comment is unchanged.

Equivalence is deliberately tight: content modulo CRLF and **at most one**
trailing final newline. `X\n\n` vs `X\n` is a real difference and still
flags.

Also considered and rejected: just appending `336cc4fb…` to the shims'
`formerly` lists. It is per-artifact whack-a-mole (every future version of
every artifact would need newline-variant hashes forever), and it "fixes" the
false positive by *rewriting* an equivalent file instead of recognizing it as
current.

## Slice 1 — comparator equivalence (`tools/refresh.py` + `tests/test_refresh.py`)

Code:

- Add `_stem(data)` (norm + strip at most one trailing `\n`) and
  `candidate_hashes(data)` (the two-hash set above).
- `classify()`: current-check via `_stem(tgt) == _stem(src)`; the
  `formerly` check and the retired-artifact check via candidate-set
  intersection with the recorded lists. `nhash()` stays as-is — it remains
  the maintenance-rule hash function.
- Update the module docstring and the `shipped-set.json` `"comment"` field:
  matching is "newline-equivalent (CRLF → LF, at most one trailing final
  newline)" rather than plain CRLF-normalized.

Tests — the fixture toolkit gains a no-final-newline shim artifact
(source content `@AGENTS.md`, no trailing newline, target `CLAUDE.md`,
class replace-if-unmodified) to mirror the real bug:

1. **Issue repro:** installed shim + appended `\n`, committed → classifies
   current: no FLAG, bytes untouched, second refresh is "nothing to do".
2. **Symmetric direction:** `tool.md` present as canonical *minus* its final
   newline → current, no FLAG.
3. **Formerly + drift:** `tool.md` = formerly-shipped content minus its
   trailing newline → still recognized, updates to current (proves
   candidate-set matching against recorded hashes).
4. **Retired + drift:** `old-hook.py` = retired content minus its trailing
   newline → still removed.
5. **Boundary negative:** `tool.md` = canonical + a second trailing newline
   → still FLAGs (equivalence stops at one newline).

Guard proof: temporarily revert the `classify()` matching change, confirm
tests 1–4 fail, restore, confirm the full suite passes.

## Slice 2 — shim templates ship with a final newline (+ shipped-set integrity test)

- `templates/shims/CLAUDE.template.md` and `GEMINI.template.md`:
  `@AGENTS.md` → `@AGENTS.md` + LF (the issue's fix 2 — POSIX convention,
  the attractor the ecosystem's tooling converges toward).
- Maintenance rule (shipped-set.json comment; unconditional): the outgoing
  version's hash must be in `formerly` in the same commit. It already is —
  `918b1c90…` sits in both lists — so this slice verifies rather than
  appends; noted here so the rule is visibly honored, not skipped.
- New test in `tests/test_templates.py`: every artifact source named in
  `shipped-set.json` ends with `b"\n"` — the durable guard against
  reintroducing a no-final-newline source. Guard proof: with the template
  byte-change stashed, the test fails; restored, the suite passes.

Deployment effect: repos holding either the 10-byte or the 11-byte shim
classify as current under slice 1 (same stem) — no churn, no flags, no
rewrite. Fresh installs get the newline-terminated bytes.

## Slice 3 — docs, self-refresh, bookkeeping

- `docs/design.md` (~:69): reword byte-match language to the equivalence
  wording. Docs-only; `git diff --check`.
- Self-refresh this repo (Earned Practices: run the refresh after template
  changes). Expected outcome: "nothing to do" — this repo's 10-byte
  `CLAUDE.md` is equivalence-current; record the actual outcome.
- `.agents/state.md`: close the issue-#1 Next item, roll the as-of forward.
- **Owner-gated (explicit go required, outward-facing):** comment on and
  close GitHub issue #1 citing the landed commits.

## Verification

Full suite per `.agents/repo-guidance.md` (Verification): from Git Bash,
`py -3 -m unittest discover -s tests -v` — after every slice, plus the two
guard proofs above. Slice 3's doc edits: `git diff --check`.

## Non-goals and risks

- **Auto-heal (issue fix 3) is not adopted.** With equivalence in place a
  newline-only-different file classifies current and is left byte-untouched —
  the same stance the existing CRLF design takes
  (`test_crlf_checkout_of_current_content_is_treated_current` asserts bytes
  stay untouched). Rewriting to canonical bytes would churn CRLF working
  copies on Windows on every refresh, fighting git's own line-ending
  handling. Revisit only if byte-convergence is ever independently needed.
- The `AGENTS.md` replace-whole path gains the same tolerance: a
  template-current `AGENTS.md` that gained/lost a final newline reads as
  current instead of drawing the foreign-file flag — strictly fewer false
  positives; genuinely hand-edited files still refuse exactly as before.
- Recorded-hash semantics are untouched: no regeneration, no migration, the
  maintenance rule keeps working verbatim.

Provenance: GitHub issue #1 (this repo, owner-filed 2026-07-09). The shim
content change's provenance under the no-shipped-rule-without-provenance
standing rule is that issue.
