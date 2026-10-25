---
id: sys-ddp-bucket
section: systems
order: 49
level: B
title: 系统：DDP 的梯度桶为什么能和反向重叠？
quick: "DDP 在一桶参数的梯度都就绪后，就能启动 AllReduce，同时继续计算前面层的反向。桶太小会频繁付启动开销，桶太大又要等太久、缩短重叠窗口，所以要用 timeline 看通信是否藏进计算里。"
tags:
  - Pretrain
  - DDP
  - Overlap
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: PyTorch Distributed Data Parallel
    url: https://pytorch.org/docs/stable/notes/ddp.html
    type: primary
---

DDP 能把通信和反向重叠，是因为反向从后往前算，靠近 loss 的参数梯度先齐，可以先放进桶里做 AllReduce，前面层的反向继续算。这道题按 PyTorch DDP 的 gradient bucketing 整理；ZeRO 拆开 AllReduce 后，重叠的通信变成 AllGather 和 ReduceScatter，见 `sys-zero-stages`。

参数按反向时梯度就绪的顺序装进桶。默认大约 25MB 量级，一个桶满了就发起通信。后面的层先就绪，所以先通信的是靠近 loss 的参数，前面的层还在算。通信和计算用不同的流，才能重叠。同一条流上先算完再通信，桶没有任何好处。

梯度累积的前几次不要通信。桶只在最后一次反向时打开。否则每个 micro batch 都在同步一份不完整的梯度。

桶很小：每次 AllReduce 的字节少，延迟占主导，GPU 在等很多个小集合通信。桶很大：要等很多参数的梯度才发车，反向快结束时才开始通信，重叠消失，步时间末尾多出一截。

调完后我会看 timeline：通信和 GEMM 在时间上同时进行，才说明重叠成功；如果两条首尾相接，通信仍然直接增加步时间。

```python
from contextlib import nullcontext

def backward_with_buckets(model, micro_batches, opt, bucket_bytes=25 * 2**20):
    opt.zero_grad(set_to_none=True)
    k = len(micro_batches)
    for i, batch in enumerate(micro_batches):
        last = i == k - 1
        ctx = nullcontext() if last else model.no_sync()
        with ctx:
            (model(**batch).loss / k).backward()
            # on the last micro-batch, DDP all-reduces a bucket
            # as soon as its grads are ready, overlapping the rest
    opt.step()
```

## 追问

**找 unused parameter 为什么慢？**
DDP 要知道哪些参数这个 batch 没有梯度，否则桶永远等不到「齐了」。静态图可以关掉这段检查。MoE 里这一步没走到的专家没有梯度，不能简单关掉，否则那些参数的桶会卡住。
