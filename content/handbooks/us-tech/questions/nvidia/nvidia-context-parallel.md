---
id: nvidia-context-parallel
section: nvidia
order: 14
level: S
title: NVIDIA：context / sequence parallel 给长上下文，和 TP 的通信差
quick: >-
  长上下文要先分清切什么：TP 切层内权重，SP 切 LN、Dropout 等激活的序列维，CP 才把整网的序列维分到多卡。TP 每层通信约为 $[B, T,
  D]$ 量级，SP 用 reduce-scatter 和 all-gather 省重复激活；CP 的 attention 则交换 KV，体积跟
  $T\cdot H_{\mathrm{kv}}\cdot d_h$ 走。
tags:
  - NVIDIA
  - Context Parallel
  - Megatron
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: 'https://arxiv.org/abs/2205.05198'
    type: primary
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: 'https://arxiv.org/abs/2310.01889'
    type: primary
  - title: Context Parallelism — NVIDIA NeMo Framework User Guide
    url: >-
      https://docs.nvidia.com/nemo-framework/user-guide/25.11/longcontext/contextparallel.html
    type: secondary
  - title: NVIDIA Megatron-LM
    url: 'https://github.com/NVIDIA/Megatron-LM'
    type: primary
---

长上下文需要把序列本身分给多卡时，我会用 CP；TP 和 SP 解决的是权重与部分重复激活的问题。例如 $T$ 增到 32k / 128k，即使增加 TP，每张卡的本地 head 仍要处理完整序列，attention 的长度没有被切开。下面先比较通信对象，整体并行规划见 `nvidia-trillion-train`，层内归约见 `nvidia-tensor-parallel`，环传 KV 见 `nvidia-megatron-cp`。

## 各自切什么、交换什么

输入 $[B, T, D]$。

**张量并行 (TP)** 切权重。QKV / MLP 上投影列切，输出投影 / 下投影行切。正向每层两次 all-reduce，payload 都是隐藏态量级 $B\cdot T\cdot D$。attention 的 $QK^{\top}$ 仍在每张卡的本地 head 上算完整 $T$。$T$ 变长，激活和这次集合通信一起涨，但 attention 计算没有被切开。

序列并行 SP 配合 TP 使用，把 LN、Dropout 和残差沿 $T$ 切开。行并行后做 reduce-scatter，让每卡只留 $[B, T/N, D]$；下一层列并行前再 all-gather 拼回 $T$。通信量与原来的 all-reduce 同阶，但不再复制那份 LN 激活。Megatron 的 SP 组就是 TP 组，$N=1$ 时没有可分的对象，$O(T^2)$ attention 也没有因此被分担。

CP 则把网络输入和几乎所有激活沿 $T$ 切开。Linear、LN 没有跨 token 依赖，可以本地计算；attention 中每段 $Q$ 都要看到全序列的 $K,V$，因此需要交换 KV。概念上是前向 all-gather KV、反向 reduce-scatter 梯度，实现常用环形 P2P。DeepSpeed Ulysses 采用另一种布局，在 $T$ 和 head 之间做 all-to-all，通信形态不同。

## 和 TP 比，通信差在哪

粗算一次消息（省 $B$，bf16）：

- TP all-reduce：约 $2(N-1)/N\cdot T\cdot D$ 字节量级，一层两次。$D=8192$、$T=8192$ 就是每次一百多 MB，还是延迟敏感的集合。跨节点做大 TP，IB 会把 kernel 切碎。
- CP 环传 KV：每卡本地 KV 是 $T/\mathrm{CP}$ 长，绕环 $\mathrm{CP}-1$ 跳。体积跟 $T\cdot H_{\mathrm{kv}}\cdot d_h$ 走，不是 $T\cdot D$。GQA / MQA 把 $H_{\mathrm{kv}}$ 压小，CP 通信量明显小于「把隐藏态 all-reduce 一遍」，见 `google-gqa-mqa`。P2P 可以和本段 FlashAttention 重叠。大块 KV 是带宽项，TP 那两次 all-reduce 更像延迟项，见 `nvidia-nccl-allreduce`。

所以摆卡：节点内 TP（NVLink 喂两次 all-reduce），节点间可以加 CP 拉长 $T$，PP / DP 仍管深度和样本。总卡数 $\mathrm{TP}\times\mathrm{CP}\times\mathrm{PP}\times\mathrm{DP}$。把 CP 说成「再开一档 TP」是常见误区：TP 不切 $T$，CP 不切 $W$。

数量级：$T=128\mathrm{k}$、$D=8192$、$H_{\mathrm{kv}}=8$、$d_h=128$，一份 KV（单层、单 batch）大约

$$
128\mathrm{k}\times 8\times 128\times 2\times 2\,\mathrm{B}\approx 0.5\,\mathrm{GB}
$$

（K 和 V）。CP=8 时每卡只常驻 $1/8$，环上搬的是分片。同设定下 TP 那次 $[T, D]$ all-reduce 大约 $2\,\mathrm{GB}$ 量级，对象完全不同。

选择时按实际瓶颈判断：$T$ 中等、激活先爆：先 SP + 重计算 + FlashAttention，见 `nvidia-flash-attn`。单层矩阵塞不进：先加 TP。深度太长：PP，气泡见 `nvidia-pipeline-bubble`。只有「单卡 attention 的 $T$ 和激活都放不下、再加 TP 也切不了序列」才上 CP。推理侧还有 chunked 输入 prefill，那是 serving 切时间，不是训练切空间，见 `nvidia-chunked-prefill`。

## 追问

**SP 和 CP 能一起开吗？**
能。SP 绑 TP 组，CP 是另一维。别把两个开关说成互斥。

**CP 能替代 FlashAttention 吗？**
不能。CP 减的是每卡看到的 $T$；每段仍不该把 $[T_{\mathrm{chunk}}, T_{\mathrm{full}}]$ 写进 HBM。

**通信能不能藏进 GEMM？**
MLP 在本地分片 $T$ 上算，不依赖远端 KV。attention 必须等 KV 块，所以 overlap 的是「算当前 KV 块的 FA」和「下一跳 P2P」，不是和 MLP 乱叠。

**Ulysses 呢？**
all-to-all 把序列维和 head 维对换，每卡拿全部 $T$、更少 head。和环传 KV 是两条实现。先答环，再提一句变体。
