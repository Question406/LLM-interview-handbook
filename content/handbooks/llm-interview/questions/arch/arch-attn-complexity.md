---
id: arch-attn-complexity
section: arch
order: 2
level: A
title: Self-Attention 的时间和显存复杂度是什么？
quick: >-
  时间上分两块：Q/K/V/O 投影是 $O(Td^2)$，$QK^\top$ 和 $\mathrm{attention}\times V$ 是 $O(T^2
  d)$；显式保存 attention 矩阵还要 $O(T^2)$ 显存。所以短序列主要花在投影上，长序列由 $T^2$ 项主导，长上下文通常先爆显存。
tags:
  - Transformer
  - Complexity
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Attention Is All You Need
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
---

对 $X\in\mathbb{R}^{T\times d}$，Self-Attention 的 FLOPs 约为 $O(Td^2+T^2 d)$：前一项是线性投影，后一项是打分和聚合；显存的痛点是物化 $T\times T$ attention 矩阵带来的 $O(T^2)$。只背一句「attention 是 $O(n^2)$」不够，要把投影和二次项拆开，再把 FLOPs 和 HBM 显存分开讲。

比如 $T$ 远小于 $d$ 的短序列，大矩阵乘法占大头；$T$ 到 8k、32k 以后，$T^2 d$ 才压过投影。

## 时间：两段别混在一起

线性投影 $Q=XW_Q$、$K=XW_K$、$V=XW_V$ 加上输出投影，约 $O(Td^2)$，常数随头数、是否 GQA 而变。分数与聚合

$$
S=QK^\top\in\mathbb{R}^{T\times T},\qquad \mathrm{Attn}=\mathrm{softmax}\!\left(\frac{S}{\sqrt{d_h}}\right)V
$$

各是 $O(T^2 d)$（按头维乘完再拼）。两项加起来就是 $O(Td^2+T^2 d)$。多头不改变渐近复杂度，只是把 $d$ 拆成 $n_h\cdot d_h$。

FFN / SwiGLU 另有一笔 $O(Td\cdot d_{\mathrm{ff}})$，和 attention 的二次项无关。MoE 只稀疏化 FFN，dense attention 的 $T^2$ 照旧。RoPE 是 $O(Td)$ 的旋转，可以忽略。

## 显存：物化 $T\times T$ 才是痛点

朴素实现把 $S$ 写进 HBM，激活显存是 $O(T^2)$，还要再乘层数和 head 数，长上下文先爆显存就是这个原因。FlashAttention 的 exact attention 渐近 FLOPs 没变，它的做法是分块在 SRAM 里做 softmax，从而不用物化大的 $T\times T$。训练还要存 backpropagation 用的中间结果；checkpoint / 重算是拿时间换空间，复杂度的阶不变。

面试时我会把「训练一步的复杂度」和「autoregressive 一步的复杂度」分开说。Decode 阶段有了 KV cache，每步只对新的 $q$ 做 $O(T_{\mathrm{cache}}d)$，不用每步重算全量 $T^2$，但 cache 本身占 $O(T d_{\mathrm{kv}})$，读它要吃带宽。

## 追问

**GQA / MLA 改的是哪一项？**
主要改 $d_{\mathrm{kv}}$，从而减少 cache 字节数，$T^2$ 并没有变成线性。

**线性 attention 为什么是 $O(Td^2)$？**
核技巧把 $QK^\top V$ 换成 $Q(K^\top V)$，先把 $T$ 维缩掉。表达力和外推要另外验证。

**FlashAttention 为什么还是二次？**
它优化的是访存，渐近 FLOPs 仍是 $O(T^2 d)$。
