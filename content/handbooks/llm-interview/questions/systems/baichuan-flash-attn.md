---
id: baichuan-flash-attn
section: systems
order: 165
level: A
title: 百川智能：FlashAttention 是什么，能提多少性能？
quick: >-
  它是 IO 感知的精确 attention：分块加 online softmax，少写 HBM。
  加速取决于序列长度、以及是不是已经算力打满。长序列收益大，短序列可能几乎没有提升，不能用一个固定倍数概括。
tags:
  - Baichuan
  - FlashAttention
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3
    type: candidate-first-hand
  - title: FlashAttention
    url: https://arxiv.org/abs/2205.14135
    type: primary-paper
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你知道 flask attention 吗？”**（现场口误，指 FlashAttention）；**“能有多大的性能提升吗？”**

百川这题常带着口误「flask attention」，先确认是 FlashAttention，别纠正语气。常见误区是：背「快 10 倍」，或把它说成近似注意力。原理和蚂蚁卡相同：SRAM 分块、online softmax 精确合并，省 HBM 而不是改公式。第二问要答「何时快」，而不是虚构全球倍数。同面还追过 encoder-decoder 里 $Q$ 与 $K/V$ 来源，要能顺口接上。相关卡：`ant-flash-attention`、`sys-flash`。

## 它是什么：IO-aware 的精确 attention

朴素实现把 $N\times N$ score 写回 HBM。FlashAttention 把 $Q$ 行块和 $K/V$ 列块搬进 SRAM，块内 GEMM，用行最大 $m$ 与归一化和 $\ell$ 做 online softmax，新块用 $\exp(\Delta m)$ 重标再合并。数学上与标准 softmax 等价。反向重算中间项换显存。不要答成 Linformer / Reformer。

## 「能提多少」取决于是不是 I/O 瓶颈

官方与实践常见：长序列上实际耗时数倍、attention 显存大幅下降；短 seq、已经融合的 kernel、或瓶颈在 TP/PP 通信、优化器、数据加载时，提升接近零甚至为负（额外 kernel 约束）。正确答法：先问序列长度、是否训练还是 逐 token 生成（decode）、GPU 代数。训练长上下文收益大；decode 单步 $N$ 虽增但还受 KV 读写和 batch 调度影响，不能把训练论文数字直接当推理 SLA。同一面若追「和 GQA 一起开」，可以说：GQA 降 KV 体积，FA 降 attention 中间 I/O，正交。给区间和条件，不给一个倍数。

## 顺手接上 cross-attn

最早 attention 论文里，decoder 的 $Q$ 来自当前层，encoder 的 $K/V$ 来自编码器输出，形状可以是 $N_{\mathrm{tgt}}\times N_{\mathrm{src}}$；self-attn 则 $Q,K,V$ 同源。FlashAttention 对这两种都能做，只要能分块。别把「Flash」和「GQA / MLA 省 KV」混为一谈：后者改的是头结构，前者改的是实现。

## 追问

- **为什么短序列没感觉？** 中间矩阵不大，HBM 不是瓶颈，FLOPs 或 launch 开销主导。
- **和 PagedAttention？** 一个省算子 I/O，一个分页管理 KV；推理栈里常同时出现。
- **一定开 FA 吗？** 不支持的头或 mask 形态要退回标准实现；先看正确性再谈速度。
- **如何自己量？** 固定模型与 batch，扫 $N$，看 attention kernel 时间占比和 tokens/s，不要只看官方 blog。
