---
id: sys-init-same
section: systems
order: 58
level: B
title: 系统：数据并行各卡的初始权重为什么必须相同？
quick: "数据并行各卡必须从同一份参数出发，梯度平均才对应同一个模型。可以让一个 rank 初始化后广播，或保证所有 rank 使用相同种子和初始化顺序；数据 shuffle 则要按 rank 错开。恢复 checkpoint 时也要检查参数一致，不能指望第一次 AllReduce 把随机权重拉齐。"
tags:
  - Pretrain
  - Data Parallel
  - Init
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: PyTorch Distributed Data Parallel
    url: https://pytorch.org/docs/stable/notes/ddp.html
    type: primary
---

数据并行需要各卡从同一份参数出发，因为 AllReduce 平均的是同一个模型在不同数据上的梯度。若各卡各自随机初始化，梯度就来自不同参数点，平均后也不能把权重拉齐。DDP 文档因此要求各进程参数一致，这道题按该要求整理。

一个 rank 初始化，再广播到同组其他 rank。或者所有 rank 用同一个种子初始化，并且初始化顺序一致。数据的 shuffle 种子要按 rank 错开，否则每张卡读到同一批样本，数据并行没有意义。

这里要区分参数随机性和数据随机性：参数种子与初始化顺序一致，数据种子按 rank 区分。

从 checkpoint 恢复时，每张卡读自己的分片，或读全量再按 rank 切开。不要让 rank 0 读完、其他 rank 用随机权重再靠第一次 AllReduce「拉齐」。梯度平均拉不齐已经分叉的参数。

张量并行各卡本来就该持有不同的切片。相同的是切片方式，不是每张卡上的字节。检查的是：拼回去之后和单卡初始化一致，而不是各卡的局部张量逐元素相同。

```python
import torch.distributed as dist


def broadcast_params(model, src, group):
    for p in model.parameters():
        dist.broadcast(p.data, src=src, group=group)
```

## 追问

**某张卡的损失（loss） 从第一步就和其他卡差一个数量级？**
先比参数的一个校验和，再比这张卡的 batch。校验和不同就是初始化或加载分叉。校验和相同再查数据。
