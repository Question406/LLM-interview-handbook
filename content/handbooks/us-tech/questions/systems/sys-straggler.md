---
id: sys-straggler
section: systems
order: 12
level: A
title: 系统：训练 straggler、弹性、跳过坏 batch，和 NCCL 超时
quick: >-
  同步训练的一步墙钟等于最慢那张卡。Straggler 先分清是数据、计算、还是某 rank 没进 collective。弹性是排空通信、换人、按逻辑
  ID reshard。坏 batch 跳过要所有 rank 一起跳。NCCL 超时是看门狗，不是根因。
tags:
  - NVIDIA
  - NCCL
  - Elastic Training
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PyTorch Distributed Elastic
    url: https://pytorch.org/docs/stable/elastic/run.html
    type: secondary
  - title: NCCL Environment Variables
    url: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
    type: secondary
  - title: Megatron-LM — Training Multi-Billion Parameter Language Models Using Model Parallelism
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

NVIDIA 大规模 Megatron、Google 的弹性 TPU 作业、Meta 千卡 FSDP，都会问为什么 step time 的尾巴很长、挂了是网坏了还是某张卡没来。OpenAI 更爱 debug：先证明所有 rank 以相同顺序进入同一个 collective。NCCL 超时是现象；straggler、分歧、坏 batch 是三类不同的病。

## 同步一步等于最慢的 rank

DDP / ZeRO / TP 每层都有屏障。某一个 data loader 慢、某一个 expert 热点、某一个 GPU 降频，所有人等它。先看 step 时间直方图，再看 Nsight：慢在 H2D、在 GEMM、还是在 NCCL wait。

常见来源：

- **数据面：** 某个 rank 的 shuffle、解压、变长 packing 更重。`drop_last` 不一致会让一个 rank 少走一步，直接变成 hang。
- **计算面：** 动态 shape、MoE 热点、某卡 thermal throttle。EP 不均就是计算 straggler，见 `sys-expert-parallel`。
- **通信面：** 拓扑不对称、一台跨 NUMA、一条 rail 拥塞。NCCL 本身很少「随机卡住还完全没日志」。

和「某 rank 没进 collective」要分开。后者是控制流分叉：OOM 被吞掉、`if rank == 0` 里包了通信、空 microbatch 跳过 all-reduce。别的 rank 会在 NCCL 里无限等，栈看起来像网络。真正的链路故障通常伴有 CRC / IB 报错或个别节点反复掉；所有人整齐停在同一个 op、其中几个永远不来，优先查 divergence。NCCL 环本身的带宽/重叠见 `nvidia-nccl-allreduce`；本题管的是「为什么有人没进来」和超时怎么设。

排查顺序：`NCCL_DEBUG=INFO` 对齐各 rank 最后一次 collective 序号；`TORCH_DISTRIBUTED_DEBUG=DETAIL` 看 unused parameter。先证明控制流一致，再怀疑链路。别一上来换网卡。

一个现场形状：1024 卡、某 rank dataloader 少一个 batch。999 张卡停在 `ncclAllReduce`，看起来像 IB 挂了。最早不再打 step log 的那个 rank 才是根因。超时只是把这个 hang 从「挂整夜」变成「几分钟后作业死掉」。

## 弹性、跳过坏 batch、超时怎么配

弹性不是「多插几张卡接着 all-reduce」。飞行中的 collective 不知道新成员，分片边界也变了。正确顺序：step 边界排空 $\to$ 按逻辑参数 ID 写齐套 checkpoint $\to$ 按新 world size reshard $\to$ 重建通信组。DP 变最常见也最好测；TP 变要能整除 head；EP 变要重排 expert。优化器状态必须跟权重同一套 plan 切。RNG 允许种子差，loss 应连续。PyTorch Elastic 管进程生命周期；DCP 管按 FQN 读写。两件一起才叫 resume。

坏 batch（NaN、损坏样本、偶发 inf）：**所有 rank 必须对「这一 step 跳不跳」达成一致**。只在某个 rank 上 `continue`，其他人仍进 all-reduce，就是人造 hang。做法是一次小 all-reduce 或广播一个 skip 标志，再一起跳。跳过不是「这张卡自己不理这批数据」。有人把 skip 写成静默 `except: pass`，进程还活着但不参加通信，看门狗会把锅甩给 NCCL。

NCCL / PyTorch 的 heartbeat、`TORCH_NCCL_HEARTBEAT_TIMEOUT_SEC`、较新的 `NCCL_TIMEOUT` 是看门狗：一步墙钟的数倍设超时，让死 rank 把作业拉下来，而不是挂一整晚。设太短会误杀长 step（checkpoint、长序列、偶发 GC）；设太长等于没有。超时栈停在 `ncclAllReduce` 时，先对齐各 rank 最后一条用户日志时间戳，找 **最早停住** 的那个，不要只看最后爆炸的受害者。

Google 弹性作业、NVIDIA 千卡，验收看 P99 step time、failover 后 loss 是否接上、跳过坏 batch 的计数是否所有 rank 一致。别只报「开了 elastic」。

## 追问

- **为什么最后超时的 rank 不是根因？** 它在正确等待一个永远不会来的 peer。根因是最早停止前进、没参加这次 collective 的那个。
- **为什么不能热加卡接着训？** 飞行中的 collective 不知道新成员；分片边界也变了。必须排水加 reshard。
- **跳过坏 batch 为什么要集体决定？** 控制流上的通信点必须对所有 rank 是常量。变的只能是张量内容，不能是「这步调不调 collective」。
- **超时设多少？** 数倍于正常一步墙钟。短了误杀，长了挂整夜。并保证异常能把进程拉死，不要 `except: pass` 变成僵尸 rank。
- **跳过很多坏 batch 还训得下去吗？** 偶发损坏可以跳；比例高说明数据或数值坏了，该停。跳是为了别把 hang 伪装成 NCCL 超时，不是为了吞 NaN。
