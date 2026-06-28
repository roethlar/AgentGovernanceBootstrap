# Eval harness

Measures whether a **governance profile** helps an agent produce working, secure code,
so loop-first governance changes are adopted on evidence rather than plausibility. See
the plan: `docs/superpowers/plans/2026-06-28-loop-first-harness-gap.md`.

## Concept

A **fixture** is a knowable-answer task with a mechanical oracle. It declares its own
setup + verify commands, so the runner is **language-agnostic** — it scores on the
verify command's exit status, whatever the language or framework.

- `kind: "smoke"` — runs a real repo's existing suite at a pinned commit to prove the
  harness spans toolchains. Not an agent task.
- (later) `kind: "gold"` — a real fix-commit's parent state as the start, the
  fix-commit's own test as the oracle (the SWE-bench pattern).
- `source: null` — synthetic fixture; inline code under `files/`.

## fixture.json

```json
{
  "id": "ts_qbit_formatters_smoke",
  "language": "typescript",
  "kind": "smoke",
  "source": {"repo_path": "/abs/path/to/repo", "base_commit": "<sha>"},
  "env": {"KEY": "VALUE"},
  "setup": ["npm ci --no-audit --no-fund"],
  "verify": "npx vitest run src/utils/formatters.test.ts",
  "task": "TASK.md"
}
```

## Run

```bash
python3 tools/run_fixture.py evals/fixtures/<id> [--profile none] [--record]
```

The runner scaffolds a throwaway clone (real source) or temp dir (synthetic), strips
git remotes so nothing can push back, overlays the chosen governance profile, runs
`setup` then `verify`, and prints a trial result. `--record` writes it under
`evals/results/`. Exit code is 0 iff `functional_pass`.

## Safety

- Never vendor a source repo's code into this repo. Fixtures reference it by path +
  pinned commit; the runner clones into a temp workspace.
- Use only offline-deterministic tests (no Playwright browser e2e, no live Graph/AD/
  Exchange calls).
- `evals/results/` holds scores + commit SHAs, never repo contents or transcripts.

## Substrate (owned repos, by language)

| Language | Repo | Runner |
|---|---|---|
| TypeScript | `qbit-mobile`, `roon-controller` | Vitest / Jest |
| PowerShell | `PowerShell-Token-Killer` | Pester |
| Python | (synthetic) | unittest/pytest |
| Rust | `blit_v2` | `cargo test` |
| C# | `ExchangeAdminWeb` | `dotnet test` (needs dotnet SDK) |
