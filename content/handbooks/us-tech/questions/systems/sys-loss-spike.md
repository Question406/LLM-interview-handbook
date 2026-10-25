---
id: sys-loss-spike
section: systems
order: 15
level: A
title: 系统：分布式训练 loss spike 排查清单
quick: "分布式训练突然 loss spike，我会先核对各 rank 的 collective 和 skip 决定，再用 sample id 复放出错数据。随后分别查并行布局、overflow 和 amax、checkpoint 与 RNG，确认系统状态一致后再调学习率等数值配方。全局平均之外还要保留 per-rank loss 和 grad norm，避免局部爆炸被平均掩盖。"
tags:
  - OpenAI
  - NVIDIA
  - Training
  - Debugging
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
  - title: "Spike No More: Stabilizing the Pre-training of Large Language Models"
    url: https://arxiv.org/abs/2312.16903
    type: primary
  - title: PyTorch Distributed Elastic
    url: https://pytorch.org/docs/stable/elastic/run.html
    type: secondary
---

loss spike 的系统排查，我会先确认所有 rank 在同一步执行了相同的通信和更新决定，再复放出错样本。比如某张卡检测到 inf 后独自 skip，其他卡继续 Adam 更新，下一步参数就会分叉，曲线看起来也像训练不稳定。数值和优化器配方见 `openai-loss-spike`，NCCL hang 与慢卡见 `sys-straggler`；这里先讨论作业还在步进的情况。

这一步先固定证据，避免同时改变数据、并行和学习率，之后分不清是哪项起作用。

同步训练里，loss 是各 rank 的平均。只看 rank 0 的标量会把局部爆炸洗掉。我会要：每 step 的全局 loss、grad norm、tokens、skip 计数、是否 overflow skip，**所有 rank 各一份**。各 rank 的计数或状态对不上，就先定位发生分歧的步骤。

控制流必须是常量：坏 batch 跳不跳、这一 microbatch 空不空、有没有 `if rank == 0` 包住通信。只在一张卡 `continue`，其他人仍进 all-reduce，轻则一步梯度错位（loss 尖刺），重则 hang。跳过要先集体投票再一起跳，见 `sys-straggler`。`drop_last`、packing 长度、padding mask 若各 rank 自己算，等于每步数据分布都在漂。

可以用一个 1024 卡的例子说明：某 rank 的 shard 里一条损坏样本把激活打成 inf，FP8/FP16 溢出后 GradScaler 只在该卡 skip，别的卡照常 Adam。下一步权重分叉，loss 从尖刺变成不可逆发散。inf 标志必须 all-reduce 之后 **所有人一起 skip 或一起 step**，见 `sys-mixed-precision`、`nvidia-loss-scale`。

先查数据。万亿 token 数据管道里，spike 的第一嫌疑是样本而不是学习率：超长 pack 把无关文档粘在一起且文档边界 token 丢了、二进制垃圾、重复高 loss 域、某 epoch shuffle 把同一脏 shard 再喂一次。dataloader 状态没和模型一起 ckpt，resume 后有的 rank 重复、有的跳过，曲线会在恢复点附近跳。查法：复放该 step 的 sample id；单卡 greedy 重算同一 pack，尖还在就是数据/数值，尖没了才查通信。管道本身见 `sys-data-pipeline`。

再查并行布局。TP 的 dropout mask / RNG 没按设备广播；SP 的 all-gather 和列并行顺序反了；PP 最后一档 loss 平均漏了某个 microbatch；CP 的因果块没 zigzag，个别 rank 的注意力统计炸掉。这类 bug 往往 **一开某种并行就稳定复现**，不像数据那样偶发。MoE 热点专家会让部分 token drop，loss 跳的同时还伴 all-to-all P99，见 `sys-expert-parallel`。

精度方面，BF16 一般不需要全局 loss scale；FP16 的 $S$ 太大造成 overflow skip 风暴，太小则小梯度冲掉。FP8 delayed amax 在 LR 跳、batch 组成突变时用过期 scale，GEMM 打出 inf。Nsight / TE 计数器上看 inf 次数和 amax 是否打满，不要只看 loss 曲线。通信用 FP16 规约、累加顺序因 DP 度改变，也会让「同一超参换卡数」后曲线对不上，见 `sys-allreduce-reducescatter`。

恢复与落盘方面，异步保存和训练并发时，若拷的是正在被 Adam 改的缓冲，落盘是撕裂的一步。下次 resume 就是人为 spike。要冻结一份一致快照再放后台，见 `sys-async-ckpt`。更少见但真实的是静默位翻转；同一 pack 换机器能复现就不是 SDC，换机器才复现再怀疑硬件。

实际排查顺序是：对齐 collective 和 skip $\to$ 复放 sample id $\to$ 关可疑并行开关 $\to$ 查 overflow / amax $\to$ 查 ckpt 与 RNG。数值配方（QK-norm、z-loss、$\beta_2$）确认系统面干净后再动，交给 `openai-loss-spike`。

再看一个 4096 卡的示意例子：step 80k 附近 loss 从 2.1 跳到 8，grad norm 同步尖，随后三步回来。rank 直方图显示只有两个 DP replica 的 per-rank loss 爆炸。复放那两个 replica 的 pack id，发现同一条 PDF 抽取出的二进制垃圾。单卡重跑该 pack 必炸；全 rank 对 skip 标志 all-reduce 之后，尖刺变成一次 skip，曲线接上。若当时只在那两张卡 `continue`，下一步就是权重分叉，看起来像「训练不稳定」。

## 追问

**尖刺之后 loss 回来了还要停吗？**
偶发 skip / 单条脏样本可以记计数；grad norm 也炸、权重范数上台阶，就该停下来复放，不能当噪声。

**为什么只看 rank 0 不够？**
平均会把单卡 inf 稀释。要 per-rank max，以及 inf 标志的 all-reduce。

**和 straggler 怎么区分？**
Straggler 是实际耗时尾巴、集体通信等不到人。Spike 是标量跳、作业仍在步进。两者可以共存：脏 pack 又慢又炸。

**换 TP 度数曲线就跳，是系统还是数值？**
先查 RNG、dropout、LN 布局、FP16 规约顺序。确认前向 bit-exact 对不上，再谈优化器。

**FP8 刚升温就尖，先怪 LR 吗？**
先看 delayed amax 是否还是 warmup 的旧值。分布一变，过期 scale 会打 inf，这是系统计数器，不是学习率。

**异步 ckpt 恢复点附近尖，先怪优化器吗？**
先对 dataloader 游标、RNG、amax 历史是否和权重同一 iteration。撕裂快照见 `sys-async-ckpt`。

**只一台机器能复现、换机不能，是什么？**
优先怀疑静默数据损坏或坏页。同一 pack 换机仍炸才是数据/数值。

## 相关题

- [[openai-loss-spike]]：同一现象的数值面，按数据、学习率、并行同步、精度、坏 batch 五层查，并要求定位到卡、step 和样本。
