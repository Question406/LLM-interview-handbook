---
id: sys-ckpt-bundle
section: systems
order: 48
level: A
title: 系统：预训练 checkpoint 里除了权重，还要存什么才能接着训？
quick: "可续训 checkpoint 要一起保存模型、主权重、Adam 矩、step、并行分片信息、dataloader 进度和各卡 RNG。各 rank 写分片并用同一步的清单发布，恢复时检查完整性，换卡数则按逻辑状态重新分片。"
tags:
  - Pretrain
  - Checkpoint
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: TorchTitan, 用 DCP 做与并行度无关的 checkpoint
    url: https://arxiv.org/html/2410.06511v1
    type: primary
  - title: 系统：异步 checkpoint
    url: https://pytorch.org/docs/stable/distributed.checkpoint.html
    type: primary
---

为了接着训练，checkpoint 要同时保存参数、优化器、数据进度和随机状态。比如漏掉 dataloader 游标，重启后可能又读一遍旧数据，loss 看似变好，实际数据覆盖已经改变。

这题按 PyTorch DCP 和 TorchTitan 的做法整理，恢复后 loss 对不上时，要先检查状态是否完整。异步写盘的一致性见 `sys-async-ckpt`。

模型参数、fp32 主权重、Adam 的两份矩、step 数。分片时存的是本地那一片，外加怎么切的（数据并行度、张量并行度、流水线 stage）。换卡数恢复时要能按新的切分重切，而不是要求卡数相同。

dataloader 的 epoch、文件偏移、shuffle 种子。没有这个，重启后同一段数据再出现，loss 会突然很好看，验证集不一定更好。

每张卡的 PyTorch 和 CUDA RNG。dropout、数据增强、以及某些并行里的随机通信都吃这个。只存 rank 0 的 RNG，其他卡会走出另一条 mask。

不要先把所有分片 gather 到 rank 0 再写成一个文件，模型大时这会顶高显存和磁盘压力。各 rank 写自己的分片，一份清单记下步数和切分。读的时候对清单，缺一片就拒绝恢复，不要用旧步的分片混进新步。

## 代码

```python
def save_bundle(model, opt, step, loader_state, rng, dp, tp, pp):
    return {
        "model": model.state_dict(),
        "optim": opt.state_dict(),
        "step": step,
        "loader": loader_state,
        "rng": rng,
        "mesh": {"dp": dp, "tp": tp, "pp": pp},
    }
```

## 追问

**评估要不要写进同一个文件？**
通常单独保存，评估属于旁路。把验证 loss 写进训练 checkpoint，恢复时多一个无关的大张量，也容易把没写完的评估结果当成必须对齐的状态。
