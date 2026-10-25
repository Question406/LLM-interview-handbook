---
id: "ml101-batchnorm-dropout"
section: "neural-networks"
order: 6
level: "A"
title: "Batch Normalization 和 Dropout 在训练与推理时怎么工作？"
quick: "BatchNorm 训练时用当前 batch 统计量归一化，默认同时维护供推理使用的移动统计；Dropout 训练时随机置零并缩放保留值，推理时直接通过。两者都依赖 train/eval 模式，no_grad 不会自动切换模式。"
tags: ["ML101", "neural-networks"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "PyTorch: BatchNorm1d"
    url: https://docs.pytorch.org/docs/2.14/generated/torch.nn.BatchNorm1d.html
    type: primary
  - title: "PyTorch: Dropout"
    url: https://docs.pytorch.org/docs/2.14/generated/torch.nn.Dropout.html
    type: primary
---

Batch Normalization（批归一化）训练时用当前批次统计量标准化，再乘可学习尺度、加可学习偏置。默认实现还维护均值和方差的移动估计，eval 时使用这些估计，所以同一个样本在训练与推理模式下可能得到不同结果。 [PyTorch: BatchNorm1d](https://docs.pytorch.org/docs/2.14/generated/torch.nn.BatchNorm1d.html)

Dropout 是另一种机制：训练时以概率 $p$ 把元素置零，其余值乘 $1/(1-p)$，保持期望尺度；eval 时关闭这种随机丢弃，直接输出输入。它主要用于正则化，不能用来修复 BatchNorm 的统计偏差。 [PyTorch: Dropout](https://docs.pytorch.org/docs/2.14/generated/torch.nn.Dropout.html)

例如 $p=0.5$，输入值 2 在某次训练中可能变成 0 或 4，期望仍是 2；推理时直接为 2。部署前要调用 `model.eval()`，仅写 `no_grad()` 只是不记录梯度，不会关闭 Dropout，也不会替换 BatchNorm 统计方式。

## 追问

**BatchNorm 在小 batch 上有什么问题？**
统计估计可能很噪，训练和推理差异变大。可以评估冻结统计或采用不依赖 batch 的归一化方式。

**eval 时 BatchNorm 一定不用 batch 统计吗？**
默认跟踪移动统计时是这样。PyTorch 若设置 `track_running_stats=False`，eval 也会用 batch 统计。

**Dropout 越大越不容易过拟合吗？**
过大的丢弃率也可能导致欠拟合，要与模型容量、数据量一起验证。
