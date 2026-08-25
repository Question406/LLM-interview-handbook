---
id: apple-token-prune
section: apple
order: 20
level: S
title: Apple：视觉 token 剪枝 / 合并，质量和延迟怎么折？
quick: >-
  深一层注意力已经不看大部分图块，可以剪或合并。质量先死在小字和定位，延迟赢在 $N_{\mathrm{vis}}$ 降了 prefill 和
  KV。端上必须剪到固定剩余个数，动态长度会掉出 ANE。别把 GPU 上的 FastV 原样搬到手机。
tags:
  - Apple
  - Vision
  - Token Pruning
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: An Image is Worth 1/2 Tokens After Layer 2 (FastV)
    url: https://arxiv.org/abs/2403.06764
    type: primary
  - title: LLaVA-PruMerge — Adaptive Token Reduction for Efficient LMMs
    url: https://arxiv.org/abs/2403.15388
    type: primary
  - title: Token Merging for Fast and Efficient Vision Transformers (ToMe)
    url: https://arxiv.org/abs/2210.09461
    type: primary
  - title: Deploying Transformers on the Apple Neural Engine
    url: https://machinelearning.apple.com/research/neural-engine-transformers
    type: primary
---

端侧多模态把 $N_{\mathrm{vis}}$ 写进 $S_{\max}$ 之后，下一问就是「能不能少留一些」。FastV：LLaVA 类模型深层几乎不看视觉 token，第 2 层之后按注意力剪，公开大约 45% FLOPs 下降。PruMerge 用 ViT class token 注意力挑重要块再合并。ToMe 按相似度两两合并。这些都是公开方法，不是 AFM 内部 kernel。端上还要过 ANE 静态 shape，见 `apple-ane`、`apple-vision-edge`。不是逐字真题。

## 剪、合并、固定 $K$

记剪之前网格 $N$，之后 $K$。Prefill 注意力从 $O((N+N_{\mathrm{text}})^2)$ 降到 $O((K+N_{\mathrm{text}})^2)$，KV 字节按 $S$ 降。三种手段不要说成一种：

- **剪。** FastV 在指定层 $L_{\mathrm{cut}}$ 按平均注意力丢掉低分视觉 token。训练免费，推理插入。问题是 **$K$ 随图变**。GPU 可以动态；ANE 要静态 $K$。
- **合并。** ToMe / PruMerge 把相似块加成一个，信息比直接丢掉温和。输出仍应是固定 $K$，用 pad 补齐。
- **训练时压缩。** 连接器平均池化到 64/144，MM1 已经走这条，见 `apple-mm-train`。这是架构选择，不是 decode 期剪枝。

端侧正确导出：永远输出 $[B,K,D]$，不足 pad，mask 掉 pad。不要 `gather` 出变长序列再 `cat`。随机 scatter 容易掉 CPU。若必须按注意力挑 top-$K$，把 top-$K$ 写成静态 $K$，分数在 CPU 或允许的 op 上算完再送回 ANE。

## 质量先死在哪

剪背景、天空通常没事。先坏的是：

- **小字 / OCR / 验证码。** 高分注意力在问句 token 上，数字块可能分数低。屏幕理解不能按自然图的压缩比切，见 `apple-multimodal`。
- **指称定位。** 「左上那个开关」依赖空间网格。合并相邻块等于糊掉边界，框 IoU 掉。
- **多图。** 每张图各自 $K$，总前缀仍可能打满 $S_{\max}$。

评测把 VQA 总分和 OCR / grounding 切片分开，延迟看 TTFT 和 decode 带宽，见 `apple-afm-eval`。公开 FastV 在通用榜上能近似持平，不代表通知截图上持平。

错法：把 14 倍压缩（PruMerge 在 LLaVA-1.5 上的平均宣传数字）当 Siri 默认；剪完不改 KV 写入长度，cache 里仍按 $N$ 分配等于没省 SRAM；训练不剪、推理激进剪，位置编码错位。RoPE 按剪后序列位置编，训练推理要一致。

和量化正交：权 2–4 bit、KV 8-bit 省的是字节，减不掉 $N_{\mathrm{vis}}$ 个 softmax 位置，见 `apple-ondevice-quant`、`apple-ondevice-kv`。先定 $K$，再量化。

具体账：576 视觉 token 的 prefill 注意力大约是 $576^2$ 量级；收到固定 $K=144$ 大约除以 16。端上若 SRAM 只够 4k 上下文，这 432 个坑是给工具 JSON 和生成的。剪完仍要测 OCR 切片：通用 VQA 持平、验证码掉点，就说明 $K$ 太小，不是「再量化一点」。ANE 上 $K$ 必须编译进图；同一款机型不要按内容动态改 $K$。

端上同一 $K$ 要写进编译图；按内容动态改 $K$ 会掉出 ANE。评测失败时先看 OCR 切片，再谈量化。

面试收尾主动报失败模式和评测切片，不要停在架构名词。

## 追问

- **为什么不全部交给连接器池化？** 池化是均匀的；问「读右下角」时均匀池化不可逆。问句相关剪枝更对题，但更难静态化。
- **视频能不能按帧剪？** 能，先抽帧再每帧固定 $K$。不要让帧数和每帧 token 都动态。
- **剪完还能 grounding 出框吗？** 要保留块到原图的索引。丢掉索引就只能出字不能点。
- **ANE 上注意力分数从哪来？** 若那层 softmax 本来就在 ANE，分数回读可能比不剪更贵。量完再决定 $L_{\mathrm{cut}}$，不要先抄论文的第 2 层。
