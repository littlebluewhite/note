---
title: "Two-Phase Commit / 兩階段提交"
note_type: knowledge
domain: backend
category: distributed_systems
tags: [backend, distributed-systems, go, rust, two-phase-commit, 2pc]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "14"
level: advanced
review_interval_days: 14
next_review: 2026-03-03
---

# Two-Phase Commit / 兩階段提交

## Purpose / 目的

理解 Two-Phase Commit（2PC）協議的運作機制、已知限制，以及何時應改用替代方案。2PC 是分散式交易中最經典的原子提交協議（atomic commit protocol），確保跨越多個資源管理器的操作要麼全部提交、要麼全部回滾。然而 2PC 本質上是**阻塞協議（blocking protocol）**——coordinator 在特定階段崩潰時，participant 會無限期等待，持有的鎖無法釋放。

核心權衡：**2PC 用可用性換取跨服務原子性。在微服務架構中，這個代價通常過高，應優先考慮 Saga Pattern。**

---

## Symptoms / 常見症狀

| 症狀 | 表現 | 影響範圍 |
|---|---|---|
| **Coordinator timeout** | Participant 回覆 `VOTE_COMMIT` 後收不到 Phase 2 決定 | 單一交易進入 in-doubt |
| **Participant blocking** | In-doubt participant 持有 row/table lock 不釋放 | 阻塞存取相同資源的所有交易 |
| **In-doubt transactions** | 資料庫殘留 prepared 但未完成的交易 | 佔用連線池、系統資源 |
| **Lock escalation** | 多筆 in-doubt 交易的鎖觸發行鎖升級為表鎖 | 整張表讀寫阻塞，連鎖擴散 |

---

## Diagnostic Steps / 診斷步驟

1. **確認 coordinator 狀態**：檢查程序是否存活，讀取其 WAL 中最後一筆決定記錄。
2. **辨識 in-doubt 交易**：查詢資料庫中 prepared 狀態的交易清單與建立時間。
3. **檢查 participant 日誌**：確認每個 participant 在 Phase 1 的投票（COMMIT / ABORT）及是否收到 Phase 2 決定。
4. **關聯交易 ID**：將 coordinator 的 global XID 與各 participant 的 prepared transaction 對應，還原完整流程。

---

## Detection Commands / 偵測指令

### PostgreSQL: Prepared Transactions

```sql
-- 列出所有 in-doubt 交易
SELECT gid, prepared, owner, database
FROM pg_prepared_xacts
ORDER BY prepared ASC;

-- 超過 5 分鐘的孤兒交易
SELECT gid, prepared, owner, database, now() - prepared AS age
FROM pg_prepared_xacts
WHERE prepared < now() - interval '5 minutes';
```

### MySQL: XA Recovery

```sql
-- 列出所有 PREPARED 狀態的 XA 交易
XA RECOVER CONVERT XID;
```

### Log Pattern Matching

```bash
# Coordinator: Phase 1 超時
grep -E "PREPARE_TIMEOUT|vote_timeout|participant_unreachable" /var/log/tx-coordinator/*.log

# Participant: in-doubt 狀態
grep -E "IN_DOUBT|waiting_for_decision|coordinator_unreachable" /var/log/tx-participant/*.log
```

---

## Common Causes & Resolutions / 常見原因與解法

### 1. Coordinator Crash After Collecting Votes / 協調者收集投票後崩潰

Coordinator 將 `GLOBAL_COMMIT` 寫入 WAL 後、發送決定前崩潰。所有 participant 進入 in-doubt。

**Resolution: Recovery Log Replay**

```rust
// coordinator_recovery.rs — Coordinator 從 WAL 重播未完成決定

#[derive(Debug, Clone, PartialEq)]
enum Decision { Commit, Abort, Pending }

struct WalEntry {
    global_xid: String,
    decision: Decision,
    participants: Vec<String>,
}

fn recover_pending_transactions(wal: &[WalEntry]) -> Vec<(String, Decision)> {
    wal.iter().map(|entry| {
        let resolved = match entry.decision {
            Decision::Commit => Decision::Commit,  // WAL 已記錄，重發 COMMIT
            Decision::Abort  => Decision::Abort,    // WAL 已記錄，重發 ABORT
            Decision::Pending => Decision::Abort,   // 未決定即崩潰，安全 abort
        };
        (entry.global_xid.clone(), resolved)
    }).collect()
}
```

### 2. Participant Crash During Prepare / 參與者準備階段崩潰

Participant 未回覆投票，coordinator 逾時。

**Resolution: Timeout + Rollback**

```go
// participant_timeout.go — Coordinator 端超時處理

func CollectVotesWithTimeout(
	participants []string, timeout time.Duration,
) string {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	results := make(chan VoteResult, len(participants))
	for _, pid := range participants {
		go func(id string) {
			vote, err := sendPrepare(ctx, id)
			results <- VoteResult{ParticipantID: id, Vote: vote, Err: err}
		}(pid)
	}

	decision := "COMMIT"
	for range participants {
		vr := <-results
		if vr.Err != nil || vr.Vote == "ABORT" {
			decision = "ABORT" // 任一 participant 超時或拒絕，全域 abort
		}
	}
	return decision
}
```

### 3. Network Partition / 網路分區

Coordinator 與部分 participant 斷聯。已投票 COMMIT 的 participant 陷入 in-doubt。

**Resolution: Manual Intervention**

```sql
-- PostgreSQL: 手動處理孤兒 prepared transaction
COMMIT PREPARED 'global_xid_12345';   -- 強制提交
ROLLBACK PREPARED 'global_xid_12345'; -- 強制回滾

-- MySQL: 手動處理 XA 交易
XA COMMIT 'global_xid_12345';
XA ROLLBACK 'global_xid_12345';
```

> **警告**：Heuristic decision 可能導致資料不一致。執行後必須進行跨服務的資料對帳（reconciliation）。

### 4. In-Doubt Transaction Accumulation / 不確定交易堆積

多次 coordinator 短暫不可用後，prepared transaction 堆積，鎖衝突擴散。

**Resolution: Automated Cleanup**

```rust
// indoubt_cleanup.rs — 自動清理超齡 prepared transaction

fn cleanup_stale_transactions(
    prepared_txns: &[PreparedTxn],
    max_age: Duration,
    coordinator_reachable: bool,
) -> Vec<CleanupAction> {
    prepared_txns.iter().filter_map(|txn| {
        let age = SystemTime::now().duration_since(txn.prepared_at).ok()?;
        if age <= max_age { return None; }

        Some(if coordinator_reachable {
            CleanupAction::QueryCoordinator(txn.xid.clone())
        } else {
            CleanupAction::HeuristicRollback(txn.xid.clone()) // 最後手段
        })
    }).collect()
}
```

---

## Prevention Checklist / 預防清單

- [ ] **Prefer Saga over 2PC**：跨服務邊界使用 Saga Pattern，僅在同一資料庫叢集內考慮 2PC
- [ ] **Set aggressive timeouts**：Phase 1 投票超時 5-30s，Phase 2 決定等待上限 30-120s
- [ ] **Implement heuristic decisions**：Coordinator 長期不可用時，participant 應能自行決定並記錄
- [ ] **Monitor prepared transactions**：告警 prepared transaction 數量 > 10 或存活時間 > 5 分鐘
- [ ] **WAL on coordinator**：決定必須先持久化到 WAL（含 `fsync`）再發送
- [ ] **Idempotent commit/rollback**：Participant 的提交與回滾操作設計為冪等，容許 coordinator 重複發送

```yaml
# Prometheus alerting rule
groups:
  - name: two_phase_commit_alerts
    rules:
      - alert: StalePreparedTransaction
        expr: pg_prepared_xacts_age_seconds > 300
        for: 1m
        labels:
          severity: warning
      - alert: PreparedTransactionAccumulation
        expr: pg_prepared_xacts_count > 10
        for: 2m
        labels:
          severity: critical
```

---

## Cross-references / 交叉引用

- [[13_saga_pattern|Saga Pattern / Saga 模式]] -- Saga 是 2PC 在微服務場景下的主要替代方案。2PC 保證原子性但犧牲可用性（阻塞協議）；Saga 保證最終一致性但需要補償操作。跨服務用 Saga，同一叢集內可用 2PC。
- [[../database/transactions|Database Transactions / 資料庫交易]] -- 單節點 ACID 交易是 2PC 的基礎構件。每個 participant 的 PREPARE 依賴底層 redo/undo log 保證本地持久性與可回滾性。

---

## References / 參考資料

1. **Designing Data-Intensive Applications (DDIA)** -- Martin Kleppmann, Chapter 9: Consistency and Consensus. 涵蓋 2PC 運作原理、阻塞問題，以及共識協議為何優於 2PC
2. **X/Open XA Specification** -- The Open Group, 1991. 定義 Transaction Manager 與 Resource Manager 之間的介面標準，PostgreSQL、MySQL、Oracle 均實作 XA
3. **Gray & Lamport, "Consensus on Transaction Commit"** -- ACM TODS, 2006. 提出 Paxos Commit，結合共識協議與 2PC 解決 coordinator 單點故障
4. **Garcia-Molina & Salem, "Sagas"** -- ACM SIGMOD, 1987. 提出 Saga 作為長交易的替代方案，避免長時間持鎖
