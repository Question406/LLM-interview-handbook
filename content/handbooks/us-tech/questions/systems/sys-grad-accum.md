---
id: sys-grad-accum
section: systems
order: 40
level: A
title: 系统：global batch、micro batch、gradient accumulation，哪一次才同步？
quick: >-
  每卡每次处理 $b$ 条、数据并行 $N$ 张卡、累积 $K$ 次，优化器一步的 global batch 就是 $N\cdot b\cdot
  K$。通常前几次反向用 `no_sync`，最后一次同步后再 `optimizer.step`，避免重复通信。流水线 microbatch 的目的则是让不同
  stage 同时工作，要另算。
tags:
  - Pretrain
  - Batch
  - Data Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: 'verl issue 1524, batch size 三层数'
    url: 'https://github.com/verl-project/verl/issues/1524'
    type: primary
  - title: 'Megatron-LM, microbatch 与流水线'
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
---

我会先算一次优化器更新真正用了多少样本，再决定哪些反向需要同步。例如每卡每次 $b$ 条、$N$ 张卡累积 $K$ 次，global batch 就是 $N \cdot b \cdot K$。这道题是依据公开材料整理的 batch 计算题，verl issue 1524 把后训练里的三层数分开：`train_batch_size` 是 prompt 数，乘上 `rollout.n` 才是回答条数；`ppo_mini_batch_size` 决定这一批数据里优化器更新几次；`ppo_micro_batch_size_per_gpu` 只决定一张卡一次前向装几条，不改变更新次数。预训练里同一套名字换成 global batch、gradient accumulation、micro batch。

设数据并行 $N$ 张卡，每卡每次前向 $b$ 条，累积 $K$ 次再更新。优化器看到的 global batch 是 $N \cdot b \cdot K$。学习率、warmup 按这个数调，不要按 $b$ 调。

梯度在 $K$ 次里相加。同步和 `optimizer.step` 只发生在第 $K$ 次。前 $K-1$ 次如果也 AllReduce，每张卡看到的是 $N \cdot b$ 而不是 $N \cdot b \cdot K$，噪声变大，你还以为自己在用大 batch。

还要明确累加时除以 $K$ 还是 $N \cdot K$，以及通信是否另外做平均，避免重复除数。有人本地先除以 $K$，通信后再除以 $N$，这是对的。有人每张卡除以 $N \cdot K$ 又在 AllReduce 里做了平均，梯度被除了两次。

流水线把一个 step 再切成 $M$ 个 microbatch，是为了让各 stage 同时有活干，见 `nvidia-pipeline-bubble`。这 $M$ 份的梯度仍然加在一起，优化器还是一步。把流水线 microbatch 说成「gradient accumulation 的 $K$」，batch 大小会对不上。

后训练里再加一维：一条 prompt 抽 $G$ 条回答。global 样本数是 prompt 数乘 $G$。GRPO 的组必须整组留在同一次优势计算里，不能为了凑 micro batch 把一组拆开。

```python
from contextlib import nullcontext


def accum_step(model, micro_batches, opt):
    opt.zero_grad(set_to_none=True)
    k = len(micro_batches)
    for i, batch in enumerate(micro_batches):
        sync = i == k - 1
        ctx = nullcontext() if sync else model.no_sync()
        with ctx:
            loss = model(**batch).loss / k
            loss.backward()
    opt.step()
```

## 追问

**显存不够，先加 $K$ 还是开激活重计算？**
先加 $K$，global batch 和优化器步数不变，只是一步更慢。重计算是用算力换激活，和 batch 无关。两个都用的时候，先把 batch 大小的计算写下来，再谈重计算。

**$K$ 很大，BN 或 dropout 怎么办？**
LLM 预训练不用 batch norm。dropout 若开着，每次 micro batch 的 mask 不同，这是预期的。不要为了「和单次大 batch 逐位一致」去关 dropout。
