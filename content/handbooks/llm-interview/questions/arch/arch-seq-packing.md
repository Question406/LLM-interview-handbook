---
id: arch-seq-packing
section: arch
order: 17
level: A
title: Sequence Packing 如何减少 Padding 浪费？
quick: "Packing 把几条短样本拼进同一条固定长度的序列，padding 少了，有效 token 的比例就上去了。拼的时候要用 block-diagonal mask 把样本隔开，position id 要和模型实现一致，loss 只算真实 token，否则一个样本会读到另一个样本的信息。"
tags:
  - Training
  - Packing
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Fewer Truncations Improve Language Modeling
    url: https://arxiv.org/abs/2404.10830
    type: primary
---

Sequence packing 就是把几条短样本塞进同一条定长序列，把原来 pad 掉的位置用起来。难点在 mask：不做隔离，样本之间会互相看见。

比如 max length 是 $4096$，四条 $800$-token 的样本各自 pad，大约八成位置是浪费的；packing 之后，它们可以放进同一条 sequence。可如果没做隔离，样本 A 的 token 就能读到样本 B，形成意外的跨文档注意力。loss 看上去在降，训练任务其实已经被改掉了。

## 三处要对齐

注意力要用 block-diagonal 的因果 mask（或者 varlen / FlashAttention 的 cu_seqlens）：段内仍是下三角，段与段之间全部屏蔽。记段 $s$ 的区间为 $[a_s,b_s)$，则

$$
M_{ij}=\begin{cases}
0 & \text{同段且 } j\le i,\\
-\infty & \text{否则.}
\end{cases}
$$

RoPE 的 position id 可以每段从 $0$ 重置，也可以沿 packed 序列连续编号，但必须和模型实现一致。弄错了，等于训练出一套和推理对不上的相对位置 $R_i^\top R_j=R_{j-i}$。loss 只在真实 token 上算交叉熵（CE），padding 和段边界的特殊符都不计。文档级任务还要带 segment id，免得模型把拼接当成一篇长文。

## 吞吐涨了，统计口径也变了

Packing 提高了每步的有效 token，但「一个 batch 有多少样本」和「有多少 token」不再成正比。梯度按 token 平均还是按 sequence 平均，会改变短样本的权重。课程学习、温度这些按 batch 算的东西都要重新看；MoE 的 aux loss 如果按 batch 内的专家频率算，packed 之后 token 来源更杂，负载统计要按真实 token 算，按「条数」算会偏。SwiGLU FFN 的算力跟着有效 token 走，padding 少了，MFU 才上得去。

实现上优先用现成的 varlen attention，自己拼 dense mask 很容易漏。评测阶段通常不做 packing，免得和线上单请求的分布错开。

## 追问

**position 连续编号有什么风险？**
模型可能学到「packed 后半段的位置总是很大」，和推理时单条短请求的位置分布对不上。

**和 gradient accumulation 是什么关系？**
两者互补，谁也替代不了谁。Packing 减少 pad，accumulation 用来凑大的 token batch。

**packing 能替代长上下文训练吗？**
不能。它用的是短样本留下的空位，提供不了跨样本的超长依赖。
