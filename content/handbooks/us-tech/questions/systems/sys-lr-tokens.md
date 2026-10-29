---
id: sys-lr-tokens
section: systems
order: 66
level: B
title: 系统：改了 gradient accumulation，学习率 warmup 按 token 还是按 step？
quick: >-
  我会按累计处理的有效 token 数设置 warmup 和衰减，这样改卡数或 gradient accumulation
  后，调度仍对应同样的数据量。每次优化器更新都统计 global batch 内的真实 token，去掉 pad。若 global batch
  本身改变，学习率是否随之缩放要单独决定。
tags:
  - Pretrain
  - LR Schedule
  - Batch
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: Megatron-LM
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
---

改变 gradient accumulation 或并行度时，我会按累计有效 token 数推进学习率调度，先保持 warmup 和衰减覆盖的数据量不变。比如一次 optimizer step 包含更多 microbatch 后，同样一次 step 就代表更多训练 token，不能直接拿 step 数比较进度。batch 定义见 `sys-grad-accum`。

一次 `optimizer.step` 处理的 token 数是 global batch 乘序列长度，再去掉 pad。warmup 设成「前 $T$ 个 token」，则累积次数变了、卡数变了，热身覆盖的数据量不变。设成「前 2000 个 step」，累积乘 8 之后，热身只覆盖原来八分之一的数据。

衰减总长同样按 token。只把 step 数对齐、不看每步 token，换机器之后余弦退火的终点会漂。

global batch 放大，有人把学习率按比例放大。这是另一条规则，要和 warmup 的 token 数分开报。只放大学习率、warmup 仍按变短的 step 走，曲线会在开头冲高。

后训练还要多区分一次生成和一次更新。一个 rollout batch 里若有多次 mini-batch 更新，调度器的一步是优化器更新，不是一次生成。把生成次数当成 step，学习率几乎不动。

```python
import math


def lr_at(tokens_seen, warmup_tokens, total_tokens, base_lr):
    if tokens_seen < warmup_tokens:
        return base_lr * tokens_seen / max(warmup_tokens, 1)
    progress = (tokens_seen - warmup_tokens) / max(total_tokens - warmup_tokens, 1)
    return base_lr * 0.5 * (1 + math.cos(math.pi * min(progress, 1)))
```

## 追问

**恢复 checkpoint 之后 warmup 重走吗？**
不重走。调度器的 token 计数和优化器的 step 一起存进 `sys-ckpt-bundle`。只存权重，恢复后调度器从 0 开始，等于重新热身。
