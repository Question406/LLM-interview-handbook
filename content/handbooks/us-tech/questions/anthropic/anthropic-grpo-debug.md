---
id: anthropic-grpo-debug
section: anthropic
order: 25
level: S
title: Anthropic：RL Fundamentals，修一段有 bug 的 GRPO
quick: >-
  我会先检查 sampling 输入和组内优势：multinomial 要吃概率或非负权重，奖励全相同时优势应为 0。公开转述中的 GRPO
  脚本约一两百行，第三处 bug 没公开；修完还要解释 ratio 为什么可能离开 1。
tags:
  - 完整编程练习
  - Anthropic
  - GRPO
  - PPO
  - Coding
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: RL Fundamentals — GRPO Debug，1Point3Acres，last asked 2026-03-02
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/rl-fundamentals-grpo-debug
    type: candidate-first-hand
  - title: 'Debug GRPO / RL Training Code, AceOffer'
    url: >-
      https://aceoffer.app/interviews/debug_grpo_rl_training_code_technical_deep_dive
    type: secondary
  - title: 'DeepSeekMath, GRPO'
    url: 'https://arxiv.org/abs/2402.03300'
    type: primary
---

## 题目描述

实现组内奖励 normalization 和带裁剪的策略损失，用于检查一个小型 GRPO 训练步骤。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`advantages(rewards)` 接收 NumPy 浮点数组 `[P,G]`，每行是一道 prompt 的 G 个奖励，返回同形数组：每组减去本组均值，再除以该行组内总体标准差（ddof=0）；标准差小于 `1e-8` 的组全部返回 0。

`loss_grad(new, old, adv, mask, eps=0.2)` 返回 `(loss, grad)`。`new`、`old` 是 `[P*G,T]` 的 sampling token log probability，`adv` 是 `[P*G]`，`mask` 是同形布尔数组，True 表示计入损失；`0 < eps < 1`。令 `r=exp(new-old)`，每个有效 token 的损失定义为 `-min(r*A, clip(r,1-eps,1+eps)*A)`，其中 A 是该序列的优势。`loss` 是有效 token 的均值，`grad` 是对 new 的导数，形状与 new 一致。old、adv 是常量；不加入额外 reference model KL 项。全部 token 被屏蔽时返回 0 和全零梯度。

### 示例

```text
advantages([[1,1],[0,2]]) = [[0,0],[-1,1]]
new = old = [[0],[0]], adv = [1,-1], mask = [[True],[True]]
loss = 0, grad = [[-0.5],[0.5]]
```

## 解题思路与参考答案

我会先跑出错误，再沿着 sampling、组内优势和 ratio 逐项检查。比如一组奖励全相同，优势应当全是 0，出现 NaN 就先看标准差和除零；第三处 bug 的具体代码没有公开，练习里的实现不能当成原题答案。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。原题是 PyTorch 脚本，这里用 NumPy 手写前向和梯度，CPU 上验证。

### 题面、接口与约束

- `advantages(rewards) -> ndarray`：`rewards` 形状 `[P, G]`，P 个 prompt、每个 prompt 采 G 个回答。每组减去组均值、除以组内总体标准差；标准差小于 `1e-8` 的组优势全为 0。
- `loss_grad(new, old, adv, mask, eps=0.2) -> (loss, grad)`：`new`、`old` 形状 `[P*G, T]`，是被选中 token 在当前策略和 sampling 策略下的 logprob；`adv` 形状 `[P*G]`；`mask` 与 `new` 同形状的布尔数组，标出参与损失的 response token。返回 PPO 式负 clipped surrogate 在有效 token 上的均值，以及它对 `new` 的梯度。
- `old` 和 `adv` 当常量，不加 reference model 的 KL；`mask` 全为 False 时返回损失 0 和全零梯度；`0 < eps < 1`，形状不符时抛 `ValueError`。
- 练习里对应三类 bug：直接用 logits sampling、零方差组除以零、ratio 漏了 `exp`。只有前两类在公开转述里有具体线索，第三类是推测，不当作已核实的原题。

### 输入输出示例

```text
advantages([[1, 1], [0, 2]])  -> [[0, 0], [-1, 1]]   # 第一组奖励全相同，优势为 0
loss_grad(new=old, ...)       -> 每个 token 的 ratio 都是 1
```

### 解题思路与正确性

先把优化目标的符号定清楚：优化器最小化损失，所以 surrogate 要取负，写成$-\min(\rho A, \mathrm{clip}(\rho, 1-\varepsilon, 1+\varepsilon) A)$，其中 $\rho = \exp(\text{new} - \text{old})$。

对单个 token，`min` 选中 clip 分支时损失与 `new` 无关，梯度为 0。这只发生在两种情况：$A>0$ 且 $\rho>1+\varepsilon$，或 $A<0$ 且 $\rho<1-\varepsilon$，也就是策略已经朝有利方向走得太远。其他情况下 `min` 选中原始的 $\rho A$，梯度是 $-A\rho$，再除以有效 token 数。

第二个 epoch 时策略已经更新，ratio 不再恒等于 1。clip 只截断梯度，不保证 KL 有硬上界。

### 完整参考实现（Python 3）

```python
import numpy as np


def advantages(rewards):
    """组内 standardization 优势：rewards [P, G] -> [P, G]；零方差组的优势为 0。"""
    rewards = np.asarray(rewards, dtype=float)
    if rewards.ndim != 2 or rewards.shape[1] == 0:
        raise ValueError(
            f"rewards must have shape [P, G] with G > 0, got {rewards.shape}"
        )
    centered = rewards - rewards.mean(axis=1, keepdims=True)
    std = rewards.std(axis=1, keepdims=True)  # 总体标准差，G=1 时为 0 而不是 NaN
    return np.divide(centered, std, out=np.zeros_like(centered), where=std >= 1e-8)


def loss_grad(new, old, adv, mask, eps=0.2):
    """PPO 式 clipped surrogate 损失（取负、按有效 token 平均）及其对 new 的梯度。

    new, old, mask: [N, T]；adv: [N]。old 和 adv 视为常量。
    """
    new = np.asarray(new, dtype=float)
    old = np.asarray(old, dtype=float)
    adv = np.asarray(adv, dtype=float)[:, None]  # [N, 1]，广播到每个 token
    mask = np.asarray(mask, dtype=bool)
    if new.ndim != 2 or new.shape != old.shape or new.shape != mask.shape:
        raise ValueError(
            f"new/old/mask shapes differ: {new.shape}, {old.shape}, {mask.shape}"
        )
    if adv.shape[0] != new.shape[0]:
        raise ValueError(f"adv has {adv.shape[0]} rows, expected {new.shape[0]}")
    if not 0 < eps < 1:
        raise ValueError(f"eps must be in (0, 1), got {eps}")

    num_tokens = int(mask.sum())
    if num_tokens == 0:
        return 0.0, np.zeros_like(new)

    ratio = np.exp(new - old)
    unclipped = ratio * adv
    clipped = np.clip(ratio, 1 - eps, 1 + eps) * adv
    loss = float((-np.minimum(unclipped, clipped) * mask).sum() / num_tokens)

    # 只有 clip 阻止策略继续往有利方向走时，梯度才为 0
    clipped_out = ((adv > 0) & (ratio > 1 + eps)) | ((adv < 0) & (ratio < 1 - eps))
    grad = -adv * ratio * ~clipped_out * mask / num_tokens
    return loss, grad
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(advantages([[1, 1], [0, 2]]), [[0, 0], [-1, 1]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 组内 standardization；奖励全相同的组优势为 0，不是 NaN
assert np.allclose(advantages([[1, 1], [0, 2]]), [[0, 0], [-1, 1]])

# 组大小为 1：总体标准差为 0，优势为 0
assert np.allclose(advantages([[3.0]]), [[0.0]])

# new == old 时 ratio 为 1，损失等于 -A 的 token 均值
logp = np.zeros((2, 2))
loss, _ = loss_grad(logp, logp, np.array([1.0, -1.0]), np.ones((2, 2), bool))
assert np.isclose(loss, 0.0)

# 解析梯度与中心差分一致；第 2 行第 1 个 token 的 ratio < 1-eps 且 A<0，被 clip，梯度为 0
new = np.array([[0.05, -0.1], [0.4, -0.5]])
old = np.zeros_like(new)
adv = np.array([1.0, -1.0])
mask = np.array([[1, 0], [1, 1]], bool)
loss, grad = loss_grad(new, old, adv, mask)
step = 1e-6
for i in range(2):
    for j in range(2):
        plus = new.copy()
        minus = new.copy()
        plus[i, j] += step
        minus[i, j] -= step
        numeric = (
            loss_grad(plus, old, adv, mask)[0] - loss_grad(minus, old, adv, mask)[0]
        ) / (2 * step)
        assert np.isclose(numeric, grad[i, j], atol=1e-7)
assert grad[1, 1] == 0

# mask 全为 False：损失和梯度都是 0
loss, grad = loss_grad(new, old, adv, np.zeros_like(mask))
assert loss == 0
assert not grad.any()

# 形状或 eps 非法
expect_value_error(advantages, [1.0, 2.0])
expect_value_error(loss_grad, new, old[:1], adv, mask)
expect_value_error(loss_grad, new, old, adv, mask, eps=1.5)
```

### 复杂度与追问

设 P 个 prompt、每组 G 个回答、每个回答 T 个 token。两个函数的时间和空间都是 O(PGT)。

- 追问「sampling 那一处怎么修」：sampling 要用 softmax 之后的非负概率，或者直接用 `Categorical(logits=...)`。
- 追问「mask 覆盖哪些 token」：只覆盖 response token；prompt、pad 和工具返回的原文都不进损失。
- 追问「要加 KL 怎么办」：先说清 reference 策略是谁、按 token 还是按序列 reduction。old 策略的 ratio 和对 reference 的 KL 是两项，不能混成一项。

## 真题记录

一亩三分地把这题标成 Anthropic 的 RLFundamentals，电话面、技术面、onsite coding 都出现过，频率低，最近一次是 2026-03-02，正文要登录才能看。AceOffer 说他们看到两份候选人报告，分别在 2025 年 10 月和 2026 年 3 月，招聘官和候选人都用 RL Fundamentals 这个名字。

脚本大约 100 到 200 行，用 PyTorch，包含 sampling、组内优势和 PPO 式的 ratio 与 clip，原文没有公开。AceOffer 写明：两份报告点名了下面前两处 bug；第三处报告只说「还有一个 bug」，具体是哪一行是 AceOffer 按追问反推的，不是候选人原话。

同一轮后面还有别的 coding，AceOffer 提到了加权 batch 和分布式找中位数，那些不是这道 GRPO。

## 跑起来就能看见的两处

`torch.multinomial` 要的是非负权重，不是 logits。logits 里有负数时直接传进去会抛 `RuntimeError`。如果某一行碰巧全是非负数，它不会崩，但会按原始 logits 的比例抽样，而不是 softmax 之后的策略。全相等的正 logits 下两种抽法都是均匀分布，所以单测可能放过这个 bug。

```python
action = torch.multinomial(torch.softmax(logits, dim=-1), num_samples=1)
# 或者 Categorical(logits=logits).sample()，它内部会做 log_softmax
```

一组回报完全一样时标准差是 0，`(r - mean) / std` 得到 NaN。PyTorch 的 `std` 默认是 unbiased estimate，组大小为 1 时分母 `n-1` 为 0，同样是 NaN，加 eps 也救不了。所以组大小至少为 2，并且用总体标准差。回报全相同时分子本来就是 0，除以 `std + eps` 得到 0，这一组不该产生更新。eps 只是避免 0 除以 0，不会把「全对」变成学习信号。

```python
def group_advantage(rewards, group_size):
    grouped = rewards.view(-1, group_size)
    mean = grouped.mean(dim=1, keepdim=True)
    std = grouped.std(dim=1, keepdim=True, correction=0)
    centered = grouped - mean
    adv = torch.where(std < 1e-8, torch.zeros_like(grouped), centered / std)
    return adv.reshape(-1)
```

## 第三处和修完之后的追问

报告没有贴出第三处的代码。修完前两处后，面试官会问 importance sampling 比。正确写法是

$$
\rho = \exp(\log\pi_\theta - \log\pi_{\mathrm{old}})
$$

如果直接把 $\log\pi_\theta - \log\pi_{\mathrm{old}}$ 当成 $\rho$，它在 0 附近，而 clip 区间是 $[1-\varepsilon, 1+\varepsilon]$，截断就失去了意义。AceOffer 认为这就是藏起来的第三处，并说面试官会问：如果 ratio 写成对数差，模型还能不能训。这是追问内容，不是一份公开的 diff。

名义上是 on-policy：第一步更新前 $\pi_\theta$ 和 sampling 策略是同一个，$\rho$ 应该是 1。如果在同一批 sampling 轨迹（rollout）上再做第二个 mini-epoch，$\pi_\theta$ 已经变了，$\rho$ 就会离开 1，这不是 bug。还有两种情况会让第一步的 $\rho$ 就不是 1：sampling 引擎和训练前向用的不是同一套 kernel；sampling 时用了 temperature 或 top-p，重算 logprob 时却用了裸 logits。打印 `ratio.mean()` 之前，先确认 old logprob 是 sampling 当时存下来的，并且已经 `detach`。

优势是每条回答一个数，要广播到它的 response token 上再乘 mask。prompt、pad 和工具返回的原文不进损失。优势本身要 `detach`，否则梯度会穿进奖励计算。

```python
def clipped_loss(new_logp, old_logp, adv, mask, eps=0.2):
    adv = adv.detach()[:, None]
    rho = torch.exp(new_logp - old_logp)
    unclipped = rho * adv
    clipped = torch.clamp(rho, 1.0 - eps, 1.0 + eps) * adv
    per_token = -torch.minimum(unclipped, clipped)
    return (per_token * mask).sum() / mask.sum().clamp(min=1)
```

Clip 只在「这一步还想往更远处推」的那一侧把梯度掐掉，即 $A>0$ 且 $\rho>1+\varepsilon$，或 $A<0$ 且 $\rho<1-\varepsilon$。它不保证 $\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{old}})$ 有上界，GRPO 论文另外加了对 reference model 的 KL。token 级 KL 的 reduction 见 `coding-kl-div`。偏好模型的 logistic 损失见 `anthropic-pref-bt`，那是另一轮，不在这段脚本里。

## 追问

**全对的一组加了 eps 之后，优势是不是一个很小的正数？**
不是。每个回报减去组均值后是 0，除以任何正数仍是 0。eps 解决的只是 NaN。

**为什么不把优势放进 logprob 的计算图里？**
优势是这批样本上的权重。如果让它跟着 $\pi_\theta$ 变，就多出一条没有推导依据的梯度。

**第一步 ratio 就是 1，clip 还有什么用？**
第一步确实没用。只有到第二个 epoch，或者 sampling 和打分不是同一次前向时，才会有 token 的 $\rho$ 离开 1。如果只更新一次、logprob 也来自同一次前向，clip 什么都不做。

## 相关题

- [[p3a-anthropic-rl-fundamentals-grpo-debug]]：同一道 Anthropic 题的另一份整理，`advantages` 和 `loss_grad` 接口几乎一样，多讲了 response mask 和 ref KL 的追问。
- [[align-grpo]]：概念题，讲 GRPO 为什么不要 critic、组内奖励全一样时为什么没梯度。
- [[sys-rollout-logprob]]：专门展开「ratio 为什么不是 1」这个追问，按 micro batch、温度、权重版本逐项排查。
- [[fireworks-grpo-sft-loss]]：同一个 clipped surrogate，改写成 detach 权重乘 logprob 的 SFT 式 loss，梯度推导更细。
- [[openai-ppo-clip]]：讲 clip 只锚 $\pi_{\mathrm{old}}$、ratio 爆了怎么收，补的是这里第一步 ratio 恒为 1 之后的情况。
- [[coding-gumbel-max]]：第一个 bug 是直接拿 logits sampling，那张讲从 logits 正确 sampling 的另一种写法 $\arg\max(z/\tau+g)$。
