---
id: coding-gqa-repeat
section: coding
order: 16
level: A
title: 白板：GQA 把 KV head repeat 成 query heads，shape 怎么断言
quick: "cache 里 K/V 保持 `[B, H_kv, S, D]`，算分数前沿 head 轴 `repeat_interleave` 成 `H_q` 份；用 repeat 会打乱分组。"
tags:
  - 完整编程练习
  - Coding
  - GQA
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `repeat_kv(x, n_rep)`：`x` 形状 `[B, H_kv, S, D]`，返回 `[B, H_kv * n_rep, S, D]`。相邻的 `n_rep` 个输出 head 来自同一个 KV head。`n_rep` 必须是正整数。
- `gqa_attn(q, k, v)`：`q` 形状 `[B, H_q, T, D]`，`k`、`v` 形状 `[B, H_kv, S, D]`，返回 `[B, H_q, T, D]`。不带 mask 的注意力（也可以看成 cross-attention）。
- $H_q$ 必须是 $H_{\mathrm{kv}}$ 的正整数倍，$T, S \ge 1$；形状不匹配时抛 `ValueError`。

### 输入输出示例

```text
H_q = 4, H_kv = 2, n_rep = 2
repeat_kv 之后的 head 顺序 -> [k0, k0, k1, k1]
错误的顺序（tensor.repeat） -> [k0, k1, k0, k1]
```

### 解题思路与正确性

在 head 轴后面插一个大小为 `n_rep` 的组维，用 `expand` 复制（不拷贝内存），再 `reshape` 把 `[H_kv, n_rep]` 合并成 `H_q`。合并后第 $h$ 个 query head 对应的 KV head 是 $\lfloor h / n_{\mathrm{rep}}\rfloor$，正好是 GQA 训练时的分组方式。

之后就是普通的缩放点积注意力。softmax 升到 fp32 计算再转回输入精度。测试拿 PyTorch 的 `scaled_dot_product_attention` 加 `repeat_interleave` 作对照。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，相邻 n_rep 个 head 共用一个 KV head。"""
    if not isinstance(n_rep, int) or n_rep < 1:
        raise ValueError(f"n_rep must be a positive int, got {n_rep!r}")
    if n_rep == 1:
        return x
    B, H_kv, S, D = x.shape
    return (
        x[:, :, None, :, :]
        .expand(B, H_kv, n_rep, S, D)
        .reshape(B, H_kv * n_rep, S, D)
    )


def gqa_attn(q, k, v):
    """GQA 注意力（无 mask）。q: [B, H_q, T, D]；k, v: [B, H_kv, S, D]；返回 [B, H_q, T, D]。"""
    B, H_q, T, D = q.shape
    H_kv = k.shape[1]
    if k.shape != v.shape:
        raise ValueError(f"k and v shapes differ: {tuple(k.shape)} vs {tuple(v.shape)}")
    if k.shape[0] != B or k.shape[-1] != D:
        raise ValueError(f"k shape {tuple(k.shape)} does not match q shape {tuple(q.shape)}")
    if H_q % H_kv != 0:
        raise ValueError(f"H_q={H_q} is not a multiple of H_kv={H_kv}")

    n_rep = H_q // H_kv
    k_rep = repeat_kv(k, n_rep)  # [B, H_q, S, D]
    v_rep = repeat_kv(v, n_rep)
    scores = torch.matmul(q, k_rep.transpose(-2, -1)) * D ** -0.5  # [B, H_q, T, S]
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    return torch.matmul(probs, v_rep)
```

### 可执行测试

```python
torch.set_num_threads(1)
torch.manual_seed(0)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


# head 顺序是 [k0, k0, k1, k1]，不是交错的
kv = torch.arange(4.0).reshape(1, 2, 1, 2)
assert torch.equal(repeat_kv(kv, 2)[:, :, 0, 0], torch.tensor([[0.0, 0.0, 2.0, 2.0]]))

# n_rep = 1 原样返回（MHA）
assert repeat_kv(kv, 1) is kv

# 和 PyTorch SDPA + repeat_interleave 一致
q = torch.randn(2, 4, 3, 2)
k = torch.randn(2, 2, 5, 2)
v = torch.randn_like(k)
out = gqa_attn(q, k, v)
ref = F.scaled_dot_product_attention(q, k.repeat_interleave(2, 1), v.repeat_interleave(2, 1))
assert out.shape == (2, 4, 3, 2)
assert torch.allclose(out, ref, atol=1e-6)

# MQA 端点：H_kv = 1
k1 = torch.randn(2, 1, 5, 2)
v1 = torch.randn_like(k1)
ref1 = F.scaled_dot_product_attention(q, k1.expand(2, 4, 5, 2), v1.expand(2, 4, 5, 2))
assert torch.allclose(gqa_attn(q, k1, v1), ref1, atol=1e-6)

# 非法输入
expect_value_error(repeat_kv, kv, 0)
expect_value_error(gqa_attn, torch.randn(1, 3, 2, 2), torch.randn(1, 2, 2, 2), torch.randn(1, 2, 2, 2))
expect_value_error(gqa_attn, q, k, torch.randn(2, 2, 4, 2))
```

### 复杂度与追问

设 batch 为 $B$、query head 数为 $H_q$、query 长度 $T$、key 长度 $S$、头维 $D$。时间 $O(BH_qTSD)$。显式 repeat 会物化 $O(BH_qSD)$ 的临时 K/V；融合的 GQA kernel 在寄存器里广播，不需要这份物化，cache 也始终只存 $H_{\mathrm{kv}}$ 组。

## 题怎么来的

Llama 2 70B 的公开配置是 $64$ 个 query head、$8$ 个 KV head、头维 $128$（$8192/64$）。Meta 白板会让你把 `repeat_kv` 写出来，并说清 cache 存几组、计算时 repeat 几次。选型讨论见 `meta-llama-gqa`、`google-gqa-mqa`。MQA 是 $H_{\mathrm{kv}}=1$ 的端点，实现见 `coding-mq-attn`。shape 检查要真的写出来，不要口头说“广播一下”。

## 分组和 repeat 的轴

$Q$ 是 `[B, H_q, T, D]`，$K,V$ 是 `[B, H_kv, S, D]`。不变量是：

$$
H_q \bmod H_{\mathrm{kv}}=0,\quad n_{\mathrm{rep}}=H_q/H_{\mathrm{kv}}.
$$

70B 的 $n_{\mathrm{rep}}=8$，每 $8$ 个 query head 共享一组 $K,V$。repeat 发生在计算 $QK^\top$ 之前，cache 里仍然只写 $8$ 组。如果把 cache 存成 $64$ 组，GQA 节省缓存和带宽的好处就没了。

正确的 head 排布是相邻 $n_{\mathrm{rep}}$ 个 $Q$ head 共用同一个 KV head：

$$
\text{kv index}=\lfloor h_q / n_{\mathrm{rep}}\rfloor.
$$

`unsqueeze` + `expand` + `reshape`，或者沿 head 维 `repeat_interleave`，得到的都是这个顺序。`tensor.repeat(1, n_rep, 1, 1)` 则是把整段 KV head 列表复制几遍，和训练时投影的分组对不上。

$H_q=H_{\mathrm{kv}}$ 时 $n_{\mathrm{rep}}=1$，函数直接返回，这就是 MHA，不需要为了写法对称硬做一次 repeat。

## 投影层的 shape

$W_Q$ 输出 `H_q * D` 维，$W_K, W_V$ 输出 `H_kv * D` 维。`view` 成 `[B, T, H, D]` 再 `transpose` 成 `[B, H, T, D]` 时，两边的 $H$ 分别是 $H_q$ 和 $H_{\mathrm{kv}}$，不能共用一个 `n_heads`。RoPE 沿头维旋转，和 $H_{\mathrm{kv}}$ 无关，见 `coding-rope`。不物化 repeat 的 GQA kernel 和显式 repeat 的数值应当一致；白板上先写显式版本，再说明融合路径里 cache 仍然是 $H_{\mathrm{kv}}$ 组。

## 追问

- **`repeat` 和 `repeat_interleave` 差在哪？** 后者（以及 expand + reshape）得到 `[k0, k0, ..., k1, k1, ...]`；`repeat` 沿 head 维得到 `[k0, k1, ..., k0, k1, ...]`。和 $W_Q$ 的分组对不上时不会报错，只会悄悄算出错误的数值。
- **逐 token 生成（decode）每步都要 repeat 吗？** 当前步的 $K_t, V_t$ 仍按 $H_{\mathrm{kv}}$ 写入 cache。算注意力时再对已缓存的 $K,V$ 做 repeat，或者走 GQA kernel 在寄存器里广播。
- **$H_q$ 能不被 $H_{\mathrm{kv}}$ 整除吗？** 标准 GQA 不行，面试时直接做检查并报错。
- **和 MQA 比？** MQA 是 $H_{\mathrm{kv}}=1$、$n_{\mathrm{rep}}=H_q$，见 `coding-mq-attn`。70B 选 GQA 而不是 MQA，主要是为了模型质量，不是因为 MQA 难实现。

## 相关题

- [[meta-gqa-kernel]]：Meta 的同类实现题，追问更偏 kernel：按 `h_q // g` 索引 KV head，不在 HBM 里先 repeat。
- [[coding-mq-attn]]：$H_{\mathrm{kv}}=1$ 的特例，用 broadcast 代替 repeat，cache 布局怎么存。
- [[coding-decode-step]]：把这里的 repeat 放进完整的一步 decode，连同 RoPE 位置、concat KV 和出 logits 一起写。
- [[google-gqa-mqa]]：口述题，讲 MHA、MQA、GQA 怎么选、KV 显存差多少，不写代码。
