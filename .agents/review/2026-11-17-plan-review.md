# Claude review: refresh defects and current boundaries

Status: Two review rounds complete; final scoped verification pending.
Implementation remains unapproved for F5, F6, F7, F8 and G1.

## Dispatch and capability

- Harness: Claude Code CLI 2.1.325.
- Model: `claude-fable-5-2`, supplied literally by the owner. The launch
  envelope and final model usage both identify that model; provider in the
  usage envelope is firstParty.
- Effort: `xhigh`, passed explicitly with the supported CLI flag.
- Pair authority: inline, session-only. The owner specified the exact pair;
  no cached default, provider substitution or competitive/fallback grade
  was inferred. This was the owner's requested whole-plan review.
- Base: `0574fd120820c51646268b4a12bfd41a2e326904`, merge-base with master.
- Reviewed head: `708aef71975941d83edd7236a430039cc0c87f29`.
- Finished: 2026-11-17 13:38:49 UTC; elapsed 352.8 seconds; exit 0.
- Prompt: the openreview question verbatim, plus mechanical coordinates,
  permissions, capability proof and result format. No author-supplied
  defect checklist or desired verdict.
- Tools: repository-confined Read/Glob/Grep; named Git inspection commands;
  exact plan-lint command. Restricted CLI, dontAsk, no MCP servers, write
  tools, delegation, commits, pushes or other mutations. No permission
  denials occurred. No separate smoke review was run.
- Capability proof: README read succeeded; `git rev-parse HEAD` returned
  the reviewed head. The reviewer confirmed the merge-base and diff.
- Reviewer's checks: all 35 plan-lint tests passed; pinned-range
  `git diff --check` passed. It did not rerun the four bug reproductions or
  query GitHub. The review is of the plan, not acceptance of implemented fixes.

## Initial outcome

`openreview claude (claude-fable-5-2 @ xhigh, owner-specified pair) over
0574fd1..708aef7: Acceptable with changes`.

The reviewer found F5–F7 consistent with the source defects and supported
F8's shared planning/preflight/application approach. It judged the initial
G1 scope too broad and insufficiently evidenced for implementation approval.

## Material recommendations and draft disposition

1. **Decide repair/draft collisions.** Accepted for the draft. The revised
   F8 protocol records explicit judgment-draft destinations and excludes
   those paths, including dependent paired moves, from mechanical repair
   planning. Apply reuses the approved exclusions. Bootstrap can copy its
   approved drafts without triggering a predictable second approval round.
2. **Slice F8.** Accepted as two dependency-ordered commits: deterministic
   repair computation first, then a coherent record/apply/bootstrap switch.
   No intermediate public release or premature issue closure.
3. **Separate and tighten G1.** Accepted. It now has its own plan and
   lifecycle. The source repository was found locally and the pre-incident
   layout checked at pinned commits; evidence lives in the incident record.
   Its two proposed behavior changes have exact wording. AGENTS remains
   byte-identical, avoiding displacement of established rules. Binding
   boundaries are inline in startup guidance; only rationale is indirect.
   Existing authority/decision/archive rules are reused, not restated.

These are revisions to unapproved proposals under the owner's planning
request. They do not adopt new operative governance or product policy.

## Smaller observations

- Added F6's ignored, present, untracked foreign-core `--force` case to its
  acceptance criteria. The reviewer inferred this failure path from code;
  the implementation test must prove it.
- Documented F7's residual body-regex false-positive risk. Header protection
  is not presented as a complete semantic Markdown repair.
- F8 input hashes are partly redundant with target HEAD, but remain explicit
  preconditions for audit and verification immediately before application.
- Kept repair diffs in the machine-plan artifact and short reasons in the
  approval summary, preserving its one-screen recommendation.

## Current proposals and next step

- [Refresh defects](../../docs/superpowers/plans/2026-11-17-refresh-defects.md).
- [Current boundaries](../../docs/superpowers/plans/2026-11-17-current-boundaries.md).
- [Incident evidence](incidents/2026-11-17-scope-expansion.md).

Next: verify the revised plan snapshot with the same owner-named Claude
pair, then return the executive summary. Implementation and plan-branch
merge/deletion remain pending their named authority.

## Follow-up: `708aef7..0d072de`

Same harness/model/effort and restricted CLI grant, fresh process, inspecting
only the original material recommendations and adjacent revision concerns.
The launch/final envelopes again identify `claude-fable-5-2`; `xhigh` was
explicitly dispatched. Finished 2026-11-17 13:58:09 UTC, elapsed 339.4 seconds,
exit 0, no permission denials. README read and HEAD command succeeded;
35 plan-lint tests and pinned-range whitespace checking passed. Relative
links resolved and the initial review record was judged accurate.

Verdict: **Acceptable with changes**. Original recommendations addressed
in substance; F5–F7 and narrowed G1 approvable as approaches. The remaining
material concern was legacy carve-out accounting: its ordinary second
refresh could repair just-committed drafts without a corresponding preview.

Draft disposition: use a record captured after rehearsing commit 1, before
installing the shipped set. Standard records retain exact-HEAD pins;
carve-out records require the approved original parent and exact rehearsed
post-commit-1 tree, plus the same operation/input/output pins. Real commit 2
applies that approved record. No unplanned ordinary-refresh fallback.

Smaller follow-up observations incorporated:

- F8 now has computation, runtime protocol, and procedure/rehearsal slices,
  with no intermediate public release.
- Prepared-path handling includes supersession banners and suppresses a
  repo-owned seed when its reviewed draft supplies that same destination.
- G1 wires the section lists in setup/bootstrap, removes the copied question
  count in the summary example, and accepts an evidenced “none established”
  when appropriate.
- The disclosure question was checked: the source repository is public and
  its public main equals the inspected head. The record contains scoped
  public document observations, not private logs or machine configuration.

The source observations were verified by the planning agent, not by Claude,
whose repository grant did not include the other checkout. Runtime defects
identified by Claude remain code-reading observations pending regression
proof during implementation. These changes still only refine draft scope.
