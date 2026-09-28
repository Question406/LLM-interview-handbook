---
id: coding-int8-symm
section: coding
order: 32
level: A
title: 白板：对称 INT8 量化，scale、饱和，以及 dequant GEMM 的形状
quick: >-
  $s=\max|x|/127$，$q=\mathrm{clip}(\mathrm{round}(x/s),-127,127)$，$\hat x=q\cdot s$。零点是 $0$。INT8
  GEMM 累加在 int32，再乘两边的 scale。权重常 per-channel `[N,1]`，激活 per-tensor 或 per-token `[M,1]`。
tags:
  - Coding
  - INT8
  - Quantization
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: LLM.int8() — 8-bit Matrix Multiplication for Transformers at Scale
    url: https://arxiv.org/abs/2208.07339
    type: primary
  - title: bitsandbytes
    url: https://github.com/bitsandbytes-foundation/bitsandbytes
    type: primary
  - title: TensorRT — Working with Quantized Types
    url: https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-with-quantized-types.html
    type: secondary
---

## 题怎么来的

NVIDIA 量化开口题常常是对称 INT8 映射；`nvidia-int8-quant` 把非对称和零点讲完。本题收成可写的 GEMM：scale
怎么广播、饱和怎么打、累加用哪一种整数。Dettmers 的 LLM.int8() / bitsandbytes 是 LLM
推理里最常被点名的实现：向量方向的 scale，外加 outlier 通道走 fp16。白板先写纯对称路径；混合精度拆通道是补丁，不是对称量化的定义。

## 映射：scale 与饱和

对称量化约定实数 $0$ 映到整数 $0$，没有零点 $z$。对一块张量（或沿指定维）：

$$
s=\frac{\max|x|}{127},\qquad
q=\mathrm{clip}\bigl(\mathrm{round}(x/s),-127,127\bigr),\qquad
\hat x=q\cdot s.
$$

用 $127$ 而不是 $128$，是为了正负范围对称；有的实现允许 $-128$，白板说清「对称就不要靠 $-128$ 多出来的那格」。$s=0$
的全零块要 clamp 成很小的正数，避免除 $0$。`round` 的平局（银行家舍入 vs 远离零）要和校准工具一致，否则重建对不齐。

Linear：$x$ 是 `[M, K]`，$W$ 是 `[N, K]`（PyTorch），$y=xW^\top$ 是 `[M, N]`。INT8 路径：

$$
Y_{\mathrm{i32}}=X_{\mathrm{i8}}W_{\mathrm{i8}}^\top,\qquad
Y_{\mathrm{f}}=Y_{\mathrm{i32}}\odot s_x\odot s_w.
$$

$s_x$ 与 $s_w$ 的形状决定广播：

- 两边 per-tensor：两个标量，乘在整个 `[M, N]` 上。
- 权重 per-channel：沿输出通道，$s_w$ 是 `[N]` 或 `[1, N]`。
- 激活 per-token：沿 batch 行，$s_x$ 是 `[M, 1]`。

累加必须在 int32（或 fp32 累加器）。两个 int8 相乘是 int16 量级，$K=4096$ 时求和会溢出 int16。不要先 dequant
成 fp16 再 GEMM：那就把 INT8 Tensor Core 吐回去了。

```python
import torch

def symm_quant_int8(x, dim=None):
    amax = x.abs().amax(dim=dim, keepdim=True) if dim is not None else x.abs().amax()
    scale = (amax / 127.0).clamp_min(1e-12)
    q = (x / scale).round().clamp(-127, 127).to(torch.int8)
    return q, scale

def int8_linear(xq, wq, sx, sw):
    # xq: [M, K] int8; wq: [N, K] int8; sx: [M,1] or scalar; sw: [N] or scalar
    acc = xq.to(torch.int32) @ wq.to(torch.int32).T  # [M, N]
    y = acc.float() * sx
    sw_t = sw.reshape(1, -1) if torch.as_tensor(sw).numel() > 1 else sw
    return y * sw_t

def roundtrip_err(x, dim=None):
    q, s = symm_quant_int8(x, dim=dim)
    return (q.float() * s - x).abs().max()
```

`sx` 用 `dim=1`（沿 $K$）就是 per-token；$W$ 用 `dim=1` 是 per-out-channel。不要把 `amax`
沿错维：沿 $M$ 对激活取 max 会让所有 token 共享一个 scale，outlier token 把别人全压到 $0$。

## LLM.int8 和「对称」差在哪

bitsandbytes 的 LLM.int8() 仍是对称、向量方向 scale，但发现少数 feature 通道幅度极大，INT8 格不够。做法：把
outlier 列留在 fp16，其余做 INT8 GEMM，再把两段结果加回 `[M, N]`。这是混合精度拆通道，不是非对称零点；别把
outlier 路径说成 $z\ne 0$。Decode 一步 $M$ 很小（常是 $B$），GEMM 瘦，INT8 加速可能被 dequant 和
kernel launch 吃掉，和 `nvidia-int8-quant` 一样：先 profile。

## 追问

- **为什么饱和要在 round 之后？** 先 clip 再 round 会改变边界附近的格子。标准映射是 round 到最近整数再打进 $[-127,127]$。
- **非对称相对这里多了什么？** 零点 $z$，让实数 $0$ 落到某个 int。对称强制 $z=0$，实现简单，激活偏置大时量化误差更大。
- **$Y_{\mathrm{i32}}$ 能原地改成 int8 吗？** 不能当累加器。输出若还要再量化，是另一次对称映射，scale 重新估。
- **和 KV 的 FP8 是一回事吗？** 不是。KV 低比特见 `nvidia-fp8-kv`，那是 cache 元素格式；这里是 GEMM 权重/激活。
