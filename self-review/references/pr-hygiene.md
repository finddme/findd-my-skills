# P7 — Pre-submit gate

## 1. Incremental re-run

- Scope = everything changed since the last run's head (fix commits included).
- Re-run P2–P5 on that delta; P4 attacks the defensive code the fixes added.
- For each `fixed` item, re-run its repro at HEAD: it must no longer reproduce.

## 2. PR hygiene checklist

| Check | How |
|---|---|
| PR body ↔ current code | every claim in the body (risk, rollback, test plan, "not reachable yet") still true? mentions of removed fields/paths? |
| deploy prerequisites | new config keys / secrets / env vars per environment — existence only (ask the user for the environment list and where config is injected; never read values). A missing key that makes the feature fail must be listed |
| unrelated changes | fixes outside the feature (split them or state them as behavior changes in the body) |
| needless diff | reformat-only / line-wrap-only changes that only add merge conflicts |
| base drift | how far the base is behind its upstream; files expected to conflict |
| prior review threads | every thread answered or resolved? (commit replies can be posted via review-post `reply` — ask first) |
| labels / templates | repo-required labels (e.g. AI-generated), PR template sections filled |
| throughput / limits | new concurrency caps, queues, timeouts stated in the risk section |

## 3. PR body draft sections

```markdown
### 검증 OK
- <invariant> — `file:line`

### 알려진 한계
- <pr_disclosure texts of deferred / wontfix items>

### 배포 선행조건
- <config key> — <environments> (존재 확인 필요)

### 레포 밖 계약 확인 요청
- <question> (확인한 곳: …)
```

Headings follow the repo's PR language. The user edits and posts the body; this skill never edits the PR.
