---
id: code-moe-sparse-forward
section: coding
order: 19
level: S
title: 手写 Mixtral 风格稀疏 MoE 层：logits → Top-$k$ → 截断 softmax → permute → 专家 → combine
quick: >-
  `logits = x @ W_g`，对 logits 做 Top-$k$（不是对 softmax），`gates = softmax(val)`，再
  permute 进各专家 MLP，`index_add` 加权合回。$k=2$、$N=8$ 时就是 Mixtral 的 FFN 替换。别先全量
  softmax 再取 Top-$k$ 当权重。
tags:
  - MoE
  - Mixtral
  - Coding
  - Router
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
---

把 `arch-moe-gating-softmax-sigmoid` 和 `code-moe-permute-combine` 收成一层可运行前向。白板要能从 $x$ 写到 $y$，中间不跳形状。专家内部用线性代替完整 SwiGLU 即可，面试口头补「生产是 `silu(xW1)*xW2` 再 down」，见 `code-swiglu`。

## 一层前向

$$
z=xW_g,\quad
(v,\mathcal{E})=\mathrm{TopK}(z,k),\quad
G=\mathrm{softmax}(v),\quad
y=\sum_{j=1}^{k}G_{:,j}\,E_{\mathcal{E}_{:,j}}(x).
$$

$W_g\in\mathbb{R}^{d\times N}$。`softmax` 只作用在选出的 $k$ 维上，所以 `G.sum(-1)==1`。Switch 风格 aux 若要写，用全量 `softmax(z)` 的 $P$ 去乘频率 $f$，不要用截断后的 $G$ 冒充 $P$，见 `code-moe-router-aux-loss`。

## 手写

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
        self.experts = nn.ModuleList([nn.Linear(d, d, bias=False) for _ in range(n_experts)])

    def forward(self, x):
        # x: [T, d]  ->  [T, d]
        logits = self.W_g(x)
        val, idx = torch.topk(logits, self.k, dim=-1)
        gates = F.softmax(val, dim=-1)

        T = x.shape[0]
        tok = torch.arange(T, device=x.device).unsqueeze(1).expand(T, self.k).reshape(-1)
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
            out_s[offset:offset + n_i] = expert(hidden_s[offset:offset + n_i])
            offset += n_i

        y = x.new_zeros(x.shape)
        y.index_add_(0, tok_s, out_s * g_s.unsqueeze(-1))
        return y
```

`nn.Linear(d, n_experts)` 就是 $W_g$。生产常把专家做成 SwiGLU 三矩阵；本题用方阵只为让形状闭合。$k$ 必须 $\le N$。

## 和 DeepSeek 路径差三行

V3：`scores = sigmoid(x @ E.T)`，`idx = topk(scores + bias)`，`gates = normalize(scores.gather(..., idx))`。不要把 bias 加进 `gates`。Shared 则 `y = y + shared(x)`。面试能改这三行，说明门控和 permute 已经拆开。

## 追问

- **先 `softmax(logits)` 再 `topk`？** Mixtral 不是。那样 `gates` 行和小于 $1$，层输出被缩小。若题目明确 Switch Top-$1$，才用 $P_{i^\star}$ 不当成 $1$。
- **专家权重 `[N, d, d]` 一次 einsum？** 小 $N$ 可以 `einsum('te,ted->td')` 配 one-hot，大 $N$ 会把未选专家也乘进去。稀疏路径必须 permute。
- **数值测什么？** $N=k=1$ 时等于那一个 Linear。再固定 `idx` 全 $0$、`gates` 全 $1$，应等于 `experts[0](x)`。
- **Dropout / 训练噪声？** Mixtral 论文不开 aux；若加 jitter，只加在训练期的 logits 上，推理关掉。
