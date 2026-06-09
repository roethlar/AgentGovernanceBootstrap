# Review: bootstrap-plan.v4.md

**Reviewer:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Reviewed at commit:** `be45d33` (working tree)

Companion review to `bootstrap-plan-review_v4_gemini.md` (signed "Antigravity"). This one
focuses on whether a v5 is warranted and what should happen instead.

## Verdict: No v5 needed. The plan has converged.

v4 closed the last substantive gaps from the v3 review (`bootstrap-plan-review_claude.md`),
and did it by *removing over-promises* rather than adding scope — the right move at this
stage.

### What v4 got right (the three best changes)

- **LLM input/output packet contract.** This is the real fix. v3 claimed "the script
  controls what the LLM reads"; v4 admits a script cannot control a chat model and instead
  defines *safe inputs in → validated outputs out*. Correct mental model.
- **Staged-apply with best-effort rollback** replaces v3's "atomic write as a unit."
  Honest — true cross-filesystem atomicity is a fiction, especially on Windows.
- **Narrowed secret guarantee** — "holds when the packet workflow is followed; cannot
  promise impossibility if someone bypasses it." Right epistemic posture, not security
  theater.

The Gemini/Antigravity review is "Highly Approved" and its four findings (A–D) are
**implementation directives, not spec gaps**: exact-match redaction, NTFS rename + retry on
file locks, concrete `git diff` staleness thresholds, monorepo marker files. None requires
a spec rewrite. That review states it itself: "No major architectural modifications are
needed."

## 4 residuals to resolve BEFORE coding (not a full v5 — a clarification pass)

Three the Gemini review missed; one it half-caught.

1. **Secret-scan paradox (Gemini caught it, but its fix contradicts the spec).**
   v4 Secret-Safe Discovery rule #2 says *never read/copy/summarize* deny-listed contents.
   Step #4 says *scan the output packet for secret values and redact*. Gemini's solution —
   load real secret values into memory to build a redaction set — is the only way to catch
   low-entropy secrets, but it **directly violates "never read."** This is a genuine spec
   decision: either explicitly permit *read-into-memory-for-redaction-only, never
   persisted, never sent to the LLM*, or accept that output scanning is pattern-only and
   weaker. The spec must pick one.

2. **Approval provenance is asserted without a mechanism — the same bug class v4 exists to
   kill.** `apply --approved-review <path>` "requires an approved review packet," but
   nothing distinguishes an *approved* packet from the one `discover` auto-generated. What
   marks it approved? If the answer is "the human's act of passing the flag IS the
   approval," that is fine — but say it. As written it is a hope, exactly like v3's
   secret-safety was.

3. **Precedence table and Evidence Classes are out of sync.** v4 (rightly) inserted
   "executed verification results" at precedence #2 and pushed `observed_from_ci` to #5 —
   correctly implementing the CI-is-a-claim nuance. But "executed verification results" is
   not in the Evidence Classes list. Add it as a class, or the two lists disagree.

4. **"Validate output packet for unsupported claims" is judgment work mislabeled as
   deterministic.** The deterministic layer can check *structure* and *secret patterns*; it
   cannot generally decide whether a proposed playbook step is "supported." Scope this down
   to structural + secret validation, or it is another assert-without-mechanism.

## The real risk now: the revision treadmill

Five plan versions and four LLM reviews in one day, zero lines of the actual tool written.
The spec is past the point of useful return — each round now polishes prose about code that
does not exist. The remaining unknowns (redaction paradox, Windows file locks, approval
flow) are **best resolved by writing the code**; implementation will answer them faster and
more truthfully than a sixth reviewer.

## Recommendation

1. Fold the 4 residuals above into a lightweight **v4.1 clarification** (or decide them
   inline — ~20 minutes). Do not open a full v5.
2. **Start building** at Part 3 step 2 (`SecretScan.ps1` + `Discover.ps1`). Secret-safety
   is the one failure that is irreversible once it lands in tracked git, so it goes first.
3. Stop reviewing; start dogfooding against a real pilot repo in preview mode.
