---
id: pdd-attention-handwrite
section: coding
order: 180
level: A
title: 拼多多应用开发：手写 Attention 时要写出哪些形状和 Mask？
quick: >-
  投影 $Q,K,V$，reshape 成 $[B,H,T,d_h]$，算 $QK^\top/\sqrt{d_h}$，softmax 前加因果 /
  padding mask，再乘 $V$ 拼头。我会口述 broadcast 形状，不能只写 `nn.MultiheadAttention`。
tags:
  - PDD
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多大模型应用开发一面凉经
    url: https://www.nowcoder.com/feed/main/detail/f87fcee060ea404ba99a20245f746e60
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型应用开发
- 届别 / 流程：一面
- 面试时间：原帖未披露；帖子发布于 2026-03-29
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手写attention”**

常见误区是：只写 `nn.MultiheadAttention`，或因果 / padding 的 True-False 反了。同面还可能接着写交叉熵，见 `pdd-ce-handwrite`，两题都要能独立写完。形状与 `deepseek-mha-handwrite` 同构，拼多多要的是口述 broadcast。

## 白板顺序与形状

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d_h}}+M\Big)V
$$

`Linear` 得 $QKV$ → `view/transpose` 到 $[B,H,T,d_h]$ → scores $[B,H,T,T]$ → 加 $M$ → softmax（fp16 升 fp32）→ 乘 $V$ → merge heads → 输出投影。$M$ 常见 $[B,1,1,T]$（padding）或 $[1,1,T,T]$（因果），靠 broadcast。因果：未来位置 `-inf`。padding：key 侧 pad 为 `-inf`。两者可相加。

```python
import torch

def mha(x, wq, wk, wv, wo, n_heads, mask=None):
    b, t, c = x.shape
    dh = c // n_heads
    q = (x @ wq).view(b, t, n_heads, dh).transpose(1, 2)
    k = (x @ wk).view(b, t, n_heads, dh).transpose(1, 2)
    v = (x @ wv).view(b, t, n_heads, dh).transpose(1, 2)
    scores = (q @ k.transpose(-2, -1)) * dh**-0.5
    if mask is not None:
        scores = scores.masked_fill(mask, float("-inf"))
    out = torch.softmax(scores.float(), dim=-1).to(x.dtype) @ v
    return out.transpose(1, 2).contiguous().view(b, t, c) @ wo
```

`view` 前 `contiguous`。GQA 只改 $K,V$ 头数，公式骨架不变。

## 易错与同面 交叉熵损失（CE）

bool mask：`True` 表示「盖住」还是「可见」必须说清，和 `masked_fill` 一致。整行全 mask 时 softmax 出 NaN。应用岗也要能讲 KV cache：逐 token 生成（decode） 步 $T_q=1$，$K,V$ 沿 $T$ 增长。不要把 dropout 当重点。交叉熵用 logsumexp，禁止 softmax 再 log，见 `pdd-ce-handwrite`。

## 追问

- **mask 加减还是 fill？** 加 $M$（0 / `-inf`）与 `masked_fill` 等价，不要又加又 fill 两次。
- **缩放除的是 $d$ 还是 $d_h$？** 头维 $d_h$。除 $d_{\mathrm{model}}$ 会过小。
- **batch 维不同长度？** padding + mask；或 varlen 实现。白板用 pad。
- **和 FlashAttention？** 数学相同。现场写显式矩阵即可。
- **GQA 要改 softmax 吗？** 不要。repeat K/V 头后仍是同一公式。
