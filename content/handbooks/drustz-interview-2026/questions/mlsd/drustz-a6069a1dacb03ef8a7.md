---
id: drustz-a6069a1dacb03ef8a7
section: mlsd
order: 103
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 0. 边界：这篇讲什么、不讲什么
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 0. 边界：这篇讲什么、不讲什么
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 0. 边界：这篇讲什么、不讲什么

| 主题 | 在哪 |
|---|---|
| 通用答题框架（Problem → Metrics → Data → …） | [01](?book=drustz-interview-2026&section=mlsd&question=drustz-5aa0ed2f208256af4b) |
| 通用数据来源与标签合同、泄漏、长尾 | [02](?book=drustz-interview-2026&section=mlsd&question=drustz-7702fad4618814bbd3) |
| reward 的一般结构、provenance 表、SFT/DPO/RL 何时用哪个 | [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) §5–§7 |
| **pre-training** 数据 funnel（crawl、parse、MinHash、mixture、scaling ablation） | [07](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) |
| offline → online 评测、阈值、延迟标签、监控 | [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) |
| search agent 的 trajectory RL | [06](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) |
| 客服 agent 的 resolution 标签与多租户 | [14](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca) |

**本篇只回答 RL post-training 数据流水线特有的问题**：prompt 从哪来、怎么变成可验证的、**怎么筛难度**、reward 从哪来且怎么验、怎么从 trace 里抓 hacking、多域怎么配比、这条 pipeline 的基础设施长什么样。

RL 数据和 pre-training 数据表面上都是「爬 → 洗 → 去重 → 配比」，[07](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) 那条 funnel 的**形状**可以复用，但**每一级的判据完全不同**——pre-training 问「这段文本值不值得预测下一个 token」，RL 问「这道题跑 128 次能不能产生非零梯度」。把 07 的答案背到这题上会被一眼看穿。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
