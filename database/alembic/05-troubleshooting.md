常見問題排查

Autogenerate 沒偵測到變更

- Model 沒被匯入
  - 確保 env.py 中 import 了所有 models
- target_metadata 指向錯誤
  - 應該是 Base.metadata
- 連到錯誤的 DB
  - 檢查 alembic.ini 與環境變數

偵測到不想要的變更

- 可能因為資料庫的 server_default 與 Model 定義不一致
- 可能因為 naming convention 不一致導致索引差異
- 可以使用 include_object 忽略特定表或 schema

出現多個 heads

- 使用 alembic heads 檢查
- 用 alembic merge 合併分支

升級後出現大量差異

- 代表 DB 與 Model 沒同步，可能缺 migration 或 baseline 未設好
- 建議先對齊 DB schema，再啟用 autogenerate

降級失敗

- 有些 migration 無法安全回滾（例如 drop column）
- 建議在 downgrade 補上保護邏輯或改成不可回滾並註記

資料遷移造成效能問題

- 大量更新需分批處理
- 盡量在非尖峰時段執行 migration
- 可先新增欄位，再用獨立腳本回填
