---
id: drustz-e0eaadd316fc806c80
section: plans
order: 37
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 2：Transformer / Attention
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 2：Transformer / Attention
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 作者复习计划与报告
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## Week 2：Transformer / Attention

### 本周目标

真正掌握 Transformer block，不只是知道 QKV。

### 必学概念

- Token embedding
- Positional embedding
- RoPE
- Q / K / V
- Self-attention
- Multi-head attention
- Causal mask
- Scaling by sqrt( $d_k$ )
- MLP / FFN
- Residual connection
- LayerNorm / RMSNorm
- Pre-norm vs post-norm
- Decoder-only model
- Logits / sampling

### 你必须能回答的问题

1. 为什么 attention 是 `softmax(QK^T / sqrt(d_k))V`？
2. Q、K、V 的 shape 是什么？
3. 多头 attention 为什么不是简单重复算多次？
4. causal mask 为什么要加 `-inf`？
5. 训练时为什么可以并行处理整个 sequence？
6. decode 时为什么不能完全并行生成所有未来 token？
7. RoPE 和 absolute positional embedding 的直觉区别是什么？
8. pre-norm 为什么在深层 transformer 中更稳定？

### 小实现

- [ ] single-head attention
- [ ] multi-head attention
- [ ] causal mask
- [ ] 一个 GPT block
- [ ] transformer bug hunt：mask、position embedding、loss shift、softmax dim

### 推荐练习顺序

1. 先只实现 single-head attention。
2. 再把 head 拆成 `[B, H, T, D]`。
3. 再加 causal mask。
4. 再加 residual + norm + MLP。
5. 最后写一个 tiny decoder-only model。

### 本周输出物

`week2_transformer_from_scratch.md`

必须包含：

- Transformer block 图
- QKV shape 推导
- Causal mask 示例
- 训练 vs 推理数据流对比
- 5 个 transformer coding bug

### 判断是否过关

面试官问：

> “Given B=2, T=128, hidden=768, heads=12, what are Q/K/V shapes?”

你能不犹豫回答，并能继续解释 attention score shape。

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
