---
id: sys-pp-imbalance
section: systems
order: 63
level: A
title: 系统：流水线第一级和最后一级为什么更慢？
quick: >-
  流水线两端除了 transformer 层，还分别承担 token embedding 和
  logits、loss，按层数均分就容易让两端更慢。应按实测时间切层，让两端少放一两层，或减少它们承担的虚 stage，再检查重计算是否加重了不均衡。
tags:
  - Pretrain
  - Pipeline Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-24T00:00:00.000Z
sources:
  - title: Megatron-LM
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
---

流水线两端容易更慢，是因为它们除了 transformer 层，还承担了嵌入和输出计算。按层数均分并不等于按耗时均分，稳态节拍会被最慢的 stage 决定。

第一级负责 token embedding，最后一级要把隐藏状态投到 vocabulary 并计算 loss。vocabulary 达到几十万时，输出这一步的 GEMM 和激活都很大；中间级则主要是重复的 transformer 层。于是 1F1B 稳态里，中间的 GPU 每格之间都要等一段。profiler 上这些空档出现在稳态，单纯增加 microbatch 未必能解决。

我会先量每一级的耗时，再把两端的一两层挪向中间，或让两端少承担虚 stage。vocabulary 并行可以沿 vocabulary 切开 logits 的 GEMM，减轻最后一级的负担。重计算也要一起计时：如果只给中间级开重计算、两端不开，可能把时间差进一步放大，不能按层数平均配置。

下面示意把两端各一层移向中间，实际分配仍要靠测量：

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

这道题按 Megatron 对嵌入和输出层的讨论拟成。均匀 stage 下的气泡公式见 `nvidia-pipeline-bubble`，它的前提是每一级耗时接近。

## 追问

**虚拟流水线能自动解决吗？**
不能。它把层分散到更多 chunk，但嵌入仍在某张卡的某个 chunk 上，那块 GEMM 的大小没有变，仍需单独调平。
