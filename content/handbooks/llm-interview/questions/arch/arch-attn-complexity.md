---
id: arch-attn-complexity
section: arch
order: 2
level: A
title: Self-Attention 的时间和显存复杂度是什么？
quick: >-
  $QK^\top$ 与 $\mathrm{attention}\times V$ 是 $O(T^2 d)$，显式 attention matrix 是 $O(T^2)$ memory；Q/K/V/O
  projections 还有 $O(Td^2)$。短序列可能 projection 主导，长序列 $T^2$ 项主导。
tags:
  - Transformer
  - Complexity
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

这块容易只背「注意力是 $O(n^2)$」就停。对 $X\in\mathbb{R}^{T\times d}$，要把投影和 $T^2$ 项拆开，并分清 FLOPs 与 HBM 显存。短序列可能是大矩阵乘法主导，长序列才是二次项主导。

## 时间：两段不要混

线性投影 $Q=XW_Q$、$K=XW_K$、$V=XW_V$ 以及输出投影，约 $O(Td^2)$（常数随头数、是否 GQA 变）。分数与聚合

$$
S=QK^\top\in\mathbb{R}^{T\times T},\qquad \mathrm{Attn}=\mathrm{softmax}\!\left(\frac{S}{\sqrt{d_h}}\right)V
$$

各是 $O(T^2 d)$（按头维乘完再拼）。因此总 FLOPs 约 $O(Td^2+T^2 d)$。当 $T\ll d$ 时第一项更大；当 $T$ 到 8k、32k，$T^2 d$ 压过投影。多头不改变渐近，只把 $d$ 拆成 $n_h\cdot d_h$。

FFN / SwiGLU 是另一笔 $O(Td\cdot d_{\mathrm{ff}})$，和注意力二次项独立。MoE 只稀疏化 FFN，**不改变** dense attention 的 $T^2$。RoPE 是 $O(Td)$ 的旋转，可忽略。

## 显存：物化 $T\times T$ 才是痛点

朴素实现把 $S$ 写进 HBM，激活显存 $O(T^2)$（再乘层数、head）。这就是长上下文先爆显存的原因。FlashAttention 不改变 exact attention 的渐近 FLOPs，而是分块在 SRAM 做 softmax，避免物化大 $T\times T$。训练还要存反传中间；checkpoint / 重算换的是时间换空间，不是改复杂度阶。

Decode 阶段若已有 KV cache，每步对新 $q$ 做 $O(T_{\mathrm{cache}}d)$，不再每步重算全量 $T^2$，但 cache 本身占 $O(T d_{\mathrm{kv}})$ 带宽。面试把「训练一步的复杂度」和「自回归一步的复杂度」分开说。

## 追问

- **GQA / MLA 改的是哪一项？** 主要改 $d_{\mathrm{kv}}$ 从而改 cache 字节，不是把 $T^2$ 变成线性。
- **线性注意力为什么是 $O(Td^2)$？** 核技巧把 $QK^\top V$ 换成 $Q(K^\top V)$，先缩 $T$ 维；表达力和外推要另验。
- **为什么 FlashAttention 还是二次？** 它优化访存，渐近 FLOPs 仍是 $O(T^2 d)$。
