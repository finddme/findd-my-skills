---
name: self-review
description: Use ONLY when the user explicitly invokes /self-review — a thorough, review-only pass over a branch/PR (or a whole codebase) before submitting: split the change into targets × review axes, verify every finding by execution in a separate session, attack defensive code with variants, and close every finding in a ledger. Does not modify code; at the end asks whether to hand fixes to vet-review or post via review-post. For a lighter static pass use /self-review-light. Does not auto-trigger.
---

# self-review

## Overview

A review-only skill. It **finds, verifies, and records** — it never edits code or commits.

Why this shape (lessons from a real PR that passed a static self-review and still drew ~80 external findings, ~88% valid):
- findings were judged by reading only, not by running → verify by execution;
- alternate paths (retry, resume, multi-interpretation, exception branches) silently lacked what the main path had → path-parity matrix;
- found-but-minor items were neither fixed nor disclosed and came back as HIGH → every finding closes in a ledger;
- a confidence-score filter dropped a real HIGH → confidence and impact are separate;
- tests, config and the PR body were out of scope → scope is everything the user ships;
- one snapshot run, then 40 more commits → incremental re-run before submitting.

## Core principles

1. **Discovery ≠ confirmation.** Discovery agents emit hypotheses; a separate verification agent confirms by **execution** (repro script or failing test through a real entry point).
2. **Confidence and impact are separate.** Confidence = `reproduced@Vn / static-confirmed / refuted / question`; impact = severity table. High impact + low confidence → verify, never drop.
3. **Every finding closes in the ledger** — review-only: each has a verification result and severity; after hand-off: `fixed <hash> / deferred (PR disclosure text) / wontfix (reason) / question (to whom)`.
4. **Matrices are deliverables, not questions** — path × invariant and trust boundaries must be filled before moving on.
5. **Attack defensive code** (guards, filters, masking, exception handling, parsers) with generated variants. After fixes, the incremental re-run attacks the fixes too.
6. **Read decision records first.** A documented product decision is a question, not a defect. A proposal that overturns a decision is labelled "overturn needed".
7. **Scope = everything shipped**: source, tests, config, prompts, PR body, deploy prerequisites — plus pre-existing code this change newly exercises.

## Phases

```
P0 baseline → P1 map → P2 discover → P3 verify → P4 attack → P5 classify + report ──(default: stop here)
                                                                  │ only if the user wants
                                                                  ▼
                                   P6 hand-off (fixes → vet-review, posting → review-post)
after fixes → P7 pre-submit gate (incremental re-run + PR hygiene)
```

| Phase | Do | Output | Reference |
|---|---|---|---|
| **P0 baseline** | Fix base/head SHA. Pick scope mode: **diff review** (PR/branch vs base) or **full review** (no base). Diff inventory (src/tests/config/prompt/infra, files · lines). Collect PR body, open review threads, prior ledger. **Ask** where decision/spec records live and where to write the ledger. Secure the execution environment. Ask the budget cap (agents, time) — no default. Run the test baseline **twice**; results that change are flaky | `baseline` section of the ledger (SHAs, mode, inventory, capability profile V0–V4, baseline failures, flaky list, decision list, budget) | `environment.md` |
| **P1 map** | Split into **targets** (dispatch point → common layer + per-feature units, ordered by risk). Path inventory (entry × alternate paths). Trust-boundary table. Invariant list (spec, PR body, docstrings). Pick extra axes by project type | `map` section (target table, path × invariant matrix with blanks, trust table, invariants, chosen axes) | `matrices.md` |
| **P2 discover** | Per target × axis group, one discovery agent. Inject "already known" (open threads, prior ledger, decisions) so they report net-new only. Output = hypothesis + how to verify. Fill matrix cells | ledger items with `status: open` | `axes.md` |
| **P3 verify** | **Separate agent per candidate** (batch trivial ones). Input: the candidate text + file locations only — never the discovery reasoning. Run at the highest level the profile allows. Record command / expected / actual. Also record invariants confirmed safe (**verified OK**) | confidence per item, refuted items kept with reason, verified-OK list | `verification.md` |
| **P4 attack** | For every defensive construct in scope, generate variants and run them. If a defense enumerates inputs, check whether an output-side invariant (size, shape, type) would close it | variant table (variant → result) | `adversarial-variants.md` |
| **P5 classify + report** | Severity per table. Decision-record conflicts → question. External-contract questions go to their own list. Report (format below). Then **ask**: hand fixes to vet-review? post selected items via review-post? | final ledger + report | `ledger.md` |
| **P6 hand-off** *(only if the user wants)* | vet-review reads the ledger as the received review and updates `status`. review-post `comment` mode reads the same ledger file | hand-off summary | — |
| **P7 pre-submit gate** *(after fixes)* | Re-run P2–P5 on the **HEAD delta** since the last run (fix commits included). For `fixed` items, confirm the repro no longer reproduces at HEAD. PR hygiene check. Draft PR body sections: verified OK / known limitations / deploy prerequisites / external-contract questions | updated ledger, PR body draft | `pr-hygiene.md` |

**Stop conditions** (conditions, not round counts): every target × axis cell reviewed ("n/a" allowed, blanks not); no blank matrix cell; every item has verification + severity (and, after hand-off, no `open`); the P7 delta run finds no new HIGH+. Budget cap hit → stop and report covered / uncovered cells.

## Review axes

Ten common axes apply to every target (see `axes.md` for the questions): correctness vs spec · path parity · trust boundary · defense robustness · resilience & resources · runtime contracts · observability & metering · test detection power · doc/contract consistency · repo rules & hygiene. Extra axes by project type (FE, data pipeline, LLM feature, public API) are chosen in P1.

## Severity

| Severity | Criterion |
|---|---|
| CRITICAL | core-function failure (whole request/batch/command), data corruption, or security-boundary break — **reproduced** in normal use |
| HIGH | a user-visible wrong result / wrong refusal / missing information on a **reachable** path |
| MEDIUM | missing defense in depth (surfaces if an upstream contract breaks), missing observability/metering, missing resource caps |
| LOW | docs, comments, rules, readability |

- "Not reachable today" is a reason to defer and disclose, not to downgrade. If unreachability rests on an external contract, keep MEDIUM+ and disclose the contract.
- Confidence is a separate column, never a filter.

## Report format (P5)

Headings in the user's language. Conclusion first, tables over prose.

1. **Coverage** — target × axis grid (reviewed / n/a / not covered) and verification levels reached.
2. **Counts** by severity × confidence.
3. **HIGH+ items** — id · title · path:line · confidence · one-line impact.
4. **Questions** — decision conflicts and external-contract questions (with "where checked" and "ask whom").
5. **Deferred** — with the PR disclosure text.
6. LOW items grouped by file/kind.
7. One-line question: hand fixes to vet-review? post via review-post?

## Agents and cost

- Discovery: one agent per target × axis group; small scopes may group targets. Verification: one agent per candidate (group trivial ones).
- Follow the user's model-assignment policy if recorded (memory); otherwise default.
- Verification agents get the candidate and locations only — no discovery reasoning.
- Light mode (user asks for it): P0 + P2 on four axes (path parity, trust boundary, defense robustness, test detection power) + P3 for HIGH only + P5.

## Rules

- **Review only.** No code edits, no commits, no pushes, no PR posts. Hand-off and posting happen only after the user says so, through vet-review / review-post.
- Other skills: ask before using vet-review or review-post. Required internal steps need no question.
- Never read or print secret values; mask credentials, account IDs, and customer data in every output.
- Do not use the `code-review` plugin (it posts to the PR).
- When comparing with external reviews, judge by the comment's `original_commit_id` and timestamp, not the updated `commit_id`.

## Common mistakes

- Confirming a finding by reading only, or reproducing it by constructing internals instead of going through a real entry point.
- Dropping a high-impact finding because confidence was low.
- Leaving "minor" findings without a close state or a disclosure text.
- Reviewing only `src/` — skipping tests, config, prompts, PR body.
- Letting discovery reasoning leak into verification agents.
- Stopping after N rounds instead of on the stop conditions.
- Editing code or committing from this skill.
