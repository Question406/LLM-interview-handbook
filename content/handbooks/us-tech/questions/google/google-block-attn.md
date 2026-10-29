---
id: google-block-attn
section: google
order: 24
level: S
title: Google：长序列 attention 的 blockwise / ring IO，和 FlashAttention 什么关系
quick: >-
  FlashAttention 把 $QK^\top$ tile 留在 SRAM，将 HBM 流量从 $O(T^2)$ 降到约 $O(T^2
  d/M)$；Blockwise 降低层激活峰值，Ring 则把序列分到多设备。三者可以叠加，仍算精确 attention，训练 / prefill 与
  decode 的布局也可以不同。
tags:
  - Google
  - Attention
  - Ring Attention
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
  - title: Blockwise Parallel Transformer for Large Context Models
    url: 'https://arxiv.org/abs/2305.19370'
    type: primary
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: 'https://arxiv.org/abs/2310.01889'
    type: primary
  - title: >-
      Gemini 1.5 — Unlocking multimodal understanding across millions of tokens
      of context
    url: 'https://arxiv.org/abs/2403.05530'
    type: primary
---

## 可以这样回答

FlashAttention、Blockwise Transformer 和 Ring Attention 可以叠加，分别处理芯片内 IO、层内激活和跨设备序列容量。它们仍在算精确 attention。比如长到百万 token 的训练或 prefill，即使单个 attention 核已省 IO，整层激活和 KV 仍可能超出单卡容量，还得继续分块、分设备。

标准实现会物化 $S=QK^\top$，形状 $[T,T]$，占用 HBM，精确 attention 计算量仍是 $\Theta(T^2 d)$。FlashAttention 把 $Q,K,V$ tile 留在 SRAM，TPU 对应 VMEM，用在线 softmax 避免把 $S$ 写回 HBM，反向重算 $P$。HBM 访问大约 $O(T^2 d^2/M)$，其中 $M$ 是片上容量。TPU 的 Splash / Pallas 也在优化同一层 IO。

## 技术备查

FlashAttention、Blockwise Transformer 和 Ring Attention 可以叠加，分别处理芯片内 IO、层内激活和跨设备序列容量。它们仍在算精确 attention。比如长到百万 token 的训练或 prefill，即使单个 attention 核已省 IO，整层激活和 KV 仍可能超出单卡容量，还得继续分块、分设备。

标准实现会物化 $S=QK^\top$，形状 $[T,T]$，占用 HBM，精确 attention 计算量仍是 $\Theta(T^2 d)$。FlashAttention 把 $Q,K,V$ tile 留在 SRAM，TPU 对应 VMEM，用在线 softmax 避免把 $S$ 写回 HBM，反向重算 $P$。HBM 访问大约 $O(T^2 d^2/M)$，其中 $M$ 是片上容量。TPU 的 Splash / Pallas 也在优化同一层 IO。

Blockwise Parallel Transformer（Liu et al.）把序列切块，按块完成 attention 后立即接 FFN / 残差，再处理下一块，减少整层 $[T, D]$ attention 输出与 FFN 中间量同时驻留的峰值。块内仍可用 FlashAttention。

Ring Attention 再把序列分到设备上，每卡 $T/N$，本地保存自己的 $Q$，KV 块沿环转一圈，边接收边算 attention 并累加。每跳通信 $O((T/N) d)$，共 $N$ 跳，总量 $O(T d)$，与全量 all-gather 同阶，优势在于能与本地计算重叠，且单卡无需保存全 KV。块不够大或环上带宽不足，就可能从 HBM 容量受限变成 ICI 通信延迟受限。

训练 / prefill 时，先用 Flash 式核避免 $[T,T]$ 分数矩阵，再用 remat / scan 降低层激活，更长时切 $T$，在 TPU mesh 增加 `seq` 轴。块大小太小，kernel 启动和 ring 同步占比高；太大又放不进 VMEM / HBM。TPU 还要对齐 128 的 MXU，XLA 的块大小在编译期固定，变长请求通过 pad 处理。

Decode 的 $T_q=1$，没有完整 $[T,T]$ 分数矩阵，重点转向 KV 头数和 cache 量化。历史 KV 分在多卡时，每步小消息收集可能拖慢延迟，因此有系统 prefill 切序列、decode 收拢 KV 或按层流水。训练拓扑不能直接搬到 serving，单卡 HBM 也仍受随 $T$ 增长的 KV 与激活限制。

稀疏窗、Linformer、线性 attention 才是修改数学结构、可能把 FLOPs 降到近线性的路线，但不规则访存可能让实际耗时不如精确 attention + Flash。Gemini 1.5 的公开百万 token 检索能力不说明只有一种实现，先解释精确 IO 栈，再按需求考虑稀疏或分层。窗口内的局部 $S$ 同样可以用 Flash，blockwise 本身不会把复杂度降成 $O(T)$。

## 追问

**Ring 怎么保证结果正确？**
用在线 softmax 的 $m,\ell$ 重缩放并累加，与单机分块是同一套代数。忽略浮点运算顺序时精确，归约树不同则无需 bitwise 相同。

**能和流水线并行叠加吗？**
可以。PP 切层，ring 切 $T$，但 PP 气泡和环同步会一起影响调度，先确认 2D mesh 是否足够。

**1M 训练必须用 Ring 吗？**
不必须。激活重算、序列并行和 Flash 也能组合，取舍看 HBM 和 ICI。FlashAttention 论文虽非 Google 工作，其 IO 思路仍适用于 TPU，不能直接照搬 CUDA 编程模型。

**Ring 与专家并行有什么不同？**
Ring 搬 KV 到持有 $Q$ 的卡，专家并行搬 token 到专家，通信对象不同。

相关：`google-flash-attention`、`google-gemini-longctx`、`google-jax-transformer`、`google-tpu-mesh`、`google-gqa-mqa`、`google-tpu-llm`、`google-moe-routing`、[[google-flash-attention]]、[[nvidia-flash-attn]]
