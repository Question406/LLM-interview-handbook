---
id: sys-clip-global
section: systems
order: 47
level: A
title: 系统：多卡上梯度裁剪，范数要先 AllReduce 再缩放
quick: >-
  全局 L2 是所有参数、所有卡上的平方和再开方。每张卡先按本地范数裁，再 AllReduce，裁剪系数不一致，这一步不再是同一份更新。
  inf 出现时整步跳过，不要把 NaN 乘进权重。
tags:
  - Pretrain
  - Gradient Clip
  - Data Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5063
    type: primary
  - title: torch.nn.utils.clip_grad_norm_
    url: https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
    type: primary
---

## 题怎么来的

单卡的 global norm 写法在 `coding-grad-clip`。这道问的是数据并行之后系数怎么对齐，按 PyTorch 的 `clip_grad_norm_` 和多卡训练的常规做法拟的。

## 顺序

先把各卡梯度里的平方和加总。ZeRO 把梯度切开时，每张卡只有自己那一片的平方，必须先 AllReduce 这个标量，再开方，得到大家共用的一个范数 $G$。系数是 $\min(1, \tau / (G+\varepsilon))$。每张卡用同一个系数乘自己的梯度，然后再 `optimizer.step`。

本地先裁再同步，阈值等于被卡数和分片方式改写了。有的 rank 裁了，有的没有，下一步的参数会分叉。检查点再加载就会对不上。

混合精度里，裁剪放在梯度已经 unscale 到 fp32 之后。scale 还在时，范数被 loss scale 放大，会误裁。

## inf

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

**流水线各 stage 的范数呢？** 每个 stage 只有自己那几层。平方和要跨 stage 再加一次，得到整个模型的 $G$。只在最后一级用 loss 的大小当范数，前面的层不会被裁。
