Alembic 筆記索引

這一組筆記把 Alembic 常用操作與設計原則整理成可查的主題文件。

導覽

- 主索引：INDEX.md
- Database 索引：database/README.md

主題導覽

- 01-baseline.md: 已存在資料庫的 baseline 建置流程
- 02-autogenerate.md: 自動生成 migration 的工作流與限制
- 03-data-migrations.md: 資料遷移與 seed 的做法
- 04-commands.md: 常用命令速查
- 05-troubleshooting.md: 常見問題與排查

快速開始

1. 確認 env.py 的 target_metadata 指向 SQLAlchemy Base.metadata
2. 先建立或校準 baseline (若資料庫已存在)
3. 使用 autogenerate 生成 migration
4. 審核 migration 內容後再升級資料庫

慣用資料夾結構

- migrations/
  - env.py
  - script.py.mako
  - versions/
- app/models/
- app/database/

備註

- Autogenerate 只能比對 schema，資料變更要自己寫 migration
- 任何 migration 都建議人工審核，避免誤刪/誤改
