---
id: coding-flash-decode
section: coding
order: 25
level: S
title: 白板：FlashDecoding 的 split-K，online softmax 怎么沿 KV 切开再合并
quick: >-
  Decode 时 $T=1$，FlashAttention 沿 $Q$ 并行吃不满 SM。把 $K,V$ 沿长度切成 $G$ 段，每段各自维护
  $(m,\ell,O)$，再按同一套 rescale 合并。单段先 softmax 再平均是错的。合并后 $O/\ell$ 才是精确注意力。
tags:
  - Coding
  - FlashDecoding
  - Softmax
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Flash-Decoding for long-context inference (Stanford CRFM)
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding
    type: primary
  - title: Flash-Decoding (PyTorch Blog)
    url: https://pytorch.org/blog/flash-decoding/
    type: secondary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
---

## 题怎么来的

NVIDIA / CUDA 岗在 `nvidia-flash-attn` 之后会追 decode。Prefill 的 $Q$ 长度 $T$
大，FlashAttention 沿 $Q$ tile 就能铺满 GPU。Decode 一步 $T=1$，并行度只剩 batch $\times$
head；上下文一长，时间全花在扫 KV，占用率掉下去。Dao 等人的 Flash-Decoding 多开一条并行轴：**沿 KV 长度
split-K**。白板要的不是背名字，是每段留下什么统计、怎么并成和单核 online softmax 一样的结果。单段递推见
`coding-online-softmax`。

## 每段留下 $(m,\ell,O)$，不要局部归一化

$q\in\mathbb{R}^{D}$，$K,V\in\mathbb{R}^{S\times D}$。把 $S$ 切成 $G$ 段，第 $g$ 段分数
$s^{(g)}=K^{(g)}q/\sqrt{D}$。段内仍用 online softmax，写出：

$$
m_g=\max_j s^{(g)}_j,\quad
\ell_g=\sum_j e^{s^{(g)}_j-m_g},\quad
O_g=\sum_j e^{s^{(g)}_j-m_g}\,V^{(g)}_j.
$$

$O_g$ 是 **未除 $\ell_g$** 的加权和，形状仍是 $[D]$（多头时 $[B,H,D]$）。评委最爱听的错法：对每段做完
$\mathrm{softmax}$ 再对 $G$ 个向量做平均。那是 $G$ 套不同分母，不是精确注意力。

合并和两 tile 相接是同一公式，只是现在 $G$ 段可以同时算完再 reduce：

$$
m=\max_g m_g,\quad
\ell=\sum_g e^{m_g-m}\ell_g,\quad
O=\sum_g e^{m_g-m}O_g,\quad
o=O/\ell.
$$

$e^{m_g-m}\in(0,1]$。某段全是 mask 掉的 $-\infty$ 时 $m_g=-\infty$、$\ell_g=0$，合并时跳过，避免
$\infty-\infty$。因果 decode 的 KV 都是「已经写出的过去」，分段只是切长度，没有未来段。

```python
import numpy as np

def split_stats(q, k, v, scale):
    # q: [D]; k,v: [Sg, D]；O 未归一化
    s = (k @ q) * scale
    m = float(np.max(s))
    p = np.exp(s.astype(np.float64) - m)
    ell = float(p.sum())
    o = p @ v.astype(np.float64)
    return m, ell, o


def merge_mlo(stats):
    m = max(mg for mg, lg, og in stats if lg > 0)
    ell, o = 0.0, 0.0
    for mg, lg, og in stats:
        if lg <= 0 or not np.isfinite(mg):
            continue
        a = np.exp(mg - m)
        ell = ell + a * lg
        o = o + a * og
    return o / ell


def flash_decode(q, k, v, scale, n_split=4):
    s_len, d = k.shape
    cuts = np.linspace(0, s_len, n_split + 1, dtype=int)
    stats = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        if a == b:
            stats.append((-np.inf, 0.0, np.zeros(d)))
        else:
            stats.append(split_stats(q, k[a:b], v[a:b], scale))
    return merge_mlo(stats)
```

单测：`n_split=1` 和 `n_split=8` 对上 `softmax(scale K q) @ V`。对不上就是某段先除了 $\ell$，或
merge 漏乘 $e^{m_g-m}$。

## 并行轴、IO、和 prefill 的差别

Split-K 换的是 **占用率**：每段一次读自己那截 $K,V$，部分 $(m,\ell,O)$ 很小，最后一次树形 reduce。HBM
上仍要读完整 KV 一遍，decode 的墙钟还是带宽；收益来自更多 CTA 同时读，而不是少读。$G$ 太大：部分结果太多、reduce
变重，还会把一段切得短过 SRAM tile。白板先写对合并，再提「$G$ 跟 SM 数和 $S$ 走，不是越大越快」。

统计放 fp32。段内 max 和跨段 max 都在 fp32 里 rescale，和 `coding-softmax-stable` 同一条。GQA 时
$K,V$ 仍是 `[B, H_{\mathrm{kv}}, S, D]`，split 沿 $S$，不要沿 head 切开再假装是
split-K。Paged KV 上每一段还要先走 block table 做 gather，见 `coding-paged-table`。

Prefill 一般不靠 split-K 救命，因为 $T$ 本身就能并行。有人把 decode kernel 拿去跑 prefill，占用率看起来很好，但 $Q$ tile 的 IO 模型和 FlashAttention-2 不同，别混报加速比。某段被 mask 成全 $-\infty$ 时 $\ell_g=0$，合并必须跳过，否则 $\exp(-\infty-(-\infty))$ 是 NaN。

## 追问

- **为什么不能每段 softmax 再加权平均？** 各段分母不是全局 $\ell$。权重对不上，不是近似 FlashAttention，是错的。
- **$O$ 若已经除过 $\ell_g$ 怎么并？** $O\leftarrow\sum_g e^{m_g-m}\ell_g O_g$，最后再除 $\ell$。和未归一化版差一个 $\ell_g$
  因子，两种约定不要混。
- **全 $-\infty$ 的一段？** $\ell_g=0$，merge 跳过。所有段都空则 $\ell=0$，那是 mask 写错，不是 split 能救的。
- **和顺序 online 扫 $K$ 块比？** 数学同一套 rescale。Flash-Decoding 把块从「一个 CTA 串行扫」改成「多 CTA 并行再 reduce」，为的是 $T=1$
  时的占用率。
