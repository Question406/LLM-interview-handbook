---
id: drustz-678e3ec931df1dcbbb
section: mlsd
order: 14
level: A
title: >-
  05 · Case Study：OCR / Signature Recognition ML System Design · 7. Production
  architecture 与 cost-efficient serving
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 7.
  Production architecture 与 cost-efficient serving
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
## 7. Production architecture 与 cost-efficient serving

### 7.1 服务架构

```text
Client / Batch Upload
        │
        ▼
API Gateway + Auth + Rate Limit
        │  content hash / idempotency key
        ▼
Secure Intake ─► Object Store (encrypted, region/tenant scoped)
        │
        ▼
Job Controller / Queue ─────────────────────────────┐
        │                                            │
        ├─► CPU preflight / native PDF fast path     │
        ├─► Detector workers (dynamic batch)         │
        ├─► OCR/layout workers                       │
        ├─► Verification + calibrated policy         │
        └─► Expensive fallback only when needed      │
                                                     ▼
                                  Artifact/Decision Store + Audit Trace
                                                     │
                                    ┌────────────────┴───────────────┐
                                    ▼                                ▼
                               Callback/API                    Review Queue/UI
                                                                     │
                                            corrections + outcomes ─► Data flywheel
```



可靠性：

- `content_hash + tenant_id + config_version` 做 artifact cache；同文档重试不重复推理；
- job/state 持久化，stage worker 幂等；大 PDF 页级 fan-out，最终 fan-in；
- queue 分 online/batch/high-risk lane，避免 backfill 挤占在线 SLA；
- timeout、bounded retry、DLQ；损坏/炸弹 PDF 在隔离 decoder 处理；
- 人工修正是 immutable correction，重跑不能静默覆盖；
- model、threshold、OCR engine、preprocessing 全部 pin version。

### 7.2 粗算规模（面试必须会）

假设日均 1,000 万页：

\[
10{,}000{,}000 / 86{,}400 \approx 116\ pages/s
\]

峰值 5 倍约 `580 pages/s`。若 detector 单 GPU dynamic batching 后稳定处理 100 pages/s，理论 6 张 GPU 覆盖峰值；加 40% headroom、rolling deploy 和故障冗余，先规划约 10 张，再用压测校正。不要把这个估算说成真实 benchmark。

真正成本常由人审主导：假设 5% 文档进入 review、每次 2 分钟、人工 &#36;30/hour，则每 1000 文档人工成本：

\[
1000\times 5\%\times(2/60)\times \$30=\$50
\]

所以把 review rate 从 5% 降到 3%，在不增加 false accept 的条件下，往往比 GPU 再快 20% 更值钱。

### 7.3 成本优化按收益排序

1. **先缩输入**：native PDF 不 OCR；template/anchor 先裁 ROI；合理 DPI/resize，不把整页原图送 verifier。
2. **级联路由**：deterministic checks → small quality model → detector → verifier；只有不确定/高价值样本走大模型。
3. **不做无意义阶段**：只查 presence 就不跑 identity verifier；没有 reference 时不伪造 verification。
4. **batch + async**：离线文档允许 dynamic batching；interactive recapture 走低延迟 lane。
5. **优化/distillation**：distillation、quantization、ONNX/TensorRT/CoreML；但必须按 slice 复测，细线签名可能对量化敏感。
6. **缓存与增量**：page hash、signature crop hash、reference embedding cache；reference 更新只重算 gallery，不重跑历史 OCR。
7. **autoscaling**：按 queue age + GPU utilization，不只按 CPU/QPS；预热模型避免冷启动毁掉 P99。
8. **压低人审时间**：UI 同屏展示 query、多个 reference、bbox、quality、reason code；不要只给一个分数让 reviewer 自己找页。

### 7.4 Edge / on-device 何时值得

手机端先做 blur/glare/clipping 与 recapture guidance，可以避免坏图上传、改善 conversion；最终高风险 verification 仍可在服务端做。优势是 latency/privacy，代价是设备碎片、模型更新、可被篡改和算力受限。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
