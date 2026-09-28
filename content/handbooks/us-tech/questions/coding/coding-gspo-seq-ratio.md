---
id: coding-gspo-seq-ratio
section: coding
order: 38
level: A
title: 白板：GSPO 的序列级 ratio，写成 token 上的加权 logprob loss
quick: >-
  $s_i = \exp\big(\frac{1}{|y_i|}\sum_t(\log\pi_\theta - \log\pi_{\mathrm{old}})\big)$，是 token ratio 的几何平均，
  不是算术平均。clip 在序列上做，一条回答要么全有梯度要么全没有。
  换成加权 logprob：每个 token 的权重是 $\mathrm{sg}(s_iA_i\cdot\mathrm{active}_i)/|y_i|$。
tags:
  - Coding
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Group Sequence Policy Optimization (GSPO)
    url: https://arxiv.org/abs/2507.18071
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题怎么来的

GRPO 的 advantage 是序列级的，ratio 却是 token 级的。GSPO 把 ratio 也换成序列级，用长度归一化的序列似然比。题目让你写 loss，再像 `fireworks-grpo-sft-loss` 一样改成 SFT 式的加权 logprob。

给你的代码：

```python
def gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps=0.2):
    # *_logprobs, mask: [B, T]；advantages: [B]
    token_ratio = torch.exp(policy_logprobs - old_logprobs)
    s = (token_ratio * mask).sum(-1) / mask.sum(-1)
    obj = torch.minimum(s * advantages, s.clamp(1 - eps, 1 + eps) * advantages)
    return -obj.mean()
```

## 错在哪

**$s$ 算成了算术平均。** GSPO 定义的是

$$
s_i(\theta) = \left(\frac{\pi_\theta(y_i\mid x)}{\pi_{\mathrm{old}}(y_i\mid x)}\right)^{1/|y_i|} = \exp\Big(\frac{1}{|y_i|}\sum_{t}\big(\log\pi_\theta(y_{i,t}) - \log\pi_{\mathrm{old}}(y_{i,t})\big)\Big)
$$

也就是 token ratio 的几何平均。算术平均会被一两个 ratio 特别大的 token 拉高，GSPO 想避开的正是这个。几何平均在 log 域里求平均，一个异常 token 的影响被除以 $|y_i|$。

**eps 照搬了 0.2。** 长度归一化之后 $s_i$ 离 1 很近，0.2 几乎永远不会触发 clip。论文用的 clip 范围比 token 级 PPO 小几个数量级，是 $10^{-4}$ 这个量级。这不算写错代码，但面试会追问为什么 eps 要换。

```python
def gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    n = mask.sum(-1).clamp(min=1)
    log_s = ((policy_logprobs - old_logprobs) * mask).sum(-1) / n
    s = torch.exp(log_s)
    obj = torch.minimum(s * advantages, s.clamp(1 - eps_low, 1 + eps_high) * advantages)
    return -obj.mean()
```

## 梯度和加权 logprob 形式

$$
\nabla_\theta s_i = s_i\,\nabla_\theta\log s_i = s_i\cdot\frac{1}{|y_i|}\sum_t\nabla_\theta\log\pi_\theta(y_{i,t})
$$

所以没被 clip 时，一条回答里每个 token 拿到同样的系数 $s_iA_i/|y_i|$。GRPO 里每个 token 的系数是自己的 $r_{i,t}A_i$，token 之间可以差很多，这是 GSPO 说 GRPO 方差大的来源。

clip mask 和 token 级一样分正负两侧，只是按序列算：

```python
def gspo_loss_sft_style(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    n = mask.sum(-1).clamp(min=1)
    s = torch.exp(((policy_logprobs - old_logprobs) * mask).sum(-1) / n).detach()
    active = torch.where(advantages >= 0, s <= 1 + eps_high, s >= 1 - eps_low)
    w = (s * advantages * active / n).detach()          # [B]
    return -(w[:, None] * policy_logprobs * mask).sum() / advantages.shape[0]
```

两版对 `policy_logprobs` 的梯度应当一致：

```python
B, T = 3, 5
lp = torch.randn(B, T, requires_grad=True)
old = lp.detach() + 1e-4 * torch.randn(B, T)
adv = torch.randn(B)
mask = torch.tensor([[1, 1, 1, 0, 0], [1, 1, 1, 1, 1], [1, 1, 0, 0, 0]]).float()
g1, = torch.autograd.grad(gspo_loss(lp, old, adv, mask), lp)
g2, = torch.autograd.grad(gspo_loss_sft_style(lp, old, adv, mask), lp)
assert torch.allclose(g1, g2, atol=1e-6)
```

## 追问

**一条回答整体被 clip，是不是浪费了很多 token？** 是。GSPO 论文报告它 clip 掉的 token 比例比 GRPO 高得多，训练效率仍然更好。他们的解释是 token 级梯度噪声太大，丢掉一些整条回答换来更干净的信号。

**想要 token 级 advantage 怎么办？** 论文给了 GSPO-token：$s_{i,t} = \mathrm{sg}(s_i)\cdot\pi_\theta(y_{i,t})/\mathrm{sg}(\pi_\theta(y_{i,t}))$。数值上等于 $s_i$，梯度走各自的 token。所有 token 的 advantage 相同时，它和 GSPO 完全等价。

**MoE 为什么特别需要这个？** 同一条回答在更新前后可能被路由到不同 expert，token 级 ratio 波动很大，GRPO 在 MoE 上要靠 routing replay 才稳。序列级 ratio 对单个 token 的波动不敏感。
