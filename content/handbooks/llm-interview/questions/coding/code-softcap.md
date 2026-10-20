---
id: code-softcap
section: coding
order: 48
level: A
title: 手写 Gemma-2 的 softcap：tanh 压 scores / logits，和 clip 差在可导
quick: >-
  $\mathrm{softcap}(x,c)=c\cdot\tanh(x/c)$。Gemma-2 对 attention scores 用 $c=50$，对最终
  logits 用 $c=30$，都在 softmax 之前。值域 $(-c,c)$，两端饱和但导数不为 0。不要写成
  `clamp(-c,c)`，那是硬截断，反传在外面是 0。
tags:
  - Softcap
  - Gemma
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Gemma 2 Technical Report
    url: https://arxiv.org/abs/2408.00118
    type: primary
---

深层网络中，$QK^\top/\sqrt{d}$ 偶尔会达到几百，使 softmax 的概率几乎集中到一个位置。softcap 将分数压缩到有界区间，有助于稳定训练。和 QK-Norm 可以同时存在，Gemma-2 用的是 softcap + 局部/全局交替。

## 公式

$$
\mathrm{softcap}(x,c)=c\tanh(x/c).
$$

$x\ll c$ 时 $\tanh(x/c)\approx x/c$，输出约等于 $x$，几乎不改小分数。$|x|\gg c$ 时逼近 $\pm c$。

```python
import torch

def softcap(x, cap):
    return cap * torch.tanh(x / cap)

def attn_scores_capped(q, k, cap=50.0):
    scores = q @ k.transpose(-1, -2) / (q.size(-1) ** 0.5)
    return softcap(scores, cap)

def logits_capped(logits, cap=30.0):
    return softcap(logits, cap)
```

加 cap 的位置：causal / padding mask 的 $-\infty$ 要在 cap **之后** 再填。先 cap 再填没问题；先填 $-\infty$ 再 `tanh`，`-inf/c` 仍是 `-inf`，`tanh` 得到 -1，再乘 $c$ 变成 $-c$，被 mask 的位置只是很小而不是零概率。顺序必须是：算 scores → softcap → masked_fill(-inf) → softmax。

## 追问

- **最终 logits 为什么也 cap？** 词表很大时，个别 logit 可能异常增大，影响采样和交叉熵损失（CE）的数值稳定性。$c=30$ 是 Gemma-2 的数，别背成 50。
- **和 z-loss？** z-loss 往 $\log\sum e^{z}$ 上加惩罚，改训练目标；softcap 改的是前向函数本身。
- **推理能去掉吗？** 训练时用了，推理必须留着，否则分布对不上。
