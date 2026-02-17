---
title: "Kafka Patterns & Operations / Kafka 維運"
note_type: knowledge
domain: backend
category: distributed_systems
tags: [backend, distributed-systems, go, rust, kafka, operations]
created: 2026-02-17
updated: 2026-02-17
status: active
source: knowledge
series: backend
chapter: "18"
level: advanced
review_interval_days: 14
next_review: 2026-03-03
---

# Kafka Patterns & Operations / Kafka 維運

## Purpose / 目的

整理 Kafka 生產環境常見維運問題：症狀辨識、診斷流程、CLI 偵測指令、根因分析與預防策略。目標讓 on-call 工程師在 15 分鐘內定位問題並採取對應措施。

---

## Symptoms / 常見症狀

| # | 症狀 | 影響 | 緊急度 |
|---|------|------|--------|
| S1 | Consumer lag 持續攀升 | 訊息延遲，下游資料過時 | High |
| S2 | Rebalancing storms | Consumer 停止消費，吞吐量驟降 | High |
| S3 | Message duplication | 重複副作用（扣款、通知） | Medium |
| S4 | Partition hotspot | 單一 partition 積壓，其餘閒置 | Medium |
| S5 | Broker disk full | Broker 拒絕寫入 | Critical |
| S6 | Under-replicated partitions | 資料可靠性下降，潛在遺失風險 | Critical |

---

## Diagnostic Steps / 診斷步驟

**Step 1 — 確認叢集健康：** 透過 `kafka-metadata.sh` 或 Kafka UI 確認 broker 存活與 controller 選舉。

**Step 2 — 檢查 consumer group：** 用 `kafka-consumer-groups.sh` 確認 lag 與 member 數，member = 0 代表全部離線。

**Step 3 — 查看 JMX metrics：**

- `kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions` — 非零即告警
- `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec` — 寫入速率
- `kafka.consumer:type=consumer-fetch-manager-metrics,attribute=records-lag-max` — 最大 lag

**Step 4 — Burrow / Kafka UI 視覺化：** Burrow 偵測 lag 趨勢，比單次快照更能判斷是否惡化。

---

## Detection Commands / 偵測指令

### S1: Consumer Lag

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group | awk 'NR==1 || $6 > 0'
```

```promql
sum(kafka_consumergroup_lag) by (consumergroup, topic, partition) > 10000
```

### S2: Rebalancing Storms

```bash
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group --state
```

```promql
rate(kafka_server_group_coordinator_metrics_group_completed_rebalance_count[5m]) > 0.1
```

### S3–S4: Duplication / Hotspot

```bash
# S3: offset commit 狀態
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group --verbose

# S4: partition log size 分佈
kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe --topic-list my-topic
```

```promql
# S4: partition 寫入速率偏差
stddev(rate(kafka_server_brokertopicmetrics_messagesin_total{topic="my-topic"}[5m])) by (topic)
```

### S5: Broker Disk Full

```bash
kafka-log-dirs.sh --bootstrap-server localhost:9092 --describe
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name my-topic --describe
```

```promql
kafka_log_log_size / node_filesystem_size_bytes > 0.85
```

### S6: Under-Replicated Partitions

```bash
kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated-partitions
```

```promql
kafka_server_replicamanager_underreplicatedpartitions > 0
```

---

## Common Causes & Resolutions / 常見原因與解法

### S1: Consumer Lag — 處理速度不足

**原因：** Consumer 跟不上 producer 寫入，常見於下游 DB 寫入慢或運算邏輯複雜。

```go
// Go (sarama): 搭配增加 partition 數與 consumer 並行度
config := sarama.NewConfig()
config.Consumer.Group.Rebalance.GroupStrategies = []sarama.BalanceStrategy{
    sarama.NewBalanceStrategyRoundRobin(),
}
// kafka-topics.sh --alter --topic my-topic --partitions 12
```

- 水平擴展 consumer（上限 = partition 數），或改用 batch / async 寫入

### S2: Rebalancing Storms — poll interval 過短

**原因：** 單筆處理耗時超過 `max.poll.interval.ms`（預設 5 分鐘），被 coordinator 踢出。

```rust
// Rust (rdkafka): 調整 consumer config
let consumer: StreamConsumer = ClientConfig::new()
    .set("group.id", "my-group")
    .set("max.poll.interval.ms", "600000")
    .set("session.timeout.ms", "30000")
    .set("heartbeat.interval.ms", "10000")
    .create()
    .expect("Consumer creation failed");
```

- 啟用 static membership（`group.instance.id`）、減少 `max.poll.records` 縮短處理時間

### S3: Message Duplication — offset commit 前 crash

**原因：** 處理完成但 commit 前 crash，或 rebalance 導致 offset 未及時 commit。

```go
// Go: 啟用 producer idempotence 防止 retry 造成重複
config := sarama.NewConfig()
config.Producer.Idempotent = true
config.Producer.RequiredAcks = sarama.WaitForAll
config.Net.MaxOpenRequests = 1
```

- 下游實作 idempotent write（message key + offset dedup），嚴格場景用 Kafka Transactions

### S4: Partition Hotspot — key 分佈不均

**原因：** 以 user_id 為 key 但大客戶流量集中。

```go
// Go: 自定義 partitioner，加入 salt 打散熱點 key
func (p *SpreadPartitioner) Partition(msg *sarama.ProducerMessage, n int32) (int32, error) {
    key, _ := msg.Key.Encode()
    salted := fmt.Sprintf("%s-%d", string(key), rand.Intn(4))
    h := fnv.New32a()
    h.Write([]byte(salted))
    return int32(h.Sum32()) % n, nil
}
```

- 注意：打散後同一 key 順序保證喪失，需評估業務可否接受

### S5: Broker Disk Full — retention 過長

**原因：** Retention policy 過長、寫入量暴增、log compaction 落後。

```bash
# 緊急：縮短 retention（12 小時）+ 設定 partition size 上限（10GB）
kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name my-topic \
  --alter --add-config retention.ms=43200000,retention.bytes=10737418240
```

- 長期規劃 tiered storage（KIP-405）將冷資料卸載至 S3

### S6: Under-Replicated Partitions — broker 過載

**原因：** Follower 跟不上 leader，常見於負載不均、網路抖動、磁碟 I/O 瓶頸。

```bash
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 \
  --reassignment-json-file reassignment.json --execute
```

- 確認 `replica.lag.time.max.ms` 是否合理（預設 30s），考慮用 Cruise Control 自動化 rebalance

---

## Prevention Checklist / 預防清單

### Monitoring / 監控

- [ ] 部署 Prometheus + kafka_exporter，收集 broker / topic / consumer group 指標
- [ ] Grafana dashboard：consumer lag、under-replicated partitions、disk usage、request rate
- [ ] 告警：lag > 10K 持續 5min、under-replicated > 0 持續 2min、disk > 85%

### Retention & Partition / 保留與分區策略

- [ ] 每個 topic 明確設定 `retention.ms` 與 `retention.bytes`，勿依賴 broker 預設
- [ ] 建立 topic 時 partition 數設為 consumer 數的 2-3 倍以留餘裕
- [ ] 選擇 partition key 前分析 key cardinality，避免熱點

### Consumer Config / 消費者調優

- [ ] `max.poll.interval.ms` 設為最慢處理時間的 2-3 倍
- [ ] `session.timeout.ms` >= heartbeat interval x 3
- [ ] 啟用 `group.instance.id`（static membership）減少非必要 rebalance
- [ ] Producer 預設啟用 `enable.idempotence=true`

### Operational Hygiene / 維運紀律

- [ ] 變更 partition 數或 retention 前先在 staging 驗證
- [ ] 維護 topic 清單文件，記錄 owner、用途、SLA

---

## Cross-references / 交叉引用

- [[17_kafka_deep_dive]] — Kafka 內部架構、ISR 機制、Exactly-Once Semantics 原理
- [[15_distributed_locking]] — 分散式鎖在 consumer coordination 中的應用

---

## References / 參考資料

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Kafka: The Definitive Guide, 2nd Ed.](https://www.oreilly.com/library/view/kafka-the-definitive/9781492043072/)
- [Confluent Developer Resources](https://developer.confluent.io/)
- [Cruise Control](https://github.com/linkedin/cruise-control) / [Burrow](https://github.com/linkedin/Burrow)
