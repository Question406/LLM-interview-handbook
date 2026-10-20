---
id: sys-context-parallel
section: systems
order: 13
level: S
title: 系统：context parallel 长上下文，ring 传 KV
quick: >-
  Megatron CP 把整段 $T$ 切开，Q 留本地，KV 沿环一块块传，用在线 softmax 拼出完整注意力。和 Megatron SP
  不是一回事：SP 只砍 LN/dropout 的复制，注意力仍要完整序列。因果 mask 要 zigzag，否则后段卡算得多。
tags:
  - NVIDIA
  - Megatron
  - Context Parallel
  - Ring Attention
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: https://arxiv.org/abs/2310.01889
    type: primary
  - title: Context Parallel Overview — Megatron Core
    url: https://docs.nvidia.com/megatron-core/developer-guide/nightly/user-guide/features/context_parallel.html
    type: secondary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

NVIDIA Megatron Core 的 `context_parallel_size`、Ring Attention、长上下文预训练都会问：单卡装不下 $T$ 时注意力怎么切。名字容易和 `sys-seq-parallel` 撞车。先划清：Megatron SP 是 TP 的配套布局，LN / dropout 按 $T$ 切开，进列并行前仍 all-gather 完整序列；CP 切的是注意力本身，Q 分段驻留，KV 在 CP 组里搬家。四维切分里 CP 和 TP/PP/DP 怎么配，见 `sys-3d-parallel`；超长序列还要结合哪些优化，见 `sys-overlong`。

NVIDIA 岗还会追因果 mask 下环是否负载均衡、KV 交换能不能和 Flash kernel overlap。不提 zigzag 和 overlap，评委会当只背过名词。

## Q 不动，KV 沿环走

注意力要每个 query 看见整段 KV。CP 度为 $P$ 时，每卡只持有 $[B, T/P, h]$ 的 Q/K/V。朴素做法是 all-gather 全部 KV，显存又回到完整 $T$，CP 白开。Ring Attention / Megatron 的 p2p CP：Q 留在本卡，把本地 KV 块发给邻居、收下上一跳的块，对当前块做一次局部注意力，用在线 softmax 累加分子和分母。转 $P-1$ 圈后，每个 query 都见过全部 KV，本卡始终只存一块 KV 工作区。

每卡搬运大约 $(P-1)\cdot(T/P)\cdot 2\cdot n_{\mathrm{kv}}\cdot d_h$ 量级（K 和 V），$P$ 大时接近一份完整 KV。GQA / MQA 让 $n_{\mathrm{kv}}$ 远小于查询头，环上体积跟着降，这是长上下文爱 GQA 的系统理由之一。通信是点对点、可和当前块的 attention kernel overlap； Megatron 文档写明 p2p 能叠，`all_gather` 模式拿齐再算、叠不上。

和 TP 正交：CP 组是「同一套 TP 坐标、不同序列块」的那些卡。总卡数 $\mathrm{TP}\times\mathrm{CP}\times\mathrm{PP}\times\mathrm{DP}$。KV 交换发生在不同 TP 组的对应 rank 之间。节点内优先 NVLink；跨 IB 做大 CP，环上每跳延迟会翻出来。层次做法是节点内 all-to-all、跨节点再 ring，见 `sys-ulysses`。

## 因果 mask 会导致环上负载不均

Decoder 下，靠前的 query 合法 KV 短，靠后的长。按连续切片排环，末段那张卡每圈都在算大块，前面的卡很闲，step time 等于最忙的那张。Megatron CP 把序列切成 $2P$ 块，让每卡同时拿一块靠前、一块靠后（zigzag / load-balanced），有用的 FLOPs 拉齐。面试不提负载均衡，评委会以为你只看过环的示意图。

Flash / cuDNN 注意力可以按块喂，不必自己写 $T\times T$ 分数矩阵。CP 省的是激活和 KV 工作区，不是把 $O(T^2)$ 的 FLOPs 变没；总计算仍在，只是摊到 $P$ 张卡。checkpoint 仍然要，见 `sys-act-checkpoint`。不要说「开了 CP 就可以关 SP」：SP 处理的是 TP 复制的 LN 激活，CP 处理的是注意力的序列轴，长上下文经常两件一起开。

一个数量级：$T=128\mathrm{k}$，$P=8$，BF16，GQA 下 $n_{\mathrm{kv}}=8$、$d_h=128$。每卡驻留 $16\mathrm{k}$ 个 token 的 KV；环上转 7 圈，每圈搬一块，总量接近一份完整 KV，大约 $2\cdot 128\mathrm{k}\cdot 8\cdot 128\cdot 2$ 字节量级，百 MB 而不是 GB。若改 all-gather 齐再算，HBM 峰值回到完整 $T$ 的 KV，CP 的显存意义没了。Nsight 上若 p2p 和 attention kernel 串行，就是通信墙，不是「环传很便宜」。

反向对称：对 KV 的梯度沿环 reduce，Q 的梯度留本地。通信体积仍是 KV 块量级，同样要和本地 dgrad overlap。GQA 让反向也变轻。和 PP 叠时，每个 stage 内部自己环；不要让 CP 环跨过 pipeline 边界，否则 P2P 激活和 KV 环抢同一条 IB。

错误说法：CP 等于把 batch 切开（那是 DP）；环传的是 Q（Q 本地才对，传 Q 体积还随头数更大）；不 overlap 也能当免费的。

推理侧不要把训练环原样搬到逐 token 生成（decode）：在线 batch 不齐、$T$ 每步在涨，环的负载均衡假设不再成立。Serving 更常是分页 KV、分块输入预填充（chunked prefill） 或 PD 分离。训练 CP 解决的是「单卡装不下这一条长序列的注意力工作区」。

## 追问

- **和 Megatron SP 一句话差在哪？** SP 改 LN/dropout 布局，注意力仍要完整 $T$。CP 切注意力的 $T$，通信是 KV 块。
- **为什么环传 KV 不传 Q？** 每个 query 只需见全部 KV；Q 分片留本地。GQA 下 KV 更窄，传 KV 更划算。
- **P 能不能大于头数？** Ring / p2p 可以，不受头数整除约束。Ulysses 式 all-to-all 要把头切开，头不够就拆不动，见 `sys-ulysses`。
- **decode 也用训练这套环吗？** 训练 prefill 形状齐、好环。在线 decode 每步 $T$ 在涨、batch 不齐，serving 更常是分页 KV 和分离部署，见 `sys-paged-attn`、`sys-prefill-decode-disagg`。
- **和 PP 的环会打架吗？** CP 环应停在 stage 内。跨 stage 会和 pipeline P2P 抢链路。
- **GQA 对环体积意味着什么？** $n_{\mathrm{kv}}$ 下降，环上字节线性降。长上下文爱 GQA 的系统理由之一。
- **不 overlap 还能开 CP 吗？** 能装下更长 $T$，但实际耗时可能更差。Nsight 上环和 kernel 串行就是以通信开销换取更低的显存占用。
