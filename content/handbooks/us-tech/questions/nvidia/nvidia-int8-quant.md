---
id: nvidia-int8-quant
section: nvidia
order: 2
level: A
title: NVIDIA：FP32 tensor 怎么量化到 INT8？非对称量化跟什么走？
quick: >-
  对称：$q=\mathrm{round}(x/s)$，$s=\max|x|/127$。非对称还要零点
  $z$，让实数 $0$ 能精确落到某个 int。校准用一小批激活统计；LLM 推理还要处理 per-channel 权重和 per-token
  激活。INT8 不等于一定更快，kernel 和 dequant 开销要算进去。
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

## 对称

给定张量 $x$，INT8 范围 $[-127,127]$（有的实现留 $-128$）：

$$
s=\frac{\max(|x|)}{127},\qquad q=\mathrm{clip}(\mathrm{round}(x/s),-127,127),\qquad \hat x=q\cdot s.
$$

实现细节：`round` 的平局规则、是否 per-tensor 还是 per-channel（权重沿输出通道各一个 $s$）。Per-channel 权重量化几乎是 LLM 默认，per-tensor 对 outlier 通道不友好。

## 非对称和零点

激活经常不是关于 $0$ 对称的。非对称：

$$
s=\frac{x_{\max}-x_{\min}}{255},\qquad
z=\mathrm{round}\left(-x_{\min}/s\right),\qquad
q=\mathrm{clip}(\mathrm{round}(x/s)+z,0,255).
$$

反量化 $\hat x=s\cdot(q-z)$。**零点的意义是让实数 $0$ 精确可表示**，这样 padding、ReLU 后的 $0$ 不会变成量化噪声。面试追问就答这句，不要只背公式。

校准：用一小批代表性激活收集 $x_{\min},x_{\max}$。用 max 对 outlier 敏感；用百分位（如 99.9%）更稳，但会 clip 极值。LLM 激活 outlier 是 SmoothQuant 要迁到权重上的原因：W8A8 才跑得动。只量化权（W8A16）实现更简单，激活仍 fp16，带宽收益小一些。

## 为什么 INT8 可能更慢

Tensor Core 有 INT8 吞吐，但：

- 通道数 / hidden 不能整除 Tensor Core tile，会走慢路径；
- dequant 和 layernorm 仍在高精度，kernel 切太碎；
- 逐 token 生成（decode） 通常受内存带宽限制，W8A16 读权更省，W8A8 还要量化激活，收益看 profile。

Nsight Compute 上看实际发出的 MMA 指令，不要假设 dtype 一改就 $\times 2$。这和 NVIDIA 岗「你有没有真的量过」的口味一致。

## 追问

- **动态量化 vs 静态？** 动态每步看当前 tensor 的 min/max，灵活但开销大；静态用校准统计，推理更快。LLM decode 常用静态权 + 动态或 per-token 激活。
- **INT4 呢？** 权重量化更狠，激活往往仍 8/16。GPTQ/AWQ 是训练后量化（PTQ）中寻找更合适的权重量化结果，不是简单 min/max。
- **和 FP8 训练的区别？** FP8 是训练时的混合精度，有 scaling recipe；INT8 这里是推理 PTQ。不要混成一个「低比特」。

## 相关题

- [[coding-int8-symm]]：同一个对称公式的白板编码版，要真写出 scale、饱和和 int32 累加的 dequant GEMM，并有单测。
- [[nvidia-fp8]]：本题追问「和 FP8 训练的区别」的完整版，讲延迟缩放和 amax 历史。
- [[nvidia-w4a8]]：INT4 权重加 FP8 激活的部署组合，接着回答「INT4 呢」那条追问。
- [[nvidia-fp8-kv]]：评委答完权重量化后常补问的 KV 量化，scale 和误差落在另一个张量上。
