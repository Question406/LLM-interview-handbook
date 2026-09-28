---
id: coding-dropout
section: coding
order: 9
level: S
title: 白板：dropout mask 训练/推理缩放（inverted dropout）
quick: >-
  训练时每个单元以概率 $p$ 置零，留下的乘 $1/(1-p)$，期望不变。推理关掉 mask，不再缩放。不要训练除
  $1-p$、推理再乘 $1-p$，那是 inverted 之前的旧写法，和 PyTorch 默认相反。
tags:
  - Coding
  - Dropout
  - Regularization
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Dropout — A Simple Way to Prevent Neural Networks from Overfitting
    url: https://jmlr.org/papers/v15/srivastava14a.html
    type: primary
  - title: torch.nn.functional.dropout
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.dropout.html
    type: primary
---

## 题怎么来的

Srivastava et al. 2014 的 dropout 是面试里最容易写反缩放的一层。OpenAI Transformer debug 会把 `train()` / `eval()` 混用：mask 改对了也对不齐。Apple 手写 MHA 之后会问 attention dropout 推理要不要留。PyTorch 默认是 inverted dropout：缩放发生在训练。白板把期望说清楚，比背 `p=0.1` 有用。

## 训练乘 $1/(1-p)$，推理恒等

输入 $x$ 形状 `[B, T, D]`（或注意力权重 `[B, H, T, S]`）。训练：

$$
m_i\sim\mathrm{Bernoulli}(1-p),\qquad
y=\frac{m}{1-p}\odot x.
$$

$\mathbb{E}[y\mid x]=x$，所以推理直接 $y=x$，不必再乘 $1-p$。这就是 inverted dropout。旧论文写法是训练只乘 mask、推理乘 $1-p$；那要求推理图和训练图不一致，框架不爱用。PyTorch `F.dropout` 走 inverted：`train=False` 时原样返回。

$p=0$ 等于关掉；$p=1$ 训练输出全 0，没有定义良好的 $1/(1-p)$，实现上应拒绝或当成「全丢」。Broadcast：mask 和 $x$ 同 shape；不要只在 batch 维丢，否则整句一起死。

```python
import torch

def dropout(x, p, training, generator=None):
    if (not training) or p == 0.0:
        return x
    if p < 0.0 or p >= 1.0:
        raise ValueError("p must be in [0, 1)")
    keep = 1.0 - p
    mask = torch.empty_like(x).bernoulli_(keep, generator=generator)
    return x * mask / keep

def attn_with_dropout(scores, p, training):
    # scores: [B, H, T, S] already masked with -inf
    w = torch.softmax(scores, dim=-1)
    w = dropout(w, p, training)
    return w

def check():
    g = torch.Generator().manual_seed(0)
    x = torch.ones(4, 8)
    y = dropout(x, 0.5, True, g)
    z = dropout(x, 0.5, False)
    assert z.equal(x)
    assert y.max() <= 2.0 + 1e-6
```

注意力 dropout 打在 softmax 之后的权重上，不是打在 logits 上。打在 logits 等于随机把某些 key 打成 $-\infty$，分布会再归一化，语义不同。残差旁的 dropout 和 attention dropout 是两份独立 mask。

## 和 debug / 端侧

评测、greedy 对齐、KV cache 对比必须 `eval()`：训练态 dropout 会让「有 cache / 无 cache」对不上。OpenAI 那轮先固定观测再改 bug，见 `openai-transformer-debug`。Apple 端侧推理 $p=0$，训练图里的除法不会出现在 ANE 上；不要把训练缩放常量编译进推理。

Seed：要复现必须把 generator 传进去。`torch.dropout` 在不同设备上的 Bernoulli 实现可能不同，单测钉 CPU。LayerDrop / DropPath 是「整层一个 Bernoulli」，不是逐元素，别混。

## 追问

- **为什么不在推理乘 $1-p$？** inverted dropout 已经把期望留在训练。推理再乘会把激活整体缩小，和 checkpoint 不匹配。
- **mask 要不要过梯度？** 离散 mask 当常数。反向就是把 upstream grad 乘同一份 `mask/(1-p)`。不要对 Bernoulli 再反传。
- **和 DropConnect？** Dropout 丢激活；DropConnect 丢权重。白板默认逐元素激活。Transformer 里 FFN 和 attention 各有各的 $p$。
