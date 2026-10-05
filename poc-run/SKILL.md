---
name: poc-run
description: Use ONLY when the user explicitly invokes /poc-run — for driving a proof-of-concept of any size, from a one-off model-performance measurement to a full design → staged experiments → pipeline build → e2e measurement → edge-case hardening cycle, including PoCs that start from a spec doc or mockup HTML. Does not auto-trigger.
---

# poc-run

## Overview

Orchestrates a proof-of-concept from start to finish. Scales from a single "measure this model" task to a full lifecycle. It does not do the work autonomously — it drives a tight, human-in-the-loop loop and applies evaluation gates at every measurement and decision.

Two invariants hold across every PoC:
1. **Operating rule** — heavy human-in-the-loop; never auto-advance.
2. **Gate spine** — a fixed evaluation discipline applied at each measurement/decision.

Everything else (phases, tools) is selected to fit the specific PoC.

## Operating rule (highest priority)

- **Never auto-advance.** No phase begins without the user's go-ahead.
- **Sub-skills fire only on request.** poc-run *can* design, generate data, harden, etc., but each sub-skill (brainstorming, data generation, experiments…) runs only when the user asks for it.
- **After finishing a step, recommend the next as options and wait.** e.g. *"Next: run per-stage trend research, or start dataset prep for stage 1?"*
- **Ask the user for PoC scale/goal** at the start — do not infer it.
- **Report the basis** for every decision, measurement, and verdict — label each value as measured / official-doc / estimate, and attach source URLs when citing external or official material.

If unsure whether to proceed, stop and ask. Presenting options ≠ starting them.

## Gate spine (always apply, domain-agnostic)

Apply the relevant gates at every measurement/decision. Report against them.

1. **Fix success criteria first** — set numeric thresholds *before* measuring. If there are scenarios/cases, define per-scenario success/failure/exception up front.
2. **Separate the holdout; never tune on it.**
3. **Repeat N times for nondeterministic systems** — a single flip is noise, not signal.
4. **State cost/latency ceilings.**
5. **Report in-sample and held-out separately.**
6. **Keep a chronic-failure catalog** — record recurring failure types.
7. **Attribute failures to the right layer** — an upstream fallback/sentinel must not masquerade as success.
8. **Regression check (before-after)** — when iterating (v2, v3…), confirm no regression vs the prior version.
9. **Prefer measured over estimated** — if the system already returns the real value (cost, tokens, status), read it; don't estimate. Never present an estimate as a measurement; label derived/vendor-published numbers as such (URL for official sources).
10. **Define comparison arms up front** — enumerate every arm before measuring; include the baseline (current production path) when one exists, otherwise state there is none.

Keep this spine free of product names and specific numbers so it ports across PoCs.

## Phase map — enter each ONLY on user request

| Phase | What it is | Gates that apply |
|---|---|---|
| 0. Intake | receive spec doc / mockup HTML / requirements | — |
| 1. Trend research | latest dev practice as of today's date | prep success criteria |
| 2. Design | research → big picture → decompose into stages | per-stage pass conditions |
| 3. Dataset | if absent, collect + generate | holdout split up front |
| 4. Staged experiments | compare variants, measure | N-repeat, no holdout tuning |
| 5. Pipeline build | assemble stages | check upstream error propagation |
| 6. E2E measurement | integrated performance | in-sample↔held-out, cost/latency |
| 7. Edge-case hardening | shore up failures | update chronic-failure catalog |
| 8. Completion check | evidence-based verdict | final numeric gate |
| 9. Migration | when production-ready | see Migration section |

**Situational extra phases** (common in past PoCs, insert as needed):
- **Model & cost comparison** (early): compare candidate models on quality/cost/latency → gates: cost/latency ceiling, N-repeat.
- **Environment/infra provisioning** (before experiments): vector DB / Docker / model access & quota.

At the end of any phase: recommend next-phase options and wait.

## Tool hints — pick what fits the PoC (do not run them all)

**A. Process (superpowers):** `brainstorming` (design intent), `writing-plans`/`executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents` (independent experiments), `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`/`receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch`.

**B. Intake — spec / mockup → design:** `Read` (PDF/MD/HTML/images), `WebFetch` (hosted mockup URL), `understand-anything:understand-figma`, `Plan` agent, `artifact-design`/`dataviz` (UI reference), `brainstorming`.

**C. Trend research (as of today) — required at design time.** `WebSearch`/`WebFetch`, `general-purpose` agent (deep fan-out), arxiv/papers, `Workflow`※ (large multi-modal sweep). Research dimensions (example: text-to-SQL):
1. How do real services building this feature implement it?
2. What errors/problems have practitioners hit?
3. Are there published fixes?
4. If not, what must we prepare for?
5. What pipeline composition is trending?
6. What research results / practitioner write-ups exist?
7. What are the security threats & mitigations? (e.g. prompt/SQL injection for text-to-SQL — research at design time)

**D. Explore/understand existing code:** `Explore` agent, `understand-anything:understand`, `pyright-lsp`.

**E. Output/verify:** `dataviz` (eval charts), `superpowers:requesting-code-review` (independent review of large changes, on request).

**F. Large-scale only (opt-in, needs user approval):** `Workflow` — experiment/research fan-out & verification pipelines.

## Dataset absent → collect + generate

**Collect (web):** `WebSearch`/`WebFetch`, `general-purpose`/`Explore` agents, `Workflow`※.
**Generate (synthetic):** `claude-api` skill (generation pipeline), Claude directly, `Workflow`※ (mind rate-limit pacing), `dataviz` (distribution).

**Prerequisite for quality/accuracy decisions:** if the PoC's verdict rests on quality or accuracy, a prepared dataset is a prerequisite — do not measure on inline ad-hoc queries hardcoded in the harness. Surface this to the user up front (surfacing a prerequisite is not auto-advancing): externalize to a versioned file, cover the relevant domains/categories, size it for a stable read (sufficient N).

**Data quality gates (required):**
- Holdout split up front (design by purpose; do not split arbitrarily after generating).
- Generation-bias: generating an eval goldenset with the same model family as the target biases results → keep them independent.
- LLM-as-judge independence: separate target vs judge model; manage the judge prompt as its own artifact.
- Scrub PII/secrets from web-collected data.
- Check licensing/ToS.
- Version the dataset (reproducibility).
- Never send sensitive internal data to external services.

**Judge implementation — two paths.** General concept: *LLM-as-a-judge*. The variant where the current session / a subagent grades directly (no API wiring) is *Agent-as-a-Judge (in-session / subagent-based judging)*.
- **(1) In-session subagent judging** — session spawns a subagent to read outputs and score. No keys/endpoints, fast PoC iteration; but consumes session tokens, weak reproducibility. **Default for early/small iterations.**
- **(2) API-harness judging** — scripted call to a separate model endpoint. Reproducible, batch/CI-friendly; needs wiring & quota. **Promote to this for large/regression/CI.**
Either way apply the judge-independence + prompt-management gates. For subagent judging, follow the session's subagent model policy.

## PoC → production migration (when production-ready)

`poc/` is a personal, uncommitted asset. Migration = **re-implement learnings into `src/` to team standards**, not copy PoC code.

- Plan: `writing-plans` (poc learnings → staged src re-implementation).
- Isolate: `using-git-worktrees`. Impact: `understand-anything:understand-diff`.
- Quality: `test-driven-development`, `pyright-lsp`.
- Security gate (required before prod): local `/security` (bandit, pip-audit), `/security-review`.
- Review: `superpowers:requesting-code-review`. Evidence: `verification-before-completion`. Integrate: `finishing-a-development-branch`.

Checkpoints: no hardcoded secrets (env/SM/1Password), team-standard logging, harden error handling & input validation, respect HITL/other-owner boundaries, follow commit rules (src → hand the user the command; never commit `poc/` or `docs/`).

## House conventions (from memory / CLAUDE.md — honor, don't hardcode into gates)

- **Numbered stage docs**: `01-prep → 02-research → 03-goldenset → 04-pipeline → 05-prompt → … → NN-migration`, plus `PLAN.md`/`SUMMARY.md`/`NN-final-report.md`, living `진행상황.md`/`todo.md`. Offer to leave these under `poc/` (personal asset, no commit).
- **Iterate as `v2`, `v3`**; pair with the regression gate.
- **Eval report sections**: headline / quality / timing / distribution.
- **Common early phases**: model longlist → model & cost comparison; environment provisioning.

## Common mistakes

- Barreling through phases without asking → violates the operating rule.
- Inferring scale instead of asking the user.
- Running sub-skills the user didn't request.
- Tuning on the holdout, or reporting a blended number instead of in-sample/held-out split.
- Treating a single nondeterministic run as signal.
- Using the same model family to both generate the goldenset and be evaluated / judge.
- Copying `poc/` code into `src/` instead of re-implementing to team standards.
- Measuring a quality/accuracy verdict on inline ad-hoc queries instead of a prepared, externalized dataset.
- Omitting the baseline (current production path) from the comparison when one exists.
- Presenting an estimate as a measurement, or estimating a value the system already returns.
- Citing an official/external claim without attaching its source URL.
