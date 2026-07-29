# Plan: publish mirrors the issue templates into Bixi

Status: DRAFT 2026-07-29 — owner authorized drafting 2026-07-29;
implementation awaits the owner's go.

## Problem

The 2026-07-29 feedback decision (`.agents/decisions.md`) makes Bixi's
GitHub issues the public inbox, but `tools/publish.py`'s `PUBLISH_PATHS`
does not carry `.github/ISSUE_TEMPLATE/`, so:

1. Bixi's web "New issue" form is free-form — the discipline preambles
   (proof-before-filing, redaction, one-defect-per-issue) that
   `.github/ISSUE_TEMPLATE/toolkit-defect.md` and
   `.github/ISSUE_TEMPLATE/harvest-rule.md` encode never reach the
   people now directed to file there.
2. Product clones lack the template files locally, so
   `procedures/bootstrap.md` Step 8's drafting step degrades to its
   plain-body fallback on every product clone.

Both templates are repo-neutral (no development-repo references) and can
ship verbatim.

## Design

Add one pair to `PUBLISH_PATHS` in `tools/publish.py`:

```python
(".github/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE"),
```

with a comment stating the reason (the 2026-07-29 decision routes
feedback to Bixi's issues; the templates carry the filing discipline)
and the boundary: the pair names the subdirectory deliberately, never
all of `.github/`, so development-only CI or workflow files can never
auto-ship. No other publish mechanics change — the preflight
missing-member refusal covers the new pair automatically, the
clear-everything-but-`.git` step already removes dotted directories,
and `dst.parent.mkdir(parents=True, ...)` already creates the nested
`.github/` target.

## Implementation

One commit:

1. `tools/publish.py` — the `PUBLISH_PATHS` pair and comment above.
2. `tests/test_publish.py`:
   - `build_dev_repo` gains `.github/ISSUE_TEMPLATE/defect.md` (any
     one-line body) and a development-only sibling
     `.github/workflows/ci.yml`.
   - `test_mirrors_publish_set_and_commits` asserts
     `.github/ISSUE_TEMPLATE/defect.md` lands in the product repo and
     `.github/workflows` does not cross.

## Verification

Interpreter per `.agents/repo-guidance.md` (Verification); on this
machine `python3.14` per `.agents/machines.md`.

1. `python3.14 -m unittest discover -s tests -v` — full suite green.
2. Guard proof: with the new assertions retained, temporarily restore
   the old `PUBLISH_PATHS` (drop the new pair) in the working tree; the
   mirror test must fail; restore; rerun green.
3. `git diff --check`.
4. This plan file: `python3.14 -m unittest tests.test_plan_lint -v`.

## Rollout boundary

The templates reach Bixi on the owner's next `publish` word after this
lands; GitHub then offers both forms on Bixi's "New issue" page, and
product clones carry the files for Step 8 drafting. No governed-repo
artifact changes — `tools/shipped-set.json` is untouched (the templates
are published, not installed into governed repos).
