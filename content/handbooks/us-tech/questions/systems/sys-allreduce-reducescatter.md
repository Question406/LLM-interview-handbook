---
id: sys-allreduce-reducescatter
section: systems
order: 11
level: A
title: 系统：all-reduce vs reduce-scatter+all-gather，ZeRO 为什么拆
quick: >-
  Ring all-reduce 本来就是 reduce-scatter 再 all-gather：先让每卡拿到自己那一片的完整和，再把各片拼回全量。
  ZeRO / FSDP 在梯度上做到 RS 就停，因为每卡只更新自己的 shard；参数需要时再 AG。少搬一次全量。
tags:
  - NVIDIA
  - NCCL
  - ZeRO
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: NCCL Collective Operations
    url: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/operations.html
    type: secondary
  - title: PyTorch FSDP — Experiences on Scaling Fully Sharded Data Parallel
    url: https://arxiv.org/abs/2304.11277
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

NVIDIA NCCL、Meta FSDP、Microsoft ZeRO，都会问 all-reduce 和 reduce-scatter 是不是两套算法。不是。Ring all-reduce 就是这两段拼起来的。ZeRO 的贡献是：**梯度不需要全量副本时，第二段可以不做**。和 `sys-zero-stages` 对着看。NCCL 环/树怎么选见 `nvidia-nccl-allreduce`。OpenAI 的 noisy all-gather 题（见 `openai-allgather-noise`）考信息论；本题考为什么训练里要把集体通信拆开。

## Ring 先散再聚

$N$ 张卡，张量大小 $M$，切成 $N$ 块：

1. **Reduce-scatter：** $N-1$ 步，每步收一块、本地规约、再传出。结束时 rank $i$ 持有第 $i$ 片的**完整和**。每卡搬大约 $\frac{N-1}{N}M$ 字节。
2. **All-gather：** 再 $N-1$ 步，把各片广播拼回大小 $M$ 的完整张量。再搬大约 $\frac{N-1}{N}M$。

两段合在一起就是 ring all-reduce，总搬运约 $2\frac{N-1}{N}M$，大消息下接近 $2M$，和 $N$ 弱相关。步数仍是 $2(N-1)$，所以 $N$ 很大、消息很小时延迟会翻出来。NCCL 对小消息会换 tree 等算法，不要背「永远 ring」。

数量级：70B 参数、BF16 梯度约 $140\,\mathrm{GB}$。DDP all-reduce 每卡搬接近 $280\,\mathrm{GB}$ 量级；ZeRO-2 只做 RS，大约一半。这就是「拆开少搬一次全量」的字面意思。小梯度桶走 tree 时，账要从带宽改成延迟，$N$ 一大，步数比字节更疼。

普通 DDP：每卡都要拿完整梯度才能本地更新完整参数，所以必须做完两段，也就是一次 all-reduce。TP 层内的激活同步往往也是 all-reduce：每个 rank 都要完整的 $[B,T,h]$ 才能进下一层。谁需要全量，谁就把 AG 做完。

## ZeRO 为什么在 RS 停手

ZeRO-2/3 和 FSDP 把梯度（以及 3 里的参数）按 DP rank 分片。Rank $i$ 只负责更新第 $i$ 片参数，**不需要**完整梯度。于是：

- 反向结束：对梯度做 **reduce-scatter**，每卡只留自己那片和。到此为止，不再 all-gather 梯度。
- 若参数也分片（ZeRO-3 / FSDP）：下一层 forward 前再 **all-gather 当前层权重**，用完丢掉。

通信模式从「每 step 一次完整 all-reduce」变成「梯度 RS + 按需 AG」。字节账：省掉把完整梯度再拼回去那一趟 $\approx M$；但 AG 次数变成每层一次，启动开销和同步点变多。带宽够、prefetch 做得好时，显存大降、墙钟可以持平；网络差或 wrap 太碎时，拆开反而更慢。这就是 ZeRO-3 的税，见 `sys-zero-stages`。

和 Megatron TP 对照：TP 的行并行输出需要完整激活，必须 all-reduce（或 SP 下的 reduce-scatter 回到序列切片，见 `sys-seq-parallel`）。那里「谁需要全量」的答案不同，原语相同，切的轴不同。NCCL 里 `AllReduce`、`ReduceScatter`、`AllGather` 是三个 API；算法上 AR $\approx$ RS + AG。面试把它们说成三个无关家族，下一步画 $2(N-1)$ 步会穿帮。

Overlap：大消息 ring 要把 RS/AG 藏进相邻 GEMM。ZeRO-3 的 AG 可以 prefetch 下一层；RS 可以跟本层 dgrad 重叠。藏不住就变成 SM 空等，Nsight 上是 NCCL kernel 后面一条长长的空白。

## 追问

- **All-reduce 的带宽怎么估？** Ring 下每卡约 $2\frac{N-1}{N}M$，接近 $2M$。步数 $2(N-1)$，大 $N$ 小消息改看延迟。
- **FSDP 为什么是 RS + AG？** 梯度 RS 回 shard；下一层 forward 再 AG 参数。和 ZeRO-3 同构。
- **小 tensor 也用 ring 吗？** 不一定。延迟主导时 NCCL 会走 tree。按 size 选，不要锁死。
- **TP 的 all-reduce 能拆成 RS 就停吗？** 下一层如果要完整激活，不能停。SP 改了布局，才用 RS 回到序列切片。
- **和 NCCL all-reduce 算法选择是一层吗？** 不是。NCCL 在 AR 内部选 ring/tree；ZeRO 是在应用层决定要不要做完 AG。先问谁需要全量，再问 NCCL 怎么传。
