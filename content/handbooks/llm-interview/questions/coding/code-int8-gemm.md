---
id: code-int8-gemm
section: coding
order: 57
level: A
title: 手写对称 INT8 量化：scale、饱和，以及 dequant GEMM 的形状
quick: >-
  对称量化 $q=\mathrm{round}(w/s).\mathrm{clamp}(-127,127)$，$s=\|w\|_\infty/127$。反量化
  $\hat w=q\cdot s$。GEMM 写成 $(x q^\top)\cdot s$，把 scale 留在外层，不要先把 $q$ 扩成 fp16 再乘。per-tensor
  一个 $s$；per-channel 是 $[V]$ 或 $[K]$ 向量，沿输出通道广播。
tags:
  - Quantization
  - INT8
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: LLM.int8()
    url: https://arxiv.org/abs/2208.07339
    type: primary
---

白板先写对称、零点为 0 的版本。非对称多一个 zp，公式更长。LLM.int8 还要处理 outlier 通道走 fp16，本题把 scale 和 GEMM 形状写对即可。

## 量化

$q_{\max}=2^{b-1}-1$，INT8 是 127（注意不是 128，+128 存不进 signed 8-bit 的正半轴）。

$$
s=\frac{\max|w|}{q_{\max}},\qquad
q=\mathrm{clip}\big(\mathrm{round}(w/s),\,-q_{\max},\,q_{\max}\big).
$$

```python
import torch

def quant_symm(w, bits=8):
    qmax = 2 ** (bits - 1) - 1
    scale = w.abs().amax() / qmax
    q = (w / scale).round().clamp(-qmax, qmax)
    return q.to(torch.int8), scale

def int8_gemm(x, q, scale):
    # x: [B,K], q: [N,K] int8, scale 标量或 [N]
    return (x @ q.to(x.dtype).T) * scale
```

反量化误差最多半个 bin：$|w-\hat w|\le s/2$。per-channel：`scale = w.abs().amax(dim=1) / qmax`，形状 `[N]`，乘在 GEMM 的输出维上。SmoothQuant 先把激活的 outlier 折进权重再量化，手写提一句。

## 追问

- **为什么不用 128？** signed int8 是 $[-128,127]$。对称且要 `round` 到可表示的正最大值，常用 127，让 $0$ 对齐。
- **激活也量化？** W8A8 还要给 $x$ 一个 scale，整数 GEMM 之后乘 $s_x s_w$。outlier 通道 LLM.int8 会拆出来走 fp16。
- **和 QLoRA？** NF4 是 4bit 分位数码本，不是均匀 INT。手写 INT8 不要说成 NF4。
