# Opus 4.8 sizing-pilot results — SWE-bench Pro 4-arm factorial

> **⚠️ INVALID — wrong prose arm. Do not cite the `prose` / `prose+hooks` columns.**
> This pilot injected the toolkit's **full `current-template` AGENTS.md** as the prose
> arm, not the `task-prose` completion-steering profile the plan specifies
> (`docs/superpowers/plans/2026-06-29-swebench-pro-governance-integration.md`, Addendum b:
> the full product governance is *deliberately not* a prose arm — it is human-interaction
> guidance, irrelevant to an autonomous bug fix). The `prose`/`prose+hooks` numbers below
> therefore measure irrelevant-prose ≈ placebo, not governance; the "prose ≤ none"
> direction is a wrong-arm artifact, **not a finding**. The hooks tested were also the
> wrong ones (re-ground/tripwire, not `hook-gate`/`hook-guard`). The `none` and `placebo`
> columns are unaffected, as is the band-selection lesson (floor/ceiling instances give no
> discordance). Re-run with the corrected arms before any prose/hooks claim. The arm
> definition that caused this is fixed in `PRE-REGISTRATION.md` §3. — flagged 2026-06-30

Confirmatory subject (Claude Code + Opus 4.8), 8 instances × 4 arms × R=3.
Capture-vs-base + invalid-accounting; headroom-routed. 2026-06-29.

## Per-arm (valid cells only; 91/96 scored, 5 rate-limit-invalid)

| arm | resolved | rate |
|-----|----------|------|
| none | 12/24 | **50%** |
| placebo | 10/24 | 42% |
| prose | 8/22 | 36% |
| prose+hooks | 9/21 | 43% |

Direction: **none ≥ hooks ≈ placebo ≥ prose.** Governance prose did NOT help; the
point estimate is slightly **negative** (none 50% vs prose 36%). This is the OPPOSITE
of codex's directional hint (where prose led). **No power** — n≈22–24/arm.

## Per-instance (resolved/scored: none / placebo / prose / hooks)

| instance | none | placebo | prose | hooks | note |
|----------|------|---------|-------|-------|------|
| NodeBB-18c45b44 | 0/3 | 0/3 | 0/3 | 1/3 | ~floor |
| ansible-d33bedc | 0/3 | 0/3 | 0/3 | 0/3 | **floor** |
| ansible-e40889e7 | 3/3 | 1/3 | 2/3 | 1/3 | none best |
| element-web-71fe08 | 3/3 | 3/3 | 3/3 | 3/3 | **ceiling** |
| openlibrary-b67138 | 3/3 | 2/3 | 0/1 | 0/0 | none best; prose/hooks data LOST to rate-limit |
| openlibrary-f0341c | 0/3 | 1/3 | 0/3 | 1/3 | mixed, low |
| qutebrowser-f77535 | 3/3 | 3/3 | 3/3 | 3/3 | **ceiling** |
| qutebrowser-ff1c02 | 0/3 | 0/3 | 0/3 | 0/3 | **floor** |

## Reads (tentative)

1. **Half the band is floor/ceiling-locked** (ansible-d33bedc + qutebrowser-ff1c02 =
   floor; element-web + qutebrowser-f77535 = ceiling) → those 4 instances give ZERO
   discordance, contributing nothing to detecting a governance effect. **Band
   selection must tighten** (pre-reg §7: select on replicated mid-range ungoverned
   rate, ~0.2–0.7). The current band came from one n=20 one-shot probe — this confirms
   the regression-to-mean risk.
2. **Discordance is low**, concentrated in ~3 instances (ansible-e40889, both
   openlibraries, NodeBB), and those lean toward **none** or are noisy.
3. **Confound caveat — prose/hooks are under-measured:** the 5 invalid cells are
   prose/hooks cells on openlibrary-b67138 (a RESOLVABLE instance: none 3/3). If those
   lost cells would have resolved like none did, prose/hooks rates rise — so the
   prose<none gap is partly a data-loss artifact and is NOT robust. **Re-run the
   openlibrary cells on Opus** (deferred; Opus paused) before trusting the gap.
4. **Cross-model (very tentative):** codex (weaker) prose>none directionally; Opus
   (stronger) prose≤none. Consistent with "governance helps where the model lacks
   headroom, not a saturating one" — but both signals are underpowered.

## Implications for the confirmatory design

- Re-pick the instance band on replicated ungoverned rate (drop floor/ceiling).
- Need more instances in the informative mid-band to get usable discordance/power.
- Re-run the rate-limit-invalidated openlibrary/Opus cells before any contrast claim.
- The headline so far: **no evidence governance helps Opus on this band; a hint it
  helps weaker codex.** Far from conclusive; sizing/selection must improve first.
