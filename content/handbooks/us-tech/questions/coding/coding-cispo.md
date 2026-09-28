---
id: coding-cispo
section: coding
order: 39
level: A
title: 白板：CISPO 和 PPO clip 的区别，clip 的是权重还是梯度
quick: >-
  PPO 的加权 logprob 形式：权重 $\mathrm{sg}(rA\cdot\mathrm{active})$，出界的 token 梯度直接是 0。
  CISPO：权重 $\mathrm{sg}(\mathrm{clip}(r))\cdot A$，出界的 token 仍有梯度，只是系数被截到上限。
  clamp 之后必须 detach，不然 clamp 的梯度会掺进来。
tags:
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention (CISPO)"
    url: https://arxiv.org/abs/2506.13585
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题怎么来的

`fireworks-grpo-sft-loss` 里推过：PPO / GRPO 的 clipped objective 等价于权重为 $\mathrm{sg}(r A\cdot\mathrm{active})$ 的加权 logprob。active 为假的 token 梯度是 0。MiniMax-M1 观察到，被 clip 掉的常常是 "However"、"Wait" 这类低概率、决定推理分叉的 token，第一次更新后 ratio 就出界，后面几个 off-policy step 里再也拿不到梯度。CISPO 的改法是只截断 IS 权重，不丢 token。

目标函数（token 级平均）：

$$
\mathcal{J}_{\mathrm{CISPO}} = \frac{1}{\sum_i|o_i|}\sum_i\sum_t \mathrm{sg}\big(\hat r_{i,t}\big)\,\hat A_{i,t}\,\log\pi_\theta(o_{i,t}),
\qquad
\hat r_{i,t} = \mathrm{clip}\big(r_{i,t},\,1-\varepsilon_{\mathrm{low}},\,1+\varepsilon_{\mathrm{high}}\big)
$$

给你的代码：

```python
def cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28):
    ratio = torch.exp(policy_logprobs - old_logprobs)
    w = ratio.clamp(1 - eps_low, 1 + eps_high)
    per_tok = -w * advantages * policy_logprobs
    return (per_tok * mask).sum() / mask.sum()
```

## 错在哪

`w` 没有 detach。$\hat r$ 本身是 $\theta$ 的函数，loss 的梯度变成两项：

$$
\nabla(-\hat r A\log\pi) = -\hat r A\,\nabla\log\pi \;-\; A\log\pi\,\nabla\hat r
$$

第二项在界内等于 $-A\log\pi\cdot r\,\nabla\log\pi$，出界时为 0。$\log\pi$ 是负数，量级还不小，这一项会让界内和界外的 token 行为完全不同，也不是任何目标函数的梯度。detach 之后只剩第一项，才是 CISPO。

```python
def cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28):
    ratio = torch.exp(policy_logprobs - old_logprobs).detach()
    w = ratio.clamp(1 - eps_low, 1 + eps_high)
    per_tok = -w * advantages * policy_logprobs
    return (per_tok * mask).sum() / mask.sum().clamp(min=1)
```

$\varepsilon_{\mathrm{low}} = 1$ 表示下界是 0，等于不设下界。论文只调上界，具体数值按任务调，这里的 0.28 只是占位。

## 和 PPO 并排

两者都写成 `-(w * logprobs)` 的形式，区别全在 `w`：

```python
def ppo_weight(ratio, adv, eps=0.2):
    active = torch.where(adv >= 0, ratio <= 1 + eps, ratio >= 1 - eps)
    return (ratio * adv * active).detach()

def cispo_weight(ratio, adv, eps_low=1.0, eps_high=0.28):
    return (ratio.clamp(1 - eps_low, 1 + eps_high) * adv).detach()
```

| 情况 | PPO | CISPO |
|---|---|---|
| $A>0$，$r > 1+\varepsilon$ | 0 | $(1+\varepsilon_{\mathrm{high}})A$ |
| $A<0$，$r < 1-\varepsilon$ | 0 | $\max(r, 1-\varepsilon_{\mathrm{low}})\cdot A$ |
| $A>0$，$r < 1-\varepsilon$ | $rA$ | $\max(r, 1-\varepsilon_{\mathrm{low}})\cdot A$ |
| 界内 | $rA$ | $rA$ |

PPO 的 clip 是个信任域：往有利方向走太远就停。CISPO 没有这个停止机制，靠的是权重有上界，单步更新幅度受控。

## 追问

**CISPO 还算 on-policy 的 policy gradient 吗？** $\mathrm{sg}(r)A\nabla\log\pi$ 在 $r$ 不被截断时就是 off-policy 的 IS 梯度，截断引入偏差、降低方差。它和 V-trace 截断 IS 权重是同一个思路。

**想要 PPO 的行为怎么办？** 论文给了带 token mask 的一般形式，mask 按 PPO 的规则取，就退回 PPO 的梯度。

**为什么 token 级平均而不是序列平均？** 论文沿用 DAPO 的 token-level loss，长回答不被稀释。见 `coding-grpo-loss-agg`。
