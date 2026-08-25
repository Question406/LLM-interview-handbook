---
id: coding-cross-entropy
section: coding
order: 2
level: S
title: 白板：从 logits 写 cross entropy，不要先 softmax 再 log
quick: >-
  $\ell=-z_y+\mathrm{logsumexp}(z)$。减行 max 再 $\log\sum\exp$。禁止 `softmax` 再 `log`：下溢成
  $0$ 会得到 $-\infty$。pad 用 ignore 下标，分母是有效 token 数。
tags:
  - Coding
  - Cross Entropy
  - OpenAI
  - Numerical Stability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.functional.cross_entropy
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html
    type: primary
  - title: torch.nn.functional.log_softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.log_softmax.html
    type: primary
---

## 题怎么来的

研究岗 / MLE 白板的默认损失。OpenAI 给带 bug 的训练 loop 时，常见植入就是 `F.softmax` 再 `log` 再 NLL，fp16 下一训就 NaN。Apple 电面手写 attention 之后也会跟一句「训练时 logits 怎么接 CE」。PyTorch 的 `cross_entropy` 内部是 log-softmax + NLL，白板要对齐这个契约，不要自己造一条会下溢的路径。稳定 softmax 见 `coding-softmax-stable`。

## 公式：NLL 在 log 域一次做完

对一条样本的 logits $z$ 和类别 $y$：

$$
\ell=-z_y+\mathrm{logsumexp}(z),\qquad
\mathrm{logsumexp}(z)=m+\log\sum_j e^{z_j-m}.
$$

这就是 $-\log\mathrm{softmax}(z)_y$，但从不物化 $p_y$。$p_y$ 一旦下溢成 $0$，$\log 0$ 是 $-\infty$，梯度也没了。label smoothing 时目标不是 one-hot，要对整个 $q$ 做 $-q\cdot\log\pi$，不能只 gather 一列。

均匀初始化时 $\ell\approx\log V$。十万词表大约 $11.5$，用它判断第一步 loss 是不是假的。

```python
import torch
import torch.nn.functional as F

def cross_entropy_logits(logits, target, ignore_index=-100):
    # logits: [N, V] or [B * T, V], target: [N]
    z = logits.float()
    z = z - z.max(dim=-1, keepdim=True).values
    logp = z - z.exp().sum(dim=-1, keepdim=True).log()
    safe = target.clamp(min=0)
    nll = -logp.gather(1, safe.unsqueeze(1)).squeeze(1)
    mask = target != ignore_index
    return nll[mask].mean()


def lm_ce(logits, labels, ignore_index=-100):
    # logits, labels: [B, T, V] / [B, T]; causal LM 只 shift 一次
    return cross_entropy_logits(
        logits[:, :-1].reshape(-1, logits.size(-1)),
        labels[:, 1:].reshape(-1),
        ignore_index,
    )
```

`gather` 前 clamp 是怕 ignore 下标越界；真正平均只在 `mask` 上。不要对 pad 算完乘 $0$ 却仍除以 $N$。

## 序列：shift、ignore、分母

Causal LM：`logits[:, :-1]` 对 `labels[:, 1:]`。HuggingFace 传入 `labels=` 时内部会 shift，手写只做一次。评委要听你说 **分母是有效 token**，不是 batch 里所有格子；pad 多的 batch 否则 loss 被人为缩小。

fp16 下即使减了 max，极端值仍可能溢，这一步升 fp32 成本可忽略。OpenAI debug 口味：先固定 greedy + `eval()`，再看 CE 是不是 NaN，不要同时开 dropout 和采样。见 `openai-transformer-debug`。

## 追问

- **为什么禁止先 softmax 再 log？** $e^{z_y}/\sum e^{z}$ 在正确类 logit 很小或词表很大时下溢成 $0$。log-sum-exp 全程有限。
- **`F.nll_loss(F.log_softmax(z), y)` 可以吗？** 可以，这就是 `cross_entropy`。错的是 `nll_loss(softmax(z).log(), y)`。
- **label smoothing？** $q=(1-\varepsilon)e_y+\varepsilon/V$，loss 是对 $q$ 的 CE。PyTorch 的 `label_smoothing` 参数走这条，不是只改 $y$ 那一列。
- **和 KL 什么关系？** 对 one-hot 的 CE 等于 $H(q)+\mathrm{KL}(q\|\pi)$ 里 $q$ 是 delta 时的 NLL。别把分布自身的熵和 CE 混成一个数，见 `openai-entropy-l1`。
