Yeah. After reading the repo, the problem is clearer:

> **The review semantics are governed, but model routing is ambient.**

That is the actual defect.

`codereview` explicitly says its tightly framed conformance task is suitable for **weaker reviewer models**, while `openreview` says its unprimed design judgment rewards **stronger reviewers**. But both operators accept only `<agent>`—not a model or capability profile—so whatever expensive model the harness currently defaults to wins. The harness-capability record already warns that unpinned defaults bite.   

That means the playbooks understand the difference, but cannot enforce it.

## The policy I would use

```text
openreview  = frontier model, once
codereview  = standard model by default
reopened    = standard model reviewing the repair delta
contested   = frontier adjudicator
formatting  = deterministic extraction or economy model
```

The most expensive model should appear at **discovery and adjudication**, not every verification round.

### Frontier escalation should be objective

A `codereview` round should automatically move from `standard` to `frontier` only when at least one of these is true:

- Severity is `CRITICAL` or `HIGH`.
- The finding crosses an authentication, authorization, secret, cryptographic, or other security boundary.
- It involves concurrency, persistence, transactions, migrations, destructive operations, or protocol compatibility.
- The guard proof is missing, manual-only, flaky, or cannot distinguish the fixed and reverted states.
- `Known gaps` is nonempty.
- The reviewer has reopened the finding twice.
- The coder disputes the finding or the reviewer rules it invalid.
- The repair materially expands beyond the originally declared files or approach.

Everything else stays on the standard cross-vendor reviewer.

That keeps the decision evidence-based rather than asking the owner or orchestrator to guess whether a change “feels hard.”

## Concrete model routing

For your current mix, I would start here:

| Role | OpenAI reviewer | Claude reviewer |
|---|---|---|
| Transport smoke / schema repair | Luna or no model | cheapest adequate model or deterministic parser |
| Normal `codereview` | Terra at high effort, or GPT-5.3-Codex | Sonnet 5 at high effort |
| `openreview` | Sol at high/xhigh effort | Fable 5 |
| Contested adjudication | Sol at xhigh/max | Fable 5 |

OpenAI positions Sol for complex professional work, Terra for balancing intelligence and cost, and Luna for cost-sensitive high-volume work. Terra’s published credit rates are exactly half Sol’s for input, cached input, and output; Luna’s are one-fifth. 

Anthropic positions Sonnet 5 as a much more agentic standard model whose performance approaches Opus 4.8 on some workloads, while Fable 5 is explicitly intended for the hardest, ambitious, long-running work. Sonnet 5’s API pricing is currently one-fifth Fable 5’s through August 31, 2026, although that ratio should not be assumed to equal the exact Max-plan quota weighting. 

I would **not** initially put Luna on substantive review verdicts. It belongs on transport tests, extraction, and similarly mechanical tasks until you have field evidence that it is reliable enough for the actual gate.

## Preserve model heterogeneity without wasting frontier capacity

A Sonnet 5 review of code authored by GPT-5.6 Sol is still heterogeneous. A Terra review of code authored by Fable 5 is still heterogeneous.

The independence comes primarily from:

- different training and post-training;
- different tool-use behavior;
- different failure tendencies;
- different vendor and model family;
- an independently constructed judgment.

It does **not** require the reviewer to be the most expensive member of that family every time.

For normal findings, the best pairing is probably:

```text
Claude-authored code  → OpenAI standard reviewer
OpenAI-authored code  → Claude standard reviewer
```

For contested findings, prefer a third provider where available. Otherwise upgrade the **reviewer side**, not the author side, so the author does not effectively adjudicate its own work.

## The second expensive mistake: full replay after every reopen

Right now, a reopened finding sends the review loop back through the same playbook over the pinned original base and current head. That encourages another broad read of the entire fix.

A follow-up round should carry three SHAs:

```text
finding_base_sha       original merge-base
previous_reviewed_sha  head that was reopened
reviewed_sha           repaired head
```

The follow-up reviewer should:

1. Start with `previous_reviewed_sha..reviewed_sha`.
2. Check whether the previous comments were actually resolved.
3. Inspect the final surrounding code where necessary.
4. Re-run the finding’s guard proof against the final head.
5. Avoid re-litigating unrelated parts of the branch unless the repair affected them.

That is still a real review. It just stops paying repeatedly for rediscovery of unchanged code.

After two consecutive reopens, escalate to frontier rather than doing unlimited standard retries. That follows the repo’s existing “escalate on stalled progress, not duration” invariant. 

## What I would change in the toolkit

### `templates/playbooks/codereview.md`

Add a short **Model routing** section:

```text
The default substantive reviewer profile is standard, never the harness
default. Pin the concrete model and effort explicitly. Use frontier only
for the escalation conditions below or an explicit owner override.
```

Change the operator to:

```text
codereview <agent> [standard|frontier]
```

`standard` should be implicit, so normal use remains:

```text
codereview codex
```

An override becomes:

```text
codereview codex frontier
```

Also:

- record concrete model ID and effort alongside harness and version;
- use repair-delta review after a reopen;
- escalate after the second reopen;
- state that schema re-emission is not a substantive review and must use deterministic extraction or an economy profile.

### `templates/playbooks/openreview.md`

Change the operator to:

```text
openreview <agent> [frontier|standard]
```

`frontier` is implicit because the whole point of `openreview` is unprimed discovery and design judgment.

Add an explicit rule:

> Findings returned by frontier `openreview` enter standard `codereview`; they do not inherit the frontier tier.

Also make clear that there is no automatic repeated frontier whole-change review after every fix. A second `openreview` happens only because the owner asks for another independent pass or because the fixes materially changed the overall design.

### Reviewer-incantation probe

The current probe discovers transport and JSON flags, but it should also discover and validate:

- model-selection flag;
- reasoning/effort flag, when supported;
- actual resolved model ID;
- harness version.

The cache should be keyed by harness version and profile. A cached invocation should not consume a premium smoke-test call every new session when neither the binary version nor profile changed.

This directly closes the contradiction with the repo’s existing instruction to pin models explicitly. 

### Local profile map

Do not hardcode fast-changing model IDs into the shipped playbooks. Extend the existing machine-local cache concept:

```json
{
  "codex": {
    "standard": {
      "model": "gpt-5.6-terra",
      "effort": "high"
    },
    "frontier": {
      "model": "gpt-5.6-sol",
      "effort": "xhigh"
    }
  },
  "claude": {
    "standard": {
      "model": "claude-sonnet-5",
      "effort": "high"
    },
    "frontier": {
      "model": "claude-fable-5",
      "effort": "high"
    }
  }
}
```

That file should remain advisory, gitignored, version-checked, and self-correcting—exactly like the existing harness-incantation cache. The committed playbook owns the meanings of `standard` and `frontier`; the local file resolves them into today’s model names.

## Expected savings

Suppose 80% of substantive review rounds are ordinary per-finding verification and 20% qualify for frontier escalation.

Using Terra for the 80% and Sol for the 20% gives an approximate OpenAI credit-rate factor of:

\[
0.80(0.50) + 0.20(1.00) = 0.60
\]

So that is roughly a **40% reduction** versus Sol every round, before counting:

- repair-delta reviews;
- avoiding repeated whole-change frontier passes;
- cheaper transport probes;
- deterministic JSON extraction;
- fewer premium calls wasted on low-severity findings.

Using Luna for purely mechanical calls lowers that portion further.

On the Claude side, the potential reduction is probably larger when replacing Fable with Sonnet for tightly framed conformance work, but the exact improvement to your Max allowance cannot be derived from API prices alone.

## One caution from the repo itself

The split landed on July 16, and the toolkit’s own state says the `openreview` dogfood ran, but the per-finding `codereview` redispatch round was **not** run. So the expensive repeated portion is not yet validated in this repo’s dogfood record. 

That makes this the right moment to fix routing. It is new enough that you are not overturning a long-proven workflow.

The clean rule is:

> **Owner chooses the review semantics. The playbook chooses the economical model tier. Frontier is reserved for open discovery, objectively risky findings, and disagreement.**

That preserves the existing owner ruling against automatically choosing between `codereview` and `openreview`; it does not require the owner to micromanage model cost for every round. The ruling is specifically tied to choosing the two playbooks by name. 

No repository changes were made.