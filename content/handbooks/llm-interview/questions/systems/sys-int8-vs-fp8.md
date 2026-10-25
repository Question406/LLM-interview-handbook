---
id: sys-int8-vs-fp8
section: systems
order: 276
level: A
title: 训推分别用 INT8 还是 FP8？
quick: "训练通常先用 BF16，硬件和稳定性允许再用 FP8；推理则按质量、带宽和 kernel 支持选择 FP8、INT8 或 INT4。INT8 适合成熟的权重量化路径，但激活 outlier 要校准；FP8 有指数位，动态范围更适合训练激活和梯度，H100 Transformer Engine 原生支持 E4M3 / E5M2。KV cache 的精度要单独选择。"
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

训练我会先用 BF16，确认硬件支持和收敛稳定后再上 FP8；推理则结合质量和 kernel 选择 INT8、FP8 或 INT4。比如 decode 受读权重带宽限制，weight-only 量化可能直接省带宽，prefill 已经受计算限制时却未必更快。权重、激活和 KV cache 是三份独立的精度选择，不能用一个「8bit」概括。BF16 / FP16 / 训练 FP8 的范围见 `sys-precision`，GPTQ / AWQ / SmoothQuant 见 `sys-quant`。

## 两种表示为什么适用不同场景

INT8 把数表示成整数 $q$，计算时用 scale 和 zero-point 还原 $x\approx s(q-z)$。范围固定，对激活 outlier 敏感，W8A8 常要 SmoothQuant 或 per-channel scale。生态老，TensorRT / 很多推理后端都熟。

FP8 的两种格式各有取舍：E4M3 更准、范围更小；E5M2 范围更大、更粗。有指数位，更像「缩小的浮点」，训练时激活和梯度比较吃得消。依赖 Hopper / Blackwell 一类 Tensor Core；老卡没有原生 FP8 就谈不上更快。

训练时还要考虑更新是否稳定。

主流仍是 BF16 GEMM + FP32 master / Adam。INT8 几乎不当全流程训练精度：量化和反量化会挡梯度，QAT 太贵。H100 以上可以 FP8 training（Transformer Engine），embedding、lm_head、归一化、MoE router logits 常留 BF16/FP32。scale 或 amax 偏移可能悄悄破坏收敛，先证明稳定再报吞吐。

强化学习（RL） 里 actor 训练图和 采样轨迹（rollout） 引擎 dtype 可以不同。BF16 训、FP8 采，必须在训练图重算 $\log\pi$，见 `meituan-verl-recompute-logprob`。不要把引擎 logp 直接当 $\pi_{\mathrm{old}}$。

推理时主要在质量、带宽和算子支持之间取舍。

质量优先时可以选 BF16 或 FP8；成本优先时，权重可以用 INT8 / INT4，激活则用 8 或 16 位。Decode 吃权带宽，weight-only 往往比 W8A8 更常见；输入预填充（prefill，即处理输入并建立缓存） 已是 compute-bound，降 bit 不一定涨速。没有对应 kernel 就要 dequant 回 16 位，等于多一次读写。

KV cache 是存 K/V 不是存权：FP8 / INT8 KV 降的是 HBM 和带宽，和 GPTQ 无关。RL 长 思维链（CoT，即分步推理过程） 上 KV 往往比权更先爆，见 `sys-rl-memory`。

训练默认 BF16，有硬件再上 FP8；推理按质量和 kernel 在 FP8 / INT8 里选；INT8 训练不是默认答案。三套 dtype 分开报。

## 追问

**W8A8 和 FP8 谁更准？**
没有万能答案。FP8 对激活更宽；INT8 配好 SmoothQuant 也能很稳。比较要锁同一校准集和同一 kernel。
**rollout 用 INT8 权会怎样？**
采样分布相对训练图有隙，ratio 方差变大。TIS / 重算 logp 是标配，不是可选项。
**MoE 呢？**
router 对小扰动敏感，常单独保高精度，见 `sys-moe-train-infer-routing-mismatch`。
