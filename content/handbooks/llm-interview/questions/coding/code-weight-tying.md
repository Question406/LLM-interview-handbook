---
id: code-weight-tying
section: coding
order: 56
level: A
title: 手写 embedding / lm_head 权重共享：同一块存储，梯度怎么流
quick: >-
  `lm_head.weight` 和 `emb.weight` 指向同一存储，$V\times d$ 只存一份。前向
  $\mathrm{logits}=h W^\top$，反向两边的梯度加到同一张表上：embedding 的 gather 梯度和 lm_head 的
  外积梯度。不要 `clone` 成两份 Parameter，那样既不省参，梯度也对不上。bias 通常没有。
tags:
  - WeightTying
  - Embedding
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Using the Output Embedding to Improve Language Models
    url: https://arxiv.org/abs/1608.05859
    type: primary
---

GPT-2 / 很多小模型默认 tying。LLaMA 不 tying，`lm_head` 是独立的 $d\times V$。面试问「为什么 7B 的 embedding 和输出层参数对不上 2 倍词表」时，先确认有没有 tying。

## 写法

$$
h=\mathrm{Emb}(x),\quad \mathrm{logits}=h W^\top,\quad W=\mathrm{Emb}.\mathrm{weight}.
$$

```python
import torch.nn as nn

class TiedLM(nn.Module):
    def __init__(self, vocab, d):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.lm_head = nn.Linear(d, vocab, bias=False)
        self.lm_head.weight = self.emb.weight          # 同一块存储

    def forward(self, idx):
        return self.lm_head(self.emb(idx))            # [B,T,V]
```

`data_ptr()` 相同就对了。优化器里这两层不要注册成两个独立参数，否则 Adam 状态会翻倍、更新写两次。`named_parameters()` 去重看 `id(p)`。

Untied 时两张表梯度各算各的，输出层可以学到和输入嵌入不同的几何。大词表 + 大 $d$ 时不 tying 更常见，因为输出层想要的特征和输入嵌入不一定一样。

## 追问

- **省多少参数？** 一份 $V d$。$V=128\mathrm{k}$、$d=4096$、fp16 大约 1 GB。
- **和 LoRA？** 只挂 `lm_head` 或只挂 `emb` 时，另一侧不会自动有低秩更新，除非共享那张 $\Delta W$。
- **梯度会冲掉 embedding 吗？** 会叠加。学习率对输入侧偏大时，用较小的 emb lr 或单独 clip。
