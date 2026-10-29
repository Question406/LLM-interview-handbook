---
id: nvidia-fp8
section: nvidia
order: 7
level: A
title: NVIDIA：FP8 训练 scale、延迟缩放、和 INT8 推理量化不是同一件事
quick: >-
  FP8 训练用 E4M3、E5M2 加速正反向 GEMM，并靠每张量的 scale 和 amax
  控制范围；延迟缩放复用历史统计，减少当前张量的同步。INT8 推理则依赖
  PTQ/QAT、calibration、整数映射和零点等配方，我会分别检查两者的误差、溢出和 kernel 支持。
tags:
  - NVIDIA
  - FP8
  - Transformer Engine
  - Mixed Precision
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Scaling Language Model Training to a Trillion Parameters Using Megatron
    url: >-
      https://developer.nvidia.com/blog/scaling-language-model-training-to-a-trillion-parameters-using-megatron/
    type: secondary
  - title: >-
      SmoothQuant — Accurate and Efficient Post-Training Quantization for Large
      Language Models
    url: 'https://arxiv.org/abs/2211.10438'
    type: primary
  - title: NVIDIA Transformer Engine
    url: 'https://github.com/NVIDIA/TransformerEngine'
    type: primary
---

## 可以这样回答

FP8 训练是混合精度训练，主要用浮点 GEMM 配合 scale 和 amax 历史来加速正反向。例如当前张量突然变大，沿用旧 scale 就可能溢出，所以还要检测和更新尺度。INT8 推理的核心则是 calibration 与整数映射，SmoothQuant 解决其中的 outlier 问题，见 `nvidia-int8-quant`。

两种常见编码：E4M3 尾数多、范围窄，正向权重 / 激活常用；E5M2 指数多、范围宽，梯度常用。都是浮点，没有 INT8 那个零点 $z$。Hopper Tensor Core 原生吃 FP8 MMA，throughput 比 bf16 高一档，但 LN、softmax、残差仍留在较高精度，和 AMP 一样是部分低精度。

## 技术备查

FP8 训练是混合精度训练，主要用浮点 GEMM 配合 scale 和 amax 历史来加速正反向。例如当前张量突然变大，沿用旧 scale 就可能溢出，所以还要检测和更新尺度。INT8 推理的核心则是 calibration 与整数映射，SmoothQuant 解决其中的 outlier 问题，见 `nvidia-int8-quant`。

## scale 和延迟缩放如何工作

两种常见编码：E4M3 尾数多、范围窄，正向权重 / 激活常用；E5M2 指数多、范围宽，梯度常用。都是浮点，没有 INT8 那个零点 $z$。Hopper Tensor Core 原生吃 FP8 MMA，throughput 比 bf16 高一档，但 LN、softmax、残差仍留在较高精度，和 AMP 一样是部分低精度。

值域不够，就要 scale。对一块张量 $x$，

$$
x_{\mathrm{fp8}}=\mathrm{cast}(x\cdot s),\qquad s=\frac{\mathrm{fp8\_max}}{\mathrm{amax}(x)\cdot 2^{\mathrm{margin}}}.
$$

GEMM 在 FP8 里做完，再用输入 scale、权重 scale 把累加器（通常 fp32）还原。Scale 可以 per-tensor，也可以沿通道 / 块（更新的 MXFP8 / block scale）。面试先把 per-tensor 说清：每张量一个 $s$，amax 是 $\max|x|$。

当前 tensor 的 amax 要整块扫一遍，还常和主机同步，训练步里插这种同步会把 kernel 切碎。Delayed scaling 会从前几步的 amax 历史中取 max，历史长度从几十到一千，用它计算本步的 $s$；本步测得的 amax 只更新历史，留给后续使用。这样减少了当前步的同步，但用到的统计会滞后。

风险是 loss spike 或 LR 跳变时，数值分布突然变大，旧 $s$ 过大，FP8 会溢出成 inf。Transformer Engine 用 margin、amax 历史、以及 inf 检测把 scale 拉回来。刚启动或切换阶段，历史空，要有 warmup。当前缩放（每步看当前 amax）更稳、更慢；面试说清取舍，不要只背「delayed 是默认」。

这和 `nvidia-loss-scale` 的 loss scaling 不是一把尺子。Loss scale 乘在整个 loss 上，保护 fp16 梯度下溢；FP8 的 $s$ 是每张量把数值塞进 E4M3 格子。训练里两套可以同时在，职责不同。

## 和 INT8 推理怎样区分

FP8 训练：目的是同一次反向里加速 GEMM；数值是浮点 E4M3/E5M2；统计是训练步内 amax（可延迟）；权重仍在更新；outlier 靠更高动态范围加 per-tensor / block scale。

INT8 推理：目的是部署降带宽、用整数 Tensor Core；数值是 $q=\mathrm{round}(x/s)+z$；统计来自 calibration 集 min/max 或百分位；PTQ 常冻结权重；outlier 用 SmoothQuant 把激活尖峰迁到权重。

SmoothQuant 的核心是：LLM 激活沿通道有固定 outlier，INT8 格子装不下，于是离线做 $X_{\mathrm{smooth}}=X\mathrm{diag}(s)^{-1}$、$W_{\mathrm{smooth}}=\mathrm{diag}(s)W$。FP8 训练一般不迁 outlier；E4M3 的动态范围比 INT8 友好，但仍要 scale，不是「换成 FP8 就不用管范围」。

推理也可以走 FP8（Hopper 上的 TensorRT-LLM），那是推理配方，仍然没有零点那套非对称 INT8。不要把「8 bit」三个字并成一种量化。手写 INT8 映射见 `nvidia-int8-quant`。

## 追问

**没有 Hopper 能训 FP8 吗？**
能模拟，没有原生 MMA 就没有那一档 throughput，面试别把模拟当线上加速。Ada 有 FP8 推理相关能力，训练栈仍以 Hopper / Blackwell + TE 为主。

**Per-tensor scale 不够怎么办？**
沿输出通道或沿块再切 scale。更碎更准，kernel 和 scale 传输更烦。MXFP8 是这条线的后续，没做过就说「块级 scale 在补 per-tensor 的动态范围」。

**和 INT8 能不能同一套 calibration？**
不能直接套。INT8 calibration 是部署前一次；FP8 训练的 amax 每个 iteration 都在动。把 calibration 表硬接到训练 GEMM 上会漂。

**溢出了怎么看？**
看 inf/nan 计数、amax 是否打满 fp8_max、以及 TE 有没有把 scale 下调。和 GradScaler 的 skip step 类似，但作用点在 tensor scale，不是全局 loss scale。

## 相关题

- [[sys-mixed-precision]]：和本题高度重合，同样强调「训练 FP8 不是推理量化」，但重点放在 FP32 master weights 和 BF16/FP16 loss scaling。
- [[sys-fp8-gemm]]：只谈推理侧的 FP8 GEMM，scale 粒度（DeepSeek-V3 的 tile/block）和 DeepGEMM 一类核。
- [[nvidia-int8-quant]]：本题用来做对比的 INT8 推理量化，讲对称/非对称和 calibration。
- [[nvidia-fp8-kv]]：同样是 FP8，但量化的是 KV cache，scale 来自每条请求自己的 K/V 分布。
