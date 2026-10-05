#!/usr/bin/env python3
"""Find which lines of a PR diff can take an inline review comment.

Reads a unified diff (e.g. `gh pr diff <n>`) on stdin.

  list  <path>                                   print commentable hunks for <path>
  check <path> <line> [<start_line>] [--side S]  exit 0 if commentable, else 1
"""

from __future__ import annotations

import re
import sys

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def parse(diff: str) -> dict[str, list[dict[str, set[int]]]]:
    """Return {path: [hunk, ...]}, hunk = {"RIGHT": {lines}, "LEFT": {lines}}."""
    files: dict[str, list[dict[str, set[int]]]] = {}
    path: str | None = None
    hunk: dict[str, set[int]] | None = None
    old = new = 0
    for raw in diff.splitlines():
        if raw.startswith("diff --git "):
            path, hunk = None, None
            continue
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            path = None if target == "/dev/null" else re.sub(r"^b/", "", target)
            if path is not None:
                files.setdefault(path, [])
            continue
        if raw.startswith("--- "):
            continue
        m = HUNK_RE.match(raw)
        if m and path is not None:
            old, new = int(m.group(1)), int(m.group(3))
            hunk = {"RIGHT": set(), "LEFT": set()}
            files[path].append(hunk)
            continue
        if hunk is None:
            continue
        if raw.startswith("+"):
            hunk["RIGHT"].add(new)
            new += 1
        elif raw.startswith("-"):
            hunk["LEFT"].add(old)
            old += 1
        elif raw.startswith(" ") or raw == "":
            hunk["RIGHT"].add(new)
            hunk["LEFT"].add(old)
            new += 1
            old += 1
        # "\ No newline at end of file" and others: ignore
    return files


def ranges(lines: set[int]) -> str:
    if not lines:
        return "-"
    out, s = [], sorted(lines)
    start = prev = s[0]
    for n in s[1:]:
        if n != prev + 1:
            out.append(f"{start}-{prev}" if start != prev else f"{start}")
            start = n
        prev = n
    out.append(f"{start}-{prev}" if start != prev else f"{start}")
    return ",".join(out)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("list", "check"):
        sys.stdout.write(__doc__ or "")
        return 2
    side = "RIGHT"
    if "--side" in argv:
        i = argv.index("--side")
        side = argv[i + 1].upper()
        argv = argv[:i] + argv[i + 2 :]
    files = parse(sys.stdin.read())
    path = argv[1]
    hunks = files.get(path)
    if hunks is None:
        sys.stdout.write(f"NOT IN DIFF: {path}\n")
        return 1
    if argv[0] == "list":
        for n, h in enumerate(hunks, 1):
            sys.stdout.write(
                f"hunk {n}: RIGHT {ranges(h['RIGHT'])} | LEFT {ranges(h['LEFT'])}\n"
            )
        return 0
    line = int(argv[2])
    start = int(argv[3]) if len(argv) > 3 else line
    if start > line:
        sys.stdout.write("INVALID: start_line > line\n")
        return 1
    wanted = set(range(start, line + 1))
    for n, h in enumerate(hunks, 1):
        if wanted <= h[side]:
            sys.stdout.write(f"OK: {path} {side} {start}-{line} in hunk {n}\n")
            return 0
    sys.stdout.write(
        f"NOT COMMENTABLE: {path} {side} {start}-{line} "
        f"(hunks: {'; '.join(ranges(h[side]) for h in hunks)})\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
