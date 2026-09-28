---
id: sys-distributed-hang
section: systems
order: 20
level: S
title: 分布式训练卡住没有报错，怎样判断是 NCCL 问题还是代码路径不一致？
quick: >-
  Collective 要求所有 rank 按相同顺序、相同 shape 进来。某个 rank 提前异常、数据耗尽、条件分支跳过通信，别人就会看起来像「卡在
  NCCL」。我会先找最早发生分歧的那个 rank 和那一次 collective，不会一上来换网卡。
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

这块容易一看到 `nccl` 栈就报「网络坏了 / 换网卡」。Hang 是现象：某个 rank 没来参加这次 collective，其他 rank 会在 NCCL 里无限等。根因更常是 **rank divergence**，代码路径、数据量、shape 不一致，而不是 IB 掉了。我先证明所有 rank 要以相同顺序、相同 shape 进入同一个 communicator，再怀疑链路。NCCL 本身很少「随机卡住还完全没日志」；更常见的是它在正确等待一个永远不会来的 peer。把现象当成诊断，会把一天花在 `nccl-tests` 上，而 bug 在 dataloader。RL 框架里还有训练图和推理引擎两套通信组，要先标 hang 发生在哪一套。

## 为什么「卡在 NCCL」常常不是 NCCL

Collective（`AllReduce` / `AllGather` / `Broadcast` / `Barrier`）的契约是：组内每个 rank 都调用、顺序一致、tensor 形状一致。任一 rank 若：

- dataloader 先耗尽或 `drop_last` 行为不同，少走一步；
- 某步 OOM / Python 异常被吃掉，没进 collective；
- `if rank == 0` 或「偶发条件」里包了一段通信；
- gradient accumulation 步数、unused parameter、checkpoint restore 后参数集合不一致；

那么它永远不会到达这次调用。别的 rank 的 watchdog 超时栈会停在 `ncclAllReduce`，看起来像网络。NCCL 没有超时默认值时，这个等待可以是无限的。

FSDP / ZeRO 每层 all-gather、Megatron TP 每层 `all_reduce`，通信点极密，路径稍微分叉就会在「很深的一层」挂住，而不是在你插的那行 `print` 上。动态 shape 是另一类分叉：某一 DP 的 micro-batch 是空的、或 packing 后 token 数为 0，实现若选择 skip 这一层通信，其他 rank 仍会进入。RL 里组内长度不同、某一 DP 先把 buffer 耗尽、动态采样 abort 只发生在部分 worker，都会制造这种 skip。原则是：**控制流上的通信点必须对所有 rank 是常量**，变的只能是 tensor 内容，不能是「这步调不调 collective」。`if has_data:` 包 `all_reduce` 是经典地雷。

## 怎么定位最早的分歧

不要只盯最后超时的 rank，它往往是受害者。

1. 为每个 collective 打 rank、step、op 类型、tensor shape、sequence number，以及前后的 batch id / loss 是否还在动。
2. 核对 dataloader 长度、sampler seed、`drop_last`、packing、动态 shape 是否所有 rank 一致。变长 RL 轨迹尤其容易在某一 DP 上先结束。
3. 用 NCCL watchdog / `TORCH_DISTRIBUTED_DEBUG` / `CUDA_LAUNCH_BLOCKING` 拿到堆栈，比较 **最早停止前进** 的 rank：它是谁、停在用户代码哪一行。
4. 确认异常没有被 `except: pass`。OOM 之后进程还活着但不参与通信，是经典假 hang。

barrier 可以缩小范围（「卡在第 $k$ 个 barrier 之前」），但在错误位置额外插 barrier 也会制造新死锁，不能当根治。先对齐控制流，再插。

## 什么时候才查网络和 communicator

代码路径一致、shape 一致、每个 rank 都进入了同一次调用，这时才查：

- communicator 是否混用了默认组和新组（veRL 里 vLLM / SGLang `init_process_group` 冲突很常见）；
- 网卡、拓扑、PXN、是否跨 NUMA、驱动与 NCCL 版本；
- 是否有 rank 落在错误的 rail / 错误的 NIC。

先 divergence、后网络，顺序反了会浪费一天。RL 一步里训练图和推理引擎各有一套通信组，更要把「哪一次 hang」标成 train 还是 rollout。veRL / slime 里 vLLM、SGLang 常会 `init_process_group`，和训练默认组抢 `WORLD`，第一次 collective 就挂，单跑 trainer 或单跑引擎却都正常。这是 communicator 混用，不是网线。查的时候把 `NCCL_DEBUG=INFO`、PyTorch distributed timeout、以及每个 rank 的最后一条用户日志对齐到同一时间轴。最早停止打日志的 rank 才是嫌疑人；最后 watchdog 炸掉的 rank 只是等得最久的受害者。真正的链路故障通常伴有 crc / ibv 报错、个别节点反复掉，而不是「所有 rank 整齐地停在同一个 op、其中几个永远不来」。两种栈长得像，根因表完全不同。

## 排查顺序

第一刀：hang 发生在 train collective 还是 rollout 初始化。第二刀：各 rank 最后一条用户日志时间戳，找最早停住的那个。第三刀：那条路径上有没有 `if`、空 batch、动态 shape、吞掉的异常。第四刀：shape 和 sequence number 是否一致。以上都齐了，才查 NIC、拓扑、NCCL 版本、是否混用 communicator。RL 框架里第三、第四刀最常中招。barrier 只能当探针，不能当补丁。超时要设成「数倍于一步墙钟」，并保证异常能把进程拉死，避免僵尸 rank。

## 追问

- **为什么最后超时的 rank 不是根因？** 它在正确等待一个永远不会来的 peer。根因是最早停止前进、没参加这次 collective 的那个。对齐各 rank 最后一条用户日志时间戳，不要只看 watchdog 栈。
- **unused parameter 怎么导致 hang？** 有的 rank 这步没用到某参数，DDP / FSDP 仍可能为它发梯度通信；`find_unused_parameters` 不一致时，有人发有人跳过。控制流上的通信点必须对所有 rank 是常量。
- **RL 里还有什么特有分叉？** 组内 $n$ 条长度不同、动态 batch 空 micro、某一 DP 先 abort、动态采样 filter 带随机。必须先对齐「这一步有没有进 collective」，再查 NCCL。
- **timeout 设多少？** 短了误杀长 CoT，长了挂一整晚。按「一步墙钟的数倍」设，并保证异常能把进程拉死而不是 `except: pass` 变成僵尸 rank。
- **什么时候才是真的网络问题？** 代码路径、shape、sequence number 都一致，每个 rank 都进入了同一次调用，并且伴有 crc / ibv 报错或个别节点反复掉。整齐地停在同一个 op、其中几个永远不来，优先 divergence。
- **veRL / slime 里还有哪类 hang？** 推理引擎 `init_process_group` 和训练默认组抢 `WORLD`。单跑两边都正常、合在一起 hang，是 communicator 混用，不是网线。
- **`if has_data` 包 all_reduce 为什么是地雷？** 某一 DP 空 batch 就跳过通信，其他 rank 仍进入，永远等。变的只能是 tensor 内容，不能是「这步调不调 collective」。
- **排查顺序？** 先标 hang 在 train 还是 rollout，再找最早停住的 rank 和条件分支，最后才查 NIC。NCCL hang 是现象，rank 分歧才是最常见根因。
