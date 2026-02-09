---
title: Divide and Conquer Build Balanced BST / 分治建構平衡 BST
note_type: knowledge
domain: algorithm
tags: [knowledge, algorithm]
created: 2026-02-09
updated: 2026-02-09
status: active
source: algorithm
complexity_time: O(n)
complexity_space: O(log n)
review_interval_days: 14
next_review: 2026-02-23
---
# Divide and Conquer Build Balanced BST / 分治建構平衡 BST

## Goal

Build a height-balanced BST from sorted values.
從排序好的值建立高度平衡的 BST。

## When to Use

- Input is sorted and you need fast future search (`O(log n)` average height).
- 輸入已排序，想建一棵後續查詢效率高的樹。
- Need to rebalance a BST after extracting sorted values by inorder.
- 已透過中序拿到排序值，下一步要平衡化重建 BST。
- Need a deterministic balanced BST baseline in interviews.
- 面試中需要穩定可解釋的平衡 BST 建構法。

## Core Idea

- Pick the middle value as root to split nodes as evenly as possible.
- 每次取中點當根，讓左右子樹節點數盡量接近。
- Recursively build left subtree from left half, and right subtree from right half.
- 左半段遞迴建左子樹，右半段遞迴建右子樹。
- Balanced split at each level yields height `O(log n)`.
- 每層都近似對半，整體高度為 `O(log n)`。

## Steps

1. Given sorted array `vals`, define `build(l, r)`.
2. 給排序陣列 `vals`，定義 `build(l, r)`。
3. If `l > r`, return `None`.
4. 若 `l > r`，回傳空節點。
5. Let `mid = l + (r - l) / 2`.
6. 令 `mid = l + (r - l) / 2`。
7. Create root with `vals[mid]`.
8. 以 `vals[mid]` 建立根節點。
9. `root.left = build(l, mid - 1)`, `root.right = build(mid + 1, r)`.
10. 分別遞迴建立左右子樹。
11. Return `root`.
12. 回傳 `root`。

## Complexity

- Time: `O(n)` (each value used once)
- Space: `O(log n)` recursion stack for balanced splits

## Pitfalls

- Wrong boundary updates can cause infinite recursion.
- 邊界更新寫錯會造成無限遞迴。
- Choosing always-left or always-right midpoint can still be valid, but keep consistent.
- 中點偏左/偏右都可行，但要一致。
- If source sequence is not sorted, result is not a valid BST.
- 若輸入序列未排序，建出的樹不保證 BST 性質。

## Examples

Sorted values: `[1, 2, 3, 4, 5, 6, 7]`
排序值：`[1, 2, 3, 4, 5, 6, 7]`

- Root: `4`
- 根：`4`
- Left from `[1,2,3]` gives root `2`
- 左半 `[1,2,3]` 會得到根 `2`
- Right from `[5,6,7]` gives root `6`
- 右半 `[5,6,7]` 會得到根 `6`

Final tree is height-balanced.
最終樹為高度平衡。

## Notes

- This is the direct template behind `q108`.
- 這個模板就是 `q108` 的核心解法。
- `q1382` often uses: inorder extraction + this reconstruction.
- `q1382` 常見作法是：先中序取值，再套用本模板。

## Related

- [q108](../leetcode/q108.md)
- [q109](../leetcode/q109.md)
- [q1382](../leetcode/q1382.md)
