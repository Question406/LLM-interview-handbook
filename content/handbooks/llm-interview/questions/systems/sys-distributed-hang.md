---
id: sys-distributed-hang
section: systems
order: 20
level: S
title: 分布式训练卡住没有报错，怎样判断是 NCCL 问题还是代码路径不一致？
quick: "我会先对齐各 rank 的日志，找出最早没有参加同一次 collective 的进程。Collective 要求参与者按相同顺序、相同 shape 进入，数据耗尽、异常被吞或条件分支都可能让其他 rank 卡在 NCCL。确认调用一致后，再查 communicator、网卡和拓扑。"
tags:
  - NCCL
  - Distributed Training
  - Debugging
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: NCCL communicator guide
    url: >-
      https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/communicators.html
    type: legacy-reference
---

我会先对齐各 rank 的日志，找最早没有参加同一次 collective 的进程，再查网络。比如一个 rank 的 dataloader 先耗尽，其他 rank 仍进入 `ncclAllReduce` 等它，超时栈就会停在 NCCL。栈说明等待发生在哪里，还不能说明根因是网卡。

Collective 的约定是同一个 communicator 里的进程按相同顺序、相同 shape 调用 `AllReduce` / `AllGather` / `Broadcast` / `Barrier`。数据步数不一、OOM 或 Python 异常被吞掉、`if rank == 0` 里夹了通信，都可能让某个 rank 缺席。Gradient accumulation 步数、unused parameter、checkpoint 恢复后的参数集合不一致也要查；没有设置超时时，等待可能持续下去。

FSDP / ZeRO 每层 all-gather，Megatron TP 每层 `all_reduce`，通信点密集，分叉可能到很深的一层才显现。比如某个 DP 的 micro-batch 为空，或 packing 后 token 数为 0，实现用 `if has_data:` 跳过 `all_reduce`，其他 rank 就会一直等。RL 还可能有组内 $n$ 条轨迹长度不同、某个 DP 先耗尽 buffer、部分 worker 动态采样 abort 或随机 filter 的情况。参与同一通信组的控制流要一致，可以改变 tensor 内容，不能各自决定是否参加本次通信。

## 先定位最早的分歧

我会给 collective 记录 rank、step、op 类型、tensor shape、sequence number、前后 batch id 和 loss 是否仍变化，再按时间戳对齐各 rank 最后一条用户日志。最早停止前进的 rank 更值得查，最后 watchdog 超时的通常是在等别人。沿那条路径核对 dataloader 长度、sampler seed、`drop_last`、packing 和动态 shape，并搜索 `except: pass` 一类吞异常的代码；OOM 后进程还活着也可能已经不再通信。

NCCL watchdog、`TORCH_DISTRIBUTED_DEBUG` 和 `CUDA_LAUNCH_BLOCKING` 可以帮助拿到堆栈。Barrier 可以缩小“在第 $k$ 个探针前后”的范围，但要先确认控制流一致，插错位置会增加死锁。超时按一步实际耗时的数倍设置：太短会误杀长 CoT，太长则挂一整晚；异常发生后应让进程退出，避免僵尸 rank。

## 对齐调用后再检查通信环境

所有 rank 确认进入同一调用、shape 和 sequence number 都一致，再查 communicator、NIC、拓扑、PXN、NUMA、驱动与 NCCL 版本，以及是否有 rank 选错 rail / NIC。链路故障通常还会有 crc / ibv 报错或个别节点反复掉线。先用证据区分两类原因，避免把时间全花在 `nccl-tests`，实际错误却在 dataloader。

RL 要先标明 hang 发生在 train collective 还是 rollout 初始化。veRL / slime 里训练默认组和 vLLM、SGLang 的 `init_process_group` 可能混用 `WORLD`：单跑各自正常，合在一起第一次 collective 就挂。把 `NCCL_DEBUG=INFO`、PyTorch distributed timeout 和用户日志放在同一时间轴，确认是哪一组成员、哪次操作没有对齐。

## 追问

**unused parameter 为什么也会卡住？**
某些 rank 没用到参数，另一些仍为它发梯度通信；`find_unused_parameters` 等行为不一致时，参与者就分叉。需要核对每步参数使用和通信顺序。

**动态 batch 为空时可以直接跳过吗？**
不能让单个 rank 独自跳过整个 collective。其他 rank 仍会等待它，先统一这一步是否通信，再讨论空数据如何表示。

**最后超时的 rank 为什么常是受害者？**
它可能一直在正确等待。应找最早停止打用户日志的 rank，检查它进入通信前发生了什么。

**什么时候才优先怀疑网络？**
调用、shape、sequence number 都一致，且有 crc / ibv 错误或节点掉线等证据时，再重点查链路、网卡和拓扑。
