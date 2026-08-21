---
id: company-meituan
section: companies
order: 10
level: A
title: 美团 / 北斗：大模型应用与算法应重点准备什么？
quick: >-
  业务闭环导向：SFT→RL 门禁、字段抽取多维 Reward、Workflow vs Agent、Memory vs
  RAG、LoRA/QLoRA 稳定性，以及 Thinking 开关对 SFT 的影响。公开面经同时覆盖 Reasoning 数据与应用八股。
tags:
  - Meituan
  - Beidou
  - 真题导航
  - 2025-2026
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
  - title: 26校招-美团大模型应用算法一面
    url: https://www.nowcoder.com/feed/main/detail/ae849dc9cdc9463782b266b2ca616ac7
    type: candidate-first-hand
  - title: 大模型算法 美团面经分享
    url: https://www.nowcoder.com/feed/main/detail/c6573225622842c290a00496c58db386
    type: candidate-first-hand
  - title: 美团北斗大模型秋招算法岗面经
    url: https://www.nowcoder.com/feed/main/detail/5a350d0aa51a4919be606348f9eed3ee
    type: candidate-first-hand
---

美团题更贴业务闭环：标注质量如何量化、简单 / 困难样本如何配比、Thinking 开关对 SFT 的影响、RL 初期 reward 先降后升怎么解释。准备时选一个字段抽取或到店助手项目，能从数据 → SFT → RL → 线上延迟完整讲通，比背更多论文名更有效。

## 准备主线

1. **SFT / RL 门禁**：已有 Reasoning SFT 为何还要 RL；格式合法率、verifier 稳定、组内对错混合后才切 RL。
2. **业务 Reward**：字段抽取要拆精确匹配、类型合法、必填、冲突、schema 与编造惩罚；会追 Reward Hacking。
3. **Agent 边界**：Workflow vs Agent、Memory vs RAG；下单 / 退款等强约束链路不要空喊 Agent。
4. **训练稳定性**：LoRA 为何挂 Linear 而不是 LayerNorm 之后；组内采样全错、reward/loss 震荡、过程监督信号。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 美团：已有 Reasoning SFT 数据，为何还要 RL？何时才切 RL
- 美团：组内采样 RL 的 on-policy rollout 没有正确答案怎么办
- 美团：RL 过程中的 reward 或 loss 震荡严重，如何排查
- 美团北斗：过程监督信号怎么设计，还能用在哪
- 美团：字段提取业务应设计哪些维度的 Reward
- 美团：Workflow 和 Agent 的核心差异与适用场景
- 美团：Memory 机制与 RAG 的区别、优势与落地场景
- 美团 26 校招：LoRA 能否插在 LayerNorm 之后
- [[meituan-thinking-on-sft|美团：开启 / 关闭 Thinking 对 SFT 有何影响]]
- 美团：7B 做 GRPO 时显存开销从哪来，怎么降
- 美团：业务里如何量化标注数据质量
- 美团：SFT 时如何平衡简单任务和复杂任务的权重
- 美团北斗：项目里为什么选 GRPO 而不是 PPO 或 DPO
- 美团：Attention 为什么要除以 $\sqrt{d_k}$
- 美团：RMSNorm 相对 LayerNorm 有何优势
- 美团：SFT 阶段如何防止过拟合
- [[meituan-langgraph-vs-prompt|美团北斗：LangGraph 比手写 prompt 流程强在哪]]
- 美团北斗：PPO/GRPO 后如何防止 OOD 崩塌
- 美团秋招二面：SwiGLU 的公式是什么，相对 ReLU / GELU 强在哪？
- 美团秋招二面：10 万词表时，交叉熵起步大概是多少？
- 美团秋招二面：GRPO 为什么还要 clip？SFT 后直接上会不会仍不稳定？
- 美团秋招二面：为何要三阶段后训练？V3 到 R1 各自在解决什么？
- 对齐为什么必须加 KL？系数太大或太小会怎样？
- 美团二面：veRL 为什么要重新 forward 算 logprob，生成时记下的不够吗？
- 美团二面：GRPO 哪个阶段最耗时？rollout 采样卡在哪？
- 美团 27 暑期：Qwen3-VL 的位置编码方案要怎么讲？
- 美团秋招二面：FLUX 怎么工作，LoRA 在这里起什么作用？
