# Review: bootstrap-plan.v6.md

**Reviewer:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Reviewed at commit:** `be45d33` (working tree)

Follows `bootstrap-plan-review_v5_claude.md`. v6 is a direct response to that review plus
one new strategic change: PowerShell-first → Python-first.

## Verdict: All six v5 findings resolved. But the Python pivot leaks a new dependency, and the treadmill warning is now overdue.

### v5 findings — all closed

| v5 finding | v6 resolution | Closed? |
|---|---|---|
| 1 (HIGH) `update` write-path dead end | `apply --update --approved-review` added; `update` produces the diff/packet and explicitly routes to `apply --update`. The loop closes. | ✅ |
| 2 (HIGH) grader's "declared scope" undefined | `current-run.md` frontmatter contract added (`task`, `declared_scope.paths`, `allowed_sensitive_paths`, `verification`). Missing frontmatter → `scope unknown`, cannot pass. | ✅ |
| 3 (MED) silent coverage truncation | Manifest `coverage` block (`status/candidate_count/included_count/cap`); truncated → review packet must say the map is partial. | ✅ |
| 4 (MED) facts-vs-guidance conflation | Split into `facts_fresh/facts_outdated` and `guidance_clean/guidance_dirty`, with an explicit "do not collapse these." | ✅ |
| 5 (LOW) packet hash looks like integrity gate | "The packet hash is audit provenance… not a tamper-proof integrity check." | ✅ |
| 6 (LOW) test-clean reports local-only as missing | "Their absence is not a failure… report them as intentionally missing." | ✅ |

That is a clean sweep, and the fixes are the *right* fixes, not hand-waves. The spec is now
internally consistent in every place v5 flagged.

## New findings on v6

### 1. (HIGH) The Python pivot leaked Python into the target-repo artifacts — that breaks portability.

The decision to implement *the bootstrap tool* in Python is defensible (one cross-platform
command surface; easy to unit-test). The problem is that v6 also changed artifacts that run
**inside the bootstrapped repo**, coupling every target repo to a Python runtime:

- `grade-agent-run.py` (was `.ps1`)
- `.agents/checks.py` "when Python is the preferred verification wrapper"
- test-current/test-clean now print `python <repo>/.agents/grade-agent-run.py ...`

The bootstrap tool's implementation language and the *generated grader/checks language* are
two different decisions. A Go shop, a .NET shop, or a JS monorepo now inherits a Python
prerequisite just to run the grader on its own CI/dev machines — on a repo that may have no
other Python. That contradicts the plan's core "portable, fits the repo's actual
mechanics" principle (and Derived Verification: "Do not invent checks that are not supported
by the repo").

Fix: state that the **tool** is Python, but the **generated grader/checks language tracks
the target repo's environment** (pick `.ps1`/`.sh`/`.py` from observed repo conventions, or
emit a thin launcher in the repo's native shell). The grader's logic can still live in the
Python package and be invoked by a small repo-native wrapper — but don't hard-require
`python` in every bootstrapped repo.

### 2. (MED) No installation/distribution story for `python -m agent_bootstrap`.

The command form assumes the package is importable, but nothing says how the human gets it
there (pipx, `pip install`, a venv, a vendored checkout). For a tool whose whole job is
portability across machines, "how is it installed on a fresh macOS/Linux/Windows box"
deserves one line in Implementation Surface. Recommend pipx or a pinned venv so the tool's
own deps don't pollute target environments.

### 3. (LOW) `verification.ran` is a self-reported claim, and Layer 1 grades the claim, not the act.

Layer 1 asks "Did the agent run the verification entry point?" but can only read
`verification.ran: true` from frontmatter the agent itself wrote. That's acceptable (it's
the only machine-decidable signal available), but the spec should say plainly that Layer 1
verifies *presence and consistency of the declaration*, not that the command actually
executed. Otherwise it reads as a stronger guarantee than it is — the same
assert-without-mechanism smell earlier versions worked to remove.

### 4. (LOW) `coverage` is a single block but monorepos are per-project elsewhere.

Discovery Budget caps are "per project" and playbooks/checks can be per-project, but the
`coverage` schema is one flat block. For a monorepo, one repo-global coverage number hides
which package was truncated. Make `coverage` per-project when project boundaries are
detected.

## Meta: this is the third review in a row telling you to stop planning.

v4-claude and v5-claude both said it; v6 makes it sharper, not softer. The PowerShell→Python
decision is exactly the kind of choice that should be made in the first 20 minutes of
*writing code*, not enshrined in a sixth versioned plan doc. v6 changed essentially nothing
about the design — it resolved my six clarifications and swapped the implementation language.
That is a commit message and a `pyproject.toml`, not a plan revision.

The spec is done. Findings 1–4 above are real but small: decide finding 1 inline (it's a
one-paragraph correction), note 2–4 as implementation directives, and build.

## Recommendation

1. Correct finding 1 in place (target-repo artifact language ≠ tool language) — this one
   matters because it lands in tracked repos and is annoying to undo later.
2. Note findings 2–4 as implementation directives; they don't need a v7.
3. Build the order v6 already prescribes: Python package + CLI dispatch → `discover`
   (manifest-only) + tests → preview run against a real pilot repo → in-repo agent drafts
   guidance → then `apply`/checks/grader.
4. **Do not open a v7 for prose.** The next artifact in this folder should be a Python
   module with a passing test, not `bootstrap-plan.v7.md`.
