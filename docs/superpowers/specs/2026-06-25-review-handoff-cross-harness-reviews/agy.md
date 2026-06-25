<!-- Raw verbatim review of 2026-06-25-synchronous-review-handoff-design.md by 'agy' (headless), 2026-06-25. Trailing whitespace stripped; content otherwise unmodified. -->

VERDICT: concerns

1. **Stdout parsing is brittle:** CLI LLM tools frequently emit ANSI color codes, conversational preamble, or markdown wrappers, making reliable extraction of a `VERDICT: ...` line from stdout highly fragile compared to a file-based structured drop.
2. **Live CLI probing is unreliable and risky:** Deriving headless commands by guessing subcommands from `--help` text and running smoke tests is prone to hallucination, failure, and risks unintended side-effects (e.g., executing the wrong mode).
3. **Guard proof side-effects in a shared workspace:** Having the reviewer independently modify the shared git tree (revert → test → restore) risks leaving the workspace dirty, broken, or in a detached state if the reviewer process crashes or fails mid-proof.
4. **Context window bloat from stdout:** Forcing the coding agent to ingest the reviewer's entire unfiltered stdout stream—which may include large diffs or verbose logs—risks exhausting the coder's token limits on long reviews.
5. **Configuration over heuristics:** The optional `.agents/review/harnesses.local.json` should be the primary, human-provided configuration mechanism rather than just a cache, which would completely avoid the brittle command-guessing logic.
