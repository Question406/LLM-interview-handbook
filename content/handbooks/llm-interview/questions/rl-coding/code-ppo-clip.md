---
id: code-ppo-clip
section: rl-coding
order: 4
level: A
title: 手写 PPO clipped surrogate，并解释 $A$ 的符号
quick: >-
  $L=\min(\rho A,\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)A)$。Clip
  不会把真实 $\rho$ 拉回区间，只是让越界且「有利」的一侧梯度为 0。$A\gt 0$ 时上限 $1+\varepsilon$ 生效；$A\lt 0$ 时下限 $1-\varepsilon$ 生效。
tags:
  - PPO
  - Clip
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Proximal Policy Optimization
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

现场最容易写错两件事：把 `clip` 当成对 $\rho$ 的硬约束；以及不管 $A$ 的符号就说「ratio 被夹在 $[1-\varepsilon,1+\varepsilon]$」。

## 公式

$$
\rho=\exp(\log\pi_\theta-\log\pi_{\mathrm{old}}),\qquad
L(\theta)=\min\big(\rho A,\;\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)\,A\big).
$$

最大化 $L$（实现里常写 `-L.mean()`）。当 $A\gt 0$，希望增大 $\rho$，但超过 $1+\varepsilon$ 后 $\min$ 选中常数项，该样本梯度为 0。当 $A\lt 0$，希望减小 $\rho$，低于 $1-\varepsilon$ 后同样被掐掉。另一侧（$A\gt 0$ 且 $\rho$ 很小，或 $A\lt 0$ 且 $\rho$ 很大）不 clip，让策略从「走错的方向」拉回来。

CISPO 不同：它 clip 的是 IS 权重并 detach，梯度仍走 $\log\pi$。见 `pt-cispo`、`pt-ppo-clip`。GAE、组优势和 GSPO 的序列比怎么接上这段 clip，以及 TRL / verl 的配置名，见 `code-ppo-grpo-gspo`。

```python
import torch

def ppo_clip_loss(logp, old_logp, adv, eps=0.2):
    rho = (logp - old_logp).exp()
    unclipped = rho * adv
    clipped = torch.clamp(rho, 1 - eps, 1 + eps) * adv
    # maximize min(...)  <=>  minimize negative
    return -torch.minimum(unclipped, clipped).mean()
```

## 追问

- **$\rho$ 真的被夹住了吗？** 没有。网络仍可把 $\rho$ 推到 10，只是这些 token 本轮不提供更新。
- **要不要对 $A$ 做标准化？** 组内 / batch 标准化改变哪些样本被 clip，和 GRPO 组相对是同一类设计。
- **和 value clip？** PPO 还有 value function clip，是另一项；本题只写 policy surrogate。
