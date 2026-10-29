---
id: fireworks-grpo-sft-loss
section: coding
order: 35
level: S
title: Fireworks：把 clipped GRPO 写成 SFT 式的加权 logprob loss
quick: >-
  把 ratio × advantage × 单侧 clip mask detach 后当作 NLL 权重，就能得到与 clipped GRPO
  相同的梯度。正 advantage 只挡上界，负 advantage 只挡下界；权重可正可负，要按 token 数平均，除以 `weights.sum()`
  会改变符号或让分母接近零。
tags:
  - 完整编程练习
  - Fireworks
  - GRPO
  - PPO
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Proximal Policy Optimization Algorithms
    url: 'https://arxiv.org/abs/1707.06347'
    type: primary
  - title: 'DeepSeekMath, GRPO'
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

## 题目描述

实现 GRPO 的 clipped 训练目标，并把其对 policy log-prob 的梯度改写为带固定权重的 SFT 损失。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `sft_loss(weights,logprobs) -> Tensor` 返回标量 `-mean(stop_gradient(weights)*logprobs)`，权重允许正负，按 token 数 normalization。
- `compute_grpo_loss_per_rollout(policy_logprobs,sampling_logprobs,advantages,clip_eps=0.2)` 返回标量 `-mean(min(r*A,clip(r,1-eps,1+eps)*A))`，r=exp(`policy_logprobs`-`sampling_logprobs`)，A=advantages，eps=`clip_eps`。
- `compute_grpo_loss_per_rollout_with_sft_loss(policy_logprobs,sampling_logprobs,advantages,epsilon=0.2)` 必须复用 `sft_loss`，并使 `policy_logprobs` 的梯度与上述标准目标一致；不要求两标量数值相同。传给 `sft_loss` 的权重必须停止梯度。
- 所有数组为相同长度 [N]、N>=1，输入有限，`sampling_logprobs` 和 advantages 固定，0<=eps<1。在恰好 r=1-eps 或 1+eps 的 endpoints，保留对应未越界分支梯度，与 PyTorch clamp 在 clipping range 内的导数约定一致。

### 输入输出示例

```text
sft_loss([1,-1],[-1,-2]) -> -0.5
其对 logprobs 的梯度为 [-0.5,0.5]
policy_logprobs=sampling_logprobs=[ln(0.5),ln(0.5)], advantages=[1,-1]
compute_grpo_loss_per_rollout(policy_logprobs,sampling_logprobs,advantages) -> 0
```

## 解题思路与参考答案

我会先从 clipped objective 求对 logprob 的导数，再把这个系数 detach 成加权 NLL 的权重。比如负 advantage 的 token 应降低概率，如果把负权重再除以负的权重和，符号就会翻转。验证时比较两版梯度，loss 数值本身不要求相同。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定；面试原代码见下文「故意错误的起始片段」。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `sft_loss(weights, logprobs) -> Tensor`：加权 negative log likelihood，`-(weights.detach() * logprobs).mean()`。权重可正可负，按 token 数取平均，不按权重和 normalization。
- `compute_grpo_loss_per_rollout(policy_logprobs, sampling_logprobs, advantages, clip_eps=0.2) -> Tensor`：标准 clipped 目标的负值，按 token 平均。
- `compute_grpo_loss_per_rollout_with_sft_loss(policy_logprobs, sampling_logprobs, advantages, epsilon=0.2) -> Tensor`：复用 `sft_loss`，权重是 detach 后的 ratio × advantage × clip mask，对 `policy_logprobs` 的梯度与上一个函数相同。
- 输入都是一维、长度 N ≥ 1 的有效 token；`sampling_logprobs` 和 `advantages` 是常量。clip mask 按 advantage 的符号选择单侧 clipping limit，ratio 和 mask 都不参与求导。

### 输入输出示例

```text
eps = 0.2
ratio = 1.5, A = +1  -> 已经朝有利方向走过头，被 clip，梯度 0
ratio = 0.5, A = -1  -> 同上，梯度 0
ratio = 1.5, A = -1  -> 不 clip，梯度照常
sft_loss([1, -1], logprobs=[1, 2]) 对 logprobs 的梯度 -> [-0.5, 0.5]
```

### 解题思路与正确性

令 $r=\exp(\log\pi_\theta-\log\pi_{\text{old}})$。clipped 目标 $\min(rA,\ \mathrm{clip}(r)A)$ 对 $\log\pi_\theta$ 求导：取到 clip 分支时是常数，梯度为 0；取到 $rA$ 分支时，因为 $\nabla r = r\nabla\log\pi_\theta$，梯度是 $rA$。所以把 $rA \cdot \text{active}$ 当作常数权重乘到 $\log\pi_\theta$ 上，得到的梯度和原目标一样。

active 的条件是单侧的：$A \ge 0$ 时要 $r \le 1+\varepsilon$，$A<0$ 时要 $r \ge 1-\varepsilon$。

`sft_loss` 必须和原目标用同一种 reduction（按 token 平均）。如果除以 `weights.sum()`，负权重会让符号整体翻转，正负权重抵消时还会除以接近 0 的数。

### 完整参考实现（Python 3）

```python
import math

import torch


def sft_loss(weights, logprobs):
    """加权 negative log likelihood，按 token 数平均；权重可正可负，不按权重和 normalization。"""
    return -(weights.detach() * logprobs).mean()


def compute_grpo_loss_per_rollout(
    policy_logprobs, sampling_logprobs, advantages, clip_eps=0.2
):
    """标准 clipped GRPO 目标的负值，按 token 平均。所有输入形状 [N]。"""
    ratio = torch.exp(policy_logprobs - sampling_logprobs)
    clipped_ratio = ratio.clamp(1 - clip_eps, 1 + clip_eps)
    objective = torch.minimum(ratio * advantages, clipped_ratio * advantages)
    return -objective.mean()


def compute_grpo_loss_per_rollout_with_sft_loss(
    policy_logprobs, sampling_logprobs, advantages, epsilon=0.2
):
    """复用 sft_loss 的等价写法：对 policy_logprobs 的梯度与上面的 clipped 目标相同。"""
    ratio = torch.exp(policy_logprobs - sampling_logprobs).detach()
    # 只挡住「朝有利方向走得太远」的那一侧
    active = torch.where(
        advantages >= 0,
        ratio <= 1 + epsilon,
        ratio >= 1 - epsilon,
    )
    weights = ratio * advantages * active
    return sft_loss(weights, policy_logprobs)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(direct_grad, sft_grad)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
# 两个被 clip 的 token（ratio 1.5 且 A>0、ratio 0.5 且 A<0）梯度为 0，两版梯度一致
logprobs = torch.tensor([math.log(1.5), math.log(0.5), 0.1, -0.1], requires_grad=True)
old = torch.zeros(4)
adv = torch.tensor([1.0, -1.0, 1.0, -1.0])
(direct_grad,) = torch.autograd.grad(
    compute_grpo_loss_per_rollout(logprobs, old, adv), logprobs
)
(sft_grad,) = torch.autograd.grad(
    compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv), logprobs
)
assert torch.allclose(direct_grad, sft_grad)
assert direct_grad[0] == 0
assert direct_grad[1] == 0

# 反方向越界不 clip：ratio 1.5 但 A<0、ratio 0.5 但 A>0 仍有梯度
logprobs = torch.tensor([math.log(1.5), math.log(0.5)], requires_grad=True)
adv = torch.tensor([-1.0, 1.0])
(sft_grad,) = torch.autograd.grad(
    compute_grpo_loss_per_rollout_with_sft_loss(logprobs, torch.zeros(2), adv), logprobs
)
assert torch.all(sft_grad != 0)

# 随机输入下两版梯度一致（边界上的不可微点概率为 0）
torch.manual_seed(0)
logprobs = torch.randn(8, requires_grad=True)
old = logprobs.detach() + 0.3 * torch.randn(8)
adv = torch.randn(8)
(direct_grad,) = torch.autograd.grad(
    compute_grpo_loss_per_rollout(logprobs, old, adv), logprobs
)
(sft_grad,) = torch.autograd.grad(
    compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv), logprobs
)
assert torch.allclose(direct_grad, sft_grad)

# 两版的 loss 数值不同，只有梯度相同
assert not torch.isclose(
    compute_grpo_loss_per_rollout(logprobs, old, adv),
    compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv),
)

# 权重正负抵消时也是有限值，梯度是 -w / N
values = torch.tensor([1.0, 2.0], requires_grad=True)
loss = sft_loss(torch.tensor([1.0, -1.0]), values)
assert torch.isfinite(loss)
assert torch.allclose(torch.autograd.grad(loss, values)[0], torch.tensor([-0.5, 0.5]))
```

### 复杂度与追问

设有效 token 数为 N。三个函数的时间和空间都是 O(N)。

- 追问「ratio 恰好等于 1±ε 时怎么办」：那是不可微点，两版选哪一侧的次梯度要和参考实现约定一致；测试刻意避开了这个点。

## 真题记录

这是本人 Fireworks 一轮面试的复盘。面试官给了一个 `sft_loss(weights, logprobs)`，再给两版 GRPO：一版直接写 clipped objective，一版复用 `sft_loss`。先问实现对不对，然后一路追问 importance ratio、advantage 和 clip mask，最后落到为什么两版梯度一样。面试给的代码就是下面这段。

## 故意错误的起始片段（用于找 bug）

下面是面试时给的原始代码，有 bug，不是参考答案。修好的版本和测试在上面的练习部分。

```python
import torch


def sft_loss(
    weights: torch.Tensor,  # [N], token weights
    logprobs: torch.Tensor,  # [N], token log probabilities
) -> torch.Tensor:
    """Return the weighted negative log-likelihood, summed over tokens."""
    weights = weights / weights.sum()
    loss = weights * logprobs
    loss = -loss.sum()
    return loss


def compute_grpo_loss_per_rollout(
    policy_logprobs: torch.Tensor,  # [N], requires gradients
    sampling_logprobs: torch.Tensor,  # [N], fixed rollout log-probs
    advantages: torch.Tensor,  # [N], fixed token advantages
    clip_eps: float = 0.2,
) -> torch.Tensor:
    ratio = torch.exp(policy_logprobs - sampling_logprobs)
    clipped_ratio = torch.clip(ratio, 1 - clip_eps, 1 + clip_eps)
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

思路是对的：`detach` 之后的 `ratio * advantages` 可以直接当权重，正负 advantage 各管一侧的 mask 也对。错在两处：

1. `compute_grpo_loss_per_rollout` 没有 `return loss`，函数返回 `None`。
2. `sft_loss` 里的 `weights / weights.sum()`。SFT 的权重非负，这样 normalization 没问题；但 GRPO 的权重是 $rA$，advantage 可以是负的。

第二处举个例子。三个 token 的 advantage 都是 $-1$，ratio 约等于 1，权重是 `[-1, -1, -1]`，和是 $-3$。除完变成 `[1/3, 1/3, 1/3]`，符号整体翻了过来，本来要压低概率的 token 被当成正样本往上推。如果一组里正负权重差不多抵消，`weights.sum()` 接近 0，梯度会直接爆掉。即使权重全是正的，除以和也改变了梯度的尺度，和直接写的那版对不上。

改法是和原 objective 用同一种 reduction，这里是按 token 数取平均：`loss = -(weights * policy_logprobs).mean()`。

## 为什么 ratio × advantage 能当权重

令 $r(\theta) = \pi_\theta / \pi_{\mathrm{old}}$。$\pi_{\mathrm{old}}$ 是常数，所以

$$
\nabla_\theta r = \frac{\nabla_\theta \pi_\theta}{\pi_{\mathrm{old}}} = r\,\nabla_\theta \log \pi_\theta
$$

不 clip 时，单个 token 的损失是 $L = -rA$，梯度是

$$
\nabla_\theta L = -rA\,\nabla_\theta \log \pi_\theta
$$

构造一个 surrogate，把 $rA$ 当常数：

$$
L_{\mathrm{sur}} = -\mathrm{sg}(rA)\,\log \pi_\theta,
\qquad
\nabla_\theta L_{\mathrm{sur}} = -rA\,\nabla_\theta \log \pi_\theta
$$

两个梯度在当前参数处相等。权重 $rA$ 是从梯度的形式推出来的，不是另外设计的。`detach` 必不可少：不 detach 的话，梯度还会沿 ratio 这条路再走一遍，多出一项 $-rA\log\pi\,\nabla\log\pi$，等价关系就不成立了。

## Clip mask

clipped objective 是

$$
L = -\min\big(rA,\ \mathrm{clip}(r, 1-\varepsilon, 1+\varepsilon)\,A\big)
$$

$A>0$ 时，我们想提高这个 token 的概率。$r > 1+\varepsilon$ 时 min 取到 clip 那一支，是常数，梯度为 0；$r < 1-\varepsilon$ 时 min 取的是 $rA$，梯度照常。所以有梯度的条件只有 $r \le 1+\varepsilon$。

$A<0$ 时，我们想压低概率。$r < 1-\varepsilon$ 时进入平台，梯度为 0；有梯度的条件是 $r \ge 1-\varepsilon$。

面试代码里的 `mask1`、`mask2` 就是这两条，只是用了严格不等号。恰好位于 endpoints 的情况是 measure-zero events，不影响结果。$A=0$ 时走哪一支都一样，权重是 0。

容易写错的是两侧都 clip，即 `(ratio >= 1 - eps) & (ratio <= 1 + eps)`。这样 $A>0$ 且 $r$ 已经很小时，这个 token 会被错误地掐掉。PPO 的 min 是一个悲观下界，只挡住「往有利方向走得太远」的那一侧。

面试时可以顺手说怎么验证：同一组 `policy_logprobs` 分别过两版，用 `torch.autograd.grad` 取梯度，`allclose` 应该成立，但 loss 的数值不会一样。练习的测试里就是这么做的。

## 追问

**两版 loss 数值一样吗？** 不一样。$r=1$ 时直接写的版本是 $-\mathrm{mean}(A)$，surrogate 是 $-\mathrm{mean}(A\log\pi)$，只有对 `policy_logprobs` 的梯度相等。所以把 surrogate 的 loss 曲线当成 RL 的目标值看没有意义，要看奖励分数（reward）、KL 和 clip fraction。

**这还算 SFT 吗？** 形式上是加权 NLL，但权重可以是负的：$A>0$ 时权重为正，提高 token 概率；$A<0$ 时权重为负，压低概率。准确的叫法是 weighted log-likelihood surrogate。好处是只要训练端支持逐 token 加权的 NLL，不改 loss 代码就能跑 GRPO。

**「只在当前参数处等价」是什么意思？** 权重是这一步 detach 下来的常数。做完一次 optimizer step，$\pi_\theta$ 变了，ratio 和 mask 都要用新的 `policy_logprobs` 重算。在同一批 sampling 轨迹（rollout）上跑多个 mini-epoch 时，每个 step 都要重新构造权重，不能缓存第一次的。

**KL 项怎么办？** 对 reference model 的 KL 不在这个 min 里。可以把它的梯度系数也折进权重，也可以单独加一项 loss。token 级 KL 的写法见 `coding-kl-div`，KL 放在 reward 里还是 loss 里见 `sys-kl-place`。

## 相关题

- [[coding-loss-atlas]]：把这里的思路推广到 SFT、PPO、DPO、CISPO 等一整张表，只比较各自的权重 $w_t$。
- [[anthropic-grpo-debug]]：同一个 clipped surrogate 的调试版，NumPy 手写梯度，重点是找 sampling 和零方差组的 bug。
- [[coding-cispo]]：这里出界 token 的 clip mask 是 0，CISPO 改成截断权重后 detach，出界 token 仍有梯度。
- [[openai-ppo-clip]]：口述题，讲 clip 只锚 $\pi_{\mathrm{old}}$、ratio 爆了怎么收，是这里 clip mask 的概念背景。
- [[sys-kl-place]]：这里的 KL 追问的展开，KL 写进奖励时 detach，写进 loss 时对当前策略可导。
