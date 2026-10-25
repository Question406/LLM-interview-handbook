---
id: sys-async-ckpt
section: systems
order: 21
level: A
title: 系统：异步 checkpoint，一致性和占用
quick: "先在同一 iteration 边界，把训练状态复制成不再被更新的快照，再由后台写盘。训练只等 staging，代价主要是额外 CPU 内存；权重、优化器、RNG 和 dataloader 必须属于同一步，写完后才发布为可恢复 checkpoint。"
tags:
  - NVIDIA
  - PyTorch
  - Checkpointing
  - Megatron
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PyTorch Distributed Checkpoint
    url: https://pytorch.org/docs/stable/distributed.checkpoint.html
    type: secondary
  - title: dist_checkpointing — Megatron Core
    url: https://docs.nvidia.com/megatron-core/developer-guide/latest/api-guide/core/dist_checkpointing.html
    type: secondary
  - title: "CheckFreq: Frequent, Fine-Grained DNN Checkpointing"
    url: https://www.usenix.org/conference/atc20/presentation/mohan
    type: primary
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary
---

异步 checkpoint 要先取得一致且独立的快照，再让后台写盘，训练才能安全继续。比如 CPU 缓冲已经拿到同一步的状态后，GPU 可以执行下一步更新；如果 DMA 时 Adam 还在改同一块显存，磁盘上就会混入两步状态。

NVIDIA Megatron / NeMo 和 PyTorch DCP 的 `async_save` 都在减少落盘对训练的阻塞。它处理容错快照；`sys-act-checkpoint` 则用重算减少 step 内激活 HBM，二者的目标不同。

同步 ckpt：停训练，所有 rank 把分片写盘，等齐再继续。简单、一致，实际耗时等于最慢的 rank 的 IO。万亿状态（权重 + Adam 矩）经常几十到上百 GB 每卡量级，几分钟一次会把有效 MFU 切一截。

异步把它拆开：

1. **Stage：** 在 step 边界 barrier 之后，把当前 state_dict 从 GPU 拷到 CPU 可写缓冲（或 pinned / CUDA IPC）。拷完这份缓冲视为冻结。
2. **Persist：** 后台线程/进程把冻结缓冲写到分布式文件系统。训练用 GPU 上的原张量继续下一步。

PyTorch DCP 的 `async_save`、Megatron 的 async / NVRx 策略都是这个形状。CheckFreq 更早把「频繁、细粒度」和后台写盘写进训练循环。Stage 期间要确保源张量不被 Adam 原地修改，可以双缓冲，或暂时停止更新。

上一份后台写还没结束又触发下一份，要排队或跳过。两个 in-flight 快照会把 CPU 内存乘上去，也分不清哪份是完整的。保留「最近一份完成的」；写到一半的目录不能当可 resume 点。失败语义：训练继续，ckpt 失败打日志，不要把半文件 rename 成最新。

一份能 resume 的快照包括：分片权重、优化器矩、GradScaler / FP8 amax 历史、RNG、dataloader 游标，见 `sys-data-pipeline`。只存权重，Adam 从零矩重启，损失（loss） 会跳，看起来像 `sys-loss-spike`。各 rank 必须对同一 iteration 编号 stage；有 rank 快一步，落盘分片就无法组成同一训练状态。TP/PP/ZeRO 下按 FQN 分片写，resume 时允许 world size 变（弹性），但不能允许「半个 iteration」。

Barrier 放在 stage 前，不是放在写盘结束。写盘结束再 barrier 就把异步又变同步。训练侧只等 stage 完成（HBM→DRAM），不等 NFS。

稳态多出来的是 **一份 CPU 侧拷贝**，大小约等于 GPU 上那份分片状态，不是再复制一份完整模型到每张卡。优化器矩是大头：Adam FP32 约 8-12 字节/参数加 master。CPU DRAM 不够时 stage 会 OOM，异步开不起来。GPU 侧若用双缓冲再占一份 HBM，长序列本来就紧，往往不可接受，所以 stage 目标是尽快离 GPU。

频率：太勤，stage 带宽和后台 IO 打满，训练被隐式拖住；太疏，故障窗口大。对着 MTBF 和一次 stage 的毫秒数选。频率最终要在 staging 成本、后台吞吐与故障后的重算量之间取舍，不能直接与训练步内的 activation checkpoint 比显存。

## 追问

**为什么不能边更新边写同一块 GPU 内存？**
写到一半的权重和已更新的矩拼在一起，resume 后必漂或 NaN。
**async 还要不要 barrier？**
要，在取快照前对齐 iteration。不要在写盘结束再挡训练。
**ZeRO-3 下存什么？**
每卡自己的参数/梯度/矩分片，外加一份公共元数据。不要 all-gather 成完整模型再存，那会把峰值打爆。
**和弹性重启什么关系？**
快照按逻辑 ID 存，新 world size 再 reshard。飞行中的 collective 不能热加卡，见 `sys-straggler`。

**stage 完了训练能立刻更新吗？**
可以，只要更新 GPU 上的原状态，CPU 冻结拷贝不再被 in-place 修改。
**写盘失败训练要不要停？**
通常不停，打日志，保留上一份完整目录。把半文件标成最新才会在 resume 时中招。
