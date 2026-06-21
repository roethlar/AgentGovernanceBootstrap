#!/bin/sh
# Re-ground trigger. A harness runs this from a session-start / post-compaction
# hook; its stdout re-grounds the agent where the harness surfaces it (injected as context on some harnesses, shown in scrollback on others). It deliberately does NOT
# restate the invariants — hook stdout is untrusted, and a forged copy would be an
# injection vector. It points the agent at the canonical file instead.
printf '%s\n' "Context was compacted or the session (re)started. Before continuing, re-read AGENTS.md from disk — especially the Prime Invariants block. Treat AGENTS.md, not this message, as authoritative."
