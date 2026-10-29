---
id: google-tpu-llm
section: google
order: 17
level: S
title: Google：TPU 上训 Transformer，MXU、流水线和 GPU 三维并行怎么对照
quick: >-
  TPU 训练 Transformer 时，要用大 GEMM 填满 $128\times 128$ 的 MXU，softmax、LayerNorm
  等算子则走向量单元。并行仍要考虑样本、层内矩阵和层间切分，但 PaLM 这类配置优先采用 Pod 内 data/model
  两轴，再按容量和拓扑决定是否加流水线，不能固定套用 $\mathrm{TP}=8$。
tags:
  - Google
  - TPU
  - MXU
  - Parallelism
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: PaLM — Scaling Language Modeling with Pathways
    url: 'https://arxiv.org/abs/2204.02311'
    type: primary
  - title: Cloud TPU System Architecture
    url: 'https://cloud.google.com/tpu/docs/system-architecture-tpu-vm'
    type: secondary
  - title: Efficiently Scaling Transformer Inference
    url: 'https://arxiv.org/abs/2211.05102'
    type: primary
  - title: GSPMD — General and Scalable Parallelization for ML Computation Graphs
    url: 'https://arxiv.org/abs/2105.04663'
    type: primary
---

## 可以这样回答

我会先让 Transformer 的大矩阵乘法填满 MXU，再按容量和互连成本选择 data/model 两轴切分，放不下时才考虑流水线。比如训练的矩阵行数是 $B\cdot T$，通常足够大；decode 退化到并发数 $B$，同一套布局的利用率就可能差很多。Mesh 轴的命名见 `google-tpu-mesh`，这里重点解释芯片执行和并行取舍。

Attention 里 $QK^\top$ 和 $PV$ 是 GEMM，可以上 MXU；行内 softmax 不是。把 $[T,T]$ 写到 HBM 再读回来做 softmax，MXU 在等内存。TPU 上的 Splash / Pallas attention 和 FlashAttention 做同一件事：tile 留在 VMEM，见 `google-flash-attention`。TPU 也能通过分块和融合实现精确 attention。

## 技术备查

我会先让 Transformer 的大矩阵乘法填满 MXU，再按容量和互连成本选择 data/model 两轴切分，放不下时才考虑流水线。比如训练的矩阵行数是 $B\cdot T$，通常足够大；decode 退化到并发数 $B$，同一套布局的利用率就可能差很多。Mesh 轴的命名见 `google-tpu-mesh`，这里重点解释芯片执行和并行取舍。

TPU 的峰值在脉动阵列 MXU 上，常见收缩维是 128。大块 $X W$ 才喂得饱；LayerNorm、softmax、Gelu、reduction 走向量 / 标量单元，带宽和 MXU 不是同一条曲线。所以：

- $d_{\mathrm{model}}$、$d_{\mathrm{ff}}$、$B\cdot T$ 尽量对齐 128 的倍数。差 1 个 token 的动态长度，XLA 会 pad；你不 pad，编译器也会。
- Prefill / 训练：$[B\cdot T, D]\times[D, D]$ 矩阵行数较大，MFU 较高。
- Decode：$T=1$，左矩阵行数是并发 $B$。$B=8$ 时 MXU 大部分格子空转。这是 TPU serving 必须靠 batch / continuous batching 的原因，和 GPU Tensor Core 怕瘦 GEMM 是同一类问题，只是 128 这个粒度更硬。

Attention 里 $QK^\top$ 和 $PV$ 是 GEMM，可以上 MXU；行内 softmax 不是。把 $[T,T]$ 写到 HBM 再读回来做 softmax，MXU 在等内存。TPU 上的 Splash / Pallas attention 和 FlashAttention 做同一件事：tile 留在 VMEM，见 `google-flash-attention`。TPU 也能通过分块和融合实现精确 attention。

MFU 我当诊断工具：理论峰值按 MXU 算。掉下去先看是 GEMM 的矩阵行数太少、是等待 ICI、还是重计算 / 流水线气泡，不要先改学习率。JAX 里层怎么 `scan` / `remat` 见 `google-jax-transformer`。

GPU 三维并行口头禅：节点内 TP，节点间 PP，最后 DP。TPU Pod 内部 ICI 比较匀，层内 model 轴 + 样本 data 轴往往够把一层塞进芯片，还不引入 PP 的气泡。PaLM 540B：Pod 内 data+model，跨两个 v4 Pod 再加一路 DP，而不是把 118 层切成很深的 stage。跨 Pod 那一层见 `google-palm-pathways`。

真要 PP，原因通常是：激活 + 参数 + 优化器，2D 切完仍然塞不下；或你想把不同 stage 映射到不同 Pod。代价在 TPU 上比 GPU 更显眼：

- XLA 静态 shape，microbatch 数量和每段长度都是编译常数。
- 气泡比例大约随 stage 数涨、随 microbatch 数降。stage 很深、microbatch 开不大（显存或数据不够），MFU 先被气泡吃掉。
- 某 stage 开了更狠的 remat，负载不齐，1F1B 的公式要重算。

GSPMD 可以把流水线也做成一条 mesh 轴，Python 仍写完整网络。API 和手写 GPipe 调度不同，气泡账相同。我的起点是先检查 2D 切分是否够用，再用实际容量和通信成本判断 PP 是否值得。

| 切什么 | GPU 常见做法 | TPU 上 Transformer |
| --- | --- | --- |
| 样本 / 梯度 | DP、ZeRO | data 轴 all-reduce / reduce-scatter |
| 层内大矩阵、多 head | TP，常绑 8 卡 NVLink | model 轴，宽度跟 ICI 维走，不是 8 |
| 层与层 | PP + microbatch | 可选；PaLM 规模优先跨 Pod DP |
| 超长 $T$ | 序列并行、ring | 再加 seq 轴，或 blockwise，见 `google-block-attn` |
| 专家 | EP all-to-all | 专家维独立轴，逐 token 生成（decode） 要降 EP，见 `google-moe-routing` |

类比停在「参数、激活、优化器状态」三本账。错的类比是把 DGX 的 $\mathrm{TP}=8$ 当常数。TPU 上 model 轴取 2、4、16 都可以，取决于那一维 ICI 和每层同步次数。

布局：激活 $[B, T, D]$ 的 $B$ 走 data、$D$ 走 model 是默认；$T$ 很长再切 $T$。权重 $[D, 4D]$ 的输出通道走 model。标错一次，GSPMD 会插一次隐式 reshard，MFU 莫名掉，日志里不像你手写的 all-reduce 那么好搜。固定中间激活的分片方式用 `with_sharding_constraint`，见 `google-jax-pjit`。

## 追问

**为什么 decode 的 MXU 利用率差？**
收缩维还够，但 batch 维只有并发数。continuous batching 是在增加 MXU 上的矩阵行数。

**TPU 上 FSDP 叫什么？**
还是参数分片 + 按需 gather。名字随意，字节和通信时机才重要。

**和 GPU 比谁更适合深 PP？**
GPU 跨节点带宽差一截，深 PP 常见。TPU Pod 内更匀，先 2D；跨 Pod 再考虑 DP 或浅 PP。

**bf16 在 MXU 上够吗？**
训练默认够。softmax / 累加仍要更高精度的累加器，这是数值问题；别说成「TPU 不支持 fp32」。
