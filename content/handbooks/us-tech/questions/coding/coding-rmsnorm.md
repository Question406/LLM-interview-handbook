---
id: coding-rmsnorm
section: coding
order: 5
level: A
title: 白板：RMSNorm 比 LayerNorm 少了什么，Llama 为什么用
quick: >-
  RMSNorm 沿最后一维把 $x$ 除以 $\mathrm{RMS}(x)$，再乘 $\gamma$，省掉 LayerNorm 的减均值，通常也没有
  $\beta$。Llama 选择它是为了减少约简和读写开销，同时保持接近 LN 的质量；两者在输入均值非零时结果不同。
tags:
  - 完整编程练习
  - Coding
  - RMSNorm
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Root Mean Square Layer Normalization
    url: 'https://arxiv.org/abs/1910.07467'
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: 'https://arxiv.org/abs/2307.09288'
    type: primary
  - title: torch.nn.RMSNorm
    url: 'https://pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html'
    type: primary
---

## 题目描述

实现一个 PyTorch RMSNorm 层，并提供与不带仿射参数的 LayerNorm 对照接口。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `RMSNorm(dim, eps=1e-6)`：`nn.Module`，可训练参数 `weight` 形状 `[dim]`，初始化为 1。`forward(x)` 输入 `x` 为 `[..., dim]` 浮点张量，返回同形张量 `x / sqrt(mean(x², last_dim) + eps) * weight`。
- 内部用 float32 计算，输出 dtype 与输入相同。
- `vs_layernorm(x, eps=1e-6) -> (ln, rms)`：对照用，返回不带仿射参数的 LayerNorm 和 RMSNorm 结果。
- `eps > 0`。

### 输入输出示例

```text
x = [3, 4]
RMS = sqrt((9 + 16) / 2 + eps) = sqrt(12.5 + eps) ≈ 3.536
RMSNorm(x) ≈ [0.849, 1.131]                     # 均值没被减掉
LayerNorm(x) = [-1, 1]（无仿射）                 # 先减均值 3.5
```

## 解题思路与参考答案

我会沿最后一维求平方均值，加 eps 后取倒数平方根，乘回输入，再乘可训练的 weight。这样保留了输入的均值方向；例如 [3, 4] 经 RMSNorm 后仍全为正，而 LayerNorm 会先减去 3.5。统计量在 float32 里算，最后把结果转回输入 dtype。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `RMSNorm(dim, eps=1e-6)`：`nn.Module`，可训练参数 `weight` 形状 `[dim]`，初始化为 1。`forward(x)` 沿最后一维用平方均值 normalization，不减均值，再乘 `weight`。
- 内部用 float32 计算，输出 dtype 与输入相同。
- `vs_layernorm(x, eps=1e-6) -> (ln, rms)`：对照用，返回不带仿射参数的 LayerNorm 和 RMSNorm 结果。
- `eps > 0`，否则抛 `ValueError`。

### 输入输出示例

```text
x = [3, 4]
RMS = sqrt((9 + 16) / 2 + eps) = sqrt(12.5 + eps) ≈ 3.536
RMSNorm(x) ≈ [0.849, 1.131]                     # 均值没被减掉
LayerNorm(x) = [-1, 1]（无仿射）                 # 先减均值 3.5
```

### 解题思路与正确性

RMSNorm 只除以均方根，不减均值，所以输入的均值方向保留在输出里。零向量的平方均值是 0，靠 `eps` 让 `rsqrt` 有限，输出仍是 0。

先把 `x` 升到 float32，乘完 `weight` 后再转回输入的 dtype。如果最后不转回去，float32 的 `weight` 会把 fp16 / bf16 的输出悄悄升精度，后面的层拿到的 dtype 就变了。

### 完整参考实现（Python 3）

```python
import torch
from torch import nn


class RMSNorm(nn.Module):
    """沿最后一维的 RMSNorm：y = weight * x / sqrt(mean(x^2) + eps)，不减均值、没有 bias。"""

    def __init__(self, dim, eps=1e-6):
        super().__init__()
        if not eps > 0:
            raise ValueError(f"eps must be positive, got {eps}")
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        # x: [..., D]；在 float32 里算统计量，输出转回输入 dtype
        x32 = x.float()
        inv_rms = torch.rsqrt(x32.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return (x32 * inv_rms * self.weight).to(x.dtype)


def vs_layernorm(x, eps=1e-6):
    """返回 (无仿射 LayerNorm, 无仿射 RMSNorm)，用来对比两者差在减均值。"""
    mean = x.mean(-1, keepdim=True)
    layer_norm = (x - mean) * torch.rsqrt(x.var(-1, keepdim=True, unbiased=False) + eps)
    rms_norm = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps)
    return layer_norm, rms_norm
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(y, reference)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
torch.manual_seed(0)

# 与公式一致，并且能 backpropagation
norm = RMSNorm(4)
x = torch.randn(2, 3, 4, requires_grad=True)
y = norm(x)
reference = x * torch.rsqrt(x.square().mean(-1, keepdim=True) + norm.eps) * norm.weight
assert torch.allclose(y, reference)
y.sum().backward()
assert torch.isfinite(x.grad).all()

# 例子 [3, 4]：分母是 sqrt(12.5 + eps)
assert torch.allclose(
    RMSNorm(2)(torch.tensor([3.0, 4.0])),
    torch.tensor([3.0, 4.0]) / 12.5**0.5,
    atol=1e-5,
)

# 零向量：eps 保护，输出仍是 0
assert torch.all(norm(torch.zeros(2, 4)) == 0)

# 输出 dtype 跟随输入
assert norm(torch.ones(2, 4, dtype=torch.float16)).dtype == torch.float16

# 与 LayerNorm 的区别：均值非零时结果不同，均值为 0 时相同
layer_norm, rms_norm = vs_layernorm(torch.tensor([[3.0, 4.0]]))
assert torch.allclose(layer_norm, torch.tensor([[-1.0, 1.0]]), atol=1e-4)
assert not torch.allclose(layer_norm, rms_norm)
layer_norm, rms_norm = vs_layernorm(torch.tensor([[-2.0, 2.0]]))
assert torch.allclose(layer_norm, rms_norm)

# eps 必须为正
try:
    RMSNorm(4, eps=0)
except ValueError:
    pass
else:
    raise AssertionError("eps=0 accepted")
```

### 复杂度与追问

设共有 N 行（所有前导维相乘）、每行 D 个特征。时间和输出空间都是 O(ND)，每行的统计量只占 O(N)。

- 追问「比 LayerNorm 省在哪」：少一次求均值的 reduction 和一次减均值的读写，也少一套 $\beta$。对带宽敏感的 decode 有点帮助，但不是显存的大头。

## 题怎么来的

Zhang & Sennrich 2019 提出了 RMSNorm；LLaMA、Llama 2、Llama 3 的公开实现都用它，不用 LayerNorm。Meta GenAI 岗会让你对照着写出两者，并说清「少了什么」和「为什么不改回去」。LN 的完整形式见 `coding-layernorm`。Apple 端侧也会问：少一次 mean reduction 对 kernel 意味着什么。

## 少了 centering，通常也没有 $\beta$

LayerNorm 先减均值 $\mu$，再除以 $\sqrt{\sigma^2+\varepsilon}$，最后乘 $\gamma$、加 $\beta$。RMSNorm 是

$$
\mathrm{RMS}(x)=\sqrt{\frac{1}{D}\sum_{i=1}^{D}x_i^2+\varepsilon},\qquad
y=\gamma\odot\frac{x}{\mathrm{RMS}(x)}.
$$

没有 $\mu$，所以不会把均值拉到 0，均值那个分量保留在残差流里。论文的论证是：LN 里真正起作用的主要是缩放，centering 可以省掉。Llama 保留了 $\gamma$，没有 bias $\beta$。输入仍是 `[B, T, D]`，只沿 $D$ 做 reduction。

Llama 里 `eps` 常见 $10^{-5}$ 或 $10^{-6}$。norm 要在 fp32 里算，因为平方均值在 bf16 下容易累积误差。`nn.RMSNorm` 在较新的 PyTorch 里已经进了核心库，但白板上仍要能手写。

## Llama 为什么换

公开的理由是少一次求均值、少一套 $\beta$，kernel 更简单，而在 7B 到 70B 上质量没有下降。RMSNorm 和 LN 在一般输入上仍会给出不同结果。GQA、RoPE、SwiGLU 和 RMSNorm 是同一套 Llama 积木，RMSNorm 是其中最便宜的一块，见 `meta-llama-gqa`。不要回答「RMSNorm 一定更准」。

Llama 用 pre-norm：每个 attention / FFN 子层的入口做 RMSNorm，残差在子层外面加。统计量只沿 $D$ 算，所以 decode 时 $T=1$ 和训练时 $T$ 很长得到的结果一致，逐步生成不会漂移。NVIDIA 会追问 kernel：RMSNorm 是一次 reduction 加一次 rsqrt，比 LN 少一次减均值的读写，对带宽敏感的逐 token 生成（decode）有点用，但不是主要的显存开销。

## 追问

**把均值再减掉还叫 RMSNorm 吗？**
不叫，那是去掉 $\beta$ 的 LN 变体。Llama 明确不减均值。
**$\gamma$ 能去掉吗？**
能跑，但失去了按通道恢复尺度的自由度。公开 checkpoint 都保留了 `weight`。
**和 BatchNorm、或者沿 $T$ standardization 是一回事吗？**
都不是，轴始终是特征维 $D$。沿 $T$ standardization 会让 padding 污染统计量，逐步 decode 时也和训练对不上。

## 相关题

- [[coding-layernorm]]：完整的 LayerNorm，减均值、除标准差再加 $\gamma,\beta$，适合和本题对照着写。
- [[coding-qk-norm]]：同样是 RMSNorm，但作用在每个 head 的 $q,k$ 上，要先 norm 再 RoPE，GQA 时 $k$ 用自己的 `k_norm`。
