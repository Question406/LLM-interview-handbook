---
id: code-decoder-block
section: coding
order: 27
level: S
title: 手写 Llama 风格 decoder block 和 tiny GPT：Pre-Norm、残差流与 loss shift
quick: "每个 block 是两段 Pre-Norm 残差：先 $x\\leftarrow x+\\mathrm{Attn}(\\mathrm{RMSNorm}(x))$，再用同样的方式接 SwiGLU，所有 block 之后补一个 final norm 再进 lm_head。loss 要错开一位，`logits[:, :-1]` 对 `idx[:, 1:]`。"
tags:
  - Transformer
  - Decoder-only
  - Pre-Norm
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "LLaMA: Open and Efficient Foundation Language Models"
    url: https://arxiv.org/abs/2302.13971
    type: primary
  - title: On Layer Normalization in the Transformer Architecture
    url: https://arxiv.org/abs/2002.04745
    type: primary
---

## 题目描述

构建一个能进行前向与 backpropagation 的小型 autoregressive Transformer。以下架构与接口属于手册重构练习约定，不是要求复刻某个公司完整模型。

### 模块与输入输出

- `Block(d,n_head,d_ff)` 接受 `[B,T,d]` 的浮点输入和 RoPE 的 cos/sin。模块采用两次预 normalization：RMSNorm 后进行多头因果 self-attention 并加残差，再经 RMSNorm、SwiGLU 前馈层并加残差。线性层均不带 bias，attention 不含 dropout。
- `rope_cache(T,dh)` 返回 rotate-half 布局的 cos/sin，各为 `[T,dh]`；每头维度 dh 为偶数。
- `TinyGPT(vocab,d,n_head,n_layer,d_ff,max_T,tie)` 接受整数 token ID `[B,T]`，满足 `T <= max_T`，返回 `[B,T,vocab]` 的未 normalization logits。包含 embedding、指定层数的 Block、末尾 RMSNorm 和 vocabulary 投影。tie=True 时 embedding 与 vocabulary 投影引用同一份权重。
- `next_token_loss(logits,idx)` 用前 T-1 个位置预测输入中后 T-1 个 token，返回所有预测位置的平均 cross entropy；T 至少为 2。

模型必须满足因果性：只改变未来 token，不能改变更早位置的 logits；损失能 backpropagation 到模型参数。

### 示例

```text
vocab=2，B=1，idx=[[0,1]]，模型所有权重置为0
logits -> [[[0,0],[0,0]]]
next_token_loss(logits,idx) -> log(2)，约0.693147
```

输入 token 在 vocabulary 内，d 可被 `n_head` 整除，不要求校验非法配置。

## 解题思路与参考答案

Llama 风格的 decoder block 就是两段 Pre-Norm 残差：先 $x\leftarrow x+\mathrm{Attn}(\mathrm{RMSNorm}(x))$，再 $x\leftarrow x+\mathrm{SwiGLU}(\mathrm{RMSNorm}(x))$；所有 block 跑完，过一个 final norm 再进 lm_head，loss 把 logits 和标签错开一位。这题是把几个小组件串起来：`code-rmsnorm`、`code-rope`、`code-attention`、`code-swiglu`。面试官一般让你先写 block，再写整个 forward 和 loss，然后顺手问 Pre-Norm 为什么好训。

常见的失分点有这么几个：norm 放到残差之后，写成了 Post-Norm；RoPE 把 v 也转了；causal mask 忘了加或者方向反了；最后少了 final norm；算 loss 时没把输入和标签错开，让位置 $t$ 去预测它自己。架构层面的讨论见 `arch-decoder-only` 和 `arch-norm`。

## 代码

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.eps, self.w = eps, nn.Parameter(torch.ones(d))

    def forward(self, x):
        return self.w * x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)


def rope_cache(T, dh, base=10000.0):
    inv = 1.0 / base ** (torch.arange(0, dh, 2).float() / dh)  # [dh/2]
    f = torch.outer(torch.arange(T).float(), inv)  # [T,dh/2]
    emb = torch.cat([f, f], -1)  # [T,dh], rotate_half layout
    return emb.cos(), emb.sin()


def apply_rope(x, cos, sin):
    x1, x2 = x.chunk(2, -1)
    return x * cos + torch.cat([-x2, x1], -1) * sin


class Block(nn.Module):
    def __init__(self, d, n_head, d_ff):
        super().__init__()
        self.h, self.dh = n_head, d // n_head
        self.n1, self.n2 = RMSNorm(d), RMSNorm(d)
        self.qkv = nn.Linear(d, 3 * d, bias=False)
        self.o = nn.Linear(d, d, bias=False)
        self.w1 = nn.Linear(d, d_ff, bias=False)  # gate
        self.w3 = nn.Linear(d, d_ff, bias=False)  # up
        self.w2 = nn.Linear(d_ff, d, bias=False)  # down

    def attn(self, x, cos, sin):
        B, T, d = x.shape
        q, k, v = (
            self.qkv(x).view(B, T, 3, self.h, self.dh).permute(2, 0, 3, 1, 4)
        )  # [B,H,T,Dh] each
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
        s = q @ k.transpose(-2, -1) / math.sqrt(self.dh)  # [B,H,T,T]
        future = torch.ones(T, T, dtype=torch.bool, device=x.device).triu(1)
        y = s.masked_fill(future, float("-inf")).softmax(-1) @ v  # [B,H,T,Dh]
        return self.o(y.transpose(1, 2).reshape(B, T, d))

    def forward(self, x, cos, sin):
        x = x + self.attn(self.n1(x), cos, sin)
        h = self.n2(x)
        return x + self.w2(F.silu(self.w1(h)) * self.w3(h))


class TinyGPT(nn.Module):
    def __init__(self, vocab, d=64, n_head=4, n_layer=2, d_ff=172, max_T=128, tie=True):
        super().__init__()
        self.emb = nn.Embedding(vocab, d)
        self.blocks = nn.ModuleList(Block(d, n_head, d_ff) for _ in range(n_layer))
        self.norm = RMSNorm(d)
        self.lm_head = nn.Linear(d, vocab, bias=False)
        if tie:
            self.lm_head.weight = self.emb.weight
        cos, sin = rope_cache(max_T, d // n_head)
        self.register_buffer("cos", cos, persistent=False)
        self.register_buffer("sin", sin, persistent=False)

    def forward(self, idx):
        T = idx.shape[1]  # idx: [B,T]
        x = self.emb(idx)  # [B,T,d]
        for blk in self.blocks:
            x = blk(x, self.cos[:T], self.sin[:T])
        return self.lm_head(self.norm(x))  # [B,T,V]


def next_token_loss(logits, idx):
    V = logits.size(-1)
    return F.cross_entropy(logits[:, :-1].reshape(-1, V), idx[:, 1:].reshape(-1))
```

RoPE 这里用的是 rotate_half 排布，前一半和后一半配对；`code-rope` 里是 even/odd 配对，两者只是维度顺序不同，转换权重时要对上。SwiGLU 比普通 FFN 多一个矩阵，所以 $d_{ff}$ 常取 $\frac{2}{3}\cdot 4d$ 左右，让参数量差不多。

## Pre-Norm 和残差流

先说为什么 Pre-Norm 好训。Post-Norm（原始 Transformer）是 $x\leftarrow\mathrm{Norm}(x+F(x))$，每层输出都要过一次 norm，梯度传回浅层时每层都要乘一次 norm 的雅可比。Xiong et al. 分析过，Post-Norm 在初始化时靠近输出层的梯度很大，所以离不开 learning rate warmup；Pre-Norm $x\leftarrow x+F(\mathrm{Norm}(x))$ 的梯度更平稳，可以少用甚至不用 warmup。

换个角度看，Pre-Norm 下从 embedding 到 final norm 有一条不经过任何 norm 的恒等通路，这就是残差流：每个子层读 $\mathrm{Norm}(x)$，把自己的输出加回 $x$。残差流本身从来没被 normalization 过，所以最后必须补一个 final norm 再进 lm_head，漏掉的话 logits 的尺度会随层数变。Pre-Norm 的代价是残差流的范数随层数增长，越靠后的子层加上去的那一份占比越小。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

建立只有一层的小模型并固定种子。除了形状，改变最后一个 token 后，前两个位置的 logits 必须不变；最后 backpropagation 检查损失有限且梯度能到达 embedding。

```python
torch.manual_seed(7)
model = TinyGPT(vocab=7, d=8, n_head=2, n_layer=1, d_ff=16, max_T=4)
a, b = torch.tensor([[1, 2, 3]]), torch.tensor([[1, 2, 4]])
logits = model(a)
assert logits.shape == (1, 3, 7)
torch.testing.assert_close(logits[:, :2], model(b)[:, :2])
loss = next_token_loss(logits, a)
assert torch.isfinite(loss)
loss.backward()
assert model.emb.weight.grad is not None
print("simple tests passed")
```

## 追问

**loss 为什么要 shift？**
因为位置 $t$ 只能看到 $\le t$ 的 token，它的输出是用来预测 $t+1$ 的。不 shift 就等于让模型抄输入，loss 很快掉到 0。最后一个位置没有标签，被 `[:, :-1]` 丢掉。

**怎么验证 causal 写对了？**
改掉第 $j$ 个 token，位置 $\lt j$ 的 logits 必须完全不变。这比读代码可靠。

**weight tying 有什么影响？**
lm_head 和 embedding 共用一个 $[V,d]$ 矩阵，小模型能省一大块参数，$V$ 大时尤其明显。大模型里常常不共享，Llama 就是分开的。

**RoPE 为什么只转 q/k？**
位置信息只需要进入 $q^\top k$ 的内积，让它只依赖相对位置 $m-n$。v 也转的话，会把绝对位置混进输出。

**加 KV cache 要改哪里？**
在 attn 里把新的 k（已经做过 RoPE）和 v 拼到 cache 上，cos/sin 按真实位置 `pos:pos+T` 取，别从 0 开始。单步逐 token 生成（decode）的写法见 `code-kv-cache-step`。

**推理时能用 `F.scaled_dot_product_attention` 吗？**
可以。`is_causal=True` 和上面的 mask 等价，还会走 FlashAttention 类的 kernel。
