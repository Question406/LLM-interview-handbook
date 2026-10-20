---
id: coding-mq-attn
section: coding
order: 22
level: A
title: 白板：MQA 单 KV head，怎么对 query heads broadcast
quick: >-
  MQA 的 K、V 只有一个 head（`[B, 1, S, d_h]`），Q 仍有 H 个 head；matmul 时让 K、V 沿 head 维广播，不要 repeat 成 H 份再写进 cache。
tags:
  - 完整编程练习
  - Coding
  - MQA
  - Attention
  - Google
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Fast Transformer Decoding — One Write-Head is All You Need
    url: https://arxiv.org/abs/1911.02150
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。下文 D 是模型维度，H 是 query head 数，$d_h = D/H$ 是 head 维度。

### 题面、接口与约束

- `mqa(q, k, v, attn_bias=None) -> Tensor[B, H, T, d_h]`：`q` 形状 `[B, H, T, d_h]`；`k`、`v` 形状 `[B, 1, S, d_h]`，或省掉 head 维的 `[B, S, d_h]`。`attn_bias` 能广播到 `[B, H, T, S]`，加在 softmax 之前。
- `mqa_projections(x, wq, wk, wv, n_heads) -> (q, k, v)`：`x` 形状 `[B, T, D]`，`wq` 形状 `[D, D]`，`wk`、`wv` 形状 `[D, d_h]`；返回 `q [B, H, T, d_h]` 和 `k, v [B, 1, T, d_h]`。
- 不物化 H 份 K、V；`D` 不能被 `n_heads` 整除、KV head 数不是 1、batch 或 head 维对不上时抛 `ValueError`。
- 调用方保证 `attn_bias` 的每一行至少留一个可见 key（否则 softmax 会得到 NaN）。

### 输入输出示例

```text
D = 8, H = 4  ->  d_h = 2
wk: [8, 2]（不是 [8, 8]），k: [B, 1, T, 2]
mqa(q [2, 4, 3, 2], k [2, 1, 3, 2], v [2, 1, 3, 2]) -> [2, 4, 3, 2]
```

### 解题思路与正确性

`q @ k.transpose(-2, -1)` 是 `[B, H, T, d_h] @ [B, 1, d_h, S]`，PyTorch 会把 K 的 head 维从 1 广播到 H，得到 `[B, H, T, S]`。所有 query head 用的是同一组 key，这正是 MQA 的定义。softmax 沿最后一维（key）做，再乘同样广播的 V，得到 `[B, H, T, d_h]`。

广播只发生在计算时，不分配 H 份 K、V，所以 cache 只需要存 `[B, 1, S, d_h]`。投影侧，`wk`、`wv` 的输出宽度是 $d_h$，元素数只够一个 KV head；如果误写成 `[D, D]`，view 成一个 head 时就会对不上。

### 完整参考实现（Python 3）

```python
import torch
import torch.nn.functional as F


def mqa(q, k, v, attn_bias=None):
    """Multi-Query Attention：q [B, H, T, d_h]，k/v [B, 1, S, d_h] 或 [B, S, d_h] -> [B, H, T, d_h]。

    K、V 沿 head 维广播，不复制成 H 份。
    """
    if k.dim() == 3:
        k = k.unsqueeze(1)
        v = v.unsqueeze(1)
    if k.shape[1] != 1 or v.shape[1] != 1:
        raise ValueError(f"MQA expects exactly one KV head, got {k.shape[1]} and {v.shape[1]}")
    if q.shape[0] != k.shape[0] or q.shape[-1] != k.shape[-1]:
        raise ValueError(f"q {tuple(q.shape)} and k {tuple(k.shape)} disagree on batch or head dim")

    scale = q.size(-1) ** -0.5
    scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H, T, S]
    if attn_bias is not None:
        scores = scores + attn_bias
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)  # 沿 key 维
    return torch.matmul(probs, v)                              # [B, H, T, d_h]


def mqa_projections(x, wq, wk, wv, n_heads):
    """x [B, T, D] -> q [B, H, T, d_h]，k/v [B, 1, T, d_h]；wq [D, D]，wk/wv [D, d_h]。"""
    batch, seq_len, model_dim = x.shape
    if model_dim % n_heads != 0:
        raise ValueError(f"model dim {model_dim} is not divisible by n_heads={n_heads}")
    head_dim = model_dim // n_heads
    if wk.shape != (model_dim, head_dim) or wv.shape != (model_dim, head_dim):
        raise ValueError(f"wk/wv must be [{model_dim}, {head_dim}], got {tuple(wk.shape)} and {tuple(wv.shape)}")
    q = (x @ wq).view(batch, seq_len, n_heads, head_dim).transpose(1, 2)
    k = (x @ wk).view(batch, seq_len, 1, head_dim).transpose(1, 2)
    v = (x @ wv).view(batch, seq_len, 1, head_dim).transpose(1, 2)
    return q, k, v
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(0)
x = torch.randn(2, 3, 8)
wq = torch.randn(8, 8)
wk = torch.randn(8, 2)
wv = torch.randn(8, 2)

# 投影形状：Q 有 4 个 head，K/V 只有 1 个
q, k, v = mqa_projections(x, wq, wk, wv, 4)
assert q.shape == (2, 4, 3, 2)
assert k.shape == (2, 1, 3, 2)

# 与把 K/V 显式 expand 成 H 份后的标准注意力一致
out = mqa(q, k, v)
reference = F.scaled_dot_product_attention(q, k.expand(-1, 4, -1, -1), v.expand(-1, 4, -1, -1))
assert torch.allclose(out, reference, atol=1e-5)

# 省掉 head 维的 [B, S, d_h] 输入结果相同
assert torch.allclose(mqa(q, k[:, 0], v[:, 0]), out)

# 因果 bias 与 SDPA 的 is_causal 一致
causal_bias = torch.full((3, 3), float("-inf")).triu(1)
causal_ref = F.scaled_dot_product_attention(q, k.expand(-1, 4, -1, -1), v.expand(-1, 4, -1, -1), is_causal=True)
assert torch.allclose(mqa(q, k, v, causal_bias), causal_ref, atol=1e-5)

# 非法输入：两个 KV head、wk 写成 [D, D]、D 不能整除
expect_value_error(mqa, q, k.expand(-1, 2, -1, -1), v.expand(-1, 2, -1, -1))
expect_value_error(mqa_projections, x, wq, torch.randn(8, 8), torch.randn(8, 8), 4)
expect_value_error(mqa_projections, x, wq, wk, wv, 3)
```

### 复杂度与追问

设 batch B、query head 数 H、query 长度 T、key 长度 S、head 维 $d_h$。注意力计算 $O(BHTS \cdot d_h)$，scores 占 $O(BHTS)$；K、V 的存储只有 $O(BS \cdot d_h)$，是 MHA 的 1/H。

- 追问「decode 时省在哪」：一步 T=1，时间主要花在读历史 KV 上，MQA 读的字节数约为 MHA 的 1/H。
- 追问「`einsum` 能写吗」：`einsum('bhtd,bsd->bhts', q, k.squeeze(1))` 等价。但不要 `expand` 出 H 份再 `contiguous`，那会真的分配 cache 大小的内存。

## 题怎么来的

Shazeer 2019 提出 Multi-Query Attention：多个 query head 共用一组 $K,V$。Google 推理岗和 Apple 端侧都会问，因为逐 token 生成（decode）的带宽取决于 $H_{\mathrm{kv}}$，MQA 把 cache 降到 MHA 的 $1/H$。和 GQA 的谱系关系见 `google-gqa-mqa`，GQA 的 repeat 实现见 `coding-gqa-repeat`。白板上要写出 broadcast，不要把 MQA 讲成「head 少一点的 MHA」。

## 形状：一个 KV head，多个 Q head

$Q$ 是 `[B, H, T, d_h]`，$K,V$ 是 `[B, 1, S, d_h]`（也可以省掉 head 维写成 `[B, S, d_h]`，matmul 前 `unsqueeze(1)`）。

$$
S_{\mathrm{scores}}[b,h,t,s]=\frac{Q[b,h,t,:]\cdot K[b,0,s,:]}{\sqrt{d_h}}.
$$

$K$ 没有 $h$ 下标，所有 query head 和同一组 key 做点积。softmax 仍沿 $s$（key 长度）做，再乘同一组 $V$：`[B, H, T, S] @ [B, 1, S, d_h] -> [B, H, T, d_h]`。广播只发生在计算里，cache 只存 `[B, 1, S, d_h]`。如果先 `repeat` 成 `[B, H, S, d_h]` 再缓存，MQA 省下的显存就没了。

$W_Q$ 的输出宽度是 $H\cdot d_h$，$W_K,W_V$ 的输出宽度是 $d_h$，再 view 成一个 head。RoPE 对这一个 KV head 旋转一次，对 $H$ 个 query head 各自旋转；不要给 $K$ 伪造 $H$ 套角度。

## 和 GQA / MHA 是一条连续谱

$H_{\mathrm{kv}}=H$ 是 MHA，$1 \lt H_{\mathrm{kv}} \lt H$ 是 GQA，$H_{\mathrm{kv}}=1$ 是 MQA。MQA 最省显存，也最容易伤害长上下文和难任务上的质量，所以 Llama 70B 停在了 8 组的 GQA。

模型必须按 MQA 训练过才能这么推理：拿 MHA 权重硬共享 $K$ 会对不上。GQA 论文给了从 MHA checkpoint 把 KV head 做 mean-pool 来初始化的办法，但那是一次转换，之后还要继续训练，并不是免费的。

Decode 一步 $T=1$，GEMM 很小，时间花在读历史 KV 上，MQA 的读带宽约为原来的 $1/H$。输入预填充（prefill，即处理输入并建立缓存）仍是 $T^2$ 的注意力，MQA 对它的加速远小于对 decode 的加速。Apple 端侧面试很爱听到这一点。

## 追问

- **broadcast 和 repeat 哪个对？** 只要 repeat 只发生在算子内部，两者数值都对。但 cache 布局必须按 $H_{\mathrm{kv}}=1$ 存。
- **head 维还是 $D/H$ 吗？** 是。$Q$ 仍按 $H$ 个头切；$K$ 只有一个头，宽度同样是 $d_h$，不是整条 $D$。
- **K 用 $d_h$、V 用别的宽度可以吗？** 标准 MQA 不这样做。GQA 和 MQA 改的是 KV head 的数量，不是 head 维度。
- **softmax 沿哪一维？** 仍是 key 长度那一维。沿 $H$ 做 softmax 是 `openai-transformer-debug` 那类轴错误，在 MQA 里更隐蔽，因为 $K$ 本身没有 $H$ 维。

## 相关题

- [[coding-gqa-repeat]]：一般的 GQA 情形，$H_{\mathrm{kv}}>1$ 时必须用 `repeat_interleave` 保住分组，这里的 broadcast 是它的特例。
- [[google-gqa-mqa]]：口述题，讲 MQA 和 GQA 怎么选、KV 显存差多少，不写代码。
- [[meta-gqa-kernel]]：Meta 的 GQA 实现题，追问 kernel 里怎么索引 KV head，并说明 MQA 只是 $g=H_q$ 的特例。
- [[coding-decode-step]]：把 KV head 的扩展放进完整的一步 decode，连同 RoPE 位置和 cache 拼接一起写。
