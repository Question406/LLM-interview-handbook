---
id: google-tpu-decode
section: google
order: 29
level: S
title: Google：TPU 上 decode，MXU 吃不满、KV 带宽，和 GPU 怎么对照
quick: >-
  Prefill 是大 GEMM，MXU 能饱；decode 左矩阵行数是并发 $B$，TPU 收缩维 128，小 $B$ 格子空转。每步还要读整段
  KV，很快变带宽墙。和 GPU 对照：更小的 Tensor Core tile、paged KV、CUDA graph；TPU 要静态
  pad、连续批、GQA，必要时投机把 $M$ 抬上去。
tags:
  - Google
  - TPU
  - Decode
  - KV cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficiently Scaling Transformer Inference
    url: https://arxiv.org/abs/2211.05102
    type: primary
  - title: Fast Transformer Decoding — One Write-Head is All You Need (MQA)
    url: https://arxiv.org/abs/1911.02150
    type: primary
  - title: Cloud TPU System Architecture
    url: https://cloud.google.com/tpu/docs/system-architecture-tpu-vm
    type: secondary
  - title: TPU v4 — An Optically Reconfigurable Supercomputer
    url: https://arxiv.org/abs/2304.01433
    type: secondary
---

`google-tpu-llm` 讲训练期 MXU 和浅流水线。这题把 **生成期** 拆开：一步 query 长度 $T_q=1$ 时算力单元在饿，HBM 在喂历史 KV。Pope 等人在 TPU v4 上服务 PaLM 540B 的公开账是：大 batch 处理输入 token 可以很高 MFU（他们报到约 76%）；低延迟逐步生成即使量化权重，利用率也掉一截。Gemini serving / JAX 推理岗要听这本账，不是背 NVLink 必须等于 8。Mesh 轴见 `google-tpu-mesh`。

## 为什么 MXU 吃不满

TPU 峰值在脉动阵列 MXU 上，常见收缩维 128。GEMM $[M,K]\times[K,N]$ 要对齐这套粒度才饱。Prefill / 训练：$M=B\cdot T$，$T$ 上千，很肥。Decode：每个请求本步只有 1 个 query token，$M$ 退化成并发序列数 $B$。$B=8$ 时，128 那一维大部分格子空转。向量单元上的 LayerNorm / softmax 更帮不上 MXU 峰值。

算术强度也掉。权重主导时，一步 FFN 大约把 $[D, D_{\mathrm{ff}}]$ 从 HBM 读进来，只跟 $B$ 行激活乘一次。$B$ 小，时间模型是字节 / 带宽，不是 FLOPs / 峰值。Pope 文用分析模型在「权重稳态 / 激活稳态」布局之间切：小 $B$ 倾向把权重量在芯片上少搬；大 $B$ 激活体积反过来，布局要换。面试抓 **$B$ 改了通信体积和 MXU 利用率一起变**，不要背布局名字。静态 shape 和 `pjit` 见 `google-jax-pjit`。

所以 TPU decode 的第一杠杆是 **把有效 $M$ 做大**：连续批处理、等待拼 batch、投机解码一次验证 $\gamma$ 个位置（$M$ 变成 $B\cdot\gamma$ 量级），见 `google-spec-decode`。XLA 要静态 shape，短序列和空槽会 pad 到编译上限；pad 也占 MXU 但不出 token，等于付电费买空气。

## KV：decode 的另一堵墙

注意力一步 $T_q=1$，但要读历史

$$
\mathrm{KV\ bytes}\approx 2\cdot L\cdot T\cdot H_{\mathrm{kv}}\cdot d\cdot \mathrm{bytes}
$$

$T$ 从 8k 到 1M，线性涨两个数量级，窗口叙事见 `google-gemini-longctx`。MXU 就算吃饱了 FFN，注意力仍可能在等 HBM。GQA / MQA 把 $H_{\mathrm{kv}}$ 砍下来，是 Google 推理论文的一等杠杆，见 `google-gqa-mqa`。量化 cache、前缀缓存、多 query 共享 KV，全是打这条带宽，不是打 FLOPs 公式。

Splash / Pallas 式注意力在 prefill 上避免物化 $[T,T]$，见 `google-flash-attention`。Decode 的主要 IO 已经是读 KV，再融一次 softmax 红利有限。别把 Flash 说成 decode 的银弹。

口算一张卡：TPU v4 公开量级大约每芯片 32 GiB HBM、约 1.2 TB/s 带宽、bf16 矩阵算力约 275 TFLOP。单请求百万 token 的 KV 可以到百 GB 量级（随 $L,H_{\mathrm{kv}}$），根本塞不下，更谈不上 MXU 利用率。并发变成「HBM 里能活几段 cache」。

## 和 GPU 对照，只对齐三件事

| | TPU decode | GPU decode |
| --- | --- | --- |
| 矩阵单元粒度 | MXU 128，瘦 GEMM 更惨 | Tensor Core tile 更小，小 $B$ 没那么空，但仍内存墙 |
| 序列 / KV | 静态 pad、SPMD 切分 | PagedAttention、连续批更常见 |
| 逐步开销 | 编译图静态，host 启动也要摊 | CUDA graph / inflight batch 减 launch |
| 长 $T$ | MQA/GQA + 切 mesh | 同；再加分页 KV 防碎片 |

类比停在「decode = 小 $M$ 的 GEMM + 线性读 KV」。错的类比是把 DGX 的 kernel 名搬过来当 TPU 答案，或说 TPU 不能做投机——验证步是标准前向，TPU 友好，难的是草稿模型和主模型都要占 MXU。

MoE decode 还要降专家并行，见 `google-moe-routing`。专家过多、token 太少，all-to-all 比 MXU 空转更早爆。

错法：用训练 MFU 报 serving；说 decode 慢是因为 softmax 不在 MXU 就换近似注意力；只加芯片不加 $B$ 和 GQA。

## 追问

- **为什么 prefill 高 MFU、decode 远低于此仍算成功？** 分子是矩阵 FLOPs，decode 根本没那么多 FLOPs 可刷。要用 tokens/s、每焦耳 token、P99 逐步延迟，不要用训练口令。
- **$B$ 是不是越大越好？** 利用率升，逐步延迟和 KV 占用一起升。Pope 的故事是延迟-吞吐 Pareto，不是单点 MFU 冠军。
- **int8 权重量化帮谁？** 帮权重带宽和容量，不帮 KV 随 $T$ 涨。长上下文还是要砍 $H_{\mathrm{kv}}$ 或量化 cache。
- **连续批在 TPU 上难在哪？** 静态 shape 和重编译。实现是槽位复用加 pad，不是 GPU 上那种随意 ragged kernel。
