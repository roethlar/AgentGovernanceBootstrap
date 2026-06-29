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

## Batch 2 — 2026-06-29 (other 4 instances, R=1; codex CAPPED mid-batch)

Codex hit its usage cap partway through; the driver self-aborted (8 cells quota-invalid,
0 neterr). **9/16 valid.** Instances: qutebrowser ff1c025, NodeBB 18c45b44,
openlibrary b67138b3, ansible e40889e7.

| arm | resolved (valid) |
|-----|------------------|
| none | 0/3 |
| placebo | 0/2 |
| prose | 1/2 |
| prose+hooks | 0/2 |

Remaining ~7 cells of batch 2 wait for the next codex reset.

## Combined codex so far (batch 1 + batch 2 valid cells) — directional, NO power

| arm | resolved |
|-----|----------|
| prose | 3/6 |
| none | 1/7 |
| prose+hooks | 1/6 |
| placebo | 0/6 |

Two independent batches agree on the **direction**: prose best, placebo worst,
none/hooks low. Suggestive only (n≈6–7/arm). The hook increment is ~null here even
though codex hooks fire — consistent with single-shot giving hooks little to enforce.
Codex is currently capped; resume batches after its reset.

## Batch 2-RETRY — 2026-06-29 (re-ran batch-2 instances after codex reset; capped again)

Codex hit its cap AGAIN mid-batch (6/16 quota-invalid, 10/16 valid). This retry
SUPERSEDES the partial batch 2 above. Batch-2-retry alone: none 1/3, placebo 0/3,
prose 0/2, prose+hooks 1/2.

## REVISED combined (batch 1 + batch-2-retry) — the earlier "prose best" was NOISE

| arm | resolved |
|-----|----------|
| none | 2/7 |
| prose | 2/6 |
| prose+hooks | 2/6 |
| placebo | 0/7 |

With fresh draws the prose advantage **disappeared**: prose ≈ none ≈ hooks (~30%);
only **placebo worst (0/7)** persists. So the batch-1 "prose 2/4 best" was
small-sample luck. **Lesson reinforced:** at n≈6–7/arm the point estimates flicker
batch-to-batch — nothing here is interpretable beyond "placebo tends worst." This also
weakens the earlier cross-model capability hypothesis: codex now looks like Opus
(prose ≈ none), not prose-favoring. Codex capped again; one more owner reset available.
