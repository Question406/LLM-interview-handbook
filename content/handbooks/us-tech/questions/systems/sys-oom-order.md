---
id: sys-oom-order
section: systems
order: 51
level: A
title: 系统：预训练 OOM，按激活、优化器、通信缓冲的顺序砍
quick: >-
  先分是权重状态还是激活。状态随参数量和卡数走，用 ZeRO 或换并行度。激活随序列长度和 micro batch 走，用重计算或减 micro batch。
  不要一 OOM 就把三种并行一起改。
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

## 题怎么来的

OOM 是预训练最常见的现场题。账的分法见 `sys-param-bytes` 和 `sys-act-checkpoint`。这道只定排查顺序。

## 先看随谁变

把序列长度减半，能跑了：激活或注意力的中间量。减 micro batch 能跑、global batch 用累积补回去：还是激活。两者都减仍然炸，而且和序列长度几乎无关：参数、梯度、Adam。那时候才动 ZeRO 阶段或张量并行。

张量并行把一层的矩阵切开，激活也会跟着降，但每层多了通信。只为了省 Adam 去开张量并行，通信不划算。Adam 用 ZeRO-1 就够。

临时缓冲也会顶满：梯度 AllReduce 的桶、流水线里在途的激活、checkpoint 时 gather 全量权重。最后一种是步末才炸，前向好好的。不要为了存 checkpoint 把训练并行度改掉，改存分片。

## 后训练多出来的两块

生成时的 KV，和训练时的 Adam，经常不会同时留在卡上，见 `sys-rollout-place`。OOM 发生在切换的那一下，多半是 KV 还没释放，训练状态已经回来了。先对切换顺序，而不是把模型再切一刀。

## 代码

```python
def oom_hint(fits_short_seq, fits_small_micro, fits_without_adam_state):
    if fits_short_seq or fits_small_micro:
        return "activation: checkpoint or smaller micro-batch"
    if fits_without_adam_state:
        return "optimizer state: ZeRO-1 or higher"
    return "weights: ZeRO-3 or tensor parallel"
```

## 追问

**只在某一张卡 OOM？** 切分不均，或这张卡多了一份没释放的激活。流水线第一级在途的 microbatch 最多。看是不是总是 stage 0。
