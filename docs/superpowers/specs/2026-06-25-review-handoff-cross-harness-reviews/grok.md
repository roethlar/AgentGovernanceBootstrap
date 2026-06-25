<!-- Raw verbatim review of 2026-06-25-synchronous-review-handoff-design.md by 'grok' (headless), 2026-06-25. Trailing whitespace stripped; content otherwise unmodified. -->

**VERDICT: concerns**

The core diagnosis is correct: the existing reviewloop's async sentinel + persistent watcher does not match how real harnesses (codex/agy/grok/Claude) actually work, and a synchronous per-finding dispatch from the coder into a headless reviewer on the shared FS is a cleaner fit. Durable recording before action and owner-gated merge are respected. However, several execution-model and contract assumptions are under-specified or optimistic.

**Top concerns:**

- Live probing (`command -v`, `--help` drill, `smoke-test "say OK"`) has no defined observable failure contract or recovery path when the trivial test passes but the real review prompt does not. Harness CLIs commonly require specific flags, env, or non-TTY conditions that a canned prompt will not reveal; a bad incantation produces either a hanging process or human-oriented output.

- Classification and action hinge on the foreign reviewer emitting a reliable leading `VERDICT: accepted|reopened|invalid` token on stdout that the caller can parse. Different-harness agents are not bound by the prompt; their output is typically interleaved reasoning + logs + formatting. No parser, tolerance rules, or escalation (re-prompt / ask owner / treat as contested) is specified.

- "Coder reads stdout, records verdict in the repo, then acts" places the primary agent in sole charge of transcribing and committing output from a second, independent harness. This satisfies the "durable truth in repo" rule on paper but creates an unaudited single-agent mapping from noisy foreign text to finding-doc edits + status flips, undermining the two-role separation the playbook exists to enforce.

- The design declares synchronous one-at-a-time the only mode and dissolves the "Faster" (disjoint-scope multi-pending sentinels) WIP option without analysis or owner knob. The current reviewloop.md explicitly documents the disjoint case; removing it changes a shipped contract for a pattern that has value on multi-finding sweeps even when the owner values accuracy.

- Wholesale replacement of `reviewloop.md` (sentinels, results/*.json, `guard_proved` field, explicit schemas) with prose inside the finding doc + contested files loses the previous machine-readable attestation that the reviewer independently re-ran the guard proof. This reduces later auditability/harvest value and is a breaking update to a template artifact.

Additional notes (lower altitude): adding `review <agent>` as an operator surfaces the same `OPERATOR_WORDS` / `playbook <name>` staleness-probe mismatch already tracked as deferred; the shared-workspace assumption (reviewer does its own checkout/diff/guard on the exact branch state) is unexamined for worktree or dirty-index cases; and the canonical reviewer prompt's physical location remains an open question in the spec itself. The intent aligns with repo invariants; the cross-harness subprocess surface does not yet.
