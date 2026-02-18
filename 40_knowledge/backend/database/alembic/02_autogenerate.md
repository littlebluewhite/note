---
title: 02-autogenerate
note_type: knowledge
domain: backend
category: database
tags: [database, backend, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: knowledge
---
# 02-autogenerate

Autogenerate（自動生成 Migration）

基本概念

Alembic 的 --autogenerate 會比較「SQLAlchemy Model」與「資料庫 Schema」的差異，產生 migration 檔案。

標準流程

1. 修改 models
2. 生成 migration

   alembic revision --autogenerate -m "add_phone_to_users"

3. 審核 migration 內容
4. 執行 migration

   alembic upgrade head

env.py 必要設定

- 確保所有 models 被匯入

  from app.models import *

- target_metadata 指向 Base.metadata

  target_metadata = Base.metadata

常見的忽略規則

當資料庫內有你不想比較的表或 schema，可以在 env.py 中設定 include_object：

  def include_object(object, name, type_, reflected, compare_to):
      if type_ == "table" and name in ["alembic_version", "spatial_ref_sys"]:
          return False
      return True

  context.configure(
      # ...
      include_object=include_object,
  )

Autogenerate 能偵測的項目

- 新增/刪除資料表
- 新增/刪除欄位
- 欄位型別變更
- 索引與外鍵變更

無法偵測的項目

- 資料遷移（INSERT/UPDATE/DELETE）
- 欄位改名、表改名（通常會被視為「刪除 + 新增」）
- 複雜約束或自訂 SQL

審核要點

- 確認是否有「刪除」動作（drop table/column）
- 確認型別或 nullable 是否符合預期
- 確認 server_default 的差異是否真實需求

提高穩定性的技巧

- 使用一致的 naming convention，避免 autogenerate 亂判索引名稱
- 對於 rename 欄位，手動寫 op.alter_column 與 op.rename_table
- 對於大量變更，分多個小 migration 較容易回溯
