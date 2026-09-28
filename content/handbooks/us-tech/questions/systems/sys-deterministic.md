---
id: sys-deterministic
section: systems
order: 67
level: B
title: 系统：两次预训练的 loss 对不上最后一位，要不要查？
quick: >-
  原子加的顺序、集合通信的归约顺序、TF32，都会让最后几位不同。对不上一开始的几位，才查初始化、数据顺序和分叉的参数。
  为了逐位一致关掉 TF32，吞吐会掉，只在对账时开。
tags:
  - Pretrain
  - Numerics
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: PyTorch notes on reproducibility
    url: https://pytorch.org/docs/stable/notes/randomness.html
    type: primary
---

## 题怎么来的

「重跑对不上」是预训练排障题。按 PyTorch 对确定性和随机性的说明拟的。初始化必须相同见 `sys-init-same`。

## 可以不同的

GPU 上浮点加不满足结合律。AllReduce 的环顺序、桶的划分变了，梯度的最后几位就变。TF32 用更低的尾数做乘加，速度换精度。两次运行一个开了 TF32、一个没有，loss 从一开始就分叉，但曲线形状还在。

dropout 和数据 shuffle 的种子不同，差的是样本，不是数值库。先把种子和数据偏移对齐，再谈逐位。

## 要对上的

第 0 步、还没 dropout 的一张固定 batch，单卡 loss 应该能复现。复现不了，先查权重校验和，再查 loss 有没有被多除了一次 world size，见 `sys-allreduce-loss-scale`。

多卡不要求和单卡逐位相同。要求的是各卡参数校验和一致、loss 的数量级和单卡同一设置接近。用逐位相同当多卡的验收，会把时间耗在归约顺序上。

## 代码

```python
import torch

def param_checksum(model):
    total = torch.zeros((), device="cpu")
    for p in model.parameters():
        total = total + p.detach().float().sum().cpu()
    return float(total)
```

## 追问

**要写论文的复现实验呢？** 固定种子、固定 TF32 开关、固定集合通信算法，报的是曲线和下游指标，不是两个日志文件逐行相同。
