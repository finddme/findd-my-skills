---
name: self-review-light
description: Use ONLY when the user explicitly invokes /self-review-light — for a thorough, multi-pass review of a branch/PR's own code changes before merge (beyond a single quick pass), then hardening confirmed issues. Does not auto-trigger.
---

# self-review-light

## Overview

Reviews a branch/PR's own changes by **broad discovery → independent re-review → systematic checklist sweep**, judging every finding against the actual code/runtime, then hardening only confirmed issues through a document-first loop.

Scale to the request: a light check runs pass 1 only; "thorough/audit" runs all three passes.

**Build on existing tools (do not reimplement):**
- Pass 1 discovery uses the `code-review` plugin's multi-agent *methodology* (the 5 agents below), run as the skill describes.
- Pass 2 independent re-review — **REQUIRED SUB-SKILL:** `superpowers:requesting-code-review`.

## Phase 0 — scope

- Identify current branch/PR; isolate the **feature diff only** (exclude unrelated changes pulled in by a merge).
- Diff against the base branch's merge-base (base branch is per-project: main/dev/…):
  ```bash
  base=$(git merge-base main HEAD)
  git diff --stat $base..HEAD -- 'src/**'
  ```
- If a PR exists, check eligibility: `gh pr view <n> --json state,isDraft` (closed/draft/existing reviews).

## Pass 1 — multi-angle discovery + confidence scoring

Cheap prep (low-cost model): PR eligibility, collect relevant CLAUDE.md paths, summarize the diff.

Five parallel review agents (harder analysis → stronger model):

| # | Angle |
|---|---|
| 1 | CLAUDE.md (project rules) compliance |
| 2 | Bug scan (logic / None / resource / security holes) |
| 3 | git blame · history + diff hygiene (past-fix regressions; and whether changed user-facing constants / error codes / messages are intentional, not silent regressions) |
| 4 | Prior PR comments (unresolved points re-applied) |
| 5 | Comment/docstring vs actual behavior (promise ↔ reality) |

Score each finding 0–100 → **filter out below 80**: 0=false-positive/known, 50=real but minor, 75=real + reachable in real use, 100=certain + frequent. Re-verify any CLAUDE.md-based claim against whether the rule actually states it.

**Intent-confirmation / QQ items are a separate track, exempt from the ≥80 defect filter.** A finding whose behavior may be intended but needs author/planner confirmation (spec ambiguity, silent behavior change, "is this intended?") is not a defect to score — carry it as a question to raise, even if minor.

**Dedup vs existing review** — drop what human review / automated gates already caught; keep net-new only.

## Pass 2 — independent re-review

- Give the reviewer subagent **precise context only** (no session history).
- **Do NOT pass pass-1 results** → unbiased re-review.
- If possible, run the **actual tests in the container**.
- Output: net-new that pass 1 missed + **conflicts/corrections vs pass 1**.

## Pass 3 — systematic coverage sweep

Split the standard checklist into 7 clusters and sweep each in parallel. **Inject the already-found issue list** into each agent → focus on net-new only.

**Checklist:** read `references/checklist.md` when running this pass (do not load it earlier).

## Cross-check principle (all passes)

- **Conflicts/doubts: no guessing — decide by code/container evidence.** (e.g. grep + runtime for an undeclared/unwired path; inspect the build artifact directly → correct false positives.)
- **Record false positives and corrections** — "why it was a false positive" is an asset for the next review.
- **Distinguish environment failure from real failure** — e.g. an error from a missing external dependency (registry/service) is not a code defect.
- **External-dependency claims: verify against the installed version's source + official docs (web search), not memory.** Library defaults, response schemas, and version-specific fields change between versions.

## Confirm → plan → implement loop (per issue)

1. **Confirm direction** — Q&A with the user; verify the basis in code (remove vs fix, etc.).
2. **Write plan/design in a doc first** — plan-first even if it looks small. The doc is the single source of approval/criteria.
3. **Re-check the real code while implementing** — adjust if the plan diverges from code reality (e.g. "needs wiring" but it's already wired → only the prompt needs changing).
4. **Verify** — run container tests + a broad sweep for regressions.

## git discipline

- **tests/ = commit directly (co-authored tag)**, **src etc. = hand the user the command.**
- Add per-file (no folder-wide add), one-line commit message (`type(scope): desc`), **separate commit per issue**.
- New files: `git add -f <exact path>` (catch-all exclude workaround).
- **Never commit docs / personal assets** (prevent remote leak). No `git add .`/`-A`/`git clean`.

## Notes

- If the target branch is already merged upstream, later fixes stack as new commits on that base — check the base branch first.
- Run execution/verification **only inside the project's designated container** (no host ad-hoc). e.g. `<service>-dev`. If the example containers are unsuitable and no discovered container fits, **ask the user which environment to run in.**
- Secrets (API/secret keys, cloud credentials) must never appear in output/commits/logs — mask and warn if found.

## Common mistakes

- Skipping the confidence filter → drowning in low-value findings.
- Passing pass-1 results into pass 2 → biased re-review.
- Guessing on a conflict instead of confirming by code/runtime.
- Treating an environment failure as a code defect.
- Implementing before writing the plan doc.
