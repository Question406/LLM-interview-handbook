---
id: drustz-276eb0fbf01071e5f8
section: mlsd
order: 162
level: A
title: 19 · Case：设计 agent 能力 benchmark · 0. 这篇解决什么 · 和其他文件的边界
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 0. 这篇解决什么 · 和其他文件的边界
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 0. 这篇解决什么 · 和其他文件的边界

题面：**"Design a benchmark for evaluating agents."**

这是一道**测量系统设计题**，不是模型设计题。交付物不是一个更强的 agent，而是一台**能稳定分辨两个 agent 谁更强、并且能说清自己误差有多大的仪器**。绝大多数候选人会把它答成"我要评哪些能力维度"——那是需求清单，不是系统设计。区分度、噪声下界、可复现性、抗污染、单次评测成本，这五件事才是本题的主体。

| 想找的内容 | 去哪 |
|---|---|
| 现有 agent benchmark 的分数、失败模式、引用姿势 | [`../agentic_prep/agentic2/04_benchmarks.md`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/04_benchmarks.md)（速查卡，本篇不重复主表） |
| agent runtime：tool 协议、durable execution、状态恢复、prompt injection 防御 | [`../agentic_prep/agentic2/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/README.md) |
| 通用 offline→online 评测阶梯、slice、judge calibration、监控 | [08](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) |
| reward 设计与 reward hacking 的通用结构 | [03](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2)、[labs/lab02](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab02_reward_design/) |
| 训练数据的污染与去污染 funnel | [07 §8](?book=drustz-interview-2026&section=mlsd&question=drustz-a31756199987603573) |
| 客服 agent 的业务指标（deflection / containment / resolution） | [14](?book=drustz-interview-2026&section=mlsd&question=drustz-1979efc83c83eeddca) |

**本篇只回答那些文件没答的**：怎么从零造一台测量仪器，以及这台仪器自己怎么被验证。凡是 08 已经讲透的（judge calibration方法、slice 原则、发布阶梯）本篇只做交叉引用。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
