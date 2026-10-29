---
id: drustz-b19cb282f9dcba34c5
section: mlsd
order: 12
level: A
title: >-
  05 · Case Study：OCR / Signature Recognition ML System Design · 5.
  Decision、calibration 与 threshold：不要只报 accuracy
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 5.
  Decision、calibration 与 threshold：不要只报 accuracy
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
## 5. Decision、calibration 与 threshold：不要只报 accuracy

### 5.1 两种错误的业务代价不同

- **FMR / FAR（False Match/Accept Rate）**：冒名/伪造被接受，通常是安全损失；
- **FNMR / FRR（False Non-Match/Reject Rate）**：真实签名被拒，通常是用户摩擦与人工成本。

在真实欺诈 base rate 很低时，普通 accuracy 会被 genuine majority 淹没。EER 只适合模型比较，不是生产 operating point。生产更应报：

- `TAR @ FAR = 10^-3 / 10^-4`；
- 不同 forgery type 的 FAR；
- 不同设备、模板、质量、时间间隔、客户的 slice metrics；
- calibration（Brier/ECE/reliability diagram）；
- review coverage 下的 selective risk。

### 5.2 双阈值 + 人工灰区

```text
score >= T_accept  → ACCEPT
score <= T_reject  → REJECT 或要求重新签署
otherwise          → REVIEW
```



阈值不应该只追求最大 F1。理想 decision 是最小化条件期望损失：

\[
a^*(x)=\arg\min_{a\in\{accept,reject,review\}}
\sum_y P(y\mid x)C(a,y)
\]

实际中按业务风险分 policy：

- &#36;50 的低风险 claim 可以扩大自动处理 coverage；
- &#36;500K 转账、单 reference、可疑 copy-paste 应直接 review/step-up；
- 新客户/新设备在 calibration 数据不足时使用更保守阈值；
- threshold 变更作为 versioned policy 发布，不需要重训模型。

### 5.3 Score calibration

在与生产 prevalence、quality、reference count 接近的 held-out calibration set 上做 Platt scaling、isotonic regression 或 likelihood-ratio calibration。**训练集不能同时拿来calibration。** 监控 score distribution 与 observed error；模型升级后旧 threshold 不可自动沿用。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
