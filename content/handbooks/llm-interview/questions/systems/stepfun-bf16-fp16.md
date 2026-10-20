---
id: stepfun-bf16-fp16
section: systems
order: 144
level: A
title: 阶跃星辰：BF16 和 FP16 有什么区别？
quick: "都是 16 位。FP16 指数 5 位、精度更高但易溢出，常需 loss scaling；BF16 指数 8 位与 FP32 同宽，动态范围大、精度略低，大模型训练更常用。"
tags:
  - StepFun
  - Mixed Precision
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阶跃星辰大模型算法实习面经
    url: https://www.nowcoder.com/feed/main/detail/933afb27edd84b438682fd5bba95fbb3
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“BF16和FP16的区别？”**

常见误区是：把「16 位」说成 16 字节，或以为 BF16 更「准」。两者都是 2 字节，不是 16 字节。FP16 尾数更多、更准，但指数窄、易 Inf；BF16 范围接近 FP32，尾数更少。大模型训练选 BF16 是因为不容易溢出，不是因为更精确。原帖还问 bit 与 byte：8 bit = 1 byte，核算显存时 $N$ 个 BF16 参数约占 $2N$ 字节。

## 位宽怎么记

- FP16：1-5-10，表示范围大约到 $6\times 10^4$。softmax、梯度累加容易 Inf，混合精度要动态 loss scaling。
- BF16：1-8-7，指数与 FP32 同宽，范围大约到 $10^{38}$，几乎可当「短 FP32」。乘法稳，但尾数 7 bit，敏感归约仍建议 FP32 累加。

面试先画 exponent / mantissa，再讲 overflow vs rounding。只说「BF16 更新」没有信息量。和 `sys-precision` 同一套表，这题再补 bit/byte，避免显存账算错一个数量级。同面若再问 GPU 死锁，精度问题不会导致死锁。溢出是 Inf，通信 hang 是集体契约，见 `stepfun-gpu-deadlock`。

## 训练为什么偏 BF16

Ampere / Hopper 对 BF16 Tensor Core 支持好，大模型激活和梯度动态范围大，FP16 要反复调 loss scale，scale 不稳会 skip update 或溢出。BF16 常可关复杂 scaling。Master weight / 优化器状态仍用 FP32，这是混合精度，不是全程 16 位：GEMM 用 16 位，Adam 动量仍是 32 位。推理两者都常见，还要和 KV 量化、FP8 分开谈：存储 dtype $\neq$ 累加 dtype。显存账按 2 字节/参数算权，再单独加优化器，不要把「16 位训练」理解成整图砍半。

## 追问

- **BF16 比 FP16 更准吗？** 不。尾数更少，相对误差更大。它赢在范围，输在精度。
- **为什么还要 FP32 累加？** 残差、softmax、梯度 all-reduce 对误差敏感，16 位累加会漂。算用 BF16，加用 FP32。
- **16 位是 16 字节吗？** 不是。16 bit = 2 byte。70B 参数 BF16 权重大约 $140\,\mathrm{GB}$，不是 $1120\,\mathrm{GB}$。
- **和 FP8 什么关系？** FP8 更省带宽，但要 scale 和格式（E4M3/E5M2）。BF16 仍是训练默认落地精度，见 `sys-precision`。
- **softmax 能全程 BF16 吗？** 能跑，但建议 FP32 累加。尾数 7 bit 在指数差大时误差更明显，长序列尤其如此。
