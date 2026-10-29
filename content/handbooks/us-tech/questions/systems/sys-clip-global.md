---
id: sys-clip-global
section: systems
order: 47
level: A
title: 系统：多卡上 gradient clipping，范数要先 AllReduce 再缩放
quick: >-
  分片梯度先汇总各卡平方和，再开方得到统一 L2 范数，所有 rank 用同一个系数裁剪。混合精度先 unscale；任一卡出现 inf / NaN
  时同步异常标志，整步跳过并记录原因。
tags:
  - Pretrain
  - Gradient Clip
  - Data Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: On the difficulty of training Recurrent Neural Networks
    url: 'https://arxiv.org/abs/1211.5063'
    type: primary
  - title: torch.nn.utils.clip_grad_norm_
    url: >-
      https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
    type: primary
---

梯度分片后，要先求整个模型的统一范数，再让每张卡用同一个系数缩放。比如 ZeRO 下某个 rank 的梯度特别大，若各卡按本地范数分别裁剪，更新就不再对应同一个全局阈值。

单卡 global norm 的代码见 `coding-grad-clip`，这里按 PyTorch `clip_grad_norm_` 与多卡训练的常规做法，解释分片后如何对齐系数。

先把各卡梯度里的平方和加总。ZeRO 把梯度切开时，每张卡只有自己那一片的平方，必须先 AllReduce 这个标量，再开方，得到大家共用的一个范数 $G$。系数是 $\min(1, \tau / (G+\varepsilon))$。每张卡用同一个系数乘自己的梯度，然后再 `optimizer.step`。

本地先裁再同步，会让实际阈值受到卡数和分片方式影响。有的 rank 裁了，有的没有，下一步的参数会分叉。检查点再加载就会对不上。

混合精度里，裁剪放在梯度已经 unscale 到 fp32 之后。scale 还在时，范数被 loss scale 放大，会误裁。

任一 rank 出现 inf 或 NaN，AllReduce 一个标志，整步跳过，loss scale 按 FP16 的规则减半。BF16 预训练通常没有 loss scale，inf 多半是数据或通信写坏了，跳过之后要打日志，不要静默继续。见 `sys-loss-spike`。

## 代码

```python
import torch
import torch.distributed as dist


def clip_global_(grads, tau, group):
    sq = torch.zeros((), device=grads[0].device)
    for g in grads:
        sq = sq + g.detach().float().pow(2).sum()
    dist.all_reduce(sq, group=group)
    scale = torch.clamp(tau / (sq.sqrt() + 1e-6), max=1.0)
    if not torch.isfinite(sq):
        for g in grads:
            g.zero_()
        return
    for g in grads:
        g.mul_(scale)
```

## 追问

**流水线各 stage 的范数呢？**
仍要合成整个模型的范数，每个 stage 只提供自己那几层的平方和。平方和要跨 stage 再加一次，得到整个模型的 $G$。只在最后一级用 loss 的大小当范数，前面的层不会被裁。
