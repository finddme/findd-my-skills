# P2 — Review axes

Apply all ten common axes to every target ("n/a" allowed, no blanks). Each discovery agent gets: target files, the matrices from P1, the "already known" list, and the axis questions below. Output per finding: hypothesis, evidence (`file:line` chain), how to verify.

## 1. correctness vs spec
- Does each decision rule in the spec / decision records map 1:1 to the code's decision?
- Boundaries: empty, NULL, zero rows, duplicates, ordering, single vs many, first/last element.
- Does the result keep its meaning (e.g. "no data" vs "data with empty cells", requested field removed from output)?
- Indexing/slicing that changes results where the full data may be needed (logging excluded).

## 2. path parity
- Fill the path × invariant matrix: does every alternate path have the main path's guards, disclosures, observability, metering, caps?
- Do sibling branches (exception handlers, fallbacks) do the same post-processing?
- Registries / parallel lists / reset lists / `else` defaults: is every member consistent? Is the rule pinned by an invariant test?
- Similar-role functions: do they handle the same cases the same way?

## 3. trust boundary
- Untrusted inputs (user text, file content, external responses, LLM output if any) validated by schema / whitelist / membership before use?
- Inserted into prompts, templates, SQL, paths, URLs, logs: neutralized or parameterized?
- Values an LLM restates from the request validated against the original request?
- Authorization: does every state-changing operation (incl. resume/cancel/retry) check ownership? Any other user's data or PII in responses/logs?
- Secrets: hard-coded keys/credentials, secrets in logs/errors, environment values hard-coded instead of configured.
- Path traversal, upload validation, recursion/size limits against malicious input (OOM).

## 4. defense robustness
- Enumerated defenses (denylists, name lists, patterns, regexes): do variants bypass them? (→ P4)
- Parse failures fail closed? Parser/tokenizer error classes all caught (siblings and parents, not one class)?
- Substring matching on identifiers/states without boundaries?
- Could an output-side invariant (size, shape, type) replace or back up an input-side enumeration?

## 5. resilience & resources
- Every external call: timeout, size cap, retry cap with backoff; retries only for retryable errors?
- Threads, pools, connections, file handles, streams: bounded, released on every path, cleanup wired to shutdown?
- Timeouts that cover real work (no duplicate processing / double billing); work that keeps running after the caller times out?
- Partial failure: are partial successes kept or discarded deliberately?
- Blocking I/O inside async code; concurrency (races, locks, transaction boundaries); process-local state across workers/restarts.
- DB: parameter binding, N+1, indexes, transaction scope, deterministic single-row selection.

## 6. runtime contracts
- State that the framework persists or ships (checkpoints, caches, queues, pickles, JSON payloads): serializable? No live objects (clients, managers, connections)?
- Context propagation across threads/tasks (request ids, contextvars).
- Library defaults and version-specific behavior verified against the **installed** version's source and official docs — not memory.
- Macro/extension/plugin constraints (e.g. a function that is a macro and rejects certain clauses).

## 7. observability & metering
- Failures, fallbacks, waits (queue time), skipped work: identifiable afterwards at the right level? Over-logging?
- If there is usage metering/billing (LLM tokens, paid APIs): counted exactly once on every path, including exception and timeout paths?
- Audit records contain the reason for refusals/errors (masked)?

## 8. test detection power
- For each changed behavior: **"if this code breaks, does a test fail?"** Check with representative mutations (flip a branch, drop a guard, swallow an exception, remove a reset line).
- Only negative asserts? Asserts that cannot tell two branches apart? Mocks that swallow exceptions so the test passes anyway? Fixtures that accidentally trigger another rule?
- Combinations and precedence of rules/flags covered, not just each alone?
- Test resources cleaned up (servers, sockets, threads)?

## 9. doc/contract consistency
- Comments, docstrings, PR body, sample config, prompt text vs current behavior.
- Unreachable branches still described as reachable; contracts ("4 fields") no longer true.
- Library claims in comments (defaults, response shapes) unverified?

## 10. repo rules & hygiene
- Repo rules (CLAUDE.md, rules dir, lint/pre-commit config): message language, forbidden patterns, immutability, logging style.
- Magic numbers, repeated literals → constants/enums; single source of truth for mappings.
- Unused params, duplicate code, needless complexity, file responsibilities and placement, unclear names.
- AI residue: dead code after refactors, deprecated idioms; comments narrating process, dates, review numbering.

## Extra axes (chosen in P1)

| Project type | Extra axes |
|---|---|
| FE / UI | accessibility, state management, large renders, XSS, listener cleanup |
| data pipeline / batch | idempotency, reprocessing, schema evolution, partial-failure recovery |
| LLM feature | prompt contract & versioning, nondeterminism (repeated measurement), token budget |
| public API | backward compatibility, versioning, rate limits, status-code mapping, pagination, idempotency |
| i18n | default language policy in one place, full-width/half-width and Unicode normalization |
