---
id: sys-oom-order
section: systems
order: 51
level: A
title: 系统：预训练 OOM，按激活、优化器、通信缓冲的顺序砍
quick: "先看 OOM 随什么变化：缩短序列或减小 micro batch 就能跑，优先处理激活；两者都无效，再检查参数、梯度和 Adam 状态，用 ZeRO 或调整并行度。若只在保存或生成与训练切换时爆显存，要先查临时缓冲和释放顺序。"
tags:
  - Pretrain
  - Memory
  - OOM
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24
sources:
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

预训练 OOM 时，我会先分清占满显存的是激活、模型状态，还是临时缓冲，再改对应的配置。最直接的判断是缩短序列或减小 micro batch，观察能不能跑起来。

序列长度减半就能跑，通常是激活或注意力中间量太大。减小 micro batch 有效，也指向激活，可以用梯度累积补回 global batch。两者都减了仍然 OOM，而且显存几乎不随序列长度变化，再查参数、梯度和 Adam，考虑 ZeRO 阶段或张量并行。具体的状态账和激活账见 `sys-param-bytes`、`sys-act-checkpoint`。

张量并行把一层矩阵切开，也能减少激活，但每层都增加通信。如果只是 Adam 放不下，ZeRO-1 就能分摊优化器状态，没必要为此承担张量并行的通信。

还要看 OOM 发生的时刻。梯度 AllReduce 的桶、流水线中在途的激活都可能形成峰值；前向正常、保存 checkpoint 才爆，可能是保存时 gather 了全量权重，这时改成存分片就行。后训练若在生成和训练切换时爆，常见原因是 KV 还没释放，Adam 等训练状态已经回到 GPU。应先核对切换顺序，见 `sys-rollout-place`。

下面用几个简化的探测结果决定先查哪一类：

```python
def oom_hint(fits_short_seq, fits_small_micro, fits_without_adam_state):
    if fits_short_seq or fits_small_micro:
        return "activation: checkpoint or smaller micro-batch"
    if fits_without_adam_state:
        return "optimizer state: ZeRO-1 or higher"
    return "weights: ZeRO-3 or tensor parallel"
```

## 追问

**为什么只有一张卡 OOM？**
先查切分是否均匀，以及它是否多留了一份激活。流水线第一级在途的 microbatch 最多，可以先看是不是总在 stage 0 发生。
