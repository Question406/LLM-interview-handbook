---
id: meta-fsdp2
section: meta
order: 4
level: S
title: Meta：FSDP / FSDP2 切什么、通信何时发生、和 ZeRO-3 的关系
quick: "FSDP 的 FULL_SHARD 将参数、梯度和优化器状态分给数据并行 ranks，计算某个 unit 前 all-gather 参数，反向后 reduce-scatter 梯度，优化器在本地分片更新。它与 ZeRO-3 的状态分片语义相近，FSDP2 改用逐参数 DTensor，峰值还需算完整 unit 缓冲与激活。"
tags:
  - Meta
  - FSDP
  - ZeRO
  - Distributed Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FullyShardedDataParallel — PyTorch docs
    url: https://pytorch.org/docs/stable/fsdp.html
    type: primary
  - title: fully_shard (FSDP2) — PyTorch docs
    url: https://docs.pytorch.org/docs/stable/distributed.fsdp.fully_shard.html
    type: primary
  - title: PyTorch FSDP — Experiences on Scaling Fully Sharded Data Parallel
    url: https://arxiv.org/abs/2304.11277
    type: primary
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

FSDP 在数据并行这一轴上分摊模型状态，计算时临时拼出所需 unit 的参数，算完再释放完整副本。它能减少每张卡常驻的参数、梯度和优化器状态，但不会切激活，也不能代替层内张量并行。

普通 DDP 每卡保存完整参数 $P$、梯度 $G$、Adam 状态 $O$，包括 fp32 副本与一阶二阶矩，约 $12$ 字节/参数。ZeRO-1 只分 $O$，ZeRO-2 再分 $G$，ZeRO-3 将 $P$、$G$、$O$ 都分片。FSDP 的 `FULL_SHARD` 对应 ZeRO-3，`SHARD_GRAD_OP` 对应 ZeRO-2，forward 期间保留完整参数，少一次 all-gather，但占更多显存。

每卡常驻参数约为 $P/N$，峰值还要加当前 FSDP unit 的完整参数缓冲。比如整网只包一个 unit，一次 gather 70B 就可能爆显存；每层一个 unit，峰值较低，但通信次数增加。激活仍是 $O(B\cdot T\cdot L\cdot d)$，长序列还要 checkpoint / FlashAttention。

## 一次计算怎样通信

对一个 `fully_shard` module，forward 前 all-gather 本地参数分片，形成完整 unit 做 GEMM；forward 后默认 reshard，留下参数分片和 backward 所需激活。Backward 前再 all-gather，除非策略选择继续缓存完整权重；backward 后 reduce-scatter 梯度，各卡只保留自己的 $G$。最后 optimizer step 在本地分片执行，不会再拼回全部 $P$ 或 Adam；全局 grad norm 可对分片另做一次归约。

DDP 是参数常驻、整网梯度 all-reduce，FSDP 则把通信放到 unit 边界，便于 prefetch：计算第 $\ell$ 层时异步 gather 第 $\ell+1$ 层。每个 unit 的 AG / RS 都是 $O(\mathrm{numel})$ 量级，与 ZeRO-3 类似，过碎会被启动延迟拖慢，过厚则增加缓冲与难以重叠的气泡，所以 wrap 粒度要测。

FSDP1 将参数 flatten、拼接、padding 为 `FlatParameter` 再均分，通信形状整齐，但部分参数冻结、混合精度、state dict 与 TP 组合更麻烦。FSDP2 的 `torch.distributed.fsdp.fully_shard` 在每个参数 dim-0 上形成 `DTensor`，module 仍决定通信组，一组做 collective，却不用真的拼成单根 1D 参数。

FSDP2 要自底向上 wrap，`named_parameters()` 保留原名字与分片 DTensor，sharded state dict 可不经 all-gather 保存，也更方便冻结参数与 TP/HSDP mesh 组合。FairScale 的 FSDP 经 Meta 进入 PyTorch，FSDP2 是这条路线的重写，和 DeepSpeed ZeRO-3 的内存语义相近，区别在实现与可组合性。DTensor / `torch.compile` 的关系见 `meta-pytorch-compile`。

万亿 dense 还常需 TP 来切层内大 GEMM，FSDP 只去掉状态复制，与 3D 并行可共存，见 `nvidia-trillion-train`。推荐的巨型 embedding 则多是表分片 all-to-all，见 `meta-dlrm`。

## 追问

**HSDP 是什么？**
按 mesh 定义机内分片、机间复制，或反过来。节点内 NVLink 快、跨机慢时，可减少跨机每层全量 gather 的成本。

**为什么可能比 DDP 慢？**
多了两次 all-gather 和 reduce-scatter，没 prefetch、wrap 太碎或 CPU offload 同步都会降低 MFU。显存够的小模型用 DDP 更简单。

**能配 pipeline 吗？**
能，PP 切层，FSDP 切状态，但 microbatch、气泡和 prefetch 可能争流，需要一起配置。
