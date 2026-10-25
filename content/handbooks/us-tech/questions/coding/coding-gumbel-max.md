---
id: coding-gumbel-max
section: coding
order: 13
level: A
title: 白板：Gumbel-max 采样，和 softmax 温度的关系
quick: "硬采样先缩放 logits，再用 argmax(z/τ+g)，得到温度采样。Gumbel-softmax 松弛用 softmax((z+g)/τ)，它的 τ 只改变连续输出和梯度，在固定噪声下不改变选中的类别。"
tags:
  - 完整编程练习
  - Coding
  - Gumbel
  - Sampling
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Categorical Reparameterization with Gumbel-Softmax
    url: https://arxiv.org/abs/1611.01144
    type: primary
  - title: torch.nn.functional.gumbel_softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.gumbel_softmax.html
    type: primary
---

## 题目描述

实现 Gumbel 噪声、离散类别采样以及可选 hard 输出的可微 Gumbel-softmax 接口。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `gumbel_noise(shape, generator=None, device=None, dtype=torch.float32) -> Tensor`：生成标准 Gumbel 噪声 $g=-\log(-\log U)$。
- `gumbel_max(logits, tau=1.0, generator=None) -> LongTensor[...]`：输出形状为 logits 去掉最后一维；沿最后一维从 $\mathrm{softmax}(\text{logits}/\tau)$ 抽一个类别。
- `gumbel_softmax(logits, tau=1.0, hard=False, generator=None) -> Tensor`：输出与 logits 同形。标准松弛 $\mathrm{softmax}((\text{logits}+g)/\tau)$。`hard=True` 时前向输出 one-hot，反向沿松弛输出传梯度（straight-through）。
- `tau` 必须是有限正数。logits 可以用 $-\infty$ 做 mask，但每行至少有一个有限值；合法输入不含 NaN 或 $+\infty$。

### 输入输出示例

```text
logits = [[-inf, 0, -inf]], tau = 1
gumbel_max(logits) -> [1]
gumbel_softmax(logits, hard=True) -> [[0, 1, 0]]

logits = [0, 2], tau = 0.5 时，gumbel_max 多次独立抽样中
类别 1 的理论概率约为 0.982；不要求单次或有限次实验精确命中此比例。
```

## 解题思路与参考答案

Gumbel-max 给 logits 加独立的标准 Gumbel 噪声，再取最大值；$\arg\max_i(z_i+g_i)$ 与从 $\mathrm{softmax}(z)$ 抽样同分布。要按温度 $\tau$ 抽类别，就先把 logits 缩放成 $z/\tau$，再加标准噪声。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `gumbel_noise(shape, generator=None, device=None, dtype=torch.float32) -> Tensor`：生成标准 Gumbel 噪声 $g=-\log(-\log U)$。
- `gumbel_max(logits, tau=1.0, generator=None) -> LongTensor[...]`：沿最后一维从 $\mathrm{softmax}(\text{logits}/\tau)$ 抽一个类别。
- `gumbel_softmax(logits, tau=1.0, hard=False, generator=None) -> Tensor`：标准松弛 $\mathrm{softmax}((\text{logits}+g)/\tau)$。`hard=True` 时前向输出 one-hot，反向沿松弛输出传梯度（straight-through）。
- `tau` 必须是有限正数。logits 可以用 $-\infty$ 做 mask，但每行至少有一个有限值；NaN 或 $+\infty$ 一律抛 `ValueError`。

### 输入输出示例

```text
z = [0, 2]，30000 次 gumbel_max(z, tau=0.5)  -> 选中类别 1 的比例 ≈ softmax([0, 4])[1] ≈ 0.982
同一份噪声 g：gumbel_softmax(z, tau=0.3, hard=True) 和 tau=3 的 hard 结果是同一个类别
```

### 解题思路与正确性

Gumbel-softmax 的 $\tau$ 除的是 $z+g$ 整体。对固定噪声，除以正数不改变 argmax，所以这个 $\tau$ 只控制连续输出有多尖、梯度有多大，不改变 `hard=True` 选出的类别。这就是两种温度不能混用的原因。

$U$ 必须严格落在 $(0,1)$ 内，否则 $\log 0$ 或 $\log(-\log 1)$ 会得到无穷大。clamp 的端点要用当前 dtype 能表示的值：下界用 `finfo.tiny`，上界用 `1 - finfo.eps`。如果写 `1 - 1e-20`，float32 会把它舍入回 1。

### 完整参考实现（Python 3）

```python
import math

import torch


def gumbel_noise(shape, generator=None, device=None, dtype=torch.float32):
    """标准 Gumbel 噪声 -log(-log U)，U 截在当前 dtype 可表示的开区间 (0, 1) 内。"""
    uniform = torch.rand(shape, generator=generator, device=device, dtype=dtype)
    finfo = torch.finfo(dtype)
    uniform = uniform.clamp(min=finfo.tiny, max=1 - finfo.eps)
    return -torch.log(-torch.log(uniform))


def _check_inputs(logits, tau):
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError(f"tau must be a finite positive number, got {tau}")
    if torch.isnan(logits).any() or torch.isposinf(logits).any():
        raise ValueError("logits must not contain NaN or +inf")
    if not torch.isfinite(logits).any(dim=-1).all():
        raise ValueError("every row needs at least one unmasked (finite) logit")


def gumbel_max(logits, tau=1.0, generator=None):
    """沿最后一维从 softmax(logits / tau) 抽一个类别下标。"""
    _check_inputs(logits, tau)
    noise = gumbel_noise(logits.shape, generator, logits.device, logits.dtype)
    return torch.argmax(logits / tau + noise, dim=-1)


def gumbel_softmax(logits, tau=1.0, hard=False, generator=None):
    """松弛输出 softmax((logits + g) / tau)；hard=True 时前向 one-hot、反向沿松弛。"""
    _check_inputs(logits, tau)
    noise = gumbel_noise(logits.shape, generator, logits.device, logits.dtype)
    soft = torch.softmax((logits + noise) / tau, dim=-1)
    if not hard:
        return soft
    index = soft.argmax(dim=-1, keepdim=True)
    one_hot = torch.zeros_like(soft).scatter_(-1, index, 1.0)
    return one_hot + soft - soft.detach()  # 前向值是 one_hot，梯度来自 soft
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert abs(samples.float().mean() - expected) < 0.015` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# gumbel_max 的采样频率匹配 softmax(z / tau)
logits = torch.tensor([[0.0, 2.0]]).expand(30000, -1)
for tau in (0.5, 2.0):
    generator = torch.Generator().manual_seed(7)
    samples = gumbel_max(logits, tau, generator)
    expected = torch.softmax(torch.tensor([0.0, 2.0]) / tau, dim=-1)[1]
    assert abs(samples.float().mean() - expected) < 0.015

# 同一份噪声下，松弛温度不改变 hard 选出的类别；输出每行和为 1
z = torch.tensor([[0.1, 0.7, -0.2]], requires_grad=True)
sharp = gumbel_softmax(z, 0.3, True, torch.Generator().manual_seed(2))
smooth = gumbel_softmax(z, 3.0, True, torch.Generator().manual_seed(2))
assert sharp.argmax(-1).equal(smooth.argmax(-1))
assert torch.allclose(sharp.sum(-1), torch.ones(1))

# hard=True 的梯度来自松弛输出，是有限值
(sharp * torch.tensor([[1.0, 2.0, 3.0]])).sum().backward()
assert torch.isfinite(z.grad).all()

# 被 -inf mask 的类别永远不会被选中
masked = torch.tensor([[float("-inf"), 0.0, float("-inf")]]).expand(1000, -1)
assert (gumbel_max(masked, 1.0, torch.Generator().manual_seed(0)) == 1).all()

# 噪声没有 inf / NaN
assert torch.isfinite(gumbel_noise((10000,))).all()

# 非法温度、整行被 mask、NaN
expect_value_error(gumbel_max, torch.zeros(1, 2), 0.0)
expect_value_error(gumbel_max, torch.full((1, 2), float("-inf")), 1.0)
expect_value_error(gumbel_softmax, torch.tensor([[0.0, float("nan")]]), 1.0)
```

### 复杂度与追问

设 batch 为 B、类别数为 V。两个函数的时间和空间都是 O(BV)。

- 追问「两种温度到底差在哪」：松弛温度改变连续输出和梯度，但在固定噪声下不改变 `hard=True` 的类别；要改变抽到哪个类别的分布，得先缩放 logits 再加噪声。
- 追问「GPU 上为什么有时更快」：加噪声加 argmax 不需要归一化，也不需要累计分布函数，容易和前一个 kernel 融合。

## 题怎么来的

Jang et al. 和 Maddison et al. 把 Gumbel-max 写成了可微松弛，研究岗喜欢问「这和 softmax 温度是不是一回事」。OpenAI 的采样题有时不用 multinomial，而是让你写 Gumbel 噪声加 logits。Apple、Anthropic 问得少一些，但作为「离散采样怎么反传」的标准答案要能写出来。普通温度采样见 `coding-topk-nucleus`。

## Gumbel-max：argmax 就是采样

$g_i=-\log(-\log U_i)$，$U_i\sim\mathrm{Uniform}(0,1)$。对概率 $\pi$，或者等价地对 logits $z=\log\pi+c$：

$$
y=\arg\max_i(z_i+g_i).
$$

$y$ 与 `multinomial(softmax(z))` 同分布。

温度要区分两种用途。要从 $\mathrm{softmax}(z/\tau)$ 抽离散类别，用 $\arg\max_i(z_i/\tau+g_i)$。标准 Gumbel-softmax 松弛的连续输出是 $\mathrm{softmax}((z+g)/\tau)$；固定噪声时 $\arg\max((z+g)/\tau)=\arg\max(z+g)$，类别不随正温度变，温度只控制松弛的尖锐程度。`hard=True` 用的是 straight-through 梯度，也不会把松弛温度变成类别温度。

## 什么时候用，什么时候不用

训练中需要对离散选择反传（硬注意力、离散 bottleneck）时才用 Gumbel-softmax。纯生成采样用 `multinomial` 或 Gumbel-max 都对。

做 nucleus / top-k 截断后再加 Gumbel，等于在截断后的子集上采样，顺序仍然是先截断再加噪声。温度只作用一次，在 logits 上，不要再对 softmax 输出除温度。mask 先打 $-\infty$ 再加 Gumbel 噪声：$-\infty$ 加任何有限噪声仍是 $-\infty$，argmax 不会选中它；整行都被 mask 时要报错。

## 追问

**为什么等价于 softmax 采样？**
Gumbel 分布是 max-stable 的：独立的 Gumbel 变量平移后取最大值仍是 Gumbel，可以算出 $\arg\max_i(\log\pi_i+g_i)=i$ 的概率正好是 $\pi_i$。面试里说到这一步就够了。
**两种温度相同吗？**
不同。硬类别温度先缩放 logits 再加标准噪声；松弛温度缩放的是 logits 与噪声的和，改变的是连续输出和梯度。
**能替代 nucleus 吗？**
不能，它不会自动截尾。要 nucleus 仍然先按 `coding-topk-nucleus` 截断，再在核上做 Gumbel-max。

## 相关题

- [[coding-softmax-stable]]：Gumbel-max 等价于按 softmax 概率采样，那张讲这个 softmax 本身怎么减 max、沿哪一维算。
- [[anthropic-grpo-debug]]：调试题里第一个 bug 就是把原始 logits 直接喂给 multinomial，从 logits 正确采样正是这张的内容。
- [[coding-topk-nucleus]]：Gumbel-max 本身不截尾，要 top-k 或 nucleus 时先按那张卡截断。
- [[p3a-cohere-numpy-top-k-sampling]]：用累计概率做逆变换的 top-k 采样，可以和 argmax 加噪声的写法对照。
- [[apple-topk-sample]]：温度、top-k、nucleus 的顺序，以及端侧为什么常用 top-k。
