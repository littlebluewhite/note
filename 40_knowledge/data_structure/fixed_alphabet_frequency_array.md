---
title: Fixed Alphabet Frequency Array / 固定字母表頻率陣列
note_type: knowledge
domain: data_structure
tags: [knowledge, data_structure]
created: 2026-02-12
updated: 2026-02-12
status: active
source: knowledge
complexity_time: O(1) per update/query
complexity_space: O(A)
review_interval_days: 14
next_review: 2026-02-26
---
# Fixed Alphabet Frequency Array / 固定字母表頻率陣列

## Purpose / 目的

Track occurrence counts for symbols from a small fixed alphabet (e.g., 26 lowercase letters) with minimal overhead.
以最低成本追蹤固定小值域（例如 26 個小寫字母）的出現次數。

## Core Idea / 核心概念

- Map each symbol to an index in `[0, A-1]`.
  / 將字元映射到固定索引區間。
- Use a fixed-size integer array `freq[A]` to store counts.
  / 用固定長度整數陣列紀錄頻率。
- Update and query are both `O(1)`.
  / 查詢與更新皆為 `O(1)`。

## Operations / 操作

- Increment count:
  - `freq[idx] += 1`
- Decrement count (for sliding window):
  - `freq[idx] -= 1`
- Check first appearance:
  - `if freq[idx] == 1 { ... }`
- Check disappearance:
  - `if freq[idx] == 0 { ... }`
- Scan all frequencies when needed:
  - `for v in freq { ... }` (cost `O(A)`)

## When to Use / 使用時機

- Alphabet is known and compact.
  / 字元集合已知且範圍小。
- Performance-sensitive counting on strings/subarrays/substrings.
  / 需要高效計數的字串或子陣列問題。
- Hash map overhead is unnecessary.
  / 不希望承受雜湊常數開銷。

## Worked Example / 實作範例

Task: count letters in `"abca"` over lowercase alphabet.
任務：統計 `"abca"` 的字母頻率。

```text
freq[26] = 0
'a' -> idx 0 -> freq[0] = 1
'b' -> idx 1 -> freq[1] = 1
'c' -> idx 2 -> freq[2] = 1
'a' -> idx 0 -> freq[0] = 2
```

Result:

- `a:2, b:1, c:1`, others `0`.

## Variations / 變化型

- `u16/u32/usize` counters depending on max frequency.
  / 根據最大次數選擇計數型別。
- Versioned array (timestamp trick) to avoid full reset for repeated runs.
  / 用版本戳記避免重設整個陣列。
- Combined with extra stats (`distinct`, `max_freq`) for `O(1)` validity checks.
  / 搭配 `distinct`、`max_freq` 做常數時間判斷。

## Complexity / 複雜度
- Time: `O(1) per update/query`, `O(A)` for full scan
- Space: `O(A)`

## Pitfalls / 常見陷阱

- Wrong index conversion (`b'a'` offset mistakes).
  / 字元到索引轉換容易出錯。
- Counter type overflow when string can be large.
  / 計數型別太小可能溢位。
- Forgetting to reset between independent windows/runs.
  / 不同視窗或輪次之間忘記重設。
- Applying this to non-fixed or huge alphabets without compression.
  / 值域過大時應改映射或改用雜湊。

## Implementation Notes / 實作細節

- Rust common mapping:
  - `let idx = (byte - b'a') as usize;`
- For uppercase/lowercase mixed input, normalize first or use a larger mapping table.
  / 大小寫混合時要先正規化或擴大映射範圍。

## Related Problems / 相關題目

- [q3713](../leetcode/q3713.md)
