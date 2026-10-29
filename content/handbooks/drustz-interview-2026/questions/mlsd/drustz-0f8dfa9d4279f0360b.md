---
id: drustz-0f8dfa9d4279f0360b
section: mlsd
order: 56
level: A
title: >-
  07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十四、Distributed data
  system：trillion-token pipeline 如何可靠运行
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十四、Distributed
  data system：trillion-token pipeline 如何可靠运行
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md
    type: primary
---
## 十四、Distributed data system：trillion-token pipeline 如何可靠运行

### 14.1 Storage layers

```text
raw/        immutable fetched bytes + source metadata
extracted/  structured text/layout + parser versions
signals/    quality/safety/dedup features (可重算)
curated/    keep/drop/downweight decisions + canonical maps
tokenized/  tokenizer-specific sequences
shards/     immutable train-ready files
manifests/  exact membership, order/sampling config, checksums
```



Raw 与 derived 分离。不要覆盖“清洗后的最终 CSV”；每层 immutable/versioned，manifest 指向具体 objects。

### 14.2 Idempotency 与 restart

每个 stage 的 output key：

```text
hash(input content/version + code commit + config + model version)
```



- Worker retry 写同 key；atomic commit manifest。
- Partial shard 放 temporary namespace，成功校验后 publish。
- Checkpoint 按 partition，而非整个 job 只有一个 done flag。
- Dead-letter queue 保留 parse/fetch failures 和 reason。
- Backfill 用新 version，不静默修改旧 object。

### 14.3 Distributed dedup 的难点

- Exact hash 可 partition/sort。
- MinHash/LSH 需要大 shuffle；按 language/length/domain blocking 降 candidate，但会漏跨 block duplicate。
- Connected components 合并 transitive clusters；防 giant boilerplate cluster。
- Canonical selection 需 deterministic tie-breaker。
- Cluster map versioned；后续 deletion 可以找所有 derived records。

### 14.4 Sharding 与 loader

- Shard size 平衡 object-store requests、shuffle granularity、failure recovery。
- 每 shard checksum、doc/token counts、source mix、min/max IDs。
- Loader prefetch、local cache、async I/O；监控 data starvation/GPU idle。
- Deterministic global order 通常代价高；至少 dataset membership、sampling algorithm 和 seeds 可重现统计等价 stream。
- 多 worker 防重复/漏读：global sample IDs + distributed sampler state checkpoint。

### 14.5 Backpressure 与 resource tiers

不同 stage：

- Crawl/network-bound。
- Parse/OCR CPU/GPU mixed。
- MinHash shuffle/memory-heavy。
- LLM quality classifier GPU inference-heavy。
- Tokenization CPU-heavy。

用 queue depth + autoscaling + per-stage quotas；昂贵 learned filter 放在便宜 rule filter 后，避免对必删垃圾跑 GPU。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
