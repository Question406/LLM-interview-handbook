---
id: tencent-sft-parameter-gpu-utilization
section: systems
order: 104
level: S
title: 腾讯 WXG：如何估算 SFT 参数量与显卡利用率？
quick: "先声明全参还是 LoRA、dtype、并行策略和 batch，再分别估算训练显存与计算利用率。显存包括参数状态、激活和临时缓冲；计算侧同时看有效 tokens/s、MFU、通信等待和数据停顿，显存占用高并不代表算得快。"
tags:
  - Tencent
  - WXG
  - SFT
  - Training Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯WXG暑期实习面经-大模型算法（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/d3c8e5962e1b43aab21aa5af52423b56
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

我会把参数量、训练显存和计算利用率分别回答。用显存 $\div$ 2 字节倒推参数量，或者只用 `nvidia-smi` 的 occupied% 判断计算效率，都会漏掉状态和等待。先声明 dtype、全参 AdamW 还是 LoRA、world size、ZeRO/TP/PP，以及是否 checkpoint 和 packing，再估每卡显存；利用率则结合有效 tokens/s 和 MFU 判断。例如 7B 的 BF16 权重约 14GB，但全参训练的参数状态起点约 112GB，还没有加激活。

全参 mixed-precision AdamW 常见五份状态：BF16 权重 $2$、梯度 $2$、FP32 master $4$，Adam $m/v$ 各 $4$，合计约 $16$ bytes/param。对 $N$ 参数，未分片约 $16N$ 字节，7B 量级约 $112\,\mathrm{GB}$；$7\mathrm{B}\times 2=14\,\mathrm{GB}$ 只算了权重。LoRA 则按可训参数计算优化器等状态，底座仍可能占一份 BF16。

接着按数据并行度 $D$ 和 ZeRO stage 分状态：ZeRO-1 只分优化器，ZeRO-3 / FSDP 连参数也分，BF16 权重约 $2N/D$，Adam 状态也按 $/D$ 分，但 all-gather 时仍有峰值。然后加 activation（$\propto B\cdot T\cdot L\cdot d$）、attention 临时量、embedding / logits、通信 buffer 和 allocator 碎片。Activation 仍取决于本地 micro-batch，checkpoint 用重复前向计算换显存。

SFT 的序列长度不齐，常有 mask，名义 batch 相同，packing / padding 前后的有效 token 和峰值可能差一倍。显存跟最长序列走，计算利用率要看有效 token，单报“每卡几条”解释不了这两件事。白板可以先写 $N$ 和 dtype，再写 16 bytes/param，按 $D$ 与分片策略拆分，最后加激活的 $B,T,L$。

显存占用率用 `allocated / capacity` 看，碎片和等待都可能让它很高，例如占用 90% 时 GPU 仍可能在等通信。计算侧用 MFU，也就是实测 FLOPs 与 GPU 峰值之比。Transformer 每 token 前反向粗估约 $6N$ FLOPs，还要加 attention 的 $O(T^2)$，再用 profiler 核对 tokens/s、step time、SM occupancy、all-reduce 等待、data loader stall 和 loss scaling 溢出。

大模型大 batch 的 MFU 常见 30% 到 50%；低于 20% 时，先查 padding、通信、数据供给与 checkpoint 是否过密。占用 90%、MFU 20% 时优先排查等待。LoRA 的优化器虽小，小 kernel 开销仍可能压低 MFU，不能直接套预训练区间。Checkpoint 会增加重算，MFU 的分母仍是峰值 FLOPs，分子多了重算，显存降低而 step time 增长是预期代价。

实际回答时，从理论 token FLOPs 出发，用 profiler 指出通信、数据还是激活拖慢，再讲对应优化。没有给 $D$、全参 / LoRA 或 packing 条件，就先问清楚，避免报出一个条件变化后无法解释的 GB 数。

相关：`tencent-zero-123`、`sys-memory`、`tencent-zero3-qwen72b-mem`、`tencent-beyond-deepspeed`


## 真题记录

- 公司：腾讯 WXG
- 团队 / 岗位：大模型算法暑期实习
- 届别 / 流程：暑期实习；具体届别与轮次原帖未披露
- 面试时间：原帖未披露；帖子发布于 2026-05-25
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、实习性质与发帖时间明确，届别、轮次和面试日期未披露）
- 原始措辞：**“算模型 SFT 的参数量大小及显卡利用率”**
