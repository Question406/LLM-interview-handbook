---
id: arch-seq-packing
section: arch
order: 17
level: A
title: Sequence Packing 如何减少 Padding 浪费？
quick: >-
  把多个短样本拼到同一个固定长度 sequence 里，提高有效 token 比例；关键是 attention mask、position/segment
  boundary 和 loss mask 不能让不同样本互相泄漏。
tags:
  - Training
  - Packing
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: Fewer Truncations Improve Language Modeling
    url: https://arxiv.org/abs/2404.10830
    type: primary
---

陷阱是只说「拼在一起提高 GPU 利用率」，却不提 mask。例如 max length $4096$，四条 $800$-token 样本各自 pad 会浪费约八成位置；packing 后可以放进同一 sequence。若不做隔离，样本 A 的 token 会看见样本 B，因果 LM 变成串味的跨文档注意力，loss 数字好看、任务却脏。

## 必须对齐的三张 mask

注意力要用 block-diagonal 因果 mask（或 varlen / FlashAttention 的 cu_seqlens）：段内仍是下三角，段间全屏蔽。记段 $s$ 的区间为 $[a_s,b_s)$，则

$$
M_{ij}=\begin{cases}
0 & \text{同段且 } j\le i,\\
-\infty & \text{否则.}
\end{cases}
$$

RoPE 的 position id 可每段从 $0$ 重置，或沿 packed 序列连续编号，必须与模型实现一致；错了等于训练了一套推理对不上的相对位置 $R_i^\top R_j=R_{j-i}$。Loss mask 只在真实 token 上计 CE，padding 与段边界特殊符不计。文档级任务还要 segment id，防止把拼接当成长文。

## 吞吐涨了，统计口径会变

Packing 提高有效 token / 步，但「一个 batch 有多少样本」和「有多少 token」不再正比。梯度按 token 平均还是按 sequence 平均，会改变短样本权重。课程学习、温度、MoE 的 aux loss 若按 batch 内专家频率算，packed 后 token 来源更杂，负载统计要按真实 token 而不是按「条数」。SwiGLU FFN 的算力跟有效 token 走，padding 少了，MFU 才上去。

实现上优先用已有 varlen attention，而不是自己拼一个容易漏的 dense mask。评测阶段通常不 packing，避免和线上单请求分布错位。

## 追问

- **position 连续编号有什么风险？** 模型可能学会「packed 后半段总是很大位置」，和推理单条短请求的位置分布不一致。
- **和 gradient accumulation 什么关系？** Packing 减少 pad；accumulation 凑大 token batch。两者互补，不要互相替代。
- **packing 能替代长上下文训练吗？** 不能。它吃的是短样本空隙，不提供跨样本的超长依赖。
