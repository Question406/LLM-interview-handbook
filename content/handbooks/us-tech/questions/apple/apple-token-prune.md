---
id: apple-token-prune
section: apple
order: 20
level: S
title: Apple：视觉 token 剪枝 / 合并，质量和延迟怎么折？
quick: >-
  视觉 token 可以按 attention 剪掉或按相似度合并，减少后续 prefill 和 KV 开销，但小字和定位通常先受损。on-device
  要把剩余数量固定为 $K$ 并保留原图索引；分别测 OCR、grounding 和 VQA，再决定压缩比例。
tags:
  - Apple
  - Vision
  - Token Pruning
  - Latency
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: An Image is Worth 1/2 Tokens After Layer 2 (FastV)
    url: 'https://arxiv.org/abs/2403.06764'
    type: primary
  - title: LLaVA-PruMerge — Adaptive Token Reduction for Efficient LMMs
    url: 'https://arxiv.org/abs/2403.15388'
    type: primary
  - title: Token Merging for Fast and Efficient Vision Transformers (ToMe)
    url: 'https://arxiv.org/abs/2210.09461'
    type: primary
  - title: Deploying Transformers on the Apple Neural Engine
    url: 'https://machinelearning.apple.com/research/neural-engine-transformers'
    type: primary
---

## 可以这样回答

视觉 token 剪枝或合并，是用少一些图块表示换后续 prefill 和 KV 的成本。比如背景可以压掉不少，小字和 button outlines 却可能一压就丢，因此要把 OCR、grounding 和通用 VQA 分开验证。

FastV 在第 2 层后按 attention 剪枝，公开约降 45% FLOPs；PruMerge 用 ViT class token attention 挑块后合并，ToMe 按相似度两两合并。这些是公开方法，不能当作 AFM 内部实现。on-device 还要让 $N_{\mathrm{vis}}$ 适配 $S_{\max}$ 和 ANE 静态 shape，见 `apple-ane`、`apple-vision-edge`。

## 技术备查

视觉 token 剪枝或合并，是用少一些图块表示换后续 prefill 和 KV 的成本。比如背景可以压掉不少，小字和 button outlines 却可能一压就丢，因此要把 OCR、grounding 和通用 VQA 分开验证。

FastV 在第 2 层后按 attention 剪枝，公开约降 45% FLOPs；PruMerge 用 ViT class token attention 挑块后合并，ToMe 按相似度两两合并。这些是公开方法，不能当作 AFM 内部实现。on-device 还要让 $N_{\mathrm{vis}}$ 适配 $S_{\max}$ 和 ANE 静态 shape，见 `apple-ane`、`apple-vision-edge`。

## 剪、合并、固定 $K$

记剪之前网格 $N$，之后 $K$。Prefill attention 从 $O((N+N_{\mathrm{text}})^2)$ 降到 $O((K+N_{\mathrm{text}})^2)$，KV 字节按 $S$ 降。三种手段不要说成一种：

- 剪。FastV 在指定层 $L_{\mathrm{cut}}$ 按平均 attention 丢掉低分视觉 token。训练免费，推理插入。问题是 $K$ 随图变。GPU 可以动态；ANE 要静态 $K$。
- 合并。ToMe / PruMerge 把相似块加成一个，信息比直接丢掉温和。输出仍应是固定 $K$，用 pad 补齐。
- 训练时压缩。连接器 mean pooling 到 64/144，MM1 已经走这条，见 `apple-mm-train`。这是架构选择，不是 逐 token 生成（decode） 期剪枝。

on-device 正确导出：永远输出 $[B,K,D]$，不足 pad，mask 掉 pad。不要 `gather` 出变长序列再 `cat`。随机 scatter 容易掉 CPU。若必须按 attention 挑 top-$K$，把 top-$K$ 写成静态 $K$，分数在 CPU 或允许的 op 上算完再送回 ANE。

## 优先检查小字和定位质量

剪背景、天空通常没事。先坏的是：

- 小字 / OCR / 验证码。高分 attention 在问句 token 上，数字块可能分数低。屏幕理解不能按自然图的压缩比切，见 `apple-multimodal`。
- 指称定位。「左上那个开关」依赖空间网格。合并相邻块等于丢掉 spatial boundaries，框 交并比（IoU，即两个区域的交集与并集之比） 掉。
- 多图。每张图各自 $K$，总前缀仍可能打满 $S_{\max}$。

评测把 VQA 总分和 OCR / grounding evaluation slices 分开，延迟看 首个 token 的等待时间（TTFT） 和 decode 带宽，见 `apple-afm-eval`。公开 FastV 在通用榜上能近似持平，不代表通知截图上持平。

PruMerge 在 LLaVA-1.5 上宣传的平均 14 倍压缩，不能直接当作 Siri 的默认预算。剪完还要改 KV 写入长度，否则仍按 $N$ 分配就省不下 SRAM；训练不剪、推理激进剪也可能造成 positional encoding 错位。RoPE 按剪后序列位置编，训练推理要一致。

和 quantization 正交：权 2–4 bit、KV 8-bit 省的是字节，减不掉 $N_{\mathrm{vis}}$ 个 softmax 位置，见 `apple-ondevice-quant`、`apple-ondevice-kv`。先定 $K$，再 quantization。

具体账：576 视觉 token 的 输入 prefill attention 大约是 $576^2$ 量级；收到固定 $K=144$ 大约除以 16。on-device 若 SRAM 只够 4k 上下文，这 432 个 token 位置是给工具 JSON 和生成的。剪完仍要测 OCR evaluation slices：通用 VQA 持平、验证码掉点，就说明 $K$ 太小，不是「再 quantization 一点」。ANE 上 $K$ 必须编译进图；同一款机型不要按内容动态改 $K$。评测失败时先看 OCR evaluation slices，再谈 quantization。

## 追问

**为什么不全部交给连接器 pooling？**
pooling 是均匀的；问「读右下角」时均匀 pooling 不可逆。问句相关剪枝更对题，但更难静态化。
**视频能不能按帧剪？**
能，先抽帧再每帧固定 $K$。不要让帧数和每帧 token 都动态。
**剪完还能 grounding 出框吗？**
要保留块到原图的索引。丢掉索引就只能出字不能点。
**ANE 上 attention 分数从哪来？**
若那层 softmax 本来就在 ANE，分数回读可能比不剪更贵。量完再决定 $L_{\mathrm{cut}}$，不要先抄论文的第 2 层。
