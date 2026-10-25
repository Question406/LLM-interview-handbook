---
id: code-linear-attn
section: coding
order: 26
level: A
title: 手写 causal linear attention：并行形式和 O(1) 状态递推要对上
quick: "把 softmax 换成非负核 $\\phi(q)^\\top\\phi(k)$，靠结合律把历史累加成 $S_t=\\sum\\phi(k)v^\\top$ 和 $z_t=\\sum\\phi(k)$。decode 时只更新这两个量，输出 $\\phi(q)^\\top S_t/\\phi(q)^\\top z_t$，状态大小和序列长度无关；训练用的并行形式和这个递推要数值一致。"
tags:
  - Linear Attention
  - RNN
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Transformers are RNNs: Fast Autoregressive Transformers with Linear Attention"
    url: https://arxiv.org/abs/2006.16236
    type: primary
---

## 题目描述

实现采用正值特征映射的因果线性注意力，并让全段与逐 token 接口计算同一个结果。本题的注意力定义不是通常的 softmax attention。

### 数学语义与接口

特征映射 `phi(x)` 定义为逐元素 `ELU(x)+1`。对序列位置 t，只允许使用位置 s<=t；其未归一化权重为映射后的 `q_t` 与 `k_s` 的内积。输出为这些权重对 `v_s` 的加权和，除以权重总和加 eps。

- `linear_attn_masked(q,k,v,eps)` 和 `linear_attn_cumsum(q,k,v,eps)`：q、k 为 `[B,H,T,Dk]`，v 为 `[B,H,T,Dv]`，返回 `[B,H,T,Dv]`。
- `linear_attn_step(q_t,k_t,v_t,S,z,eps)`：当前 q/k 为 `[B,H,Dk]`，v 为 `[B,H,Dv]`。S 是此前各位置映射后的 k 与 v 外积的总和 `[B,H,Dk,Dv]`，z 是此前映射后的 k 总和 `[B,H,Dk]`。返回当前输出与纳入当前 token 后的新 S、z。

eps 为正数，首次逐 token 调用使用全零状态。三个接口应在浮点容差内一致；不需要进行模型训练。

### 示例

```text
B=H=Dk=Dv=1，q和k的两个序列值均为0，v=[2,4]，eps=1e-6
全段输出约为[2/(1+eps), 6/(2+eps)]
从全零S、z逐token调用，得到同一序列输出
```

## 解题思路与参考答案

Causal linear attention 把 softmax 换成非负核 $\phi(q)^\top\phi(k)$，再用结合律把全部历史压成两个累加量 $S_t$ 和 $z_t$。训练时按并行形式算，逐 token 生成（decode）时按递推形式一步步更新状态，面试官要看的就是同一个模型能写成这两种形式，而且两边算出来数值一致。softmax 版本的写法见 `code-attention`。

写的时候最容易错两处。一处是算完 $\phi(Q)\phi(K)^\top$ 又套了一层 softmax，那就回到了普通 attention。另一处是只写分子 $\sum\phi(q)^\top\phi(k)v$，漏了分母归一化 $\sum\phi(q)^\top\phi(k)$，输出的尺度会随序列长度变。

第 $t$ 个位置的输出是

$$
o_t=\frac{\phi(q_t)^\top\sum_{j\le t}\phi(k_j)v_j^\top}{\phi(q_t)^\top\sum_{j\le t}\phi(k_j)}
=\frac{\phi(q_t)^\top S_t}{\phi(q_t)^\top z_t},\quad
S_t=S_{t-1}+\phi(k_t)v_t^\top,\ z_t=z_{t-1}+\phi(k_t)
$$

能这么写靠的是结合律：先算 $\phi(K)^\top V$ 这个 $[d_k,d_v]$ 的小矩阵，就用不着算 $[T,T]$ 的矩阵。因果注意力只能累加当前位置及之前的项，所以要用前缀和，前缀和自然就能写成逐步更新状态的递推。下面三个函数分别是只用来对拍的 $O(T^2)$ masked 版本、cumsum 并行版本和单步递推版本：

```python
import torch
import torch.nn.functional as F

def phi(x):
    return F.elu(x) + 1                                          # > 0, keeps denominator positive

def linear_attn_masked(q, k, v, eps=1e-6):
    # q,k: [B,H,T,Dk], v: [B,H,T,Dv]; O(T^2), for checking only
    q, k = phi(q), phi(k)
    T = q.shape[2]
    a = q @ k.transpose(-2, -1)                                  # [B,H,T,T], no softmax
    a = a.masked_fill(~torch.tril(torch.ones(T, T, dtype=torch.bool, device=q.device)), 0.0)
    return (a @ v) / (a.sum(-1, keepdim=True) + eps)

def linear_attn_cumsum(q, k, v, eps=1e-6):
    q, k = phi(q), phi(k)
    S = torch.einsum("bhtd,bhte->bhtde", k, v).cumsum(2)         # [B,H,T,Dk,Dv]
    z = k.cumsum(2)                                              # [B,H,T,Dk]
    num = torch.einsum("bhtd,bhtde->bhte", q, S)
    den = (q * z).sum(-1, keepdim=True)
    return num / (den + eps)

def linear_attn_step(q_t, k_t, v_t, S, z, eps=1e-6):
    # q_t,k_t: [B,H,Dk], v_t: [B,H,Dv], S: [B,H,Dk,Dv], z: [B,H,Dk]
    q_t, k_t = phi(q_t), phi(k_t)
    S = S + k_t[..., :, None] * v_t[..., None, :]
    z = z + k_t
    num = torch.einsum("bhd,bhde->bhe", q_t, S)
    den = (q_t * z).sum(-1, keepdim=True)
    return num / (den + eps), S, z
```

decode 时从 `S = zeros(B,H,Dk,Dv)`、`z = zeros(B,H,Dk)` 开始，每来一个 token 就调用一次 `linear_attn_step`。

## 和 KV cache 对比

softmax attention 做 decode 要把所有历史的 $k,v$ 存下来（见 `arch-kv-cache`），第 $t$ 步要读 $O(td)$ 的 cache，显存随长度线性涨。linear attention 把全部历史压进 $S_t$ 和 $z_t$，每层每头只有 $d_k d_v+d_k$ 个数，和 $t$ 无关，每步的计算量也是常数。代价在表达力上：固定大小的状态没法像 softmax 那样精确回看任意一个旧 token，长上下文检索这类任务通常会更弱。

`linear_attn_cumsum` 把整个 $[B,H,T,D_k,D_v]$ 都物化了，T 一长显存就吃不消，所以实际训练用 chunk 形式：块内用 masked 矩阵乘，块间传递状态 $S$。Mamba、RetNet 走的也是"训练可并行、推理是固定大小状态的递推"这个思路，区别在状态的更新规则，比如 RetNet 会给状态乘一个衰减因子，这里不展开。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用同一组小张量比较显式因果矩阵、cumsum 与逐 token 状态更新三种接口。它们都计算相同的特征映射注意力，不能拿 softmax attention 当标准答案。

```python
torch.manual_seed(7)
q, k, v = [torch.randn(1, 1, 3, 2) for _ in range(3)]
expected = linear_attn_masked(q, k, v)
torch.testing.assert_close(linear_attn_cumsum(q, k, v), expected)
S, z = torch.zeros(1, 1, 2, 2), torch.zeros(1, 1, 2)
outputs = []
for t in range(3):
    out, S, z = linear_attn_step(q[:, :, t], k[:, :, t], v[:, :, t], S, z)
    outputs.append(out)
torch.testing.assert_close(torch.stack(outputs, dim=2), expected)
print("simple tests passed")
```

## 追问

**$\phi$ 为什么必须非负？**
分母 $\phi(q)^\top z$ 是注意力权重之和，权重得非负，否则分母可能接近 0 甚至变号，数值就不稳了。$\mathrm{elu}+1$ 恒大于 0，梯度也不会像 ReLU 那样在负半轴变成 0。

**复杂度是多少？**
并行 masked 形式是 $O(T^2d)$，递推或 chunk 形式是 $O(Td_kd_v)$。$T\gg d$ 时才划算。

**直接去掉 softmax、不加 $\phi$ 行不行？**
不行。$q^\top k$ 可以是负数，权重和可能为 0，归一化就没有意义了。

**训练时也用递推形式可以吗？**
能算对，但要按时间步串行，GPU 利用率很低。所以训练用并行或 chunk 形式，推理用递推，两者数学上等价。

**linear attention 能和 KV cache 共存吗？**
能。有些混合架构一部分层用 softmax attention、带 KV cache，另一部分层用线性或状态空间层，在显存和长程检索能力之间折中。
