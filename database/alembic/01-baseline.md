---
title: "01-baseline"
category: database
tags: [database]
created: 2026-02-03
updated: 2026-02-03
difficulty: "n/a"
source: database
status: active
---
# 01-baseline

Baseline（現有資料庫起點）

適用情境

- 你的資料庫已經存在且有正式資料
- Alembic 已加入專案，但從未建立過第一個 migration
- 不希望 Alembic 嘗試重建現有資料表

核心概念

Baseline = 告訴 Alembic「現在的資料庫結構就是起點」，不對既有結構做任何改動。

建立 Baseline 的步驟

1. 建立空的 baseline migration

   alembic revision --message "initial_baseline" --rev-id "000000000000"

2. 編輯生成檔案（migrations/versions/000000000000_initial_baseline.py）

   - revision: "000000000000"
   - down_revision: None
   - upgrade/downgrade 保持空

   範例：

   revision: str = "000000000000"
   down_revision: str | None = None

   def upgrade() -> None:
       pass

   def downgrade() -> None:
       pass

3. 將現有 migration 接到 baseline

   把第一個真正會變更結構的 migration 的 down_revision 指向 "000000000000"。

4. 標記資料庫版本（不執行 migration）

   alembic stamp 000000000000

5. 驗證

   alembic current
   alembic history

注意事項

- Baseline 不會執行任何 DDL，不會動到資料庫
- 如果資料庫不一致，autogenerate 可能會產生大量差異，務必先校準
- baseline ID 建議固定格式（如 12 碼 0）以方便辨識

常見錯誤

- down_revision 沒設為 None：會造成 Alembic 嘗試追溯不存在的父版本
- 使用 upgrade head 來建立 baseline：會對現有資料庫做不必要的 DDL
