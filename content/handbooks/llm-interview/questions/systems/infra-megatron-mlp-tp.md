---
id: infra-megatron-mlp-tp
section: systems
order: 243
level: A
title: AI Infra 实习：Megatron TP 切 MLP 时，两个矩阵怎么切、通信是什么？
quick: "第一层（up/gate）列切，每张卡算一部分隐层，中间不用 all-gather；第二层（down）行切，局部乘完再 all-reduce（或 reduce-scatter）得到完整输出。一套 MLP 前向通常只有一次跨 TP 通信，Attention 的 $QKV$ 列切、$O$ 行切也是同一个套路。"
tags:
  - Megatron
  - Tensor Parallel
  - RL Infra
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AI infra实习面经（小厂）
    url: https://www.nowcoder.com/feed/main/detail/166e576d5afa4a298cf9492ed51bed04
    type: candidate-first-hand
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary
---

## 真题记录

- 岗位：AI Infra 实习
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Megatron，tp是怎么切分的，mlp中第一个矩阵和第二个矩阵分别是行切还是列切，通信分别是什么算子”**

第一个矩阵列切，第二个矩阵行切，中间的激活沿隐层维度切开，两层之间不用 gather 完整的 $h'$；最后对输出做一次 all-reduce（序列并行时常是 reduce-scatter）。所以一套 MLP 前向通常只有一次跨 TP 的归约。最容易错的是把行切列切说反，或者每层都报一次 all-gather。

记两个式子：$h'=W_1 x$，$y=W_2 h'$，SwiGLU 的话 $W_1$ 里包含 gate 和 up。列切 $W_1$，每张卡持有 $h'$ 的一块，激活沿隐层切开；输入 $x$ 在 TP 组内要一致，进 MLP 之前它通常已经是完整的向量。中间不需要 all-gather。行切 $W_2$，每张卡拿自己那块 $h'$ 去乘 $W_2$ 对应的行块，得到 $y$ 的一份部分和，再对 $y$ 做 all-reduce。这样 $W_2$ 的行划分正好接住 $W_1$ 的列划分，宽隐层不用在卡间复制一份。我面试时会画成：$x$ 完整，$h'$ 分片，$y$ 再还原，这样比背算子名更不容易说反。

反向的通信方向对调：前向的 all-reduce 对应反向里对输入梯度的 split / identity 模式，按 Megatron 论文里 column / row parallel linear 的配对来。

Attention 是同一个套路：$QKV$ 列切，$O$ 行切，输出再做一次 reduce。如果被追问 SwiGLU：gate 和 up 都列切，SiLU 在分片的隐层上局部做，然后逐元素相乘，再做行切的 down 投影。别把 ZeRO 的参数 gather 说成 TP 通信，那是另一套机制。veRL 用 Megatron 当 actor 时，**训练 TP** 和 **vLLM TP** 不需要相等，差的部分靠 HybridEngine 去 reshard。我会先讲清 MLP 前向，再提 reshard，别一上来就画 3D 并行。

## 追问

**为什么不两层都列切？**
两层都列切，中间就得强制 all-gather 完整的 $h'$，带宽更差。

**all-reduce 什么时候换成 reduce-scatter？**
后面要接序列并行、把输出再切开时，常用 reduce-scatter 加 all-gather 配对，总量上仍然是一次归约的语义。

**bias 加在哪？**
列并行线性层的 bias 只在一份上加，避免重复；行并行的输出在 reduce 之后再加。

**和专家并行有什么不同？**
EP 对 token 做 all-to-all 通信，TP 是切矩阵。MoE 层里两者可以叠，但通信模式不同。

相关：`sys-parallel`、`baichuan-pretrain-parallel`、`sys-verl-hybridengine`
