---
id: sys-zero-stages
section: systems
order: 2
level: S
title: 系统：ZeRO 1/2/3 与 FSDP 对照，CPU offload 何时值得
quick: "ZeRO-1 分片优化器，ZeRO-2 再分梯度，ZeRO-3 再分参数，FSDP 与 ZeRO-3 的原理相近。它们用通信换显存，峰值还要算激活和 all-gather 工作区；GPU 不够时可先 offload 优化器，参数 offload 则要评估每层 PCIe 传输成本。"
tags:
  - Microsoft
  - Meta
  - ZeRO
  - FSDP
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: ZeRO-Offload — Democratizing Billion-Scale Model Training
    url: https://arxiv.org/abs/2101.06840
    type: primary
  - title: PyTorch FSDP — Experiences on Scaling Fully Sharded Data Parallel
    url: https://arxiv.org/abs/2304.11277
    type: primary
  - title: Introducing PyTorch Fully Sharded Data Parallel API
    url: https://pytorch.org/blog/introducing-pytorch-fully-sharded-data-parallel-api/
    type: secondary
---

ZeRO-1、2、3 依次分片优化器、梯度和参数，FSDP 在原理上对应 ZeRO-3。显存越省，热路径上的通信通常越多，所以选择时还要看网络和峰值，不能只套稳态公式 $16N/D$。例如把参数也 offload 到 CPU 后，每层都要搬权重，可能放得下却跑得慢。

## 三档各省掉哪些副本

Adam 下每参数大约：BF16 权重 $2$ + BF16 梯度 $2$ + FP32 master 与一二阶矩 $12$，合计大约 $16$ 字节。普通 DDP 每卡一份。$N$ 是数据并行度：

| Stage | 权重 | 梯度 | 优化器 | 稳态每卡（字节/参数） | 额外通信 |
| --- | --- | --- | --- | --- | --- |
| DDP | 复制 | 复制 | 复制 | $16$ | all-reduce 梯度 |
| ZeRO-1 | 复制 | 复制 | 分片 | $4 + 12/N$ | 更新后广播切片 |
| ZeRO-2 | 复制 | 分片 | 分片 | $2 + 14/N$ | 梯度 reduce-scatter |
| ZeRO-3 / FSDP | 分片 | 分片 | 分片 | $16/N$ | 每层参数 all-gather |

激活、通信 buffer、碎片都不在这张表里。ZeRO 不分激活，长序列该 checkpoint / 序列并行，见 `sys-act-checkpoint`。

FSDP 和 ZeRO-3 同构：前向 all-gather 当前包装模块的完整权重，算完丢掉；反向再 gather，梯度 reduce-scatter 回本卡切片。差别在工程：FSDP 按模块 wrap（通常一个 Transformer block），有 prefetch、混合精度；DeepSpeed 按 stage 和 bucket。Meta 训 Llama 使用 FSDP，微软生态常用 ZeRO；比较时先讲清分片和通信原理，再谈具体 API。

## 峰值和通信成本怎么估

升到 3 之后，每层热路径上多了参数 all-gather。消息大小是这一层的权重，次数跟层数走。网络差、wrap 太碎、prefetch 关着，MFU 会掉一截。这就是「ZeRO-3 为什么可能更慢」：显存下去了，集体通信从每 step 一次变成每层几次。

峰值高于 $16N_{\mathrm{param}}/N$ 是正常的：all-gather 工作区会短暂回到「一层完整参数」，再加梯度桶和 allocator 碎片。`nvidia-smi` 对不上纸面稳态，我会主动说看峰值。

和 TP 正交：TP 切的是单层 GEMM 怎么算；ZeRO 切的是副本之间的状态。万亿 dense 常见 Megatron TP 乘 PP 再乘 ZeRO-1/2，不必一上来 3。参数已经按 TP 切开时，再对剩余 DP 组做 ZeRO-3，all-gather 更碎，要量过。切分直觉见 `sys-3d-parallel`。

GPU 不够时，ZeRO-Offload 可以先把优化器状态放进 CPU DRAM，GPU 上保留权重和激活。Adam 更新在 CPU 上跑，和下一层 GPU 计算重叠。这在「单机必须塞下 70B、GPU 还剩激活」时很值：PCIe 传的是梯度切片和更新后的权重切片，不是每层完整参数。

第二刀是参数也 offload。每层 forward 从 CPU 拉权重，等于把 NVLink 级的 all-gather 换成 PCIe。只有在「没有更多 GPU 可 shard、再减 batch 会让 GEMM 瘦死」时才考虑。已经有空闲 GPU，先加 DP/FSDP 分片，别先 offload。

有空闲 GPU 时，我会先增加分片。Optimizer-only offload 可以重叠一部分传输，parameter offload 则要实测 PCIe。用 Nsight 看 H2D 是否让 kernel 出现空闲，就能判断搬运有没有拖慢训练。

相关：`meta-fsdp2`、`msft-deepspeed-zero`、`sys-allreduce-reducescatter`。

## 追问

**为什么不能只用 TP 替代 ZeRO？**
TP 解决层内计算和参数切分；优化器副本是 DP 维的问题。两边经常组合。
**FSDP wrap 粒度怎么选？**
一个 block 一层是默认。再细，all-gather 启动开销吃掉带宽；再粗，峰值 gather 一块太大。
**LoRA 还按全参 Adam 算吗？**
不要。一阶二阶矩只挂 adapter；底座至多一份分片权重。Offload 底座时稳态更低，但一层 gather 的峰值还在。
**升到 3 还 OOM 怎么办？**
ZeRO 已经到头。砍激活、减 microbatch，或加 TP/PP，不要找 stage 4。
