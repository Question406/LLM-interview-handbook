---
id: ant-flash-attention
section: systems
order: 160
level: A
title: 蚂蚁：FlashAttention 原理是什么？
quick: "标准 attention 的瓶颈在把 $N\\times N$ score 写回 HBM。FlashAttention 在 SRAM 里分块做 GEMM 和 online softmax，用行最大值和归一化和把各块结果合并，数学上是精确的；它省的是 I/O，attention 本身没有近似。"
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

FlashAttention 是一种 IO-aware 的精确 attention：它把 $Q$、$K$、$V$ 分块搬进 SRAM，在片上用 online softmax 把各块结果精确合并，这样完整的 $N\times N$ score 就不用写回 HBM。它省的是 HBM 流量，数值上和标准 attention 等价。把它说成「更快的近似注意力」或者只说「算子融合」，都没讲到原理。

先说为什么 $N\times N$ 会打满带宽。Attention 是 $\mathrm{softmax}(QK^\top/\sqrt{d})V$。标准实现会把 $QK^\top$ 和 softmax 概率都写入 HBM：朴素的 kernel 先写出 $N\times N$ 的 score，再读回来做 softmax，写出概率，再读回去乘 $V$。$N$ 到 4k-32k 时，这块中间矩阵主导了显存和带宽，GPU 的算力却闲着，长序列下读写远比 FLOPs 贵。融合 GEMM 只能少几次 launch，必须落地的那个大矩阵还在。所以优化目标是别把完整的 score 写回 HBM，公式本身不用动。

具体做法是把 $Q$ 按行块、$K/V$ 按列块搬进 SRAM。块内算完 score，用 online softmax 维护这一行目前见过的最大值 $m$ 和归一化和 $\ell$。新块进来时，先用 $\exp(m_{\mathrm{old}}-m_{\mathrm{new}})$ 把旧的分子累计量重新缩放，再合并，最后除以 $\ell$。这和一次性算 softmax 在代数上等价，跟 top-$k$ 或稀疏近似没关系。反向常用 recompute：不存完整的 attention 矩阵，用前向留下的统计量重新算，拿额外的计算换显存。美团面经里说的「分块后还要把 softmax 聚合」，指的就是 $m,\ell$ 的合并。causal mask 在块内用局部 mask 实现，结果也不会因此变成近似。

还要分清它和别的优化不在一层。FlashAttention 解决单步算子的 I/O；PagedAttention 解决 KV cache 的分页和碎片，见 `ant-vllm-paged`。短序列，或者算力已经打满、瓶颈在通信时，加速可能接近零，所以别背一个通用的倍数。总结起来就是三点：精确、IO-aware、online softmax；和 Linformer、Reformer 那类近似方法是两回事。

## 追问

**为什么说它是精确的？**
块和块之间用 $m,\ell$ 做等价的重新缩放，结果和标准 softmax 一致，只有浮点累加顺序上的差别。

**反向为什么也能省显存？**
不存 $N\times N$ 的概率矩阵，用 checkpoint / recompute 拿计算换显存。

**FA2、FA3 又改了什么？**
更好的并行切分和 warp 调度，目标是吞吐，数学没变。

**它能替代梯度检查点吗？**
不能完全替代。它省的是 attention 的中间项，MLP 的激活可能还得 checkpoint。

相关：`sys-flash`、`sys-online-softmax`、`baichuan-flash-attn`
