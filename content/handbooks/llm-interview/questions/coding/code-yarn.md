---
id: code-yarn
section: coding
order: 49
level: A
title: 手写 NTK-aware / YaRN：哪些频率内插、哪些外推
quick: "NTK-aware 只把 RoPE 基频改成 $\\theta'=\\theta\\cdot s^{d/(d-2)}$。YaRN 按波长分段处理：高频维不动（外推），低频维的 inv_freq 除以 $s$（内插），中间用 ramp 过渡。"
tags:
  - YaRN
  - RoPE
  - LongContext
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "YaRN: Efficient Context Window Extension of Large Language Models"
    url: https://arxiv.org/abs/2309.00071
    type: primary
---

## 题目描述

实现本卡用于演示长上下文位置频率缩放的一组纯张量函数。任务是按照给定的频率定义返回数值，不是复刻完整 YaRN 训练流程，也不以此保证长上下文模型质量。

### 接口与数值定义

- `ntk_base(base,scale,dh)`：返回 `base * scale ** (dh/(dh-2))`，base 与 scale 为正数，dh 为大于2的偶数。
- `yarn_ramp(dim_idx,dh,beta_fast=32,beta_slow=1)`：把 `dim_idx/dh` 从区间 `[1/beta_fast,1/beta_slow]` 线性映射到 `[0,1]`，区间外取最近端点。`beta_fast` 大于 `beta_slow` 且均为正。
- `yarn_inv_freq(dh,scale,base=10000)`：维度索引为 `0,2,...,dh-2`，未缩放频率为 `base ** (-dim_idx/dh)`；按上面默认 ramp 的值 r，将该频率除以 `scale ** r`，返回长度 dh/2 的张量。

输入均有限且合法。scale=1 时必须与未缩放频率相同。

### 示例

```text
ntk_base(10000,1,8) -> 10000
ntk_base(10000,2,4) -> 40000
yarn_inv_freq(dh=4,scale=1,base=10000) -> [1,0.01]
```

返回值形状和浮点容差均应正确，不要求加载任何模型权重。

## 解题思路与参考答案

两种方法改的都是 RoPE 的频率本身。NTK-aware 只改基频，$\theta'=\theta\cdot s^{d/(d-2)}$；YaRN 按波长分段，波长短的高频维保持不动做外推，波长长的低频维除以 $s$ 做内插，中间用 ramp 过渡。

对比的起点是线性插值（PI）：它把 `pos / s` 再查原表，高频维也被一起压缩，压得太狠，近距离 token 的相对位置就更难区分了。NTK / YaRN 改的是频率，位置照常。基础 RoPE 见 `code-rope`。

## 两种改法

NTK-aware 的公式短，先写这个：

$$
\theta'=\theta\cdot s^{d/(d-2)}.
$$

YaRN 对第 $i$ 个二维对（$i=0,2,\ldots,d-2$）算一个 ramp $r_i\in[0,1]$，波长短的 $r=0$（外推），波长长的 $r=1$（内插）：

$$
\omega_i'=\omega_i\big/ s^{r_i},\qquad \omega_i=\theta^{-2i/d}.
$$

论文用 $\beta_{\mathrm{fast}}=32$、$\beta_{\mathrm{slow}}=1$ 划界，另外还乘一个 attention 温度 $m_{\mathrm{scale}}$，手写时可以先不加。

```python
import torch


def ntk_base(base, scale, dh):
    return base * scale ** (dh / (dh - 2))


def yarn_ramp(dim_idx, dh, beta_fast=32.0, beta_slow=1.0):
    # 0=外推，1=内插
    inv_dim = dim_idx / dh
    lo, hi = 1.0 / beta_fast, 1.0 / beta_slow
    return ((inv_dim - lo) / (hi - lo)).clamp(0, 1)


def yarn_inv_freq(dh, scale, base=10000.0):
    dim_idx = torch.arange(0, dh, 2).float()
    inv = 1.0 / (base ** (dim_idx / dh))
    ramp = yarn_ramp(dim_idx, dh)
    return inv / (scale**ramp)
```

建表时 $\cos(t\omega')$ 仍按绝对位置 $t$ 算。KV cache 里的 $K$ 在写入时已经用当时的 $\omega'$ 转过了，换 scale 就等于换了位置编码，旧 cache 不能直接复用。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

scale=1 时频率应退化为普通 RoPE；scale=2 时频率不应放大。测试覆盖这里的简化频率公式，不代表已经验证完整 YaRN 的长上下文效果。

```python
base_freq = 1 / (10000.0 ** (torch.arange(0, 8, 2).float() / 8))
torch.testing.assert_close(yarn_inv_freq(8, 1), base_freq)
scaled = yarn_inv_freq(8, 2)
assert scaled.shape == (4,) and torch.isfinite(scaled).all()
assert (scaled > 0).all() and (scaled <= base_freq).all()
assert ntk_base(10000.0, 1, 8) == 10000.0
print("simple tests passed")
```

## 追问

**scale=1 时呢？**
退回原 RoPE。`s^r=1`，ramp 取多少都无所谓。

**和 ALiBi 比呢？**
ALiBi 不改 $Q,K$，外推靠相对距离 bias，见 `code-alibi`。YaRN 是 RoPE 模型的续训手段。

**只改 $\theta$ 算 YaRN 吗？**
不算，那是 NTK-aware。YaRN 多了分段 ramp 和 $m_{\mathrm{scale}}$。
