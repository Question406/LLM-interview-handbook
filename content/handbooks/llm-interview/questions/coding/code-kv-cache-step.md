---
id: code-kv-cache-step
section: coding
order: 15
level: A
title: 手写一步 decode：用 KV cache 算当前 token 的 attention
quick: >-
  一步 decode 只为当前 token 算 $q_t,k_t,v_t$，把 $k_t,v_t$ concat 到 cache 末尾，再拿 $q_t$
  对全部过去的 key 做点积。整段 $K,V$ 在 prefill 时已经写进 cache，所以这一步的复杂度从完整 self-attention 的
  $O(t^2 d)$ 变成 $O(t d)$。
tags:
  - KV Cache
  - Decode
  - Attention
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: GQA
    url: 'https://arxiv.org/abs/2305.13245'
    type: primary
---

## 题目描述

实现逐 token 生成时的一步 attention。调用者提供当前 token 的 Q/K/V，以及此前已经缓存的 K/V；函数需要把当前 K/V 计入历史，再计算当前 query 的输出。

### 接口与形状

`decode_step(q,k,v,cache_k,cache_v)` 中 q、k、v 为 `[B,H,1,D]`，两个旧缓存均为 `[B,H,S,D]`，S 可以为 0。返回 `(out,new_cache_k,new_cache_v)`，其中 out 为 `[B,H,1,D]`，两个新缓存长度均为 S+1，历史条目必须按原顺序保留。

输出按 `QK^T/sqrt(D)` 在全部历史与当前 key 上 normalization，对 V 加权。这里只传入已到达的 token，不另加未来 token mask；本练习不涉及 RoPE、padding 或多请求分页管理。

### 示例

```text
B=H=D=1，Q与K均为0，起始cache长度0
第1步V=2 -> out=2，cache长度1
第2步V=4 -> out=3，cache长度2，缓存V顺序为[2,4]
```

以上是手册重构的独立函数接口，输入的 batch、头数和每头维度保证匹配。

## 解题思路与参考答案

一步 decode 只算当前这个 token：投影出 $q_t,k_t,v_t$，把 $k_t,v_t$ 接到 cache 末尾，再用 $q_t$ 去打 cache 里全部的 key。过去 token 的 $Q$ 不用再算，它们的 $K,V$ 早就在 cache 里了。显存公式在 `arch-kv-cache` 里讲过，这题要的是能把一步里的张量变化写出来。

面试官常画的场景是：已经有 $t-1$ 个 token 的 cache，现在来了第 $t$ 个。设 $B$ 是 batch、$H$ 是 head 数、$S$ 是已缓存长度、$D$ 是 head dim，那么 cache_k 和 cache_v 都是 `[B, H, S, D]`；当前 hidden 是 `[B, 1, d_model]`，投影之后 $q,k,v$ 各是 `[B, H, 1, D]`。这一步做的事情是

$$
K\leftarrow [K;k_t],\quad V\leftarrow [V;v_t],\quad
\mathrm{Attn}(q_t,K,V)=\mathrm{softmax}\Big(\frac{q_t K^\top}{\sqrt{D}}\Big)V.
$$

$q_t K^\top$ 的形状是 `[B, H, 1, S+1]`。Causal mask 在这一步通常不用加，当前 query 只看 $\le t$ 的 key，而 cache 里存的本来就全是过去。

整个生成过程分两段。Prefill 一次算出完整的 $Q,K,V$，把 cache 写满，复杂度 $O(S^2)$；之后每步 decode 都是 $O(S)$。代码就是一次 concat 加一次 attention：

```python
import torch
import torch.nn.functional as F


def decode_step(q, k, v, cache_k, cache_v):
    # q,k,v: [B, H, 1, D]
    cache_k = torch.cat([cache_k, k], dim=2)
    cache_v = torch.cat([cache_v, v], dim=2)
    att = (q @ cache_k.transpose(-2, -1)) / (q.shape[-1] ** 0.5)
    out = F.softmax(att, dim=-1) @ cache_v
    return out, cache_k, cache_v
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

从长度 0 的 cache 开始追加，第一步只看自己，应输出 2；第二步 Q/K 仍为零，会平均两个 value 得到 3，同时检查长度增长。

```python
empty = torch.empty(1, 1, 0, 1)
q = k = torch.zeros(1, 1, 1, 1)
out, ck, cv = decode_step(q, k, torch.tensor([[[[2.0]]]]), empty, empty)
torch.testing.assert_close(out, torch.tensor([[[[2.0]]]]))
out, ck, cv = decode_step(q, k, torch.tensor([[[[4.0]]]]), ck, cv)
torch.testing.assert_close(out, torch.tensor([[[[3.0]]]]))
assert ck.shape == cv.shape == (1, 1, 2, 1)
print("simple tests passed")
```

## 追问

**KV cache 占多少显存？**
每个 token 在每层都要存一份 $K$ 和 $V$，$L$ 层合起来是 $2\cdot L\cdot H\cdot D\cdot \mathrm{bytes}$，再乘 batch。用 GQA 的话把 $H$ 换成 $H_{\mathrm{kv}}$。

**PagedAttention 下还是这样 concat 吗？**
逻辑上一样，还是当前 $q$ 打全部过去的 $k$，只是物理上 cache 不再连续拼接。手写的时候用 `cat` 就够了。

**prefill 一次进来一整个 chunk 的多个 query，也这么写吗？**
那是 chunked prefill，新 chunk 内部要做因果 mask，同时对 cache 做 cross-attn，和纯 decode 一步分开讲，别混在一起。
