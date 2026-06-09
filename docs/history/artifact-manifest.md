# Artifact Manifest

## Location

These artifacts are stored outside the example repo at:

`D:\source\AgentGovernanceBootstrap`

The example repo `D:\source\ExchangeAdminWeb` was not modified.

## Artifacts

| File | Purpose | Status |
|---|---|---|
| `bootstrap-plan.v0.md` | Versioned copy of the original plan. | Created |
| `bootstrap-plan.v1.md` | Revised plan incorporating review feedback on lifecycle, evidence promotion, verification derivation, baseline health, init/update mode, secret-safe discovery, monorepo scoping, and artifact staleness. | Created |
| `bootstrap-plan.v2.md` | Revised plan adding hybrid script/LLM mechanics, default harness adapter baseline, stable principles vs repo facts, plain-language fact refresh handling, command-driven operation, and current-checkout/clean-local-copy tests. | Created |
| `bootstrap-planv3.claude.md` | Claude-authored v3 draft adding operational contracts for secret-safety, apply semantics, grading, staleness, and implementation sequence. Filename preserved as received. | Added |
| `bootstrap-plan.v4.md` | Revised plan tightening v3 around LLM packet handoff, realistic secret-safety guarantees, staged apply semantics, explicit approval, and implementation-language portability. | Created |
| `bootstrap-plan.final.md` | Final approved plan incorporating valid v4 review points and closing the planning loop before implementation. | Created |
| `bootstrap-plan.v5.md` | Revised plan removing generated content packets and replacing them with manifest-only discovery. | Created |
| `bootstrap-plan.v6.md` | Revised plan switching the primary implementation surface from PowerShell to Python for cross-platform testing. | Created |
| `bootstrap-plan.v7.md` | Revised plan separating the core markdown/JSON governance system from implementation surface options and adding a no chat-context leakage rule. | Created |
| `bootstrap-plan.v8.md` | Revised plan simplifying workflow around an ignored in-repo `.agent-bootstrap/` handoff directory and AGENTS.md startup behavior. | Created |
| `bootstrap-plan.v9.md` | Revised plan replacing `.agent-bootstrap/` with `.bootstrap-tmp/`, adding first-run START-HERE.md, self-ignore behavior, freshness checks, and data-not-instructions handling. | Created |
| `bootstrap-plan-review.md` | Review of v0 plan (Claude). | Added |
| `bootstrap-plan-review_gemini.md` | Review of v1 plan (Gemini). | Added |
| `bootstrap-plan-review_claude.md` | Review of v2 plan (Claude). | Added |
| `bootstrap-plan-review_v4_gemini.md` | Review of v4 plan (Gemini, signed "Antigravity"). | Added |
| `bootstrap-plan-review_v4_claude.md` | Review of v4 plan (Claude): converged, no v5 needed; 4 residuals to resolve before coding. | Added |
| `bootstrap-plan-review_v5_claude.md` | Review of v5 plan (Claude): approves manifest-only direction; identifies update loop and grader scope clarifications. | Added |
| `artifact-manifest.md` | Records where artifacts live and confirms they are outside the example repo. | Created |

## Notes

No artifact files existed in the earlier temporary folder. The durable artifacts were created directly here after the durable external folder was approved.

All substantive revisions should keep old versions live using `v{N}` filenames. Do not keep unversioned plan files; the latest reviewed revision should be named with the next version number rather than replacing earlier versions.
