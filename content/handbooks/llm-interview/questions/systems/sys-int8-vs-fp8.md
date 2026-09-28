---
id: sys-int8-vs-fp8
section: systems
order: 276
level: A
title: 训推分别用 INT8 还是 FP8？
quick: >-
  INT8 是定点，推理生态熟，适合权重量化，激活 outlier 要校准。FP8 是 8-bit 浮点（E4M3 / E5M2），动态范围更适合训练激活和梯度，H100
  Transformer Engine 原生支持。训练默认 BF16，有硬件再上 FP8；推理按质量和 kernel 在 FP8 / INT8 / INT4 里选。KV
  cache 量化是第三条线。
tags:
  - FP8
  - INT8
  - Quantization
  - Precision
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FP8 Formats for Deep Learning
    url: https://arxiv.org/abs/2209.05433
    type: primary
  - title: NVIDIA Transformer Engine FP8 primer
    url: https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html
    type: primary
  - title: SmoothQuant
    url: https://arxiv.org/abs/2211.10438
    type: primary
---

BF16 / FP16 / 训练 FP8 的动态范围见 `sys-precision`。GPTQ / AWQ / SmoothQuant 见 `sys-quant`。题目专门对打 INT8 vs FP8，以及训、推、KV 三套 dtype 不要混成一种「开了 8bit」。

## 表示差在哪

INT8：整数 $q$，用 scale（和 zero-point）还原 $x\approx s(q-z)$。范围固定，对激活 outlier 敏感，W8A8 常要 SmoothQuant 或 per-channel scale。生态老，TensorRT / 很多推理后端都熟。

FP8：E4M3 更准、范围更小；E5M2 范围更大、更粗。有指数位，更像「缩小的浮点」，训练时激活和梯度比较吃得消。依赖 Hopper / Blackwell 一类 Tensor Core；老卡没有原生 FP8 就谈不上更快。

## 训练侧

主流仍是 BF16 GEMM + FP32 master / Adam。INT8 几乎不当全流程训练精度：量化和反量化会挡梯度，QAT 太贵。H100 以上可以 FP8 training（Transformer Engine），embedding、lm_head、归一化、MoE router logits 常留 BF16/FP32。scale / amax 漂了会 silent 坏收敛，先证明稳定再报吞吐。

RL 里 actor 训练图和 rollout 引擎 dtype 可以不同。BF16 训、FP8 采，必须在训练图重算 $\log\pi$，见 `meituan-verl-recompute-logprob`。不要把引擎 logp 直接当 $\pi_{\mathrm{old}}$。

## 推理侧

质量优先：BF16 或 FP8。成本优先：权 INT8 / INT4，激活 8 或 16。Decode 吃权带宽，weight-only 往往比 W8A8 更常见；prefill 已是 compute-bound，降 bit 不一定涨速。没有对应 kernel 就要 dequant 回 16 位，等于多一次读写。

KV cache 是存 K/V 不是存权：FP8 / INT8 KV 降的是 HBM 和带宽，和 GPTQ 无关。RL 长 CoT 上 KV 往往比权更先爆，见 `sys-rl-memory`。

训练默认 BF16，有硬件再上 FP8；推理按质量和 kernel 在 FP8 / INT8 里选；INT8 训练不是默认答案。三套 dtype 分开报。

## 追问

- **W8A8 和 FP8 谁更准？** 没有万能答案。FP8 对激活更宽；INT8 配好 SmoothQuant 也能很稳。比较要锁同一校准集和同一 kernel。
- **rollout 用 INT8 权会怎样？** 采样分布相对训练图有隙，ratio 方差变大。TIS / 重算 logp 是标配，不是可选项。
- **MoE 呢？** router 对小扰动敏感，常单独保高精度，见 `sys-moe-train-infer-routing-mismatch`。
