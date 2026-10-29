---
id: coding-layernorm
section: coding
order: 4
level: S
title: 白板：LayerNorm vs 在 feature 维上的 standardization，eps 和仿射
quick: >-
  对 $[B,T,D]$ 的每个 token，沿 $D$ 减均值、除以 $\sqrt{\sigma^2+\varepsilon}$，再乘 $\gamma$ 加
  $\beta$。统计量只来自这个 token 的特征，方差除以 $D$，训练和推理都不依赖 batch 统计。
tags:
  - 完整编程练习
  - Coding
  - LayerNorm
  - Normalization
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Layer Normalization
    url: 'https://arxiv.org/abs/1607.06450'
    type: primary
  - title: torch.nn.LayerNorm
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html'
    type: primary
---

## 题目描述

实现一个可训练的 LayerNorm 模块。给定最后一维大小 dim，对任意前置 batch / 序列维度的浮点 tensor 逐行 normalization，再执行可学习的缩放与平移；输入输出形状相同。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `LayerNorm(dim, eps=1e-5)`：`nn.Module`，可训练参数 `gamma`（初始化为 1）和 `beta`（初始化为 0），形状都是 `[dim]`。
- `forward(x)`：只在最后一维上做 standardization，方差用总体方差（`unbiased=False`，除以 $D$）。内部先升到 float32 计算，输出再转回输入的 dtype。
- 要求 `dim >= 1`、`eps > 0`。

- 对最后一维 D 个元素，输出定义为 `(x-mean(x))/sqrt(mean((x-mean(x))^2)+eps)*gamma+beta`，`gamma` 和 `beta` 对前置维度广播。
### 示例

```text
LayerNorm(dim=2, eps=1e-5)，gamma=[1,1]，beta=[0,0]
输入 [[1,3]] -> 输出约 [[-0.999995,0.999995]]
LayerNorm(dim=1)，beta=[2]，输入 [[7]] -> 输出 [[2]]
```

## 解题思路与参考答案

LayerNorm 对每个 token 的最后一维做 standardization，再应用可学习的仿射变换。归约只看它自己的 $D$ 个特征，batch 和时间维的数据不会混进来。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，只在 CPU 浮点 tensor 上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `LayerNorm(dim, eps=1e-5)`：`nn.Module`，可训练参数 `gamma`（初始化为 1）和 `beta`（初始化为 0），形状都是 `[dim]`。
- `forward(x)`：只在最后一维上做 standardization，方差用总体方差（`unbiased=False`，除以 $D$）。内部先升到 float32 计算，输出再转回输入的 dtype。
- 要求 `dim >= 1`、`eps > 0`，否则抛 `ValueError`。

### 输入输出示例

```text
x = [1, 3], gamma = [1, 1], beta = [0, 0], eps -> 0  ->  [-1, 1]
# 均值 2，总体方差 1
D = 1 时，任意输入  ->  beta
# 唯一的元素减去均值后是 0，输出只剩 beta
```

### 解题思路与正确性

方差必须用总体方差。用无偏方差（除以 $D-1$）时，$D=1$ 会除以 0 得到 NaN；用总体方差时方差是 0，加上 $\varepsilon$ 后有限，输出就是 $\beta$。

正确性靠和 `F.layer_norm` 对照：forward 输出和对输入的 gradient 都要一致。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F
from torch import nn


class LayerNorm(nn.Module):
    """沿最后一维做 LayerNorm：总体方差，float32 计算，输出转回输入 dtype。"""

    def __init__(self, dim, eps=1e-5):
        super().__init__()
        if dim < 1:
            raise ValueError(f"dim must be >= 1, got {dim}")
        if not eps > 0:
            raise ValueError(f"eps must be positive, got {eps}")
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))

    def forward(self, x):
        # x: [..., D]，例如 [B, T, D]；只在最后一维 D 上归约
        x32 = x.float()
        mean = x32.mean(dim=-1, keepdim=True)
        var = x32.var(dim=-1, keepdim=True, unbiased=False)  # 总体方差，除以 D
        normalized = (x32 - mean) * torch.rsqrt(var + self.eps)
        return (self.gamma * normalized + self.beta).to(x.dtype)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(output, reference, atol=1e-6)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 前向与 F.layer_norm 一致
layer = LayerNorm(4)
x = torch.randn(2, 3, 4, requires_grad=True)
output = layer(x)
reference = F.layer_norm(x, (4,), layer.gamma, layer.beta, layer.eps)
assert torch.allclose(output, reference, atol=1e-6)

# 对输入的梯度也一致
(grad_ours,) = torch.autograd.grad(output.square().sum(), x)
(grad_reference,) = torch.autograd.grad(reference.square().sum(), x)
assert torch.allclose(grad_ours, grad_reference, atol=1e-5)

# 题面示例：[1, 3] standardization 成 [-1, 1]
tiny_eps = LayerNorm(2, eps=1e-12)
assert torch.allclose(tiny_eps(torch.tensor([[1.0, 3.0]])), torch.tensor([[-1.0, 1.0]]))

# D = 1：输出有限，且等于 beta
single = LayerNorm(1)
with torch.no_grad():
    single.beta.fill_(0.5)
single_output = single(torch.tensor([[2.0], [-7.0]]))
assert torch.isfinite(single_output).all()
assert torch.allclose(single_output, torch.full((2, 1), 0.5))

# 低精度输入：输出 dtype 和输入一致
half_input = torch.randn(3, 4).to(torch.bfloat16)
assert LayerNorm(4)(half_input).dtype == torch.bfloat16

# 全零向量靠 eps 不会除零
assert torch.equal(LayerNorm(3)(torch.zeros(1, 3)), torch.zeros(1, 3))

# 非法参数
expect_value_error(lambda: LayerNorm(0))
expect_value_error(lambda: LayerNorm(4, eps=0.0))
```

### 复杂度与追问

设 token 数为 N、特征维度为 D。时间 O(N·D)，输出空间 O(N·D)；float32 副本也是 O(N·D)。

- 追问「怎么确认实现是对的」：和 PyTorch 的 `F.layer_norm` 对照 forward 输出和 gradient，上面的测试就是这么做的。
- 追问「和 RMSNorm 的区别」：RMSNorm 不减均值、没有 $\beta$，只除以 $\sqrt{\mathrm{mean}(x^2)+\varepsilon}$，见 `coding-rmsnorm`。

## 题怎么来的

Ba et al. 2016 提出的 LayerNorm 是 Transformer 的默认组件。Apple 手写 MHA 的前后会让你接上 LN；OpenAI 的 debug 题会把 `eps` 写成 $0$，或者把归约轴写成时间维。要说清楚三件事：沿哪一维 normalization、和 BatchNorm 差在哪、仿射参数是什么形状。Llama 把 LN 换成了 RMSNorm，对照见 `coding-rmsnorm`。

## 公式：每个 token 沿 $D$ standardization

输入 $x$ 的形状是 `[B, T, D]`。对每个 $(b,t)$：

$$
\mu=\frac{1}{D}\sum_{i=1}^{D}x_i,\quad
\sigma^2=\frac{1}{D}\sum_{i=1}^{D}(x_i-\mu)^2,\quad
\hat x=\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}},\quad
y=\gamma\odot\hat x+\beta.
$$

$\gamma,\beta\in\mathbb{R}^{D}$，沿 $D$ 广播，与 $T$ 无关。这就是「在 feature 维上的 standardization」：同一条样本、同一个位置上，自己的 $D$ 个通道被调到均值为 0、方差为 1。不同 token 之间互不影响，不同 batch 行之间也互不影响。所以在小 batch 下，或者逐 token 生成（decode）时每步 $T=1$，LN 的行为都不变，on-device 推理和训练是对齐的，Apple 爱听这一点。

BatchNorm 是沿 $B$（卷积网络里再加上空间维）为每个通道估计 $\mu,\sigma$，inference 时要用训练中累积的 running stats。LN 没有 running stats，训练和推理是同一份代码。

方差用有偏的 $1/D$（`unbiased=False`），和论文及 `nn.LayerNorm` 一致；用 $1/(D-1)$ 就和它们对不上了。归约放在 fp32 里做，因为低精度下平方和容易溢出或丢精度。

## $\varepsilon$ 和仿射不要省略

$\varepsilon$ 的典型值是 $10^{-5}$。输入是全零向量时 $\sigma=0$，没有 $\varepsilon$ 就会除零。$\varepsilon$ 太大，相当于没有 standardization；太小的话，在 fp16 里 `rsqrt` 仍可能得到 inf。

$\gamma,\beta$ 让模型能把「单位方差」再调回它需要的尺度和偏移。Pre-LN（LN 放在每个块的入口）比 Post-LN 训练更稳，GPT-2 之后成为默认做法；白板上先把 forward 写对，再说 LN 放在残差的哪个位置。如果把轴写成 `dim=1`（时间维），就变成在序列长度上做 standardization，padding 会把均值拉偏，必须再配 mask，那已经不是 LN 了。

## 追问

**和 BatchNorm 差在哪？**
BN 沿 batch 为每个通道估计统计量，推理依赖 running mean；LN 沿 feature 维计算，逐步 decode 时不需要改代码。
**$\gamma$ 怎么初始化？**
$\gamma$ 为 1，$\beta$ 为 0，训练开始时 $y\approx\hat x$。有人把 $\gamma$ 初始化得很小，给 Pre-LN 做热身，那是训练技巧，不是 LN 的定义。
**padding 要不要 mask？**
标准 LN 对 pad 位置也照常做 standardization，但这些位置的隐藏状态后面不会计入损失（loss），所以没关系。不要在 LN 里偷偷沿 $T$ 求均值。

## 相关题

- [[coding-rmsnorm]]：Llama 用的简化版，去掉减均值和 $\beta$，要说清少了什么、为什么不换回 LN。
- [[coding-qk-norm]]：同类 normalization 用在每个 head 的 $q,k$ 上而不是残差流，还要处理和 RoPE 的先后顺序。
