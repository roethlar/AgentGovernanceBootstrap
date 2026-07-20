# Model-Map Reviewer Dispatch: Fleet-Global Nickname Map, Loud-Stop Resolution

Status: OPEN

Draft 2026-07-19. Codex review round 1 (2026-07-19) returned REJECT — 10
findings, all admitted; ledger below. Rework round same day on owner
directive ("go"): folds F1–F10, sharpens F6 with the retired-set collision
found in the owner's adversarial pass, trims the F1/F8 remedies to the
owner's engineering appetite, withdraws the advisory-trigger proposal (F3),
and adds owner-pass finding F11. Round 2 (codex diff-validation, one
round per owner cap) returned REJECT: five findings closed, four
admitted gaps folded post-round, and F1/F8 re-litigation of owner-sized
remedies contested to the owner — ledger below. Implementation blocked
until the owner gates the reworked plan.

## Problem

Reviewer dispatch names models three different ways today: concrete slugs
pinned per machine in `.agents/review/harnesses.local.json`, ad-hoc inline
ids in operator phrases, and prose in `docs/harness-capabilities.md`. The
fleet drifts: two machines resolve the same owner phrase to different
models, and a stale pin silently downgrades a review. The owner ruled for
one fleet-global nickname map, published in this repo and fetched over the
public raw link, with loud-stop semantics — a dispatch that cannot resolve
its model stops and says so; it never silently substitutes.

## Ruled invariants (owner, 2026-07-19)

- `agents/model-map.json` is the single committed home for concrete model
  slugs, fetched unauthenticated from the public raw link on `master`
  (reachability re-verified 200 during drafting).
- Map unavailable or invalid ⇒ **loud stop**. No cached fallback, no
  last-known-good, no default model. The stop message names the failed
  constraint; it never echoes fetched content.
- Inline slug override is **session-only** — never written back; the
  dispatch record carries `(inline, session-only)` provenance so no
  artifact can launder an override into a pin (F9).
- `/harness-update` is the **sole write path** to the map (normal commit
  flow in this repo; no dispatch-time writes).
- Dispatch grammar: `/codereview <harness> <nickname> <effort>`, with
  `/review` as a pure alias of `/codereview`. Codex is the only MCP
  review harness in scope for this plan.

## Map schema and fetch contract (F1, F9)

Schema, strict:

```json
{
  "version": 1,
  "nicknames": {
    "sol":   { "codex": "<slug>", "claude": "<slug>" },
    "luna":  { "codex": "<slug>", "claude": "<slug>" },
    "terra": { "codex": "<slug>" }
  }
}
```

Validation happens **before any fetched byte reaches model-visible
context** (F1). The dispatching agent fetches with
`curl -fsS --max-time 10` into a scratch file, then applies, in order:

1. **Size cap**: reject files over 16 KiB.
2. **Strict parse**: `json.loads` with an `object_pairs_hook` that rejects
   duplicate keys anywhere in the document (F9).
3. **Shape**: top level is an object; `"version"` equals `1`; `"nicknames"`
   is an object of objects.
4. **Charset**: every nickname, harness key, and slug matches
   `^[a-z0-9][a-z0-9._-]{0,63}$`. Exact lowercase only — no case folding
   (F9).
5. **Closed harness set**: harness keys outside the known set
   (`codex`, `claude`, `gemini`) are a hard failure, not ignored —
   strictness serves the loud-stop philosophy (F9).

Any step failing ⇒ loud stop quoting the constraint name only. On success,
exactly one validated slug enters context; the raw document does not.

Remedy sizing (owner adjudication of F1, 2026-07-19): the contract above
is enforced as playbook text plus the executable checks in Verification —
the Slice 1 hostile fixtures exercise the validator in
`tests/test_model_map.py` against committed content. What the owner
declined is a standalone runtime resolver program sitting between fetch
and dispatch. The owner sizes any escalation beyond that.

## Pinned MCP call contract (F2)

A codex review dispatch is exactly one `mcp__codex__codex` call:

- `model`: the validated slug (or session-only inline override)
- `sandbox`: `read-only`
- `approval-policy`: `never`
- `cwd`: the disposable review worktree
- `config`: `{ "model_reasoning_effort": "<effort>" }` where `<effort>` is
  the effort named in the dispatch phrase
- `prompt`: the review prime exactly as `templates/playbooks/codereview.md`
  specifies for a dispatch — scope line, `base..head`, finding-record
  format; nothing else is model-visible (F2)
- Result: the playbook's verdict envelope, recorded verbatim in the
  dispatch record (F2)

Follow-ups ride `mcp__codex__codex-reply` on the returned conversation id;
a tier or effort change never rides an existing thread (fresh-session rule
in `templates/playbooks/codereview.md` unchanged). Self-permissioning per
the 2026-07-18 decision is untouched: the launch-scoped grant travels in
the harness cache entry's `flags`; the map supplies the model id and
nothing else.

## Escalation and openreview interplay (F3, F4)

- **F3 — withdrawn.** The round-1 draft proposed advisory (warn-don't-stop)
  handling for escalation triggers. Codex correctly objected that T3 is a
  pre-dispatch blocker (owner adjudication of OR4, 2026-07-18) and T4 a
  contested-halt — integrity and scope stops, not routing preferences. The
  proposal is removed from this plan entirely; if advisory routing for
  T1/T2 is ever wanted, it is its own plan with its own owner gate.
- **F4.** The map supplies slugs; it never confers eligibility. An
  openreview dispatch still requires the owner-confirmed frontier entry
  with `openreview_confirmed` set (amendment of 2026-07-18); a nickname
  resolving to some frontier slug does not qualify a pair the owner has
  not confirmed. `/review` aliases `codereview`, never `openreview`.

## Supersession matrix (F5)

Recorded here and, at implementation, as dated amendment entries in
`agents/decisions.md`:

| Prior ruling | Effect of this plan |
| --- | --- |
| 2026-07-17 D1/D2: concrete pins live in machine-local, gitignored `.agents/review/harnesses.local.json` | **Superseded for model slugs** — slugs move to fleet-global `agents/model-map.json`. Harness flags, transports, and capability grades remain machine-local, unchanged. |
| 2026-07-17 D1: default reviewer tiers and trigger-driven escalation | **Untouched** — `<effort>` selects effort within whatever tier the trigger machinery dispatches; nicknames never select tier (F5). |
| 2026-07-17: committed text is model-free (curated-denylist lint) | **Amended** — model-freedom governs templates; `agents/model-map.json` is the single sanctioned committed home for slugs. Lint boundary made explicit (F11). |
| 2026-07-16: `review` operator split; `.claude/commands/review.md` retired | <!-- plan-lint: allow --> **Amended** — the path returns as a pure alias command (F6 surgery below). |
| 2026-07-18: reviewer dispatch is self-permissioning | **Untouched** — grants still launch-scoped; the map feeds only the model id. |

## Shipped-set and lint surgery (F6, F11)

The owner's adversarial pass sharpened F6: `.claude/commands/review.md` <!-- plan-lint: allow -->
sits in the `retired` list of `tools/shipped-set.json`, so shipping the
`/review` alias without surgery would have `tools/refresh.py` machine-delete
the alias on the next converge. Required, in one commit:

- Move `.claude/commands/review.md` out of `retired` into the shipped set, <!-- plan-lint: allow -->
  sourced from new `templates/commands/claude/review.md` (a one-line alias <!-- plan-lint: allow -->
  delegating to `codereview`), honoring the shipped-set MAINTENANCE RULE
  (outgoing normalized hashes appended to `formerly[]` in the same commit).
- Add shipped entries and mirrors for the new surfaces, exact paths (F6):
  `templates/commands/claude/harness-update.md` →
  `.claude/commands/harness-update.md`, skill mirror
  `templates/skills/shared/harness-update/SKILL.md` →
  `.agents/skills/harness-update/SKILL.md`; the alias returns with its
  mirrored skill `templates/skills/shared/review/SKILL.md` → <!-- plan-lint: allow -->
  `.agents/skills/review/SKILL.md`, un-retired under the same <!-- plan-lint: allow -->
  `formerly[]` rule, so
  `test_wrapper_set_covers_operators_and_update_governance`,
  `test_shared_skill_set_mirrors_the_wrapper_set`, and the marker test
  stay green.
- `test_codereview_carries_tier_semantics` hard-asserts
  `harnesses.local.json` in the playbook body; the reference survives
  (flags stay machine-local) and the assertion is extended in the same
  slice to also require the model-map contract section.
- **F11** (owner pass): the model-denylist lint scans only
  `templates/playbooks/*.md`. Extend its scope to all shipped template
  text (`templates/commands/**`, `templates/skills/**`, shims), with
  `agents/model-map.json` recorded in the test docstring as the sole
  deliberate exemption.

## Slices (F7 — reordered so nothing references a file a later slice creates)

1. **Map + map lint.** Create `agents/model-map.json` (seeded from the
   owner-confirmed slugs in the local cache) and `tests/test_model_map.py`
   enforcing every rule in the fetch contract against the committed file,
   with hostile fixtures for each rejection rule (oversize, duplicate key,
   bad charset, unknown harness, non-object).
2. **Playbook text.** `templates/playbooks/codereview.md`: routing section
   gains the fetch contract, loud stop, grammar, and session-only override;
   `templates/playbooks/openreview.md`: one pointer, `openreview_confirmed`
   untouched. Same commit: extended tier-semantics assertion and the F11
   lint-scope extension in `tests/test_templates.py`.
3. **Command surfaces + shipped-set surgery.** New
   `templates/commands/claude/review.md` and <!-- plan-lint: allow -->
   `templates/commands/claude/harness-update.md`, updated
   `templates/commands/claude/codereview.md`, new
   `templates/playbooks/harness-update.md`; `tools/shipped-set.json`
   un-retire + mirror entries + `formerly[]` maintenance, with the mirror
   lints green in the same commit.
4. **Records.** `agents/decisions.md` supersession amendments (matrix
   above), `docs/harness-capabilities.md` updated to point at the map,
   `agents/state.md` handoff.
5. **Converge proof.** `tools/refresh.py` run against a scratch clone of a
   governed repo; the alias must install, not vanish — this is the direct
   regression proof for the F6 collision.

Suite green under python3.14 before every slice commit.

## Verification (F8)

Executable:

- Full suite: `python3.14 -m unittest discover -s tests -p 'test_*.py'`
  green at every slice (125 tests pre-plan; grows with slices 1–3).
- `tests/test_model_map.py` hostile fixtures prove each rejection rule of
  the fetch contract bites.
- Mirror, marker, retired-operator, and extended denylist lints green
  after slice 3.
- Slice 5 converge run shows `.claude/commands/review.md` installed by <!-- plan-lint: allow -->
  `tools/refresh.py`, not deleted.

Recorded evidence (runtime promises a repo test cannot reach — F8 remedy
at owner sizing, marked owner-accepted):

- Raw-link reachability: HTTP 200 from the public raw URL, captured at
  implementation time.
- One live `/codereview codex <nickname> <effort>` dispatch transcript.
- One deliberate map-corruption demo showing the loud stop firing and
  naming the failed constraint without echoing content.

## Plan review

Round 1 — codex (MCP, read-only, unpinned default model — the disease this
plan cures; noted both rounds), 2026-07-19: **REJECT**, 10 findings, all
admitted.

| # | Finding | Resolution in this rework |
| --- | --- | --- |
| F1 | Fetched bytes reach the model before validation; JSON strictness underspecified | Fetch contract §above; remedy trimmed to owner sizing |
| F2 | MCP call contract promised, never pinned | Pinned §above |
| F3 | Advisory triggers over-reach T3/T4 hard stops | Proposal withdrawn |
| F4 | Slug feed could bypass `openreview_confirmed` | Eligibility rule §above |
| F5 | Supersession of 07-17 D1/D2 unmarked | Matrix §above |
| F6 | Wrapper/skill mirror lint and retired-set work missed | Surgery §above; sharpened by owner pass — retired entry would machine-delete the alias |
| F7 | Slice 4 referenced a file slice 5 creates | Slices reordered |
| F8 | Verification could not prove runtime promises | Executable + recorded-evidence split at owner sizing |
| F9 | Duplicate keys / unknown harness / case folding unspecified | Fetch contract steps 2, 4, 5 |
| F10 | Internal cross-reference inconsistency | Fixed during round 1 |

Owner adversarial pass (2026-07-19): confirmed F3/F4/F2 against source
text; sharpened F6; trimmed F1/F8 remedies; added F11 (denylist lint
scope); withdrew the suspected pre-existing suite failure (interpreter
age — suite is 125-green under python3.14).

Round 2 — codex diff-validation over the rework diff (fresh conversation,
read-only, low effort, still the unpinned default model), 2026-07-19:
**REJECT**. Verbatim result: F3, F4, F7, F10, F11 RESOLVED; F1, F2, F5,
F6, F8, F9 NOT-RESOLVED; one new finding (remedy-sizing prose
contradicted the Slice 1 hostile fixtures). Adjudication:

- Admitted, folded post-round (codex has not seen these folds; the owner
  gate covers them): F2 — prompt/result envelope pinned; F5 — D1
  tier-default row added to the matrix; F6 — exact mirror paths and the
  skill un-retire specified; F9 (rescoped by the reviewer from round 1's
  dup-key/case semantics, which stand resolved, to override provenance)
  — provenance rule added; new finding — remedy prose rewritten.
- Contested to the owner: F1 and F8 re-litigate remedy sizing the owner
  adjudicated on 2026-07-19. Per the contested-record rule the round does
  not loop; the owner either stands on the sizing (recorded here) or
  grants the larger remedy. No round 3 dispatched — the owner capped
  this pass at one validation round.
- Owner ruling (2026-07-19): **stand**. The adjudicated sizing holds; the
  larger remedy is declined with rationale — the standalone resolver has
  no independent source of truth (codex cannot enumerate models; names
  come only from the pinned map), and the live acceptance harness buys
  earlier notice of a retired slug for a failure mode codex already
  reports loudly at first dispatch. F1/F8 are closed at owner sizing.
  Plan is final as of this ruling; next gate is owner go-ahead to
  implement.
