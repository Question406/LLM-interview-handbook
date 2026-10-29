---
id: sys-ulysses
section: systems
order: 14
level: A
title: 系统：DeepSpeed Ulysses all-to-all 切序列，和 Megatron SP
quick: >-
  Ulysses 先沿 $T$ 分片，再用 all-to-all 临时换成完整序列、部分 attention 头，算完换回去，通信量按 $N/P$
  分摊。Megatron SP 主要减少 TP 中 LN 等激活的复制；GQA 头数少时，Ulysses 还会受可切头数限制。
tags:
  - Microsoft
  - DeepSpeed
  - Sequence Parallel
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: >-
      DeepSpeed Ulysses — System Optimizations for Enabling Training of Extreme
      Long Sequence Transformer Models
    url: 'https://arxiv.org/abs/2309.14509'
    type: primary
  - title: DeepSpeed-Ulysses blog (DeepSpeed)
    url: >-
      https://github.com/deepspeedai/DeepSpeed/blob/master/blogs/deepspeed-ulysses/README.md
    type: secondary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: 'https://arxiv.org/abs/2205.05198'
    type: primary
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: 'https://arxiv.org/abs/2310.01889'
    type: primary
---

Ulysses 把整网的序列激活分片，attention 前用 all-to-all 临时换成「完整序列、部分头」，算完再换回去。它与 Megatron SP、context parallel / ring 的布局不同，讨论 sequence parallel 时先明确指的是哪一种。Ulysses 论文指出，序列长度 $N$ 和设备数 $P$ 同比增加时，每条链路的通信体积可以保持常数；但 GQA 的 KV 头较少，会限制可用并行度。

## attention 前后怎么换布局

两次 all-to-all 完成序列切分 $\leftrightarrow$ 头切分的转换。

输入按序列维切开，每卡 $[B, T/P, h]$。MLP、LN 都在这段局部序列上算，激活随 $P$ 降。attention 是 token 之间的算子，局部 $T/P$ 不够。Ulysses 用 **all-to-all 换轴**，不环传 KV：

1. 对 Q/K/V 做 all-to-all：每卡从「一段序列、全部头」变成「完整 $T$、大约 $H/P$ 个头」。
2. 本地对这子集头做完整序列的 attention（可接 FlashAttention）。
3. 再一次 all-to-all，把输出拧回「一段序列、全部头」，交给 MLP。

论文把 QKV 三次 all-to-all 加输出一次，合计大约 $4Nh/P$ 每层每卡（$h$ 是 hidden）。$N$ 和 $P$ 一起加倍，每卡字节量不变。这和 ring 每卡搬接近一份完整 KV 的账不同：Ulysses 吃的是 all-to-all 的双分带宽，ring 吃的是点对点加 overlap。NVLink 域里 all-to-all 通常较高效；跨 IB、消息再碎，启动开销会翻出来。

并行度的上限由还能切开的 attention 头数决定。GQA 之后 KV 头本来就少，再叠 TP（TP 已经按头切了），留给 Ulysses 的头 $= H_{\mathrm{kv}}/\mathrm{TP}$，很快触顶。头不够还硬开，要么补 dummy 头浪费算力，要么改走 ring / CP。Megatron Core 的 `cp_comm_type` 现在也能选 `a2a`（Ulysses 味）或 `p2p`（环），以及节点内 a2a、跨节点 p2p 的层次组合。

## 与 Megatron SP 怎么配合

Megatron SP 绑死 TP 组：LN / dropout 按 $T/\mathrm{TP}$ 存，列并行前 all-gather 完整 $T$，行并行后 reduce-scatter。attention 在 TP rank 上仍是 **完整序列、本地那几头**（已经是头并行），并不是 Ulysses 那种先把序列拼齐。SP 解决的是 TP 复制激活，见 `sys-seq-parallel`。Ulysses 解决的是 **整网沿 $T$ 分片**，attention 用 all-to-all 临时换成头并行。

可以叠：节点内 TP + SP 走 Megatron 布局，另一组做 Ulysses 或 CP。不要对同一组又 SP 又 Ulysses 还以为通信会抵消。ZeRO 切的是 DP 维状态，碰不到这条序列轴，见 `sys-zero-stages`。

数量级：设 $T=128\mathrm{k}$，$P=8$，每卡只驻留 $16\mathrm{k}$ 的非 attention 激活；attention 窗口里每卡仍要看见完整 $128\mathrm{k}$ 的那几头，所以 Ulysses **不减少 attention FLOPs 的 $T^2$ 项**，只是把序列激活和通信摊开。Flash 已经不写 $T\times T$ 到 HBM，省的是分片后的残差 / MLP 中间结果。再长就要 ring，让 KV 工作区也不持有完整 $T$，见 `sys-overlong`。

从通信上对照，Megatron SP 的 all-gather / reduce-scatter 与原来层内 all-reduce 体积同阶，主要改变激活布局；Ulysses 的 all-to-all 按 $N/P$ 分摊，把 attention 临时换成头并行。Microsoft 语境中 sequence parallel 经常指 Ulysses，NVIDIA 语境中则经常指 SP，画并行组前先确认含义。万亿参数切分如何给 CP 留组，见 `sys-3d-parallel`。

形状上可以记：进入 attention 前 $[B, T/P, H, d_h]$ $\to$ all-to-all $\to$ $[B, T, H/P, d_h]$，出来再拧回去。GQA 时 K/V 的头维更窄，A2A 之后更容易出现 $H_{\mathrm{kv}}/P<1$。这时不要补假头硬撑，改 ring 或把 Ulysses 度数降到头数。节点内 A2A、跨节点 ring 的层次 CP，就是在躲这个整除墙。

相关：`sys-seq-parallel`、`sys-context-parallel`。

## 追问

**All-to-all 比 ring 一定快吗？**
头够、NVLink 域、消息大时经常更快。头不够或跨 IB，ring / 层次 CP 更稳。
**为什么 GQA 会卡住 Ulysses？**
A2A 之后每卡至少要有一头（KV 头更严）。GQA 加 TP 把可切的头砍光了。
**能替代 TP 吗？**
不能。Ulysses 不切层内矩阵。万亿 dense 仍要节点内 TP，见 `sys-3d-parallel`。
**和 DeepSpeed ZeRO 什么关系？**
正交。Ulysses 是序列维；ZeRO 是参数/梯度/优化器分片。长序列两者常一起开。
**A2A 之后每卡还要存完整 $T$ 的 KV 吗？**
对它分到的那几头，是的。所以 Ulysses 减的是非 attention 激活和通信摊销，不是把 attention 工作区降到 $T/P$。那一刀是 ring / CP。
**能和 Megatron SP 同一组吗？**
不建议。SP 已经在 TP 组里改布局；Ulysses 另开序列组。叠在同一组上通信会打架。
