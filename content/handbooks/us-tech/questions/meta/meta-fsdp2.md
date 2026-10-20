---
id: meta-fsdp2
section: meta
order: 4
level: S
title: Meta：FSDP / FSDP2 切什么、通信何时发生、和 ZeRO-3 的关系
quick: >-
  FULL_SHARD 把参数、梯度、优化器状态都按 data-parallel rank 切成 $1/N$。Forward / backward 前
  all-gather 出完整层，算完再丢掉；backward 后 reduce-scatter 梯度。语义对齐 ZeRO-3。FSDP2 用
  DTensor 按参数第 0 维切，不再做 FlatParameter。
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

Meta 训练栈岗（PyTorch / Llama pretrain / Recsys 大模型）默认讲 FSDP，DeepSpeed 反而是旁支。FairScale 的 FSDP 从 Meta 进了 PyTorch；FSDP2 是同一条产品线的重写。和 `nvidia-trillion-train` 的 3D 并行不互斥：FSDP 是数据并行这一轴怎么切状态。

## 切什么：先对齐 ZeRO 表

普通 DDP：每张卡一份完整参数 $P$、一份梯度 $G$、一份 Adam 状态 $O$（fp32 副本 + 一阶二阶，大约 $12$ 字节/参数量级）。ZeRO 的三级是逐项分片：

- ZeRO-1：只切 $O$
- ZeRO-2：切 $O$ 和 $G$（参数仍复制）
- ZeRO-3：切 $P$、$G$、$O$

FSDP 的 `FULL_SHARD` 对齐 ZeRO-3；`SHARD_GRAD_OP` 对齐 ZeRO-2（forward 期间参数是完整的，省掉一次 all-gather，显存更高）。面试先说这张表，再谈 API 名字。不要答「FSDP 是另一种流水线并行」。

每张卡稳态大约持有 $P/N$ 的参数分片，外加**当前正在算的那一个 FSDP unit 的完整参数缓冲**。所以 wrap 粒度决定峰值：整网一个 unit，一次 all-gather 就可能超出显存；每层一个 unit，通信次数变多但峰值低。激活还是 $O(B\cdot T\cdot L\cdot d)$，FSDP 不替你解决激活，该上 checkpoint / FlashAttention 还是要上。

## 通信何时发生

对一个已 `fully_shard` 的 module，时间线是：

1. Forward 前：对该 unit 的参数 **all-gather**，本地分片变成完整权重，再做 GEMM。
2. Forward 后：默认 **reshard**，丢掉完整副本，只留分片。激活留下给 backward。
3. Backward 前：再 all-gather 一次参数（除非策略选择缓存未切分权重）。
4. Backward 后：对梯度 **reduce-scatter**，每张卡只留自己那一份 $G$，完整梯度丢掉。
5. Optimizer step 只作用在本地分片上，**这一步没有把 $P$ 重新拼起来**。

和 DDP 的差别：DDP 是整网梯度 all-reduce，参数始终完整；FSDP 把集合通信拆到 unit 边界，才能和计算重叠。Prefetch：算第 $\ell$ 层时异步 all-gather 第 $\ell+1$ 层。讲不出 overlap，评委会觉得你只背了分片表。

通信量：每个 unit 的 all-gather / reduce-scatter 都是 $O(\mathrm{numel})$ 量级，和 ZeRO-3 同类。层太碎，启动延迟吃掉带宽；层太厚，缓冲显存和无法重叠的气泡都会难看。所以才要调 wrap。

## FSDP1 → FSDP2，以及和 TP 怎么叠

FSDP1：一组参数 flatten、拼接、padding 成 `FlatParameter`，再均分。集合通信好做（尺寸整齐），但冻结部分参数、混合精度、state dict 都别扭，和张量并行组合要很多胶水。

FSDP2（`torch.distributed.fsdp.fully_shard`）：每个参数在 dim-0 上切成 `DTensor`，逻辑上仍按你调用 `fully_shard` 的 module 打成一个通信组（一组一次 collective），但不再真的拼成一根 1D 向量。文档强调：自底向上 wrap；`named_parameters()` 仍是原名加分片 DTensor；sharded state dict 不必为了保存再 all-gather。对冻结参数、和 TP/HSDP 组 mesh，这是 Meta 现在推的原因。

和 ZeRO-3：**内存语义同类，实现和可组合性不同。** DeepSpeed 是引擎；FSDP2 吃 PyTorch 的 DTensor / torch.compile（见 `meta-pytorch-compile`）。万亿 dense 通常还要 TP，单靠 FSDP 只能把复制去掉，切不了层内大 GEMM，见 `nvidia-trillion-train`。推荐侧巨型 embedding 表也不是 FSDP 的主战场，那是按表切的 all-to-all，见 `meta-dlrm`。

## 追问

- **Optimizer 的通信呢？** Step 在分片上本地做。需要全局 grad norm 时再对分片做一次归约，不要想象成又 all-gather 全量 Adam。
- **HSDP 是什么？** 机内切分、机间复制（或反过来按 mesh 定义）。机间流量从「每层全量 all-gather」降到副本组之间，适合节点内 NVLink 快、跨机较慢。
- **为什么会比 DDP 慢？** 两次 all-gather + reduce-scatter，若没 prefetch、wrap 太碎、或 CPU offload 同步，MFU 会掉。显存够的小模型继续 DDP 更简单。
- **和 pipeline 一起用吗？** 可以。PP 切层、FSDP 切层内状态。气泡、microbatch 和 FSDP unit 的 prefetch 会互相抢流，配置要比单用 FSDP 更小心。
