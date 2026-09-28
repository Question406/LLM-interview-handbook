---
id: sys-pp-imbalance
section: systems
order: 63
level: A
title: 系统：流水线第一级和最后一级为什么更慢？
quick: >-
  词嵌入在第一级，logits 和 loss 在最后一级。按层数均分时，这两级的计算和激活都更重，稳态里别的卡在等它们。
  把嵌入和输出头旁边的 transformer 层少放一两层，或者让这两级少承担虚 stage。
tags:
  - Pretrain
  - Pipeline Parallel
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

气泡公式假设每个 stage 一样慢。Megatron 的流水线讨论里，嵌入和输出层会把这个假设打破。这道按这个不均衡拟的。均匀时的气泡见 `nvidia-pipeline-bubble`。

## 两头

第一级除了若干 transformer 层，还有词嵌入。最后一级要把隐藏状态投到词表，词表几十万时，这一下的 GEMM 和激活都大，还要算 loss。中间级只是重复的层。

1F1B 的稳态节拍等于最慢的一级。两头慢，中间的卡在每格之间空一截。profiler 上这截空档不在 warmup，而在稳态，所以不是「microbatch 太少」能单独解释的。

## 怎么补

按时间切，不按层数切。两头少放层。词表并行可以把 logits 的 GEMM 沿词表切开，不要整份压在最后一级。只在中间级开激活重计算、两头不开，会把不均衡再放大。重计算要按实测时间加，不是按层数平均加。

## 代码

```python
def assign_layers(n_layers, n_stages):
    # ends also own embed / lm_head, so move one transformer layer inward
    base, extra = divmod(n_layers, n_stages)
    counts = [base + (i < extra) for i in range(n_stages)]
    if n_stages > 2 and counts[0] > 1 and counts[-1] > 1:
        counts[0] -= 1
        counts[-1] -= 1
        counts[1] += 1
        counts[-2] += 1
    return counts
```

## 追问

**虚拟流水线能自动治好吗？** 不能。虚 stage 把层打散，嵌入仍在某张卡的某一个 chunk 上。那一张卡的那一个 chunk 还是更慢。调度变密，不改变这块 GEMM 的大小。
