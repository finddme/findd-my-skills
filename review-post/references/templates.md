# Body templates

## 1. Inline finding (`comment`)

```markdown
**[<tag>] <title>**

<explanation>

- 시나리오: <scenario>
- 제안: <proposal>

재현: `<command>` → 기대 `<expected>` / 실제 `<actual>`

<!-- review-post id=<id> base=<base_sha> -->
```

- Drop the scenario / proposal / repro lines when the item has none.
- Labels (`시나리오`, `제안`, `재현`) follow the PR's language (English PR: `Scenario`, `Proposal`, `Repro`).
- `suggestion` present → append a GitHub suggestion block:
  ````markdown
  ```suggestion
  <replacement lines>
  ```
  ````
- A static-only finding must not read as reproduced; omit the repro line rather than inventing one.
- The trailing HTML comment is invisible on GitHub and is the dedup marker.

## 2. Review summary body (`comment`)

```markdown
라인 코멘트 <N>건 남깁니다. <one line on what was excluded, e.g. 기존 리뷰·게이트 지적과 겹치는 항목은 제외했습니다.>
```

If some items fell back to PR comments, add one line: `인라인으로 달 수 없는 <K>건은 PR 코멘트로 남겼습니다.`

## 3. PR comment fallback (`comment`)

```markdown
**[<tag>] <title>** — `<path>` L<start>-L<end> (<head_sha short>)

https://github.com/<o>/<r>/blob/<head_sha>/<path>#L<start>-L<end>

```<lang>
<quoted lines>
```

<same explanation / scenario / proposal lines as §1>

<!-- review-post id=<id> base=<base_sha> -->
```

## 4. Replies (`reply`)

| Case | Body |
|---|---|
| done | ``처리 커밋: `<hash>` (tests) · `<hash>` (src)`` — extra groups/follow-ups as written in the doc |
| duplicate | ``이전 지적에서 반영된 커밋: `<hash>` (tests) · `<hash>` (src)`` |
| original is a PR issue comment | ``[<original review title>](<original link>) 처리 커밋: `<hash>` (tests) · `<hash>` (src)`` |
| protocol requested (e.g. lens review) | `<id>: fixed <src hash> (tests <tests hash>)` |

- Drop the author part of the doc's commit line (`(tests, Claude)` → `(tests)`).
- English thread → `Resolved in: …` / `Resolved earlier in: …`.
