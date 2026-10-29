---
id: baichuan-flash-attn
section: systems
order: 165
level: A
title: 百川智能：FlashAttention 是什么，能提多少性能？
quick: >-
  普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。FlashAttention
  将计算分块，并在更快的片上存储里组织中间结果，减少这些往返。
tags:
  - Baichuan
  - FlashAttention
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 百川智能大模型实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/290832d2cd3242c386e56f27f975bce3'
    type: candidate-first-hand
  - title: FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary-paper
---

## 回答思路

> **问题与场景：** 普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。
>
> **做法与原因：** Online softmax 让分块计算仍能组合成同一个 attention 结果；这不是把 attention 改成稀疏近似，也不意味着所有二次计算都消失。
>
> **检查与取舍：** 我会按序列长度、head dimension、dtype 和硬件测耗时与显存，并检查输出及 gradients。

## 可以这样回答

普通 attention 可能把很大的 score matrix 写入显存，再读回来做 softmax。FlashAttention 将计算分块，并在更快的片上存储里组织中间结果，减少这些往返。

Online softmax 让分块计算仍能组合成同一个 attention 结果；这不是把 attention 改成稀疏近似，也不意味着所有二次计算都消失。浮点执行顺序不同，结果可能有数值误差。

我会按序列长度、head dimension、dtype 和硬件测耗时与显存，并检查输出及 gradients。速度提升依赖具体工作负载，不能背一个固定倍数。

## 技术备查

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“你知道 flask attention 吗？”**（现场口误，指 FlashAttention）；**“能有多大的性能提升吗？”**

FlashAttention 是 IO-aware 的精确 attention，它能提多少性能取决于 attention 是不是 I/O 瓶颈：长序列训练收益大，短序列可能接近零。我会先给条件和区间，不背「快 10 倍」这种固定倍数。这题面试官常带着口误说「flask attention」，先确认指的是 FlashAttention 就行，不用去纠正。

原理和蚂蚁那张卡一样。朴素实现把 $N\times N$ 的 score 写回 HBM；FlashAttention 把 $Q$ 的行块和 $K/V$ 的列块搬进 SRAM，块内做 GEMM，用行最大值 $m$ 和 normalization 和 $\ell$ 做 online softmax，新块进来时用 $\exp(\Delta m)$ 把旧结果重新缩放再合并。数学上和标准 softmax 等价，反向靠重算中间项换显存。它和 Linformer、Reformer 那种近似方法是两回事。

第二问「能提多少」，关键看瓶颈在哪。官方和实践里常见的是，长序列上实际耗时快好几倍，attention 显存大幅下降；可如果序列短、kernel 已经融合过，或者瓶颈在 TP/PP 通信、优化器、数据加载，提升会接近零，甚至因为额外的 kernel 约束变成负的。所以我会先反问三件事：序列多长，是训练还是逐 token 生成（decode），GPU 是哪一代。训练长上下文收益最大；decode 时单步的 $N$ 虽然变大，但还受 KV 读写和 batch 调度影响，训练论文里的数字不能直接当推理 SLA。要是同一面追问「和 GQA 一起开怎么样」，可以说两者正交：GQA 降的是 KV 的体积，FA 降的是 attention 中间结果的 I/O。

同一场面试还追问过 encoder-decoder 里 $Q$ 和 $K/V$ 从哪来，最好能顺口接上。最早的 attention 论文里，decoder 的 $Q$ 来自当前层，$K/V$ 来自 encoder 的输出，score 的形状是 $N_{\mathrm{tgt}}\times N_{\mathrm{src}}$；self-attn 的 $Q,K,V$ 同源。只要能分块，FlashAttention 两种都能做。也别把它和 GQA、MLA 省 KV 混为一谈：后者改的是头的结构，FlashAttention 改的是实现。

## 追问

**为什么短序列感觉不到加速？**
中间矩阵不大，HBM 不是瓶颈，主导的是 FLOPs 或 launch 开销。

**和 PagedAttention 什么关系？**
一个省算子的 I/O，一个分页管理 KV，推理栈里常常同时出现。

**是不是一定要开 FA？**
不一定。有些头的形态或 mask 不支持，要退回标准实现；先保证正确，再谈速度。

**自己怎么量？**
固定模型和 batch，扫 $N$，看 attention kernel 的时间占比和 tokens/s，别只看官方 blog。

相关：`ant-flash-attention`、`sys-flash`
