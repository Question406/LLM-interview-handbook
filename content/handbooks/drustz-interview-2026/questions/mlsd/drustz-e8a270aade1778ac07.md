---
id: drustz-e8a270aade1778ac07
section: mlsd
order: 20
level: A
title: 05 · Case Study：OCR / Signature Recognition ML System Design · 13. 面试前一页速记
quick: >-
  作者文档章节 · 05 · Case Study：OCR / Signature Recognition ML System Design · 13.
  面试前一页速记
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
## 13. 面试前一页速记

```text
1. 消歧：detect / quality / verify 1:1 / identify 1:N / OCR-link；offline vs online
2. 风险：业务动作、FAR 目标、人审率、reference provenance、attack model
3. 数据：prod + consented collection + licensed + synthetic supplement
4. 矩阵：capture × quality × background × template × signer variation × attack
5. 标签：polygon + type/quality + claimed signer + pair subtype + provenance
6. 防泄漏：split by signer/document/session/template/device；forward-time；dedup
7. 稀缺：metric learning、P×K batch、hard negative、SSL、active + random audit
8. Pipeline：preflight → detect → OCR/link → quality → embed → calibrate → policy
9. 模型：detector/segmenter + layout graph + Siamese/ArcFace；VLM teacher/fallback
10. 指标：detection recall；field F1；TAR@FAR；FMR/FNMR；calibration；STP/cost
11. 决策：T_accept / T_reject；灰区 review；按 expected loss 和风险分 policy
12. 成本：native PDF、ROI、cascade、batch、quantize、cache；human cost first-class
13. 安全：replay/copy-paste/skilled/gen/enrollment poisoning；多信号 + step-up
14. 监控：input/score/OOD + random audit + delayed outcome；shadow→canary→rollback
15. 收尾：静态签名模型是 risk signal，不是 cryptographic proof
```



> 一句话收尾：高质量方案不是“找一个最强视觉模型”，而是用可信 reference 和无泄漏数据训练可calibration的专用模型，在真实攻击与未来域上评估，再用双阈值、人审和多信号把错误成本管住。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/05_case_ocr_signature.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/05_case_ocr_signature.md)。作者整理资料；许可和第三方来源范围见阅读指南。
