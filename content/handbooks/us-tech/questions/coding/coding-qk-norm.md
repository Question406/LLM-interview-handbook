---
id: coding-qk-norm
section: coding
order: 30
level: A
title: 白板：QK RMSNorm 再 RoPE，Qwen / 部分 Llama 变体怎么写
quick: "对每个 head 的 $q,k$ 先沿 $D$ 做 RMSNorm，再按训练架构的顺序做 RoPE；归一化有 $\\gamma$、无 $\\beta$，不处理 $v$。GQA 的 $k$ 只有 $H_{\\mathrm{kv}}$ 份，要先用自己的 `k_norm` 处理，最后需要时再 repeat。"
tags:
  - 完整编程练习
  - Coding
  - QK-Norm
  - RMSNorm
  - Qwen
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Qwen3 Technical Report
    url: https://arxiv.org/abs/2505.09388
    type: primary
  - title: Gemma 2 Technical Report
    url: https://arxiv.org/abs/2408.00118
    type: primary
  - title: Query-Key Normalization for Transformers
    url: https://arxiv.org/abs/2010.04245
    type: primary
---

## 题目描述

实现 Q/K 的 RMSNorm 与位置旋转组合，明确归一化和 RoPE 的作用顺序。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`rmsnorm_last(x,weight,eps=1e-6)` 沿最后一维用均方根归一化，不减均值；分母为 `sqrt(mean(x²)+eps)`，再乘长度为 d 的 weight，weight=None 视为全 1。统计使用 float32，输出转回输入 dtype，不含 bias。

`apply_rope(x,cos,sin)` 接收 `[B,H,T,d]` 和 `[T,d/2]` 的 cos/sin 表，对最后一维相邻的偶、奇分量成对旋转：一对 `(a,b)` 变为 `(a*cos-b*sin,a*sin+b*cos)`。

`qk_norm_then_rope(q,k,wq,wk,cos,sin)` 返回处理后的 `(q,k)`，先分别 RMSNorm，再 RoPE。q 为 `[B,Hq,T,d]`、k 为 `[B,Hkv,T,d]`，头数可不同，d 为正偶数；本题不处理 V。

### 示例

```text
q=k=[[[[2,2]]]]，wq=wk=[1,1]，cos=[[1]], sin=[[0]]。
返回的 q、k 均约为 [[[[1,1]]]]（考虑 eps 后略小于 1）。
相同设置的全零输入仍返回全零。
```

## 解题思路与参考答案

我会先沿每个 head 的最后一维分别归一化 Q、K，再做 RoPE，V 保持不变。GQA 的 Q、K 头数不同也没关系，各自沿头维计算即可；顺序则必须匹配 checkpoint，因为逐维缩放和旋转一般不能交换。下面先给可执行练习，再解释架构和缓存的边界。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，CPU 上验证；没有验证 GPU 或性能。

### 题面、接口与约束

- `rmsnorm_last(x, weight, eps=1e-6)`：沿最后一维做 RMSNorm，统计量在 fp32 里算，结果转回输入的 dtype。`weight` 是 `[d]` 的 $\gamma$，传 `None` 表示不缩放；没有 bias。
- `apply_rope(x, cos, sin)`：对 `[B, H, T, d]` 做 RoPE，维度 (0, 1)、(2, 3)… 两两成对旋转。`cos`、`sin` 是 `[T, d/2]`。`d` 为奇数或表的形状不对时抛 `ValueError`。
- `qk_norm_then_rope(q, k, w_q, w_k, cos, sin)`：Q 和 K 各用自己的权重做 RMSNorm，然后再做 RoPE，返回 `(q, k)`。
- `q` 是 `[B, H_q, T, d]`，`k` 是 `[B, H_kv, T, d]`，两者 head 数可以不同（GQA），`d` 为偶数。V 不做归一化。

### 输入输出示例

```text
q, k 全零                       -> 归一化后仍全零（eps 防止除 0）
q 任意，w_q = 全 1              -> 每个 head 的 RMS ≈ 1，RoPE 之后范数不变
位置 0（cos = 1, sin = 0）      -> RoPE 不改变这个 token
```

### 解题思路与正确性

RMSNorm 的约简轴是最后一维 `d`：每个 head、每个位置单独算一次 RMS，不在 head 之间、也不在时间维上混合。K 只有 `H_kv` 个 head，就按 `H_kv` 份来算，用的是 `w_k`。

RoPE 把每一对维度当作平面上的一个点做旋转，旋转不改变向量长度，所以 RMS 在旋转前后一样。真正让顺序有区别的是逐维相乘的 $\gamma$：旋转会把一对维度混在一起，先乘 $\gamma$ 再旋转和先旋转再乘 $\gamma$，在 $\gamma$ 不均匀时结果不同。测试里分别验证了这两种情况。按 Qwen3 的顺序，先 norm 再 RoPE。

### 完整参考实现（Python 3）

```python
import torch


def rmsnorm_last(x, weight, eps=1e-6):
    """沿最后一维 d 做 RMSNorm（统计量用 fp32 算），weight 为 [d] 或 None（不缩放）。"""
    x_fp32 = x.float()
    inv_rms = torch.rsqrt(x_fp32.pow(2).mean(dim=-1, keepdim=True) + eps)
    normed = (x_fp32 * inv_rms).to(x.dtype)
    return normed if weight is None else normed * weight


def apply_rope(x, cos, sin):
    """对 x: [B, H, T, d] 做 RoPE，维度 (0, 1)、(2, 3)… 两两成对旋转。cos, sin: [T, d/2]。"""
    seq_len, head_dim = x.shape[-2], x.shape[-1]
    if head_dim % 2:
        raise ValueError(f"RoPE requires an even head dim, got {head_dim}")
    expected = (seq_len, head_dim // 2)
    if cos.shape != expected or sin.shape != expected:
        raise ValueError(f"cos and sin must be {expected}, "
                         f"got {tuple(cos.shape)} and {tuple(sin.shape)}")
    even, odd = x[..., 0::2], x[..., 1::2]
    rotated_even = even * cos - odd * sin
    rotated_odd = even * sin + odd * cos
    # 把两半交错拼回 [.., d]：(e0, o0, e1, o1, ...)
    return torch.stack((rotated_even, rotated_odd), dim=-1).flatten(-2)


def qk_norm_then_rope(q, k, w_q, w_k, cos, sin):
    """先各自做 QK RMSNorm，再做 RoPE。q: [B, H_q, T, d]，k: [B, H_kv, T, d]。"""
    q = rmsnorm_last(q, w_q)
    k = rmsnorm_last(k, w_k)
    return apply_rope(q, cos, sin), apply_rope(k, cos, sin)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert q_out.shape == q.shape` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def rope_tables(seq_len, head_dim):
    positions = torch.arange(float(seq_len))[:, None]
    inv_freq = 10000 ** (-torch.arange(0, head_dim, 2) / head_dim)
    return torch.cos(positions * inv_freq), torch.sin(positions * inv_freq)


torch.manual_seed(0)
torch.set_num_threads(1)
q = torch.randn(2, 4, 3, 4)  # H_q = 4
k = torch.randn(2, 2, 3, 4)  # H_kv = 2，Q/K 的 head 数可以不同
ones = torch.ones(4)
cos, sin = rope_tables(3, 4)

# 形状不变；单位权重下旋转不改变归一化之后的范数
q_out, k_out = qk_norm_then_rope(q, k, ones, ones, cos, sin)
assert q_out.shape == q.shape
assert k_out.shape == k.shape
assert torch.allclose(q_out.square().sum(-1),
                      rmsnorm_last(q, ones).square().sum(-1), atol=1e-5)

# 全零输入归一化后仍是 0（eps 防止除 0）
assert torch.all(rmsnorm_last(torch.zeros_like(q), ones) == 0)

# 归一化后每个 head 的 RMS 约为 1；weight=None 等价于全 1 权重
assert torch.allclose(rmsnorm_last(q, None).square().mean(-1),
                      torch.ones(2, 4, 3), atol=1e-4)
assert torch.allclose(rmsnorm_last(q, None), rmsnorm_last(q, ones))

# 位置 0 的 cos = 1、sin = 0，RoPE 不改变第一个 token
assert torch.allclose(apply_rope(q, cos, sin)[:, :, 0], q[:, :, 0])

# 顺序：gamma 全为 1 时两种顺序相同（旋转不改变 RMS），gamma 不均匀时就不同了
gamma = torch.tensor([1.0, 2.0, 0.5, 3.0])
norm_first = apply_rope(rmsnorm_last(q, ones), cos, sin)
rope_first = rmsnorm_last(apply_rope(q, cos, sin), ones)
assert torch.allclose(norm_first, rope_first, atol=1e-5)
norm_first = apply_rope(rmsnorm_last(q, gamma), cos, sin)
rope_first = rmsnorm_last(apply_rope(q, cos, sin), gamma)
assert not torch.allclose(norm_first, rope_first, atol=1e-3)

# 非法输入：head 维为奇数；cos/sin 的长度和 T 对不上
expect_value_error(apply_rope, torch.randn(1, 1, 3, 3), cos, sin)
expect_value_error(apply_rope, q, cos[:2], sin[:2])
```

### 复杂度与追问

设 batch 为 B、长度为 T、head 维为 d，query 和 KV 的 head 数分别是 $H_q$、$H_{kv}$。归一化和旋转都是逐元素或沿 d 约简，时间 $O(B \cdot (H_q + H_{kv}) \cdot T \cdot d)$，输出也是同样大小。和投影 GEMM 相比，这两次额外约简的开销可以忽略。

- 追问「GQA 时 K 能不能先 repeat 再 norm」：不行，见下文。先按 `H_kv` 份 norm 和 RoPE，需要时再 repeat。

## 题怎么来的

Henry et al. 把 QK 归一化当作稳定训练的手段，Gemma 2 和 Qwen3 把它写进了公开架构。Qwen3 的报告明确说去掉了 QKV bias、加上 QK-Norm，HuggingFace 实现里是先 RMSNorm 再 RoPE。部分 Llama 变体（社区里常提到 Llama 4 一类）可能把 norm 放在 RoPE 之后，和 Qwen 不是同一张计算图。Meta 和跨境 Qwen 岗的白板会要你写清顺序、约简的轴，以及 $H_q\ne H_{\mathrm{kv}}$ 时有几份 $\gamma$。层输入处的那份 RMSNorm 仍然在，见 `coding-rmsnorm`；本题说的是注意力内部多出来的两份。

## 沿 head dim 归一，再旋转

$Q$ 的形状是 `[B, H_q, T, D]`，$K$ 是 `[B, H_kv, S, D]`。QK-Norm 沿最后一维 $D$ 约简，每个 head 算自己的 RMS，不在 head 之间混：

$$
\mathrm{RMS}(x)=\sqrt{\frac{1}{D}\sum_{i=1}^{D}x_i^2+\varepsilon},\qquad
\hat q=\gamma_q\odot\frac{q}{\mathrm{RMS}(q)},\quad
\hat k=\gamma_k\odot\frac{k}{\mathrm{RMS}(k)}.
$$

$\gamma_q\in\mathbb{R}^{D}$ 广播到所有 query head。有的实现把它做成 `[H_q, D]` 的 per-head 参数，Qwen3 通常只用一份长度为 $D$ 的。没有 bias $\beta$，$V$ 也不做归一化。之后再旋转：

$$
q',k'=\mathrm{RoPE}(\hat q,\hat k).
$$

公开的 Qwen3 权重是按「norm → RoPE」训练出来的。顺序反了不会报错，但 $\gamma$ 作用的坐标系变了（见上面练习里的顺序测试），结果和 checkpoint 对不上。这种错误和把 RoPE 的相邻配对与 half-rotate 配对搞混是同一类，都不容易发现。decode 时 $T=1$，RMS 仍然沿 $D$ 算，不沿 cache 长度算。

GQA 时不要先对 `k` 做 `repeat_kv` 再 norm，否则 $H_{\mathrm{kv}}$ 份的计算被复制成 $H_q$ 份，如果用的是 per-head 参数，还会和训练时的 `k_norm` 对不上。正确顺序是：对 $H_{\mathrm{kv}}$ 份 $K$ 做 norm，再做 RoPE，需要时最后 repeat，见 `coding-gqa-repeat`。cache 里存的是已经 norm 加 RoPE 之后的 $K$，逐 token 生成（decode）时不要对历史 $K$ 再 norm 一遍。

## 为什么要它，和层 RMSNorm 别并成一个

QK 点积没有自己的归一化时，logit 的尺度会随 $\|W_Q\|,\|W_K\|$ 增长，softmax 越来越尖，训练容易不稳定。QK-Norm 把每个 head 的 $q,k$ 固定在相近的 RMS 上，相当于给注意力温度加了一个锚。层上的 RMSNorm 管的是残差流 `[B, T, D_model]`，约简的轴和作用对象都不同，不能删掉其中一个来代替另一个。

$\varepsilon$ 可以和层 norm 的不同，实现里常用 $10^{-6}$，统计量在 fp32 里算。Apple 端侧面试可能会问多两次约简值不值：相对 GEMM 的开销可以忽略，换来的是能用更大的学习率、训更深的注意力。MLA 这类不显式生成完整 $q,k$ 的结构不一定能直接套用，面试里说明「这是给 MHA/GQA 打的补丁」就够了。

## 追问

**一定要在 RoPE 之前吗？**
Qwen3 和常见的 Gemma 路径是在之前，公开讨论里 Llama 4 一类是在之后。加载权重前先看 `q_norm` 插在哪里，不要猜。
**$V$ 要不要 norm？**
标准 QK-Norm 不做。$V$ 是被加权求和的内容，不是点积的两边。
**和点积的 $1/\sqrt{D}$ 缩放重复吗？**
不重复。缩放是常数，RMSNorm 随每个样本、每个 head 变化，两者都要保留。
**decode 时历史 $K$ 还要 norm 吗？**
写入 cache 时做过了，就不要再做。对 cache 再 norm 一次，等于用当前的 $\gamma$ 去改旧向量，逐步生成的结果会和一次性输入预填充（prefill，即处理整段输入并建立缓存）的结果对不齐。

## 相关题

- [[coding-rmsnorm]]：残差流上的层 RMSNorm，公式和本题相同，但约简对象是 `[B, T, D_model]`，两者不能互相替代。
- [[coding-layernorm]]：带减均值和 $\beta$ 的完整 LayerNorm，用来说明 QK-Norm 为什么选 RMSNorm。
- [[coding-rope]]：QK norm 之后接的就是这一步旋转，decode 位置取 cache 长度。
