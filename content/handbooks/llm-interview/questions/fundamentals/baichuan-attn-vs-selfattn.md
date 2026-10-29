---
id: baichuan-attn-vs-selfattn
section: fundamentals
order: 181
level: B
title: 百川智能：最早机器翻译的 Attention 和 Self-Attention 的 QKV 各从哪来？
quick: >-
  分三种说。最早做机器翻译的 seq2seq Attention 里，$Q$ 是 decoding 器当前状态 $s_t$，$K,V$ 都是编码器的全部隐状态
  $h_j$，用加性或点积打分，不一定有三套同型投影；Self-Attention 的 $Q,K,V$
  由同一条序列各乘一个投影矩阵得到；Cross-Attention 是 decoding 器出 $Q$、编码器出 $K,V$。
tags:
  - Baichuan
  - Attention
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3'
    type: candidate-first-hand
  - title: Neural Machine Translation by Jointly Learning to Align and Translate
    url: 'https://arxiv.org/abs/1409.0473'
    type: primary
  - title: Attention Is All You Need
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你知道最早的 attention 做机器翻译，它的 attention 怎么得的吗？”**；**“这个 attention 和 self attention 的 QKV 怎么来的？”**

分三种来说。最早做机器翻译的 Attention（Bahdanau / Luong）里，query 是 decoding 器当前的状态 $s_t$，key 和 value 都是编码器的全部隐状态 $h_j$；Self-Attention 的 $Q,K,V$ 是同一条序列分别乘三个投影矩阵得到的；Cross-Attention 是 decoding 器出 $Q$、编码器出 $K,V$。这题最常见的错，是把所有 attention 都画成 Transformer 的 $Q,K,V$ 三投影，Bahdanau / Luong 时代的 seq2seq 没有「三个同型矩阵都乘在同一条序列上」。

先讲经典的对齐 attention。编码器把源句变成隐状态序列 $h_1,\ldots,h_S$。decoding 到第 $t$ 步时，用当前 decoding 状态 $s_t$ 给每个 $h_j$ 打分，比如 Bahdanau 的加性打分：

$$
e_{tj}=v^\top\tanh(W_s s_t+W_h h_j),\qquad
\alpha_{tj}=\mathrm{softmax}_j(e_{tj}),\qquad
c_t=\sum_j\alpha_{tj}h_j.
$$

这里 $s_t$ 扮演 query，$h_j$ 同时提供 key（用来打分）和 value（用来加权求和），Luong 可以直接用点积 $s_t^\top h_j$。比如把「我爱你」翻成 "I love you"，生成 "love" 那一步，$s_t$ 去和三个源端隐状态打分，「爱」那个位置的权重最大，上下文向量 $c_t$ 主要由它构成。这样 decoding 时每一步都能回头读源端记忆，缓解了把整句压进一个固定向量的瓶颈。这里没有 $W_Q,W_K,W_V$ 三套同型投影，也没有 self-attention 的因果 mask，query 常常就是 $s_t$ 本身，或者过一层 $W_s$。所以被问「它有没有 QKV」，我会说：角色有，矩阵不一定有。

再讲 Transformer。对同一矩阵 $X$ 做 $Q=XW_Q$、$K=XW_K$、$V=XW_V$，再算 $\mathrm{softmax}(QK^\top/\sqrt{d_k})V$。Self-attention 是序列内部互相查，同一个位置既当提问者又当被查的对象，所以需要三套投影把它映到不同的空间，要是 $Q$ 和 $K$ 用同一个向量，表达力会受限。QKV 的角色是向量，$W_Q,W_K,W_V$ 是把隐状态映到这些角色上的线性层。Encoder self-attention 没有因果 mask；Decoder self-attention 加因果 mask，因为 teacher forcing 时未来的目标词已经在输入里了，不 mask 等于作弊。Cross-attention 把机器翻译的对齐重新嵌进 Transformer 层里：$Q$ 来自目标侧（decoding 器层输出），$K,V$ 来自源侧（编码器输出）。Decoder 的一层通常是「masked self-attn → cross-attn → FFN」。

面试时画一张来源表就够用：

| 机制 | Query 从哪来 | Key / Value 从哪来 | Mask |
| --- | --- | --- | --- |
| Bahdanau / Luong | decoding 器当前 $s_t$ | 编码器全部 $h_j$ | 无因果；源端全可见 |
| Encoder self-attn | 源序列 $X$ 的投影 | 同一 $X$ 的投影 | 通常无因果 |
| Decoder self-attn | 目标序列已生成部分 | 同一目标序列 | 因果 mask |
| Cross-attn | decoding 器层输出 | 编码器输出 | 源端全可见 |

「最早做机器翻译的 attention」指的是第一行。别把 2014 年的加性 attention 硬说成 2017 年的 scaled dot-product：缩放 $\sqrt{d_k}$ 是点积 attention 的数值稳定问题，加性 attention 不靠这一项，Bahdanau 那一问里不用硬塞进去（留给 `meituan-attention-scale-dk`）。画完表再写一行公式，比背两个年份更稳。矩阵形状见 `ali-attention-math`，手写实现见 `pdd-attention-handwrite`。

## 追问

**最早的 Attention 有 QKV 吗？**
概念上有 query / key / value 的角色，实现上往往就是 $s_t$ 和 $h_j$，没有三套同型的 $W$。

**Decoder 为什么要因果 mask？**
训练时目标序列已知，不 mask 会泄漏 $t+1$ 及以后的词。推理时本来就看不到未来，训练要和它匹配。

**Self 和 Cross 能在同一层吗？**
能。标准 Encoder-Decoder Transformer 的 decoder 层就是先 masked self 再 cross。Encoder-only（BERT）没有 cross；Decoder-only（GPT）用带因果的 self-attention，把「源」也拼进同一条序列时靠内容区分，没有单独的 cross 模块。

**Luong 和 Bahdanau 差在哪？**
差在打分函数：点积 / 双线性对加性 MLP。query 都是 $s_t$，key / value 都是 $h_j$。
