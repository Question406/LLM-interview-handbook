---
id: arch-mtp
section: arch
order: 19
level: A
title: Multi-Token Prediction（MTP）训练目标能带来什么？为什么不等于“每次 decode 多吐几个 token”？
quick: >-
  MTP 让模型在训练时预测多个未来 token，可增强序列表征；若把额外头作为 speculative draft，还需要 target
  verification 和足够 acceptance rate，才能在不改变目标分布的前提下获得实际加速。
tags:
  - MTP
  - Speculative Decoding
  - Architecture
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-V3 / MTP
    url: 'https://arxiv.org/abs/2412.19437'
    type: legacy-reference
  - title: FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---

这块容易把 MTP 说成「训练时一次看未来 $k$ 个 token，推理就自然一次吐 $k$ 个」。标准 next-token loss 只直接监督 $t+1$。MTP 增加多个未来位置的预测目标，让 hidden state 被要求携带更长程的可预测信息；其价值首先是训练信号，不是魔法式地改变自回归语义。推理若要用额外头当 draft，必须走 speculative verification，否则分布就变了。

## 训练：多偏移监督，防泄漏

对位置 $t$ 的隐状态 $h_t$，除 $\hat y_{t+1}$ 外再设头预测 $t+2,\ldots,t+1+k$。DeepSeek-V3 一类实现用串联的 MTP 模块，每个模块吃上一模块的表示再预测更远一位。损失是加权和

$$
\mathcal{L}=\mathcal{L}_{\mathrm{NTP}}+\sum_{i=1}^{k}\lambda_i\mathcal{L}_{\mathrm{MTP}}^{(i)}.
$$

必须划清 teacher forcing 边界：未来 label 不能泄漏进主干输入。位置编码仍按真实下标走 RoPE，$R_m^\top R_n=R_{n-m}$，多头预测的是不同偏移，不是改相对位置定义。骨干可以是 MoE + SwiGLU，MTP 头通常更轻，避免把 $k$ 倍算力全压在主路径。

## 推理：draft 不能直接采纳

若把 MTP 头当 draft，一次提出多个候选 token，再用目标模型并行验证：接受前缀直到第一次拒绝，拒绝处按目标分布重采样。目标分布由验证规则保证，不是「多吐几个就算加速」。系统收益取决于 draft 成本、acceptance rate、KV / 调度开销。候选差则只增加工作量。这和独立小模型做 speculative decoding 同一套验收，只是 draft 来自同源多头。

FlashAttention 等内核加速的是单步 attention 访存，不代替 acceptance rate。别把「训得更好」和「decode 更快」说成一件事。

## 追问

- **和 beam search 的区别？** Beam 在推理维护多假设；MTP 主要是训练多目标，推理默认仍可贪心 / 采样单路径。
- **$k$ 越大越好吗？** 远偏移更难、泄漏风险更高，$\lambda_i$ 通常递减。以主任务 CE 和下游为准。
- **没做验证能不能上线加速？** 不能。那会改采样分布，延迟数字再好看也不算同一模型。
