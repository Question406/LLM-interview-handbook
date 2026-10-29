---
id: code-moe-sparse-forward
section: coding
order: 19
level: S
title: 手写 Mixtral 风格稀疏 MoE 层：logits → Top-$k$ → 截断 softmax → permute → 专家 → combine
quick: >-
  `logits = x @ W_g`，直接对 logits 做 Top-$k$，再 `gates = softmax(val)`，然后 permute
  进各专家 MLP，`index_add` 加权合回。$k=2$、$N=8$ 时就是 Mixtral 替换 FFN 的那一层。先全量 softmax 再取
  Top-$k$ 当权重是错的，行和会小于 1。
tags:
  - MoE
  - Mixtral
  - Coding
  - Router
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Mixtral of Experts
    url: 'https://arxiv.org/abs/2401.04088'
    type: primary
---

## 题目描述

实现一个小型稀疏 MoE 模块 `SparseMoE(d,n_experts,k=2)`。它接收 T 个 d 维 token 表示，为每个 token 选择 k 个专家，最后返回与输入相同形状的结果。

### 输入输出与模块语义

`forward(x)` 的 x 为 `[T,d]`，`1 <= k <= n_experts`。router 是不带 bias 的线性层 `W_g: d -> n_experts`，每个专家是不带 bias 的 `d -> d` 线性层。对每个 token 取 router logits 最大的 k 个专家，只在这些被选 logits 上形成和为 1 的 softmax 权重；输出是被选专家对该 token 的结果按该权重加权之和。

返回 `[T,d]`，行顺序必须与 x 一致，保留 autograd。没有收到 token 的专家可以不执行；本练习没有容量截断、溢出丢弃或额外辅助损失。平票不要求固定专家顺序，只需与当前框架的 top-k 结果一致。

### 示例

```text
T=2,d=2,n_experts=3,k=2
x=[[1,2],[-1,3]]，所有专家权重都设置为2×2单位矩阵
无论router选中哪两个专家，forward(x) -> [[1,2],[-1,3]]
```

本卡是手册重构的 CPU 计算练习，不要求实现多设备专家通信。

## 解题思路与参考答案

Mixtral 风格的稀疏 MoE 层是这样一条链：`x @ W_g` 得到 logits，对 logits 取 Top-$k$，只在这 $k$ 个值上做 softmax 当 gating，然后把 token permute 到各自的专家，算完按 gating 加权合回。这题就是把 `arch-moe-gating-softmax-sigmoid` 和 `code-moe-permute-combine` 收成一层能跑的前向，白板上要能从 $x$ 一路写到 $y$，中间不跳形状。专家内部用一个线性层代替完整的 SwiGLU 就行，口头补一句「生产里是 `silu(xW1)*xW2` 再 down」，见 `code-swiglu`。

$$
z=xW_g,\quad
(v,\mathcal{E})=\mathrm{TopK}(z,k),\quad
G=\mathrm{softmax}(v),\quad
y=\sum_{j=1}^{k}G_{:,j}\,E_{\mathcal{E}_{:,j}}(x).
$$

$W_g\in\mathbb{R}^{d\times N}$。`softmax` 只作用在选出来的 $k$ 维上，所以 `G.sum(-1)==1`。如果还要写 Switch 风格的 aux，用全量 `softmax(z)` 得到的 $P$ 去乘频率 $f$，别拿截断后的 $G$ 冒充 $P$，见 `code-moe-router-aux-loss`。

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class SparseMoE(nn.Module):
    def __init__(self, d, n_experts, k=2):
        super().__init__()
        self.k = k
        self.n_experts = n_experts
        self.W_g = nn.Linear(d, n_experts, bias=False)
        self.experts = nn.ModuleList(
            [nn.Linear(d, d, bias=False) for _ in range(n_experts)]
        )

    def forward(self, x):
        # x: [T, d]  ->  [T, d]
        logits = self.W_g(x)
        val, idx = torch.topk(logits, self.k, dim=-1)
        gates = F.softmax(val, dim=-1)

        T = x.shape[0]
        tok = (
            torch.arange(T, device=x.device).unsqueeze(1).expand(T, self.k).reshape(-1)
        )
        eid = idx.reshape(-1)
        hidden = x[tok]
        g = gates.reshape(-1)

        order = torch.argsort(eid, stable=True)
        eid_s, hidden_s, g_s, tok_s = eid[order], hidden[order], g[order], tok[order]
        counts = torch.bincount(eid_s, minlength=self.n_experts)

        out_s = hidden_s.new_empty(hidden_s.shape)
        offset = 0
        for i, expert in enumerate(self.experts):
            n_i = int(counts[i].item())
            if n_i == 0:
                continue
            out_s[offset : offset + n_i] = expert(hidden_s[offset : offset + n_i])
            offset += n_i

        y = x.new_zeros(x.shape)
        y.index_add_(0, tok_s, out_s * g_s.unsqueeze(-1))
        return y
```

`nn.Linear(d, n_experts)` 就是 $W_g$。生产里专家常做成 SwiGLU 的三个矩阵，这里用方阵只是为了让形状闭合。$k$ 必须 $\le N$。

## 换成 DeepSeek 只改三行

V3 的路径是 `scores = sigmoid(x @ E.T)`，`idx = topk(scores + bias)`，`gates = normalize(scores.gather(..., idx))`。bias 只用来选专家，别加进 `gates`。有 shared expert 的话再 `y = y + shared(x)`。能顺手改出这三行，说明 gating 和 permute 已经拆干净了。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

把所有专家设为单位矩阵，则不论 router 选择谁，加权 normalization 后的输出都应等于输入；再用逐 token、逐专家的朴素循环对照非相同专家，覆盖分组和合并。

```python
torch.manual_seed(7)
model = SparseMoE(2, n_experts=3, k=2)
x = torch.tensor([[1.0, 2.0], [-1.0, 3.0]])
with torch.no_grad():
    for expert in model.experts:
        expert.weight.copy_(torch.eye(2))
torch.testing.assert_close(model(x), x)
with torch.no_grad():
    for i, expert in enumerate(model.experts):
        expert.weight.mul_(i + 1)
values, indices = model.W_g(x).topk(2, dim=-1)
gates = values.softmax(-1)
expected = torch.stack(
    [
        sum(gates[t, j] * model.experts[int(indices[t, j])](x[t]) for j in range(2))
        for t in range(len(x))
    ]
)
torch.testing.assert_close(model(x), expected)
print("simple tests passed")
```

## 追问

**先 `softmax(logits)` 再 `topk` 行不行？**
Mixtral 不是这么做的。那样 `gates` 的行和小于 $1$，层输出会被整体缩小。只有题目明确是 Switch Top-$1$ 时，才用 $P_{i^\star}$，不把它当成 $1$。

**专家权重存成 `[N, d, d]`，一次 einsum 算完可以吗？**
$N$ 小的时候可以配 one-hot 用 `einsum('te,ted->td')`，$N$ 大了会把没选中的专家也乘进去。走稀疏路径就得 permute。

**数值上测什么？**
$N=k=1$ 时应该等于那一个 Linear。再固定 `idx` 全为 $0$、`gates` 全为 $1$，结果应该等于 `experts[0](x)`。

**Dropout 和训练噪声怎么处理？**
Mixtral 论文没开 aux。如果加 jitter，只加在训练期的 logits 上，推理时关掉。
