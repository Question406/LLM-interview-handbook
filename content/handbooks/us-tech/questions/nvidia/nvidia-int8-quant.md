---
id: nvidia-int8-quant
section: nvidia
order: 2
level: A
title: NVIDIA：FP32 tensor 怎么量化到 INT8？非对称量化跟什么走？
quick: "对称量化用 $q=\\mathrm{round}(x/s)$、$s=\\max|x|/127$ 把浮点值映射到整数；非对称量化再引入零点 $z$，保证实数 $0$ 可以精确表示。范围来自校准统计，LLM 还要分别考虑 per-channel 权重和 per-token 激活，最后实测 kernel 和 dequant 开销才能判断是否加速。"
tags:
  - NVIDIA
  - Quantization
  - INT8
  - Inference
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: NVIDIA Interview Question Bank (1Point3Acres)
    url: https://www.1point3acres.com/interview/problems/company/nvidia
    type: secondary
  - title: TensorRT Developer Guide — Quantization
    url: https://docs.nvidia.com/deeplearning/tensorrt/latest/inference-library/work-with-quantized-types.html
    type: primary
  - title: SmoothQuant
    url: https://arxiv.org/abs/2211.10438
    type: primary
---

## 真题记录

- 公司：NVIDIA
- 来源：一亩三分地 NVIDIA 题库公开条目「FP32 Tensor to INT8 Quantization (with Asymmetric Quantization Follow-ups)」，2026-05 仍列在题库里
- 形态：coding / 数值题，随后追非对称、校准、以及为什么线上没加速

系统对比 GPTQ / AWQ / SmoothQuant 见 `sys-quant`。本题主要讲如何手写量化映射，这是 NVIDIA 面试里更常见的开口。

## 对称和非对称怎么映射

把 FP32 映射到 INT8，要先选 scale，再舍入和截断；非对称量化还需要一个 zero point，用来对齐实数的零。系统对比 GPTQ / AWQ / SmoothQuant 见 `sys-quant`，这里先把这套映射写清楚。


给定张量 $x$，INT8 范围 $[-127,127]$（有的实现留 $-128$）：

$$
s=\frac{\max(|x|)}{127},\qquad q=\mathrm{clip}(\mathrm{round}(x/s),-127,127),\qquad \hat x=q\cdot s.
$$

实现时要确定 `round` 如何处理恰好位于中间的值，还要决定整个 tensor 共用 scale，还是沿权重输出通道分别用一个 $s$。LLM 通常采用 per-channel 权重量化，因为单个 outlier 通道会拉大 per-tensor 的范围，使其他通道分到的精度变少。

激活的范围经常不以 $0$ 为中心，这时可以用非对称映射：

$$
s=\frac{x_{\max}-x_{\min}}{255},\qquad
z=\mathrm{round}\left(-x_{\min}/s\right),\qquad
q=\mathrm{clip}(\mathrm{round}(x/s)+z,0,255).
$$

反量化用 $\hat x=s\cdot(q-z)$。零点让实数 $0$ 能精确表示，因此 padding 和 ReLU 后的 $0$ 不会额外引入量化噪声。

校准：用一小批代表性激活收集 $x_{\min},x_{\max}$。用 max 对 outlier 敏感；用百分位（如 99.9%）更稳，但会 clip 极值。LLM 激活 outlier 是 SmoothQuant 要迁到权重上的原因：W8A8 才跑得动。只量化权（W8A16）实现更简单，激活仍 fp16，带宽收益小一些。

## 为什么 INT8 可能更慢

Tensor Core 有 INT8 吞吐，但：

- 通道数 / hidden 不能整除 Tensor Core tile，会走慢路径；
- dequant 和 layernorm 仍在高精度，kernel 切太碎；
- 逐 token 生成（decode） 通常受内存带宽限制，W8A16 读权更省，W8A8 还要量化激活，收益看 profile。

我会在 Nsight Compute 中检查实际发出的 MMA 指令，并测量端到端耗时；修改 dtype 本身并不能证明速度提高了 $\times 2$。

## 追问

- **动态量化 vs 静态？** 动态每步看当前 tensor 的 min/max，灵活但开销大；静态用校准统计，推理更快。LLM decode 常用静态权 + 动态或 per-token 激活。
- **INT4 呢？** 权重量化更狠，激活往往仍 8/16。GPTQ/AWQ 是训练后量化（PTQ）中寻找更合适的权重量化结果，不是简单 min/max。
- **和 FP8 训练的区别？** FP8 是训练时的混合精度，有 scaling recipe；INT8 这里是推理 PTQ。不要混成一个「低比特」。

## 相关题

- [[coding-int8-symm]]：同一个对称公式的白板编码版，要真写出 scale、饱和和 int32 累加的 dequant GEMM，并有单测。
- [[nvidia-fp8]]：本题追问「和 FP8 训练的区别」的完整版，讲延迟缩放和 amax 历史。
- [[nvidia-w4a8]]：INT4 权重加 FP8 激活的部署组合，接着回答「INT4 呢」那条追问。
- [[nvidia-fp8-kv]]：评委答完权重量化后常补问的 KV 量化，scale 和误差落在另一个张量上。
