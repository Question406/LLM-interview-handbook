---
id: coding-rope-cache
section: coding
order: 21
level: A
title: 白板：RoPE 的 cos/sin cache，decode 时怎么 index
quick: "预计算 `[max_seq, D/2]` 的 $\\cos,\\sin$ 表，用绝对的 `position_ids` 查表；decode 一步的位置是 `cache_len`，只旋转当前的 $q,k$。"
tags:
  - 完整编程练习
  - Coding
  - RoPE
  - KV Cache
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没有验证 GPU、多卡或性能。

### 题面、接口与约束

- `RopeCache(dim, max_seq=4096, base=10000.0)`：预计算 `[max_seq, dim/2]` 的 `cos`、`sin` 表，存成不进 checkpoint 的 buffer。`dim` 必须是偶数，否则抛 `ValueError`。
- `RopeCache.at(position_ids) -> (cos, sin)`：`position_ids` 是共享的 `[T]` 或每条序列各自的 `[B, T]`，返回同样前缀形状加上 `dim/2` 的表。任何位置为负或不小于 `max_seq` 时抛 `ValueError`，不静默取模。
- `position_ids_for(cache_len, q_len, batch) -> [batch, q_len]`：prefill 时 `cache_len=0` 得到 $0..T-1$；decode 时 `q_len=1` 得到 `[cache_len]`。
- `apply_rope(x, cos, sin)`：`x` 是 `[B, H, T, D]`，按相邻的偶数位、奇数位两两配对旋转；`cos`、`sin` 是 `[T, D/2]` 或 `[B, T, D/2]`，在 head 维上广播。

### 输入输出示例

```text
position_ids_for(cache_len=3, q_len=2, batch=2) -> [[3, 4], [3, 4]]
position_ids_for(cache_len=5, q_len=1, batch=1) -> [[5]]          # decode 一步
RopeCache(4, max_seq=8).at([8])                 -> ValueError     # 超出表长
```

### 解题思路与正确性

表按绝对位置索引：第 $t$ 行存的是 $\cos(t\theta_i)$、$\sin(t\theta_i)$。有 KV cache 时，本步 query 的位置从 `cache_len` 开始，所以用 `arange(cache_len, cache_len + q_len)`，而不是每步从 0 重建。

`at` 用高级索引直接得到 `[B, T, D/2]` 或 `[T, D/2]` 的角度表，`apply_rope` 在 head 维插一个长度为 1 的维度去广播。旋转后每对分量的范数不变，而且 $\langle R_m q, R_n k\rangle$ 只依赖 $m-n$，测试用这两点检查实现。

### 完整参考实现（Python 3）

```python
import torch
from torch import nn


class RopeCache(nn.Module):
    """按绝对位置预计算的 RoPE cos / sin 表，形状 [max_seq, dim / 2]。"""

    def __init__(self, dim, max_seq=4096, base=10000.0):
        super().__init__()
        if dim % 2 != 0:
            raise ValueError(f"RoPE dim must be even, got {dim}")
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))  # [D/2]
        positions = torch.arange(max_seq).float()
        freqs = torch.outer(positions, inv_freq)                              # [max_seq, D/2]
        self.register_buffer("cos", freqs.cos(), persistent=False)
        self.register_buffer("sin", freqs.sin(), persistent=False)

    def at(self, position_ids):
        """position_ids: [T] 或 [B, T]，返回同前缀形状的 (cos, sin)，最后一维 D/2。"""
        max_seq = self.cos.shape[0]
        if bool(((position_ids < 0) | (position_ids >= max_seq)).any()):
            raise ValueError(f"position_ids must be in [0, {max_seq})")
        return self.cos[position_ids], self.sin[position_ids]


def position_ids_for(cache_len, q_len, batch, device=None):
    """本步 query 的绝对位置。prefill: cache_len=0 -> 0..T-1；decode: q_len=1 -> [cache_len]。"""
    positions = torch.arange(cache_len, cache_len + q_len, device=device)
    return positions.unsqueeze(0).expand(batch, -1)  # [batch, q_len]


def apply_rope(x, cos, sin):
    """x: [B, H, T, D]；cos / sin: [T, D/2] 或 [B, T, D/2]。相邻偶奇分量成对旋转。"""
    if cos.dim() == 2:
        cos = cos[None, None, :, :]  # [1, 1, T, D/2]
        sin = sin[None, None, :, :]
    elif cos.dim() == 3:
        cos = cos[:, None, :, :]     # [B, 1, T, D/2]
        sin = sin[:, None, :, :]
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    rotated_even = x_even * cos - x_odd * sin
    rotated_odd = x_even * sin + x_odd * cos
    return torch.stack((rotated_even, rotated_odd), dim=-1).flatten(-2)
```

### 可执行测试

```python
def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)
torch.manual_seed(0)
rope = RopeCache(4, max_seq=8)

# 有 cache 时位置从 cache_len 开始
positions = position_ids_for(3, 2, 2)
assert torch.equal(positions, torch.tensor([[3, 4], [3, 4]]))
assert torch.equal(position_ids_for(5, 1, 1), torch.tensor([[5]]))

# [B, T] 的 position_ids 与逐条用 [T] 的结果一致
x = torch.randn(2, 3, 2, 4)
cos, sin = rope.at(positions)
rotated = apply_rope(x, cos, sin)
for b in range(2):
    cos_row, sin_row = rope.at(positions[b])
    assert torch.allclose(rotated[b:b + 1], apply_rope(x[b:b + 1], cos_row, sin_row))

# 位置 0 不旋转；旋转保持范数
cos0, sin0 = rope.at(torch.tensor([0, 0]))
assert torch.allclose(apply_rope(x, cos0, sin0), x)
assert torch.allclose(rotated.norm(dim=-1), x.norm(dim=-1), atol=1e-6)

# 点积只依赖相对位置：(5, 3) 与 (4, 2) 相同
q = torch.randn(1, 1, 1, 4)
k = torch.randn(1, 1, 1, 4)


def score(q_pos, k_pos):
    cos_q, sin_q = rope.at(torch.tensor([q_pos]))
    cos_k, sin_k = rope.at(torch.tensor([k_pos]))
    return (apply_rope(q, cos_q, sin_q) * apply_rope(k, cos_k, sin_k)).sum()


assert torch.allclose(score(5, 3), score(4, 2), atol=1e-6)

# 越界位置报错，不取模
expect_error(ValueError, rope.at, torch.tensor([-1]))
expect_error(ValueError, rope.at, torch.tensor([8]))

# 奇数维度报错
expect_error(ValueError, RopeCache, 3)
```

### 复杂度与追问

设表长为 $T_{\max}$、头维为 $D$、batch 为 $B$、头数为 $H$、本步长度为 $T$。建表 $O(T_{\max}D)$，查表 $O(BTD)$，旋转 $O(BHTD)$。

- 追问「为什么不能 `arange(q_len)`」：$q_{\mathrm{len}}$ 是本步 query 的个数，不是它们在序列里的下标。decode 时它永远是 $1$，位置却在一直增长。
- 追问「batch 里每条序列 `cache_len` 不同」：把 `position_ids` 做成 `[B, T]`，不要假设一个标量 $S$。连续 batching 见系统题，白板上至少要提到按行的下标。

## 题怎么来的

旋转公式见 `coding-rope`，这道题考的是工程：cos/sin 表怎么建，decode 时下标怎么取。OpenAI Transformer debug 的经典植入是 `pos = arange(q_len)`：decode 时 $q_{\mathrm{len}}=1$，于是永远旋转位置 $0$，和完整 forward 的 greedy 结果对不上，却不报错。排查方法见 `openai-rope-offset`。Meta / Apple 手写 MHA 时常会追问一句：cache 里的 $K$ 还要不要再转？

## 表：按位置预计算

头维 $D$ 是偶数。设 $\theta_i=10000^{-2i/D}$，$t=0..T_{\max}-1$：

$$
\mathrm{cos}[t,i]=\cos(t\theta_i),\quad \mathrm{sin}[t,i]=\sin(t\theta_i).
$$

表的形状是 `[max_seq, D/2]`，注册成 buffer，不进优化器。apply 时按偶奇配对（或 Llama 的 half-rotate 布局）广播到 `[B, H, T, D/2]`。索引键是绝对位置，不是「当前这段的局部 0..L」；有 KV cache 时，两者不是一回事。

prefill 时 `cache_len=0`，整段 $Q,K$ 用 $0..T-1$ 旋转，再把 $K,V$ 写进 cache。decode 时 `position_ids = cache_len`（有 left pad 或 packing 时用真实下标），只旋转当前长度为 $1$ 的 $q,k$。历史 $K$ 在写入时已经旋转过，不要对 cache 里的 $K$ 再 apply 一遍，否则角度会变成 $2t\theta$。

## packed 和越界

`position_ids` 不一定是 `arange`。left pad 时，有效 token 的位置从 pad 长度开始；文档 packing 时，每篇可能从 $0$ 重新计数，见 `coding-packed-lm`。下标 $\ge$ `max_seq` 会越界：要么建更大的表，要么用 NTK / YaRN 改 $\theta$，不要静默地 `pos % max_seq`。GQA 下 RoPE 仍按头维 $D$ 旋转，和 $H_{\mathrm{kv}}$ 无关，见 `coding-gqa-repeat`。

不变量：在同一前缀上，逐步 decode 和一次完整 forward 的 greedy 下一个 token 相同。对不上时先打印 `position_ids`，再去怀疑 kernel。

## 追问

- **$V$ 要不要用 cos 表旋转？** 不要。RoPE 不旋转 $V$，cache 里的 $V$ 就是内容本身。
- **cos 表要不要和权重一起存进 checkpoint？** 不必，它由 `dim, base, max_seq` 重算即可。但为长上下文换 base 时，必须和训练时一致。

## 相关题

- [[openai-rope-offset]]：同一个不变量的排查版：decode 位置写成 0 不报错，要靠有/无 cache 的 greedy 对齐才发现。
- [[openai-kv-cache-impl]]：从零写 NumPy 版 KV cache 的完整题，RoPE 从 `prefix` 起算只是其中一条约束。
- [[openai-transformer-debug]]：给一份带 bug 的 Transformer 先排查再加 cache，位置偏移是它五类 bug 之一。
- [[kv-prefix-transformer]]：多层 Transformer 上做前缀复用，后缀的 RoPE 位置从前缀长度起算，验收分块 prefill 一致。
- [[openai-attention-sink]]：滑窗驱逐 KV 后也不能重写位置编号，和这里按绝对位置查表是同一条规矩。
- [[coding-rope]]：只写旋转本身：偶数维成对旋转，decode 位置取 cache 长度。
