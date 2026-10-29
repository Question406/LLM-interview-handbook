---
id: nvidia-flash-attn
section: nvidia
order: 6
level: S
title: NVIDIA：FlashAttention IO 分析，SRAM tiling，为什么 decode 收益不同
quick: >-
  FlashAttention 用 SRAM 分块和在线 softmax，避免把 $[T,T]$ 的分数与概率矩阵写进 HBM，访问量从
  $\Theta(T^2)$ 降到 $\Theta(T^2 d^2/M)$。Prefill 能明显受益；decode 的 $Q$ 只有一行，主要成本是读历史
  KV，通常还要沿 KV 切分来填满 SM。
tags:
  - NVIDIA
  - FlashAttention
  - CUDA
  - IO
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      FlashAttention — Fast and Memory-Efficient Exact Attention with
      IO-Awareness
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: >-
      https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: NVIDIA Megatron-LM
    url: 'https://github.com/NVIDIA/Megatron-LM'
    type: primary
---

## 可以这样回答

FlashAttention 的收益来自少读写 HBM：把 attention 分块放进 SRAM，边算 softmax 边累积输出，保留精确结果。例如 $T=4096$、$d_h=128$ 时，完整分数矩阵比 $Q$ 大一个数量级以上，省掉这份读写很划算。Megatron、Transformer Engine 和 TensorRT-LLM 都使用同类 kernel，但 prefill 和 decode 的瓶颈不同。

训练还要把 $P$ 留给反向，激活显存也是 $O(T^2)$。这就是长上下文时「attention 激活比 MLP 还可怕」的来源。

## 技术备查

FlashAttention 的收益来自少读写 HBM：把 attention 分块放进 SRAM，边算 softmax 边累积输出，保留精确结果。例如 $T=4096$、$d_h=128$ 时，完整分数矩阵比 $Q$ 大一个数量级以上，省掉这份读写很划算。Megatron、Transformer Engine 和 TensorRT-LLM 都使用同类 kernel，但 prefill 和 decode 的瓶颈不同。

## 为什么分块能减少 IO

$Q,K,V$ 各 $[B, H, T, d_h]$（下面省 $B,H$，写 $T\times d$）。$S=QK^{\top}$ 是 $[T, T]$，softmax 成 $P$，再 $PV$。HBM 上光 $S$、$P$ 就要读写 $\Theta(T^2)$ 个元素，再加上 $O(Td)$ 的 $QKV$ 和输出。$T=4096$、$d_h=128$ 时，$S$ 比 $Q$ 大一个数量级以上。算力上 attention 是 $O(T^2 d)$，但 A100/H100 的 HBM 带宽更先爆，所以这是 IO 墙，不是算子写错。

训练还要把 $P$ 留给反向，激活显存也是 $O(T^2)$。这就是长上下文时「attention 激活比 MLP 还可怕」的来源。

具体计算时，SRAM 大小记 $M$（片上，大约一百到几百 KB 量级，看架构和 occupancy）。把 $K,V$ 切成宽 $B_c=\Theta(M/d)$ 的块，把 $Q$ 切成高 $B_r$ 的块。外层沿 $K/V$ 块扫，内层载入一块 $Q$：

1. 算局部 $S_{ij}=Q_i K_j^{\top}$，还在 SRAM。
2. 维护行上的运行最大值 $m_i$ 和指数和 $\ell_i$（在线 softmax），用新块的 rowmax 去 rescale 旧的输出累加。
3. 用局部 $P_{ij}$ 乘 $V_j$，累加到 $O_i$。
4. 写回 HBM 的只有最终 $O$，以及反向需要的少量统计（$m,\ell$），不写满 $[T, T]$。

论文给出 HBM 访问 $\Theta(T^2 d^2 / M)$。当 $M$ 明显大于 $d^2$ 时，这比标准实现的 $\Theta(T^2)$ 更好。结果仍是精确 attention，只改变了求和顺序。数值上要像普通 softmax 减 max 那样保持稳定，尤其处理 fp16 的最大值时。

反向时重算局部 $S$，省下存储 $P$ 的 HBM，用更多计算换更少访存。这和 Megatron 的 activation checkpoint 同一逻辑，只是粒度在 attention tile 里。共享内存用得猛，occupancy 可能并不高，但 SOL 的内存项下来了，总时间仍快。别看见 occupancy 低就说 kernel 没写好，见 `nvidia-occupancy`。

## 为什么 decode 收益不同

Prefill：一条序列 $[B, T, D]$，$Q$ 和 $K$ 一样长，$S$ 是 $[T, T]$。少写 $S$ 是一等红利，FlashAttention 几乎是默认。

Decode：当前 $Q$ 是 $[B, 1, D]$，历史 $K,V$ 在 cache 里长度 $T$。$S$ 只有 $[1, T]$，本来就不占 HBM。每步真正贵的是从 HBM 读整段 KV，字节数 $O(T\cdot H_{\mathrm{kv}}\cdot d_h)$，和 GQA 绑在一起。FlashAttention 的 tiling 对「别物化 $T\times T$」几乎无事可做；还能融合 softmax、少几次 round-trip，但加速比通常远小于 prefill。

Decode 要吃满 GPU，得把 KV 沿 $T$ 切开并行（FlashDecoding / split-K），各块出一份 partial softmax 统计再合并。这是 occupancy 问题：单 query 的序列太瘦，不切的话 SM 闲着。TensorRT-LLM 一类 serving 栈在长上下文 decode 上走的是这条，不是把 prefill kernel 原样套上来。Paged KV 的布局见 `nvidia-paged-kv`。

有因果 mask 时，下三角之外的 tile 可以直接跳过，继续减少 IO 和 FLOPs。Decode 每步本来只看历史，这部分收益就小得多。

## 追问

**Dropout 怎么办？**
正向若 drop，反向重算要对齐同一份 RNG。FlashAttention 会存 mask 或 seed，不能假装「融合了就不用记状态」。

**GQA 的 K/V head 更少，FlashAttention 还值不值？**
Prefill 仍值，因为 $S$ 还是 $[T, T]$ 对每个 query head。Decode 更是 KV 带宽墙，GQA 本身往往比换 attention kernel 更划算，见 `google-gqa-mqa`。

**FlashAttention-2/3？**
2 改 work partitioning，减少 split-K 式的无效同步；3 吃 Hopper 的 TMA / WGMMA。面试主线仍是 IO：HBM 上不要放 $[T, T]$。

**窗口 attention / 压缩 KV 还要不要 FA？**
要。稀疏只是少算一些块；剩下的块照样不该把 $S$ 写回 HBM。

## 相关题

- [[google-flash-attention]]：和本题几乎是同一题的 Google 问法，IO 公式和 decode 结论相同，多了 TPU（VMEM、Pallas/Splash）怎么落地。
- [[nvidia-flash-decode]]：本题最后一节的续问，decode 时怎么沿 KV 做 split-K，并和训练核对照网格与切分轴。
- [[openai-flash-decode]]：同样问 FlashDecoding，侧重什么时候 $BH$ 已经够大、不必切，以及和 split-K GEMM 的类比。
- [[coding-flash-decode]]：把 split-K 的分段统计和合并写成代码，带空段和单测。
- [[coding-online-softmax]]：本题 SRAM tiling 里 online softmax 的白板实现，running max 和 sumexp 怎么 rescale。
- [[google-block-attn]]：把 FlashAttention 和 blockwise、Ring Attention 放在一起，分清三层各省哪一份 IO。
