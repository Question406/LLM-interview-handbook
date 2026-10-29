---
id: company-minimax
section: companies
order: 7
level: A
title: MiniMax：Agent-Native Post-Training 该准备什么？
quick: >-
  MiniMax 我会重点讲清 LLM policy 与 environment 的职责划分、交错的 agent SFT 轨迹、可执行环境和与
  artifact 对齐的奖励、长 horizon Agent RL，还有训练、推理、Agent 怎么解耦。
tags:
  - MiniMax
  - Agent RL
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ MiniMax M2
    url: 'https://arxiv.org/abs/2605.26494'
    type: legacy-reference
---

MiniMax 方向的 Agent RL 远不止 `model.generate()` 加一个标量奖励分数（reward）。M2 一类材料强调，sampling 轨迹（rollout）要进 sandbox、browser、tools，轨迹很长；策略生成的 token 和环境返回的 token 怎么区分、state reset、reward 和权重同步，都比单 response GRPO 复杂。

比如一条 100 步的轨迹，最后只有一个「任务成没成」的分数。单轮 outcome RL 里省掉价值评估模型（critic）的经验，机械搬到这种 100-step Agent 上就不灵了，长 horizon 下 action-level credit 可能重新变得重要。公开真题还会问数据质量和参数量怎么拆，光用 Agent 名词填满时间撑不住。

## 准备主线

1. 先区分 token roles：哪些 token 属于 policy（思考、工具调用），哪些属于环境（observation、页面、编译器输出）。SFT 要把环境 token 排除在损失计算之外，见 `pt-tool-mask`。
2. 奖励要可执行，对齐 artifact（测试通过、文件 diff、页面断言），「看起来像完成」不算。评测拆成 planning 和 hallucination 率，见 `minimax-agent-eval-planning-hallucination`。
3. 数据和规模方面，怎么提高数据集质量、怎样用 GPT 辅助又不泄漏标准，见 `minimax-data-quality-gpt`；参数量在 embedding / attn / FFN / 头上怎么拆，见 `minimax-param-breakdown`、`code-sizing`。
4. 系统解耦要讲训练、推理、Agent runtime 的权重和工具版本怎么对齐，长轨迹怎么 reset 和部分回放。SFT→RL 的 acceptance checks 对照 `byte-agent-posttrain-data-stage`。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- `minimax-data-quality-gpt`：如何提高数据集质量、怎样用 GPT 辅助
- `minimax-param-breakdown`：大模型参数量在各部分大概怎么拆
- `minimax-agent-eval-planning-hallucination`：Planning 与 hallucination 率怎么评
- `pt-tool-mask`：tool-response 为何要 mask 损失（loss）
- `byte-agent-posttrain-data-stage`：SFT / RL 数据与切换 acceptance checks
- `code-sizing`：参数量与 KV 估算

## 追问

**为什么单 response GRPO 迁不过去？**
一组里一条轨迹就有 100 步，outcome 很稀疏，全对或全错的组会更多。需要过程分，或者分阶段 reset。

**环境 token 进了 loss 会怎样？**
模型会学着复读观察，学不到决策，所以一定要 mask。

**GPT 辅助造数据，实验怎么做？**
先过验证器（verifier），再人工抽检，并报告 teacher model（teacher）带来的风格偏差，见 `minimax-data-quality-gpt`。
