<!-- Raw verbatim review of 2026-06-25-synchronous-review-handoff-design.md by 'codex' (headless), 2026-06-25. Trailing whitespace stripped; content otherwise unmodified. -->

VERDICT: concerns

1. Shared-workspace guard proof is risky: the reviewer must revert/restore in the same worktree, so a failed or overeager reviewer can leave the coder branch dirty or changed.

2. The stdout verdict protocol is too weak: logs, refusals, nonzero exits, or missing `VERDICT:` lines need an explicit fail-closed parser and outcome.

3. Dynamic harness probing needs stricter bounds: specify timeout, non-interactive detection, safe command-token validation, and what happens when smoke tests hang or launch a UI.

4. Durable record semantics are underspecified: recording into the finding doc should preserve reviewer, harness/version, reviewed SHA, guard result, timestamp, and whether that record is committed.

5. Diff/base identity is underdefined: `git diff <main>..<branch>` can drift if main moves; capture and review against an explicit base SHA and branch HEAD.
