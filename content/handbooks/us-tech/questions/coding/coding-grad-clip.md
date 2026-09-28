---
id: coding-grad-clip
section: coding
order: 10
level: A
title: 白板：global norm clip， inf/nan 怎么处理
quick: >-
  先把所有参数梯度拼成一个大向量，算 $L_2$ 总范数 $g$。若 $g>\mathrm{max}$，全体乘 $\mathrm{max}/(g+\varepsilon)$。总范数非有限时不要静默缩放：报错、跳过 step，或按
  `error_if_nonfinite` 处理。混合精度要先 unscale。
tags:
  - Coding
  - Gradient Clipping
  - NVIDIA
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.utils.clip_grad_norm_
    url: https://pytorch.org/docs/stable/generated/torch.nn.utils.clip_grad_norm_.html
    type: primary
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5065
    type: primary
---

## 题怎么来的

Pascanu et al. 把 global norm clip 写成 RNN 训练的标配；LLM 预训练同样依赖它兜 overflow。NVIDIA 训练岗爱问「clip 的是什么范数、inf 怎么办」；OpenAI / Meta 的训练代码题会把 clip 放在 scaler 前面当植入 bug。PyTorch 入口是 `clip_grad_norm_`。和 AdamW 的衔接见 `coding-adamw`。

## Global $L_2$：一个标量管所有参数

$$
g=\sqrt{\sum_i \|h_i\|_2^2},\qquad
c=\min\bigl(1,\ \mathrm{max\_norm}/(g+\varepsilon)\bigr),\qquad
h_i\leftarrow c\,h_i.
$$

$h_i$ 是每个参数的 `.grad`。这是全局范数，不是逐层各自 clip。逐层 clip 会改变层与层之间的相对步长；global 只保证整步更新的欧氏长度不超过 `max_norm`。$g\le \mathrm{max}$ 时 $c=1$，梯度不动。

不要对每个 tensor 单独除自己的范数再乘 max，那是 per-tensor clip，和 `clip_grad_norm_` 不是一回事。`clip_grad_value_` 是逐元素夹紧，也不是 global norm。

```python
import math
import torch

def total_grad_norm(params, eps=1e-6):
    total = 0.0
    for p in params:
        if p.grad is None:
            continue
        g = p.grad.detach().float()
        if not torch.isfinite(g).all():
            return float("inf")
        total += float(g.norm(2).item() ** 2)
    return math.sqrt(total)

def clip_grad_norm_(params, max_norm, eps=1e-6, error_if_nonfinite=True):
    params = [p for p in params if p.grad is not None]
    g = total_grad_norm(params, eps)
    if not math.isfinite(g):
        if error_if_nonfinite:
            raise RuntimeError("non-finite grad norm")
        return g
    clip = max_norm / (g + eps)
    if clip < 1.0:
        for p in params:
            p.grad.mul_(clip)
    return g
```

返回值 $g$ 是 clip 之前的范数，用来打日志：突然变 `inf` 就是这条 batch 坏了。$\varepsilon$ 只防 $g=0$ 时除零；正常训练 $g$ 不会真是 0。

## inf / nan：不要乘一个 NaN 系数

若某个 `.grad` 已是 inf/nan，$g$ 非有限，`max_norm/g` 也是 NaN，再 `mul_` 会把所有参数的梯度毒成 NaN，整次 run 报废。PyTorch 1.13+ 的 `error_if_nonfinite=True` 直接抛。训练实践：

1. 跳过这一 step（zero_grad，不 `optimizer.step`）；
2. 或直接 crash，留 checkpoint 回滚；
3. 不要「当 0 继续训」却不打日志。

混合精度：`GradScaler.unscale_(opt)` 之后再 clip。先 clip 再 unscale，等于在放大过的 fp16 梯度上算范数，阈值对不上。For-each kernel 和单 tensor 循环在有限情况下应给出同一 $g$；有 inf 时 foreach 路径的行为要查当前版本文档，白板说「先查有限性再算范数」更稳。

NVIDIA 还会问：clip 改变的是更新方向的长度，不改变各坐标的相对比例。Loss 本身爆 inf 时 clip 救不了，要先查数据、overflow、没减 max 的 softmax，见 `coding-softmax-stable`。

## 追问

- **为什么用全局而不是逐层？** 全局保持层间相对尺度；逐层等于每层自己做一次单位化，深层/浅层步长被强行拉齐。
- **$g=0$？** 全参数无梯度（忘了 backward、全被 mask）。不要 step。$\varepsilon$ 只是除零保护。
- **和 grad scaler 的顺序？** unscale → clip → step → scaler.update。反了阈值错，还可能把 inf 写进 master weight。
