---
id: openai-grad-checkpoint
section: openai
order: 14
level: A
title: OpenAI：activation checkpoint 省显存的代价，和 ZeRO 怎么叠
quick: >-
  Checkpoint 不存整段激活，反向时再前向一遍，激活显存从 $O(L)$ 降到按切段的 $O(\sqrt{L})$ 或每层常数，代价是
  额外计算（常见多 20%–40% 时间）。ZeRO 切的是参数 / 梯度 / 优化器。长上下文两者都要，谁也替不了谁。
tags:
  - OpenAI
  - Gradient Checkpointing
  - ZeRO
  - Memory
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training Deep Nets with Sublinear Memory Cost
    url: https://arxiv.org/abs/1604.06174
    type: primary
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

OpenAI 规模的训练岗会问显存账，不一定点名某篇内部 wiki。公开来源是 checkpoint 的亚线性激活论文和 ZeRO。万亿怎么切并行见 `nvidia-trillion-train`；本题只讲「重计算」和「分片状态」怎么叠。Adam 状态有多大见 `openai-adamw`。

## 省的是哪一类显存，代价是什么

一次 Transformer 正向，每层要留下给反向用的激活，总量跟 $B\cdot T\cdot L\cdot d$ 走，长上下文时它占用甚至超过参数。Activation checkpointing（也叫 recompute）：只在段界存一份，反向走进这一段时把中间激活当场再算出来。

代价是多一次被 checkpoint 段的前向。若每层都 checkpoint，粗算正向约占 fwd+bwd 的三分之一，实际耗时常见 $+30\%$ 量级，换来激活显存掉一个档。切得更稀（每 $\sqrt{L}$ 层存一次）是论文里的亚线性方案，实现更烦，面试说结论即可。

选择性 checkpoint 更实际：重算贵的注意力 / FFN，LayerNorm、残差短连接留下。FlashAttention 已经不把完整 `[B,H,T,T]` 分值留在 HBM，和 checkpoint 是同一方向的「别存那么多激活」，但只覆盖注意力。

不要 checkpoint 到连需要的输入都丢了：段的入口张量必须留着，否则无法重算。和 `torch.no_grad` 不是一回事；这是训练图里的重计算边。

粗算一份 7B、bf16：$B=2$、$T=8\mathrm{k}$、$L=32$、$d=4096$，激活按每层一份 hidden 就有 $B T L d \times 2$ 字节，已经是数 GB，中间注意力和 FFN 还要再乘几份。同模型 Adam 状态大约 $12$ 字节/参数 $\approx 84$ GB 量级，ZeRO-2 能把它摊到多卡，但激活这份仍然每卡一份 microbatch。这就是「为什么 ZeRO 之后还要 checkpoint」。

## 和 ZeRO 正交，叠的顺序按瓶颈

ZeRO-1 分片优化器状态，ZeRO-2 再分片梯度，ZeRO-3 连参数也分片，用前 all-gather。它砍的是模型状态，跟 $B,T$ 关系弱，跟参数量关系强。Checkpoint 砍的是激活，跟 $B,T,L$ 强相关。

典型演变：

- 模型大、上下文短：先 ZeRO / 张量并行把参数放下，激活还好。
- 上下文一长，ZeRO-3 之后单卡参数已经很少，HBM 仍爆，那就是激活。这时加 checkpoint，而不是再加 ZeRO 级数。
- 两者一起用时，ZeRO-3 的 gather 和重计算都会吃时间，MFU 掉是预期。要用通信重叠和更粗的 checkpoint 段把额外前向藏住。

常见误区是：把 ZeRO 说成「也能少激活」；把 checkpoint 说成「能少 Adam 的 12 字节/参数」。面试画两列：左激活右状态，看现在哪一类显存超出了预算，再选工具。

数据并行下每张卡仍要一份当前 microbatch 的激活，所以纯堆 GPU 而不切 $T$（序列并行）也救不了超长上下文。那是第三条轴，点到即可。

和 `openai-prefill-decode` 对照：训练没有 逐 token 生成（decode） 循环，每步都是满 $T$ 的正向，所以激活峰值按最长文档走。packing 能降低 padding，但峰值仍由最长 packed 序列决定。checkpoint 解决的是峰值，不是平均浪费。

ZeRO 管状态分片，checkpoint 管用算力换激活；长上下文先看激活列，大参数先看状态列，两类都超过预算时，就同时使用两种方法。

## 追问

- **推理要 checkpoint 吗？** 一般不要。decode 没有整段反向。训练才有。
- **和梯度累积？** 累积降的是等价 batch，不降单步激活峰值。峰值仍由 microbatch 的 $B,T$ 决定。
- **offload 能不能代替？** CPU/NVMe offload 救参数和优化器，激活带宽更怕来回拷。长 $T$ 优先重算。
- **MoE？** 专家激活更碎，checkpoint 段要划在路由之后，避免重算时 all-to-all 两次，见 `openai-moe-aux-loss`。
