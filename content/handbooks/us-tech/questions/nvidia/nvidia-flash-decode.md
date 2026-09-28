---
id: nvidia-flash-decode
section: nvidia
order: 21
level: S
title: NVIDIA：FlashDecoding split-K，和训练用 FlashAttention 差在哪
quick: >-
  Prefill 的 $Q$ 够长，FlashAttention 沿 query tile 铺满 SM。Decode 的 $Q$ 是 $[B,1,d_h]$，沿
  $Q$ 切没有 occupancy。FlashDecoding 把 KV 沿 $T$ 做 split-K，每块出一份 partial softmax
  统计再合并。训练核省的是 $[T,T]$ 的 HBM；decode 核抢的是 SM 数量。不是把同一份 FA 换个名字。
tags:
  - NVIDIA
  - FlashDecoding
  - Split-K
  - CUDA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Flash-Decoding for long-context inference
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding.html
    type: primary
  - title: Flash-Decoding — PyTorch Blog
    url: https://pytorch.org/blog/flash-decoding/
    type: secondary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: FlashAttention-2 — Faster Attention with Better Parallelism and Work Partitioning
    url: https://arxiv.org/abs/2307.08691
    type: primary
---

## 题怎么来的

NVIDIA CUDA / LLM serving 岗在 `nvidia-flash-attn` 之后常补一句：那 decode 呢。Tri Dao、Haziza 等人 2023 的 Flash-Decoding 博客把答案写死了：再加一维并行，沿 KV 的序列长切。产品侧 xFormers dispatcher、FlashAttention 2.2+、TensorRT-LLM 的 generation attention，思路同源。我会先画训练核的网格，再画 split-K 的网格，评委听的是 occupancy 从哪来，不是「都叫 Flash」。

## 训练核：沿 $Q$ 铺，墙在 $[T,T]$ 的 IO

标准注意力物化 $S=QK^{\top}$，形状 $[T,T]$，HBM 是 $\Theta(T^2)$。FlashAttention 把 $K,V$ 切成宽 $B_c$ 的块、把 $Q$ 切成高 $B_r$ 的块，SRAM 里做在线 softmax，HBM 访问掉到 $\Theta(T^2 d^2/M)$。网格主要沿 **query 行** 铺：CTA 数大约 $B\cdot H\cdot \lceil T/B_r\rceil$。训练 / prefill 里 $T$ 是千到万，这个数能喂满 A100/H100 的 SM。

FlashAttention-2 改的是 CTA **内部** 的 warp 分工：不再 sliced-K 那样多 warp 切 $K$ 再在 shared memory 归约，而是切 $Q$，warp 之间少同步。那是 tile 内部的 work partitioning，并行轴仍是 $Q$。反向还要重算 $S$，存 $m,\ell$ 而不是满 $P$。这些都是训练核的税，decode 没有。

## Decode 核：沿 $K$ 切，墙在 occupancy

Decode 一步：$Q$ 是 $[B, H, 1, d_h]$，历史 $K,V$ 长度 $T$。$S$ 只有 $[1,T]$，本来就不必写回 HBM。IO 主项是读 KV：

$$
\mathrm{bytes}\approx 2\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot b.
$$

若仍按 FA 训练核那样「一个 CTA 吃一整行 $Q$」，网格只剩 $B\cdot H$ 个 block。$B=1$、$H=32$ 时几十个 CTA，H100 有一百多个 SM，大半空转。Nsight 上 theoretical occupancy 可以不差，**achieved** 低，因为根本没有足够的 block，见 `nvidia-occupancy`。

Flash-Decoding 的 split-K：

1. 把 $K,V$ 沿 $T$ 切成 $G$ 段，每段大约 $T/G$ 个 token。
2. $G$ 个 CTA 并行跑这段上的 FlashAttention 式在线 softmax，各写一份 partial 输出 $O^{(g)}$ 和标量 $\ell^{(g)}=\mathrm{logsumexp}$（博客里还强调每 split 一行一个 extra scalar）。
3. 第二次归约：用各段的 $\ell^{(g)}$ 做稳定的加权合并，

$$
m=\max_g m^{(g)},\quad
O=\sum_g \exp(m^{(g)}-m)\,O^{(g)},\quad
\ell=\log\sum_g\exp(\ell^{(g)}).
$$

在线 softmax 用了两层：段内一层（和 FA 一样），段间再一层。精确注意力，只是求和顺序换了。$G$ 太大：归约核和 extra 写回变明显，tile 也变瘦；$G$ 太小：又填不满 SM。经验是让 $B\cdot H\cdot G$ 至少盖住 SM 数，再按 $T$ 调。Paged 布局下每段还要按 block table gather，见 `nvidia-paged-kv`。

```python
# q: [B, H, 1, d], k,v: [B, H_kv, T, d]
G = num_splits(T, sm_count)
partial_o, partial_lse = flash_attn_splitk(q, k, v, G)  # [G, B, H, 1, d]
o = merge_lse(partial_o, partial_lse)  # 段间 rescale
```

xFormers 的 dispatcher 按问题尺寸在 FA 和 Flash-Decoding 之间切换：短 $T$、大 $B$ 不必 split；长 $T$、小 $B$ 才切。面试别说「decode 一律 split-K」。

## 和训练核对照时我怎么收

| | 训练 / prefill FA | FlashDecoding |
|---|---|---|
| $Q$ 长 | $T$ 大 | $1$ |
| 并行轴 | query tile | KV split |
| 主墙 | 别写 $[T,T]$ | 填满 SM、读 KV |
| 反向 | 重算 + 存统计 | 没有 |
| 额外同步 | tile 内 warp | split 间 lse 归约 |

GQA 只减 $H_{\mathrm{kv}}$，query head 仍在，$B\cdot H$ 可能够、也可能不够，长上下文仍常要 split。Hopper 上还可以再叠 TMA / warp specialization，那是实现，见 `nvidia-ws-decode`；算法差仍是这一维并行。

错法：把 FA-2「少做 split-K 式 warp 同步」和 Flash-Decoding 的 **CTA 级 split-K** 说成同一件事。前者是训练核不想在 CTA 内切 $K$；后者是 decode 必须在 CTA 间切 $K$。

## 追问

- **$G=1$ 是什么？** 退回单 CTA 吃整段 KV，小 batch 长上下文会闲 SM。短 $T$ 反而可能更快，少一次 merge。
- **和 FlashAttention-2 的 sliced-K？** FA-1 CTA 内切 $K$ 要 shared memory 同步；FA-2 改切 $Q$。FlashDecoding 的 split 是 CTA 之间，必须写 partial 到 HBM 再 merge。
- **数值？** 段间必须走 log-sum-exp，不能把 $G$ 份 softmax 输出直接平均。fp16 的 $m$ 要用 fp32 累加 $\ell$。
- **CUDA Graph 还录得动吗？** $G$ 随 $T$ 变，形状不固定。常 pad 到几档 split，或只对 decode 步捕获，见 `nvidia-cuda-graph`。
