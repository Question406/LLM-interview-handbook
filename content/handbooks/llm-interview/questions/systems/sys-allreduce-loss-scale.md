---
id: sys-allreduce-loss-scale
section: systems
order: 271
level: A
title: 分布式训练时如果对 loss 多 AllReduce 几次，会发生什么？
quick: "先看 reduce 是 SUM 还是 AVG，以及结果是否参与 backward。SUM 没除 world size 时，loss 与相应梯度会放大 $n$ 倍，重复 $k$ 次可能达到 $n^k$；已有全局均值再 AVG 几乎不改数值，却增加通信，日志 loss 应先 detach。"
tags:
  - Distributed Training
  - AllReduce
  - Debugging
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: PyTorch Distributed
    url: https://pytorch.org/docs/stable/distributed.html
    type: primary
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

重复 AllReduce 的后果取决于归约操作和这个标量是否用于反传。先检查 SUM / AVG，再看 tensor 的 `requires_grad` 和计算图；这里只讨论损失（loss）标量的误归约，FSDP / ZeRO 在 backward 中做的梯度通信是另一条路径，见 `sys-collectives`。

$n$ 个 rank 的 local loss 为 $L_i$。数据并行下应对样本平均：

$$
L=\frac1n\sum_{i=1}^n L_i.
$$

实现上常是每个 rank 先在 micro-batch 上求平均，再 `all_reduce` AVG（或 SUM 后除 $n$）。梯度尺度和单卡、同一全局 batch 时一致。

误用 SUM 且没除 $n$：$L'=nL$，若 $L'$ 进 backward，则 $\nabla L'=n\nabla L$，等价于学习率乘 $n$。若这段图上又 SUM 了 $k$ 次，可能到 $n^k$。症状是第一步就 loss spike、NaN、grad norm 比日志大一个 world size。world size 从 8 改到 64 时「突然不能训」，优先查这条，而不是先怪数据。

AVG 在各 rank 已经拿到同一个 $L$ 之后再 AVG，期望不变：$\frac1n\sum_i L=L$。仍有额外 NCCL 和浮点噪声，不该出现在热路径。

训练 loss 要能反传到 current $\log\pi$；用于 logging 的全局均值则先 `detach()`，再单独 reduce。把已经 AVG 过的 logging tensor 接回计算图，等于把通信结果又当目标。强化学习（RL） 里 old logprob、奖励分数（reward）、advantage 本来就该 detach；再对标量 loss 多 reduce，会使每步的梯度尺度失控。

DP 下 token 数不一致时，先对 local 有效 token 求和再全局除总 token，才是 token-mean。先各 rank 平均再 AVG，是样本等权，长序列被摊薄。这和 DAPO / Dr.GRPO 的归约之争是同一轴，见 `baidu-grpo-loss-agg`。因此要先核对 token 权重，再检查通信次数。

## 追问

**FSDP 已经在 backward 里 reduce-scatter 梯度了，loss 还要 AllReduce 吗？**
反传不依赖你对标量再 reduce。对 loss 做通信只为让各 rank 看到同一数，或为了日志。不要把两条通信叠在训练 tensor 上。
**怎么在代码里查？**
看 `loss.grad_fn` 是否还在、reduce op、有没有 `/ world_size`、logging 分支是否 `detach`。用 `torch.autograd.gradcheck` 不如直接打 `loss.item()` 和 `grad_norm` 是否差 $n$ 倍来得快。
**SUM 一次但后面 AMP 的 loss scale 也在乘，会怎样？**
两套尺度叠乘，动态 loss scale 可能疯狂 skip update。先把通信尺度修对，再看 AMP。
