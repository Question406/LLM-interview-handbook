---
id: sys-mixed-precision
section: systems
order: 17
level: S
title: 系统：BF16/FP8 训练，master weights，和推理量化分开
quick: >-
  训练混合精度是 GEMM 走窄格式，更新走 FP32 master。BF16 指数够，通常不用全局 loss scale；FP16 要。FP8
  再加每张量 amax。推理量化是冻住的整数或 FP8 部署，没有反向、没有 master，不要和训练配方并成一套。
tags:
  - NVIDIA
  - Mixed Precision
  - Transformer Engine
  - Quantization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
  - title: FP8 Formats for Deep Learning
    url: https://arxiv.org/abs/2209.05433
    type: primary
  - title: NVIDIA Transformer Engine
    url: https://github.com/NVIDIA/TransformerEngine
    type: primary
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

## 题怎么来的

NVIDIA 训推都会问「8 bit / 16 bit」。我会先挡：训练混合精度（AMP / Transformer Engine）和推理 PTQ 不是一件事。Hopper 上两者都能快，但溢出模型、是否更新权重、要不要 master copy 全不同。FP8 每张量 scale 见 `nvidia-fp8`；FP16 全局 $S$ 见 `nvidia-loss-scale`。本题把 master weights 和「别跟 serving 量化混」讲清。

KV 量化、权重量化是部署带宽问题，不要在这题里展开成同一套 scale 故事，见 `sys-kv-quant`。

## 算用窄的，存一份 FP32 真身

2017 混合精度的核心不是「模型改成 FP16」，而是：前向/反向 GEMM 走 FP16 或 BF16，**一份 FP32 master 权重**给优化器。小更新在 FP16 尾数里会冲掉；Adam 的一阶二阶矩更需要宽累加。典型一步：

1. Master $W_{32}$ 转成 $W_{16}$ 做 GEMM。
2. 反向得到窄格式梯度，升到 FP32，除 loss scale（若有），Adam 更新 $W_{32}$。
3. 再拷回 $W_{16}$ 给下一步。

BF16 指数和 FP32 同宽，动态范围够，LLM 预训练默认它，通常 **不需要** 全局 loss scale。FP16 指数窄，小梯度下溢成 0，才乘 $S$；$S$ 太大就 overflow，要 skip step，见 `nvidia-loss-scale`。LN、softmax、残差累加仍常留 FP32，和「整网都是 BF16」不是一句话。

ZeRO / FSDP 分片的是这份状态：Adam 约 12 字节/参数的 FP32 矩，加上 master。只把 GEMM 改 BF16 而不保留 master，长训会静默退化。8-bit Adam 是另一笔税，别和 FP8 GEMM 说成同一个开关。分布式下 inf 标志要 all-reduce，一张卡 skip、别的卡 step，权重立刻分叉，见 `sys-loss-spike`。

## FP8 训练不是 INT8 推理

FP8 训练（Transformer Engine）：E4M3 正向、E5M2 梯度常见；每张量或每块一个 scale，delayed amax 用历史最大值避免每步同步。GEMM 在 Tensor Core 上，累加器仍是 FP32，再除 scale。权重仍在更新，master 仍在。分布突变时旧 amax 过时会打 inf，这是训练稳定性问题。

推理量化：GPTQ / AWQ / SmoothQuant / INT8 TensorRT，目的是冻住权重、减带宽。有零点、校准集、outlier 迁移。没有反向，没有 Adam，没有「skip 这一 step」。KV 的 INT8/FP8 更是 cache 带宽问题，见 `sys-kv-quant`。Hopper 上推理也可以走 FP8，那是部署配方，仍然没有训练那套 delayed amax 历史。

错误并法：把 SmoothQuant 的通道 scale 接到 TE 的 per-tensor amax 上；用校准表当训练 GEMM 的 scale；说「开了 FP8 就可以删 master」。面试先问：这条 8 bit 路径有没有反向。有，就是混合精度；没有，就是量化部署。

通信也不要和计算精度绑死。梯度 all-reduce 常用 FP32 或 FP16 累加；用 BF16 规约会让换 DP 度数后曲线对不上，见 `sys-allreduce-reducescatter`。FP8 训练里 amax 历史要进 checkpoint，否则 resume 后第一步用错 scale，尖刺像 `sys-loss-spike`。

## 追问

- **为什么 BF16 还要 master？** 指数够只保证不炸，尾数仍短。长时间小更新累加在 16 bit 上会丢。Adam 矩更不该只留 BF16。
- **FP8 还要 GradScaler 吗？** 通常不要全局 $S$。溢出走 TE 的 amax / inf 计数。和 FP16 loss scale 叠在一起要说清两把尺子。
- **ZeRO-3 下 master 在哪？** 分片后每卡只持有自己那片 FP32 状态；all-gather 的是这一层用来算的窄权重。峰值仍会短暂出现一层完整拷贝。
- **推理 FP8 和训练 FP8 能共用 scale 吗？** 不能直接套。训练 amax 每步在动；推理 scale 来自校准或运行时观察，没有优化器。
- **LN / softmax 也要进 FP8 吗？** 通常不要。窄格式放在 GEMM；归一化和概率仍留较宽累加，和 AMP 一样是部分低精度。
- **删了 master 长训会怎样？** 小更新在窄尾数里冲掉，表面 loss 还在动，过长距离质量掉。这是静默的，不是立刻 NaN。

- **通信用 BF16 规约行不行？** 能更快，但换 DP 度数后累加顺序变，曲线可能对不上。要对齐再谈数值。
