# Review: bootstrap-plan.v5.md

**Reviewer:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Reviewed at commit:** `be45d33` (working tree)

Follows `bootstrap-plan-review_v4_claude.md` and `_v4_gemini.md`. Focus: did v5's
packet-removal resolve the open residuals, and what (if anything) blocks coding now.

## Verdict: The big change was right. v5 resolved all four v4 residuals — mostly by deletion.

Removing the content-packet design is the strongest single edit in the whole version
history. It collapsed three hard problems into "don't copy contents, point instead":

| v4 residual | How v5 disposes of it |
|---|---|
| 1. Secret-scan paradox (never-read vs redact-output) | **Gone.** No artifact contains source contents, so there is no output to redact. Secret handling reduces to "flag paths, don't read flagged, don't write secret values." Honest and achievable. |
| 2. Approval provenance asserted without mechanism | **Fixed.** Apply Semantics now states the act of passing `--approved-review` *is* approval, and records path + packet hash + user + timestamp + repo. |
| 3. Precedence table vs Evidence Classes out of sync | **Fixed.** `executed_verification_result` is now both an evidence class and precedence #2; the two lists are consistent (9 entries, same set). |
| 4. "Validate output for unsupported claims" mislabeled deterministic | **Gone.** No output packet. Grader Layer 1 is now scoped to genuinely machine-decidable signals. |

This is the rare revision that *removes* scope to close gaps. Approve the direction.

## Findings on v5 itself

### 1. (HIGH) The `update` write-path is a dead end — the mode loop doesn't close.

`apply` "refuses if durable guidance already exists and routes to `update`." But `update`
only "produce[s] a proposed diff. Never silently overwrite." Nothing in the spec lets an
*approved* update actually be written. So: first bootstrap works (`apply`), but every
subsequent change has no documented path to land. Either `update` must end by handing an
approved diff to `apply` (e.g., `apply --update --approved-review <path>`), or `apply`
needs a guarded overwrite mode. Pick one and write it down — this is the same
assert-without-mechanism class v4 existed to kill, just relocated to the second run.

### 2. (HIGH) The deterministic grader depends on "declared task scope" that is never defined.

Grader Layer 1 checks "Did changes stay within the declared task scope, based on
changed-file set versus declared scope?" and "Were likely-sensitive files modified without
being declared?" Both require a **machine-readable declared scope**, but nothing in the
plan says where it comes from or what format it is. The test prompt is free English; the
grader can't diff against prose. Define the scope-declaration artifact (a path glob list
the agent must emit, e.g. into `current-run.md` frontmatter) or Layer 1 cannot run.

### 3. (MEDIUM) Discovery Budget can truncate coverage with no "incomplete" signal.

The budget caps files-read and playbooks per project and says "summarize directories." Good
for bounding cost. But there's no required flag in the manifest stating *coverage was
truncated* when a repo exceeds budget. Silent truncation reads downstream as "everything
was covered" — the exact failure the v4 gemini review warned about for staleness. Add a
manifest field like `coverage: complete | truncated (cap=N, candidates=M)` so the in-repo
agent and reviewer know the map is partial.

### 4. (MEDIUM) Folding "canonical guidance" into fact-bearing paths conflates two different changes.

Outdated-facts inputs include "canonical guidance, adapter templates." That means editing a
playbook typo flips the verdict to `outdated`, even though no *repo fact* changed. The whole
point of the section is to separate "repo facts went stale" from "our guidance changed."
Either (a) state explicitly that any guidance edit also requires re-validation (defensible,
but say so), or (b) split the verdict: `facts_outdated` (CI/build/test/package/structure
changed) vs `guidance_dirty` (our own artifacts changed since stamp). Right now one verdict
carries two meanings.

### 5. (LOW–MED) The approval "packet hash" looks like an integrity gate but isn't one.

Apply records the packet hash, which is good audit provenance. But a reader may assume it
*verifies* the packet wasn't tampered with — it can't, because the human is expected to edit
the packet (answer open questions) as part of approving it. State plainly: the hash is for
audit/traceability of *what was approved*, not a tamper check against discovery's output.

### 6. (LOW) `test-clean` vs `install-derived`/`missing` interaction is underspecified.

A local `git clone` clean copy correctly drops local-only and install-derived files — that's
the test's value. But discovery on the clean copy will then legitimately report those paths
as `missing`. The plan should say test-clean must treat "missing because
local-only/install-derived" as expected, not a failure, so the clean test doesn't produce
false alarms. The custody categories exist; the cross-reference doesn't.

## Meta: this is the version to stop on.

The v4 review's central warning — five plans, four reviews, zero lines of code — is now
*more* pressing, not less, because v5 removed the complexity that justified further design.
Findings 1 and 2 are real and must be decided, but both are ~15-minute spec decisions or,
better, answered by writing the code. Findings 3–6 are clarifications that can ride along.

Recommendation, unchanged in spirit from the v4 review:

1. Decide findings 1 and 2 inline (they're small). Note 3–6 as implementation directives.
2. Build the order v5 already prescribes: dispatcher → `discover` (manifest-only) → preview
   run against a real pilot repo → in-repo agent drafts guidance → then `apply`/checks/grader.
3. Do not open a v6 for prose. The next artifact should be `Discover.ps1`, not `bootstrap-plan.v6.md`.
