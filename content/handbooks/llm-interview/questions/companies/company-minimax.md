---
id: company-minimax
section: companies
order: 7
level: A
title: MiniMax：Agent-Native Post-Training 该准备什么？
quick: >-
  我会重点讲清 LLM policy 和环境边界、交错的 agent SFT 轨迹、可执行环境以及和 artifact 对齐的奖励、长 horizon
  Agent RL，还有训练、推理、Agent 怎么解耦。
tags:
  - MiniMax
  - Agent RL
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ MiniMax M2
    url: 'https://arxiv.org/abs/2605.26494'
    type: legacy-reference
---

MiniMax 方向，这块容易直接答成 `model.generate()` 加一个标量 reward。M2 一类材料强调：rollout 要进 sandbox、browser、tools，轨迹很长。policy 和环境的 token 归属、state reset、reward 和权重同步，都比单 response GRPO 复杂。单轮 outcome RL 省 critic 的经验，不能机械迁到 100-step Agent；长 horizon 下 action-level credit 可能重新重要。公开真题还会问数据质量和参数量拆分，不要只用 Agent 名词填满时间。

## 准备主线

1. **边界**：哪些 token 属于 policy（思考、工具调用），哪些属于环境（observation、页面、编译器输出）。SFT 要对环境 token 做 loss mask，见 `pt-tool-mask`。
2. **可执行奖励**：奖励对齐 artifact（测试通过、文件 diff、页面断言），不是「看起来像完成」。评测拆 planning 和幻觉率，见 `minimax-agent-eval-planning-hallucination`。
3. **数据与规模**：怎么提高数据集质量、怎样用 GPT 辅助但不泄漏标准，见 `minimax-data-quality-gpt`；参数量在 embedding / attn / FFN / 头上怎么拆，见 `minimax-param-breakdown`、`code-sizing`。
4. **系统解耦**：训练、推理、Agent runtime 的权重和工具版本怎么对齐；长轨迹 reset 与部分回放。对照 `byte-agent-posttrain-data-stage` 的 SFT→RL 门禁。

## 本手册真题卡

点击下面每条即可跳到对应题。

- `minimax-data-quality-gpt`：如何提高数据集质量、怎样用 GPT 辅助
- `minimax-param-breakdown`：大模型参数量在各部分大概怎么拆
- `minimax-agent-eval-planning-hallucination`：Planning 与幻觉率怎么评
- `pt-tool-mask`：tool-response 为何要 mask loss
- `byte-agent-posttrain-data-stage`：SFT / RL 数据与切换门禁
- `code-sizing`：参数量与 KV 估算

## 追问

- **为什么单 response GRPO 迁不过去？** 组内一条轨迹 100 步，outcome 稀疏，全对或全错组更多。需要过程分或分阶段 reset。
- **环境 token 进 loss 会怎样？** 模型学着复读观察，而不是决策。必须 mask。
- **GPT 辅助数据的实验怎么做？** 先 verifier，再人抽检，报告 teacher 风格偏差。见质量卡，不要说「用 GPT 生成就行」。
