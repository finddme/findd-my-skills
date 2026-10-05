# GitHub API notes

Verified shape at authoring time; re-check the official REST docs if a call fails unexpectedly.

| Action | Call |
|---|---|
| PR info | `gh pr view <n> --json number,state,isDraft,baseRefName,headRefOid,url` |
| Diff | `gh pr diff <n>` |
| Inline review (batch) | `gh api -X POST repos/{o}/{r}/pulls/{n}/reviews --input <payload.json>` with `{"commit_id": "<head>", "event": "COMMENT", "body": "<summary>", "comments": [{"path": "...", "line": 142, "side": "RIGHT", "start_line": 138, "start_side": "RIGHT", "body": "..."}]}` (omit `start_*` for single lines) |
| Thread reply | `gh api -X POST repos/{o}/{r}/pulls/{n}/comments/{comment_id}/replies -f body=<text>` |
| PR comment | `gh api -X POST repos/{o}/{r}/issues/{n}/comments -f body=<text>` |
| Existing inline comments | `gh api repos/{o}/{r}/pulls/{n}/comments --paginate` (`in_reply_to_id`, `body`, `user.login`) |
| Existing PR comments | `gh api repos/{o}/{r}/issues/{n}/comments --paginate` |

- With `--paginate`, `--jq` runs **per page** — do not aggregate (e.g. `length`) inside jq. Emit one line per match (`--jq '.[] | select(.body | contains("review-post id=X")) | .id'`) and count the lines.
- Build the review payload as a JSON file (bodies contain newlines and backticks); do not inline it in `-f`.
- `commit_id` on returned inline comments is later updated by GitHub; record the posting-time head SHA and timestamp yourself.
- A `GET` is the default for `gh api`; posting always needs `-X POST`. Never run a POST before R4 approval.

## Errors

| Status | Meaning | Action |
|---|---|---|
| 422 on review | a comment's line/range not resolvable in the diff, or a pending review conflict | report the offending comment; do not retry blindly |
| 404 on reply | comment id wrong or deleted | skip that target, report |
| 403 | no permission / blocked | stop, report |
| 403/429 with rate-limit headers | secondary rate limit | stop, report; resume later with the remaining list |
