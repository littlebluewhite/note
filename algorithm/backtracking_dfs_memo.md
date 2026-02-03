---
title: "Backtracking + DFS Memoization (回溯 + DFS 記憶化)"
category: algorithm
tags: [algorithm]
created: 2026-02-03
updated: 2026-02-03
difficulty: n/a
source: algorithm
status: active
complexity_time: O(S * B)
complexity_space: O(S)
---
# Backtracking + DFS Memoization (回溯 + DFS 記憶化)

Goal: explore combinational choices with pruning, while caching repeated states to avoid recomputation.
目標：以回溯探索組合選擇並剪枝，同時用記憶化避免重複計算相同狀態。

## When to use / 何時使用

- Need to try all combinations or paths. / 需要枚舉所有組合或路徑。
- State repeats across different branches. / 不同分支會遇到相同狀態。
- Constraints are small but branching is high. / 規模小但分支數多。

## Core idea / 核心概念

- Backtracking builds partial solutions step by step, undoing choices when they fail.
  / 回溯逐步建立部分解，失敗時撤銷選擇。
- Memoization stores result per state so each state is solved once.
  / 記憶化對狀態存答案，讓每個狀態只計算一次。

## Standard workflow / 標準流程

1. Define state. / 定義狀態。
   - Example: current row string, current index, remaining items.
2. Define transitions. / 定義轉移。
   - From state, enumerate valid next choices.
3. Define base cases. / 定義終止條件。
4. Add memo cache. / 加入記憶化。
   - If state in memo, return cached result.
5. Backtrack with pruning. / 回溯並剪枝。
   - Stop early when a valid solution is found.

## Template (boolean search) / 範本（回傳能否成立）

```text
bool dfs(state):
    if state is terminal: return true/false
    if memo has state: return memo[state]
    for choice in choices(state):
        apply choice
        if dfs(next_state): 
            memo[state] = true
            undo choice
            return true
        undo choice
    memo[state] = false
    return false
```

## Complexity / 複雜度

- Time: `O(S * B)`
- Space: `O(S)`

Where:
`S`: number of distinct states cached in memo.
`B`: average branching factor per state.


- Without memo: exponential in depth / 無記憶化時通常指數級。
- With memo: `O(#states * branching_per_state)` / 有記憶化後接近狀態數規模。

## Common pitfalls / 常見陷阱

- State not unique enough → wrong cache hits.
  / 狀態定義不完整會導致錯誤快取。
- Forget to undo choices (backtrack) → corrupted state.
  / 忘記回溯會污染狀態。
- Using mutable state as key without cloning.
  / 用可變資料當 key 卻未複製，導致 memo 失效。

## Example idea / 範例概念

- Pyramid transition: state = current row string.
  / 金字塔轉移：狀態是目前一層字串。
- Choices: for each adjacent pair, choose any allowed top block.
  / 選擇是每一對相鄰底塊可對應的上層字母。
- Memoize whether a row can reach the top.
  / 記憶化某層是否能堆到頂端。

## Related problems / 相關題目

- [q756](../leetcode/q756.md)