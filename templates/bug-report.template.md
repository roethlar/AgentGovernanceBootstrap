# Bug Report: <short title>, <YYYY-MM-DD>

A confirmed defect in the AgentGovernanceBootstrap product (its code or its
procedures), found while running the bootstrap process.

Discipline (read before writing anything):

- File a report only for a defect you have PROVEN with a citable command or
  observation. A suspected-but-unverified problem is an assumption: label it as
  one and leave it out, or verify it first. An unproven or padded report wastes
  the owner's triage and erodes trust in the dropbox.
- This is a defect in the product, not a record of your own mistake in this run.
  If the procedure or code did the right thing and you misread it, there is no
  bug.
- Use the EXACT headings below. The format is machine-checkable; a noncompliant
  report may be skipped at sweep time and named as skipped.
- One defect per file. File separate reports for separate defects.

## Bug

- **Source:** the repo you were running in when you found it, and its `HEAD`
  commit (e.g. `AgentGovernanceBootstrap @ e751f87`)
- **Severity:** low / medium / high, with one clause on impact
- **Status:** found / fix-proposed / fixed
- **Summary:** one or two plain-English sentences — what breaks, and the
  consequence.
- **Root cause:** the file and line (or procedure section) and the mechanism —
  why it misbehaves.
- **Evidence:** the exact command and its output that proves the defect is
  currently active, not merely plausible. No evidence, no report.
- **Why it slipped through:** which test, guard, or review should have caught it
  and why it didn't (omit if not applicable).
- **Proposed fix:** the change, in one or two sentences, and the bite proof that
  would confirm it (e.g. "revert fix → test X fails; apply → suite passes").
  Write "none yet" if you are only reporting.
- **Affected files:** the paths a fix would touch.
