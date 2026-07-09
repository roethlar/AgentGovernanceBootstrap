# refresh.py: unmissable non-replacement notice + offer to run bootstrap

Status: DRAFT 2026-07-09, awaiting owner go on this plan. Direction is
owner-set (this session, 2026-07-09): the refresh output that matters is an
**unmissable notice that a core file was NOT replaced, for any reason**; the
notice resolves to "run bootstrap"; and refresh should **offer to run
bootstrap**, with a harness chosen from those installed on the machine at
that moment. Standing constraints (owner, 2026-07-09, recorded with the
declined shim proposal in `docs/history/state-archive.md`): must not assume
Claude, PowerShell, a remembered path, or a remembered interpreter.

## Why this plan exists

Today a refused core-file replacement is a single
`  FLAG <target>: <reason>` line emitted by `summarize()`
(`tools/refresh.py:329-330`), interleaved with installed/updated/removed
lines and followed by the NOTE/LINT lint block, and `main()` returns 0
regardless (`:387`). The one line the owner actually cares about is the
easiest one to miss.

The core case already exists and already names the fix — the
`replace-whole` refusal (`:149-155`) for an `AGENTS.md` that matches no
known template version says "run the bootstrap procedure instead" — but in
prose, mid-list, with recovery left entirely to the reader: know the
procedure exists, pick a harness, compose the kickoff prompt by hand. This
is the entry friction the smoother-entry record has tracked since the
qbit-mobile carve-out run.

## Design

**1. The banner.** After all other output, if any flag sits on a
`replace-whole` artifact (today exactly one: `AGENTS.md`, the core-file
class), print a closing block that cannot be read past:

    ==================================================================
      ATTENTION: AGENTS.md was NOT replaced.
      It matches no known template version (hand-edited or foreign).
      Hand-repair is not the fix. The fix is the bootstrap procedure.
    ==================================================================

Scope call, made here: the banner fires **only** for `replace-whole` flags.
The other flag classes — owner-modified `replace-if-unmodified` artifacts,
retired-but-modified, unrecognized-ignore skips — are legitimate,
potentially permanent steady states; a banner that fires forever on every
owner-modified wrapper is a cried wolf, and the owner named *core file*
specifically.

**2. The offer.** When the banner fires **and** stdin and stdout are both a
TTY, refresh enumerates installed harness CLIs and asks one question:

    Run bootstrap now? Installed harnesses: [1] claude  [2] codex  [q] no
    >

A number launches that harness interactively in the target repo, with a
kickoff prompt naming the toolkit's `procedures/bootstrap.md` (path resolved
from `__file__` at that moment — never remembered) and the target repo path,
and instructing: read the procedure in full, then run it against this repo.
`q`/empty/EOF declines and changes nothing.

Non-TTY (agent-run refresh, CI, piped output): **never prompt, never
hang** — below the banner, print the exact ready-to-paste launch command for
each detected harness instead. Exit code stays 0: the advisory contract and
the bootstrap `--stage-only` flow are unchanged; unmissability comes from
the banner, and agents read stdout.

**3. Harness detection.** A small constant table in `tools/refresh.py` —
(executable name, interactive-launch argv shape with a prompt slot) — seeded
from the recorded live behavior in `docs/harness-capabilities.md`: `claude`,
`codex`, `gemini`, `grok`. Detection is `shutil.which` per candidate at
offer time; only hits are offered, in table order, no default. Nothing is
remembered between runs. Adding a harness to the table is a normal
provenance-bearing change (standing rule, 2026-07-08). If nothing is
detected: banner still prints, offer degrades to naming the procedure path.

Why this satisfies the constraints: no Claude assumption (enumerate what is
installed), no PowerShell (pure Python + `shutil.which`), no remembered path
(toolkit root from `__file__`, target from argv), no remembered interpreter
(the offer runs inside the interpreter already executing refresh).

## Slice 1 — banner + non-TTY command block (code and tests)

- `classify()` flags gain the artifact class (or a
  `core_flags(plan, shipped)` helper derives it); `main()` prints the banner
  block after the lint output when any `replace-whole` flag exists.
- Non-TTY branch: detected-harness launch commands printed under the banner.
- Tests: banner present exactly when a `replace-whole` flag exists (foreign
  `AGENTS.md` fixture); absent for owner-modified-wrapper and clean-repo
  fixtures; non-TTY output contains commands and no prompt is attempted.

## Slice 2 — interactive offer + launch (code and tests)

- `detect_harnesses(which=shutil.which)` and
  `offer_bootstrap(candidates, input_fn, launch_fn)` — dependency-injected
  so tests never touch a real TTY or spawn a harness.
- TTY gate: `sys.stdin.isatty() and sys.stdout.isatty()`.
- Launch: `subprocess.call` with inherited stdio, cwd = target repo, argv
  from the table with the kickoff prompt filled in.
- Tests: fake `which` → enumeration order and misses; scripted `input_fn` →
  launch argv composition, decline paths (q / empty / EOF) are no-ops;
  guard proof — with the TTY gate forced false, no `input_fn` call occurs.

## Slice 3 — bookkeeping

- Decisions entry (the shipped-behavior change needs provenance per the
  2026-07-08 standing rule), citing this plan and the owner direction.
- `.agents/state.md`: resolve the smoother-entry Next bullet (rotate
  verbatim to `docs/history/state-archive.md`); this closes the
  entry-friction thread opened 2026-07-09.
- Self-refresh this repo (expects: current, banner absent) and one deliberate
  foreign-`AGENTS.md` run in a scratch clone to see the banner + offer live.
- This plan's Status updated with the commit map.

## Verification

Full suite per `.agents/repo-guidance.md` (Verification) after every slice;
slice-2 guard proof above; the live scratch-clone demonstration in slice 3.

## Non-goals and risks

- **No new entry point, no shim, no PATH step** — the declined 2026-07-09
  proposal stays declined; this changes only what refresh does when it
  refuses.
- **No behavior change on the happy path** — clean repos and normal
  reconciliations print exactly what they print today.
- **No auto-run** — the harness launches only on an explicit interactive
  yes; agent-run refreshes can never trigger a launch (TTY gate).
- Harness CLIs change invocation shapes over time; the table rides on
  `docs/harness-capabilities.md` currency, and a stale entry degrades to a
  failed launch the owner sees immediately — loud, not silent.
- Windows: `shutil.which` honors PATHEXT; the launch inherits the console.
  The Store-stub hazard is a Python-interpreter problem and does not apply
  to harness executables, but a stub-like miss just means a failed launch,
  same loud degradation.

Provenance: owner direction this session (2026-07-09) — the unmissable
non-replacement notice resolving to "run bootstrap," offered with a harness
chosen from what is installed; standing constraints from the declined
shim/skill proposal (archived 2026-07-09).
