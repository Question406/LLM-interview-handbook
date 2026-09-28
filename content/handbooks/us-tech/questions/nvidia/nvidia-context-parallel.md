---
id: nvidia-context-parallel
section: nvidia
order: 14
level: S
title: NVIDIA：context / sequence parallel 给长上下文，和 TP 的通信差
quick: >-
  TP 切的是层内矩阵，通信是 $[B, T, D]$ 量级的 all-reduce，延迟敏感，通常钉在 NVLink。Megatron 的序列并行只切
  LN / Dropout 的 $T$，把那次 all-reduce 换成 reduce-scatter + all-gather，省激活不省注意力。Context
  parallel 把整网的 $T$ 切开，注意力靠环传 KV，通信体积跟 $T\cdot H_{\mathrm{kv}}\cdot d_h$ 走。
tags:
  - NVIDIA
  - Context Parallel
  - Megatron
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: https://arxiv.org/abs/2310.01889
    type: primary
  - title: Context Parallelism — NVIDIA NeMo Framework User Guide
    url: https://docs.nvidia.com/nemo-framework/user-guide/25.11/longcontext/contextparallel.html
    type: secondary
  - title: NVIDIA Megatron-LM
    url: https://github.com/NVIDIA/Megatron-LM
    type: primary
---

## 题怎么来的

长上下文训练面几乎必问「$T$ 到 32k / 128k 你加哪一维并行」。NVIDIA / NeMo / Megatron-Core 岗要把 **TP、SP、CP** 三刀分开。万亿怎么切见 `nvidia-trillion-train`；层内两次 all-reduce 见 `nvidia-tensor-parallel`。本题只答：长 $T$ 时通信对象换成了谁。环上传 KV 的实现见 `nvidia-megatron-cp`。

## 三刀切的不是同一根轴

输入 $[B, T, D]$。

**张量并行 (TP)** 切权重。QKV / MLP 上投影列切，输出投影 / 下投影行切。正向每层两次 all-reduce，payload 都是隐藏态量级 $B\cdot T\cdot D$。注意力的 $QK^{\top}$ 仍在每张卡的本地 head 上算完整 $T$。$T$ 变长，激活和这次集合通信一起涨，但注意力计算没有被切开。

**序列并行 (SP)** 是 TP 的伴侣，不是另一种切权重。LN、Dropout、残差沿 $T$ 可分。行并行之后改 reduce-scatter，每卡只留 $[B, T/N, D]$；下一层列并行前 all-gather 把 $T$ 拼回。通信量与原来的 all-reduce 同阶，省的是被 TP 复制的那份 LN 激活。Megatron 里 SP 组就是 TP 组，$N=1$ 开 SP 没有对象。SP 不解决 $O(T^2)$ 注意力。

**Context parallel (CP)** 把网络输入和几乎所有激活沿 $T$ 切开。Linear、LN 没有跨 token 依赖，本地就算。注意力不行：$Q$ 的每一段必须看见全序列 $K,V$。所以要多一次 KV 的集合：概念上 all-gather KV、反向 reduce-scatter 梯度；实现上常收成环上的 P2P。这才是长上下文那一刀。DeepSpeed Ulysses 是另一条：沿 $T$ 和 head 做 all-to-all，通信形态不同，面试先把 Megatron CP 说清。

## 和 TP 比，通信差在哪

粗算一次消息（省 $B$，bf16）：

- TP all-reduce：约 $2(N-1)/N\cdot T\cdot D$ 字节量级，一层两次。$D=8192$、$T=8192$ 就是每次一百多 MB，还是延迟敏感的集合。跨节点做大 TP，IB 会把 kernel 切碎。
- CP 环传 KV：每卡本地 KV 是 $T/\mathrm{CP}$ 长，绕环 $\mathrm{CP}-1$ 跳。体积跟 $T\cdot H_{\mathrm{kv}}\cdot d_h$ 走，不是 $T\cdot D$。GQA / MQA 把 $H_{\mathrm{kv}}$ 压小，CP 通信量明显小于「把隐藏态 all-reduce 一遍」，见 `google-gqa-mqa`。P2P 可以和本段 FlashAttention 重叠。大块 KV 是带宽项，TP 那两次 all-reduce 更像延迟项，见 `nvidia-nccl-allreduce`。

所以摆卡：节点内 TP（NVLink 喂两次 all-reduce），节点间可以加 CP 拉长 $T$，PP / DP 仍管深度和样本。总卡数 $\mathrm{TP}\times\mathrm{CP}\times\mathrm{PP}\times\mathrm{DP}$。把 CP 说成「再开一档 TP」是错法：TP 不切 $T$，CP 不切 $W$。

数量级：$T=128\mathrm{k}$、$D=8192$、$H_{\mathrm{kv}}=8$、$d_h=128$，一份 KV（单层、单 batch）大约

$$
128\mathrm{k}\times 8\times 128\times 2\times 2\,\mathrm{B}\approx 0.5\,\mathrm{GB}
$$

（K 和 V）。CP=8 时每卡只常驻 $1/8$，环上搬的是分片。同设定下 TP 那次 $[T, D]$ all-reduce 大约 $2\,\mathrm{GB}$ 量级，对象完全不同。

## 什么时候还没到 CP

$T$ 中等、激活先爆：先 SP + 重计算 + FlashAttention，见 `nvidia-flash-attn`。单层矩阵塞不进：先加 TP。深度太长：PP，气泡见 `nvidia-pipeline-bubble`。只有「单卡注意力的 $T$ 和激活都放不下、再加 TP 也切不了序列」才上 CP。推理侧还有 chunked prefill，那是 serving 切时间，不是训练切空间，见 `nvidia-chunked-prefill`。

## 追问

- **SP 和 CP 能一起开吗？** 能。SP 绑 TP 组，CP 是另一维。别把两个开关说成互斥。
- **CP 能替代 FlashAttention 吗？** 不能。CP 减的是每卡看到的 $T$；每段仍不该把 $[T_{\mathrm{chunk}}, T_{\mathrm{full}}]$ 写进 HBM。
- **通信能不能藏进 GEMM？** MLP 在本地分片 $T$ 上算，不依赖远端 KV。注意力必须等 KV 块，所以 overlap 的是「算当前 KV 块的 FA」和「下一跳 P2P」，不是和 MLP 乱叠。
- **Ulysses 呢？** all-to-all 把序列维和 head 维对换，每卡拿全部 $T$、更少 head。和环传 KV 是两条实现。先答环，再提一句变体。
