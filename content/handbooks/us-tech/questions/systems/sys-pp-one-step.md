---
id: sys-pp-one-step
section: systems
order: 41
level: A
title: 系统：流水线里优化器为什么不能在稳态中间 step？
quick: >-
  一个优化器步对应一整批 microbatch 的梯度加总。GPipe 和 1F1B 都是排空之后才更新权重。
  稳态中间 step，还在流水线里的 microbatch 会混用旧权重和新权重，这一步不再是同步 SGD。
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

## 题怎么来的

图上米色的格子经常被问成「这里能不能顺手更新」。GPipe 和 Megatron 的 1F1B 都把优化器放在流水线排空之后。这道是按这两篇的调度拟的，不是某一场的逐字题。气泡本身见 `nvidia-pipeline-bubble`。

## 一步的边界

$P$ 个 stage、$M$ 个 microbatch。每个 microbatch 的前向和反向都用**这一步开始时**的同一份权重。梯度在本地累加。最后一个反向结束、通信也结束，才 `optimizer.step`，然后才允许下一批的前向读新权重。

1F1B 的稳态是「一个新前向、一个老反向」交替，不是「反向完了就可以更新」。那个老反向用的激活，是旧权重算出来的。若在这里 step，下一格前向用新权重，梯度却还在加旧权重的贡献，这一步没有一个明确的 $\theta$。

## 和 Zero Bubble 的差别

Zero Bubble 把反向拆成对激活的 B 和对权重的 W，W 可以填进空槽。优化器仍然要等该等的梯度到齐。他们为了不在 step 前做一次全局 all-reduce（梯度范数、inf 检查会把流水线打断），会先按局部状态更新，下一步 warmup 里拿到全局结果再决定回滚。那是「先更新、错了撤」，不是「稳态里每格都 step」。没实现回滚就照抄，数值和同步 SGD 对不上。

## 代码

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

## 追问

**梯度累积和流水线叠在一起，step 几次？** 仍是每个 global step 一次。流水线的 $M$ 和累积的 $K$ 都只增加「加进这份梯度的 microbatch 数」。

**最后一级先算完 损失（loss），能不能先更新最后一级？** 不能。前面的 stage 还在用旧权重产生激活。各 stage 的 `step` 要对齐到同一次迭代，否则下一圈前向和反向的权重版本错开。
