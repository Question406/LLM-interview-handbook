---
id: drustz-9be14cc13fc8e65455
section: robotics
order: 67
level: A
title: 08 · 个人故事与提问清单（Stories & Asks） · §1 · 60 秒英文自我介绍（定制版）
quick: 作者文档章节 · 08 · 个人故事与提问清单（Stories & Asks） · §1 · 60 秒英文自我介绍（定制版）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## §1 · 60 秒英文自我介绍（定制版）

> 目标岗位假设：Multimodal Foundation Models 一类的 ML 岗（JD 要求 pretraining/post-training/RL、data mixtures、edge 部署）。若面 ML Infra-Data Infrastructure，把第二段换成 data pipeline 侧重（见 §1.1 变体）。

**逐字稿（~150 词，practice 到 55–70 秒）：**

> I'm Ray. For the last three years I've done LLM post-training, and before that a decade in human-computer interaction.
>
> Most recently I was at Reflection AI, where I owned mid-training and RL data pipelines — synthetic data generation, difficulty-based curriculum, and async rollout inference on GPU clusters. Before that, at Meta AI, I post-trained LLM ranking agents with SFT and RL — our multi-agent RL work on table reasoning hit #1 on TableBench and is in ACL 2026. Earlier, at Meta Reality Labs, I built EMG-based text input for AR glasses — real sensors, noisy signals, tight on-device latency budgets. My PhD at UW was in HCI.
>
> Why I'm here: robot learning is adopting the LLM playbook — behavior cloning is SFT, interventions are preference data, and the real bottlenecks are data mixtures and evaluation. That's the exact loop I've owned end-to-end, and I want to run it where the flywheel is just starting: robots in homes.

**讲法纪律：**

| 规则 | 原因 |
|---|---|
| 结尾主动收：*"Happy to go deep on any of these."* | 把深挖的选择权交给面试官，显得有存货 |
| 三段各 20 秒：现在→轨迹→为什么来 | Bridgewater 备考里验证过的结构（04_mock_questions Q1） |
| 不要展开 EMG 细节 | 它是弱点预案（§4）的弹药，别提前打光 |
| "owned" 只用于真属于你的部分 | 单轮否决制下被追穿一次就完了 |

### §1.1 变体：如果面的是 Data Infrastructure 岗

把第二段 Reflection 部分换成：

> At Reflection I built the data side of mid-training: synthetic data generation at scale, async inference over a shared GPU cluster to score and filter millions of samples, and the internal tooling that let researchers iterate on data mixtures without touching infra. [填入你的具体规模数字：每天处理多少 token/样本、多少 GPU]

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/08_stories_and_asks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md)。作者整理资料；许可和第三方来源范围见阅读指南。
