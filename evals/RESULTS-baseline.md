# Baseline results — run `base` (2026-06-28)

First real measurement: codex driver, 3 fixtures × 3 governance profiles × 3 runs =
27 agent trials. Raw per-trial JSON in `evals/results/`; regenerate this table with
`python3 evals/aggregate.py`.

| fixture | none | current-template | candidate-loop-first | tamper |
|---|---|---|---|---|
| ts_qbit_confirmdelete_gold (TS/Vitest) | 3/3 | 3/3 | 3/3 | 0 |
| ps_token_killer_commentstrip_gold (PowerShell/Pester) | 3/3 | 3/3 | 3/3 | 0 |
| py_duration_parser (Python/unittest) | 3/3 | 3/3 | 3/3 | 0 |

**Pass-rate delta vs `none`: +0.000 everywhere.**

## Finding

No measurable governance effect — but because of a **ceiling effect, not a real null
result**. codex solves all three fixtures 100% of the time with no governance at all, so
there is no room for `current-template` or `candidate-loop-first` to move the pass rate.
You cannot measure a delta between two arms that both score 100%.

This is consistent with the structural point behind the whole effort: governance prose
narrows attention but does not change the harness's solve loop, so for tasks the model
already aces, more prose changes nothing. It does **not** tell us governance is useless —
it tells us these fixtures are **too easy to discriminate**.

## What the run *did* validate

The apparatus works end-to-end across 27 real agent trials: language-agnostic scoring on
three toolchains, gold-standard oracles, history-isolated workspaces, governance-profile
overlay, tamper detection (0 flags — no agent edited a test), and aggregation. The
measuring instrument is sound; the fixtures are the limiting factor.

Secondary, weak signal: governance may add latency (the Python fixture trended
none 119s → current-template 173s → candidate 179s as the agent reads more guidance), but
this is noisy at n=3 and not robust.

## Next

Build **margin fixtures** — tasks where codex's no-governance pass rate is materially
below 100% (multi-step / subtle / "first-green-but-incomplete"), so a governance effect
has room to show. The plan's Slice 4 multi-step fixture is exactly this. Easy fixtures at
the pass ceiling cannot answer the question; harder ones at the model's margin can.
