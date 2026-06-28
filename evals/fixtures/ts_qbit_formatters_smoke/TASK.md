# Smoke fixture — TypeScript / Vitest

A **harness smoke fixture**, not yet a gold-standard task. It proves the runner can
scaffold a real TypeScript repo, install deps, run its native test command (Vitest),
and read pass/fail — a different toolchain than the Pester fixture, on the same scorer.

- Source: `qbit-mobile` @ `283556d`, scaffolded into a throwaway clone (remotes stripped).
- Setup: `npm ci` in the clone (Playwright browser download skipped via env; we score
  only deterministic Vitest unit tests, never the browser/Playwright e2e tests).
- Verify: `npx vitest run src/utils/formatters.test.ts`. Green at the pinned commit, so a
  correctly-wired harness scores `functional_pass: true`.

Gold-standard upgrade (later slice): pick a real fix-commit, set `base_commit` to its
parent, and let that commit's added/changed test be the oracle.
