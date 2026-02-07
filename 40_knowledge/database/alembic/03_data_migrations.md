---
title: 03-data-migrations
note_type: knowledge
domain: database
tags: [database, knowledge]
created: 2026-02-03
updated: 2026-02-03
status: active
source: database
canonical: database/alembic/03-data-migrations.md
---
# 03-data-migrations

資料遷移與 Seed

結論先說

Alembic 的 autogenerate 只比對 schema，不會偵測資料變更。

資料變更的處理方式

方法 1：在 migration 中手動寫 SQL

  from alembic import op
  import sqlalchemy as sa

  def upgrade() -> None:
      op.execute(
          sa.text("""
              INSERT INTO roles (id, name, description) VALUES
              ('uuid-1', 'admin', '管理員'),
              ('uuid-2', 'user', '一般用戶')
          """)
      )

  def downgrade() -> None:
      op.execute(
          sa.text("""
              DELETE FROM roles WHERE name IN ('admin', 'user')
          """)
      )

方法 2：Schema + Data 一起做（最常見）

  def upgrade() -> None:
      # 1. 先新增欄位（允許 null）
      op.add_column('users', sa.Column('role_id', sa.UUID(), nullable=True))

      # 2. 回填資料
      op.execute(sa.text("""
          UPDATE users SET role_id = (
              SELECT id FROM roles WHERE name = 'user'
          )
      """))

      # 3. 改成不可為空
      op.alter_column('users', 'role_id', nullable=False)

方法 3：Seed Script（適合初始資料或環境特定資料）

  # scripts/seed_data.py
  from app.models import Role
  from app.database import get_session

  async def seed_roles():
      async with get_session() as session:
          session.add_all([
              Role(name="admin", description="管理員"),
              Role(name="user", description="一般用戶"),
          ])
          await session.commit()

設計原則

- Migration 內的資料操作要可重複執行或可安全回滾
- 大量資料更新要注意鎖表與效能影響
- 需要依賴應用程式邏輯時，使用獨立 script 會更安全
- 不同環境有不同資料時，不建議放入 migration
