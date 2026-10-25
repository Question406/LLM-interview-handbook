---
id: code-gqa
section: coding
order: 16
level: A
title: 手写 GQA：`repeat_kv` 让多组 Q head 共享 KV
quick: "$Q$ 有 $H_q$ 个头，$K,V$ 只有 $H_{\\mathrm{kv}}$ 个头，且 $H_q=g\\cdot H_{\\mathrm{kv}}$。把每个 KV head 重复 $g$ 次（或者按组索引）对齐 Q 的头，再做标准 attention。显存和 KV cache 都按 $H_{\\mathrm{kv}}$ 算。"
tags:
  - GQA
  - Attention
  - KV Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: GQA
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

## 题目描述

实现分组查询注意力 GQA，使一组 query head 共享同一个 key/value head。这里不使用因果 mask、padding mask 或 KV cache。

### 接口与约定

- `repeat_kv(x,n_rep)`：x 为 `[B,Hkv,S,D]`。将每一个 KV head 连续重复 `n_rep` 次，输出 `[B,Hkv*n_rep,S,D]`；不能把整个 head 序列循环拼接成另一种顺序。
- `gqa_attn(q,k,v)`：q 为 `[B,Hq,S,D]`，k、v 为 `[B,Hkv,S,D]`，Hq 是 Hkv 的正整数倍。第 i 个 query head 使用第 `i // (Hq/Hkv)` 个 KV head；按每头维度平方根缩放分数，沿全部 key 位置归一化。返回 `[B,Hq,S,D]`。

输入维度保证合法。该接口是手册的小型实现约定，默认测试比较结果和共享分组语义，不要求物理复制 KV 数据。

### 示例

```text
B=D=1，S=2，Hq=4，Hkv=2，Q和K全为0
V的第0个头的两个值都是2，第1个头的两个值都是7
gqa_attn(...) 的每个序列位置、按头输出 -> [2,2,7,7]
repeat_kv(V,1) -> 与V数值和形状相同
```

## 解题思路与参考答案

GQA 的写法是让每 $g$ 个 Q head 共享一个 KV head：$K,V$ 只有 $H_{\mathrm{kv}}$ 个头，用 `repeat_kv` 把每个 KV head 复制 $g$ 次对齐到 $H_q$，后面就是普通的多头注意力。它介于两个极端之间：MHA 是 $H_q=H_{\mathrm{kv}}$，MQA 是 $H_{\mathrm{kv}}=1$。GQA 的质量接近 MHA，cache 接近 MQA。

拿 Llama-3 8B 来说，它是 32 个 Q head、8 个 KV head，$g=4$，KV cache 按 8 个头算，只有 MHA 的四分之一。

## 怎么对齐

$H_q$ 必须能被 $H_{\mathrm{kv}}$ 整除，组大小 $g=H_q/H_{\mathrm{kv}}$。`repeat_kv` 把 `[B, H_kv, S, D]` 沿 head 维每个头复制 $g$ 次，变成 `[B, H_q, S, D]`，然后照普通 MHA 计算：

$$
\mathrm{Attn}(Q,\;\mathrm{repeat}(K),\;\mathrm{repeat}(V)).
$$

等价的实现是用 `einsum` 或 gather：第 $i$ 个 Q head 用第 $\lfloor i/g\rfloor$ 个 KV head，这样不用真的把显存放大 $g$ 倍。手写面试时直接复制就行，但要说一句生产实现是按组索引，不做物理 repeat。

```python
import torch
import torch.nn.functional as F

def repeat_kv(x, n_rep):
    # x: [B, H_kv, S, D]
    if n_rep == 1:
        return x
    b, h, s, d = x.shape
    return (
        x[:, :, None, :, :]
        .expand(b, h, n_rep, s, d)
        .reshape(b, h * n_rep, s, d)
    )

def gqa_attn(q, k, v):
    # q: [B, H_q, S, D], k,v: [B, H_kv, S, D]
    n_rep = q.shape[1] // k.shape[1]
    k, v = repeat_kv(k, n_rep), repeat_kv(v, n_rep)
    att = (q @ k.transpose(-2, -1)) / (q.shape[-1] ** 0.5)
    return F.softmax(att, dim=-1) @ v
```

每个 decode 步先把新的 KV 拼进历史 cache，再对这些 KV 做 repeat，Q 还是 $H_q$ 个头。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

Q、K 全零时注意力权重均匀，把两个 KV head 的 V 分别设成 2 和 7，就应得到 [2,2,7,7]，能直接发现 repeat 的顺序错误。

```python
k = torch.zeros(1, 2, 2, 1)
q = torch.zeros(1, 4, 2, 1)
v = torch.tensor([[[[2.], [2.]], [[7.], [7.]]]])
expected = torch.tensor([2., 2., 7., 7.]).view(1, 4, 1, 1).expand(1, 4, 2, 1)
torch.testing.assert_close(gqa_attn(q, k, v), expected)
torch.testing.assert_close(repeat_kv(v, 1), v)
print("simple tests passed")
```

## 追问

**Cache 公式怎么改？**
把 `arch-kv-cache` 里的 $n_{\mathrm{heads}}$ 换成 $n_{\mathrm{kv}}$ 就行。

**$H_q$ 不能被 $H_{\mathrm{kv}}$ 整除怎么办？**
那是非法配置。Llama-3 8B 就是 32 Q / 8 KV。

**GQA 和 MLA 是一回事吗？**
不是一回事。MLA 压的是 KV 的低秩潜变量，和简单 repeat 是两种做法；DeepSeek 用的 MLA 不是 GQA。
