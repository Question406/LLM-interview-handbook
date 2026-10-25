---
id: code-swiglu
section: coding
order: 218
level: A
title: 手写 SwiGLU 前向（含形状与 $d_{\mathrm{ff}}\approx 8d/3$）
quick: >-
  SwiGLU 是 $(\mathrm{SiLU}(xW_1)\odot xW_2)W_3$，$W_1,W_2:d\to d_{\mathrm{ff}}$，$W_3:d_{\mathrm{ff}}\to d$。三个矩阵要和旧 FFN 的 $2d\cdot 4d=8d^2$ 对齐，所以 $d_{\mathrm{ff}}\approx 8d/3$。门控那一路别漏，中间维也别还写成 $4d$。
tags:
  - SwiGLU
  - FFN
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: GLU Variants Improve Transformer
    url: https://arxiv.org/abs/2002.05202
    type: primary
---

## 题目描述

实现不带 bias 的 SwiGLU 前馈模块，把最后一维 d 的输入映射到中间宽度 `d_ff`，再返回 d 维输出。该模块应支持任意前导 batch 或序列维。

### 接口与语义

`SwiGLU(d,d_ff=None)` 包含三份可学习线性权重：w1、w2 为 `d -> d_ff`，w3 为 `d_ff -> d`。输出定义为 `w3(SiLU(w1(x)) * w2(x))`，乘号是逐元素乘法，不能把两支输入相加或互换激活位置。

`forward(x)` 输入形状 `[...,d]`，输出形状相同。若 `d_ff` 未给出，本卡约定把 `8*d/3` 向下取整并向下对齐到128的倍数；输入保证得到正宽度。小尺寸测例显式传入正整数 `d_ff`。不需要 dropout、残差或 LayerNorm。

### 示例

```text
layer=SwiGLU(d=4,d_ff=8)，x为[2,3,4]形状的全1张量
输出形状 -> [2,3,4]
若把w1权重置为0，输出 -> 同形状全零张量
```

需要保留 PyTorch 参数与 autograd 行为。

## 解题思路与参考答案

SwiGLU 前向就是三次投影：gate 过 SiLU，和 up 逐元素相乘，再 down 回 $d$。中间维取 $8d/3$ 左右，是为了让三矩阵的参数和 FLOPs 跟旧的 $4d$ 两矩阵 FFN 持平。这题要能写前向、报形状，并推出为什么中间维不是 $4d$。

常见写错有两个方向：写成两矩阵的 GELU FFN，门控没了；或者三矩阵还用 $4d$，层白白贵了 1.5 倍。架构直觉见 `arch-swiglu`，美团口述见 `meituan-swiglu`。

## 公式与形状

$$
\mathrm{SiLU}(z)=z\cdot\sigma(z),\qquad
\mathrm{SwiGLU}(x)=\bigl(\mathrm{SiLU}(xW_1)\odot xW_2\bigr)W_3.
$$

$x$ 是 $[\ldots,d]$。$W_1,W_2\in\mathbb{R}^{d\times d_{\mathrm{ff}}}$ 分别是 gate 和 up，$W_3\in\mathbb{R}^{d_{\mathrm{ff}}\times d}$ 是 down，中间激活是 $[\ldots,d_{\mathrm{ff}}]$，输出回到 $[\ldots,d]$。GLU 家族只换门上的非线性：sigmoid / SiLU / GELU 分别对应 GLU / SwiGLU / GeGLU，结构都是「门 $\odot$ 值」。

实现上常把 $W_1,W_2$ 合成一块 $[d,2d_{\mathrm{ff}}]$，一次 GEMM 再 chunk，数值和两次独立投影一致，只要别 `cat` 完在错误的维上切开。偏置可有可无，LLaMA / Qwen 系通常不带 bias。

## 为什么 $d_{\mathrm{ff}}\approx 8d/3$

旧的两矩阵 FFN（ReLU / GELU）中间维常取 $4d$，参数和主导 FLOPs 大约是

$$
2\cdot d\cdot 4d=8d^{2}.
$$

SwiGLU 有三块投影，同样中间维时约 $3d\,d_{\mathrm{ff}}$。要和原来的 $8d^{2}$ 对齐：

$$
3d\cdot d_{\mathrm{ff}}=8d^{2}\implies d_{\mathrm{ff}}=\frac{8}{3}d.
$$

实际还要按 128 / 256 对齐 Tensor Core，所以代码里看到的是「约 $8d/3$」，没有精确的分数。要是还用 $4d$，参数和 FLOPs 约为旧 FFN 的 $3/2$，等于无端多加 50% 的 FFN 算力，这时再说「SwiGLU 更强」就不是公平对比了。PaLM / LLaMA 把这一条写进了默认宽度，我会从 $8d^{2}$ 推回来。

现场给个数：$d=4096$ 时 $8d/3\approx 10923$，对齐 128 后常见的是 11008，LLaMA-7B 就是这个宽度。参数约 $3\times 4096\times 11008$，别再乘一个 $4d$。激活显存会多一份 $[\ldots,d_{\mathrm{ff}}]$ 的门控张量，这是三路投影比两路 FFN 多付的带宽。

至于门控好在哪：通道可以关也可以放，SiLU 在负半轴还有梯度。没有定理保证它处处优于 GELU，这是算力对齐之后的经验选择。MoE 专家内部也可以是同一套 SwiGLU，宽度公式按单个专家的 $d_{\mathrm{ff}}$ 算。

## 手写

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SwiGLU(nn.Module):
    def __init__(self, d, d_ff=None):
        super().__init__()
        if d_ff is None:
            d_ff = int(8 * d / 3)
            d_ff -= d_ff % 128
        self.w1 = nn.Linear(d, d_ff, bias=False)  # gate
        self.w2 = nn.Linear(d, d_ff, bias=False)  # up
        self.w3 = nn.Linear(d_ff, d, bias=False)  # down

    def forward(self, x):
        # x: [..., d] -> [..., d]
        return self.w3(F.silu(self.w1(x)) * self.w2(x))
```

`F.silu` 就是 $z\sigma(z)$，别先 sigmoid 再乘错张量。形状上断言 `x.shape[-1]==d`，中间是 `d_ff`，输出和 `x` 最后一维相同。fused 写法是 `gate, up = self.w_gup(x).chunk(2, dim=-1)`，再 `self.w3(F.silu(gate)*up)`。

现场最容易写错的几处：两路都做了 SiLU，其实值通路应该是线性的；先 down 再门控，形状对不上，也就不是 GLU 了；`chunk` 切在了 batch 维，应该切最后一维。残差在层外加，$x+\mathrm{SwiGLU}(\mathrm{Norm}(x))$，别写进这个模块把形状改掉。Pre-Norm 时先 RMSNorm 再进三路投影，学习率才稳；手写时也别把 Norm 融进 `SwiGLU` 类里，否则和注意力支路的 Norm 对不齐。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

显式给一个小的中间维度。先检查输出形状，再把 gate 投影清零，此时 silu(0)=0，输出也应归零。

```python
layer = SwiGLU(4, d_ff=8)
x = torch.ones(2, 3, 4)
assert layer(x).shape == x.shape
with torch.no_grad():
    layer.w1.weight.zero_()
torch.testing.assert_close(layer(x), torch.zeros_like(x))
print("simple tests passed")
```

## 追问

**$W_1$ 和 $W_2$ 能不能共享？**
能写成单路，但那就不是 GLU 了。门和值必须是两路。

**和 ReLU FFN 的代码差在哪？**
差在多一次线性投影再逐元素相乘。漏了这次乘法，门控就丢了。

**TP 怎么切？**
gate / up 列切，SiLU 和乘法在分片上做，down 行切再 reduce，见 `infra-megatron-mlp-tp`。手写本题用完整的 $d$ 就行。

**$d_{\mathrm{ff}}$ 为什么还要 `% 128`？**
Tensor Core 喜欢 64/128 对齐。公式给的是目标 FLOPs，代码里的整数宽度可以略偏，别为了「整除 $3$」硬用没对齐的 10922。

**和 GeGLU 的代码差什么？**
把 `F.silu` 换成 GELU，三个矩阵不变。面试先写结构，再换非线性。
