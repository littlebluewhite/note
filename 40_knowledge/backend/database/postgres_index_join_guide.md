---
title: postgres index join guide
note_type: knowledge
domain: backend
category: database
tags: [database, backend, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: knowledge
---
# postgres index join guide

PostgreSQL Index vs Join Strategy Guide

目的

快速判斷何時加索引、何時改查詢、何時調整 join 策略。

決策要點

1) WHERE / JOIN 欄位是否有索引
- 有索引但仍慢，先看 EXPLAIN 是否真的使用
- 沒索引且資料量大，先建立索引

2) 選擇性（selectivity）
- 高選擇性（結果很少）適合索引
- 低選擇性（例如狀態欄位）索引效益低

3) 排序與 LIMIT
- ORDER BY + LIMIT 常可用索引避免 Sort
- 索引順序要對應排序方向

4) JOIN 型態判斷
- Nested Loop: 外層結果小 + 內層索引
- Hash Join: 中大型資料量，內層可建立 hash
- Merge Join: 兩邊已排序或有排序索引

常見對應策略

- 查詢條件固定、結果小 -> 建單欄或複合索引
- 多條件且選擇性一般 -> 複合索引或 Bitmap Scan
- 需要大小寫不敏感 -> 表達式索引 (lower(col))
- 只查活躍資料 -> 部分索引 (WHERE is_active = true)

EXPLAIN 判讀提示

- Seq Scan + Filter rows 很多 -> 考慮索引
- Sort 節點昂貴 -> 考慮索引順序或增加 work_mem
- Nested Loop loops 很大 -> 可能需要改成 Hash Join 或加索引

避免的作法

- 為每個欄位都加索引
- 在索引欄位上包函式（除非有表達式索引）
- 用 SELECT * 導致 Index Only Scan 失效

實務流程

1. 用 EXPLAIN (ANALYZE, BUFFERS) 找出瓶頸
2. 評估索引是否能改變計畫
3. 測試變更後的執行計畫
4. 保留最少必要索引
