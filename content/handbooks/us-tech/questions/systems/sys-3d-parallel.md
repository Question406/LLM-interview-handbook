---
id: sys-3d-parallel
section: systems
order: 1
level: S
title: 系统：DP+TP+PP 三维并行怎么选切分，通信体积直觉
quick: "先看单层能否放下，把频繁同步的 TP 尽量留在 NVLink 域，再用 PP 分层，剩余卡做 DP。TP 通信随激活增加，DP 随参数增加，PP 还要留意 microbatch 不足造成的流水线气泡。"
tags:
  - NVIDIA
  - Megatron
  - Parallelism
  - Training
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Megatron-LM — Training Multi-Billion Parameter Language Models Using Model Parallelism
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
  - title: Sequence Parallelism — Long Sequence Training from System Perspective
    url: https://arxiv.org/abs/2105.13120
    type: primary
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
---

我会先按单层显存和网络拓扑选 TP，再按深度配 PP，剩余资源给 DP。比如同一台 8 卡机器，TP 通常先考虑 $4$ 或 $8$，让每层频繁同步留在 NVLink / NVSwitch 内，避免跨 IB 的延迟反复进入关键路径。

这也是 NVIDIA Megatron / NeMo、Meta Llama 和 Google GSPMD 一类训练系统会面对的选择。OpenAI 式追问会进一步要求估字节数，说明 TP 跨 IB 的代价。整体规模见 `nvidia-trillion-train`，层内切分见 `nvidia-tensor-parallel`，流水线气泡见 `nvidia-pipeline-bubble`。

| 轴 | 切的对象 | 每步通信 | 体积跟谁走 |
| --- | --- | --- | --- |
| TP | 层内 GEMM 的列/行、注意力头 | 每层 all-reduce / all-gather | 激活 $[B,T,h]$，乘层数 |
| PP | 连续若干层成 stage | 相邻 stage 点对点 | 一份 $[B_{\mu},T,h]$，次数少 |
| DP | 样本；ZeRO/FSDP 再切状态 | 梯度 reduce-scatter / all-gather | 参数量，每 step 一次 |

Megatron 列并行接行并行：前向在 MLP 出口 all-reduce 一次，反向对称再一次；注意力块同样两段。所以 TP 的集体通信次数跟层数、microbatch 成正比，单次 payload 跟 $B\cdot T\cdot h$ 成正比。序列变长时，TP 的通信量会随激活增长，通常比 DP 更早感到压力。DP 的集体通信是整份梯度，跟 $T$ 无关，可以藏在反向后几层后面。

PP 看起来通信少，代价在空转：warmup 时后段 GPU 闲。1F1B 把气泡压到大约 $(p-1)/m$，所以 microbatch 数 $m$ 要明显大于 stage 数 $p$。气泡占的是实际耗时，不是总线字节。

配置可以按下面顺序确定。$8\times 8\times 16$ 这类并行组合，要等显存与拓扑核对后再给。

1. 一层的参数和激活能不能放进单卡。放不下就加 TP。GEMM 被切太碎、喂不饱 Tensor Core 时停手。
2. TP 锁在 NVLink / NVSwitch 域。一台 8 卡就取 $4$ 或 $8$，几乎不跨节点。跨 IB 做 TP，每层同步会被延迟打死。
3. 模型深度仍放不下，上 PP。stage 对齐层数，词表和首尾大层单独处理。跨机用 IB 做 P2P 可以接受，因为不在每层热路径上。
4. 剩下的卡给 DP / ZeRO。全局 batch $= B_{\mu}\cdot m\cdot \mathrm{DP}$。batch 不够就梯度累积，别为了填 DP 把 $B_{\mu}$ 砍到 GEMM 变瘦。

核对性能时，TP 看激活流量，DP 看参数与梯度流量，PP 则同时看点对点传输和气泡。 长上下文时 $B\cdot T\cdot h$ 涨，先加序列并行（见 `sys-seq-parallel`），不要盲目加 TP。参数极大、激活还好时，ZeRO-3 比加深 TP 更对症（见 `sys-zero-stages`）。

纯 DP 训练万亿模型可能先放不下优化器；PP 切成五十段会增加气泡；TP 设成 64 且跨机柜，NCCL 延迟可能显著降低 MFU。用 Nsight 看 GPU 在计算、等 NVLink 还是等 IB，可以帮助判断是哪条轴的配置在拖慢。

设 $h=8192$，BF16。一次层内 all-reduce 激活大约 $2\cdot B_{\mathrm{local}}\cdot T\cdot h\cdot 2$ 字节量级，每层两次，几十层就是数十 GB 级的层内流量，必须走 NVLink。同一 step 的 DP 梯度若七十亿参数 BF16，体积更大，但只发生一次、可 overlap。两者不能比谁 GB 多，要比是不是在每层 critical path 上。

## 追问

**ZeRO-3 能替 TP 吗？**
能打散参数，但单层 GEMM 仍要一块完整矩阵。万亿 dense 通常仍要节点内 TP。
**PP 加深是不是总更省显存？**
每卡层少了，但 1F1B 要存多份 in-flight 激活，气泡也涨。有拐点。
**为什么 TP 不和 DP 换个网络？**
TP 同步频率高、对延迟敏感；DP 消息大、可 overlap。拓扑反了，Nsight 上一眼全是 NCCL wait。
