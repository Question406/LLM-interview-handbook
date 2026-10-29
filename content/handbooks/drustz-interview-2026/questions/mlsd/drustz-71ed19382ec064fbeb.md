---
id: drustz-71ed19382ec064fbeb
section: mlsd
order: 83
level: A
title: 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 边界：这篇和 08 的分工
quick: 作者文档章节 · 15 · Case：设计 ChatGPT 级对话系统的评测流水线 · 边界：这篇和 08 的分工
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md
    type: primary
---
## 边界：这篇和 08 的分工

[08 · Evaluation、Production 与成本闭环](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) 讲的是**任意 ML 系统**的通用 eval stack：四层结构、slice gate、offline→online 阶梯、监控、延迟标签。那些不在这里重复。

**本篇只讲通用对话助手特有的部分**：没有 ground truth 时如何构造可信判决、LLM judge 的系统性偏差与验证方法、benchmark 污染的攻防、以及"人工评不起"这个硬约束下的sampling设计。

相关：[04 §7 reward 与 verifier 的分离](?book=drustz-interview-2026&section=mlsd&question=drustz-7ba2d317f214182b45)、[07 §8 预训练侧的 decontamination pipeline](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573)、[14 §8 客服 agent 的评测切片](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca)、agent 轨迹与  $\mathrm{pass}^k$  见 [`../agentic_prep/agentic2/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/README.md)。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/15_case_eval_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/15_case_eval_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
