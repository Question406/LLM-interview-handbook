---
id: infra-megatron-mlp-tp
section: systems
order: 243
level: A
title: AI Infra 实习：Megatron TP 切 MLP 时，两个矩阵怎么切、通信是什么？
quick: >-
  第一层（up/gate）列切，各卡算部分隐层，中间不必 all-gather。第二层（down）行切，局部乘完
  all-reduce（或 reduce-scatter）得到完整输出。一套 MLP 前向通常一次跨 TP 通信。Attention
  $QKV$ 列切、$O$ 行切是同一套路。
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

错法：把行切列切说反，或每层都报一次 all-gather。Megatron MLP 的关键是列切再行切，让中间激活沿隐层切开、两层之间不必 gather 完整 $h'$，一套前向通常只需一次跨 TP 归约。先把这一层讲清，再提 veRL 里训练 TP 与 vLLM TP 可以不同。相关卡：`sys-parallel`、`baichuan-pretrain-parallel`、`sys-verl-hybridengine`。

## 记两个矩阵：$W_1$ 列切，$W_2$ 行切

记 $h'=W_1 x$、$y=W_2 h'$（SwiGLU 则 $W_1$ 含 gate/up）。列切 $W_1$：每卡持有 $h'$ 的一块，激活沿隐层切开，输入 $x$ 需在 TP 组内一致（进入 MLP 前通常已是完整向量）。中间不必 all-gather。行切 $W_2$：每卡用自己那块 $h'$ 乘对应行块，得到一份不完整的 $y$ 贡献，再对 $y$ 做 all-reduce（序列并行时常是 reduce-scatter）。这样 $W_2$ 的行划分恰好吃掉 $W_1$ 的列划分，避免把宽隐层在卡间复制一份。反向通信方向对调：前向 all-reduce 对应反向对输入梯度的 split/identity 模式，按 Megatron 论文的 column/row parallel linear 配对。

## 通信次数与 Attention 同构

一套 MLP 前向通常一次跨 TP 通信（输出上的 reduce），不是每个 GEMM 都 all-gather。Attention 是同一套路：$QKV$ 列切、$O$ 行切，输出再 reduce。面试若被追 SwiGLU：gate 与 up 都列切，SiLU 在分片隐层上局部做，再点乘，然后进行切的 down。不要把 ZeRO 的参数 gather 说成 TP 通信，那是另一套。veRL 用 Megatron 当 actor 时，**训练 TP** 和 **vLLM TP** 不必相等，差集靠 HybridEngine reshard；先讲清 MLP 前向，再提 reshard，不要一上来画 3D 并行。把「列切 / 行切」画成 $x$ 完整、$h'$ 分片、$y$ 再还原，比背算子名更不容易说反。

## 追问

- **为什么不是两层都列切？** 两层都列切会在中间强制 all-gather 完整 $h'$，带宽更差。
- **all-reduce 和 reduce-scatter 何时换？** 后面若接序列并行 / 把输出再切开，常用 reduce-scatter + all-gather 配对，总量仍是一次归约语义。
- **bias 放哪？** 列并行线性的 bias 只在一档上加，避免重复加；行并行输出在 reduce 之后加。
- **和专家并行？** EP 是 token all-to-all；TP 是矩阵切分。MoE 层里两者可叠，但通信模式不同。
