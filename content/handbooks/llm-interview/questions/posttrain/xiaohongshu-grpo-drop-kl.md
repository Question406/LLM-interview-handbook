---
id: xiaohongshu-grpo-drop-kl
section: posttrain
order: 122
level: S
title: 小红书大模型实习：GRPO 为何可以去掉 KL？Reward 怎么设？
quick: >-
  在强可验证奖励、组内相对优势已提供稳定基线时，有人会减弱或去掉对 ref 的 KL 以放开探索；代价是格式崩与语言漂移。Reward
  应可复核（任务成功、格式、安全），并监控 KL / 熵 / 崩坏率决定是否加回约束。
tags:
  - Xiaohongshu
  - GRPO
  - KL
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
  - title: DeepSeekMath
    url: https://arxiv.org/abs/2402.03300
    type: primary-paper
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary-paper
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲一下论文里的 GRPO 算法原理，为什么去掉 KL 散度，reward function 怎么设置”**

小红书实习一面这题，这块容易把「去 KL」讲成定理，或把 GRPO 原理、去 KL、reward 三问搅成一句「组内对比所以不需要约束」。我会分三层：GRPO 用组相对优势替代 critic；KL 是把策略锚在 reference 上的护栏；去 KL 是强可验证奖励下的工程取舍，不是 DeepSeekMath 原文的必然结论。

## GRPO 原理：组相对优势，不是「没有基线」

对同一 prompt 采样一组输出，用组内标准化优势做 clipped policy gradient，从而弱化对 value model 的依赖。组相对 baseline 提供局部对比信号，这是它和 PPO+critic 的主要差别。clip 仍在，ratio 过大照样裁。没有 critic 不等于没有约束：reward 噪声大时，组内排序本身就会漂。公式与方差问题见 `pt-grpo`、`pt-grpo-variance`。

## 「去 KL」是取舍，不是免费探索

KL 把 $\pi_\theta$ 锚在 SFT / $\pi_{\mathrm{ref}}$ 上，抑制偏离和格式崩。若任务奖励极可靠（可执行 verifier）、更在意探索更长推理链，固定 $\beta$ 的 token 级 KL 会拖慢或压扁有用探索。DAPO 等后续工作也讨论过减弱显式 KL、改用采样与 clip 管更新。必须同时讲清风险：reward hacking、重复、乱码、语言漂移。实务常用动态 $\beta$、阶段性关闭、或只在格式 / 安全维保留硬约束，并监控熵、崩坏率和 holdout 成功率再决定是否加回。相关卡：`gaode-dapo-no-kl`、`ant-grpo-kl-vs-ppo`。

## Reward：可复核，过程分不能靠「看起来像 CoT」

优先规则 / 环境反馈：最终任务成功、格式可解析、安全不变量。过程分只覆盖可观测里程碑（编译过、单测红绿、工具返回合法），不能把不可验证的 CoT 文本直接当正确过程。credit assignment 要能解释到关键错误步，并用反例集检查 hacking：空实现、恒真断言、把拒绝说成成功。主信号必须可程序化复核；LLM-as-judge 最多当辅助。去 KL 之后，reward 是唯一还在拉住策略的东西，定义一松，熵和语言立刻会漂。

## 追问

- **论文原文一定去 KL 吗？** 不一定。DeepSeekMath 的 GRPO 仍可带 KL；去掉是后续工程选择。
- **没有 KL 还要不要 clip？** 要。clip 管单步更新幅度，KL 管相对 reference 的全局偏离，不是同一个旋钮。
- **开放对话能不能去 KL？** 通常不能。奖励不可靠时，KL 往往是唯一还在的护栏。
- **如何决定加回 KL？** 熵骤降、格式崩坏率升、holdout 掉而训练 reward 仍涨时，先加回约束或硬格式门，而不是继续加大探索。
