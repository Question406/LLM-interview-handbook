---
id: code-tp-linear
section: coding
order: 35
level: S
title: 手写 Megatron 张量并行：Column / Row Parallel Linear 与一次 all-reduce 的 MLP
quick: >-
  ColumnParallelLinear 按输出维切 $W$，每个 rank 算出一段输出，要完整结果时才 all-gather；RowParallelLinear 按输入维切 $W$，每个 rank 拿到部分和，all-reduce 之后 bias 只加一次。MLP 用 column 接 row，中间激活逐元素算、不用通信，前向只有一次 all-reduce；attention 按 head 切也是一样。
tags:
  - Tensor Parallel
  - Megatron
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism"
    url: https://arxiv.org/abs/1909.08053
    type: primary
---

## 题目描述

在单个 Python 进程里模拟张量并行，验证分片计算与未分片计算的结果一致。每个 rank 的数据用一个列表元素表示，不需要启动进程组或 GPU 通信。

### 接口与约定

所有线性层权重 W 使用 `[out,in]` 布局，未分片基准为 `x @ W.T + b`。

- `all_reduce(xs)`：xs 包含 world 个同形状张量，返回 world 份各输入逐元素之和；`all_gather(xs,dim=-1)` 返回 world 份按 rank 顺序沿 dim 拼接的张量。
- `ColumnParallelLinear(W,b,world,gather_output=False)`：实例通过 `__call__(xs)` 调用；xs 是长度为 world 的张量列表，每个元素均为相同的完整输入 `[... ,in]`。返回长度为 world 的列表，默认每个 rank 按输出特征分得一个结果切片；`gather_output`=True 时，每个元素均为拼回的完整结果。
- `RowParallelLinear(W,b,world)`：实例通过 `__call__(xs)` 调用；xs 是长度为 world 的张量列表，xs[r] 是按 rank 顺序分配的输入特征切片 `[... ,in/world]`。返回长度为 world 的列表，每个元素都等于未分片线性层的完整输出；bias 只能贡献一次。
- `ParallelMLP(W1,b1,W2,b2,world)`：实例通过 `__call__(x)` 调用，x 是单个完整输入张量 `[... ,in]`；返回长度为 world 的列表，各 rank 的结果相同，数学语义为两层线性变换之间使用 GELU。
- `parallel_attention(x,Wq,Wk,Wv,Wo,n_heads,world)` 模拟按头分片的因果自注意力，返回每个 rank 的完整 `[B,T,d]` 输出。

相应输入/输出维度及头数都能整除 world，参数形状保证合法。

### 示例

```text
x=[[1,2]], W=[[1,2],[3,4]], b=[5,6], world=2
未分片完整输出 -> [[10,17]]
列并行并gather后，每个rank -> [[10,17]]
行并行输入分别为[[1]]和[[2]]，每个rank -> [[10,17]]
```

## 解题思路与参考答案

张量并行要讲清三件事：切哪一维、每个 rank 手里是完整值还是部分和、哪里必须通信。Column 按输出维切，每人拿一段完整的输出；Row 按输入维切，每人拿一份部分和，all-reduce 之后再加 bias。MLP 用 column 接 row，前向只要一次 all-reduce。

常见错法有两个。一个是 RowParallel 里每个 rank 都加一遍 bias，all-reduce 后 bias 变成 world_size 倍；另一个是 MLP 两层都按列切，中间得先 all-gather 再重新切，平白多一次通信。原理和显存账见 `infra-megatron-mlp-tp`、`sys-parallel`，这里只写代码。

## 单进程模拟

不需要 `torch.distributed`，用长度为 world_size 的 list 表示各个 rank 的张量就行：`all_reduce` 就是求和后每人一份，`all_gather` 就是沿切分维 `cat`。`nn.Linear` 的权重是 `[out, in]`，所以 column 切 `dim=0`，row 切 `dim=1`。

```python
import torch
import torch.nn.functional as F

def all_reduce(xs):
    s = torch.stack(xs).sum(0)
    return [s.clone() for _ in xs]

def all_gather(xs, dim=-1):
    y = torch.cat(xs, dim=dim)
    return [y.clone() for _ in xs]

class ColumnParallelLinear:
    def __init__(self, W, b, world, gather_output=False):
        assert W.shape[0] % world == 0
        self.W = list(W.chunk(world, dim=0))    # 每份 [out/world, in]
        self.b = list(b.chunk(world, dim=0))    # bias 跟着输出维切
        self.gather = gather_output
    def __call__(self, xs):                     # xs[r]: 完整输入 [..., in]
        ys = [x @ w.T + b for x, w, b in zip(xs, self.W, self.b)]  # [..., out/world]
        return all_gather(ys) if self.gather else ys

class RowParallelLinear:
    def __init__(self, W, b, world):
        assert W.shape[1] % world == 0
        self.W = list(W.chunk(world, dim=1))    # 每份 [out, in/world]
        self.b = b                              # 不切，只在 reduce 之后加一次
    def __call__(self, xs):                     # xs[r]: 已切好的输入 [..., in/world]
        partial = [x @ w.T for x, w in zip(xs, self.W)]            # 部分和 [..., out]
        return [y + self.b for y in all_reduce(partial)]

class ParallelMLP:
    def __init__(self, W1, b1, W2, b2, world):
        self.world = world
        self.fc1 = ColumnParallelLinear(W1, b1, world)
        self.fc2 = RowParallelLinear(W2, b2, world)
    def __call__(self, x):
        xs = [x] * self.world                   # f：前向 identity
        h = [F.gelu(y) for y in self.fc1(xs)]   # 逐元素激活，在切片上直接算
        return self.fc2(h)                      # g：前向唯一一次 all-reduce

def parallel_attention(x, Wq, Wk, Wv, Wo, n_heads, world):
    # x: [B, T, d]；W*: [d, d]；每个 rank 拿 n_heads/world 个 head
    B, T, d = x.shape
    hd, hr = d // n_heads, n_heads // world
    outs = []
    for r in range(world):
        sl = slice(r * hr * hd, (r + 1) * hr * hd)
        q, k, v = [(x @ W[sl].T).view(B, T, hr, hd).transpose(1, 2) for W in (Wq, Wk, Wv)]
        o = F.scaled_dot_product_attention(q, k, v, is_causal=True)  # [B, hr, T, hd]
        o = o.transpose(1, 2).reshape(B, T, hr * hd)
        outs.append(o @ Wo[:, sl].T)            # Wo 按输入维切，得到部分和
    return all_reduce(outs)
```

## 为什么是 column 接 row

MLP 是 $Y=\mathrm{GeLU}(XA)B$。把 $A$ 按列切成 $[A_1,\dots,A_p]$，每个 rank 算 $\mathrm{GeLU}(XA_i)$；GeLU 是逐元素的，在切片上算和先拼起来再算结果一样。要是 $A$ 按行切，$XA$ 就成了部分和，GeLU 没法作用在部分和上（$\mathrm{GeLU}(a+b)\ne \mathrm{GeLU}(a)+\mathrm{GeLU}(b)$），得先 all-reduce。第二层 $B$ 按行切，正好接住按列切好的 $\mathrm{GeLU}(XA_i)$，输出 $\sum_i \mathrm{GeLU}(XA_i)B_i$，一次 all-reduce 就完事。SwiGLU 版本（见 `code-swiglu`）把 gate 和 up 两个投影都按列切，同一个 rank 拿对应的列，逐元素相乘也不用通信。

Attention 是同一个道理。$W_Q,W_K,W_V$ 按 head 切，本质上就是 column parallel，每个 rank 独立算自己那几个 head 的 softmax；$W_O$ 按输入维切成 row parallel，最后一次 all-reduce。所以一个 Transformer 层前向 2 次 all-reduce，反向也是 2 次。前提是 head 数和 FFN 隐维都能被 world_size 整除。

反向靠论文里的 $f$、$g$ 两个共轭算子。$f$ 放在 column 层之前，前向 identity，反向 all-reduce，因为每个 rank 对 $X$ 的梯度只是自己那片权重贡献的部分和；$g$ 放在 row 层之后，前向 all-reduce，反向 identity，因为输出梯度每个 rank 都是完整的，直接往下传。真实实现里这两个写成 `autograd.Function`。

## 简单测试怎么写

把参考实现与以下测试按顺序放进 solution.py，运行 python3 solution.py。数值测试使用同一 PyTorch 环境，浮点数用带容差的比较；通过后输出 simple tests passed。

用两个 rank 的单进程模拟与普通线性层比较。非零 bias 可以发现 row-parallel 在归约之前重复加 bias 的错误。

```python
x = torch.tensor([[1., 2.]])
W, bias = torch.tensor([[1., 2.], [3., 4.]]), torch.tensor([5., 6.])
expected = x @ W.T + bias
column = ColumnParallelLinear(W, bias, 2, gather_output=True)
row = RowParallelLinear(W, bias, 2)
for actual in column([x, x]):
    torch.testing.assert_close(actual, expected)
for actual in row(list(x.chunk(2, dim=-1))):
    torch.testing.assert_close(actual, expected)
print("simple tests passed")
```

## 追问

**ColumnParallel 什么时候要 gather_output？**
后面接 row 层就不用，只有下一步需要完整输出时才 gather，比如最后的 LM head 要算 softmax/loss。Megatron 在 vocab 维切 embedding 和输出层，损失也用并行实现来算，避免 gather 整个 `[B, T, V]`。

**RowParallel 的 bias 为什么不能切，也不能各加一次？**
输出维没切，每个 rank 手里是部分和；各加一次，all-reduce 后就成了 $p\cdot b$。要么 reduce 之后加，要么只让 rank 0 加。

**Dropout / LayerNorm 在 TP 下怎么办？**
LayerNorm 和残差在 all-reduce 之后，各 rank 的输入完全相同，参数复制一份，重复计算就行。dropout 作用在复制的激活上时，各 rank 要用同一个随机种子，否则激活就不一致了；作用在切分的部分上时，则要用不同的种子。

**通信量多大，为什么 TP 限制在节点内？**
每层前向 2 次、反向 2 次 all-reduce，每次大小是 $B\cdot T\cdot d$ 的激活，而且在关键路径上，每层都要等。论文把 TP 放在单机 8 卡 NVLink 内，跨机用数据并行，拓扑细节见 `sys-parallel`。

**和 ZeRO / DP 有什么区别？**
TP 切的是一层内部的计算，每个 rank 只算一部分 FLOPs、只存一部分权重和激活；DP 每个 rank 算完整模型，再同步梯度。两者正交，常组合成 2D/3D 并行。
