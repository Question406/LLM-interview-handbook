---
id: coding-embedding-lookup
section: coding
order: 14
level: S
title: 白板：embedding lookup + padding mask，大词表显存
quick: >-
  `E[ids]` 把 $[B,T]$ 的 id gather 成 $[B,T,D]$。`padding_idx` 那一行保持 0、梯度为 0，但注意力仍要
  padding mask，零向量照样能吃分数。显存是 $V\cdot D\cdot \mathrm{bytes}$；128k$\times$4096 bf16 约 1
  GB，tying 才省第二份。
tags:
  - Coding
  - Embedding
  - Memory
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.Embedding
    url: https://pytorch.org/docs/stable/generated/torch.nn.Embedding.html
    type: primary
  - title: scaled_dot_product_attention
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题怎么来的

看起来像 API 题，翻车点是 **pad 和 mask 不是一件事**、以及大词表把 embedding 矩阵当成「小表」。NVIDIA 问显存；Apple 问端侧词表；OpenAI debug 会漏 padding mask，pad 位置仍进 softmax。权重共享见 `coding-weight-tying`。

## Lookup：gather 一行，不是 matmul

$E\in\mathbb{R}^{V\times D}$，`ids` 形状 `[B, T]`，输出

$$
x_{b,t}=E_{\mathrm{ids}[b,t]}\in\mathbb{R}^{D},\qquad x\ \mathrm{shape}\ [B,T,D].
$$

实现是 index，不是 $U\times E$。`padding_idx=p` 时第 $p$ 行初始化为 0，**每次 backward 把该行梯度清零**，所以它学不会。这只保证 pad token 的向量固定为 0，**不保证** attention 忽略它：零向量和 $q$ 的点积是 0，softmax 仍给正质量。必须在 scores 上把 pad key 打成 $-\infty$，见 `apple-mha-code`、`coding-softmax-stable`。

```python
import torch
from torch import nn

def embed_forward(embed, ids, pad_id=0):
    # ids: [B, T] -> x: [B, T, D]
    x = embed(ids)
    pad = ids.eq(pad_id)  # [B, T]
    return x, pad


def attn_pad_mask(pad, qlen=None):
    # pad True = ignore this key; scores: [B, H, T, S]
    # mask broadcast: [B, 1, 1, S]
    key_pad = pad[:, None, None, :]
    return key_pad


class SmallLM(nn.Module):
    def __init__(self, vocab, dim, pad=0):
        super().__init__()
        self.pad = pad
        self.embed = nn.Embedding(vocab, dim, padding_idx=pad)

    def forward(self, ids):
        x, pad = embed_forward(self.embed, ids, self.pad)
        # scores += -inf where attn_pad_mask(pad)
        return x, pad


def check():
    m = SmallLM(100, 16, pad=0)
    ids = torch.tensor([[1, 2, 0], [3, 0, 0]])
    x, pad = m(ids)
    assert x.shape == (2, 3, 16)
    assert pad[0, 2] and (not pad[0, 0])
    assert torch.equal(x[0, 2], torch.zeros(16))
```

Loss 侧 `ignore_index=pad` 和 attention mask 是两道闸：一个不训练 pad 目标，一个不让 pad key 进上下文。只做一件，另一面仍漏。

## 大词表显存

$$
\mathrm{bytes}(E)=V\cdot D\cdot b,\quad b=2\ \mathrm{(bf16/fp16)},\ 4\ \mathrm{(fp32)}.
$$

Llama 3 词表 $V\approx 128256$，$D=4096$，bf16 一份 $\approx 1.05$ GB。再加 AdamW 的 $m,v$（fp32）大约 $\times 8$ 到参数自身。Tying 把 lm_head 那份省掉，optimizer state 也只留一套。词表并行：按 $V$ 切开，lookup 前 all-to-all id，是系统题，白板先报 1 GB 这个数。

Apple 端侧：词表大、ANE 上 gather 不连续，常压 int8 embedding 或缩小 $V$。不要假设「embedding 相对 70B 可忽略」——decode 时它和 lm_head 仍是 $V$ 维大 GEMM / gather。扩词表要同时改 tokenizer id 和 $E$ 的行数，新行初始化（均值、零、copy 相近 token）要说一声。

## 追问

- **零向量为什么还要 mask？** softmax($[\ldots,0]$) 仍给 pad 正质量。必须 $-\infty$。
- **`padding_idx` 的梯度？** PyTorch 每步把该行 grad 置 0，行向量保持 0。不要指望它学成「pad 语义」。
- **和 one-hot matmul？** 等价但浪费。Lookup 是稀疏 gather；反向只对出现过的行累加。
