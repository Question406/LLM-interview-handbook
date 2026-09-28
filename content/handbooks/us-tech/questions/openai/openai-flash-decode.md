---
id: openai-flash-decode
section: openai
order: 31
level: S
title: OpenAI：FlashDecoding 为什么沿 KV 长度做 split-K，decode 时和 FlashAttention 差在哪
quick: >-
  Prefill 的 $Q$ 长，$T_q$ 能把 SM 填满。Decode 时 $T_q=1$，并行度只剩 $B\cdot H$，长上下文、小 batch 吃不满带宽。FlashDecoding 把
  $K,V$ 沿序列切成 $S$ 段并行算局部注意力，再按 log-sum-exp 归约，数学仍是精确 softmax。$B H$ 已经大于 SM 数时不要硬切。
tags:
  - OpenAI
  - FlashDecoding
  - Inference
  - CUDA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Flash-Decoding for long-context inference (Stanford CRFM)
    url: https://crfm.stanford.edu/2023/10/12/flashdecoding.html
    type: primary
  - title: Flash-Decoding (PyTorch Blog)
    url: https://pytorch.org/blog/flash-decoding/
    type: primary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

Dao、Haziza、Massa、Sizov 的 Flash-Decoding 是公开推理 kernel，不是 OpenAI 内部代号。推理岗会把它接在 `openai-prefill-decode` 后面问：既然 FlashAttention 已经不物化 $[T,T]$，decode 为什么还慢。差在并行度，不在公式。片上 softmax 见 `google-flash-attention`、`nvidia-flash-attn`、`coding-online-softmax`。

## Decode 的并行度塌了

FlashAttention 的外层并行是 batch、head、query tile。Prefill 时 $T_q$ 上千，每个 query 块都能占一个 CTA，HBM 往返被 tile 吃掉，这是 prefill 的红利。

Decode 一步：$Q$ 是 `[B, H, 1, D]`，$K,V$ 是 `[B, H_{\mathrm{kv}}, T, D]`。分数已经是 `[1, T]`，没有 $[T,T]$ 可省。墙上的时间是把整段 KV 从 HBM 读进来。更糟的是能发 load 的 CTA 太少：并行度大约 $B\cdot H$（GQA 时是 $B\cdot H_q$，但 KV 头更少）。$B=1$、$H=32$，A100 有 108 个 SM，大部分 SM 闲着，带宽打不满。这不是算术强度公式变了，是 occupancy。

所以「decode 再套一遍 prefill 的 FlashAttention」加速比通常很小。GQA / 量化 cache 降的是每步要读的字节，见 `google-gqa-mqa`；FlashDecoding 降的是读这些字节时 SM 闲着。两杠杆正交。

## Split-K：沿 KV 切开，再用 LSE 合并

Flash-Decoding 多一个并行轴：把长度为 $T$ 的 $K,V$ 切成 $S$ 段。每段对同一个 $q$ 跑一块 FlashAttention，写出局部输出 $O_s$ 和该段的 log-sum-exp $\ell_s=\log\sum\exp(q k^\top/\sqrt{d})$。然后做一次小归约：

$$
\ell=\log\sum_{s=1}^{S}e^{\ell_s},\qquad
O=\sum_{s=1}^{S}e^{\ell_s-\ell}\,O_s.
$$

实现上先减 $\max_s \ell_s$ 再 exp，避免 overflow。这和 online softmax 跨块 rescale 是同一套代数，精确注意力，不是近似。CTA 数变成大约 $B\cdot H\cdot S$，只要 $T$ 够长，就能把 SM 喂饱。博客报过长序列上最高大约 8 倍的生成加速；数字随 GPU、头数、是否已经有足够 $B H$ 变，面试报趋势不要报成 SLA。

```python
def merge_splits(O_s, lse_s):
    # O_s: [S, D], lse_s: [S]  fp32
    m = lse_s.max()
    w = torch.exp(lse_s - m)
    ell = m + torch.log(w.sum())
    return (w.unsqueeze(-1) * O_s).sum(0) / w.sum(), ell
```

启发式：`num_splits=1` 当 $B H$ 已经大于 SM 数。硬切 $S=8$ 只会加一次同步和若干次额外写 $O_s$，更慢。FlashAttention-2 论文也讨论过 split-K 的无效同步；decode 长、$B$ 小才是这条路径的工作点。$S$ 太大，每段 $T/S$ 太短，tile 效率掉下去，和 prefill 块太小同一类病。

因果：decode 一步没有未来 key，mask 不是主因。Paged KV 只改物理布局，split 仍然按逻辑 $T$ 切，见 `openai-continuous-batching`。投机解码的验证步 $T_q=\gamma\gt 1$，并行度回来了，往往不必 split-K，见 `openai-speculative-decoding`。

错法：说 FlashDecoding 把复杂度改成线性；说它和 FlashAttention 公式不同；在大 batch 上默认 split。要讲清何时切、怎么合并、何时不切。

## 追问

- **和 split-K GEMM 什么关系？** 同一思想：M 维太瘦，把 K 维切开填 SM，再归约。注意力的归约必须带 LSE，不能把各段 $O_s$ 直接平均。
- **GQA 的 $H_{\mathrm{kv}}$ 更少，还要不要 split？** 更要。KV 头少意味着发 load 的 CTA 更少，长 $T$ 更吃不满带宽。
- **数值会和单核 bit exact 吗？** 不会。浮点归约顺序变了，ulp 级差。下游 greedy 应对齐到 token；不要用 bitwise 当回归。
- **训练要不要 FlashDecoding？** 不要。训练 $T_q$ 大，prefill 式 FlashAttention 才是主路径。这是推理 decode 的 occupancy 补丁。
