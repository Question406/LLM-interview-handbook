---
id: coding-topk-nucleus
section: coding
order: 8
level: S
title: 白板：温度 → top-k → nucleus 的顺序，实现细节
quick: >-
  先把非法 token 打成 $-\infty$，再除温度 $T$，稳定 softmax，然后 top-k，再在剩余质量上做 nucleus。先截断再除
  $T$ 会得到另一套分布。至少留一个 token；$T\le 0$ 或 $p\le 0$ 走 greedy。
tags:
  - Coding
  - Sampling
  - Nucleus
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: The Curious Case of Neural Text Degeneration
    url: https://arxiv.org/abs/1904.09751
    type: primary
  - title: Generation strategies (Hugging Face)
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: secondary
  - title: torch.nn.functional.softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html
    type: primary
---

## 题怎么来的

Holtzman et al. 的 nucleus sampling 是解码默认件。Apple Siri MLE 电面把 sampling 和 attention 并列；OpenAI / Anthropic 推理岗会问温度和截断谁先谁后。公开实现（Transformers `generate`）是 **温度 → top-k → top-p**，白板要对齐，不要发明第四种顺序。稳定 softmax 见 `coding-softmax-stable`；和 greedy / beam 的取舍见 `coding-beam-search`。

## 顺序：先整形分布，再截尾

记 logits 为 $z$。非法位置先打 $-\infty$，再 $z' = z / T$（$T>0$），

$$
\pi_T=\mathrm{softmax}(z').
$$

Top-k：只保留 $\pi_T$ 里最大的 $k$ 个，其余置零。Nucleus（top-p）：在剩下的概率上按降序累计，取最小前缀使质量和 $\ge p$，其余丢掉，**核内重新归一化** 再采样。

$T$ 越小分布越尖，同一 $p$ 进核的 token 越少。所以 nucleus 必须定义在温度化之后的分布上。先按原始 softmax 截断再除 $T$，截尾集合不随温度变，和开源推理栈不一致。Top-k 与 top-p 同时开时，常见是先 k 再 p（HF 默认）；反过来保留集不同，必须写进注释和单测。

$T\to 0$ 或 $p\le 0$ 走 $\arg\max$，不要真除 0、不要把核裁空。$p=1$ 等于不截尾。

```python
import numpy as np

def sample_temp_k_p(logits, T, k, p, rng, mask=None):
    z = np.asarray(logits, dtype=np.float64)
    if mask is not None:
        z = np.where(mask, z, -np.inf)
    if not np.isfinite(z).any() or T <= 0 or p <= 0:
        z = np.where(np.isfinite(z), z, -np.inf)
        return int(np.argmax(z))
    z = z / T
    z = z - np.max(np.where(np.isfinite(z), z, -np.inf))
    z = np.where(np.isfinite(z), z, -np.inf)
    logp = z - np.logaddexp.reduce(z)
    prob = np.exp(logp)
    prob = np.where(np.isfinite(prob), prob, 0.0)
    if k is not None and 0 < k < prob.size:
        keep = np.argpartition(prob, -k)[-k:]
        q = np.zeros_like(prob)
        q[keep] = prob[keep]
        prob = q / q.sum()
    order = np.argsort(-prob)
    cdf = np.cumsum(prob[order])
    n = int(np.searchsorted(cdf, min(p, 1.0), side="left")) + 1
    keep = order[:n]
    q = np.zeros_like(prob)
    q[keep] = prob[keep]
    q /= q.sum()
    return int(rng.choice(q.size, p=q))
```

`searchsorted(..., side="left")+1` 保证至少一枚 token。全 mask 在入口挡一次，归一化后再挡一次。累计用概率序不是 logit 序：温度会改相对大小，但单调变换下 argmax 不变。

## 边界比公式容易翻车

不要在 logits 上做累计（质量含义不对）；截尾后不重新归一化就 `choice`（概率和小于 1）；把 $-\infty$ 拿去减 max（全体变 NaN）。Batch 里每条样本的核大小不同，不能假设同一个 `n`。重复惩罚若存在，规定清是改 logits 还是改概率，并且发生在 softmax 之前。

Apple 端侧还会问：top-k 在词表 $10^5$ 上要不要全排序。`argpartition` $O(V)$ 够；不要每步 `sort` 除非你要解释。Gumbel-max 是另一条采样路，见 `coding-gumbel-max`。

## 追问

- **为什么不能先 top-p 再温度？** 核依赖当前概率序。先截再改 $T$，等于在另一个分布上采样，和 Transformers 默认策略不一致。
- **$p=0$ 怎么办？** 裁空会让归一化失败。实现上当作 greedy。和 $T\to 0$ 应落到同一 token。
- **top-k 和 top-p 谁先？** 先约定再测。HF 常见先 k 后 p。两种顺序保留的 token 不同，不要口头含糊。
