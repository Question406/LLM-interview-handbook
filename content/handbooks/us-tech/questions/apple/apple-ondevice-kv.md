---
id: apple-ondevice-kv
section: apple
order: 12
level: S
title: Apple：端侧 KV 的显存和带宽怎么估，GQA 加量化 cache 各省哪一刀？
quick: >-
  Decode 每步都要扫完整段 KV，墙是手机 DRAM / ANE SRAM，不是 HBM。字节大约 $2 L H_{\mathrm{kv}} d_h S
  b$。GQA 砍 $H_{\mathrm{kv}}$，8-bit cache 砍 $b$，2025 的跨块 KV 共享再砍一层深度。权已经 2–4 bit
  之后，长上下文的下一刀是 KV，不是再压 softmax。
tags:
  - Apple
  - KV Cache
  - GQA
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

量化卡 `apple-ondevice-quant` 问的是 palettization 和 mask 的 $-\infty$。这题问的是 decode 为什么读不动历史。Apple 2024 就写 GQA 和 Neural Engine 上的 KV 更新；2025 明确 KV cache 8-bit，并把模型切成两段、第二段复用第一段末层 KV，cache 大约再降 37.5%。云端同一笔账见 `sys-kv-quant`、`google-gqa-mqa`，这里把墙换成手机带宽和预分配静态 shape，见 `apple-ane`。

## 先写字节，再谈技巧

一份 KV 的驻留大约：

$$
\mathrm{Bytes} \approx 2 \cdot L \cdot H_{\mathrm{kv}} \cdot d_h \cdot S \cdot b
$$

$2$ 是 K 和 V，$L$ 层数，$S$ 是已写入的上下文，$b$ 是每元素字节。Query head 数 $H_q$ 不进 cache。GQA 把 $H_{\mathrm{kv}}$ 收到 $H_q/g$；MQA 收到 1。形状是 $[B,H_{\mathrm{kv}},S_{\max},d_h]$，算注意力时再 broadcast 到 $H_q$，不要把 cache 存成 $H_q$ 份，否则 GQA 白做。手写 attention 见 `apple-mha-code`。

端上 decode 每步 $T_q=1$，算术强度接近 1：FLOPs 和从 DRAM 搬来的 KV 字节同一量级。权已经 palettize 到约 3.7 或 2 bpw 之后，读权变便宜，长 $S$ 时 KV 成为主带宽。所以面试顺序是：GQA $\to$ 量化 cache $\to$ 少算一些层的 KV，而不是「再 INT8 一下 softmax」。

三刀正交，不要说成一种量化：

- GQA。线性降 $H_{\mathrm{kv}}$。质量敏感时不要直接 MQA；AFM 公开走 grouped-query。
- 8-bit KV。$b: 2\to 1$（相对 fp16）。Scale 按 head 或按 token 存。Score 仍建议在 fp16 累加；mask 加在反量化之后，见 `apple-ondevice-quant`。K 的 outlier 常沿通道，乱 per-tensor 会把注意力打歪，云端同构讨论见 `sys-kv-quant`。
- KV sharing（2025）。模型按约 5:3 深度切成两块，block 2 的 KV 直接用 block 1 末层的 cache，公开写降约 37.5%，还能让 prefill 跳过第二块的 KV 生成。这是改深度结构，不是 PTQ。

ANE 还要求预分配 $S_{\max}$，不能 `torch.cat` 沿时间维涨。Stateful 模型把 KV 登记成跨 `predict` 的 state；写入是定点 slice。随机 scatter 容易掉出 ANE。档位太稀浪费 SRAM，太密二进制膨胀，见 `apple-ane`。

## 带宽例子，用来证明你算过

假设端侧 $L=28$，$d_h=128$，$H_{\mathrm{kv}}=8$（GQA），$S=4096$，fp16：

$$
2\cdot 28\cdot 8\cdot 128\cdot 4096\cdot 2 \approx 470\ \mathrm{MB}
$$

每步 decode 都要扫这一份（加上当前层的计算）。改 8-bit 大约减半；若 $H_{\mathrm{kv}}$ 从 32 收到 8，再除以 4；KV sharing 再乘约 0.625。三刀叠完，同一 4k 窗口才谈得上和系统、激活抢内存。视觉前缀也占这条 cache，见 `apple-multimodal`：减不掉已经写进去的图像 token。

不要承诺「8-bit KV 无损」。短上下文 greedy 要和 fp16 cache 对得上；长上下文看的是摘要接地和指令跟随，不是再刷一遍 MMLU。RoPE 必须在量化前转到 $K$，否则 cache 里是未旋转向量，decode 错位。

## 我会怎么答

先问上下文上限和 batch（端上常常 $B=1$，但预分配仍按 $S_{\max}$）。再写公式，标出 $H_{\mathrm{kv}}$、$b$、$L_{\mathrm{effective}}$ 三处旋钮。主动说失败模式：cache 存成 $H_q$；INT8 分数上加 mask；动态 `cat` 掉出 ANE；投机拒绝后不回滚 KV，见 `apple-spec-edge`、`openai-speculative-decoding`。

评测：同一前缀 greedy 对齐；Instruments 上看 decode 是否被内存墙拖住；热和功耗跟 $S$ 走，连续对话会降频，见 `apple-afm-eval`。采样仍在 CPU 的小 $k$ 上可以，见 `apple-topk-sample`，那不改变 KV 带宽。

## 追问

- **GQA 和 8-bit 谁先做？** 训练时就 GQA，几乎零推理税。8-bit 是推理压缩，要校准和可能的 recovery adapter。长窗口两者都要。
- **Paged KV 端上有吗？** 云端分页是为了并发和碎片。端上 $B\approx 1$、静态 $S_{\max}$，预分配更符合 ANE。不要把 vLLM 故事原样搬到 iPhone。
- **为什么不把 KV 也 2-bit？** 权可以 QAT 到 2-bit；KV 每 token 写入、对 softmax 敏感。公开停在 8-bit 是质量和带宽的折中。
- **第二段复用第一段 KV，注意力还对吗？** 设计假设后段可以从前段末层的压缩状态继续。这是架构选择，要在长上下文任务上验，不能口头保证等于满 KV。
