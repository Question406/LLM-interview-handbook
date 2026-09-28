---
id: code-swiglu
section: coding
order: 218
level: A
title: 手写 SwiGLU 前向（含形状与 $d_{\mathrm{ff}}\approx 8d/3$）
quick: >-
  $(\mathrm{SiLU}(xW_1)\odot xW_2)W_3$。$W_1,W_2:d\to d_{\mathrm{ff}}$，$W_3:d_{\mathrm{ff}}\to d$。三矩阵要对齐旧
  FFN 的 $2d\cdot 4d=8d^2$，故 $d_{\mathrm{ff}}\approx 8d/3$。别漏门控那一路，也别把中间维仍写成 $4d$。
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

架构直觉见 `arch-swiglu`、美团口述见 `meituan-swiglu`。本题要能写前向、报形状、并推出为什么中间维不是 $4d$。错法：写成两矩阵 GELU FFN，或三矩阵仍用 $4d$ 把层做贵 1.5 倍。

## 公式与形状

$$
\mathrm{SiLU}(z)=z\cdot\sigma(z),\qquad
\mathrm{SwiGLU}(x)=\bigl(\mathrm{SiLU}(xW_1)\odot xW_2\bigr)W_3.
$$

$x$ 为 $[\ldots,d]$。$W_1,W_2\in\mathbb{R}^{d\times d_{\mathrm{ff}}}$ 是 gate 与 up，$W_3\in\mathbb{R}^{d_{\mathrm{ff}}\times d}$ 是 down。中间激活 $[\ldots,d_{\mathrm{ff}}]$，输出回到 $[\ldots,d]$。GLU 家族只换门的非线性：sigmoid / SiLU / GELU 分别对应 GLU / SwiGLU / GeGLU，结构都是「门 $\odot$ 值」。

实现上常把 $W_1,W_2$ 合成一块 $[d,2d_{\mathrm{ff}}]$ 一次 GEMM 再 chunk，数值应与两次独立投影一致。不要 `cat` 完在错误维上切开。偏置可有可无，LLaMA / Qwen 系通常无 bias。

## 为什么 $d_{\mathrm{ff}}\approx 8d/3$

旧两矩阵 FFN（ReLU / GELU）中间维常取 $4d$，参数与主导 FLOPs 约

$$
2\cdot d\cdot 4d=8d^{2}.
$$

SwiGLU 三块投影，同样中间维时约 $3d\,d_{\mathrm{ff}}$。要对齐原来的 $8d^{2}$：

$$
3d\cdot d_{\mathrm{ff}}=8d^{2}\implies d_{\mathrm{ff}}=\frac{8}{3}d.
$$

再按 128 / 256 对齐 Tensor Core，所以代码里看到的是「约 $8d/3$」不是精确分数。若仍用 $4d$，参数和 FLOPs 约为旧 FFN 的 $3/2$，层明显更贵；这不是「SwiGLU 更强」的公平对比。PaLM / LLaMA 把这一条写进默认宽度，我会从 $8d^{2}$ 推回来。

门控的好处是通道可关可放，SiLU 在负半轴仍有梯度。没有定理保证处处优于 GELU；是对齐算力之后的经验选择。MoE 专家内部仍可以是同一套 SwiGLU，宽度公式按单个专家的 $d_{\mathrm{ff}}$ 算。

现场给个数：$d=4096$ 时 $8d/3\approx 10923$，对齐 128 后常见 11008（LLaMA-7B 就是这个宽度）。参数约 $3\times 4096\times 11008$，不要再乘一个 $4d$。激活显存会多一份 $[\ldots,d_{\mathrm{ff}}]$ 的门控张量，这是三路投影相对两路 FFN 多付的带宽。

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

`F.silu` 就是 $z\sigma(z)$，不要先 sigmoid 再乘错张量。形状断言：`x.shape[-1]==d`，中间 `d_ff`，输出与 `x` 最后一维相同。fused 写法：`gate, up = self.w_gup(x).chunk(2, dim=-1)` 再 `self.w3(F.silu(gate)*up)`。

常见写错：对两路都做 SiLU（值通路应是线性）；先 down 再门控（形状对不上，也不是 GLU）；`chunk` 切在 batch 维而不是最后一维。残差在层外加，$x+\mathrm{SwiGLU}(\mathrm{Norm}(x))$，不要写进本模块里把形状改掉。Pre-Norm 时先 RMSNorm 再进三路投影，学习率才稳；手写不要把 Norm 融进 `SwiGLU` 类里，否则和注意力支路的 Norm 对不齐。

## 追问

- **为什么不是 $4d$？** 三矩阵要对齐两矩阵 $\times 4d$ 的 $8d^{2}$。保持 $4d$ 等于无端加 50% FFN 算力。
- **$W_1$ 和 $W_2$ 能否共享？** 能写成单路，那就不是 GLU。门与值必须两路。
- **和 ReLU FFN 的代码差一行？** 差在多一次线性再逐元乘。漏乘就把门控丢掉。
- **TP 怎么切？** gate / up 列切，SiLU 与乘在分片上做，down 行切再 reduce，见 `infra-megatron-mlp-tp`；手写本题用完整 $d$ 即可。
- **$d_{\mathrm{ff}}$ 为什么还要 `% 128`？** Tensor Core 喜欢 64/128 对齐。公式给的是目标 FLOPs，代码里的整数宽度可以略偏，不要为了「整除 $3$」硬用未对齐的 10922。
- **和 GeGLU 代码差什么？** 把 `F.silu` 换成 GELU，其余三矩阵不变。面试先写结构，再换非线性。
