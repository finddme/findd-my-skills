# Line mapping and pre-validation (`comment`)

## Rules

- GitHub inline comments can only target lines **inside the PR diff** (added, deleted, or context lines of a hunk).
- `side: RIGHT` → line number in the new file (added/context lines). `side: LEFT` → line number in the old file (deleted/context lines).
- A range (`start_line`–`line`) must lie **within one hunk** and on the same side.
- One PR review is atomic: one invalid comment → the whole review is rejected (422). Validate every comment first.

## Checker

`scripts/commentable_lines.py` reads a unified diff on stdin.

```bash
# list commentable ranges for a file
gh pr diff <n> | python3 ~/.claude/skills/review-post/scripts/commentable_lines.py list <path>

# check one comment (exit 0 = ok, 1 = not commentable, message on stdout)
gh pr diff <n> | python3 ~/.claude/skills/review-post/scripts/commentable_lines.py check <path> <line> [<start_line>] [--side RIGHT|LEFT]
```

Fetch the diff once per run and reuse it for all items (`gh pr diff <n> > <scratch>/pr.diff`).

## When `base_sha` ≠ PR head

1. `git diff <base_sha> <head> -- <path>` — did the anchor lines move or change?
2. Moved only → find the same code at head (search the anchored text), update `line`/`start_line`.
3. Renamed file → `git log --follow --name-status <base_sha>..<head> -- <path>`.
4. Code removed or changed so the finding no longer applies → **do not post**; tell the user.

## Not in the diff

Fall back to a PR comment (`templates.md` §3) with a blob link at the PR head and the quoted lines. Mark it in the preview as "inline not possible → PR comment".
