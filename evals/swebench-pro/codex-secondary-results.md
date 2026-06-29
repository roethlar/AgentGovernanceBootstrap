# Codex (gpt-5.5) secondary-harness results — SWE-bench Pro 4-arm

Codex is the **secondary/exploratory** harness (Claude is the confirmatory subject; see
`PRE-REGISTRATION.md`). Codex has ~¼ of Claude's usage budget, so codex runs are
**throttled into small batches spread over days**; the driver self-aborts on codex's
usage-limit signature and flags quota/neterr-empty cells as invalid (not failures).
This file accumulates batches. Arms: none / placebo / prose / prose+hooks.
Subject: codex gpt-5.5 @ xhigh via headroom, subscription auth, in-container.

## Batch 1 — 2026-06-29 (4 instances, R=1, valid; 0 quota/neterr)

| arm | resolved |
|-----|----------|
| none | 1/4 |
| placebo | 0/4 |
| prose | 2/4 |
| prose+hooks | 1/4 |

Per-instance (✓=resolved):
- qutebrowser: none ✓, placebo ✗, prose ✓, prose+hooks ✓
- ansible: none ✗, placebo ✗, prose ✓, prose+hooks ✗
- element-web: all ✗
- openlibrary: all ✗

Notes:
- **Directional only — n=4 per arm, no power.** Reads as prose (2) ≥ none (1) ≈
  prose+hooks (1) > placebo (0); placebo worst. Do NOT conclude anything yet; this is
  one small batch feeding the accumulating codex study.
- **Codex hooks DO fire** under single-shot: the PreToolUse tripwire ran 13–15× per
  prose+hooks cell (codex makes many `apply_patch`/Edit calls). Contrast with the
  earlier worry that hooks are inert — on codex they execute, though they still only
  *warn* on AGENTS.md edits, which don't occur. Re-ground (compaction) still never fires.
- The earlier 96-cell codex run (2026-06-29) was invalidated by codex quota exhaustion
  mid-run; this batch was sized to fit the window with margin and completed clean.
