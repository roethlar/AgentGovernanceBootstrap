# Plan: MIT license for the development repo, published to Bixi

Status: DRAFT 2026-07-30 — awaits the owner's go to implement. Rulings in
hand (owner, 2026-07-30): the license is MIT; the copyright line is
"Copyright (c) 2026 Michael Coelho". These rulings lift the license item
out of the deferred release-engineering set in the 2026-07-10
release-posture decision (`.agents/decisions.md`); the rest of that set
(versioned releases, changelogs, CI matrices, signed tags) stays deferred.

## Problem

Neither repo carries a license. The 2026-07-10 release-posture decision
deferred licensing while the toolkit was private, but Bixi has been a
public product repo since the 2026-07-24 first publish and is now the
public feedback inbox — a public repo without a license grants no rights
to anyone. `tools/publish.py` mirrors exactly its `PUBLISH_PATHS` set
(clearing everything but `.git` first), so the product repo can only
carry a license that ships from here; a LICENSE written by hand into the
product checkout would be deleted by the next release.

## Design

One canonical copy at this repo's root, `LICENSE`, holding the MIT text
with the ruled copyright line — the one-canonical-location invariant: the
same terms cover the development repo and the product, so no second copy
under `product/`. `PUBLISH_PATHS` in `tools/publish.py` gains one pair:

```python
("LICENSE", "LICENSE"),
```

with a comment stating why it ships (mirroring clears the product repo;
a public repo needs its license). The file-level pair follows the
`product/README.md` precedent; the preflight missing-member refusal
covers the new pair automatically.

No README changes: GitHub surfaces a root LICENSE on its own, and a
badge or section is outside this ruling.

## Implementation

One commit:

1. `LICENSE` — MIT text, copyright line "Copyright (c) 2026 Michael
   Coelho", at the repo root.
2. `tools/publish.py` — the `PUBLISH_PATHS` pair and comment above.
3. `tests/test_publish.py`:
   - `build_dev_repo` gains a root `LICENSE` (any one-line body).
   - `test_mirrors_publish_set_and_commits` asserts `LICENSE` lands in
     the product repo.
4. `.agents/decisions.md` — new dated entry: MIT license, copyright line,
   license item lifted from the 2026-07-10 deferred set (remainder stays
   deferred), one canonical copy at the root published to Bixi.
5. `.agents/state.md` — `## Now` entry once landed.

## Verification

Interpreter per `.agents/repo-guidance.md` (Verification); on this
machine `py -3` (Python 3.14) per `.agents/machines.md`, with
`PYTHONIOENCODING=utf-8`.

1. `py -3 -m unittest discover -s tests -v` — full suite green.
2. Guard proof: with the new assertion retained, temporarily restore the
   old `PUBLISH_PATHS` (drop the new pair); the mirror test must fail;
   restore; rerun green.
3. `git diff --check`.
4. This plan file: `py -3 -m unittest tests.test_plan_lint -v`.

## Rollout boundary

The license reaches Bixi on the owner's next `publish` word after this
lands. Nothing in `tools/shipped-set.json` changes — governed repos do
not inherit the toolkit's license; repos created or governed by the
toolkit remain their owners' own licensing decisions.
