---
id: code-chunked-prefill
section: coding
order: 51
level: S
title: 手写 chunked prefill：块内因果，块对 cache 做 cross-attn
quick: "把 prompt 切成长 $C$ 的块，每块先把自己的 $K,V$ 追加进 cache，再用带 offset 的因果 mask 做 attention：块内第 $i$ 个 query 能看到 $j\\le \\mathrm{past}+i$ 的所有位置。拼起来的结果要和整段 prefill 一致。"
tags:
  - ChunkedPrefill
  - KV Cache
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "Sarathi: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills"
    url: https://arxiv.org/abs/2308.16369
    type: primary
---

## 题目描述

把一段已有 Q/K/V 的序列分块执行因果 prefill。无论分块长度如何选择，输出应与整段一次执行因果 attention 相同；分块不应改变 token 的绝对位置。

### 接口与张量

- `chunked_prefill(q,k,v,chunk)`：q、k、v 均为 `[B,H,T,D]`，T 和 chunk 为正整数。返回 `[B,H,T,D]`。第 t 个输出只使用位置 0 到 t 的 key/value，每头分数按 D 的平方根缩放。最后一块可以不足 chunk，chunk 大于 T 也合法。
- `KVBuf(B,H,max_len,dh).append(k,v)`：缓存收到的连续块，append 返回截至当前有效长度的 K/V 视图，`len` 记录已经写入的 token 数。输入保证不超过容量。
- `attn_with_offset(q,k,v,past)`：q 对应的位置从 past 开始，k/v 从位置 0 开始；返回这一段 query 的因果注意力输出。

本卡是 CPU 正确性练习，不要求实现生产调度器或 GPU kernel。

### 示例

```text
B=H=D=1, T=3，q、k 全为 0，v 的序列值为 [1,2,3]
chunked_prefill(q,k,v,chunk=2) 的序列输出 -> [1,1.5,2]
chunk=1、3 或 8 时也必须得到同样结果
```

第一个 query 不能读取后两个 value，最后一个 query 可以使用全部三个。

## 解题思路与参考答案

Chunked prefill 就是把 prompt 切成长 $C$ 的块，每块先把自己的 $K,V$ 追加进 cache，再拿块内的 query 对「历史 cache + 本块」做带 offset 的因果 attention。`code-attention` 里的 KV cache 实现是一次 prefill 处理整段输入，$T=S$；分块之后注意力的算法一样，只是每次处理的长度变成 $T=C$。

offset 是最容易写错的地方。比如第二块的第一个 query，绝对位置是 $C$，它应该能看到第一块的全部 $C$ 个 key 和自己。如果块内照搬 `triu(C,C)`，cache 里的历史 key 会被当成「未来」挡掉；如果 offset 从 0 算，第二块就能看见自己后面的 token，却看不见第一块。

## 带 offset 的 causal

已缓存长度为 $\mathrm{past}$，当前块长 $T$：

$$
\mathrm{keep}(i,j)=\big[j\le \mathrm{past}+i\big],\quad i\in[0,T),\; j\in[0,\mathrm{past}+T).
$$

第一块 $\mathrm{past}=0$，退回普通的 triu。逐 token 生成（decode）是 $T=1$ 的特例。

```python
import math
import torch

class KVBuf:
    def __init__(self, B, H, max_len, dh):
        self.k = torch.zeros(B, H, max_len, dh)
        self.v = torch.zeros_like(self.k)
        self.len = 0

    def append(self, k, v):
        t = k.size(2)
        self.k[:, :, self.len:self.len + t] = k
        self.v[:, :, self.len:self.len + t] = v
        self.len += t
        return self.k[:, :, :self.len], self.v[:, :, :self.len]

def attn_with_offset(q, k, v, past):
    scores = q @ k.transpose(-1, -2) / math.sqrt(q.size(-1))
    q_pos = torch.arange(past, past + q.size(2), device=q.device)[:, None]
    k_pos = torch.arange(k.size(2), device=q.device)[None, :]
    scores = scores.masked_fill(k_pos > q_pos, float("-inf"))
    return torch.softmax(scores.float(), dim=-1).to(q.dtype) @ v

def chunked_prefill(q, k, v, chunk):
    B, H, T, D = q.shape
    buf = KVBuf(B, H, T, D)
    outs = []
    for s in range(0, T, chunk):
        e = min(s + chunk, T)
        past = buf.len
        kk, vv = buf.append(k[:, :, s:e], v[:, :, s:e])
        outs.append(attn_with_offset(q[:, :, s:e], kk, vv, past))
    return torch.cat(outs, dim=2)
```

调度的时候，一次迭代可以同时安排若干个 decode 步和一块 prefill，让每次迭代的计算量更均匀，这就是 Sarathi 和 vLLM 里的 chunked prefill。RoPE 用绝对位置 `past+i`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

长度 5 用 chunk=1、2、5、8 切分，既覆盖逐 token，也覆盖尾块与 chunk 大于序列。比较全量因果注意力，验证 past 偏移。

```python
torch.manual_seed(7)
q, k, v = [torch.randn(1, 1, 5, 2) for _ in range(3)]
expected = attn_with_offset(q, k, v, past=0)
for chunk in (1, 2, 5, 8):
    torch.testing.assert_close(chunked_prefill(q, k, v, chunk), expected)
print("simple tests passed")
```

## 追问

**和 decode 有什么差别？**
decode 时 $T=1$，块内不需要再做 triu。chunked prefill 的块内仍然要因果。

**块越大越好吗？**
不一定。大块更容易把算力用满，但可能拉长首个 token 的等待时间（TTFT）；小块更方便穿插在 decode 请求之间，代价是 kernel 启动次数变多。

**和 prefix cache 什么关系？**
公共前缀可以整块复用，见 `code-attention` 里的 `fork`。chunked prefill 解决的是单条超长输入提示（prompt）。
