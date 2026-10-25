---
id: code-int8-gemm
section: coding
order: 57
level: A
title: 手写对称 INT8 量化：scale、饱和，以及 dequant GEMM 的形状
quick: "对称量化是 $q=\\mathrm{round}(w/s).\\mathrm{clamp}(-127,127)$，$s=\\|w\\|_\\infty/127$，反量化 $\\hat w=q\\cdot s$。GEMM 写成 $(x q^\\top)\\cdot s$，scale 留在外层乘，不用先把 $q$ 扩成 fp16 再乘。per-tensor 只有一个 $s$；per-channel 的 $s$ 是 $[V]$ 或 $[K]$ 向量，沿输出通道广播。"
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

## 题目描述

实现权重的对称低位量化，以及用该量化权重做矩阵乘法的浮点参考结果。本题不要求真正的整数 GEMM 内核。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `quant_symm(w,bits=8)` 与 `int8_gemm(x,q,scale)`。w 为非全零浮点权重 [N,K]，bits 在2到8之间；x 为 [B,K]，q 为 [N,K] int8，scale 为标量或长度N的每输出通道缩放。

### 输出与约束

量化接口以 `qmax=2^(bits-1)-1`，scale=max(abs(w))/qmax，使用 `torch.round` 舍入（恰好半整数时取最近的偶数），再限制在 [-qmax,qmax] 的 int8 q 及 scale。乘法接口返回 [B,N]，数值为 (x@q.T)*scale，输出浮点张量。

### 示例

```text
w=[[-1,0,1]], bits=8 -> q=[[-127,0,127]], scale=1/127
x为3×3单位矩阵时，int8_gemm(x,q,scale) -> [[-1],[0],[1]]
```

## 解题思路与参考答案

对称 INT8 量化就是用权重的最大绝对值定一个 scale：$s=\max|w|/127$，$q=\mathrm{round}(w/s)$ 再截到 $[-127,127]$，反量化时乘回 $s$。做 GEMM 时先用整数权重和输入相乘，scale 留到最后在输出上乘一次。白板先写零点为 0 的对称版本；非对称多一个 zp，公式长一些。LLM.int8 还会把 outlier 通道拆出来走 fp16，这题把 scale 和 GEMM 的形状写对就够了。

比如一个权重矩阵里绝对值最大的那个数正好映射到 127，其余的按比例落在 $-127$ 到 $127$ 之间，比 $s/2$ 还小的权重会被 round 成 0。

## 量化

$q_{\max}=2^{b-1}-1$，INT8 时是 127。用 128 的话，+128 存不进 signed 8-bit 的正半轴。

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

反量化的误差最多半个 bin：$|w-\hat w|\le s/2$。per-channel 的写法是 `scale = w.abs().amax(dim=1) / qmax`，形状 `[N]`，乘在 GEMM 的输出维上。SmoothQuant 会先把激活的 outlier 折进权重再量化，手写时提一句。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用可精确表示的 [-1,0,1] 检查量化端点，再用单位矩阵做 GEMM，结果应还原权重的转置。这里避免全零权重，因为原片段尚未处理 scale=0 的分支。

```python
w = torch.tensor([[-1., 0., 1.]])
q, scale = quant_symm(w)
assert q.dtype == torch.int8 and q.tolist() == [[-127, 0, 127]]
torch.testing.assert_close(q.float() * scale, w)
torch.testing.assert_close(int8_gemm(torch.eye(3), q, scale), w.T)
print("simple tests passed")
```

## 追问

**为什么用 127，不用 128？**
signed int8 的范围是 $[-128,127]$。对称量化要 `round` 到能表示的最大正数，所以常用 127，这样 $0$ 正好对齐。

**激活也要量化吗？**
W8A8 要。还得给 $x$ 一个 scale，整数 GEMM 之后乘 $s_x s_w$。LLM.int8 会把 outlier 通道拆出来走 fp16。

**和 QLoRA 是一回事吗？**
不是。QLoRA 的 NF4 是 4bit 的分位数码本，不是均匀的 INT。手写 INT8 别说成 NF4。
