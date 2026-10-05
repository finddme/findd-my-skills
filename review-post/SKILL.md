---
name: review-post
description: Use ONLY when the user explicitly invokes /review-post — to post review results to a GitHub PR. `comment` mode posts user-selected new findings as inline comments (one PR review, each comment on its own code line/range); `reply` mode posts the resolving commits as a reply to each handled review thread, read from vet-review item docs. Outward-facing; always previews and asks before posting. Does not auto-trigger.
---

# review-post

## Overview

Posts review results to a GitHub PR. **What to post is always the user's choice** — this skill never picks, recommends, or adds items on its own.

| Mode | Input | Posts |
|---|---|---|
| `comment` | a findings list file (`references/input-format.md` §1), usually a self-review ledger | selected findings as **one PR review** whose inline comments each sit on their own code line/range; items that cannot be inline fall back to a PR comment |
| `reply` | vet-review item docs (a folder or files) | for every handled review link, **one reply with the resolving commits** |

**Role boundaries**

| Skill | Does | Does not |
|---|---|---|
| self-review | find, verify, write ledger | post, fix |
| vet-review | judge received review, fix, commit; the user posts rationale replies as they go | post |
| **review-post** | post selected findings / commit replies, record URLs | judge, fix, commit, choose targets, post refuted/rationale replies |

Other skills that want to use this one **ask the user first**.

## Invocation

```
/review-post comment <findings file> [<id> ...] [--dry-run]
/review-post reply <docs folder | doc paths ...> [--dry-run]
```

- `comment` without ids → show the item list (id · tag · title · path:line) and let the user **pick by number**. No attribute-based auto-selection (e.g. `severity>=HIGH`).
- Missing or ambiguous mode/paths → **ask**. Never guess file locations.
- `--dry-run` → run R0–R4 fully (including line validation), post nothing.

## Procedure

```
R0 target → R1 load/select → R2 line mapping + pre-validation (comment) → R3 bodies → R4 preview + approval → R5 post → R6 record + report
```

**R0 — Target.**
- Resolve repo and PR: `gh pr view <n> --json number,state,isDraft,baseRefName,headRefOid,url`. Closed/draft → tell the user, ask whether to continue.
- Show the posting identity: `gh auth status`.
- Every commit hash that will be cited must exist on the remote (`git branch -r --contains <hash>`). Missing → stop and ask the user to push. Never push yourself.
- Hosting other than GitHub → not supported; say so and stop.

**R1 — Load / select.**
- `comment`: parse the findings file (`references/input-format.md` §1); take the given ids or the user's picks. Skip items with `status: refuted` or `confidence: refuted` unless the user names them explicitly. A self-review ledger file is a valid findings file.
- `reply`: parse the docs (`references/input-format.md` §2) and build the reply-target list per review link (rules below).

**R2 — Line mapping + pre-validation (`comment` only).**
- A single PR review is **atomic**: if one inline comment points outside the diff, GitHub rejects the whole review (422). So validate **every** comment before submitting:
  ```bash
  gh pr diff <n> | python3 ~/.claude/skills/review-post/scripts/commentable_lines.py check <path> <line> [<start_line>] [--side RIGHT|LEFT]
  ```
- If `base_sha` ≠ PR head, re-locate the code at head first (`references/line-mapping.md`). Code gone or already fixed → do not post; tell the user.
- Items that fail validation leave the review batch and become a **PR comment fallback** (code link + quoted lines). Mark them in the preview.

**R3 — Bodies.** Use `references/templates.md`. Mask secrets, credentials, account IDs, and customer data; warn if found. Reply language follows the thread's language.

**R4 — Preview + approval.** Show every post: target (file:line range / thread link), method (inline / PR comment / reply), full body. **Post nothing without the user's explicit approval.** Approval covers this run only.

**R5 — Post.**
- `comment`: one `POST /pulls/{n}/reviews` with `event: "COMMENT"`, `commit_id` = PR head, the short summary body, and all validated inline comments. Fallback items as separate PR comments.
- `reply`: one reply per target (`POST /pulls/{n}/comments/{id}/replies`), or a PR comment when the original review is an issue comment. Space posts ~1s apart.
- API details: `references/github-api.md`.

**R6 — Record + report.**
- `comment`: write `posted_url` (and post time, head SHA) into the item in the findings file.
- `reply`: append `게시: <url> (<time>)` (or `Posted:` in English docs) under the doc's reply section.
- Report a table: posted / fallback / skipped (with reason) / failed.

## Reply targets (`reply` mode)

| Doc / item state | Action | Body |
|---|---|---|
| done | reply | resolving commits |
| duplicate | reply | "commits from the earlier item" |
| refuted / deferred / n/a / no commits | **skip** | — (rationale replies are the user's) |
| in progress | skip, tell the user | — |
| original review is a PR issue comment (`issuecomment-…`) | PR comment that links the original | link + commits |
| original comment asks for a protocol line (e.g. `R1-03: fixed <sha>`) | reply in that protocol | protocol line |

- A batch doc (several links): reply per link, using the per-item status in its item table.
- Skip a thread that already has a reply with the same commit hash(es) or the same body.
- File-name status tag and header `Status` disagree → tell the user before posting.

## Safety rules

1. **Preview + explicit approval before any post.**
2. **No duplicates.** `comment`: skip items whose `review-post id=` marker already exists on the PR. `reply`: the dedup rule above.
3. **No PR state changes.** Review event is `COMMENT` only. No approve/request-changes, resolving threads, labels, or PR body edits.
4. **No push / PR creation.**
5. **Mask sensitive data** in every body.
6. Do not substitute other posting tools (e.g. the `code-review` plugin's `--comment`).
7. **Failures:** a 422 on the review batch after pre-validation → report which comment and stop. 403 / rate limit → stop and report. Partial success → record only what posted and list what remains.

## Common mistakes

- Submitting the review batch without validating every line against the diff (one bad line rejects all).
- Posting before showing the full preview and getting approval.
- Treating the inline comment's `commit_id` as the commit the comment was written against — GitHub updates it; record the posting-time head SHA and time separately.
- Posting refuted/rationale replies in `reply` mode.
- Citing a commit that is not on the remote (broken link).
