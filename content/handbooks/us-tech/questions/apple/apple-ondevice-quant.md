---
id: apple-ondevice-quant
section: apple
order: 4
level: S
title: Apple：端侧权重量化 / KV 量化，ANE 上 mask 的 -inf 还安全吗？
quick: >-
  权走调色板（k-means 码本，混合 2/4-bit，公开约 3.7 bpw），KV 走 8-bit，用 LoRA 把精度捞回来。ANE 上
  softmax 不要赌 IEEE $-\infty$：用 fp16 可表示的大负数，mask 放在反量化之后的高精度里。int8 分数溢出或
  wrap 会漏看未来 token。
tags:
  - Apple
  - Quantization
  - KV Cache
  - ANE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

这不是把 NVIDIA 那道 INT8 映射再背一遍。Apple Intelligence 岗问量化，要落到能塞进 iPhone 内存、能在 Neural Engine 上跑、mask 仍然因果。公开技术叙述在 2024 / 2025 的 foundation model 报告里，不是某次现场的逐字题。对称 / 非对称公式可以借 `nvidia-int8-quant`，但面试官听的是 ANE 和 KV。Exponent 指南也把 quantization 和 on-device limits 列为 MLE 基本盘。

## 权、激活、KV 不是一种量化

2024 报告里，端侧约 3B 模型在 ANE 上对投影权做 palettization：每 16 列或行共享一本查找表，k-means 出 16 个中心，也就是 4-bit 码本，块可以很大（公开写到十万量级）。Embedding 因为输入输出共享，按通道 8-bit。再把一部分层压到 2-bit，平均大约 3.5 bpw，生产取约 3.7 bpw。2025 更新更狠：端侧权 2-bit QAT，embedding 4-bit，KV cache 8-bit，再用低秩 adapter 补质量。

三句话分开说：

- 权决定模型能不能驻留。3B 乘 2 byte 大约 6 GB，塞不进当时的高端机；3.7 bpw 大约 1.4 GB 量级，加上 KV 和系统才谈得上。
- 激活决定算子能不能走低比特通道。ANE 主精度是 fp16；乱引入 Python 字面量 fp32 会整段掉到 GPU 或 CPU，见 `apple-ane`。
- KV决定长上下文还跑不跑得动。Decode 是带宽墙，8-bit KV 几乎是半价读。2025 还把模型切成两段，第二段复用第一段末层的 KV，cache 再降约 37.5%。

质量靠 accuracy-recovery LoRA（公开 rank 16，adapter 自身 16-bit，几十 MB），不是靠口头「4-bit 无损」。产品 adapter 从这份 recovery 初始化，再为邮件摘要、通知摘要各训一份，见 `apple-personalize`。Palettization 本身就是按块 k-means，手写聚类见 `apple-kmeans`。

## Mask：$-\infty$ 在量化图里会撒谎

因果 / padding mask 的契约是：非法位置 softmax 后必须是 0。PyTorch 习惯 `masked_fill` 填 $-\infty$。端上有三层坑。

1. IEEE $-\infty$ 和 $0\cdot\infty$。Softmax 里对 $-\infty$ 做 `exp` 应为 0。但 padding 位的 value 常是 0，attention 实现里一旦出现 $0\times\infty$，fp16 会出 `NaN`，整行注意力烂掉。ANE 公开实现里更进一步：硬件 softmax 不能当 IEEE $-\infty$ 一定正确，用 fp16 可表示的大负数（常见 $-10^4$ 到 $-4\times 10^4$）。$e^{-40000}$ 在 fp16 下已经下溢成 0，同时避开 NaN。
2. 分数若量化到 int8。int8 没有 $-\infty$。若先量化 $QK^\top$ 再加 mask，mask 会被 clip 到 $-128$。反量化 $\hat s = s(q-z)$ 之后，这个「最负」可能只是 $-5$，softmax 仍会给未来 token 百分之几的质量，表现为泄漏未来或泄漏 padding。正确顺序：反量化到 fp16，再加 mask，再 softmax。不要在 int8 分数上加 $-10^9$，那个数会 wrap。
3. KV 8-bit。$K,V$ 量化后，score 仍建议在 fp16 累加。Scale 按 head 或按 token 存；outlier 通道会把 $s$ 拉大，同样的 int8 最小值在反量化后「不够负」。GQA 下 cache 形状是 $[B,H_{\mathrm{kv}},S,d_h]$，mask 要能广播到 query head，shape 错了是 silent 的，见 `apple-mha-code` 和 `google-gqa-mqa`。

白板验收：同一前缀，量化 KV 加有限 mask，greedy 解码要和 fp16 全量注意力在短序列上逐 token 对得上；对不上先查 mask，再查 RoPE 是否在量化前旋转。

## 我会怎么收这道题

先问「量化的是权、激活还是 KV」。再画一条 decode 路径：从 palettized 权查出 fp16 激活，算出当前 $q,k,v$，写入 8-bit cache，反量化历史 KV，在 fp16 加 mask，softmax，加权 $V$。然后主动说：int8 映射公式和 `nvidia-int8-quant` 一样，但 ANE 不保证 $-\infty$，生产 mask 是有限大负数；校准用 Talaria 一类工具看每层比特，而不是全局一个 $s$。Palettization 的码本就是按块 k-means，手写见 `apple-kmeans`。

不要承诺 W8A8 一定更快。端上 decode 往往是读权加读 KV。权已经 2–4 bit 之后，下一刀是 KV 和 GQA，不是再把 softmax 也量化烂。和 `apple-topk-sample` 连起来：logits 若仍在 CPU 上做小 $k$ 采样，fp32 的 $-\infty$ 可以；一旦采样也进量化图，同样要用有限 mask。

## 追问

- **2-bit 权为什么还能用？** QAT 加上 recovery adapter。纯 PTQ 到 2-bit 通常崩。公开数字是先压再捞，不是一步 min/max。
- **Padding 用 0 当 mask 行吗？** 不行。Softmax 会把质量分给未来。必须是足够负，且加在 softmax 前。
- **动态量化每步算 min/max？** 权静态；KV / 激活可以按 token 动态。每步统计有开销，端上更常见静态权加分组 KV scale。
- **和 Private Cloud Compute 的关系？** 量化是为了留在设备上。上 PCC 的是更大的 server 模型，压缩配方不同（公开有 ASTC、约 3.56 bpw），不要把两套数混在一个 INT8 里。
