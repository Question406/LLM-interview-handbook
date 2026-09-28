---
id: code-moe-permute-combine
section: coding
order: 18
level: S
title: 手写 MoE permute / combine：按专家聚 token，算完再按门控加回
quick: >-
  把 $[T,k]$ 的 expert id 展平，按专家排序后 gather hidden，得到每专家一段连续 $X_i$。算完 MLP 用同一套逆序
  scatter，按 gates 加权 `index_add` 回 $[T,d]$。不要 for-token 调专家；也不要在 combine 前把门控漏乘。
tags:
  - MoE
  - Permute
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
---

Router 只给出「谁、多重」。真正把矩阵乘喂饱的是一次按专家重排。现场允许伪代码，但必须能说清：展平 → 排序 → 分段 GEMM → 逆重排加权。形状错了后面 Grouped GEMM 全废，见 `sys-moe-grouped-gemm`。

## 形状

token 矩阵 $x\in\mathbb{R}^{T\times d}$。Router 得到

- `expert_idx`: $[T,k]$，每个 token 的专家下标；
- `gates`: $[T,k]$，已在选中集合上归一，行和为 $1$。

展平后有 $Tk$ 条「token-专家」记录。Permute 不改变这 $Tk$ 条的内容，只改变顺序，让同一专家的记录相邻。Combine 把 $Tk$ 条输出按原 token 下标加回去。

Top-$k$ 不可导，梯度只走 `gates` 和被选中专家的 MLP。未选中专家这一步没有 token 梯度；aux / bias 是另一条路，见 `code-moe-router-aux-loss`。

## 手写

```python
import torch

def moe_permute_combine(x, expert_idx, gates, n_experts, expert_fn):
    # x: [T, d], expert_idx: [T, k], gates: [T, k]
    T, k = expert_idx.shape
    tok = torch.arange(T, device=x.device).unsqueeze(1).expand(T, k).reshape(-1)
    eid = expert_idx.reshape(-1)
    hidden = x[tok]              # [T*k, d]
    g = gates.reshape(-1)

    order = torch.argsort(eid, stable=True)
    eid_s, hidden_s, g_s, tok_s = eid[order], hidden[order], g[order], tok[order]
    counts = torch.bincount(eid_s, minlength=n_experts)

    out_s = hidden_s.new_empty(hidden_s.shape)
    offset = 0
    for i in range(n_experts):
        n_i = int(counts[i].item())
        if n_i == 0:
            continue
        out_s[offset:offset + n_i] = expert_fn(i, hidden_s[offset:offset + n_i])
        offset += n_i

    y = x.new_zeros(T, x.shape[-1])
    y.index_add_(0, tok_s, out_s * g_s.unsqueeze(-1))
    return y
```

`expert_fn(i, chunk)` 是专家 $i$ 的 MLP，输入输出都是 `[n_i, d]`。生产里这段循环换成 grouped GEMM；面试保留循环，但要说「循环在专家维，不在 token 维」。

`stable=True` 让同分专家的 token 顺序确定，便于对照数值。`bincount` 得到每专家长度，空专家必须跳过，不要喂 $0$ 行 GEMM。

## 易错点

- Combine 用 `scatter` 而不是 `index_add`：$k\gt 1$ 时同一 token 有多条记录，`scatter` 会覆盖，只留下最后一个专家。
- 先加再乘门控：必须 `out * g` 再累加。漏乘等于每个选中专家权重为 $1$，和 router 无关。
- 用 `x` 的原序去切专家：不 permute 就只能 `x[mask]` 每次拷一块，等价于 $N$ 次随机 gather，带宽更差。
- Capacity：真正带 drop 时，在排序后对每个专家截断前 $C$ 条，被丢掉的记录不进 `expert_fn`、不进 `index_add`，见 `sys-moe-capacity-token-drop`。本题默认 dropless。

## 追问

- **逆 permute 存什么？** 存 `order` 或 `tok_s`。只存 counts 不够，因为还要把输出写回原 token 行。
- **Shared expert？** 另算 `y = y + shared(x)`，不进这张表。
- **测什么？** $k=1$、$N=1$ 时应等于 `gates * expert_fn(0, x)`。构造两个 token 指向不同专家，确认不会串行。再令 $k=2$、gates 为 $(0.7,0.3)$，输出应是两路加权和。
- **和 all-to-all？** 多卡时 permute 在 dispatch 之后、本卡本地做。先按目的 rank 通信，再按本地专家 id 排序。
