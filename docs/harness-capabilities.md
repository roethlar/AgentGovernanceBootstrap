# Harness capabilities

Use these dated observations only for the mechanisms they establish. Reuse
known capabilities; recheck an affected claim when version/profile changes
or contrary evidence makes it uncertain. Presence on PATH does not prove
authentication, headless tools or review quality. Full probes and historical
limitations: [evidence ledger](history/2026-09-08-harness-capabilities.md).
Reviewer dispatch and response handling live in the codereview playbook.

| Harness | Recorded support and limits |
| --- | --- |
| Claude Code | `CLAUDE.md` imports AGENTS; the shim is required (2026-06-29). Compaction hook fires (2026-06-21). Repo PreToolUse blocks through the shipped JSON deny (2026-08-01). |
| Codex | Native AGENTS loading; `@` imports are literal, so guidance explicitly directs reading repo guidance (2026-07-08). Repo skills verified on 0.143.0. Repo hooks and JSON deny verified on 0.146.0 (2026-08-01); exit 2 alone did not block. |
| Grok | AGENTS/CLAUDE loading and repo skills verified (2026-06-29/07-08). Global hooks were observed; repo hook support remains unverified. |
| agy | AGENTS/GEMINI loading observed with `--new-project` in headless mode (2026-06-29). Repo skills and SessionStart verified on 1.1.0 with workspace trust (2026-07-08). Compaction immunity is an assumption; no re-ground hook ships. |
| Kimi / Gemini CLI | No live adapter-mechanism proof recorded. Existing generic launch support is not such proof. |

For Codex 0.146.0, the verified repo-hook chain requires hooks enabled,
project trust and per-handler trust. Trust must not be widened automatically.
The app-server can pin the current handler hash and verify it via
hooks/list; refresh offers that only after relevant hook changes and owner
confirmation. A changed handler invalidates its prior trust pin.

The shared guard emits JSON deny with exit 0. On Windows, Codex requires
plain `commandWindows` plus `command`; its hook process uses the payload's
cwd. POSIX Codex command support remains assumed in the recorded probe.
Claude's interpreter chain tries working Python 3.10+ interpreters and
fails open if none runs; prose authority and refresh reconciliation remain
the other protections.

Codex headless prompts use stdin; argv prompts have hung. For agy, recorded
headless authentication/write-permission failures need their actual cause
resolved, not retries or privilege escalation. Default model IDs and old
CLI quirks stay in the ledger, not current dispatch defaults.

Owner priority (2026-08-01): Claude Code and Codex, then Kimi, Grok and agy.
Preserve every shipped adapter; add or change a mechanism from evidence.
No new live capability claims are made by this documentation cleanup.
