---
title: Array / 陣列
note_type: knowledge
domain: data_structure
tags: [data_structure, knowledge]
created: 2026-02-03
updated: 2026-02-15
status: active
source: data_structure
complexity_time: O(1) access
complexity_space: O(n)
review_interval_days: 14
next_review: 2026-03-01
---
# Array / 陣列

## Purpose / 目的

Store ordered elements in contiguous memory to support fast random access and cache-friendly linear scans.
以連續記憶體儲存有序元素，提供快速隨機存取與快取友善的線性掃描。

## Core Idea / 核心概念

- Index `i` maps directly to memory offset, so `read/write` is `O(1)`.
  / 索引可直接對應位址偏移，因此讀寫為 `O(1)`。
- Elements are contiguous, making sequential traversal efficient in practice.
  / 元素連續存放，順序遍歷通常有更好的實務效能。
- Dynamic arrays (e.g., Rust `Vec<T>`) grow capacity geometrically to keep append amortized `O(1)`.
  / 動態陣列（如 Rust `Vec<T>`）通常採倍增擴容，使尾端追加維持攤銷 `O(1)`。

## Operations / 操作

- Read by index: `O(1)` / 依索引讀取：`O(1)`
- Write by index: `O(1)` / 依索引寫入：`O(1)`
- Append at end (`Vec`): amortized `O(1)` / 尾端追加（`Vec`）：攤銷 `O(1)`
- Pop at end: `O(1)` / 尾端彈出：`O(1)`
- Insert/delete in middle: `O(n)` / 中間插入或刪除：`O(n)`（需要搬移）
- Full scan: `O(n)` / 完整掃描：`O(n)`

## When to Use / 使用時機

- Need frequent indexed access and bounded-memory representation.
  / 需要頻繁索引存取，且希望記憶體布局簡單可預測。
- Data is naturally processed left-to-right or right-to-left.
  / 資料天然適合線性掃描（由左到右或反向）。
- Need a mutable output buffer for string/number construction.
  / 需要可變緩衝區來組裝字串或數字結果（例如逐位運算）。

## Worked Example / 實作範例

Problem pattern: binary string addition (`q67`).
題型：二進位字串加總（`q67`）。

Use `Vec<u8>` as an output buffer:
以 `Vec<u8>` 作為輸出緩衝：

1. Read input bytes by index from right to left.
   / 用索引從尾端讀取輸入位元。
2. Push each computed result bit to `Vec`.
   / 將每次算出的位元 push 進 `Vec`。
3. Reverse once and convert to `String`.
   / 最後反轉一次並轉成字串。

Why array helps:
陣列/向量的關鍵價值：

- Constant-time indexed read simplifies two-pointer digit simulation.
  / `O(1)` 索引讓雙指標逐位模擬更直接。
- Push + reverse pattern avoids costly front insertion.
  / 使用 push 再 reverse，可避免前端插入的高成本。

## Variations / 變化型

- Fixed-size array: length known and constant; no reallocation.
  / 固定長度陣列：長度固定，不需擴容。
- Dynamic array (`Vec<T>`): supports growth and builder patterns.
  / 動態陣列（`Vec<T>`）：可擴容，適合建構輸出。
- Slices / views: borrowed subranges without copy.
  / 切片 / 視圖：可借用子區間而不複製。

## Complexity / 複雜度

- Time: `O(1) access`
- Space: `O(n)`

Where:
`n`: number of elements.

## Pitfalls / 常見陷阱

- Repeated front insertions cause repeated shifts (`O(n)` each).
  / 反覆前端插入會持續搬移元素，效能差。
- Out-of-bounds indexing in pointer loops.
  / 指標迴圈容易出現索引越界。
- Confusing capacity with length in dynamic arrays.
  / 混淆 `capacity` 與 `length` 會造成錯誤假設。

## Implementation Notes / 實作細節

- Pre-allocate with `Vec::with_capacity(...)` when result size is predictable.
  / 若可預估輸出長度，先配置容量可減少重配。
- Prefer byte arrays (`as_bytes`) for numeric string processing in Rust.
  / 在 Rust 進行數字字串運算時，優先使用位元組陣列處理。
- Reserve front insertion for deque/list structures, not plain arrays.
  / 若需要高頻前端操作，應改用 deque/linked list，而非陣列。

## Related problems / 相關題目

- [q66](../leetcode/q66.md)
- [q67](../leetcode/q67.md)
- [q3379](../leetcode/q3379.md)
- [q3637](../leetcode/q3637.md)
- [q3640](../leetcode/q3640.md)
