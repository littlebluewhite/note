# Unlocking permutations with a root of minimal complexity

## Idea
- Only computer `0` is initially unlocked; any other computer `i` needs an already-unlocked `j < i` with `complexity[j] < complexity[i]`.
- If there exists any `i > 0` with `complexity[i] <= complexity[0]`, `i` can never be unlocked (no smaller-index, lower-complexity helper), so the answer is `0`.
- When `complexity[0]` is the unique minimum, computer `0` alone satisfies the requirement for every other computer (`0 < i` and `complexity[0] < complexity[i]`), so after unlocking `0`, all remaining computers can appear in any order.

## Resulting formula
- If some `complexity[i] <= complexity[0]` for `i > 0`: answer `0`.
- Otherwise: answer `(n-1)! mod 1e9+7` (permutations of the remaining `n-1` computers with `0` fixed first).

## Complexity
- Time: `O(n)` to verify the minimum and compute factorial.
- Space: `O(1)` extra.
