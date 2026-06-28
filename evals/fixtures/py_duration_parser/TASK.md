# Synthetic fixture — Python, combined duration parsing

> Harness documentation only — **not** sent to the agent. The agent-facing prompt is
> `PROMPT.md`.

A synthetic (not mined-from-history) fixture covering the third language, Python. The
inline `files/` payload ships a `duration.py` that handles single units but not combined
"1h30m" forms, plus a stdlib-`unittest` test that fails until the combined case works.
The agent must fix `duration.py` only.

Stdlib `unittest` is used deliberately — no pytest install, dependency-free, runs
anywhere. Verify: `python3 -m unittest test_duration` (non-zero exit on failure).

Non-vacuous by construction: on the shipped code the combined-units test is red; a
correct fix makes the suite green.
