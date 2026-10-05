---
name: vet-review
description: Use ONLY when the user explicitly invokes /vet-review — when you have RECEIVED a code review (from a person or a tool) and need to judge each point's validity against the actual code before acting, then document and fix only the valid ones. Does not auto-trigger.
---

# vet-review

## Overview

Judges a **received** code review before acting on it: verify each point against the real code, document the verdict per item, and fix only what holds up.

**Core principle — verify before implement.** Do not start with the social agreement "good point." Judge validity against code reality first.

**REQUIRED BACKGROUND:** `superpowers:receiving-code-review` (verify-before-implement, no performative agreement). This skill adds triangulation, history-vetting, and per-item documentation on top.

## Principles

- **Don't trust comments/docs — establish facts from code only.** Don't assume a comment/docstring/doc's "behavior description" is true. Read the actual control flow / conditions / return values / call graph and **confirm real behavior** before judging. A comment that disagrees with the code is itself a finding.
- **Be skeptical of external review.** Is it actually right for this codebase/stack? Does it break existing behavior? Is there a reason for the current implementation? Does the reviewer know the full context?
- **Question-type review** ("is this intended?") → establish intent from history first, then answer.
- **No performative agreement.** Respond with evidence/actions, not "you're right / good point."

## 1. Read / classify

Read the whole received review first, classify each item: `bug/security (blocking)` · `improvement` · `question (intent)` · `unclear`.

- **Input can be a self-review ledger** (handed over by the user). Read each `### <id>` item block as one review item; its `confidence`/`repro` are the reviewer's claim, still to be verified (§2). Update the item's `status` in the ledger when it is resolved (`fixed <hash>` / `wontfix` / `deferred`).

> If any item is unclear, **ask first.** No partial start (items may be interrelated).

## 2. Independent verdict (cross-check)

Don't take the received review's conclusion at face value — judge the code independently.

- **Read the actual code.** Confirm each point against the real code; if a tool's result disagrees with the code, follow the code.
- **superpowers code review** (`requesting-code-review`) — an independent LLM review, internal (posts nowhere).
- **A deterministic checker matched to the finding type** — security/injection/secrets → bandit / pip-audit (or Semgrep if available); types/signatures → `pyright-lsp`. These give an objective yes/no, unlike a second LLM reviewer (whose result just correlates with the first).

> ⚠️ Do NOT use the `code-review` plugin (`code-review:code-review`) here — its workflow reviews a GitHub PR and **posts the result as a `gh pr comment`**. Only use it when you actually intend to post to a PR.

Compare (independent review(s) + received review + direct code read) → verdict:

| Verdict | Meaning |
|---|---|
| Valid | review(s) + code confirmation agree |
| Partially valid | only partly holds / needs scope/condition limits |
| Refuted | grounded disagreement (proven by code/test) |
| History needed | re-judge after establishing intent |
| Duplicate | valid, but the same defect is already handled (done or in progress) by another item — cite that item's commits instead of fixing again |

**Duplicate vs. refuted:** "it looks already fixed" is not a refutation. If the fix landed *after* the review was written, the review was valid → **Duplicate**, never Refuted (see §3 timing check).

Reading the code directly comes first; re-verify tool/agent results against code too.

**Token scope:** run the cross-check on blocking/unclear items; light items can be judged from code directly.

## 3. Intent / history (when needed)

For question-type items or "why was it done this way":

- **Ask the user what to reference first** — design/spec doc location, related PoC/experiment paths, issues/PRs, decision records. Locations differ per project; don't guess.
- **Always check the file's last-modified date** and prefer the latest decision (older docs may diverge; code + latest docs win).
- If a fixed design/invariant exists (architecture map, safety mechanism), compare against it to judge "intended behavior."
- Use git history (`git log` / `git blame`) to establish the change's origin/intent.
- **Timing check for "already fixed / stale" judgments.** A GitHub inline comment's `commit_id` is *updated* to the latest commit; it is not the commit the reviewer saw. Compare the comment's `original_commit_id` and `created_at` with the fix commit's time before calling a review stale. Fixed after the review → Duplicate (§2), not Refuted.

## 4. Respond (verdict report)

Report in this shape (headings and prose in the user's language; include a section only when it applies):

```markdown
## <item no.> verdict: <valid | partially valid | refuted | history needed | duplicate> (<class>)
<1–2 sentences, reproduction/measurement result first>

**Reproduction** (when run)
| input | expected | actual |

| item | verdict | basis (file:line / measurement) | action (fix / keep / ask) |

## History (only when overturning an earlier decision)
<what was decided when, what this overturns, what stays unchanged>

## Decision values to confirm (only when there are open values)
| # | decision | recommendation | basis (type: derived / measured / external spec / decision / estimate) |

## Reply text (only for refuted / duplicate)
<short text to paste into the review thread>

<one-line question: proceed as recommended?>
```

Writing rules:
1. **Conclusion first** — verdict heading → key 1–2 sentences → tables.
2. **Show reproduction as a table before prose** (input → expected → actual).
3. **Conditional sections:** add *History* when overturning a prior decision (say what is overturned and what stays); omit *Decision values* when none are open; add *Reply text* for refuted/duplicate.
4. The *basis* column of the decision table uses the evidence types in §6 (mark estimates as "estimate").
5. Number decision values `D-1, D-2 …` matching the item doc. No circled numbers.
6. Short sentences, comparisons in tables, no repetition (tighten-prose style).
7. If the user asks for a simpler re-explanation, summarize in this order: conclusion → what the review asks → what conflicts with what → is it a real problem → does it deviate from product intent.
8. When refuting, give technical grounds and note if the reviewer missed context.

## 5. Per-item documentation

After the verdict, document each **fix-target** item.

- **Ask the user where to write the docs first.** Don't create arbitrarily.
- **One file per review item.**
- **Header lines (fixed form — `review-post reply` reads them):** labels in the user's language (e.g. Korean `리뷰:`/`상태:`/`커밋:`) or English.
  ```markdown
  - Review: <PR> [<id>](<link with #discussion_r<id> or #issuecomment-<id>>) (<reviewer>, <date>, <commit>, <path:line>)
  - Status: <in progress | done | deferred | refuted | duplicate | n/a> (<date>)
  - Commits: `<hash>` (tests, <author>) · `<hash>` (src, <author>)   ← when done / duplicate (cite the other item's hashes)
  ```
  A batch doc covering several review links lists them in an item table with a **link column and per-item status**.

Each file contains (write plainly, easy to read):
1. **Review content** — exactly what was raised (quote it).
2. **What the problem is** — why it's a problem.
3. **What the problem could lead to** — the *problem's* real impact/risk if left unfixed (with an **example** if helpful).
4. **What to fix** — the fix, clearly.
5. **Fix risk · cautions** — risks and easy-to-miss points introduced by the *fix itself* (distinct from item 3, which is the problem's risk). What could this change break or get wrong?
6. **Side-effect review** — pre-analysis of the change's blast radius: callers of the touched code, the I/O contract, shared/global state, other paths relying on current behavior.
7. **If it changes an I/O contract** — if the fix changes the input/output contract with the backend (BE) or other external systems, include **input/output data examples** of the change.
8. **Fix plan as a step-by-step todo checklist** — write the plan/design as concrete, executable todo items (not prose). This checklist is exactly what §6 loads and eliminates one by one.
   - **Per-step cautions:** under each todo step that carries risk, add an indented `⚠` line directly beneath it — a one-line summary of only the §5.5 (fix risk) / §5.6 (side-effect) points that apply to *that step*, tagged with the source section (e.g. `(5-1)`). Skip steps with no risk (lint, etc.). §5.5/§5.6 remain the full analysis; the `⚠` lines are the at-execution summary, so keep them consistent.
     ```markdown
     - [ ] 8-2. Add `_validate_response_schema` + call it after the status check
       - ⚠ Only check name/type are non-empty strings; don't validate type vocabulary or extra keys (avoid rejecting valid responses, 5-1)
       - ⚠ Never put field values in the error reason — index/type name only (5-2)
     ```
9. **Commit record** — once the fix lands, record every commit that resolved this item: short hash, scope (tests / src / etc.), author (Claude / user), and the commit message. Put the hash(es) in the doc header too, so the review → commit trace is visible at a glance. An item isn't "done" until its commits are recorded.

> This file is the **approval basis / single source of truth** for the §6 fix. The items 5–6 (fix risk · side-effects) and item 8 (todo checklist) are what §6 reads before and during execution.

**Refuted / duplicate items** — write the header + review gist + **reply text**. Mark whether the reply text is final. If a verdict changes after a reply was already posted, write a **correction reply** text too (posting stays with the user).

## 6. Fix → design → implement

Only for items judged valid; driven by the §5 per-item docs.

### Decision values need evidence

Applies to every value proposed in §4's decision table and in the §5 doc.

1. **Every numeric decision value carries an evidence type.** Targets: limits, timeouts, sizes, counts, retry counts, thresholds.

   | Evidence type | Meaning | Write down |
   |---|---|---|
   | derived | computed from existing constants/contracts | formula + base constants (`file:line`) |
   | measured | obtained by measurement | command, data, result |
   | external spec | official doc/standard | doc + version |
   | decision | set by the user/product | source (doc, date) |
   | estimate | none of the above | label it **"estimate"** and state the assumptions |

2. **No evidence → do not recommend a value.** Propose a **measurement plan** instead (what to measure to fix the value, target data, cost).
3. **A reviewer's example value is not evidence** — treat it as something to verify.
4. **State representativeness and limits** of the evidence (e.g. "local test/synthetic data only, not production data").
5. **Ask before costly measurement** — repeated LLM calls, paid external APIs, rate-limited calls, production reads. Give call count and concurrency.
6. **When evidence is thin, say which way it is safer to be wrong** (over-blocking valid requests vs. letting some problems through) and why.
7. **State when to revisit the value** (base constant changes, upstream contract changes, production measurement becomes possible). Keep derived values as a formula in code so they move with their base constants.
8. **Several candidates → comparison table:** value · evidence type · impact on normal cases · blocking effect · notes.
9. **Non-numeric decisions (location, approach, log level, return shape) need grounds too** — if it follows an existing code convention, cite it (`file:line`).
10. **Constants added to code get a rationale comment** ("why this value"), without dates or process narration.

### Steps

1. **Present the fix plan/design and get approval before starting** (no jumping to code). Approval must cover **every open decision value, not just the approach** — numbers (limits, timeouts, sizes), locations (config vs. constant, which file), and verification scope (e2e cases, counts). If the user only picked the approach, ask for the remaining values before starting; never fill them with your own defaults. If a value must change mid-execution (e.g. reduce concurrency for a rate limit), ask before changing it.
2. **Work through the §5 checklists in the doc itself**, ordered **blocking → simple fixes → complex fixes**, ticking each step `[x]` in the doc as it completes. (Do not rely on TodoWrite/Task tools — they are disabled by default on current models and the user chose not to enable them; the doc checklist is the tracker.)
3. **Before executing each todo item, read its `⚠` lines (§5.8) first, then re-read the fix risk · cautions (§5.5) and side-effect review (§5.6)** from its doc, and execute accordingly.
4. **One item at a time**, test each, confirm no regression, then **check it off** — proceed until the checklist is fully eliminated.
5. **After committing, record the commits in the item's doc (§5.9).** For `src` commits made by the user, ask for / look up the hash (`git log`) once they confirm the commit, then record it.

### git discipline

Follow the user's commit rules from memory / CLAUDE.md; if none are recorded, ask. The defaults below are this user's rules:

- `tests/` only = commit directly (co-authored tag).
- `src` etc. = hand the user the command.
- `docs/`, `poc/` = never commit (personal assets).
- `git push` / PR creation = never autonomous, always ask the user. Check the base branch first.
- Commit message = one English line `type: desc` (e.g. `fix: reject empty schema in ready response`).
  - (Note: the `(scope)` after the type is not required — no need to write the area in parentheses like `feat(manager): ...`; plain `feat: ...` / `fix: ...` is fine.)

### Posting replies to the review

- Posting is outward-facing. When the user wants the **resolving commits** posted to the review threads (usually once, after all items are handled), **ask first whether to use the `review-post` skill** (`reply` mode, fed with the item docs folder), if it is installed. Do not post on your own.
- Refuted/rationale replies are posted by the user while handling each item; `review-post reply` does not post them.
- Required internal sub-skills (`superpowers:requesting-code-review` for the cross-check, `superpowers:receiving-code-review` as background) are used without asking, as before.

## Notes

- If the target branch is already merged upstream, later fixes stack as new commits on that base — check the base branch first.
- **Execution environment:** do not assume one. Check memory / CLAUDE.md for the project's rule first (e.g. "run only inside container X"); if none, **ask the user** which environment to use (container, host venv allowed or not) and whether starting/restarting servers is allowed. Explore facts (test runner, entrypoints, running processes) read-only yourself; never read secret values.
- Secrets (API/secret keys, cloud credentials) must never appear in output/commits/logs — mask and warn if found.

## Common mistakes

- Agreeing before verifying against the code.
- Trusting a comment/doc's description instead of reading real behavior.
- Starting fixes on unclear items instead of asking first.
- Documenting a contract change without input/output examples.
- Jumping to code before the per-item doc/plan is approved.
- Confusing the problem's risk (§5.3) with the fix's own risk (§5.5) — collapsing both into one line.
- Executing a fix step without first re-reading its fix-risk/side-effect notes.
- Writing the fix plan as prose instead of an executable todo checklist to eliminate.
- Marking an item done without recording its commit hashes in the doc (§5.9).
- Leaving risky todo steps without their `⚠` caution lines (§5.8), so step-specific risks get lost at execution time.
- Getting approval for the approach only, then silently picking numbers/locations/verification scope yourself.
- Recommending a value from intuition or the reviewer's example without an evidence type; presenting an estimate as if measured.
- Calling a review "stale / already fixed" from the inline `commit_id` without comparing `original_commit_id` and timestamps with the fix commit (→ it is usually a Duplicate, not Refuted).
