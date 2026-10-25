---
id: sys-straggler
section: systems
order: 12
level: A
title: 系统：训练 straggler、弹性、跳过坏 batch，和 NCCL 超时
quick: "同步训练受最慢 rank 限制，先区分数据或计算变慢、链路异常，以及某个 rank 没进入 collective。坏 batch 必须所有 rank 一起决定跳过，弹性恢复要在通信结束后按逻辑 ID 重新分片；NCCL 超时只是发现卡住的看门狗。"
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

训练出现 straggler 时，我会先找最早变慢或停止前进的 rank，再区分数据、计算、通信和控制流问题。同步训练里，一个 rank 慢，其他 rank 就要等它，最后报 NCCL 超时的往往只是等待者。

DDP、ZeRO、TP 在层间有同步依赖。先看 step 时间直方图，再用 Nsight 区分 H2D、GEMM 和 NCCL wait。数据侧可能是某 rank 的 shuffle、解压、变长 packing 更重；`drop_last` 不一致甚至会让它少走一步。计算侧可能是动态 shape、MoE 专家热点或 GPU thermal throttle，EP 不均见 `sys-expert-parallel`。通信侧可能是拓扑不对称、跨 NUMA 或某条 rail 拥塞。

还要单独检查 rank 是否进入了同一个 collective。OOM 被吞掉、`if rank == 0` 中包含通信、空 microbatch 跳过 all-reduce，都会让其他 rank 看起来卡在 NCCL。链路故障通常伴随 CRC / IB 错误或节点反复掉线；如果多数 rank 停在同一 op、少数始终没来，先查控制流分歧。打开 `NCCL_DEBUG=INFO` 对齐最后的 collective 序号，用 `TORCH_DISTRIBUTED_DEBUG=DETAIL` 看 unused parameter，再核对用户日志时间戳。带宽和重叠本身见 `nvidia-nccl-allreduce`。

例如原题用一个 1024 卡的示意场景：某 rank 的 dataloader 少了一个 batch，999 张卡停在 `ncclAllReduce`，表面像 IB 出故障。应找最早不再打印 step log 的 rank，超时只把整夜等待变成几分钟后退出。NVIDIA 的 Megatron、Google 弹性 TPU、Meta 千卡 FSDP 以及 OpenAI 风格调试都会关注这种区分。

## 恢复与跳过必须保持一致

弹性恢复需要先在 step 边界完成或终止在途通信，再按逻辑参数 ID 写齐 checkpoint $\to$ 按新 world size reshard $\to$ 重建通信组。DP 度变化最常见也较容易验证；TP 度要能整除 head；EP 度要重排 expert。优化器状态与权重必须使用同一分片计划。RNG 可有种子差异，但损失（loss）应连续。PyTorch Elastic 管进程生命周期，DCP 按 FQN 读写，两者需要配合。

NaN、损坏样本或偶发 inf 需要跳过时，先用小 all-reduce 或广播统一 skip 标志，所有 rank 一起跳。本地 `continue` 或静默 `except: pass` 会让进程活着却缺席通信，制造新的 hang。偶发损坏可跳，比例高说明数据或数值有问题，应该停下来排查。

Heartbeat、`TORCH_NCCL_HEARTBEAT_TIMEOUT_SEC`、较新的 `NCCL_TIMEOUT` 是看门狗，通常按正常一步耗时的数倍设置。太短会误杀 checkpoint、长序列或偶发 GC，太长则长期等待。异常要让进程真正退出，别留下僵尸 rank。验收同时看 P99 step time、failover 后 loss 能否衔接，以及各 rank 的坏 batch 跳过计数。

## 追问

**最后超时的 rank 为什么常不是根因？**
它可能一直在正确等待，根因是最早停止前进、没参加通信的 peer。

**能热加卡接着 all-reduce 吗？**
不能。在途 collective 不认识新成员，分片边界也改变，要先处理当前通信再重新分片。

**为什么 skip 也得集体决定？**
各 rank 必须以一致顺序调用 collective，不能让某个 rank 自己省掉一次通信。

**超时设置多长？**
按正常 step 耗时的数倍，并覆盖可接受的长 step。它负责及时失败，不能替代根因排查。
