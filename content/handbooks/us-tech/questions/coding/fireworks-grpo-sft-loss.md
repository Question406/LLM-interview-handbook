---
id: fireworks-grpo-sft-loss
section: coding
order: 35
level: S
title: Fireworks：把 clipped GRPO 写成 SFT 式的加权 logprob loss
quick: >-
  $\nabla r = r\,\nabla\log\pi$，所以 $-rA$ 的梯度等于 $-\mathrm{sg}(rA)\log\pi$ 的梯度。
  权重是 detach 后的 ratio × advantage × clip mask。A>0 时要 $r\le 1+\varepsilon$，A<0 时要 $r\ge 1-\varepsilon$。
  权重有正有负，不能除以 weights.sum()，要和原 loss 用同一种 mean。
tags:
  - Fireworks
  - GRPO
  - PPO
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 真题记录

本人 Fireworks 一轮面试复盘。给一个 `sft_loss(weights, logprobs)`，再给两版 GRPO：一版直接写 clipped objective，一版复用 `sft_loss`。问这个实现对不对，然后一路追问 importance ratio、advantage、clip mask，最后落到为什么两版梯度一样。

面试给的代码：

```python
import torch

def sft_loss(
    weights: torch.Tensor,   # [N], token weights
    logprobs: torch.Tensor,  # [N], token log probabilities
) -> torch.Tensor:
    """Return the weighted negative log-likelihood, summed over tokens."""
    weights = weights / weights.sum()
    loss = weights * logprobs
    loss = -loss.sum()
    return loss

def compute_grpo_loss_per_rollout(
    policy_logprobs: torch.Tensor,    # [N], requires gradients
    sampling_logprobs: torch.Tensor,  # [N], fixed rollout log-probs
    advantages: torch.Tensor,         # [N], fixed token advantages
    clip_eps: float = 0.2,
) -> torch.Tensor:
    ratio = torch.exp(policy_logprobs - sampling_logprobs)
    clipped_ratio = torch.clip(ratio, 1-clip_eps, 1+clip_eps)
    loss1 = ratio * advantages
    loss2 = clipped_ratio * advantages
    loss = torch.minimum(loss1, loss2)
    loss = -torch.mean(loss)

def compute_grpo_loss_per_rollout_with_sft_loss(
    policy_logprobs: torch.Tensor,
    sampling_logprobs: torch.Tensor,
    advantages: torch.Tensor,
    epsilon: float = 0.2,
) -> torch.Tensor:
    ratio = torch.exp(policy_logprobs - sampling_logprobs).detach()
    weights = ratio * advantages
    mask1 = ratio < 1 + epsilon
    mask2 = ratio > 1 - epsilon
    mask = torch.where(advantages > 0, mask1, mask2)
    weights = torch.where(mask, weights, 0)
    return sft_loss(weights, policy_logprobs)
```

## 哪里对，哪里错

思路是对的。`detach` 之后的 `ratio * advantages` 可以直接当权重，正负 advantage 各管一侧的 mask 也对。错在两处：

1. `compute_grpo_loss_per_rollout` 没有 `return loss`，函数返回 `None`。
2. `sft_loss` 里的 `weights / weights.sum()`。SFT 的权重非负，这样归一化没事。GRPO 的权重是 $rA$，advantage 可以是负的。

第二处举个例子。三个 token 的 advantage 都是 $-1$，ratio 约等于 1，权重是 `[-1, -1, -1]`，和是 $-3$。除完变成 `[1/3, 1/3, 1/3]`，符号整体翻过来，本来要压低概率的 token 被当成正样本往上推。一组里正负差不多抵消时 `weights.sum()` 接近 0，梯度直接爆掉。就算权重全是正的，除以和也改了梯度的尺度，和直接写的那版对不上。

改法：和原 objective 用同一种 reduction，这里是按 token 数取平均。

```python
loss = -(weights * policy_logprobs).mean()
```

## 为什么 ratio × advantage 能当权重

令 $r(\theta) = \pi_\theta / \pi_{\mathrm{old}}$。$\pi_{\mathrm{old}}$ 是常数，所以

$$
\nabla_\theta r = \frac{\nabla_\theta \pi_\theta}{\pi_{\mathrm{old}}} = r\,\nabla_\theta \log \pi_\theta
$$

不 clip 时单个 token 的 loss 是 $L = -rA$，梯度是

$$
\nabla_\theta L = -rA\,\nabla_\theta \log \pi_\theta
$$

构造一个 surrogate，把 $rA$ 当常数：

$$
L_{\mathrm{sur}} = -\mathrm{sg}(rA)\,\log \pi_\theta,
\qquad
\nabla_\theta L_{\mathrm{sur}} = -rA\,\nabla_\theta \log \pi_\theta
$$

两个梯度在当前参数处相等。权重 $rA$ 是从梯度形式推出来的，不是另外设计的。`detach` 必须有：不 detach 的话，梯度还会从 ratio 这条路再走一遍，多出一项 $-rA\log\pi\,\nabla\log\pi$，等价就没了。

## Clip mask

clipped objective：

$$
L = -\min\big(rA,\ \mathrm{clip}(r, 1-\varepsilon, 1+\varepsilon)\,A\big)
$$

$A>0$：想提高这个 token 的概率。$r > 1+\varepsilon$ 时 min 取到 clip 那一支，是常数，梯度为 0。$r < 1-\varepsilon$ 时 min 取的是 $rA$，梯度照常。所以有梯度的条件只有 $r \le 1+\varepsilon$。

$A<0$：想压低概率。$r < 1-\varepsilon$ 时进入平台，梯度为 0。有梯度的条件是 $r \ge 1-\varepsilon$。

面试代码里 `mask1`、`mask2` 就是这两条，只是用了严格不等号，边界上是测度为零的情况，不影响。$A=0$ 走哪一支都一样，权重是 0。

```python
active = torch.where(
    advantages >= 0,
    ratio <= 1 + epsilon,
    ratio >= 1 - epsilon,
)
weights = ratio * advantages * active
```

容易写错的是两侧都 clip，即 `(ratio >= 1 - eps) & (ratio <= 1 + eps)`。$A>0$ 且 $r$ 已经很小时，这个 token 被错误地掐掉了。PPO 的 min 是悲观下界，只挡住「往有利方向走太远」的那一侧。

## 修好的两版

直接写 clipped objective：

```python
def compute_grpo_loss_per_rollout(policy_logprobs, sampling_logprobs, advantages, clip_eps=0.2):
    ratio = torch.exp(policy_logprobs - sampling_logprobs)
    clipped_ratio = ratio.clamp(1 - clip_eps, 1 + clip_eps)
    objective = torch.minimum(ratio * advantages, clipped_ratio * advantages)
    return -objective.mean()
```

SFT 式 surrogate：

```python
def compute_grpo_loss_per_rollout_with_sft_loss(policy_logprobs, sampling_logprobs, advantages, epsilon=0.2):
    ratio = torch.exp(policy_logprobs - sampling_logprobs).detach()
    active = torch.where(
        advantages >= 0,
        ratio <= 1 + epsilon,
        ratio >= 1 - epsilon,
    )
    weights = (ratio * advantages * active).detach()
    return -(weights * policy_logprobs).mean()
```

面试时可以顺手说怎么验：同一组 `policy_logprobs` 分别过两版，`torch.autograd.grad` 取梯度，`allclose` 应该成立。loss 的数值不会一样。

```python
lp = torch.randn(8, requires_grad=True)
old = lp.detach() + 0.3 * torch.randn(8)
adv = torch.randn(8)
g1, = torch.autograd.grad(compute_grpo_loss_per_rollout(lp, old, adv), lp)
g2, = torch.autograd.grad(compute_grpo_loss_per_rollout_with_sft_loss(lp, old, adv), lp)
assert torch.allclose(g1, g2)
```

## 追问

**两版 loss 数值一样吗？** 不一样。$r=1$ 时直接写的是 $-\mathrm{mean}(A)$，surrogate 是 $-\mathrm{mean}(A\log\pi)$。只有对 `policy_logprobs` 的梯度相等。所以拿 surrogate 的 loss 曲线当 RL 的 objective 看没有意义，要看 reward、KL、clip fraction。

**这还算 SFT 吗？** 形式上是加权 NLL，但权重可以是负的。$A>0$ 权重为正，提高 token 概率；$A<0$ 权重为负，压低概率。准确的叫法是 weighted log-likelihood surrogate。好处是：只要训练端支持逐 token 权重的 NLL，不改 loss 代码就能跑 GRPO。

**只在当前参数处等价，是什么意思？** 权重是这一步 detach 下来的常数。做完一次 optimizer step，$\pi_\theta$ 变了，ratio 和 mask 都要用新的 `policy_logprobs` 重算。同一批 rollout 上跑多个 mini-epoch，每个 step 都要重新构造权重，不能缓存第一次的。

**KL 项怎么办？** 对参考模型的 KL 不在这个 min 里。可以把它的梯度系数也折进权重，或者单独加一项 loss。token 级 KL 的写法见 `coding-kl-div`，放在 reward 还是 loss 里见 `sys-kl-place`。
