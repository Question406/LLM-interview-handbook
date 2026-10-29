---
id: sys-deterministic
section: systems
order: 67
level: B
title: 系统：两次预训练的 loss 对不上最后一位，要不要查？
quick: "最后几位的差异可以先按浮点归约顺序和 TF32 设置排查；若一开始的有效数字就差很多，再查初始化、数据顺序和参数分叉。对账时固定种子、数据偏移和精度开关，并检查各卡参数一致，性能验收则看曲线和下游指标。"
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

如果两次预训练的 loss 只差最后几位，我会先检查浮点运算顺序和 TF32 设置，不会立刻判成训练出错。比如改了 AllReduce 桶划分，归约顺序变了，也可能出现小差异。这道题按 PyTorch 的可复现性说明整理，初始化一致性见 `sys-init-same`。

GPU 上浮点加不满足结合律。AllReduce 的环顺序、桶的划分变了，梯度的最后几位就变。TF32 用更低的尾数做乘加，速度换精度。两次运行一个开了 TF32、一个没有，损失（loss）从一开始就出现差异，但曲线形状还在。

dropout 和数据 shuffle 的种子不同，差的是样本，不是数值库。比较数值前，要先把种子和数据偏移对齐，保证两次运行确实处理了同样的样本。

第 0 步、还没 dropout 的一张固定 batch，单卡 loss 应该能复现。复现不了，先查权重校验和，再查 loss 有没有被多除了一次 world size，见 `sys-allreduce-loss-scale`。

多卡不要求和单卡逐位相同。要求的是各卡参数校验和一致、loss 的数量级和单卡同一设置接近。用逐位相同当多卡的验收，会把时间耗在归约顺序上。

```python
import torch


def param_checksum(model):
    total = torch.zeros((), device="cpu")
    for p in model.parameters():
        total = total + p.detach().float().sum().cpu()
    return float(total)
```

## 追问

**要写论文的复现实验呢？**
固定种子、固定 TF32 开关、固定集合通信算法，报的是曲线和下游指标，不是两个日志文件逐行相同。
