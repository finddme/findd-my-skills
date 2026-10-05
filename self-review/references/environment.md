# P0 — Execution environment

Principle: **ask about permissions and side effects; explore facts yourself.**

## 1. Ask the user (minimum)

Check memory / CLAUDE.md first; ask only what is not already answered.

| Question | Why |
|---|---|
| Which environment may be used? (container name / host virtualenv allowed / none) | repos may forbid host installs |
| May servers be started, or running servers restarted? | they may belong to other work |
| Are real external dependencies allowed (DB, cloud, LLM, internal APIs)? Read-only constraints? Call/rate limits? | cost, rate limits, production data |
| Are there e2e inputs (test files, tenant/user ids)? | inputs for local repro |
| Budget cap (number of agents, time)? | no default — the user sets it |
| Where are decision/spec records? Where should the ledger be written (and is it committed)? | never guess locations |

## 2. Explore (read-only)

| Item | How |
|---|---|
| test runner and command, installed dependency versions | inside the environment (`pip list`, `package.json`, lock files, `go env` …) |
| entrypoints and how to start the service | Dockerfile, compose, Makefile, scripts, README |
| running processes, ports, start time | process/port listing; is the start time later than the latest code change? |
| config needed to start locally | existence and **key names only** of env vars / config files — never values |
| baseline failures | run the tests **twice**; failures present in both = baseline, results that change = flaky |

- A **trial start** (boot the server, hit health) only with permission from §1 — it may bind ports, run migrations/seeds, or call externals.

## 3. Capability profile → verification level

| Level | What | Needs |
|---|---|---|
| V0 | static (read code, trace the call chain) | nothing |
| V1 | run existing tests, write a failing test | environment + test runner |
| V2 | in-process repro script calling the real function/node entry | V1 + dependencies |
| V3 | start the local API and reproduce per request | server start allowed + config |
| V4 | real external dependencies | user permission + credentials |

- P3 verifies at the highest level the profile allows and records it (`reproduced@V2`).
- A HIGH+ finding stuck at V0 is not confirmed → `question`, with what was missing.
- No environment at all → V0 only; put **"no execution verification"** at the top of the report.
- Offer to save the confirmed profile per repository in memory so later runs ask less.
