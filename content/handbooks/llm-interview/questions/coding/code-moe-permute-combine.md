---
id: code-moe-permute-combine
section: coding
order: 18
level: S
title: 手写 MoE permute / combine：按专家聚 token，算完再按门控加回
quick: >-
  把 $[T,k]$ 的 expert id 展平，按专家排序后 gather hidden，每个专家拿到一段连续的 $X_i$；MLP 算完用同一套顺序逆回去，按 gates 加权 `index_add` 回 $[T,d]$。循环放在专家维，别按 token 一个个调专家，combine 前也别漏乘门控。
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

## 题目描述

给定已经决定好的专家路由和门控权重，执行一层稀疏 MoE 的专家计算，并把输出还原到原 token 顺序。本题不计算 router logits 或 top-k 选择。

### 接口与形状

`moe_permute_combine(x,expert_idx,gates,n_experts,expert_fn)` 中 x 为 `[T,d]`，`expert_idx` 为 `[T,k]` 的专家编号，gates 为同形状浮点权重，专家编号在 0 到 `n_experts`-1 内。`expert_fn(i,rows)` 接收分配给专家 i 的若干行 `[Ni,d]`，返回同形状结果。

输出 y 为 `[T,d]`，每个 token 的结果等于它被分配到的 k 个专家输出按对应 gate 加权相加；不能把不同 token 的贡献混在一起。允许某些专家没有收到 token；这不应改变其他 token 的结果。输入形状和权重均合法。

### 示例

```text
x=[[1,2],[3,4]]
expert_idx=[[0,1],[1,0]]
gates=[[0.25,0.75],[0.5,0.5]]，n_experts=3
专家0返回输入本身，专家1返回输入的2倍
输出 -> [[1.75,3.5],[4.5,6.0]]
```

专家2没有收到任何 token。该例仍必须得到相同结果，而不是为它虚构输入。

## 解题思路与参考答案

我会按「展平 → 按专家排序 → 分段算专家 → 逆重排加权加回」这四步写。Router 只给出每个 token 选了哪些专家、权重是多少，要先按专家把记录重排，同一专家的输入才能集中起来做一次矩阵乘法。现场允许伪代码，但这条链路要讲清楚，形状错了，后面的 Grouped GEMM 就没法正确执行，见 `sys-moe-grouped-gemm`。

## 形状

token 矩阵 $x\in\mathbb{R}^{T\times d}$。Router 得到

- `expert_idx`: $[T,k]$，每个 token 的专家下标；
- `gates`: $[T,k]$，已在选中集合上归一，行和为 $1$。

展平后有 $Tk$ 条「token-专家」记录。比如 $k=2$ 时，每个 token 会变成两条记录，分别指向它选中的两个专家。Permute 只改这 $Tk$ 条记录的顺序，让同一专家的记录相邻，内容不变；Combine 再把 $Tk$ 条输出按原 token 下标加回去。

Top-$k$ 不可导，梯度只走 `gates` 和被选中专家的 MLP。没被选中的专家这一步拿不到 token 梯度；aux 或 bias 是另一条路，见 `code-moe-router-aux-loss`。

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

`expert_fn(i, chunk)` 是专家 $i$ 的 MLP，输入输出都是 `[n_i, d]`。生产里这段循环会换成 grouped GEMM；面试时保留循环没问题，但要说明循环在专家维上，不在 token 维上。

`stable=True` 让同一个专家内部的 token 顺序确定，方便对照数值。`bincount` 给出每个专家分到的长度，空专家要跳过，别喂 $0$ 行的 GEMM。

最容易写错的是 combine。用 `scatter` 代替 `index_add` 的话，$k\gt 1$ 时同一个 token 有多条记录，`scatter` 会覆盖，只留下最后一个专家的输出。门控也要先乘再加，`out * g` 之后再累加；漏乘就等于每个选中专家的权重都是 $1$，和 router 算出来的权重无关。如果不做 permute，直接用 `x` 的原始顺序去切专家，就只能每次 `x[mask]` 拷一块出来，相当于 $N$ 次随机 gather，带宽更差。

真正带 capacity 和 drop 的时候，在排序之后对每个专家只保留前 $C$ 条，被丢掉的记录既不进 `expert_fn`，也不进 `index_add`，见 `sys-moe-capacity-token-drop`。本题默认 dropless。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两个 token 都路由到两个专家，专家 0 乘 1、专家 1 乘 2。用不同 gates 手算得到 [1.75,3.5] 和 [4.5,6]；留一个空专家，覆盖零负载分支。

```python
x = torch.tensor([[1., 2.], [3., 4.]])
idx = torch.tensor([[0, 1], [1, 0]])
gates = torch.tensor([[0.25, 0.75], [0.5, 0.5]])
out = moe_permute_combine(x, idx, gates, 3, lambda expert, rows: (expert + 1) * rows)
torch.testing.assert_close(out, torch.tensor([[1.75, 3.5], [4.5, 6.]]))
print("simple tests passed")
```

## 追问

**逆 permute 需要存什么？**
存 `order` 或 `tok_s`。只存 counts 不够，还得知道每条输出该写回哪一行 token。

**Shared expert 怎么加？**
单独算，`y = y + shared(x)`，不进这张排序表。

**怎么测？**
$k=1$、$N=1$ 时，输出应该等于 `gates * expert_fn(0, x)`。再构造两个 token 指向不同专家，确认结果不会串行。最后令 $k=2$、gates 为 $(0.7,0.3)$，输出应该是两路的加权和。

**多卡 all-to-all 时 permute 放在哪？**
放在 dispatch 之后，在本卡本地做。先按目的 rank 通信，再按本地专家 id 排序。
