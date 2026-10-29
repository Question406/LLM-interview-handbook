---
id: google-tpu-mesh
section: google
order: 7
level: S
title: Google：TPU mesh / 把 batch 和模型维切到芯片上，和 GPU 三维并行怎么类比
quick: >-
  JAX mesh 给芯片定义逻辑轴，再用 PartitionSpec 声明数组怎样切：batch 可沿 data 轴，头或隐层维可沿 model
  轴。编译器根据切分安排集合通信，物理连接则由 ICI 提供。它和 GPU 的 TP$\times$PP$\times$DP
  都是在切参数、激活和状态，轴宽应按实际拓扑选择。
tags:
  - Google
  - TPU
  - Mesh
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
  - title: GSPMD — General and Scalable Parallelization for ML Computation Graphs
    url: 'https://arxiv.org/abs/2105.04663'
    type: primary
  - title: Cloud TPU System Architecture
    url: 'https://cloud.google.com/tpu/docs/system-architecture-tpu-vm'
    type: secondary
---

## 可以这样回答

我会先用 mesh 把芯片排成逻辑轴，再把 batch、模型宽度等张量维映射到这些轴，并让频繁通信的轴对齐更好的物理互连。比如 batch 沿 data 切、权重输出通道沿 model 切，前者分摊样本，后者分摊一层的参数和计算。PaLM 跨 Pod 的做法见 `google-palm-pathways`，这里先讨论单 Pod。

TPU Pod 里芯片用高速互连连成环面（v3/v4 常见 2D，更新代有 3D）。和 GPU 集群「盒内 NVLink、盒间 InfiniBand」那种两级带宽不同，Pod 内部更接近一张比较匀的网。所以 Google 代码里先 `Mesh(devices, axis_names)`，再给数组贴 `PartitionSpec`。

## 技术备查

我会先用 mesh 把芯片排成逻辑轴，再把 batch、模型宽度等张量维映射到这些轴，并让频繁通信的轴对齐更好的物理互连。比如 batch 沿 data 切、权重输出通道沿 model 切，前者分摊样本，后者分摊一层的参数和计算。PaLM 跨 Pod 的做法见 `google-palm-pathways`，这里先讨论单 Pod。

TPU Pod 里芯片用高速互连连成环面（v3/v4 常见 2D，更新代有 3D）。和 GPU 集群「盒内 NVLink、盒间 InfiniBand」那种两级带宽不同，Pod 内部更接近一张比较匀的网。所以 Google 代码里先 `Mesh(devices, axis_names)`，再给数组贴 `PartitionSpec`。

最简单的两轴声明可以写成：

```python
mesh = Mesh(devices.reshape(D, M), ("data", "model"))
# 激活 [B, T, D_model]：B 沿 data 切，模型宽沿 model 切
# 权重 [D_in, D_out]：输出通道沿 model 切
```

- **data 轴**：切 batch。每张芯片一份微批，反向对梯度 all-reduce（或 reduce-scatter）。对应 GPU 的 **DP / FSDP 的样本维**。
- **model 轴**：切层内矩阵的列或行、以及 attention head。对应 GPU 的 **张量并行 (TP)**。每层要在 model 轴上做 all-gather / all-reduce，延迟敏感，必须映射到 ICI 跳数少的方向。

第三轴常见两种：再切一层 FSDP（参数分片、激活仍按 data），或把 **流水线** 做成 `pp` 轴（层分成 stage）。TPU 上不一定先上 PP：单 Pod 芯片数够、ICI 够匀时，2D 的 data$\times$model 往往更干净。PaLM 是 Pod 内 data+model，跨两个 Pod 再加一路 DP，而不是 Megatron 式很深的 PP。

| 你要切的东西 | GPU 口头禅 | TPU mesh 怎么说 |
| --- | --- | --- |
| 样本 / 梯度同步 | DP、ZeRO | `P("data", ...)`，data 轴集合通信 |
| 层内大 GEMM、多 head | TP（常取 8，一盒） | `P(None, "model")`，model 轴对齐 ICI |
| 层与层 | PP + microbatch 填泡 | 可选 `pp` 轴，或 GSPMD 流水线 |
| 超长序列激活 | 序列 / 上下文并行 | 再加一条 `seq` 轴切 $T$ |
| 专家 | EP + all-to-all | 专家维贴独立 mesh 轴，见 `google-gemini-moe` |

类比停在三本账：参数、激活、优化器状态。万亿参数塞不进单芯片，必须有一条轴切权重；batch 太小则 data 轴利用率差。别把 `TP=8` 搬到 TPU 上：8 来自 DGX 拓扑。TPU 的 model 轴取 2、4、16 都可以，取决于那一维 ICI 和每层同步次数。

编译器（XLA GSPMD）看切分标注，不看你有没有手写 `all_reduce`。逻辑上写完整 matmul，它在 model 轴切开的地方插入通信。和手写 Megatron 的差别：你调的是轴和 PartitionSpec，通信模式是推导出来的。`pjit` / `shard_map` 怎么讲 SPMD，见 `google-jax-pjit`。

Batch 很小却把 data 轴拉满：每芯片 $B=1$，GEMM 瘦，MFU 崩。模型很宽却不切 model：单芯片 HBM 装不下一层。PP 太深：气泡和每 stage 的 padding 浪费，TPU 静态 shape 更痛。序列很长却只切 $B$：激活按 $B\cdot T\cdot L\cdot d$ 涨，该切 $T$ 或开重计算 / Flash 式核，见 `google-flash-attention`。

最后要检查物理映射。model 轴每层都频繁同步，如果映射到 ICI 较差的方向，就会额外等通信；所以逻辑 mesh 和物理环面的对应关系也属于调优的一部分。

## 追问

**FSDP 在 TPU 上叫什么？**
还是参数分片 + 按需 all-gather。实现上往往是 mesh 上多一条轴，或 ZeRO 风格的 `P("data")` 打在权重上。名字不重要，字节账重要。

**为什么 TPU 讨厌动态 shape？**
XLA 按静态 shape 编译。MoE 变长 dispatch、变长 逐 token 生成（decode） 都要 padding 到容量。这是 mesh 上 MoE 慢的常见原因。

**单芯片 debug 和多芯片不一致？**
切分改变了归约顺序和浮点，bitwise 不一定相同。功能正确看 loss 曲线和下游，不要用 CPU 单核 bit exact 当 TPU SPMD 的验收。

**和 GPU 3D 哪个更「先进」？**
都是切这三维。差别在你能不能按带宽层次选轴，不在硬件品牌。
