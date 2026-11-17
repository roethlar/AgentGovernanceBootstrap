# Incident: a settled exclusion was treated as a platform gap

Status: Evidence recorded 2026-11-17; toolkit changes remain proposals.

## Source and limits

The owner supplied a transcript from the Vela playback project. Its agent
reported listing X11 as a lack, accepting a stop-check's repetition of that
list as confirmation, and amending an approved plan without an owner
ruling. It also reported that it had not checked the existing exclusions.
Those admissions are transcript evidence, not an independently verified
trace of which files the process read. No inference about deliberate
intent is warranted.

The local source repository was subsequently inspected read-only. Commit
`07fc2ed79521522d7d4d5659e1797e3f3b03efbd` is the parent of amendment
`d1f24da9d6f8521cc8a1dc73a3b318c8edfb1730`. These pinned snapshots,
rather than today's edited documents, establish the pre-incident layout.
No source-project file was changed. The later inspected head
`d7b86420c2a516935147680ee124da589fa55a0c` matched its origin main when
queried on 2026-11-17.

## Independently observed facts

| At parent `07fc2ed` | Observation |
|---|---|
| `.agents/repo-guidance.md`, 199 lines | Around line 18, mandatory startup guidance said “Linux on Wayland first” and pointed to the embedded-player plan. It did not state the precise X11 exclusion inline. |
| `.agents/state.md`, 551 lines | Around line 12, a prominent platform-parity entry described Linux/macOS/Windows parity and directed the reader to the last decision. |
| `.agents/plans/embedded-player.md`, 2,711 lines | Non-goals began at line 773. Line 776 explicitly excluded X11 embedding. |
| Same plan, around lines 483–487 | The NVIDIA exclusion was explicitly marked ASSUMED and conditional on testing. |
| Same plan, line 854 | Historical expected behavior described an X11 external-player fallback. This is evidence of what the document then said, not a current product policy. |
| `.agents/decisions.md`, 2,567 lines | Around line 1972, the embedded-player decision described HDR on Wayland as the project's reason for existing. |
| Amendment `d1f24da` | Added 53 lines starting at plan line 2713, under a heading presenting remaining platform gaps as an owner ruling. The source change is visible with `git show d1f24da -- .agents/plans/embedded-player.md`. |

The later head `d7b8642` places an explicit owner clarification in
repo guidance around lines 24–31: X11 is not a fallback and is unsupported.
It must not be weakened by treating the older fallback text as current
authority. Later hardware/test-venue decisions are outside this toolkit
investigation.

Reproduction of the document observations: use `git show
07fc2ed:<repo-relative-path>` for each pre-incident file above, and
`git show d7b8642:.agents/repo-guidance.md` for the later clarification.
Line counts and locations are pinned to those commits, not live facts.

## Assessment

Verified: the exact settled exclusion was separated from the mandatory
startup summary by a reference to a long, repeatedly amended plan; the
nearby platform summary was less precise. Existing explicit-go and scope
rules already prohibited unilateral expansion.

Plausible mitigation: put consequential operative boundaries, including
their exceptions, in text already read at startup, and keep an active
plan's current contract above its history. This addresses an observed
discovery cost. It does not establish historical volume as the sole cause
or guarantee that an agent will obey guidance it has read.

No raw session logs, credentials, machine configuration or private network
coordinates are copied into this record. Proposed work is in
[the current-boundaries plan](../../../docs/superpowers/plans/2026-11-17-current-boundaries.md).
