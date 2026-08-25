---
id: google-block-attn
section: google
order: 24
level: S
title: Google：长序列注意力的 blockwise / ring IO，和 FlashAttention 什么关系
quick: >-
  FlashAttention 在单芯片上把 $QK^\top$ tile 留在 SRAM，HBM 流量从 $O(T^2)$ 降到大约 $O(T^2 d/M)$，数学仍是精确注意力。Blockwise
  按块算注意力再立刻做 FFN，砍的是层激活。Ring 把 KV 块在设备环上转，切的是 $T$。三件叠，不是三个互斥名词。
tags:
  - Google
  - Attention
  - Ring Attention
  - IO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: Blockwise Parallel Transformer for Large Context Models
    url: https://arxiv.org/abs/2305.19370
    type: primary
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: https://arxiv.org/abs/2310.01889
    type: primary
  - title: Gemini 1.5 — Unlocking multimodal understanding across millions of tokens of context
    url: https://arxiv.org/abs/2403.05530
    type: primary
---

Gemini 长上下文要训练和 serving 都碰到 $T$ 到百万。FlashAttention 论文不是 Google 的，但 TPU 岗照样问 IO。单卡 tile 见 `google-flash-attention`；窗口数字和 KV 成本见 `google-gemini-longctx`。这题往上问一层：块在芯片内、块在设备间、和 FFN 怎么叠，别把三个名字背成一种近似注意力。

## 三层 IO，别并成一句「我们用了 Flash」

标准注意力物化 $S=QK^\top$，形状 $[T,T]$，HBM 和激活爆掉。精确注意力的 FLOPs 仍是 $\Theta(T^2 d)$，谁也没改公式。

FlashAttention：在片上 SRAM（TPU 叫 VMEM）里对 $Q,K,V$ 分块，在线 softmax，不把 $S$ 写回 HBM。HBM 访问大约 $O(T^2 d^2/M)$，$M$ 是片上容量。反向重算 $P$ 而不是存它。它解决的是 **单设备上注意力核的带宽**。TPU 上 Splash / Pallas 做同一件事。

Blockwise Parallel Transformer（Liu et al.）：序列切成块，一块 query 对一块 KV 算完注意力，立刻把这块送进 FFN / 残差，再处理下一块。峰值激活不再需要整层 $[T, D]$ 的注意力输出和 FFN 中间同时在。它解决的是 **层内激活 HBM**，不是换一种注意力数学。块内仍然可以跑 Flash 式核。

Ring Attention：把序列沿设备切，$T/N$ 每卡。每卡拿自己的 $Q$，KV 块沿着环传一圈，本地算一块注意力，累加输出。通信量和计算可以重叠，前提是块够大、环上带宽够。它解决的是 **跨设备的序列并行**，让 $T$ 超出单卡 HBM。块内同样可以是 Flash。

所以关系是包含，不是替代：Ring 的一跳里跑 blockwise 的一块，一块里跑 Flash tile。面试说「Ring 取代了 Flash」是错的；说「有了 Flash 就不需要切 $T$」也是错的。单卡 HBM 仍按 $T$ 线性（KV）或按激活策略走。

## 和训练 / decode 怎么对表

训练 / prefill：$T$ 大，二次项和激活都痛。顺序通常是：先 Flash 式核（否则 $[T,T]$ 先炸），再 remat / scan 砍层激活，见 `google-jax-transformer`；再长就切 $T$（序列并行或 ring）。TPU mesh 上这是再加一条 `seq` 轴，见 `google-tpu-mesh`。

Decode：$T_q=1$，没有 $[T,T]$ 可物化。Flash 仍避免多余写回，但一等杠杆是 KV 头数和量化 cache，见 `google-gqa-mqa`。Ring 在 decode 上变成「历史 KV 分在多卡、每步收集」，通信是小消息，延迟墙。很多系统 prefill 切序列、decode 把 KV 收拢或按层流水，不要训练拓扑原样搬。

块大小是超参：太小，kernel 启动和 ring 同步压过计算；太大，VMEM / HBM 又塞不下。TPU 还要对齐 128 的 MXU，见 `google-tpu-llm`。XLA 静态 shape，块大小在编译期定死，变长请求靠 pad。

Ring 一圈的通信量大约是整段 KV 扫过每个设备：每跳 $O((T/N) d)$，共 $N$ 跳，总量 $O(T d)$，和把 KV all-gather 一遍同阶，但可以和本地注意力重叠。重叠不够时，ring 只是把 HBM 爆换成 ICI 延迟，没有免费午餐。

## 别和近似注意力混

Linformer、稀疏窗、线性注意力改的是数学，FLOPs 可以降到近线性，但不规则访存经常让墙钟输给精确 + Flash。Google 长上下文的公开叙事（Gemini 1.5）是能在百万 token 上做检索式任务，面试默认先讲精确注意力的 IO 栈，再谈要不要上稀疏 / 分层。窗口注意力仍然需要 Flash：局部 $S$ 也不该写回 HBM。

错法：说 blockwise 把复杂度变成 $O(T)$；说 ring 是另一种 softmax；把 MoE 专家并行和 ring 说成同一件事。专家并行搬的是 token 到专家，见 `google-moe-routing`；ring 搬的是 KV 块到持有 $Q$ 的卡。

## 追问

- **Ring 的正确性？** 每块用在线 softmax 的 $m,\ell$ 做 rescale 再累加，和单机分块同一套代数，精确（忽略浮点顺序）。归约树不同，bitwise 不必相同。
- **和流水线并行一起用吗？** 可以：PP 切层，ring 切 $T$。气泡和环同步叠在一起很难排，先看 2D mesh 是否够。
- **为什么 TPU 不直接抄 CUDA Flash？** 编程模型不同，IO 层次相同：tile 留在 VMEM，别把 $S$ 吐到 HBM。Splash 是这条线。
- **1M 训练必须 ring 吗？** 不是唯一路径。激活重算 + 序列并行 + Flash 也能堆。Ring 的卖点是通信隐藏和单卡不存全 KV。选哪条看 HBM 和 ICI，不要背论文标题。窗口数字和 KV 字节账见 `google-gemini-longctx`。

Serving 侧同一句话：prefill 用切 $T$ 的 IO 栈，decode 用 KV 布局，两套可以不同。

