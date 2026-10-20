---
id: coding-dpo-weighted
section: coding
order: 43
level: A
title: 白板：DPO 的梯度写成加权 logprob，权重是什么，什么时候大
quick: "DPO 的 policy 梯度等于加权 logprob 差：chosen 权重 $+c$、rejected 权重 $-c$，$c=\\mathrm{sg}(\\beta\\sigma(-z))$；排反时权重大，排对时趋于 0。"
tags:
  - 完整编程练习
  - Coding
  - DPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `seq_logprob(tok_logp, mask) -> [B]`：按 mask 把 token logprob 求和，得到序列 logprob。是求和，不是按长度平均。
- `dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1) -> 标量`：标准 DPO loss，batch 上取平均。`pol_*` / `ref_*` 是 policy / reference 的 token logprob，形状 `[B, T]`；`_w` 是 chosen，`_l` 是 rejected；两边的 mask 可以对应不同长度。用 `logsigmoid` 避免溢出。
- `dpo_loss_weighted(...)`：同样的参数，返回加权 logprob 形式的 surrogate loss。它的数值和 DPO loss 不同，但对 policy 的梯度完全一样。
- `beta > 0`，否则抛 `ValueError`。reference logprob 和 mask 都不接梯度。

### 输入输出示例

```text
z = beta * ((logπ_w - logref_w) - (logπ_l - logref_l))
z = 0  -> dpo_loss = ln 2 ≈ 0.693
z > 0  -> dpo_loss < ln 2      # chosen 相对 reference 涨得比 rejected 多
```

### 解题思路与正确性

DPO loss 是 $-\log\sigma(z)$。对 $z$ 求导得 $-\sigma(-z)$，而 $z$ 对 policy 的梯度是 $\beta(\nabla\log\pi_w-\nabla\log\pi_l)$。所以每对样本的梯度等于 $-\beta\sigma(-z)$ 乘以“chosen 序列 logprob 减 rejected 序列 logprob”的梯度。

把系数 $c=\beta\sigma(-z)$ 放在 `no_grad` 里算出来当常数，再构造 $-c\,(\log\pi_w-\log\pi_l)$，它对 policy 的梯度就和 DPO 一样。两边都对 batch 求平均，测试直接比较两种写法对 `pol_w`、`pol_l` 的梯度。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def seq_logprob(tok_logp, mask):
    """[B, T] token logprob 按 mask 求和，得到 [B] 序列 logprob。"""
    return (tok_logp * mask).sum(-1)


def _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta):
    """z = beta * ((logπ_w - logref_w) - (logπ_l - logref_l))，形状 [B]。"""
    if beta <= 0:
        raise ValueError(f"beta must be positive, got {beta}")
    chosen = seq_logprob(pol_w, mask_w) - seq_logprob(ref_w, mask_w)
    rejected = seq_logprob(pol_l, mask_l) - seq_logprob(ref_l, mask_l)
    return beta * (chosen - rejected)


def dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    """标准 DPO loss：-log sigmoid(z) 的 batch 平均。"""
    z = _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta)
    return -F.logsigmoid(z).mean()


def dpo_loss_weighted(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    """加权 logprob surrogate：数值不同于 DPO loss，但对 policy 的梯度相同。"""
    with torch.no_grad():
        z = _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta)
        weight = beta * torch.sigmoid(-z)  # [B]，排反时接近 beta，排对时趋于 0
    batch_size = pol_w.shape[0]
    margin = seq_logprob(pol_w, mask_w) - seq_logprob(pol_l, mask_l)
    return -(weight * margin).sum() / batch_size
```

### 可执行测试

```python
import math

torch.set_num_threads(1)
torch.manual_seed(4)

pol_w = torch.randn(3, 4, requires_grad=True)
pol_l = torch.randn(3, 4, requires_grad=True)
ref_w = torch.randn(3, 4)
ref_l = torch.randn(3, 4)
mask_w = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 0.0]])
mask_l = torch.ones_like(mask_w)
args = (pol_w, pol_l, ref_w, ref_l, mask_w, mask_l)

# 两种写法对 policy 的梯度一致
grads_dpo = torch.autograd.grad(dpo_loss(*args), (pol_w, pol_l))
grads_weighted = torch.autograd.grad(dpo_loss_weighted(*args), (pol_w, pol_l))
for expected, actual in zip(grads_dpo, grads_weighted):
    assert torch.allclose(expected, actual, atol=1e-6)

# 被 mask 掉的 token 没有梯度
assert torch.all(grads_dpo[0][mask_w == 0] == 0)

# z = 0 时 loss = ln 2；chosen 相对更好时 loss < ln 2
zeros = torch.zeros(2, 3)
ones = torch.ones(2, 3)
assert math.isclose(dpo_loss(zeros, zeros, zeros, zeros, ones, ones).item(), math.log(2), rel_tol=1e-6)
assert dpo_loss(ones, zeros, zeros, zeros, ones, ones).item() < math.log(2)

# z 极负时 logsigmoid 仍然有限
assert torch.isfinite(dpo_loss(zeros, ones * 1e4, zeros, zeros, ones, ones, beta=1.0))

# beta 必须为正
try:
    dpo_loss(*args, beta=0.0)
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError for beta = 0")
```

### 复杂度与追问

设 batch 大小为 $B$、序列长度为 $T$。时间 $O(BT)$，中间张量空间 $O(BT)$。

- 追问「两个 loss 数值不同有关系吗」：没关系。surrogate 只保证对 policy 的梯度一致，日志里要报的还是 `dpo_loss` 的值。
- 追问「reference 为什么不能接梯度」：DPO 的目标是在固定 reference 附近优化 policy，reference 一旦被更新，隐式奖励的基准也跟着变，目标就不是 DPO 了。

## 题怎么来的

`fireworks-grpo-sft-loss` 把 GRPO 写成了加权 logprob。这道题把同样的问题换成直接偏好优化（DPO）：如果训练端只支持“带权重的 logprob 之和”，DPO 能不能跑，权重是什么。DPO loss 本身怎么推导见 `openai-dpo-loss`。面试官会先给你一段有问题的代码，见下一节。

## 故意错误的起始片段（用于找 bug）

下面是旧版教学里要修复的错误片段，不是参考答案。对照上面的题面，找出偏离接口或梯度契约的地方；正确实现和测试在前面的练习部分。

```python
def dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    # pol_* / ref_*: [B, T] token logprob；mask_*: [B, T] response mask
    lw = (pol_w * mask_w).sum(-1) / mask_w.sum(-1)
    ll = (pol_l * mask_l).sum(-1) / mask_l.sum(-1)
    rw = (ref_w * mask_w).sum(-1) / mask_w.sum(-1)
    rl = (ref_l * mask_l).sum(-1) / mask_l.sum(-1)
    z = beta * ((lw - rw) - (ll - rl))
    return -torch.log(torch.sigmoid(z)).mean()
```

## 错在哪

**序列 logprob 被除以了长度。** DPO 里的 $\log\pi(y\mid x)$ 是 token logprob 之和。按长度平均得到的是另一个目标，接近 SimPO 的长度归一化，$\beta$ 的尺度也不一样。可以这么做，但要说清楚这已经不是 DPO。

**`log(sigmoid(z))` 数值不稳。** $z$ 很负时 `sigmoid` 下溢到 0，`log` 得到 `-inf`。应该用 `F.logsigmoid(z)`。

另外，参考模型的 logprob 要在 `no_grad` 下算。这段代码里看不出来，面试时要问一句。

## 梯度

$\frac{d}{dz}\big(-\log\sigma(z)\big) = -\sigma(-z)$，$z$ 对 $\theta$ 的梯度是 $\beta(\nabla\log\pi_w - \nabla\log\pi_l)$，参考模型不贡献梯度。合起来：

$$
\nabla_\theta\mathcal{L} = -\beta\,\sigma(-z)\,\big(\nabla_\theta\log\pi_\theta(y_w\mid x) - \nabla_\theta\log\pi_\theta(y_l\mid x)\big)
$$

所以等价的加权 logprob loss 是：chosen 的每个 token 权重为 $+c$，rejected 的每个 token 权重为 $-c$，其中 $c = \mathrm{sg}(\beta\sigma(-z))$，$\mathrm{sg}$ 表示停止梯度。练习里的 `dpo_loss_weighted` 就是这个形式。

## 权重怎么读

$\sigma(-z)$ 可以读成模型当前“把这一对排反了”的概率。$z \ll 0$ 时模型更偏向 rejected，权重接近 $\beta$；$z \gg 0$ 时已经排对了，权重趋于 0。所以 DPO 自带难例挖掘，不需要另外按 loss 采样。

和 GRPO 对比：GRPO 的权重来自奖励算出的 advantage，在一步之内固定；DPO 的权重来自模型自己当前的隐式奖励差，会在训练过程中一直变化。

## 追问

**chosen 的 logprob 为什么也会下降？** 梯度只约束 $\log\pi_w - \log\pi_l$ 这个差，没有约束 $\log\pi_w$ 本身。两者一起降、rejected 降得更快，loss 照样在下降。常见的补救是在 chosen 上加一项监督微调（SFT）loss，在加权形式里就是给 chosen 的 token 权重再加一个正常数。

**$\beta$ 大小有什么影响？** $\beta$ 同时出现在 $z$ 里和权重前面。$\beta$ 大时 $z$ 很快饱和，权重很快掉到 0，模型离参考模型不远就停了；$\beta$ 小时要走很远才饱和。

**IPO 呢？** 记 $h = \Delta_w - \Delta_l$，其中 $\Delta=\log\pi_\theta(y\mid x)-\log\pi_{\mathrm{ref}}(y\mid x)$。IPO 的 loss 是 $\big(h - \frac{1}{2\tau}\big)^2$，梯度系数是 $-2\big(h - \frac{1}{2\tau}\big)$，对 $h$ 是线性的：间隔不够时为正，把 chosen 往上推；间隔超过 $\frac{1}{2\tau}$ 时变成负的，往回拉。DPO 的系数永远为正，只是趋于 0。见 `align-ipo`。

## 相关题

- [[align-dpo]]：口述版，讲隐式奖励怎么推出来、$\beta$ 怎么取，不要求写代码。
- [[openai-dpo-loss]]：口述版，从 DPO 相对 PPO 少了什么切入。
- [[coding-loss-atlas]]：把 DPO 和 SFT、PPO、SimPO、KL 等 loss 都写成「权重 × logprob」放在一起对照。
- [[align-ipo]]：IPO 的损失形状和动机，可以和本卡末尾 IPO 梯度系数的追问对照着看。
