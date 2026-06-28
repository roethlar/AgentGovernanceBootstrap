## Authorized execution mode

Default mode is interactive-governed mode: for non-trivial code changes, write a short plan before editing.

Authorized execution mode begins when the human explicitly delegates a bounded task with words such as "go", "implement", "fix it", "make the change", "run the playbook", or an equivalent instruction. In authorized execution mode, the plan gate is satisfied by writing a concise plan before the first edit, then executing within the delegated scope.

Authorized execution mode does not authorize:

- destructive git operations
- history rewrite or force-push
- credential, secret, private-key, or token access
- production, cloud, deployment, billing, or outward-facing mutations
- broad scope expansion beyond the requested task
- disabling tests, guards, validation, or checks without explicit provenance review

Stop and ask only when the requested behavior is ambiguous, the plan exceeds delegated scope, verification cannot be run, or progress stalls without a new verifiable delta.

## Change loop

For non-trivial repository changes, define a compact change contract before editing:

- requested outcome
- acceptance criteria
- non-goals
- likely files/subsystems
- fastest relevant verification command
- broader verification command, if known
- applicable risks or quality dimensions

Then execute the smallest loop that can prove the change:

1. localize the relevant code and tests
2. reproduce or characterize the current behavior when practical
3. patch the narrowest implementation point
4. run targeted verification
5. classify any failure before editing again
6. retry only with a new observable delta
7. review the diff before stopping

Do not stop after a code change until the change contract is either satisfied or blocked with a concrete reason.

## Completion report

After a code change, the final response must substantively report:

- what changed
- files changed
- verification commands and results
- checks not run and why
- remaining risk or blocker

Do not merely name these headings; provide enough content for a reviewer to know what was actually changed and verified.
