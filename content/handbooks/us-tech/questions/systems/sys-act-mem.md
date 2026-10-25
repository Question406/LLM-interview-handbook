---
id: sys-act-mem
section: systems
order: 64
level: B
title: 系统：激活显存随序列长度怎么涨，和参数的 16 字节怎么分开？
quick: "参数状态的 16 字节不随序列长度变，激活则随 batch、长度、层数和隐藏维增长，未优化的 attention 分数还随长度平方增长。长度增加后 OOM，先看重计算、microbatch 和序列并行，再判断状态分片是否有帮助。"
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

激活显存会随输入长度增加，参数状态本身不会。比如参数账能放下，但长度从 4k 提到 32k 后 OOM，优先查激活、attention 工作区和本地 microbatch。

`sys-param-bytes` 给出参数状态的估算，这里补上激活项。这是按机制整理的估算题，重计算的细节见 `sys-act-checkpoint`。

每一层保存的隐藏状态大约是 batch × 长度 × 隐藏维 × 字节。层数一乘，这是大头。没有 FlashAttention 时，注意力分数大小是 batch × 头数 × 长度 × 长度，长度增加后这项可能最先耗尽显存。FlashAttention 不物化整张分数，这一项掉下去，剩下的是隐藏状态和 MLP 的中间激活。

micro batch 减半，这些项大约减半。梯度累积把 global batch 加回来，峰值仍由一次前向决定。

估算时把参数的 16 字节与这些随长度变化的量分开，才能看出是哪一项导致峰值增长。

张量并行把隐藏维切开，激活的一部分跟着降，通信每层都有。序列并行再把 LayerNorm 和 dropout 的激活沿长度切开，专门打这个随长度涨的部分，见 `sys-seq-parallel`。流水线不减少单级激活的峰值，只是别的级不在这张卡上。

## 代码

```python
def activation_bytes(batch, seq, hidden, layers, dtype_bytes=2):
    hidden_state = batch * seq * hidden * dtype_bytes * layers
    # FlashAttention does not store the seq x seq score matrix
    return hidden_state
```

## 追问

**重计算之后还存什么？**
只存每层或每若干层的边界激活，反向时重算中间。峰值从「所有层」变成「边界加上正在重算的那一段」。算力大约增加三分之一，见 `sys-mfu`。
