---
id: drustz-b4bee63bda8ae97f88
section: mlsd
order: 122
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 19. 诚实边界：哪些要主动标注
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 19. 诚实边界：哪些要主动标注
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
## 19. 诚实边界：哪些要主动标注

| 边界 | 怎么诚实地说 |
|---|---|
| **RL 训练器内部**（PPO/GRPO 的分布式实现、rollout 调度器、优化器细节）不是我主责 | 「训练器本身不是我的模块——我在 mid-training 侧负责数据供给和筛选，以及它依赖的batch inference基础设施。算法层面我能讲清楚为什么退化样本梯度为 0、以及 DAPO 那几个改动在解决什么，但我没有实现过分布式 rollout 调度器。」 |
| **没有金融/交易经验** | 直接说没有，然后转到结构：「金融我完全没做过。如果这里的任务是把交易信号做成可验证 reward，我能讲的是**怎么判断一个 reward 是不是被策略主动搜索**这类结构问题，具体的市场微结构我需要学。」 |
| **没有大规模在线 serving 的 oncall 经验** | 「我做的batch inference是离线throughput场景——抢占、幂等、可恢复、并发调节这些我踩过；但**面向用户的低延迟在线 serving 和 oncall 我没做过**，p99 SLO、限流降级、事故响应那套我只有读来的知识。」（这条在被问「训完怎么上线」时一定要说） |
| **多轮/agentic RL 环境的数据** 我做的主要是单轮可验证的 math/STEM | 「我的经验集中在单轮、终态可验证的题。多轮 agentic RL 的环境构建、中间状态的 credit assignment 是相邻但不同的问题，我能推理但没有实操过。」 |
| **真实用户 prompt 分布** 接触有限 | 「mid-training 侧我拿到的主要是语料和合成的 prompt，产品侧真实分布我接触有限——所以 §5.1 里那一条我讲的是设计考量，不是我做过的。」 |
| **HCI 博士背景** | 不用回避，它是资产：「我的 HCI 训练让我对『我以为我在测的东西其实不是』这类 construct validity 问题特别敏感——§10 那套读 trace 的分层协议本质上就是定性编码的方法。」（迁移句式见 [12](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) §3） |

**绝不要说的**：把设计方案说成已做过的结果；把团队产出说成个人 ownership；报一个自己没算过的数字。本篇里所有带具体数字的地方，要么是真实经历（16/128/12%），要么是当场可推导的（退化率表、筛选占比公式、90 亿 token），后者要说清楚是「我现在算给你看」。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
