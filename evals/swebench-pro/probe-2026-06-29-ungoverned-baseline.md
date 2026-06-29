# SWE-bench Pro — ungoverned baseline probe (2026-06-29)

Durable record of the first sizeable ungoverned probe for the governance-efficacy
eval. This is the headroom measurement that decided whether **Option A** (mine the
existing 731 instances for a hard band) yields a usable agent-failure set. It does.

See `.agents/state.md` (2026-06-29 entries) for the live workstream status and the
experiment sequence this feeds.

## Setup (all proven mechanics; see state.md for provenance)

- **Subject under test:** harness + model = **Claude Code** (host native amd64 ELF
  `claude` v2.1.195) on **subscription auth** (mounted `~/.claude/.credentials.json`).
  No API keys.
- **Where:** netwatch-01 (amd64 Linux, native Docker; SWE-bench Pro checkout at
  `/home/michael/dev/SWE-bench_Pro-os`).
- **Arm:** **ungoverned** (no AGENTS.md, no hooks) — the baseline arm.
- **Per instance:** `docker run` the instance image → create non-root `agent` user →
  copy credential → **anti-leak scrub: `rm -rf .git && git init && git add -A &&
  commit -m base`** (gold fix commit leaves zero trace) → `claude -p "$(task)"
  --permission-mode bypassPermissions` as `agent`, 600 s timeout → capture
  **source-only diff** (`git add -A && git diff --staged` excluding the gold test
  files + test-run artifacts) → score with the third-party `swe_bench_pro_eval.py`
  (`--redo`) in its own fresh image container.
- **Sample:** 20 instances drawn from the 92-instance complex+regression-rich pool
  (gold ≥3 files, PASS_TO_PASS ≥15, FAIL_TO_PASS ≥3), 3 parallel workers.

## Result

**Ungoverned resolved: 10/20 (50%).** Every one of the 20 produced a genuine
non-empty source patch — **0 empty/infra failures**, 0 non-`ok` statuses — so the 10
non-resolves are real agent failures (agent edited source, gold tests still fail),
not measurement noise. This is the headroom the experiment needs: a 50% baseline
leaves room for governance to move the rate in either direction, and gives 10
concrete candidate instances.

| result   | repo            | files | patch chars |
|----------|-----------------|-------|-------------|
| RESOLVED | NodeBB          | 11    | 9147  |
| FAILED   | NodeBB          | 5     | 9910  |
| FAILED   | NodeBB          | 7     | 8765  |
| RESOLVED | qutebrowser     | 3     | 5722  |
| RESOLVED | qutebrowser     | 2     | 1641  |
| FAILED   | qutebrowser     | 3     | 7011  |
| FAILED   | NodeBB          | 2     | 3005  |
| RESOLVED | qutebrowser     | 4     | 3172  |
| FAILED   | element-web     | 8     | 18998 |
| RESOLVED | element-web     | 8     | 13626 |
| RESOLVED | element-web     | 7     | 21438 |
| RESOLVED | element-web     | 6     | 7171  |
| RESOLVED | ansible         | 10    | 6943  |
| RESOLVED | ansible         | 4     | 31945 |
| FAILED   | ansible         | 6     | 13917 |
| FAILED   | openlibrary     | 3     | 8412  |
| FAILED   | ansible         | 1     | 12954 |
| FAILED   | openlibrary     | 4     | 11231 |
| RESOLVED | openlibrary     | 6     | 50008 |
| FAILED   | openlibrary     | 3     | 8467  |

Failures by repo: NodeBB ×3, openlibrary ×3, ansible ×2, qutebrowser ×1, element-web ×1.

## Agent-FAILURE band (governance-experiment candidate set, 10 instances)

These are the instances the ungoverned arm failed — the headroom band for the
governed none/prose/prose-hooks factorial:

```
instance_NodeBB__NodeBB-18c45b44613aecd53e9f60457b9812049ab2998d-v0495b863a912fbff5749c67e860612b91825407c
instance_NodeBB__NodeBB-04998908ba6721d64eba79ae3b65a351dcfbc5b5-vnan
instance_NodeBB__NodeBB-9c576a0758690f45a6ca03b5884c601e473bf2c1-vd59a5728dfc977f44533186ace531248c2917516
instance_qutebrowser__qutebrowser-ff1c025ad3210506fc76e1f604d8c8c27637d88e-v363c8a7e5ccdf6968fc7ab84a2053ac78036691d
instance_element-hq__element-web-aeabf3b18896ac1eb7ae9757e66ce886120f8309-vnan
instance_ansible__ansible-d33bedc48fdd933b5abd65a77c081876298e2f07-v0f01c69f1e2528b935359cfe578530722bca2c59
instance_ansible__ansible-ecea15c508f0e081525be036cf76bbb56dbcdd9d-vba6da65a0f3baefda7a058ebbd0a8dcafb8512f5
instance_internetarchive__openlibrary-7c8dc180281491ccaa1b4b43518506323750d1e4-v298a7a812ceed28c4c18355a091f1b268fe56d86
instance_internetarchive__openlibrary-b112069e31e0553b2d374abb5f9c5e05e8f3dbbe-ve8c8d62a2b60610a3c4631f5f23ed866bada9818
instance_internetarchive__openlibrary-f0341c0ba81c790241b782f5103ce5c9a6edf8e3-ve8fc82d8aae8463b752a211156c5b7b59f349237
```

## Caveats before this becomes the confirmatory sample (per the plan reviews)

- **n=20 is a probe, not the powered sample.** A single ungoverned pass labels an
  instance failed; some are flaky/near-miss. The reviewers' must-fixes still apply
  before the factorial: pre-registered analysis + power/MDE, a length-matched PLACEBO
  prose arm, F2P/P2P reported separately, subset-selection rigor (don't build the
  confirmatory set from a single n=20 pass — re-measure the band with replicates to
  avoid regression-to-the-mean), ONE harness for the confirmatory factorial.
- **Single-shot per instance.** No replicate runs yet, so the 50% is a point estimate.
- The probe driver is scratch (`$SP/probe.py`); formalizing it into `evals/` (with
  `shell=True` hardened to arg-lists) is the deferred engineering step.
