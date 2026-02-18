---
title: 04-commands
note_type: knowledge
domain: backend
category: database
tags: [database, backend, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: knowledge
---
# 04-commands

常用命令速查

版本與狀態

- alembic current
  查看資料庫目前版本

- alembic history
  查看所有版本歷史

- alembic heads
  查看所有 head（若有分支會有多個）

- alembic show <rev>
  查看指定版本內容

建立 migration

- alembic revision -m "message"
  建立空白 migration

- alembic revision --autogenerate -m "message"
  自動生成 migration（需設定 target_metadata）

升級/降級

- alembic upgrade head
  升級到最新

- alembic upgrade <rev>
  升級到指定版本

- alembic downgrade -1
  回退一個版本

- alembic downgrade <rev>
  回退到指定版本

標記版本（不執行）

- alembic stamp <rev>
  標記 DB 版本為指定 revision

輸出 SQL（不執行）

- alembic upgrade head --sql
  產生 SQL script

分支與合併

- alembic merge <rev1> <rev2> -m "merge heads"
  合併多個 heads
