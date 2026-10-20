---
id: sys-precision
section: systems
order: 4
level: A
title: BF16 vs FP16 vs FP8：训练时怎么理解？
quick: "BF16 和 FP32 都有 8 位指数，动态范围大，训练时更不容易溢出。FP16 的尾数位更多，但指数位少，常需缩放损失来保护小梯度。FP8 更省带宽和算力，但需要管理缩放系数、选择格式，敏感层仍要保留高精度。"
tags:
  - Precision
  - Training
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
  - title: FP8 Formats for Deep Learning
    url: https://arxiv.org/abs/2209.05433
    type: primary
---

这块容易以为 bit 越少就越快、越稳，或把训练 dtype、KV dtype、累加 dtype 混成一种「精度」。训练我先问三件事：会不会 overflow、舍入是否可接受、硬件 kernel 是否真吃得下。BF16 赢在范围，FP16 赢在尾数，FP8 赢在带宽，三者都不是全程替代 FP32。面经里的 BF16/FP16 对照见 `stepfun-bf16-fp16`。

## FP16 与 BF16

FP16：5 exponent / 10 fraction（另有 hidden bit）。范围大约到 $6\times 10^4$，softmax / 梯度易 Inf，要动态 损失（loss） scale。BF16：8 exponent / 7 fraction，指数与 FP32 同宽，范围大约到 $10^{38}$，大模型训练更稳，几乎可关复杂 scaling。

选 BF16 不是因为它更准：尾数更少，相对误差更大。Master weight 和优化器状态仍常用 FP32：16 位只承担 GEMM 和激活。敏感归约（softmax、residual、某些 all-reduce）建议高精累加。

## FP8：E4M3 / E5M2 与 scale

常见两种：E4M3 更准、范围更小；E5M2 范围更大、更粗。训练需要 per-tensor / per-channel scale、amax history，有时 stochastic rounding。并非所有 op 都适合 FP8：embedding、lm_head、归一化、路由 logits 常留 BF16/FP32。

推理侧还有 FP8 KV（`--sglang-kv-cache-dtype fp8_e4m3`），那是存储精度，和训练 FP8 不是同一套 recipe，见 `slime-sglang-native`。

## 实践怎么讲

大模型训练我默认 BF16；必须 FP16 时把 loss scale 和 skip-update 讲清楚。上 FP8 先证明 kernel 和 scale 稳定，再谈吞吐；scale 偏移可能悄悄破坏收敛。显存账：参数 $N$ 个，BF16 约 $2N$ 字节，再加 FP32 优化器（Adam 约 $8N$）和激活。ZeRO 切的是后面这两项，见 `sys-zero`。不要把「开了 BF16」说成显存砍半：权砍半，Adam 动量和 variance 往往还在 32 位。

## 追问

- **为什么大模型不爱 FP16？** 动态范围不够，loss scale 调参本身成为不稳定源。
- **FP8 一定更快吗？** 硬件不支持、dequant 重、或模型已是 compute-bound 时，bit 降了也不快，见 `sys-quant`。
- **训练 BF16、采样轨迹（rollout） FP8 要重算 logp 吗？** 要。分布不一致，ratio 必须用训练图 $\log\pi$。
- **8 bit 是 1 字节吗？** 是。核算显存时不要把「16 位」说成 16 字节。
- **敏感层为什么不量化？** embedding / ln / lm_head 的动态范围和误差会直接进 logits。先量化线性层，再决定要不要动它们。
