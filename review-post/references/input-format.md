# Input formats

## 1. Findings list (`comment` mode)

A markdown file. One block per finding: a `### <id>` heading, field lines, then body sections. Other text in the file is ignored. A self-review ledger uses this same block format (with extra tracking fields such as `severity`, `axis`, `confidence`, `fingerprint`), so it can be passed directly; extra fields are ignored.

```markdown
### R-03
- path: src/app/orders/sync_job.py
- line: 142
- start_line: 138            (optional — multi-line range)
- side: RIGHT                (optional — RIGHT = new code (default), LEFT = deleted line)
- base_sha: 1a2b3c4d
- tag: 관측
- title: 중단된 주기에도 processed가 배치 전체 건수로 찍힙니다
- status: open               (optional — refuted items are skipped unless named)
- posted_url:                (filled by review-post)

#### explanation
오류로 루프를 중단한 경우에도 `processed=len(batch)`는 조회한 배치 크기 그대로입니다.

#### scenario
20건 배치에서 3번째 항목에서 중단 → `ok=2 processed=20`.

#### proposal
실제로 처리한 건수를 `processed`로 쓰거나, 중단 여부(`stopped=True`)를 같이 남기기.

#### repro                   (optional)
`pytest tests/... -k processed` → expected `processed=3` / actual `processed=20`

#### suggestion              (optional — exact replacement for the selected lines)
```python
processed=handled,
```
```

| Field | Required | Notes |
|---|---|---|
| `### <id>` | yes | unique in the file |
| `path`, `line`, `base_sha`, `tag`, `title` | yes | `line` is the anchor (last line of a range) |
| `start_line`, `side`, `status`, `posted_url` | no | |
| `#### explanation` | yes | what is wrong, with the code evidence |
| `#### scenario`, `#### proposal`, `#### repro`, `#### suggestion` | no | omitted sections are left out of the body |

## 2. vet-review item docs (`reply` mode)

review-post reads the header lines (Korean or English labels):

| Line | Example | Used for |
|---|---|---|
| `리뷰:` / `Review:` | `- 리뷰: PR #123 discussion [r1000000001](https://github.com/<owner>/<repo>/pull/123#discussion_r1000000001) (...)` | target thread. `#discussion_r<id>` = inline thread (reply), `#issuecomment-<id>` = PR issue comment (link it in a new PR comment) |
| `상태:` / `Status:` | `- 상태: 완료 (2026-09-28)` | reply or skip |
| `커밋:` / `Commits:` | ``- 커밋: `aaaa1111` (tests, Claude) · `bbbb2222` (src, 사용자)`` | reply body |

- `리뷰:` may be followed by an **indented sub-list** of links (one doc handling several reviews of the same issue). Every link in the sub-list shares the doc's `상태:` and `커밋:`:
  ```markdown
  - 리뷰:
    - 7-1. PR #123 issue comment [`2000000001`](…#issuecomment-2000000001) (…)
    - 7-2. PR #123 discussion [`r1000000007`](…#discussion_r1000000007) (…)
  ```
- Status words: `완료`/done, `중복`/duplicate → reply; `기각`/refuted, `보류`/deferred, `해당없음`/n-a, `진행중`/in progress → skip.
- The file-name tag (`NN-(완료)-…`) must agree with `상태:`; if not, tell the user.
- **Batch docs** (one doc, several review links): an item table with a link column and a per-item status column, e.g.
  ```markdown
  | 항목 | 내용 | 판정 | 상태 |
  | 5-1 | [r1000000005](…#discussion_r1000000005) … | … | 완료 |
  ```
  Reply per link whose row status is done/duplicate, using the doc's `커밋:` line.
- Commits written as prose groups (e.g. `9-1 \`cccc3333\` (tests) · \`dddd4444\` (src) / 9-2 …`) are kept as written in the reply, labels included.
