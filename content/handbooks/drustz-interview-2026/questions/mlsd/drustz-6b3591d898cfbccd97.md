---
id: drustz-6b3591d898cfbccd97
section: mlsd
order: 7
level: A
title: >-
  05 · Case Study：OCR / Signature Recognition ML System Design · 0.
  先把题目钉死：五种任务不能混在一起
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 0.
  先把题目钉死：五种任务不能混在一起
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
## 0. 先把题目钉死：五种任务不能混在一起

| 任务 | 输入 → 输出 | 典型用途 | 主要指标 | 主要风险 |
|---|---|---|---|---|
| Signature detection | 文档页 → bbox / polygon / absent | 检查表单是否签名、定位 ROI | Recall、mAP、漏检率 | 把印刷线条、手写备注、印章当签名 |
| Quality/type classification | 签名 crop → usable / blur / clipped；wet / typed / e-sign | 决定是否重拍、走哪条 pipeline | Macro-F1、per-class recall、coverage | 低质量图被错误放行 |
| Signature verification（1:1） | 当前签名 + 声称身份的 reference → genuine / reject / review | 银行、保险、合同核验 | TAR@FAR、FMR/FNMR、calibration | 欺诈者被接受，或合法用户被拒绝 |
| Signature identification（1:N） | 当前签名 + gallery → top-k signer / unknown | 档案归属、法证辅助 | Recall@k、open-set FAR | gallery 大、相似签名、隐私风险更高 |
| OCR / field association | 文档 → signer name/date/title + source span | 抽取“谁、何时、以什么身份签署” | Field F1、CER/WER、link accuracy | 把邻近字段错误地关联给签名 |

**必须再问一句**：是离线图像（offline signature image），还是触控笔产生的在线轨迹（online signature）？后者有坐标、压力、速度、笔画顺序，验证信号强得多；前者不能假装拥有这些 liveness/dynamics 信号。

### 面试中建议提出的 8 个澄清问题

1. **业务动作**：结果只是预填/排序，还是会自动拒绝付款、合同或身份？错误成本差几个数量级。
2. **任务范围**：只判断“签过了”，还是要和 reference 做 1:1 verification？是否需要 1:N identification？
3. **输入分布**：PDF 原件、扫描仪、手机照片、传真、截图分别占多少？每份多少页？
4. **reference 条件**：每个 signer 有几张可信 enrollment signatures？多久以前采集？reference 本身是否可能被污染？
5. **对手模型**：只处理自然质量问题，还是要抵抗 copy-paste、trace、skilled forgery、生成式伪造？
6. **SLO 与规模**：QPS、P95 latency、日文档量、允许的人工审核率和单文档成本？
7. **风险目标**：可以接受多大的 false match rate？不同交易金额是否应使用不同 threshold？
8. **隐私/地域**：是否把签名视为 biometric / sensitive personal data？consent、retention、deletion、region 有什么约束？

下面用一个具体假设回答：

> 为保险/金融文档做离线签名处理。输入是 PDF 或手机照片；先检测签名、判断质量，再用 1–5 张可信 reference 做 1:1 verification，同时 OCR 姓名/日期并关联到签名。低风险文档 P95 < 1 秒，高风险允许异步；不自动做最终法律/欺诈裁决，灰区进入人工审核。日均 1,000 万页，峰值约均值 5 倍。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
