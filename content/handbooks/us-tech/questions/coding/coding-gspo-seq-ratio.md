---
id: coding-gspo-seq-ratio
section: coding
order: 38
level: A
title: 白板：GSPO 的序列级 ratio，写成 token 上的加权 logprob loss
quick: "先对有效 token 的 log ratio 取均值再 exp，得到 GSPO 的序列级 ratio，并按整条序列做 clip。改写成加权 logprob 时，每个 token 的权重为 $\\mathrm{sg}(s_iA_i\\cdot\\mathrm{active}_i)/|y_i|$，整体停止梯度。"
tags:
  - 完整编程练习
  - Coding
  - GRPO
  - PPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Group Sequence Policy Optimization (GSPO)
    url: https://arxiv.org/abs/2507.18071
    type: primary
  - title: DeepSeekMath, GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

## 题目描述

给定当前策略和旧策略在回答 token 上的 log-prob、序列优势与有效位置 mask，实现 GSPO 序列级损失。还要提供一个加权 log-prob 形式，其对当前策略的梯度与直接损失一致，但不要求两者的前向损失值相同。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4) -> 标量`：GSPO 的 clipped 目标，取负作为 loss，对 batch 取平均。
- `gspo_loss_sft_style(...)`：同样参数，写成监督微调（SFT）式的加权 logprob，对 `policy_logprobs` 的梯度必须和 `gspo_loss` 一致。
- `sequence_log_ratio(policy_logprobs, old_logprobs, mask) -> [B]`：两者共用的辅助函数，算每条序列的 $\log s_i$。
- 约束：`*_logprobs`、`mask` 是 `[B, T]`，每条序列至少有一个有效的 response token；`advantages` 是 `[B]`，视为常量。序列 ratio 是 `exp(masked_mean(new - old))`，不是 token ratio 的算术平均。`eps_low`、`eps_high` 均非负。

- 记每序列有效长度为 `L_i=sum(mask_i)`、`log_s_i=sum(mask_i*(new_i-old_i))/L_i`、`s_i=exp(log_s_i)`，损失定义为 `-mean_i(min(s_i*A_i, clamp(s_i,1-eps_low,1+eps_high)*A_i))`。旧 log-prob 不接收梯度。
- SFT 形式里，每条序列有效 token 的常量权重为 `stop_gradient(s_i*A_i*active_i/L_i)`，对所有有效 token 的加权当前 log-prob 求和后除以 B 并取负。`active_i` 在 `A_i>=0 且 s_i<=1+eps_high` 或 `A_i<0 且 s_i>=1-eps_low` 时为 1，其余为 0。
### 示例

```text
一条序列，两个 token 的 ratio 是 [4, 1/4]，A = 1
序列 ratio s = exp((log 4 + log 1/4) / 2) = 1   -> gspo_loss = -1
算术平均 (4 + 0.25) / 2 = 2.125                 -> 错误写法
```

## 解题思路与参考答案

GSPO 先把 token ratio 合成序列级 ratio，再对整条回答做 clip。几何平均等于先平均 log ratio 再求 exp，因此 $\log s_i$ 就是 mask 内 `new - old` 的均值。clip 和 PPO 一样分正负两侧，只是作用在整条序列上：一条回答要么所有 token 都有梯度，要么都没有。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4) -> 标量`：GSPO 的 clipped 目标，取负作为 loss，对 batch 取平均。
- `gspo_loss_sft_style(...)`：同样参数，写成监督微调（SFT）式的加权 logprob，对 `policy_logprobs` 的梯度必须和 `gspo_loss` 一致。
- `sequence_log_ratio(policy_logprobs, old_logprobs, mask) -> [B]`：两者共用的辅助函数，算每条序列的 $\log s_i$。
- 约束：`*_logprobs`、`mask` 是 `[B, T]`，每条序列至少有一个有效的 response token；`advantages` 是 `[B]`，视为常量。序列 ratio 是 `exp(masked_mean(new - old))`，不是 token ratio 的算术平均。`eps_low`、`eps_high` 必须非负，否则抛 `ValueError`。

### 输入输出示例

```text
一条序列，两个 token 的 ratio 是 [4, 1/4]，A = 1
序列 ratio s = exp((log 4 + log 1/4) / 2) = 1   -> gspo_loss = -1
算术平均 (4 + 0.25) / 2 = 2.125                 -> 错误写法
```

### 解题思路与正确性

改写成加权 logprob 时，由 $\nabla s_i = s_i\cdot\frac{1}{|y_i|}\sum_t\nabla\log\pi_\theta(y_{i,t})$，每个 token 的权重是 $\mathrm{sg}(s_iA_i\cdot\mathrm{active}_i)/|y_i|$。权重要除以这条序列的有效长度，并且整体 detach，否则梯度会多出别的项。

### 完整参考实现（Python 3）

```python
import math

import torch


def _check_eps(eps_low, eps_high):
    if eps_low < 0 or eps_high < 0:
        raise ValueError(f"clip ranges must be non-negative, got eps_low={eps_low}, eps_high={eps_high}")


def sequence_log_ratio(policy_logprobs, old_logprobs, mask):
    """log s_i：每条序列有效 token 上 log ratio 的平均。[B, T] -> [B]。"""
    lengths = mask.sum(-1).clamp(min=1)
    return ((policy_logprobs - old_logprobs) * mask).sum(-1) / lengths


def gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    """GSPO 的 clipped 目标（取负作为 loss）。

    *_logprobs, mask: [B, T]；advantages: [B]，视为常量。
    序列 ratio s_i 是 token ratio 的几何平均，clip 在序列上做。
    """
    _check_eps(eps_low, eps_high)
    s = torch.exp(sequence_log_ratio(policy_logprobs, old_logprobs, mask))   # [B]
    clipped = s.clamp(1 - eps_low, 1 + eps_high)
    objective = torch.minimum(s * advantages, clipped * advantages)
    return -objective.mean()


def gspo_loss_sft_style(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    """和 gspo_loss 梯度相同的加权 logprob 写法。

    每条序列的 token 共用权重 sg(s_i * A_i * active_i) / |y_i|。
    """
    _check_eps(eps_low, eps_high)
    lengths = mask.sum(-1).clamp(min=1)                                        # [B]
    s = torch.exp(sequence_log_ratio(policy_logprobs, old_logprobs, mask)).detach()
    active = torch.where(advantages >= 0, s <= 1 + eps_high, s >= 1 - eps_low)
    weight = (s * advantages * active / lengths).detach()                      # [B]
    return -(weight[:, None] * policy_logprobs * mask).sum() / advantages.shape[0]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(grad_clipped, grad_weighted, atol=1e-6)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def grad_of(loss_fn, logprobs, *args):
    (grad,) = torch.autograd.grad(loss_fn(logprobs, *args), logprobs)
    return grad


torch.set_num_threads(1)
torch.manual_seed(2)

# 两种写法对 policy_logprobs 的梯度一致；mask 外的 token 梯度为 0
logprobs = torch.randn(3, 5, requires_grad=True)
old = logprobs.detach() + 0.0001 * torch.randn(3, 5)
adv = torch.tensor([1.0, -1.0, 2.0])
mask = torch.tensor([[1, 1, 0, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0.0]])
grad_clipped = grad_of(gspo_loss, logprobs, old, adv, mask)
grad_weighted = grad_of(gspo_loss_sft_style, logprobs, old, adv, mask)
assert torch.allclose(grad_clipped, grad_weighted, atol=1e-6)
assert torch.all(grad_clipped[mask == 0] == 0)

# token ratio 为 [4, 1/4]：几何平均 s = 1，loss = -1；算术平均会得到 2.125
pair = torch.tensor([[math.log(4.0), math.log(0.25)]], requires_grad=True)
loss = gspo_loss(pair, torch.zeros_like(pair), torch.ones(1), torch.ones_like(pair))
assert torch.allclose(loss, torch.tensor(-1.0))

# A > 0 且 s 超出上界：整条序列被 clip，两种写法梯度都为 0
far = torch.zeros(1, 3, requires_grad=True)
far_old = torch.full((1, 3), -0.01)
assert torch.all(grad_of(gspo_loss, far, far_old, torch.ones(1), torch.ones(1, 3)) == 0)
assert torch.all(grad_of(gspo_loss_sft_style, far, far_old, torch.ones(1), torch.ones(1, 3)) == 0)

# 负的 clip 范围报错
expect_value_error(gspo_loss, logprobs, old, adv, mask, eps_low=-1e-4)
```

### 复杂度与追问

设 batch 为 $B$、序列长 $T$。时间和中间张量都是 $O(BT)$，序列级统计（$s_i$、长度、active）是 $O(B)$。

- 追问「两种写法 loss 值一样吗」：不一样。加权 logprob 写法只保证梯度相同，它的标量值没有物理意义；这里也不声称 GSPO 和 PPO 的目标相同。
- 追问「为什么默认 eps 是 $10^{-4}$ 量级」：长度归一化后 $s_i$ 离 1 很近，照搬 token 级 PPO 的 0.2 几乎不会触发 clip。

## 题怎么来的

GRPO 的 advantage 是序列级的，ratio 却是 token 级的。GSPO 把 ratio 也换成序列级，用的是按长度归一化的序列似然比。这道题让你写出损失（loss），再像 `fireworks-grpo-sft-loss` 那样改写成监督微调（SFT）式的加权 logprob。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修复的错误片段，不是参考答案。对照上面的题面，找出它偏离接口或梯度约定的地方；正确实现和测试在前面的练习部分。

```python
def gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps=0.2):
    # *_logprobs, mask: [B, T]；advantages: [B]
    token_ratio = torch.exp(policy_logprobs - old_logprobs)
    s = (token_ratio * mask).sum(-1) / mask.sum(-1)
    obj = torch.minimum(s * advantages, s.clamp(1 - eps, 1 + eps) * advantages)
    return -obj.mean()
```

## 错在哪

**$s$ 算成了算术平均。** GSPO 的定义是

$$
s_i(\theta) = \left(\frac{\pi_\theta(y_i\mid x)}{\pi_{\mathrm{old}}(y_i\mid x)}\right)^{1/|y_i|} = \exp\Big(\frac{1}{|y_i|}\sum_{t}\big(\log\pi_\theta(y_{i,t}) - \log\pi_{\mathrm{old}}(y_{i,t})\big)\Big)
$$

也就是 token ratio 的几何平均。算术平均会被一两个 ratio 特别大的 token 拉高，而 GSPO 想避开的正是这种情况。几何平均在 log 域里求平均，单个异常 token 的影响被除以 $|y_i|$。

**eps 照搬了 0.2。** 长度归一化以后 $s_i$ 离 1 很近，0.2 几乎永远不会触发 clip。论文用的 clip 范围比 token 级 PPO 小几个数量级，在 $10^{-4}$ 这个量级。这一点不算代码写错，但面试会追问 eps 为什么要换。

## 梯度和加权 logprob 形式

$$
\nabla_\theta s_i = s_i\,\nabla_\theta\log s_i = s_i\cdot\frac{1}{|y_i|}\sum_t\nabla_\theta\log\pi_\theta(y_{i,t})
$$

所以在没被 clip 的情况下，一条回答里每个 token 拿到的系数都是 $s_iA_i/|y_i|$。GRPO 里每个 token 的系数是各自的 $r_{i,t}A_i$，token 之间可能差很多，GSPO 认为这是 GRPO 方差大的来源。

参考实现里的 `active` 就是按序列算的正负两侧 clip mask；测试第一组检查两种写法的梯度一致。

## 追问

**一条回答整体被 clip，是不是浪费了很多 token？**
是。GSPO 论文报告它 clip 掉的 token 比例比 GRPO 高得多，但训练效率仍然更好。他们的解释是 token 级梯度噪声太大，丢掉一些整条回答，换来更干净的信号。

**想要 token 级 advantage 怎么办？**
论文给了 GSPO-token：$s_{i,t} = \mathrm{sg}(s_i)\cdot\pi_\theta(y_{i,t})/\mathrm{sg}(\pi_\theta(y_{i,t}))$。它的数值等于 $s_i$，但梯度分别走各自的 token。所有 token 的 advantage 相同时，它和 GSPO 完全等价。

**MoE 为什么特别需要这个？**
同一条回答在更新前后可能被路由到不同的 expert，token 级 ratio 波动很大，GRPO 在 MoE 上要靠 routing replay 才能稳定。序列级 ratio 对单个 token 的波动不敏感。

## 相关题

- [[coding-loss-atlas]]：总览题，把 GSPO 和 PPO、GRPO、CISPO 都放进「权重 × logprob」的同一张表里对照。
- [[coding-grpo-loss-agg]]：GRPO 的 token loss 怎么聚合、各自的长度偏置，是这里「除以 $|y_i|$」的背景。
- [[coding-cispo]]：另一种改 PPO clip 的方案，仍在 token 级，只截 IS 权重、不丢梯度。
- [[coding-tis-mismatch]]：那张也比较了序列级和 token 级重要性权重，但修正的是推理引擎和训练端的 logprob 差。
