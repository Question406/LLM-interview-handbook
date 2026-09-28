---
id: sys-act-mem
section: systems
order: 64
level: B
title: 系统：激活显存随序列长度怎么涨，和参数的 16 字节怎么分开？
quick: >-
  参数状态不随序列变。激活大致随 batch、长度、层数、隐藏维变，注意力的分数矩阵还随长度的平方。
  长度加倍 OOM，先动重计算或 micro batch，不要先升 ZeRO 阶段。
tags:
  - Pretrain
  - Activation
  - Memory
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

`sys-param-bytes` 只算参数状态。这道补激活，仍是估算题，不是某一场原话。重计算见 `sys-act-checkpoint`。

## 哪些项随长度走

每一层保存的隐藏状态大约是 batch × 长度 × 隐藏维 × 字节。层数一乘，这是大头。没有 FlashAttention 时，注意力分数是 batch × 头数 × 长度 × 长度，长度一长先炸这个。FlashAttention 不物化整张分数，这一项掉下去，剩下的是隐藏状态和 MLP 的中间激活。

micro batch 减半，这些项大约减半。梯度累积把 global batch 加回来，峰值仍由一次前向决定。

参数的 16 字节不随长度变。长度从 4k 到 32k 仍 OOM，而参数账明明够，就是激活。

## 和并行的关系

张量并行把隐藏维切开，激活的一部分跟着降，通信每层都有。序列并行再把 LayerNorm 和 dropout 的激活沿长度切开，专门打这个随长度涨的部分，见 `sys-seq-parallel`。流水线不减少单级激活的峰值，只是别的级不在这张卡上。

## 代码

```python
def activation_bytes(batch, seq, hidden, layers, dtype_bytes=2):
    hidden_state = batch * seq * hidden * dtype_bytes * layers
    # FlashAttention does not store the seq x seq score matrix
    return hidden_state
```

## 追问

**重计算之后还存什么？** 只存每层或每若干层的边界激活，反向时重算中间。峰值从「所有层」变成「边界加上正在重算的那一段」。算力大约增加三分之一，见 `sys-mfu`。
