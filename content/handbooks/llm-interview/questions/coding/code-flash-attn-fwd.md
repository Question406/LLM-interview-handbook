---
id: code-flash-attn-fwd
section: coding
order: 25
level: S
title: 手写 tiled FlashAttention forward：分块 online softmax 与 logsumexp
quick: >-
  Q 按 $B_r$ 切行块，K/V 按 $B_c$ 切列块，每个行块维护 running max $m$、running sum $\ell$ 和未
  normalization 的 $O$；来一个新块，先用 $e^{m_{\text{old}}-m_{\text{new}}}$ 把旧的 $\ell,O$
  缩放再累加，最后 $O/\ell$，并存下 $\mathrm{lse}=m+\log\ell$ 给 backward。Causal
  时对角线上方的块整块跳过，只有跨对角线的块在块内做 mask，全程不物化 $[T,T]$ 的分数矩阵。
tags:
  - FlashAttention
  - Online Softmax
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28T00:00:00.000Z
sources:
  - title: >-
      FlashAttention: Fast and Memory-Efficient Exact Attention with
      IO-Awareness
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
---

## 题目描述

实现一个分块计算的 attention 前向练习，同时返回每个 query 的 normalization 常数。目标是在不保存完整 T×T attention 矩阵的情况下得到与普通 attention 相同的数值。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `flash_attn_fwd(q,k,v,causal=False,Br=64,Bc=64)`。q/k/v 为 [B,H,T,D] 同形浮点张量；Br、Bc 为正的 query/key 分块大小，T 不必整除分块大小。

### 输出与约束

返回 `(o,lse)`。o 为 [B,H,T,D]、与输入同 dtype；lse 为 [B,H,T] 的 float32 张量，是每个 query 的有效缩放分数的 logsumexp。分数为 q·k/sqrt(D)，causal=True 时只允许 key 位置≤query 位置。

### 示例

```text
q=k=全零，B=H=D=1,T=3，v=[1,2,3]，Br=Bc=2
causal=False -> o=[2,2,2], lse=[ln(3),ln(3),ln(3)]
causal=True -> o=[1,1.5,2], lse=[0,ln(2),ln(3)]
示例省略大小为1的维度。
```

## 解题思路与参考答案

Tiled FlashAttention forward 的核心是 online softmax：Q 按行切块，K/V 按列切块，每个行块一边扫列块一边维护 running max $m$、running sum $\ell$ 和未 normalization 的输出 $O$，换块时用新的 max 把旧的累加器缩放一下再加。扫完所有列块，$O/\ell$ 就是精确的 attention 结果，全程不会出现 $[T,T]$ 的分数矩阵。最后再存一份每行的 logsumexp 给 backward 用。

最常见的错法有两种。一种是先把一整行 $QK^\top$ 算完再 softmax，那只是把 batch 切小了，$[T,T]$ 还是整块落在显存里；另一种是分了块，但换块时忘了用新的 max 去缩放旧的累加器，结果只在 T 小于块大小时才对。面试官要看三件事：online softmax 的递推写对（原理见 `sys-online-softmax`），causal 的块级跳过和块内 mask 分清楚，以及能说出返回的 logsumexp 在 backward 里干什么。朴素版本见 `code-attention`，kernel 层面的 SRAM/HBM 讨论见 `sys-flash`。

## 递推

对一个行块 $Q_i$，按顺序扫列块 $j$，$S_{ij}=Q_iK_j^\top/\sqrt{d}$：

$$
m^{\text{new}}=\max\big(m,\ \mathrm{rowmax}(S_{ij})\big),\quad
P=e^{S_{ij}-m^{\text{new}}},\quad
\alpha=e^{m-m^{\text{new}}}
$$

$$
\ell\leftarrow \alpha\,\ell+\mathrm{rowsum}(P),\qquad
O\leftarrow \alpha\,O+PV_j,\qquad m\leftarrow m^{\text{new}}
$$

扫完所有块后 $O/\ell$ 就是精确的 softmax attention，没有任何近似。$\mathrm{lse}=m+\log\ell$ 就是每一行的 $\log\sum_j e^{s_j}$。

```python
import math
import torch


def flash_attn_fwd(q, k, v, causal=False, Br=64, Bc=64):
    # q,k,v: [B,H,T,D]
    B, H, T, D = q.shape
    scale = 1.0 / math.sqrt(D)
    dev = q.device
    o = torch.empty_like(q)
    lse = torch.empty(B, H, T, device=dev, dtype=torch.float32)
    for i0 in range(0, T, Br):
        i1 = min(i0 + Br, T)
        qi = q[:, :, i0:i1].float() * scale  # [B,H,br,D]
        m = torch.full((B, H, i1 - i0), -float("inf"), device=dev)
        l = torch.zeros(B, H, i1 - i0, device=dev)
        acc = torch.zeros(B, H, i1 - i0, D, device=dev)
        j_end = i1 if causal else T  # causal: blocks with j0 >= i1 are all masked
        for j0 in range(0, j_end, Bc):
            j1 = min(j0 + Bc, T)
            kj = k[:, :, j0:j1].float()  # [B,H,bc,D]
            vj = v[:, :, j0:j1].float()
            s = qi @ kj.transpose(-2, -1)  # [B,H,br,bc]
            if causal and j1 - 1 > i0:  # block crosses the diagonal
                rows = torch.arange(i0, i1, device=dev)[:, None]
                cols = torch.arange(j0, j1, device=dev)[None, :]
                s = s.masked_fill(cols > rows, -float("inf"))
            m_new = torch.maximum(m, s.amax(-1))  # [B,H,br]
            p = torch.exp(s - m_new[..., None])
            alpha = torch.exp(m - m_new)  # first block: exp(-inf) = 0
            l = alpha * l + p.sum(-1)
            acc = alpha[..., None] * acc + p @ vj
            m = m_new
        o[:, :, i0:i1] = (acc / l[..., None]).to(q.dtype)
        lse[:, :, i0:i1] = m + torch.log(l)
    return o, lse
```

有两项适用条件要讲清楚。列块从 $j_0=0$ 开始扫，第一块一定包含第 0 列，causal 下每一行至少有一个合法的 key，所以第一块之后 $m$ 就是有限值，不会出现 $-\infty-(-\infty)$ 的 NaN。T 不能被 $B_r,B_c$ 整除时，靠 `min(..., T)` 截尾，最后一块小一点没关系。

## 为什么省 HBM

标准实现要把 $S$ 和 $P$ 两个 $[T,T]$ 矩阵写回 HBM 再读出来，显存和 IO 都是 $O(T^2)$。分块以后，每次只有一个 $[B_r,B_c]$ 的分数块，放在 SRAM 里用完就丢；每个行块额外只存 $m,\ell$ 两个长度为 $B_r$ 的向量。FLOPs 并没有少，还是 $O(T^2d)$，省的是 HBM 读写。长序列上 attention 是 memory-bound，所以实际耗时也能降下来。上面这段 PyTorch 只是在模拟分块逻辑，真正的收益要在一个 kernel 里把两层循环融合掉才拿得到。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

序列长度 3、块大小 2 会留下不满块。用全零 Q/K 和 V=[1,2,3] 手算：无 mask 时全为 2，因果时为 [1,1.5,2]；同时核对 LSE。

```python
q = k = torch.zeros(1, 1, 3, 1)
v = torch.tensor([1.0, 2.0, 3.0]).view(1, 1, 3, 1)
for causal, expected in [(False, [2.0, 2.0, 2.0]), (True, [1.0, 1.5, 2.0])]:
    out, lse = flash_attn_fwd(q, k, v, causal=causal, Br=2, Bc=2)
    torch.testing.assert_close(out.flatten(), torch.tensor(expected))
    counts = torch.tensor([1.0, 2.0, 3.0] if causal else [3.0, 3.0, 3.0])
    torch.testing.assert_close(lse.flatten(), counts.log())
print("simple tests passed")
```

## 追问

**backward 为什么要 lse？**
因为 backward 需要 $P$，前向又没存 $[T,T]$。有了每行的 lse，可以按块重算 $P_{ij}=\exp(S_{ij}-\mathrm{lse}_i)$，不用再做一遍 max 和 sum 的归约，用重算换显存。

**外层循环为什么放 Q？**
这是 FlashAttention-2 的做法：外层 Q 块、内层 K/V 块，每个行块的 $m,\ell,O$ 一直留在片上，最后只写一次 $O$；不同行块之间没有依赖，可以分给不同的 thread block 并行。FA1 原文是外层 K/V，要反复读写 $O$。

**causal 能省多少？**
大约一半的块。对角线上方的块直接不算，只有对角块做逐元素 mask。如果所有块都算完再 mask，结果是对的，但白算了一半。

**$B_r,B_c$ 怎么选？**
受 SRAM 大小约束：$Q_i,K_j,V_j,O_i$ 和分数块要同时放得下，大致是 $B_c\approx M/(4d)$ 这个量级。head dim 越大，块越小。

**为什么累加用 fp32？**
$\ell$ 和 $O$ 是多次缩放再加总的结果，用 bf16 累加的话，误差会随块数增长。输入输出可以是 bf16，片上的累加器保持 fp32。

**逐 token 生成（decode）阶段也用这个吗？**
一般换成 split-K 变体。decode 时 Q 只有 1 行，瓶颈在读 KV cache，常见做法是按 KV 长度切分再合并，合并各段时同样用 $m,\ell$ 做 rescale。
