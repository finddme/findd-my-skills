# P4 — Attack defensive code

For every defensive construct in scope (and, in P7, in the fixes): list variants by the families below, run them through the real entry point, and record variant → result. A bypass is a finding (axis 4) with the variant as the repro.

## Variant families

| Family | Examples |
|---|---|
| case / encoding / normalization | `HTTPS://`, mixed case, percent-encoding, full-width characters, Unicode look-alikes, NFC/NFD |
| synonym constructs | a different function with the same effect, aliases, operators instead of functions, set operations (UNION/INTERSECT/EXCEPT), subqueries, CTEs, recursion |
| wrapping | casts (`::VARCHAR`), stringify/serialize functions, nesting, concatenation, formatting helpers |
| splitting | spreading one payload across several fields/columns/requests so each part passes a per-part limit |
| exception siblings | tokenizer vs parser errors, subclass vs parent, errors raised by a different layer |
| boundaries | empty, NULL, zero rows, one row, huge, negative, maximum length, exactly at a cap and cap+1 |
| delimiters / comments | injected quotes, comment markers, template placeholders (`{key}`), tag delimiters |
| URL components | scheme case, userinfo (`user:pass@`), ports, dot-segments, double slashes, host suffix tricks |
| type confusion | string vs int ids, list vs object JSON bodies, missing vs null fields |
| state / timing | retry after partial success, resume after pause, concurrent duplicate requests |

## Output-side check

If a defense works by enumerating **inputs** (names, patterns), ask whether an **output** invariant closes the whole class (e.g. cap result size/shape/type at the point of emission). Enumerations stay useful as early exits; the output invariant is the backstop.

## Record

| Construct (`file:line`) | Variant | Expected | Actual | Finding |
|---|---|---|---|---|
