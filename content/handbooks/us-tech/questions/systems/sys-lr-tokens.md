---
id: sys-lr-tokens
section: systems
order: 66
level: B
title: 系统：改了梯度累积，学习率 warmup 按 token 还是按 step？
quick: "warmup 和衰减按处理的 token 数走，不按优化器 step 的次数走。累积从 1 改成 8，step 少了 8 倍，按 step 的 warmup 会把热身缩短 8 倍。 global batch 变了，线性放大学习率要单独说，不要和 warmup 长度绑在一起。"
tags:
  - Pretrain
  - LR Schedule
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

改并行或累积之后 损失（loss） 曲线变了，常是调度器用错了计数单位。这道按「token 而不是 step」这个口径拟的。batch 定义见 `sys-grad-accum`。

## 计数

一次 `optimizer.step` 处理的 token 数是 global batch 乘序列长度，再去掉 pad。warmup 设成「前 $T$ 个 token」，则累积次数变了、卡数变了，热身覆盖的数据量不变。设成「前 2000 个 step」，累积乘 8 之后，热身只覆盖原来八分之一的数据。

衰减总长同样按 token。只把 step 数对齐、不看每步 token，换机器之后余弦退火的终点会漂。

## 和学习率数值

global batch 放大，有人把学习率按比例放大。这是另一条规则，要和 warmup 的 token 数分开报。只放大学习率、warmup 仍按变短的 step 走，曲线会在开头冲高。

后训练更碎。一个 采样轨迹（rollout） batch 里若有多次 mini-batch 更新，调度器的一步是优化器更新，不是一次生成。把生成次数当成 step，学习率几乎不动。

## 代码

```python
import math

def lr_at(tokens_seen, warmup_tokens, total_tokens, base_lr):
    if tokens_seen < warmup_tokens:
        return base_lr * tokens_seen / max(warmup_tokens, 1)
    progress = (tokens_seen - warmup_tokens) / max(total_tokens - warmup_tokens, 1)
    return base_lr * 0.5 * (1 + math.cos(math.pi * min(progress, 1)))
```

## 追问

**恢复 checkpoint 之后 warmup 重走吗？** 不重走。调度器的 token 计数和优化器的 step 一起存进 `sys-ckpt-bundle`。只存权重，恢复后调度器从 0 开始，等于重新热身。
