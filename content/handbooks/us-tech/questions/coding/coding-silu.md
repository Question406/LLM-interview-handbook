---
id: coding-silu
section: coding
order: 24
level: A
title: 白板：SiLU / Swish 手写，数值上哪里会炸
quick: >-
  SiLU 是 $\mathrm{SiLU}(x)=x\cdot\sigma(x)$，也就是 $\beta=1$ 的 Swish。手写时要防止大负数使
  $e^{-x}$ 溢出，可以只计算 `exp(-abs(x))` 后按符号分支，或用 `tanh` 形式；Llama 的 SwiGLU 在 gate
  支路使用它。
tags:
  - 完整编程练习
  - Coding
  - SiLU
  - Swish
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: torch.nn.functional.silu
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.functional.silu.html'
    type: primary
  - title: >-
      Sigmoid-Weighted Linear Units for Neural Network Function Approximation in
      Reinforcement Learning
    url: 'https://arxiv.org/abs/1702.03118'
    type: primary
  - title: Searching for Activation Functions (Swish)
    url: 'https://arxiv.org/abs/1710.05941'
    type: primary
---

## 题目描述

实现可在大正数和大负数上正常工作的 sigmoid 与 SiLU 接口。除了前向结果正确，还要保证对有限输入求导时不因中间计算出现 inf 或 NaN。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `sigmoid_stable(x)`：数值稳定的 sigmoid，任何有限输入都不溢出，返回 float32。
- `silu(x)`：$x\cdot\sigma(x)$，用 `sigmoid_stable` 实现。
- `silu_tanh(x)`：用恒等式 $\sigma(x)=\tfrac12(1+\tanh(x/2))$ 实现的 SiLU，作为独立对照。
- 输入是有限的浮点张量，可以包含 ±1000 这样的极端值。两个 SiLU 都在 float32 里计算，输出的形状和 dtype 与输入一致；前向和梯度都不能出现 inf/NaN。

- sigmoid 的数学定义是 `sigma(x)=1/(1+exp(-x))`；本题要求实现与该函数相同的有限数值结果。
### 示例

```text
silu(0)     = 0
silu(1000)  ≈ 1000
silu(-1000) ≈ 0
```

## 解题思路与参考答案

我会把 SiLU 写成输入乘稳定的 sigmoid，并用极大正负输入同时检查前向和梯度。比如 -1000 的朴素写法前向可能碰巧接近 0，反向却会因为指数溢出产生 NaN。实现里先算不会上溢的指数，再按符号组合 sigmoid。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `sigmoid_stable(x)`：数值稳定的 sigmoid，任何有限输入都不溢出，返回 float32。
- `silu(x)`：$x\cdot\sigma(x)$，用 `sigmoid_stable` 实现。
- `silu_tanh(x)`：用恒等式 $\sigma(x)=\tfrac12(1+\tanh(x/2))$ 实现的 SiLU，作为独立对照。
- 输入是有限的浮点张量，可以包含 ±1000 这样的极端值。两个 SiLU 都在 float32 里计算，输出的形状和 dtype 与输入一致；前向和梯度都不能出现 inf/NaN。

### 输入输出示例

```text
silu(0)     = 0
silu(1000)  ≈ 1000
silu(-1000) ≈ 0      # 朴素写法前向碰巧也是 -0，但反向梯度是 NaN
```

### 解题思路与正确性

稳定版 sigmoid 只算 $z=e^{-|x|}$。$|x|$ 非负，所以 $z\in(0,1]$，永远不会溢出。$x\ge 0$ 时 $\sigma(x)=1/(1+z)$；$x<0$ 时 $\sigma(x)=e^{x}/(1+e^{x})=z/(1+z)$。

`torch.where` 会把两个分支都算出来再挑选，没被选中的分支也参与计算，反向时它的梯度虽然乘了 0，但如果那个分支本身是 inf，$0\cdot\infty$ 仍然是 NaN。所以两个分支都必须对所有输入安全，这里两个分支都只用 $z$，满足这个要求。

`silu_tanh` 走的是另一条公式，`tanh` 本身对大输入是饱和的，不会溢出。两个实现和 `F.silu` 三方对照，前向和梯度都一致，才说明稳定写法是对的。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def sigmoid_stable(x):
    """数值稳定的 sigmoid：只计算 exp(-|x|)，任何有限输入都不溢出。返回 float32。"""
    x = x.float()
    z = torch.exp(-torch.abs(x))  # z ∈ (0, 1]
    return torch.where(x < 0, z / (1 + z), 1 / (1 + z))


def silu(x):
    """SiLU(x) = x * sigmoid(x)，在 float32 里计算，输出转回输入 dtype。"""
    return (x.float() * sigmoid_stable(x)).to(x.dtype)


def silu_tanh(x):
    """用 sigmoid(x) = (1 + tanh(x / 2)) / 2 计算 SiLU，作为独立对照。"""
    x32 = x.float()
    return (x32 * (0.5 * (1.0 + torch.tanh(0.5 * x32)))).to(x.dtype)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.isfinite(ours).all()` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
torch.set_num_threads(1)

x = torch.tensor([-1000.0, -40.0, -2.0, 0.0, 2.0, 40.0, 1000.0], requires_grad=True)

# 前向：极端值也有限，和 F.silu 一致
ours = silu(x)
reference = F.silu(x)
assert torch.isfinite(ours).all()
assert torch.allclose(ours, reference, atol=1e-6)

# 反向：梯度和 F.silu 一致，没有 NaN
(grad_ours,) = torch.autograd.grad(ours.sum(), x)
(grad_reference,) = torch.autograd.grad(reference.sum(), x)
assert torch.isfinite(grad_ours).all()
assert torch.allclose(grad_ours, grad_reference, atol=1e-6)

# tanh 形式作为独立对照
assert torch.allclose(silu_tanh(x), reference, atol=1e-5)

# 题面示例
assert silu(torch.tensor(0.0)).item() == 0
assert abs(silu(torch.tensor(1000.0)).item() - 1000) < 1e-3
assert abs(silu(torch.tensor(-1000.0)).item()) < 1e-6

# sigmoid_stable 在两侧都不溢出，且 sigma(-x) = 1 - sigma(x)
grid = torch.linspace(-50, 50, 101)
assert torch.isfinite(sigmoid_stable(grid)).all()
assert torch.allclose(sigmoid_stable(-grid), 1 - sigmoid_stable(grid), atol=1e-6)

# 半精度输入：输出 dtype 不变，-20 处结果约为 0 而不是 NaN
half = torch.tensor([-20.0, 0.0, 3.0], dtype=torch.float16)
assert silu(half).dtype == torch.float16
assert torch.allclose(silu(half).float(), F.silu(half.float()), atol=1e-2)
assert torch.isfinite(silu(half)).all()

# 输出形状不变
assert silu(torch.randn(2, 3, 4)).shape == (2, 3, 4)
```

### 复杂度与追问

设元素个数为 N。时间和输出空间都是 O(N)；float32 中间结果也是 O(N)。

- 追问「为什么不能只在一个分支里用 `exp(-x)`」：`torch.where` 两个分支都会算，没选中的分支溢出成 inf，反向时也会把 NaN 带进梯度。所以两侧都必须数值安全。

## 题怎么来的

Llama MLP 的 gating 用的是 SiLU，不是 ReLU 或 GELU。Meta 会让你手写；Apple 端侧会问 fp16 下大负值会怎样。SwiGLU 怎么接三个权重矩阵见 `coding-swiglu`。PyTorch 的 `F.silu` 就是这个函数，但白板上不能调用一下就完事，要能写出稳定的 $\sigma$。

## 定义和稳定 sigmoid

$$
\mathrm{SiLU}(x)=x\,\sigma(x)=\frac{x}{1+e^{-x}},\qquad
\sigma(x)=\tfrac12\big(1+\tanh(x/2)\big).
$$

Swish$_\beta(x)=x\,\sigma(\beta x)$，SiLU 就是 $\beta=1$ 的情况。$x\to+\infty$ 时 SiLU $\to x$；$x\to-\infty$ 时 SiLU $\to 0$。它过原点，$\mathrm{SiLU}(0)=0$，在小正数区域略大于 $0$，像一个「平滑的 ReLU」。它不是奇函数：$\mathrm{SiLU}(-x)=-x\sigma(-x)=-x(1-\sigma(x))=\mathrm{SiLU}(x)-x$，和 $\mathrm{SiLU}(x)$ 差一项 $x$；奇函数则要求它等于 $-\mathrm{SiLU}(x)$。

直接写 `x / (1 + exp(-x))` 会怎样：$x$ 是大正数时，$e^{-x}$ 下溢成 $0$，结果是 $x$，没问题；$x$ 是大负数时，$-x$ 是大正数，$e^{-x}$ 溢出成 inf，分母变成 inf。前向结果是 $x/\infty=-0$，碰巧接近正确值，但反向的梯度里会出现 $\infty/\infty$，得到 NaN。所以要按符号拆开：

$$
\sigma(x)=\begin{cases}
1/(1+e^{-x}) & x\ge 0\\
e^{x}/(1+e^{x}) & x<0.
\end{cases}
$$

或者全程用 $\tanh$ 形式。$x$ 极负时 $\sigma(x)\approx 0$，乘积 $x\cdot\sigma(x)$ 自然是 $0$，关键是计算过程中不能先溢出再乘。

`F.silu` 对半精度有融合的 kernel。自己写时先升到 fp32 计算，再转回原 dtype，和 RMSNorm 是同一个习惯，见 `coding-rmsnorm`。

## 和 GELU 的关系、在 MLP 里的位置

GELU 是 $x\Phi(x)$（$\Phi$ 是标准正态分布的 CDF），形状和 SiLU 很接近，GPT-2 用的是 GELU。Llama 把 SiLU 放在 gate 支路上：`silu(x W_g) * (x W_u)`，而不是 `silu(x W)` 之后再接一个线性层。

导数是 $\mathrm{SiLU}'(x)=\sigma(x)+x\sigma(x)(1-\sigma(x))$，手推反向时别漏掉第二项。面试如果问「为什么不用 ReLU」：gating 需要光滑、负半轴梯度不为零的激活；ReLU 在负半轴梯度为零，会出现 dead ReLU，和 GLU 结构不搭。

## 追问

**fp16 里朴素的 `x * sigmoid(x)` 在 $-20$ 处会怎样？**
fp16 最大约 65504，`exp(20)` 约为 $4.9\times10^8$，会溢出成 inf。前向结果碰巧是 0，但反向梯度是 NaN。稳定写法前向给出 $\approx 0$，梯度也有限。
**SiLU 和 Swish 要不要当成两个函数？**
论文里的 Swish 带参数 $\beta$；实现里和 Llama 说的 SiLU 就是 $\beta=1$ 的 Swish。别把它答成另一个不相关的激活函数。
**能不能 inplace？**
反向要用 $x$ 来算 $\sigma(x)$。除非融合的 backward 自己存了中间结果，否则不要用 `silu_` 把唯一一份 $x$ 覆盖掉。
**和 z-loss 有关吗？**
无关。z-loss 约束的是 logits 的 log-partition，见 `coding-z-loss`；SiLU 是 MLP 里的非线性。
