# Review: bootstrap-plan.v7.md

**Reviewer:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Reviewed at commit:** `be45d33` (working tree)
**Mode:** collaborator, not gatekeeper. You said you're struggling with the tooling choice — this review is mostly about killing that struggle, not cataloguing nits.

## Verdict: The architecture is finished and correct. The tooling "choice" is smaller and more reversible than v7 makes it feel — and v7's own recommendation works against your stated goal.

### What v7 got right

- **`Core System` section** adopts the decoupling cleanly: governance = docs + data; executable helpers are "optional support… not the source of truth." This is the single most important sentence in the whole version history. Once this is true, the language of any helper is a *packaging* decision, not an *architecture* decision.
- **`No Chat-Context Leakage`** is a genuinely good new rule, and notably self-aware — it generalizes the exact failure mode this very planning thread could produce (a font correction becoming `Do not use Font X`). One sharpening: this is a **Layer-2 / judgment** rule. Nothing deterministic can reliably catch "this rule is contextless." Say so, so it isn't mistaken for an enforced check.
- **Generated-artifacts rule** now explicitly forbids imposing the helper language as a target-repo runtime dependency. That closes my v6 HIGH finding at the spec level.

## The core problem: v7 widened the choice instead of narrowing it

You're struggling because v7 presents **five options (A–E)** as if they were five strategic choices. They aren't. They collapse to **three postures**, and two of the five are just source-vs-binary of the same posture:

| v7 options | Real posture | What it costs you |
|---|---|---|
| **A** (markdown only, agent runs `git` by checklist) | **No code.** Agent does the deterministic work. | Contradicts the plan's own foundational thesis (below). |
| **B, C** (`.agents/reposcan.sh` / `.ps1` in the repo) | **Embedded per-repo helper.** | Re-introduces the coupling Decision 2 just removed (below). |
| **D, E** (external CLI: Python source / Go binary) | **One external tool operating *on* repos.** | An install/distribution story. D vs E is *only* "runtime required?" |

So the decision is not 1-of-5. It is: **A vs (B/C) vs (D/E)** — and I think two of those three are eliminable on the plan's own stated values.

### Why Option A is in tension with the whole plan

Every version since v2 has insisted: *"The LLM should not be trusted to remember custody, overwrite, secret-safety, or verification mechanics without deterministic checks."* Option A is precisely trusting the LLM to do that, by checklist. You can choose A — but only by **downgrading that thesis** to "a disciplined agent + a good checklist is good enough for v1." If A is acceptable, much of the deterministic-layer argument was over-built. Decide that consciously; don't let A in through the side door because it has the smallest surface.

### Why v7's recommendation (B/C first) undercuts your goal

v7's Implementation Direction says: *"Start with a repo-local slash-command helper."* But a tracked `.agents/reposcan.ps1` living **inside each target repo** *is* the per-repo language dependency that the Core System and Generated-Artifacts sections forbid two pages earlier. This is an internal contradiction:

- **Generated Artifacts:** "must not impose the helper implementation language as a target-repo runtime dependency."
- **Implementation Direction:** start with `.agents/reposcan.sh`/`.ps1` in the repo.

A `.sh` scanner in a .NET shop, or a `.ps1` scanner on a teammate's Mac, is exactly that imposition — now multiplied by N repos, with N copies to keep from drifting. The slash-command *ergonomics* are nice; the *embedded helper* behind it is the weakest posture on your own values (reduce surface, multi-platform). **The slash command is fine; what it invokes should not be a per-repo script.**

## The reframe that should end the struggle

You are treating the language pick as an **irreversible architectural commitment**. It is neither, for one reason you can verify by looking at the work:

**The deterministic core is tiny.** It is: `git ls-files`, `git status --ignored`, glob-match sensitive paths, detect a handful of marker files, compute a freshness verdict from `git diff --name-only`, emit JSON. That is a few hundred lines with no exotic dependencies. Consequences:

1. **Language barely affects capability.** Python, Go, shell, PowerShell can all do this comfortably. So *stop choosing on capability* — choose only on distribution/coupling.
2. **The choice is cheap to reverse.** A few hundred lines of git-plumbing is a port you can do in an afternoon. Picking Python now does **not** lock out a Go binary later. So this is a *late, cheap bind*, not an early architectural one.
3. **Therefore the only decision you must make now is posture, not language** — and for the very next step (dogfooding) the posture is forced, see below.

## My recommendation (with a clear trigger, so you can stop deciding)

1. **Lock Decision 2 as done.** Docs/data core; helpers operate *on* repos and write *preview output outside* the repo (the plan already allows this). Nothing lands in a target repo until `apply`, and even then only docs + data + an optional repo-native wrapper.

2. **For the next two weeks, build posture D in its cheapest form: a Python script you run from your own machine against one pilot repo, writing preview output to an external folder.** Rationale:
   - Preview-external means **zero coupling** to the pilot repo — sidesteps the B/C contradiction entirely.
   - Python because *you already have it here and it iterates fastest*; capability is irrelevant at this size.
   - You learn the only thing that matters right now: **is the manifest actually useful to a fresh agent?** No language choice answers that; only a dogfood run does.

3. **Defer Go entirely behind one trigger:** *the first time someone other than you, on a machine you don't provision, needs to run this.* At that moment, port the (small, proven) logic to a Go static binary. Until that trigger fires, Go is solving a distribution problem you don't have yet.

4. **Resolve the embedded-helper question in the spec** before it confuses the build: decide that `reposcan`/discovery is **governance-tool-local, not a tracked target-repo artifact.** The slash command is harness config that *invokes* the external tool; it is not a per-repo script. Fix the Implementation Direction wording to match the Core System rule.

## Smaller spec nits (note as directives, don't spawn a v8 for them)

- **`repo-map.md` OR `repo-map.json`** — allowing both invites drift, and the freshness calc reads "`.agents/repo-map.md` or `.agents/repo-map.json`." Pick **one canonical machine-readable form** (JSON) for anything the deterministic layer parses; keep markdown for the human narrative if you want both, but only one is authoritative.
- **Config moved YAML → JSON** (`bootstrap.config.json`). JSON has no comments. For a human-edited file (harness list, budgets, thresholds), losing inline explanation is a real ergonomic downgrade. Consider JSONC, TOML, or keeping YAML for *human-edited* config while using JSON for *machine-emitted* manifests.
- **Coverage block is still single/global** (carried from v6). Make it per-project when boundaries are detected, or a monorepo's truncation hides which package was cut.

## Meta (fourth review in a row, said plainly)

v7 changed **no design** — it adopted Decision 2, added one good rule, and turned one decision into a five-item menu. That menu is why you're stuck. The architecture has been done since v5. The remaining question is not answerable by a v8; it is answerable by **running a 300-line Python script against one real repo this week.** The next file in this folder should be `discover.py` and a manifest from a pilot run — not `bootstrap-plan.v8.md`.
