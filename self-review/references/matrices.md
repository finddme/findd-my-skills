# P1 — Map: targets, paths, trust boundaries, invariants

## 1. Target split

Derived fresh for every change; the **method** is fixed.

1. **Find the dispatch point** where requests split by feature (router, registry, graph, handler table). Its entries are the feature list. Library → public API; CLI → commands.
2. **Common-layer target**: what every feature passes through (entry API/streaming, execution skeleton, safety/permission gate, user-confirmation framework, external clients, config/locale loaders). Review once.
3. **Per-feature targets**: feature body + helpers it uses + the execution path it takes + its tests/config/prompts. Group by **call chain from entry to result**, not by file or directory.
4. **Include callers and callees** of changed functions, and pre-existing code this change newly exercises.
5. **Size**: what one agent can read in one pass (a few hundred changed lines plus related code). Too big → split by sub-path.
6. **Cross-feature parity**: with many features, apply the path-parity axis across features (e.g. "every state-changing feature does gate → impact check → confirmation → execute").
7. **Order and depth by risk**:

| Criterion | first / deep | later / light |
|---|---|---|
| side effects | writes, permission changes, deletes | reads |
| reversibility | hard | easy |
| external effects | external API/DB writes | internal compute |
| complexity | many branches / confirmation steps, large | simple |

- Full review of a new project: invariants come from product/spec docs; if none exist, draft "candidate invariants" and confirm them with the user first.
- Multi-session is normal: the ledger carries progress; stop conditions are judged per target.

Template:

| Target | Kind (common / feature) | Entry | Files (incl. tests/config) | Risk order | Depth |
|---|---|---|---|---|---|

## 2. Path × invariant matrix

Rows = paths, columns = invariants. Every cell: ✓ (holds, with `file:line`), ✗ (finding id), n/a.

Paths to enumerate per entry: main path · retry/self-correction · multi-result/multi-interpretation · streaming vs non-streaming · pause/resume · each exception branch · fallback/degraded mode · batch vs single.

Invariants to test across paths (examples): same guards/validation · same user-facing message rules · same logging/observability · same metering/billing · same resource caps · same output contract · same cleanup.

| Path \ Invariant | guard A | disclosure B | metering | caps | … |
|---|---|---|---|---|---|
| main | ✓ `x.py:120` | ✓ | ✓ | ✓ | |
| alternate (e.g. multi-interpretation) | ✗ R-07 | ✓ | ✓ | n/a | |
| resume | … | | | | |

## 3. Trust-boundary table

| Input | Source | Trusted? | Where it flows (prompt, SQL, path/URL, template, log, output) | Validation / neutralization (`file:line`) |
|---|---|---|---|---|
| user text | client | no | | |
| LLM output (if any) | model | **no** | | |
| external API response | service | no | | |
| file content (cells, headers, names) | user upload | no | | |
| config | deploy | yes | | |

An LLM's copy of request data (ids, names it "restates") is untrusted: validate it against the original request.

## 4. Invariant list

| # | Invariant | Source (spec / PR body / docstring / decision) | Checked by |
|---|---|---|---|
