---
id: nvidia-flash-attn
section: nvidia
order: 6
level: S
title: NVIDIA：FlashAttention IO 分析，SRAM tiling，为什么 decode 收益不同
quick: >-
  标准注意力要把 $[T, T]$ 的 $S$ 和 $P$ 写进 HBM，IO 是 $\Theta(T^2)$。FlashAttention 把 $Q,K,V$
  切进 SRAM，在线 softmax，HBM 访问降到 $\Theta(T^2 d^2/M)$。Prefill 的 $T$ 大，这笔 IO
  是主因。Decode 的 $Q$ 只有当前一步，$S$ 已经是 $[1, T]$，瓶颈改成读 KV cache，tiling 的红利小得多。
tags:
  - NVIDIA
  - FlashAttention
  - CUDA
  - IO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: NVIDIA Megatron-LM
    url: https://github.com/NVIDIA/Megatron-LM
    type: primary
---

## 题怎么来的

NVIDIA 岗把注意力当 kernel 题，不是当 Transformer 名词题。论文是 FlashAttention 的 IO 分析；产品侧 Megatron / Transformer Engine / TensorRT-LLM 都接了同类 kernel。我会先写标准注意力在 HBM 上写了什么，再画 SRAM tile，最后说明 decode 为什么不能抄 prefill 的加速比。

## 标准注意力的 IO

$Q,K,V$ 各 $[B, H, T, d_h]$（下面省 $B,H$，写 $T\times d$）。$S=QK^{\top}$ 是 $[T, T]$，softmax 成 $P$，再 $PV$。HBM 上光 $S$、$P$ 就要读写 $\Theta(T^2)$ 个元素，再加上 $O(Td)$ 的 $QKV$ 和输出。$T=4096$、$d_h=128$ 时，$S$ 比 $Q$ 大一个数量级以上。算力上注意力是 $O(T^2 d)$，但 A100/H100 的 HBM 带宽更先爆，所以这是 IO 墙，不是算子写错。

训练还要把 $P$ 留给反向，激活显存也是 $O(T^2)$。这就是长上下文时「注意力激活比 MLP 还可怕」的来源。

## SRAM tiling 和在线 softmax

SRAM 大小记 $M$（片上，大约一百到几百 KB 量级，看架构和 occupancy）。把 $K,V$ 切成宽 $B_c=\Theta(M/d)$ 的块，把 $Q$ 切成高 $B_r$ 的块。外层沿 $K/V$ 块扫，内层载入一块 $Q$：

1. 算局部 $S_{ij}=Q_i K_j^{\top}$，还在 SRAM。
2. 维护行上的运行最大值 $m_i$ 和指数和 $\ell_i$（在线 softmax），用新块的 rowmax 去 rescale 旧的输出累加。
3. 用局部 $P_{ij}$ 乘 $V_j$，累加到 $O_i$。
4. 写回 HBM 的只有最终 $O$，以及反向需要的少量统计（$m,\ell$），不写满 $[T, T]$。

论文给出 HBM 访问 $\Theta(T^2 d^2 / M)$。当 $M$ 明显大于 $d^2$ 时，这比标准实现的 $\Theta(T^2)$ 更好。精确注意力，不是近似：只是换了求和顺序，数值上要小心 fp16 的 max 稳定，和普通 softmax 减 max 是同一件事。

反向：重算局部 $S$ 而不是存 $P$，用算力换 HBM。这和 Megatron 的 activation checkpoint 同一逻辑，只是粒度在 attention tile 里。共享内存用得猛，occupancy 可能并不高，但 SOL 的内存项下来了，总时间仍快。别看见 occupancy 低就说 kernel 没写好，见 `nvidia-occupancy`。

## 为什么 decode 收益不同

Prefill：一条序列 $[B, T, D]$，$Q$ 和 $K$ 一样长，$S$ 是 $[T, T]$。少写 $S$ 是一等红利，FlashAttention 几乎是默认。

Decode：当前 $Q$ 是 $[B, 1, D]$，历史 $K,V$ 在 cache 里长度 $T$。$S$ 只有 $[1, T]$，本来就不占 HBM。每步真正贵的是从 HBM 读整段 KV，字节数 $O(T\cdot H_{\mathrm{kv}}\cdot d_h)$，和 GQA 绑在一起。FlashAttention 的 tiling 对「别物化 $T\times T$」几乎无事可做；还能融合 softmax、少几次 round-trip，但加速比通常远小于 prefill。

Decode 要吃满 GPU，得把 KV 沿 $T$ 切开并行（FlashDecoding / split-K），各块出一份 partial softmax 统计再合并。这是 occupancy 问题：单 query 的序列太瘦，不切的话 SM 闲着。TensorRT-LLM 一类 serving 栈在长上下文 decode 上走的是这条，不是把 prefill kernel 原样套上来。Paged KV 的布局见 `nvidia-paged-kv`。

因果 mask：tile 落在下三角之外的块直接跳，IO 和 FLOPs 都能再省；decode 一步本来就只看历史，mask 不是主因。

## 追问

- **Dropout 怎么办？** 正向若 drop，反向重算要对齐同一份 RNG。FlashAttention 会存 mask 或 seed，不能假装「融合了就不用记状态」。
- **GQA 的 K/V head 更少，FlashAttention 还值不值？** Prefill 仍值，因为 $S$ 还是 $[T, T]$ 对每个 query head。Decode 更是 KV 带宽墙，GQA 本身往往比换注意力 kernel 更划算，见 `google-gqa-mqa`。
- **FlashAttention-2/3？** 2 改 work partitioning，减少 split-K 式的无效同步；3 吃 Hopper 的 TMA / WGMMA。面试主线仍是 IO：HBM 上不要放 $[T, T]$。
- **窗口注意力 / 压缩 KV 还要不要 FA？** 要。稀疏只是少算一些块；剩下的块照样不该把 $S$ 写回 HBM。
