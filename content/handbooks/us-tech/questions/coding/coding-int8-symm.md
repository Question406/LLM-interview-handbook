---
id: coding-int8-symm
section: coding
order: 32
level: A
title: 白板：对称 INT8 量化，scale、饱和，以及 dequant GEMM 的形状
quick: >-
  先取 $s=\max|x|/127$，再按 $q=\mathrm{clip}(\mathrm{round}(x/s),-127,127)$ 映射到
  INT8，零点为 $0$。GEMM 用 int32 累加，再按输出的行、列乘激活和权重 scale，全零块要给 scale 正下限。
tags:
  - 完整编程练习
  - Coding
  - INT8
  - Quantization
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: LLM.int8() — 8-bit Matrix Multiplication for Transformers at Scale
    url: 'https://arxiv.org/abs/2208.07339'
    type: primary
  - title: bitsandbytes
    url: 'https://github.com/bitsandbytes-foundation/bitsandbytes'
    type: primary
  - title: TensorRT — Working with Quantized Types
    url: >-
      https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-with-quantized-types.html
    type: secondary
---

## 题目描述

实现对称 INT8 量化、反量化误差检查和带 scale 的整数线性层，支持整个张量共用 scale 或按指定维度量化。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `symm_quant_int8(x, dim=None) -> (q, scale)`：对称量化到 int8，范围 $[-127, 127]$。`scale = max|x| / 127`，并设一个正下限，避免全 0 输入除以 0。`dim=None` 时整个张量共用一个标量 scale；给定 `dim` 时沿该轴取最大值，scale 保留该维（`keepdim=True`）。
- `int8_linear(xq, wq, sx, sw) -> y`：`xq` 是 `[M, K]` int8，`wq` 是 `[N, K]` int8，先升到 int32 做 $X W^\top$ 得到 `[M, N]`，再乘 scale。`sx` 是标量或 `[M, 1]`（per-token），`sw` 是标量、`[N]` 或 `[N, 1]`（per-output-channel）。
- `roundtrip_err(x, dim=None)`：量化再反量化后的最大绝对误差，用于检查。
- scale 下限固定为 1e-12；q 是 round(x/scale) 后截断到 [-127,127] 的 int8，round 使用 PyTorch 的 ties-to-even。反量化为 q*scale。所有输入有限，指定 dim 为合法轴，`int8_linear` 输出 float32。

### 输入输出示例

```text
symm_quant_int8([-1,0,1]) -> ([-127,0,127], 1/127)
roundtrip_err([-1,0,1]) -> 0
int8_linear([[1,2]], [[3,4]], sx=0.5, sw=0.25) -> [[1.375]]
```

## 解题思路与参考答案

对称 INT8 量化先确定 scale，再把 $x/s$ 四舍五入、裁到 $[-127, 127]$，最后转成 int8。scale 取 $\max|x|/127$，所以绝对值最大的元素正好落在 ±127，其余元素的取整误差不超过半格，即 $s/2$。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，只在 CPU 上验证数值；没有用到硬件 INT8 GEMM，也没有验证性能。

### 题面、接口与约束

- `symm_quant_int8(x, dim=None) -> (q, scale)`：对称量化到 int8，范围 $[-127, 127]$。`scale = max|x| / 127`，并设一个正下限，避免全 0 输入除以 0。`dim=None` 时整个张量共用一个标量 scale；给定 `dim` 时沿该轴取最大值，scale 保留该维（`keepdim=True`）。
- `int8_linear(xq, wq, sx, sw) -> y`：`xq` 是 `[M, K]` int8，`wq` 是 `[N, K]` int8，先升到 int32 做 $X W^\top$ 得到 `[M, N]`，再乘 scale。`sx` 是标量或 `[M, 1]`（per-token），`sw` 是标量、`[N]` 或 `[N, 1]`（per-output-channel）。
- `roundtrip_err(x, dim=None)`：量化再反量化后的最大绝对误差，用于检查。

### 输入输出示例

```text
x = [[0, 1, -2], [1, -0.2, 0]]，dim=1（每行一个 scale）
-> scale = [[2/127], [1/127]]，每行绝对值最大的元素映射到 ±127
-> 反量化误差不超过该行 scale / 2

x = [0, 0, 0] -> q = [0, 0, 0]，scale 是一个很小的正数
```

### 解题思路与正确性

int8 直接相乘再累加会溢出，所以两边先升到 int32 再做矩阵乘。结果 `[M, N]` 的第 $(i, j)$ 个元素要乘激活第 $i$ 行的 scale 和权重第 $j$ 个输出通道的 scale。权重 scale 量化时是 `[N, 1]`，必须转成 `[1, N]` 才能沿列广播；直接乘 `[N, 1]` 会在 $M = N$ 时悄悄按行广播，得到错的结果。

### 完整参考实现（Python 3）

```python
import torch


def symm_quant_int8(x, dim=None):
    """对称 INT8 量化。dim=None 为 per-tensor，否则沿 dim 取 max（keepdim）。

    返回 (q: int8，与 x 同形状, scale: 正的浮点张量)。
    """
    if dim is None:
        amax = x.abs().amax()
    else:
        amax = x.abs().amax(dim=dim, keepdim=True)
    scale = (amax / 127.0).clamp_min(1e-12)
    q = (x / scale).round().clamp(-127, 127).to(torch.int8)
    return q, scale


def int8_linear(xq, wq, sx, sw):
    """INT8 线性层的数值参考：int32 累加后再乘两边的 scale。

    xq: [M, K] int8，wq: [N, K] int8；sx: 标量或 [M, 1]；sw: 标量、[N] 或 [N, 1]。
    返回 [M, N] float32。
    """
    acc = xq.to(torch.int32) @ wq.to(torch.int32).T  # [M, N] int32
    y = acc.float() * sx
    sw = torch.as_tensor(sw)
    if sw.numel() > 1:
        sw = sw.reshape(1, -1)  # [N] 或 [N, 1] -> [1, N]，沿输出通道广播
    return y * sw


def roundtrip_err(x, dim=None):
    """量化后再反量化的最大绝对误差。"""
    q, scale = symm_quant_int8(x, dim=dim)
    return (q.float() * scale - x).abs().max()
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert y.shape == (2, 2)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
torch.set_num_threads(1)
x = torch.tensor([[0.0, 1.0, -2.0], [1.0, -0.2, 0.0]])
w = torch.tensor([[1.0, 0.0, -0.5], [-1.0, 0.5, 0.0]])

# per-token 激活 + per-channel 权重：结果接近浮点矩阵乘
xq, sx = symm_quant_int8(x, dim=1)
wq, sw = symm_quant_int8(w, dim=1)
y = int8_linear(xq, wq, sx, sw)
assert y.shape == (2, 2)
assert torch.allclose(y, x @ w.T, atol=0.04)

# 每行最大绝对值映射到 ±127，反量化误差不超过半格
assert xq.abs().amax(dim=1).tolist() == [127, 127]
assert torch.all((xq.float() * sx - x).abs() <= sx / 2 + 1e-6)

# 全 0 输入：量化结果全 0，scale 仍为正
q, scale = symm_quant_int8(torch.zeros(3))
assert torch.all(q == 0)
assert scale > 0

# per-tensor：两个标量 scale 也能得到同样的近似
xq, sx = symm_quant_int8(x)
wq, sw = symm_quant_int8(w)
assert sx.dim() == 0
assert torch.allclose(int8_linear(xq, wq, sx, sw), x @ w.T, atol=0.05)

# M = N 时 [N, 1] 的权重 scale 也必须沿列广播
x_square = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
w_rows = torch.tensor([[10.0, 0.0], [0.0, 1.0]])
xq, sx = symm_quant_int8(x_square, dim=1)
wq, sw = symm_quant_int8(w_rows, dim=1)
assert torch.allclose(int8_linear(xq, wq, sx, sw), x_square @ w_rows.T, atol=1e-4)

# roundtrip_err 与 scale / 2 的上界一致
assert roundtrip_err(torch.tensor([0.3, -1.0, 0.77])) <= 1.0 / 127 / 2 + 1e-6
```

### 复杂度与追问

设激活为 $M\times K$、权重为 $N\times K$。量化是 $O(MK+NK)$，矩阵乘是 $O(MNK)$。这段代码是数值参考，`int32` 矩阵乘在 CPU 上跑，不代表硬件 INT8 GEMM 的速度。

- 追问「为什么不先 dequant 成 fp16 再乘」：那样乘法走的是 fp16，用不上 INT8 Tensor Core，量化只省了存储。
- 追问「激活 scale 沿哪一维取」：per-token 沿 $K$ 取（`dim=1`），每个 token 一个 scale。沿 $M$ 取会让所有 token 共用一个 scale，见下文。

## 题怎么来的

NVIDIA 的量化开口题常常从对称 INT8 映射开始；非对称和零点在 `nvidia-int8-quant` 里讲完。这道题把映射落到一个能写出来的 GEMM 上：scale 怎么广播、饱和怎么做、累加用哪种整数。

LLM 推理里最常被点名的实现是 Dettmers 的 LLM.int8() / bitsandbytes：按向量方向取 scale，再让 outlier 通道走 fp16。白板上先写纯对称路径；按通道拆出混合精度是后加的补丁，不属于对称量化的定义。

## 映射：scale 与饱和

对称量化约定实数 $0$ 映射到整数 $0$，没有零点 $z$。对一块张量（或沿指定维）：

$$
s=\frac{\max|x|}{127},\qquad
q=\mathrm{clip}\bigl(\mathrm{round}(x/s),-127,127\bigr),\qquad
\hat x=q\cdot s.
$$

用 $127$ 而不是 $128$，是为了让正负范围对称。有的实现允许取到 $-128$，白板上要说清楚：对称量化不依赖 $-128$ 多出来的那一格。全零块的 $s=0$ 要 clamp 成一个很小的正数，避免除以 $0$。`round` 遇到平局时用银行家舍入还是远离零舍入，要和 calibration 工具保持一致，否则重建结果对不齐。

线性层里 $x$ 是 `[M, K]`，PyTorch 的 $W$ 是 `[N, K]`，$y=xW^\top$ 是 `[M, N]`。INT8 路径是

$$
Y_{\mathrm{i32}}=X_{\mathrm{i8}}W_{\mathrm{i8}}^\top,\qquad
Y_{\mathrm{f}}=Y_{\mathrm{i32}}\odot s_x\odot s_w.
$$

$s_x$ 和 $s_w$ 的形状决定怎么广播：

- 两边都 per-tensor：两个标量，乘在整个 `[M, N]` 上。
- 权重 per-channel：沿输出通道，$s_w$ 是 `[N]` 或 `[1, N]`。
- 激活 per-token：沿 batch 的行，$s_x$ 是 `[M, 1]`。

累加必须在 int32（或 fp32 累加器）里做。两个 int8 的乘积是 int16 量级，$K=4096$ 时求和会溢出 int16。

对激活用 `dim=1`（沿 $K$）就是 per-token，对 $W$ 用 `dim=1` 就是 per-output-channel。`amax` 不要沿错维：对激活沿 $M$ 取 max，所有 token 会共用一个 scale，一个异常大的 token 就会把 scale 撑大，让其他 token 的小值都被量化成 $0$。

## LLM.int8 和「对称」差在哪

bitsandbytes 的 LLM.int8() 仍然是对称量化、按向量方向取 scale。它发现少数 feature 通道的幅度极大，INT8 的格子不够用，于是把这些 outlier 列留在 fp16，其余列做 INT8 GEMM，最后把两部分结果加回 `[M, N]`。这是按通道拆分的混合精度，不是非对称零点，不要把 outlier 路径说成 $z\ne 0$。

decode 一步的 $M$ 很小（常常就是 batch 大小 $B$），GEMM 的行数少，INT8 带来的加速可能被 dequant 和 kernel launch 的开销吃掉。和 `nvidia-int8-quant` 的结论一样：先 profile。

## 追问

**round 和 clip 谁先谁后？**
clipping boundaries ±127 是整数，所以先 round 再 clip 和先 clip 再 round 得到的结果相同。真正要注意的是 clip 必须在转成 int8 之前：如果先转类型，超出范围的值（比如 128）可能溢出回绕成负数。
**非对称比这里多了什么？**
多一个零点 $z$，让实数 $0$ 落到某个整数上。对称量化强制 $z=0$，实现更简单；激活整体偏向一侧时，量化误差会更大。
**$Y_{\mathrm{i32}}$ 能原地改成 int8 吗？**
不能拿 int8 当累加器。输出如果还要再量化，那是另一次对称映射，scale 要重新估计。
**和 KV 的 FP8 是一回事吗？**
不是。KV 的低比特格式见 `nvidia-fp8-kv`，那是 cache 元素的存储格式；这里量化的是 GEMM 的权重和激活。

## 相关题

- [[nvidia-int8-quant]]：同一个对称 INT8 公式的口答版，多讲了非对称零点、calibration 和 INT8 为什么可能反而更慢，不用写代码。
- [[nvidia-w4a8]]：把视角从单个 INT8 映射拉到部署配方，讲 W4、A8、KV 三套 scale 各自省哪笔带宽。
