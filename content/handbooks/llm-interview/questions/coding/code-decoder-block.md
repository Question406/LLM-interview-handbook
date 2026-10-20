---
id: code-decoder-block
section: coding
order: 27
level: S
title: 手写 Llama 风格 decoder block 和 tiny GPT：Pre-Norm、残差流与 loss shift
quick: "每个 block 是 Pre-Norm 残差：先 $x\\leftarrow x+\\mathrm{Attn}(\\mathrm{RMSNorm}(x))$，再用同样方式接 SwiGLU。loss 要错一位：`logits[:, :-1]` 对 `idx[:, 1:]`。"
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

这题是把几个小组件串起来：`code-rmsnorm`、`code-rope`、`code-attention`、`code-swiglu`。常见失分点：norm 放到残差之后写成了 Post-Norm；RoPE 对 v 也转了；causal mask 忘了或方向反了；最后少了 final norm；计算损失时没错开输入和标签，让位置 $t$ 去预测自己。面试官一般让你先写 block，再写整个 forward 和 loss，顺手问 Pre-Norm 为什么好训。架构层面的讨论见 `arch-decoder-only` 和 `arch-norm`。

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
    inv = 1.0 / base ** (torch.arange(0, dh, 2).float() / dh)     # [dh/2]
    f = torch.outer(torch.arange(T).float(), inv)                 # [T,dh/2]
    emb = torch.cat([f, f], -1)                                   # [T,dh], rotate_half layout
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
        self.w1 = nn.Linear(d, d_ff, bias=False)                  # gate
        self.w3 = nn.Linear(d, d_ff, bias=False)                  # up
        self.w2 = nn.Linear(d_ff, d, bias=False)                  # down

    def attn(self, x, cos, sin):
        B, T, d = x.shape
        q, k, v = self.qkv(x).view(B, T, 3, self.h, self.dh).permute(2, 0, 3, 1, 4)  # [B,H,T,Dh] each
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
        s = q @ k.transpose(-2, -1) / math.sqrt(self.dh)          # [B,H,T,T]
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
        T = idx.shape[1]                                          # idx: [B,T]
        x = self.emb(idx)                                         # [B,T,d]
        for blk in self.blocks:
            x = blk(x, self.cos[:T], self.sin[:T])
        return self.lm_head(self.norm(x))                         # [B,T,V]

def next_token_loss(logits, idx):
    V = logits.size(-1)
    return F.cross_entropy(logits[:, :-1].reshape(-1, V), idx[:, 1:].reshape(-1))
```

RoPE 这里用 rotate_half 排布（前一半和后一半配对），和 `code-rope` 里 even/odd 配对只是维度顺序不同，权重转换时要对上。SwiGLU 比普通 FFN 多一个矩阵，因此常将 $d_{ff}$ 设为 $\frac{2}{3}\cdot 4d$ 左右，以保持相近的参数量。

## Pre-Norm 和残差流

Post-Norm（原始 Transformer）是 $x\leftarrow\mathrm{Norm}(x+F(x))$，每层输出都要过 norm，梯度回传到浅层时每层都乘一次 norm 的雅可比。Xiong et al. 的分析是 Post-Norm 在初始化时靠近输出层的梯度很大，所以离不开 learning rate warmup；Pre-Norm $x\leftarrow x+F(\mathrm{Norm}(x))$ 的梯度更平稳，可以少用甚至不用 warmup。

换个角度看，Pre-Norm 下从 embedding 到 final norm 有一条不经过任何 norm 的恒等通路，叫残差流：每个子层读 $\mathrm{Norm}(x)$，把自己的输出加回 $x$。因为残差流本身从不被归一化，最后必须补一个 final norm 再进 lm_head，漏掉它 logits 尺度会随层数变。Pre-Norm 的代价是残差流的范数随层数增长，越靠后的子层加上去的那一份相对占比越小。

## 追问

- **loss 为什么要 shift？** 因果语言模型在位置 $t$ 只能看到 $\le t$ 的 token，它的输出用来预测 $t+1$。不 shift 等于让模型抄输入，loss 很快到 0。最后一个位置没有标签，被 `[:, :-1]` 丢掉。
- **怎么验证 causal 写对了？** 改掉第 $j$ 个 token，位置 $\lt j$ 的 logits 必须完全不变。这比读代码可靠。
- **weight tying 有什么影响？** lm_head 和 embedding 共用 $[V,d]$ 矩阵，小模型能省一大块参数（$V$ 大时尤其明显）。大模型里常不共享，Llama 就是分开的。
- **RoPE 为什么只转 q/k？** 位置信息只需要进入 $q^\top k$ 的内积，使它只依赖相对位置 $m-n$；v 转了会把绝对位置混进输出。
- **加 KV cache 要改哪？** attn 里把新 k（已做 RoPE）和 v 拼到 cache，cos/sin 用真实位置 `pos:pos+T` 索引而不是从 0 开始，单步逐 token 生成（decode）的写法见 `code-kv-cache-step`。
- **推理时用 `F.scaled_dot_product_attention` 可以吗？** 可以，`is_causal=True` 等价于上面的 mask，并且会走 FlashAttention 类 kernel。
