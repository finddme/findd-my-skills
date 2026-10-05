# Ledger

One markdown file per review run (location asked in P0; not committed unless the user says so). It is also a valid input for `/review-post comment` and for `/vet-review`.

## File layout

```markdown
# Review ledger — <repo> <branch or PR> (<date>)

## baseline
- mode: diff | full
- base: <sha>  head: <sha>
- inventory: src <files/lines>, tests …, config …, prompts …
- capability: V2 (container <name>; server restart not allowed)
- baseline failures: …   flaky: …
- decisions read: <paths>
- budget: <agents>, <time>

## map
<target table, path × invariant matrix, trust table, invariants, chosen axes>

## verified-ok
- <invariant> — `file:line` (V1)

## questions
| # | question | where checked | ask whom |

## items
### R-01
…
```

## Item block

Same core fields as review-post's findings format, plus tracking fields.

```markdown
### R-01
- path: src/pkg/module.py
- line: 142
- start_line: 138
- side: RIGHT
- base_sha: 7729ffc3
- tag: 경로대칭
- title: 재개 경로에는 빈 계획 오류 처리가 없습니다
- severity: HIGH
- axis: path parity
- target: resume
- confidence: reproduced@V2
- fingerprint: <short hash of path + cause>
- decision_ref:            (conflicting decision record, if any)
- status: open
- pr_disclosure:           (for deferred / wontfix)
- posted_url:              (filled by review-post)

#### explanation
…

#### scenario
…

#### proposal
…

#### repro
`<command>` → expected `<…>` / actual `<…>`
```

## Status transitions

| From | To | By |
|---|---|---|
| open | verified result + severity (review-only done) | self-review P3/P5 |
| open | `question` | P3 (intent / contract / environment) |
| any | `fixed <hash>` | vet-review, after the fix is committed |
| any | `deferred` + `pr_disclosure` | user decision; disclosure text goes to the PR body |
| any | `wontfix` + reason | user decision |
| `fixed` | re-checked at HEAD in P7 | self-review P7 |

## Rules

- Never delete an item; refuted items stay with the reason.
- LOW items stay separate in the ledger but are **grouped** by file/kind in the report and when posting.
- Match external reviews by `fingerprint` and location; judge "already fixed" by the review's `original_commit_id` and timestamp.

## PR disclosure text (example)

```text
알려진 한계: <무엇이 어떤 조건에서 일어나는지>. 이번 PR에서는 <이유>로 수정하지 않으며, <재개 조건>이면 다시 검토한다.
```
