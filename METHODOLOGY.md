# Bug-hunting methodology

Patterns that actually hit, each proven by a real find.

1. **Boundary off-by-one** - `>=` vs `>`, `<=` vs `<` at thresholds.
   Checklist: enumerate inputs around every threshold; compare against the spec.
2. **Last-batch-is-full** - batching by fixed size, then guessing "more to come"
   from `len(batch) == MAX`. When total % MAX == 0 the flush never runs.
3. **Return type vs declared type** - `xpath()` returns a list; assigning it to a
   `str` field silently stringifies (`['magnet:...']`).
4. **Assumed directory/file exists** - cleanup jobs iterating a dir that is only
   created on first use.
5. **sample/population mismatch** - `random.sample(items, n)` with n > len(items).
6. **Unvalidated path joins** - user input concatenated into paths = traversal.
   Fix pattern: reject separators + `resolve()` then `is_relative_to()`.
7. **Random range hitting protocol special values** - e.g. OneBot `duration=0`
   means *unban*; a `[0, 300]` range turns punishment into unban 1/301 of the time.
8. **Dropped string-method results** - `s.replace(...)` without assignment is a no-op.
9. **`lstrip` treated as prefix-strip** - it strips a character set; hostnames
   starting with those chars get eaten (`proxy.` -> `roxy.`).
10. **Hardcoded enum typo** - diff the hardcoded list against the data file's
    real values (`set(code) - set(data)`); a whole class of data goes unreachable.
11. **Guard asymmetry in one function** - one branch checks existence, its sibling
    forgets; zero-value defaults leak into comparisons.

Reading order: README/CONTRIBUTING first, recent commits second, core logic third;
diff copy-paste siblings line by line.
