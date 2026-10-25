---
id: coding-tis-mismatch
section: coding
order: 40
level: A
title: 白板：推理引擎的 logprob 和训练端对不上，截断重要性权重怎么加
quick: "PPO 的 $\\pi_{\\mathrm{old}}$ 用训练端在旧权重上重算的 logprob，再用固定的截断权重 $\\min(\\pi_{\\mathrm{old}}/\\mu, C)$ 修正推理引擎分布 $\\mu$ 的差异。权重必须 detach，单独乘在 PPO 目标上，避免把实现差异也混进 PPO clip。"
tags:
  - 完整编程练习
  - Coding
  - PPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "IMPALA: Scalable Distributed Deep-RL with Importance Weighted Actor-Learner Architectures (V-trace)"
    url: https://arxiv.org/abs/1802.01561
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
---

## 题目描述

实现带 truncated importance sampling 的 PPO token loss，区分当前策略、重计算旧策略和 rollout 时记录的策略概率。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `ppo_loss_tis(policy_logprobs, old_logprobs, rollout_logprobs, advantages, mask, eps=0.2, C=2.0) -> 标量`：所有输入形状 `[B, T]`。
  - `policy_logprobs`：当前策略 $\pi_\theta$ 的 token logprob，带梯度。
  - `old_logprobs`：训练端在 $\theta_{\mathrm{old}}$ 上重算的 logprob，固定。
  - `rollout_logprobs`：推理引擎采样时记录的 logprob（分布 $\mu$），固定。
- PPO ratio 是 $\exp(\text{policy} - \text{old})$，照常 clip 到 $[1-\epsilon, 1+\epsilon]$。截断重要性权重是 $\min(\exp(\text{old} - \text{rollout}), C)$，并且 detach。
- 每个 token 的目标为 `min(ratio * advantage, clip(ratio) * advantage)`；loss 是此目标乘截断权重后的负值。`mask` 仅含 0/1，`eps >= 0`、`C > 0`。loss 在有效 token（`mask` 为 1）上取平均；mask 全为 0 时返回可反传的 0。

### 输入输出示例

```text
policy_logprobs = old_logprobs = rollout_logprobs = [[0]]
advantages = [[1]], mask = [[1]], eps=0.2, C=2
ppo_loss_tis(...) -> -1
仅将 rollout_logprobs 改为 [[-5]] -> -2
仅将 mask 改为 [[0]] -> 0，反向传播的策略梯度为 0
```

## 解题思路与参考答案

我会把策略更新的 ratio 和训推实现差异分开计算：前者按 PPO clip，后者截断后 detach，再乘到逐 token 目标上。比如还没开始更新时，当前策略和旧策略应当相同，但推理引擎的 logprob 仍可能有误差；直接拿它作分母会提前触发 clip。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `ppo_loss_tis(policy_logprobs, old_logprobs, rollout_logprobs, advantages, mask, eps=0.2, C=2.0) -> 标量`：所有输入形状 `[B, T]`。
  - `policy_logprobs`：当前策略 $\pi_\theta$ 的 token logprob，带梯度。
  - `old_logprobs`：训练端在 $\theta_{\mathrm{old}}$ 上重算的 logprob，固定。
  - `rollout_logprobs`：推理引擎采样时记录的 logprob（分布 $\mu$），固定。
- PPO ratio 是 $\exp(\text{policy} - \text{old})$，照常 clip 到 $[1-\epsilon, 1+\epsilon]$。截断重要性权重是 $\min(\exp(\text{old} - \text{rollout}), C)$，并且 detach。
- loss 在有效 token（`mask` 为 1）上取平均；mask 全为 0 时返回可反传的 0。

### 输入输出示例

```text
old == rollout          -> 权重 = 1，退化成普通 PPO
policy == old           -> PPO ratio = 1，但 old != rollout 时权重仍可能不是 1
old - rollout = 1       -> exp(1) ≈ 2.72，被截断到 C = 2
```

### 解题思路与正确性

PPO 的 ratio 只衡量这一步策略变了多少，所以分母必须是训练端自己算的 $\pi_{\mathrm{old}}$。推理引擎和训练端的数值差是另一件事，用单独的权重 $\pi_{\mathrm{old}}/\mu$ 修正。

这个权重里不能出现当前的 $\pi_\theta$：它是采样分布不一致的校正，和这一步怎么优化无关。权重乘在 PPO 的逐 token 目标上，detach 后它只缩放梯度，不额外贡献梯度。截断上界 $C$ 防止个别 token 的权重过大。

### 完整参考实现（Python 3）

```python
import torch


def ppo_loss_tis(policy_logprobs, old_logprobs, rollout_logprobs, advantages, mask,
                 eps=0.2, C=2.0):
    """PPO clip loss 加截断重要性权重 min(π_old / μ, C)。所有输入 [B, T]，返回有效 token 平均。"""
    # old_logprobs 由训练端在 θ_old 上重算；rollout_logprobs 来自推理引擎
    ratio = torch.exp(policy_logprobs - old_logprobs)
    clipped = ratio.clamp(1 - eps, 1 + eps)
    objective = torch.minimum(ratio * advantages, clipped * advantages)
    weight = torch.exp(old_logprobs - rollout_logprobs).clamp(max=C).detach()
    return -(weight * objective * mask).sum() / mask.sum().clamp(min=1)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(loss, reference)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
torch.set_num_threads(1)

policy = torch.tensor([[0.1, 0.2]], requires_grad=True)
old = torch.zeros_like(policy)
rollout = torch.tensor([[-1.0, 0.0]])
advantages = torch.tensor([[1.0, -1.0]])
mask = torch.ones_like(policy)

# 和按公式手写的参考值一致，梯度也一致
loss = ppo_loss_tis(policy, old, rollout, advantages, mask)
ratio = (policy - old).exp()
weight = (old - rollout).exp().clamp(max=2.0)
reference = -(weight * torch.minimum(ratio * advantages, ratio.clamp(0.8, 1.2) * advantages)).mean()
assert torch.allclose(loss, reference)
grad_loss, = torch.autograd.grad(loss, policy)
grad_ref, = torch.autograd.grad(reference, policy)
assert torch.allclose(grad_loss, grad_ref)

# old == rollout 时权重为 1，等于普通 PPO
plain = ppo_loss_tis(policy, old, old, advantages, mask)
plain_ref = -torch.minimum(ratio * advantages, ratio.clamp(0.8, 1.2) * advantages).mean()
assert torch.allclose(plain, plain_ref)

# 权重被截断到 C
far = torch.tensor([[-5.0, -5.0]])
capped = ppo_loss_tis(old, old, far, torch.ones(1, 2), mask, C=2.0)
assert torch.allclose(capped, torch.tensor(-2.0))

# 空 mask 返回 0
assert ppo_loss_tis(policy, old, rollout, advantages, torch.zeros_like(mask)) == 0
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$。时间和空间都是 $O(BT)$。

- 追问「TIS 让 off-policy 数据都能用了吗」：不能。截断本身引入偏差，它只适合修正推理引擎和训练端之间较小的数值差，不能说任意 off-policy 数据加上它就无偏可用。

## 题怎么来的

采样轨迹（rollout）用 vLLM / SGLang 这类推理引擎生成，训练则用 FSDP / Megatron 做前向。权重相同，但 kernel、精度和 batch 形状都不同，同一个 token 的 logprob 就会有差异。名义上是 on-policy，实际上采样分布 $\mu$ 和训练端的 $\pi_{\mathrm{old}}$ 并不是同一个分布。怎么排查这种差异见 `sys-rollout-logprob`，这道题只讨论 loss 里怎么修正。面试官给的起始代码见下一节。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修复的错误片段，不是参考答案。对照上面的题面，找出偏离接口或梯度契约的地方；正确实现和测试在前面的练习部分。

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

clip 本来只想限制第一项。第二项和优化无关，却也会让 ratio 出界：第一步更新之前 $\pi_\theta = \pi_{\mathrm{old}}$，本该所有 token 都在界内，结果一部分 token 因为数值差被 clip 掉，拿不到梯度。两套实现在低概率 token 上的相对误差最大，而这些 token 恰好是最该学的。

另外，这段代码在 mask 全为 0 时会除以 0；练习里的实现用 `clamp(min=1)` 挡掉了。

## 改法

训练端在更新前用 $\theta_{\mathrm{old}}$ 重算一遍 logprob，作为 PPO 的 $\pi_{\mathrm{old}}$。实现之间的差异用单独的截断 IS 权重修正：

$$
w_t = \min\Big(\frac{\pi_{\mathrm{old}}(y_t)}{\mu(y_t)},\,C\Big)
$$

练习里的 `ppo_loss_tis` 就是这个写法。$w$ 里没有 $\pi_\theta$，本来就不带梯度；detach 是为了防止 `old_logprobs` 忘了在 `no_grad` 下算。

$C$ 越大偏差越小，方差越大。这里只截上界：$\pi_{\mathrm{old}}/\mu$ 很小的 token 权重接近 0，本来就不会爆。V-trace 的截断 IS 权重是同样的做法。

## 一个常见的错写

把权重写成 `torch.exp(policy_logprobs - rollout_logprobs).clamp(max=C)`：用了当前的 $\pi_\theta$，而且没有 detach。第一个 mini-epoch 里它的数值和正确写法一样，但梯度多了一条穿过 $w$ 的路径；从第二个 mini-epoch 开始连数值都不一样了，因为 $w$ 把策略这一步的变化又算了一遍。

## 追问

**多花一次前向值得吗？** 重算 $\pi_{\mathrm{old}}$ 要多做一次训练端前向。如果只做一次更新（一个 mini-epoch），$\pi_\theta$ 和 $\pi_{\mathrm{old}}$ 数值相同，可以直接把当前前向的结果 detach 当作 $\pi_{\mathrm{old}}$，省掉这次前向。

**要监控什么？** $\log(\pi_{\mathrm{old}}/\mu)$ 的均值和分位数，以及 $w$ 被截断的 token 比例。如果这个比例突然升高，通常是推理引擎的权重同步出了问题，而不是模型在学习，见 `sys-weight-remap`。

**序列级还是 token 级？** 序列级权重是 token 权重的连乘，长回答上方差会爆炸。token 级截断有偏但稳定，实践里多用 token 级。

## 相关题

- [[sys-rollout-logprob]]：同一个现象的排查题：on-policy 下 rollout 和训练前向的 logprob 对不上，先查 micro batch、温度和权重版本，再谈修正。
- [[coding-cispo]]：同样是截断后 detach 的重要性权重，但那里截的是新旧策略的 ratio，用来代替 PPO clip。
- [[coding-gspo-seq-ratio]]：这里选了 token 级权重，那张讲序列级 ratio 用几何平均后怎么避免方差爆炸。
- [[coding-token-logprob]]：训练端的 $\pi_{\mathrm{old}}$ 要自己从 logits 重算，shift 和温度写错就会制造假的 mismatch。
