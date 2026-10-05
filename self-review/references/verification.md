# P3 — Verification

## Rules

1. **Separate agent**, fresh context: the candidate (id, hypothesis, locations) only. No discovery reasoning, no session history.
2. **Through a real entry point** (the public function, graph node, API route) — not by constructing internal objects directly. Direct construction is supporting evidence at most.
3. **Installed versions** of libraries; note versions in the record.
4. **Record** command · expected · actual, and the level reached (V0–V4, `environment.md`).
5. **Environment failure ≠ defect.** Missing registries, credentials, network → mark `question` with what was missing; compare against the baseline failure list.
6. **Refuted is a result.** Keep refuted items with the reason — it prevents the same false positive next time.
7. If the premise is a runtime behavior ("the renderer prints raw"), **measure before confirming**.
8. **Verified OK:** when a check shows an invariant holds (e.g. "all three entry points use the same builder"), record it with `file:line` — it goes to the report and the PR body draft.

## Outcomes

| Outcome | Meaning |
|---|---|
| `reproduced@Vn` | failing test or repro showed the defect at level n |
| `static-confirmed` | code chain proves it; execution not possible or not needed (LOW/doc items) |
| `refuted` | does not hold; reason recorded |
| `question` | depends on intent, an external contract, or an unavailable environment |

## Test-detection mutations (axis 8)

Pick one representative mutation per changed behavior; apply it in a scratch copy or with a temporary patch, run the relevant tests, revert.

| Mutation | Catches |
|---|---|
| flip a condition / remove an `elif` | branch not asserted |
| delete a guard or validation call | guard untested |
| make an exception handler `pass` | tests that pass because errors are swallowed |
| remove a reset/cleanup line | state leaking across calls |
| return a constant | asserts that only check "something returned" |

If a mutation survives (tests still pass), that is a finding on axis 8 with the mutation as the repro.
