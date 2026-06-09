# Decision Note: Tool Language & Artifact Coupling

**Author:** Claude (Opus 4.8) · **Date:** 2026-06-08 · **Status:** Open — awaiting human tie-breaker on Decision 2

Context: collaborating on the actual build. The v6 plan pivoted PowerShell-first →
Python-first to "reduce surface and streamline multi-platform usage." This note records the
reasoning that the v6 review (`bootstrap-plan-review_v6_claude.md`) only partially captured.
The review caught the artifact-coupling symptom but assumed the tool language was settled as
Python and did not work through the Go alternative or the cleaner decoupling below.

## Two decisions were merged in v6; they are orthogonal

1. **Tool language** — what you run to `discover`/`apply`/`grade`.
2. **Generated-artifact language** — the grader/checks that land *inside* each target repo.

The Python pivot was aimed at Decision 1 (kill the PS+bash duplication). The damage was that
it dragged Decision 2 along (`grade-agent-run.py`, `.agents/checks.py`), pushing a Python
runtime into every bootstrapped repo — including Go/.NET/JS repos with no other Python. That
contradicts the plan's own portability principle.

## Decision 2 (decide first — highest value, language-independent)

**Generated repos receive docs + data only. No executable logic.**

- **Grader** logic stays *in the tool*: `agent-bootstrap grade <run-file>`. The repo already
  has the tool (it was used to `discover`/`apply`), so there is no new dependency and no
  language question. Drop `grade-agent-run.py` from Generated Artifacts.
- **Checks** is not a "language" — it sequences the repo's own commands (`npm test`,
  `dotnet build`). Emit a thin native wrapper (`.sh`/`.ps1`/`.cmd`) chosen from the repo's
  observed conventions, or record the command list in `repo-map.md` and let the tool run it.
  Drop `.agents/checks.py`.

Result: target repos get only AGENTS.md / repo-map / playbooks / manifests + a native
wrapper. **Zero runtime coupling, regardless of what the tool is written in.** This dissolves
v6 review finding #1 instead of patching it.

## Decision 1 (tool language) — depends on a distribution tie-breaker

Neither candidate is literally "one binary, all OSes."

| | Python | Go |
|---|---|---|
| Distributable unit | One source tree | N prebuilt binaries (one per OS/arch) |
| Host requirement | Compatible Python + package install (pipx/venv) per machine | **Nothing** — static binary |
| Cross-build | n/a | From one machine: `GOOS/GOARCH` env vars → all targets |
| Iteration speed | Best | Medium |
| Release plumbing | `pip install` / pipx | Build + publish 3–6 files (GitHub Releases) |

- **Python** = single source, runtime required on every host (version-skew + install burden).
- **Go** = a handful of prebuilt files, nothing required on any host.

The tool is mostly file-walking, git plumbing, and YAML/markdown emission — both languages
do this comfortably; pure-Go (no cgo) keeps the static-binary property.

### Tie-breaker question

**Will this tool run on machines you don't control (CI images, other teams, fresh laptops)?**

- **Yes** → **Go.** The no-install static binary is the real "minimal surface" the pivot was
  reaching for; the release plumbing pays for itself.
- **No (dev boxes that already have Python)** → **Python.** Bank the iteration speed — and
  once Decision 2 removes Python from target repos, Python's only real weakness is gone.

## Recommendation

1. Adopt Decision 2 now, unconditionally. Remove `grade-agent-run.py` and `.agents/checks.py`
   from the Generated Artifacts list; add `agent-bootstrap grade` and native check-wrappers.
2. Answer the tie-breaker for Decision 1, then commit the tool language and start the
   skeleton. Do not open a v7 just to record this — fold it into the implementation.
