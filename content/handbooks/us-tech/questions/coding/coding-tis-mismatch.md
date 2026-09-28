---
id: coding-tis-mismatch
section: coding
order: 40
level: A
title: 白板：推理引擎的 logprob 和训练端对不上，截断重要性权重怎么加
quick: >-
  rollout 来自推理引擎 $\mu$，PPO 的 $\pi_{\mathrm{old}}$ 应该用训练端在同一份权重上重算的 logprob。
  两者的差用一个额外的权重 $w=\min(\pi_{\mathrm{old}}/\mu,\,C)$ 修正，$w$ 是常数，必须 detach。
  把 $\mu$ 直接当 $\pi_{\mathrm{old}}$，clip 会被数值误差触发。
tags:
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "IMPALA: Scalable Distributed Deep-RL with Importance Weighted Actor-Learner Architectures (V-trace)"
    url: https://arxiv.org/abs/1802.01561
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题怎么来的

rollout 用 vLLM / SGLang 这类推理引擎生成，训练用 FSDP / Megatron 前向。权重相同，kernel、精度、batch 形状不同，同一个 token 的 logprob 就不同。名义上 on-policy，实际上采样分布 $\mu$ 和训练端的 $\pi_{\mathrm{old}}$ 不是同一个分布。怎么排查差异见 `sys-rollout-logprob`，这道题只管 loss 里怎么修正。

给你的代码：

```python
def ppo_loss(policy_logprobs, rollout_logprobs, advantages, mask, eps=0.2):
    # rollout_logprobs 来自推理引擎
    ratio = torch.exp(policy_logprobs - rollout_logprobs)
    obj = torch.minimum(ratio * advantages, ratio.clamp(1 - eps, 1 + eps) * advantages)
    return -(obj * mask).sum() / mask.sum()
```

## 错在哪

这里的 ratio 把两件事乘在了一起：

$$
\frac{\pi_\theta}{\mu} = \underbrace{\frac{\pi_\theta}{\pi_{\mathrm{old}}}}_{\text{策略这一步变了多少}}\cdot\underbrace{\frac{\pi_{\mathrm{old}}}{\mu}}_{\text{两套实现的差}}
$$

clip 的本意是限制第一项。第二项和优化无关，却也会让 ratio 出界：第一步更新之前 $\pi_\theta = \pi_{\mathrm{old}}$，本该所有 token 都在界内，结果一部分 token 因为数值差被 clip 掉，拿不到梯度。低概率 token 上两套实现的相对误差最大，恰好是最该学的那些。

## 改法

训练端在更新前用 $\theta_{\mathrm{old}}$ 重算一遍 logprob，作为 PPO 的 $\pi_{\mathrm{old}}$。实现差异用单独的截断 IS 权重修正：

$$
w_t = \min\Big(\frac{\pi_{\mathrm{old}}(y_t)}{\mu(y_t)},\,C\Big)
$$

```python
def ppo_loss_tis(policy_logprobs, old_logprobs, rollout_logprobs, advantages, mask, eps=0.2, C=2.0):
    # old_logprobs: 训练端在 theta_old 上重算，no_grad
    ratio = torch.exp(policy_logprobs - old_logprobs)
    obj = torch.minimum(ratio * advantages, ratio.clamp(1 - eps, 1 + eps) * advantages)
    w = torch.exp(old_logprobs - rollout_logprobs).clamp(max=C).detach()
    return -(w * obj * mask).sum() / mask.sum().clamp(min=1)
```

$w$ 里没有 $\pi_\theta$，本来就不带梯度，detach 是为了防止 `old_logprobs` 忘了在 `no_grad` 下算。

$C$ 越大偏差越小、方差越大。只截上界：$\pi_{\mathrm{old}}/\mu$ 很小的 token 权重接近 0，本来就不会爆。V-trace 截断 IS 权重是同一个做法。

## 一个常见的错写

```python
w = torch.exp(policy_logprobs - rollout_logprobs).clamp(max=C)
```

用了当前的 $\pi_\theta$，而且没 detach。第一个 mini-epoch 数值上和正确写法一样，梯度却多了一条穿过 $w$ 的路径；第二个 mini-epoch 起连数值都不一样，$w$ 把策略这一步的变化又算了一次。

## 追问

**多花一次前向值得吗？** 重算 $\pi_{\mathrm{old}}$ 要多一次训练端前向。只做一次更新（一个 mini-epoch）时 $\pi_\theta$ 和 $\pi_{\mathrm{old}}$ 的数值相同，可以直接用当前前向 detach 当 $\pi_{\mathrm{old}}$，省掉这次前向。

**要监控什么？** $\log(\pi_{\mathrm{old}}/\mu)$ 的均值和分位数，以及 $w$ 被截断的 token 比例。比例突然升高，通常是推理引擎的权重同步出了问题，不是模型在学，见 `sys-weight-remap`。

**序列级还是 token 级？** 序列级权重是 token 权重的连乘，长回答上方差爆炸。token 级截断有偏但稳，实践里多用 token 级。
