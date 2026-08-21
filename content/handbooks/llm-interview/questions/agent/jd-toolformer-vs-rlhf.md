---
id: jd-toolformer-vs-rlhf
section: agent
order: 102
level: S
title: 京东大模型：Toolformer 自监督 tool-call 数据与 RLHF 有何不同，为什么可能更泛化？
quick: >-
  Toolformer 从文本中自举候选 API call，以对后续 token likelihood 的改进筛选伪标注，主要是 imitation / self-supervision；RLHF
  由偏好或 reward 优化整条策略。前者能从广泛未标注文本覆盖 API 使用模式，但泛化并不自动成立，仍依赖工具语义与分布匹配。
tags:
  - JD
  - Toolformer
  - Tool Use
  - RLHF
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 秋招面经-京东大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/3f02a8e652fa414c819de810452a2b2a
    type: candidate-first-hand
  - title: 'Toolformer: Language Models Can Teach Themselves to Use Tools'
    url: https://arxiv.org/abs/2302.04761
    type: primary-paper
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法
- 届别 / 流程：秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Toolformer中通过自监督学习生成tool call数据,这个训练范式和RLHF的差别在哪里?为什么它更容易泛化?”**

陷阱是把「更容易泛化」说成定理。京东大模型一面要的是范式对比：Toolformer 用语言模型自己当过滤器造伪标注，RLHF 用偏好或环境奖励优化整条策略。前者数据覆盖可以更广，但不等于对新工具、新权限语义有保证。面试若直接答「自监督一定比 RLHF 泛化」，缺的是 held-out 工具和任务测试。

## Toolformer：自举调用，用下文似然做过滤

Toolformer（Schick et al., arXiv:2302.04761）的流程是：在自然语言位置插入候选 API 调用，执行得到 observation，再看这段调用是否降低后续 token 的损失。只有能改善语言建模 / 下文预测的调用被保留，插回文本当训练数据，然后做 imitation。它不要求每条都有人类偏好标签或线上 reward，因此能吃更广的未标注文本和 API 文档，学习何时调用、如何把 observation 写回上下文。

目标函数本质是下一词似然，不是任务成功。过滤器问的是「这次调用对接着把句子说完有没有帮助」，不是「最终有没有下对单」。所以它擅长补计算器、日历、检索这类能立刻改善局部文本的工具；对需要多步、有副作用、要权衡成本的策略，信号偏弱。数据是自监督伪标注，噪声来自过滤器本身：能降低 perplexity 的调用不一定是用户想要的动作。

## RLHF：序列级目标，覆盖窄、权衡直接

RLHF / 后来的 RLVR 直接优化人偏好、规则或环境给出的标量，适合最终成功、延迟、安全和成本等 sequence-level trade-off。它依赖 reward 定义和 rollout 分布：偏好数据贵、容易过拟合标注员口味；reward hacking 会让模型学会讨好评分而不是用对工具。和 Toolformer 比，RLHF 不是在造「何时调用」的监督文本，而是在改整条策略的采样分布。

「更容易泛化」应限定为：不依赖狭窄人工偏好、能从开放文本覆盖更多 API 使用模式。若新工具 schema、权限或环境动态变了，两种范式都要在 held-out tools / tasks 上测。Toolformer 对新 API 仍要能采样出合法调用并让过滤器看见下文增益；RLHF 则要 reward 覆盖新失败模式。工具调用的 SFT vs RL 怎么分工，见 `ali-tool-call-error-sft-rl`：格式和基本调用可 imitation，对错与重试更适合带环境的 RL。生产 Agent 的 tool schema 与权限是另一层，见 `agent-tool-call`，训练范式解决不了越权。

## 追问

- **过滤器只用 perplexity，会留下什么坏样本？** 能让下文更流畅但调用了不该用的工具，或编造了看起来合理的 observation。要用 schema / 执行成功再加一层硬过滤。
- **能不能两者叠用？** 可以：Toolformer 式伪标注做 SFT 打底，再用 RLHF / RLVR 优化成功率和安全。面试要说清各管哪一段损失。
- **泛化怎么实证？** 留出未见过的工具名或参数格式，看调用是否仍合法且对任务有用；不能从「自监督」三字推出保证。
- **和 Function Calling SFT 有何不同？** 普通 SFT 依赖人工或蒸馏轨迹；Toolformer 的监督来自「调用是否改善 LM loss」，规模可以更大，但目标不是任务 reward。
