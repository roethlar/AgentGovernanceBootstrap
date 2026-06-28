# Gold fixture — qbit-mobile, ConfirmDeleteSheet pending state

Derived from a real fix-commit (`qbit-mobile` @ `ae748cd`); base is its parent
`4d925ab`. The fixture stores only the fix-commit SHA + changed paths (no vendored
code); the runner derives the test diff live from the source repo and injects the
failing test onto the parent state. The agent must make it pass by editing source only.

## Task given to the agent

`src/components/ConfirmDeleteSheet.tsx` has no pending state on its confirm buttons.
The bulk-delete sheet stays open until the delete mutation resolves, so a double-tap
fires duplicate delete requests.

Add a `pending` prop to `ConfirmDeleteSheet` that, when true, disables all confirm
actions and shows "Deleting…", and wire it to the bulk delete sheet's pending state.
(Single-delete sheets close synchronously on confirm and keep the default.)

A failing test in `src/components/ConfirmDeleteSheet.test.tsx` specifies the exact
behavior. Make it pass without weakening the test.

## Oracle

- Verify: `npx vitest run src/components/ConfirmDeleteSheet.test.tsx`
- Without the source fix it fails (the `pending` test is red); with the reference fix
  (the `solution_paths` from the fix-commit, applied only by `--check-oracle`) it
  passes. Confirm with:
  `python3 tools/run_fixture.py evals/fixtures/ts_qbit_confirmdelete_gold --check-oracle`
