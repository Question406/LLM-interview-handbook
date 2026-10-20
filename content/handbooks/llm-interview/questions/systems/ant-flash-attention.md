---
id: ant-flash-attention
section: systems
order: 160
level: A
title: 蚂蚁：FlashAttention 原理是什么？
quick: >-
  瓶颈在把 $N\times N$ score 写回 HBM。FlashAttention 分块在 SRAM 里做 GEMM 和 online
  softmax，用行最大值与归一化和把各块结果合并，数学上精确，省的是 I/O，不是近似 attention。
tags:
  - Ant Group
  - FlashAttention
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 20260508蚂蚁集团大模型智能体优化算法一二面
    url: https://www.nowcoder.com/feed/main/detail/263bc804663b4a0aa7b312154d720817
    type: candidate-first-hand
  - title: FlashAttention
    url: https://arxiv.org/abs/2205.14135
    type: primary-paper
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型智能体优化算法
- 届别 / 流程：一面
- 面试时间：2026-05-08
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“Flash attention原理”**

常见误区是：「更快的近似注意力」，或者只说「算子融合」。先讲 I/O：标准实现把 $QK^\top$ 和 softmax 概率写入 HBM，长序列时读写远贵过 FLOPs。FlashAttention 在 SRAM 里分块做精确 softmax 合并，省的是 HBM 流量，数值上和标准 attention 等价。相关卡：`sys-flash`、`sys-online-softmax`、`baichuan-flash-attn`。

## 为什么 $N\times N$ 会打满带宽

Attention 是 $\mathrm{softmax}(QK^\top/\sqrt{d})V$。朴素 kernel 先写出 $N\times N$ score 再读回来做 softmax，再写概率、再读去乘 $V$。$N$ 到 4k-32k 时，这块中间矩阵主导显存与带宽，GPU 算力反而闲着。融合 GEMM 只能少几次 launch，减不掉必须落地的大矩阵。所以优化目标是「不要把完整 score 写回 HBM」，公式不用改。

## 分块 + online softmax 如何精确合并

把 $Q$ 按行块、$K/V$ 按列块搬进 SRAM。块内算 score 后，用 online softmax 维护该行已见过的最大值 $m$ 与归一化和 $\ell$。新块到来时，用 $\exp(m_{\mathrm{old}}-m_{\mathrm{new}})$ 重标旧的分子累计量再合并，最后除以 $\ell$。这和一次性 softmax 代数等价，不是 top-$k$ 或稀疏近似。反向常用 recompute：不存完整 attention 矩阵，利用前向统计量重新计算，以额外计算换取显存节省。美团面经里「分块后还要把 softmax 聚合」指的就是 $m,\ell$ 合并。

## 和 PagedAttention / 量化不是一层

FlashAttention 解决单步算子的 I/O；PagedAttention 解决 KV cache 的分页与碎片，见 `ant-vllm-paged`。短序列或已经算力打满、瓶颈在通信时，加速可能接近零，别背一个全球倍数。causal mask 在块内用局部 mask 实现，不会因此变成近似。记住三点：精确、IO-aware、online softmax；不是 Linformer / Reformer 那类近似。

## 追问

- **为什么说精确？** 块间用 $m,\ell$ 做等价重标，结果与标准 softmax 一致（忽略浮点顺序）。
- **反向为什么还能省显存？** 不存 $N\times N$ 概率，用 checkpoint / recompute 换计算。
- **FA2 / FA3 还改了什么？** 更好的并行切分与 warp 调度，目标仍是吞吐，不是改数学。
- **能替代梯度检查点吗？** 不能完全替代。它省 attention 中间项；MLP 激活仍可能要 checkpoint。
