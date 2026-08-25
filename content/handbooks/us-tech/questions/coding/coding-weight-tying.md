---
id: coding-weight-tying
section: coding
order: 11
level: A
title: 白板：embedding 与 lm_head 权重共享，梯度怎么流
quick: >-
  `lm_head.weight` 和 `embed.weight` 同一块存储，形状都是 $[V, D]$。前向 lookup 用 $E$，logits 是
  $h E^\top$。反向两条路的梯度累加到同一份 $E$。省 $VD$ 个参数；Llama 通常不绑，GPT-2 绑。
tags:
  - Coding
  - Weight Tying
  - Embedding
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Using the Output Embedding to Improve Language Models (Press & Wolf)
    url: https://arxiv.org/abs/1608.05859
    type: primary
  - title: torch.nn.Embedding
    url: https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html
    type: primary
---

## 题怎么来的

Press & Wolf、Inan et al. 把输入 embedding 和输出投影绑成同一矩阵。GPT-2 / GPT-3 风格模型默认 tying；Llama 2/3 公开实现 **不绑**，`lm_head` 是独立的 $[V, D]$。OpenAI / Google 白板爱问「省了什么、梯度会不会算两遍」。Lookup 显存见 `coding-embedding-lookup`。

## 同一份 $E$：lookup 进，inner product 出

`nn.Embedding(V, D).weight` 是 $[V, D]$。`nn.Linear(D, V, bias=False).weight` 也是 $[V, D]$（PyTorch Linear 存 $[out, in]$）。绑定时：

$$
x = E_{\mathrm{id}},\qquad \mathrm{logits} = h E^\top \in \mathbb{R}^{V}.
$$

不要再 transpose 一份参数。`self.lm_head.weight = self.embed.weight` 是引用，不是 copy。Optimizer 只能看到一个 param；state 里不要给 head 再开一套 $m,v$。

```python
import torch
from torch import nn

class TiedLM(nn.Module):
    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)
        self.ln = nn.LayerNorm(dim)
        self.lm_head = nn.Linear(dim, vocab, bias=False)
        self.lm_head.weight = self.embed.weight  # same storage

    def forward(self, ids, targets=None):
        # ids: [B, T]
        h = self.ln(self.embed(ids))
        logits = self.lm_head(h)  # [B, T, V]
        if targets is None:
            return logits
        return torch.nn.functional.cross_entropy(
            logits[:, :-1].reshape(-1, logits.size(-1)),
            targets[:, 1:].reshape(-1),
            ignore_index=0,
        )


def check_tied():
    m = TiedLM(32, 8)
    assert m.lm_head.weight.data_ptr() == m.embed.weight.data_ptr()
    ids = torch.randint(1, 32, (2, 5))
    m(ids, ids).backward()
    assert m.embed.weight.grad is not None
```

`data_ptr` 相同才能算绑上。若 `load_state_dict` 后又 `lm_head = Linear(...)` 重建，引用会断，变成两份权重。

## 梯度：两条路加到同一块

前向两条使用：$E$ 的第 $t$ 行被 gather 进 hidden；同一 $E$ 又和 $h$ 做点积出 logits。反向：

- CE → logits → $h E^\top$ 对 $E$ 的梯度是 $\sum_t h_t^\top (\partial L/\partial \mathrm{logits}_t)$；
- embedding lookup 对出现过的行累加 $\partial L/\partial h_t$。

Autograd 对同一 storage 做 **accumulate**。不要自己再乘 2，也不要 `detach` 其中一条路。Pad 行若 `padding_idx` 置零梯度，两条路都不应更新那一行。Bias：输出层多一个 $b\in\mathbb{R}^{V}$ 可以不绑；GPT-2 的 lm_head 无 bias。

显存：不绑要两份 $V\times D$。$V=128256$，$D=4096$，bf16 一份约 1 GB，绑了省一份。FSDP / tensor parallel 下两份必须 shard 成同一 layout，否则 all-gather 对不齐。Llama 不绑是质量和实现选择，不是 tying 错了。

## 追问

- **logits 为什么是 $h E^\top$ 不是 $h E$？** $E$ 行是 token 向量，$h$ 和某行点积才是该 token 的 logit。$h E$ 形状对不上。
- **AdamW 的 $m,v$？** 一份权重一份 state。绑了却给 head 再建 state，等于 decay / 更新打到幽灵参数上。
- **扩词表？** 两行一起扩，新 id 的初始化两边是同一行。只扩 embedding 不扩 head 会在 tying 下直接 shape 冲突。
