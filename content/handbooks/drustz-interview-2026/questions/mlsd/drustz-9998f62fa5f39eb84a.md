---
id: drustz-9998f62fa5f39eb84a
section: mlsd
order: 57
level: A
title: 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十五、Lineage、监控与删除 ⭐⭐⭐
quick: >-
  作者文档章节 · 07 · Pre-training Data Systems：从原始网页到可审计训练 tokens · 十五、Lineage、监控与删除
  ⭐⭐⭐
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
## 十五、Lineage、监控与删除 ⭐⭐⭐

### 15.1 Data lineage 最小字段

```text
dataset_version
source_asset_id + rights_version
raw object pointer + content hash
all transform code/config/model versions
all keep/drop/redact/downweight reason codes
dedup cluster + canonical
tokenizer version
train shard/sample offsets
model run IDs consuming this version
```



Data lineage 不是只为了 debug，也是 rights update、PII incident、benchmark contamination 和 model card 的基础。

### 15.2 Funnel dashboard

每 stage 按 source/language/domain 报：

- docs/bytes/chars/tokens in/out；
- pass/drop/quarantine/redact reason；
- extraction empty/error/OCR confidence；
- exact/near duplicate rate 和 cluster size；
- PII/secret/safety hit rate；
- quality score distribution/threshold；
- tokenizer fertility、sequence length、packing utilization；
- estimated unique tokens、repeat count；
- processing throughput、cost/TB、retry/failure/backlog。

### 15.3 Drift detection

- crawl source/domain mix 变化；
- 新 AI-generated spam/style；
- language ID/quality score shift；
- parser change 导致平均长度突变；
- PII detector hit rate 突变；
- duplicate giant cluster；
- tokenizer fertility/unknown byte spike。

任何大幅变化先抽样 raw/extracted/kept/dropped examples，再决定阈值；不要自动“把分布调回去”，可能现实 web 真变了。

### 15.4 Human audit

每个 release 至少抽：

- uniform kept；
- uniform dropped；
- filter threshold 两侧；
- each language/domain/source；
- high duplicate clusters；
- PII/safety uncertain；
- new/changed domains；
- synthetic data。

记录 annotator rubric、agreement、adjudication。只看 kept data 会漏掉 filter false positives。

### 15.5 Takedown / deletion

```text
verified request / rights expiry / incident
  → resolve source assets + dedup/derived lineage
  → block future acquisition
  → tombstone raw/derived according to policy
  → rebuild affected curated/tokenized manifests
  → mark affected model runs/releases
  → document what can/cannot be removed from already trained weights
```



不要承诺从既有 model weights 中“精准删除”某条训练样本，除非有已验证 unlearning process；数据删除、未来不再训练、模型下架/重训是不同动作。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/07_pretraining_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/07_pretraining_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
