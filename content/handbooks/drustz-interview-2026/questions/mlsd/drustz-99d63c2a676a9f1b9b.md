---
id: drustz-99d63c2a676a9f1b9b
section: mlsd
order: 13
level: A
title: >-
  05 · Case Study：OCR / Signature Recognition ML System Design · 6.
  Evaluation：离线、端到端与线上三层
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 6.
  Evaluation：离线、端到端与线上三层
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md
    type: primary
---
## 6. Evaluation：离线、端到端与线上三层

### 6.1 Stage-level 指标

| Stage | 必看指标 | 必看 slice |
|---|---|---|
| Preflight | unusable recall、false recapture rate | capture/device、blur/glare/clipping |
| Detection | Recall、precision、mAP、IoU；文档级“是否漏掉任一签名” | template、signature size/type、重叠对象 |
| Quality/type | Macro-F1、per-class recall、calibration | rare type、新设备、低 DPI |
| OCR | CER/WER、field exact match/F1 | printed vs handwriting、语言、quality |
| Field linking | signature-to-name/date link accuracy | 多签名、多姓名、复杂表格 |
| Verification | ROC/DET、TAR@FAR、FMR/FNMR、EER（诊断） | forgery type、unseen signer、reference count、time gap |
| Identification | Recall@k、open-set detection/FAR | gallery size、unseen signer、相似姓名 |

### 6.2 End-to-end / workflow 指标

- 文档“所有必需 signer 都存在且关联正确”的 exact success rate；
- straight-through processing（STP）率；
- 人工审核率、审核分钟数/文档、review overturn rate；
- fraud loss / false rejection downstream outcome（有延迟 label 时分 cohort）；
- recapture rate 与完成率；
- P50/P95/P99 latency、availability、cost per 1K pages；
- 不同金额/客户/文档类型的 expected loss；
- 模型错误 vs data-quality 错误 vs policy 阈值错误的归因。

### 6.3 Benchmark 组成

至少维护：

1. clean canonical set；
2. production-distribution random holdout；
3. hard-quality set（blur/fax/clipped/overlap）；
4. real fraud/red-team set（按 attack type）；
5. unseen signer/template/device/customer set；
6. forward-time set；
7. synthetic stress set——单独报告，不能混成主要分数；
8. privacy/security tests（跨 tenant 检索、删除、日志泄漏、malformed input）。

每次 model/policy 发布做 paired comparison；关键安全 slice 不允许被 aggregate improvement 掩盖。先 shadow，再 canary，再 gradual rollout；所有 prediction 保存 version、threshold、输入质量特征和路由原因以便重放。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
