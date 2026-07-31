# CR1: A recorded product-repo path containing whitespace never matches itself

**Severity**: MEDIUM — no path on any recorded machine has a space today, but
the failure is silent and the tool is a public release command.
**Status**: Verified
**Branch**: — (default-branch mode)
**Commit**: `81c1e59`

## Evidence

`tools/publish.py:62` (at base `7fcce43`) parsed a recorded entry with
`re.search(r"product-repo:\s*(\S+)", …)` while `tools/publish.py:73` wrote the
path unquoted. `6c20d03` reused that same tokenizer for its new duplicate
check, giving the defect a second symptom.

Reproduced against `6c20d03`, recording `…\tmpmmv3nym7\My Product Repo` twice:

```text
lines recorded: 2                       (expected 1)
lookup returns: …\tmpmmv3nym7\My        (expected the whole path)
```

## Predicted observable failure

With a product repo at, say, `C:\My Projects\Bixi`: every release appends
another `product-repo:` line, because the idempotence check compares the whole
path against the stored prefix `C:\My` and never matches. Worse, a later
`publish` with no path argument resolves to `C:\My` — refusing outright, or
mirroring the release into that directory if it happens to be a git repo.
Caught by `test_a_path_with_spaces_round_trips`.

## What

The recorded path had no round-trippable format: the writer emitted it bare
and the reader consumed one whitespace-delimited token, so any path with a
space was stored whole and read back truncated. The truncating read predates
this work (`272c0a1`, publish's first commit); `6c20d03` inherited it into the
duplicate check.

## Approach

Reader and writer now share one shape, `_RECORDED`: a bare token, or a quoted
string when the path contains whitespace. `_recorded_paths()` is the single
parser (used by `recorded_product_repo()` and by the idempotence check) and
`_record_line()` the single writer, so the two cannot drift apart again — the
drift was the defect. Bare entries still parse, so everything recorded before
quoting existed keeps working, and no machines.md needs editing.

## Files changed

- `tools/publish.py:57-84` — `_RECORDED`, `_recorded_paths()`,
  `_record_line()`; `recorded_product_repo()` and `record_product_repo()` now
  go through them.
- `tests/test_publish.py:199-240` — `RecordProductRepoTests` parses with the
  tool's own pattern instead of a second tokenizer; two cases added.

## Guard proof

- `tests/test_publish.py::RecordProductRepoTests::test_a_path_with_spaces_round_trips`
  — asserts one recorded line and a lookup equal to the full path. Restoring
  the bare tokenizer and the unquoted writer makes it FAIL; the fix makes it
  PASS. The other four cases correctly stay green either way: they use paths
  with no whitespace, so they do not discriminate.
- `tests/test_publish.py::RecordProductRepoTests::test_a_bare_hand_written_entry_still_parses`
  — pins the backward compatibility the quoting change could have broken.

## Coder dispute (if any)

None on the defect. One correction to the finding's scope: the reviewer
attributed the truncating lookup to `6c20d03`. It shipped in `272c0a1` and is
unchanged by that commit — verified against `git show 7fcce43:tools/publish.py`.
`6c20d03` spread it to a second call site rather than introducing it.

## Known gaps

Quoting is applied on write; an entry a human hand-writes with a space and no
quotes still truncates. Nothing detects that, and no repo evidence suggests it
has ever happened.

## Reviewer comments

`Reviewer: codex / gpt-5.6-sol / max / standard`

- Harness: codex-cli 0.146.0, `codex exec -s workspace-write` reading the
  prompt on stdin, run from a disposable worktree of the head SHA. Dispatched
  with no `-m`: the owner asked for codex's own configured default, so the
  model resolved from `~/.codex/config.toml` (`model = "gpt-5.6-sol"`,
  `model_reasoning_effort = "max"`), and the CLI transcript confirms
  `model: gpt-5.6-sol` / `reasoning effort: max`. Not written to the tier
  cache: pinning a model the owner deliberately left unpinned is the stale-pin
  failure the 2026-07-31 bare-invocation decision exists to avoid. Tier
  standard; T1 evaluated against the range diff pre-dispatch and did not match.
- Reviewed `6c20d03d89277ba9d9520f141684ae70800457b9`, base
  `7fcce434f7b9863d2d58260322aa04415770ecf2`; `capability_ok: true`; verdict
  `findings` (1). 2026-07-31.
- Note on the reviewer's own verification run: it redirected `TEMP`/`TMP` into
  its worktree, which broke three `ProductRemoteFreshnessTests` cases on
  `git clone` inside its sandbox. Those pass in a normal run and are an
  artifact of the reviewer's environment, not a finding.
