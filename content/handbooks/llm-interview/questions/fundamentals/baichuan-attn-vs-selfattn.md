---
id: baichuan-attn-vs-selfattn
section: fundamentals
order: 181
level: B
title: 百川智能：最早机器翻译的 Attention 和 Self-Attention 的 QKV 各从哪来？
quick: >-
  我会先分三种。经典 seq2seq Attention：$Q$ 来自解码器当前状态，$K,V$ 来自编码器全部隐状态。Self-Attention
  的 $Q,K,V$ 都从同一序列线性投影得到。Cross-Attention 则是解码器 $Q$、编码器 $K,V$。
tags:
  - Baichuan
  - Attention
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3
    type: candidate-first-hand
  - title: Neural Machine Translation by Jointly Learning to Align and Translate
    url: https://arxiv.org/abs/1409.0473
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你知道最早的 attention 做机器翻译，它的注意力怎么得的吗？”**；**“这个 attention 和 self attention 的 QKV 怎么来的？”**

错法：所有注意力都画成 Transformer 的 $Q,K,V$ 三投影。Bahdanau / Luong 时代的 seq2seq 没有「三个同型矩阵都乘在同一条序列上」。先画一张来源表，再写公式。缩放点积见 `meituan-attention-scale-dk`；矩阵形状见 `ali-attention-math`；手写实现见 `pdd-attention-handwrite`。

## 经典对齐注意力

编码器把源句变成隐状态序列 $h_1,\ldots,h_S$。解码到第 $t$ 步，用当前解码状态 $s_t$ 对每个 $h_j$ 打分，例如 Bahdanau 的加性

$$
e_{tj}=v^\top\tanh(W_s s_t+W_h h_j),\qquad
\alpha_{tj}=\mathrm{softmax}_j(e_{tj}),\qquad
c_t=\sum_j\alpha_{tj}h_j.
$$

对应关系：$s_t$ 扮演 query，$h_j$ 同时提供 key（打分）与 value（加权求和）。Luong 可用点积 $s_t^\top h_j$。这里没有 $W_Q,W_K,W_V$ 三套同型投影，也没有自注意力的因果 mask。

## Self-Attention 与 Cross-Attention

Transformer 对同一矩阵 $X$ 做 $Q=XW_Q$、$K=XW_K$、$V=XW_V$，再 $\mathrm{softmax}(QK^\top/\sqrt{d_k})V$。Encoder 自注意力无因果 mask；Decoder 自注意力加因果 mask，防止看见未来目标词。Encoder-Decoder 的 cross-attention：$Q$ 来自目标侧（解码器层输出），$K,V$ 来自源侧（编码器输出）。Decoder 一层里通常是「masked self-attn → cross-attn → FFN」。

机器翻译对齐就是解码状态去查源端记忆；self-attn 是序列内部互相查；cross-attn 是目标查源。不要把 2014 的加性注意力硬说成 2017 的 scaled dot-product。

## 面试画一张来源表就够用

| 机制 | Query 从哪来 | Key / Value 从哪来 | Mask |
| --- | --- | --- | --- |
| Bahdanau / Luong | 解码器当前 $s_t$ | 编码器全部 $h_j$ | 无因果；源端全可见 |
| Encoder self-attn | 源序列 $X$ 的投影 | 同一 $X$ 的投影 | 通常无因果 |
| Decoder self-attn | 目标序列已生成部分 | 同一目标序列 | 因果 mask |
| Cross-attn | 解码器层输出 | 编码器输出 | 源端全可见 |

「最早做机器翻译的 attention」指的是上表第一行：用对齐权重读源端记忆，缓解固定向量瓶颈。当时常见实现是加性或点积，不一定出现名为 $W_Q,W_K,W_V$ 的三个同型矩阵。Self-attention 把「查别人」改成「序列内部互查」，这才需要三套投影把同一 $X$ 映射到不同空间，否则 $Q$ 和 $K$ 用同一向量，表达力受限。Cross-attention 则是把 MT 对齐重新嵌进 Transformer 层里：目标侧发问，源侧提供记忆。

缩放 $\sqrt{d_k}$ 是点积注意力的数值问题，加性注意力不靠它，不要在 Bahdanau 那一问里硬塞进去（留给 `meituan-attention-scale-dk`）。Decoder 因果 mask 的原因也很具体：teacher forcing 时未来词已在输入里，不 mask 等于作弊。要是追问「QKV 到底是向量还是矩阵」：角色是向量，$W_Q,W_K,W_V$ 是把隐状态映到该角色的线性层；经典 MT 里 query 常常就是 $s_t$ 本身或经过一层 $W_s$，不一定三套同型。Self-attention 为了让同一位置既当提问者又当被查对象，才需要三套投影把空间拆开。画完表再写一行公式，比背 2014 与 2017 两个年份更稳。

## 追问

- **最早的 Attention 有 QKV 吗？** 概念上有 query/key/value 角色，实现上往往是 $s_t$ 与 $h_j$，不是三套同型 $W$。可以说「角色有、矩阵不一定有」。
- **Decoder 为什么要因果 mask？** 训练时目标序列已知，不 mask 会泄漏 $t+1$ 及以后的词。推理时本来也看不到未来，训练必须匹配。
- **和 $\sqrt{d_k}$ 的关系？** 缩放是点积注意力的数值稳定，Bahdanau 加性注意力不靠这一项。
- **Self 和 Cross 能否同层？** 标准 Encoder-Decoder Transformer 的 decoder 层就是 masked self 再 cross。Encoder-only（BERT）没有 cross；Decoder-only（GPT）用自注意力加因果，把「源」也拼进同一序列时靠内容而不是单独 cross 模块。
- **Luong 和 Bahdanau 差在哪？** 打分函数：点积 / 双线性 vs 加性 MLP；query 仍是 $s_t$，key/value 仍是 $h_j$。
