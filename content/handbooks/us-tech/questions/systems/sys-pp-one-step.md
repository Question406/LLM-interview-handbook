---
id: sys-pp-one-step
section: systems
order: 41
level: A
title: 系统：流水线里优化器为什么不能在稳态中间 step？
quick: "GPipe 和 1F1B 的一次优化器更新，要等整批 microbatch 的反向与通信结束、流水线排空后再执行。若在稳态中间 step，在途 microbatch 就会混用新旧权重，累加出的梯度不再对应同一次同步 SGD 更新。"
tags:
  - Pretrain
  - Pipeline Parallel
  - Optimizer
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: GPipe
    url: https://arxiv.org/abs/1811.06965
    type: primary
  - title: Megatron-LM pipeline schedules
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

GPipe 和 1F1B 都要等流水线排空、这一批梯度与通信全部完成，再执行一次优化器更新。否则在途的 microbatch 会混用新旧权重，梯度就不再对应同一个参数版本。

假设有 $P$ 个 stage、$M$ 个 microbatch。这一批每个 microbatch 的前向和反向都使用本步开始时的权重，梯度在各 stage 本地累加。最后一个反向及通信结束后才调用 `optimizer.step`，下一批前向再读取新权重。

1F1B 稳态会交替执行一个新前向和一个老反向。老反向所用的激活来自旧权重；如果这时 step，后面的前向已经读到新权重，累积梯度里却还有旧权重的贡献，无法给这一步指定一个明确的 $\theta$。图上出现空槽，也不意味着可以在那个位置更新。

Zero Bubble 会把反向拆成对激活的 B 和对权重的 W，用 W 填空槽，优化器仍要等所需梯度齐全。为避免 step 前的梯度范数和 inf 检查触发全局 all-reduce、打断流水线，它可以先按局部状态更新，在下一步 warmup 收到全局结果后决定是否回滚。这需要完整的回滚机制，不能理解成稳态里每格都能 step。

下面示意 1F1B 排空后才更新：

```python
def one_f1b(forward, backward, opt, num_micro, num_stages, stage):
    warmup = min(num_micro, num_stages - stage - 1)
    for _ in range(warmup):
        forward()
    for _ in range(num_micro - warmup):
        forward()
        backward()
    for _ in range(warmup):
        backward()
    opt.step()  # after the pipeline is drained
```

这道题按 GPipe 和 Megatron 调度拟成，并非某次逐字面经。气泡本身见 `nvidia-pipeline-bubble`。

## 追问

**再加梯度累积，step 几次？**
每个 global step 仍只更新一次。流水线的 $M$ 和累积的 $K$ 都在增加进入这份梯度的 microbatch 数量。

**最后一级先算完损失（loss），能先更新吗？**
不能。前面的 stage 仍在用旧权重产生激活，各 stage 的 `step` 必须对齐到同一次迭代，否则下一轮的前向、反向权重版本会错开。
