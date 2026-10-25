---
id: arch-mtp
section: arch
order: 19
level: A
title: Multi-Token Prediction（MTP）训练目标能带来什么？为什么不等于“每次 decode 多吐几个 token”？
quick: "MTP 的价值主要在训练：除了下一个 token，再让每个位置预测更远的几个 token，给表示多加一层监督。推理时想用这些头加速，就得把它们的预测当 draft，交给目标模型验证，接受率够高才真的变快。训练能预测多步，不等于解码能直接一次吐多步。"
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

MTP 首先是一个训练信号。标准 next-token loss 只直接监督 $t+1$，MTP 再加几个更远位置的预测目标，要求 hidden state 带上更长程、可预测的信息。它不会改变自回归的语义，推理时想用额外的头一次出好几个 token，必须走 speculative verification，否则输出分布就变了。

举个例子，模型训练时在位置 $t$ 同时预测后面 $k$ 个 token，很容易被顺口说成「那推理就能一次吐 $k$ 个」。可那几个只是猜测，越往后猜错的可能越大，直接采纳就等于换了一个模型在采样。

## 训练时怎么加，怎么防泄漏

对位置 $t$ 的隐状态 $h_t$，除了 $\hat y_{t+1}$，再设头预测 $t+2,\ldots,t+1+k$。DeepSeek-V3 一类实现用串联的 MTP 模块，每个模块吃上一个模块的表示，再往远预测一位。损失是加权和：

$$
\mathcal{L}=\mathcal{L}_{\mathrm{NTP}}+\sum_{i=1}^{k}\lambda_i\mathcal{L}_{\mathrm{MTP}}^{(i)}.
$$

这里要守住 teacher forcing 的边界：未来的 label 不能漏进主干的输入。位置编码照旧按真实下标走 RoPE，$R_m^\top R_n=R_{n-m}$；多个头预测的是不同偏移，相对位置的定义没有变。骨干可以是 MoE + SwiGLU，MTP 头通常做得更轻，免得把 $k$ 倍算力全压在主路径上。

## 推理时 draft 要过验证

把 MTP 头当 draft 用，就是一次提出多个候选 token，再让目标模型并行验证：从头往后接受，直到第一次被拒绝，被拒的位置按目标分布重采样。输出仍然服从目标分布，靠的就是这条验证规则。能快多少，取决于 draft 的成本、acceptance rate，以及 KV 和调度的开销；候选质量差，只会白白多算。这和用独立小模型做 speculative decoding 是同一套验收，区别只在 draft 来自同一个模型的多个头。

FlashAttention 这类内核加速的是单步 attention 的访存，提高不了 acceptance rate。所以「训得更好」和「decode 更快」要分开讲。

## 追问

**MTP 和 beam search 有什么区别？**
Beam search 在推理时维护多个假设。MTP 主要是训练时的多目标，推理默认还是贪心或采样，走单条路径。

**$k$ 越大越好吗？**
不是。偏移越远越难预测，泄漏风险也越高，所以 $\lambda_i$ 通常递减。最后看主任务的交叉熵（CE）和下游指标。

**不做验证，能直接拿 MTP 头上线加速吗？**
不能。那会改变采样分布，延迟数字再好看，也已经不是同一个模型了。
