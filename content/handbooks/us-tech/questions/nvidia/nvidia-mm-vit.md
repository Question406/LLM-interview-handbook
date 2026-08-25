---
id: nvidia-mm-vit
section: nvidia
order: 27
level: A
title: NVIDIA：视觉 encoder 和 LLM 同卡 serving，prefill 形状为什么不齐
quick: >-
  ViT 一次吃 $[B_{\mathrm{img}}, N_{\mathrm{patch}}, D_v]$ 的规整 GEMM；LLM prefill 吃的是
  文本加视觉 token 拼起来的变长 $[N_{\mathrm{tok}}, D]$。两者 batch 轴、序列长、算力墙都不一样，不能当同一个
  IFB 步里的同形状核。同卡是为了省 embedding 的 PCIe，代价是调度要拆 encoder 阶段和 decoder
  prefill 阶段。
tags:
  - NVIDIA
  - Multimodal
  - ViT
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Multimodal Support in TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/multi-modality.html
    type: primary
  - title: End to end workflow to run a Multimodal model — Triton TensorRT-LLM Backend
    url: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/tensorrtllm_backend/docs/multimodal.html
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: primary
  - title: Long Sequences — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/long-sequence.html
    type: primary
---

## 题怎么来的

LLaVA / VILA / Qwen2-VL 一类在 TensorRT-LLM 里是「视觉 encoder + LLM decoder」。Triton 后端文档把视觉引擎和 LLM 引擎拆开建；新一点的 LLM-API 可以同进程跑。NVIDIA serving 岗问的不是 CLIP 原理，是：**同卡时一步 scheduler 看见的 token 形状为什么和纯文本 prefill 对不上**。我会先写两条流水线的 shape，再讲混 batch 和 chunked prefill 不能切 encoder 内部。

## 两条流水线，两种矩阵

视觉侧（ViT / CLIP 塔）：图像预处理成 pixel，encoder 输出对齐到 LLM 隐空间的 embedding。固定分辨率例子：336、patch 14，大约 $N_{\mathrm{patch}}=576$（再加 class token 看实现）。形状规整：

$$
X_{\mathrm{vit}}:[B_{\mathrm{img}}, N_{\mathrm{patch}}, D_v],\qquad
E_{\mathrm{vis}}:[B_{\mathrm{img}}, N_{\mathrm{vis}}, D].
$$

这是完整前向，自注意力是对称的、没有 KV cache、没有逐步 decode。算术强度高，GEMM 好看，batch 维是 **图的张数**，不是请求数。

LLM 侧：文本 embedding 和 $E_{\mathrm{vis}}$ 按占位符插进同一条序列。一条请求的 prefill 长是 $T_{\mathrm{text}}+N_{\mathrm{vis}}$（多图再加）。IFB 一步看到的是 packed token：

$$
X_{\mathrm{llm}}:[N_{\mathrm{tok}}, D],\quad N_{\mathrm{tok}}=\sum_i (T_{\mathrm{text},i}+N_{\mathrm{vis},i}).
$$

Attention 走 paged KV，因果 mask，新视觉 token 也要写 cache，见 `nvidia-paged-kv`。墙的位置：encoder 偏算力；LLM 长 prefill 也偏算力；随后 decode 偏带宽。同卡意味着 **同一块 SM 时间片要在两种核之间切换**，不是把 ViT 的 $[B,576,D]$ 和 LLM 的 ragged pack 拼成一次 GEMM。

动态分辨率（Qwen2-VL 一类）更狠：$N_{\mathrm{vis}}$ 跟图尺寸走，同一 batch 里 256 和 2048 视觉 token 坐一桌。ViT 若还想组成一个 batch，就要 padding 或 packing；NaViT 式 pack 是训练技巧，线上常变成「逐图或按分辨率分桶」。面试把「形状不齐」说成 **$N_{\mathrm{patch}}$ 和 $T_{\mathrm{text}}$ 不是一个轴上的同质长度**。

## 同卡混部的调度坑

纯文本 IFB 以 `max_num_tokens` 为预算，一步里 decode 行 + chunked prefill，见 `nvidia-inflight-batch`、`nvidia-chunked-prefill`。多模态多出来的坑：

1. **Encoder 不可切成 LLM 那种 token chunk。** ViT 的层间依赖是整图注意力。Chunked prefill 切的是 **已经算好的视觉 embedding 在 LLM 里的消费**，不是把一张图的 patch 分两步跑完 encoder。TRT-LLM 后来给 llava-next / Qwen2 补的 multimodal chunked prefill，文档强调 embedding cache / 只跑尚未消费的视觉段。把一张图的 encoder 斩两半当 chunk，hidden 对不上。

2. **Token budget 被图打满。** 一张图 576–2k token，再加长 caption，$U=2048$ 可能只够半张图的 LLM prefill。正在飞的 decode TBT 被这条视觉 prefill 抬成尖刺，比纯文本 8k 还常见，因为请求一来就带着图。

3. **Batch 轴错位。** 4 条文本 decode（$B=4$、$T_q=1$）和 1 张待编码的图。Encoder 想要 $B_{\mathrm{img}}\ge 8$ 才饱和；LLM decode 已经在抢 HBM。同卡要么让图排队凑 encoder batch（TTFT 差），要么 $B_{\mathrm{img}}=1$ 跑瘦 ViT（利用率差）。分卡（encoder 池 / decode 池）把 embedding 经 PCIe 或 NVLink 送过去，形状问题变成带宽问题。

4. **KV 容量。** 视觉 token 全部进 cache，fp16 时一张图就按百兆级往上加。要先 FP8 KV / 分页，见 `nvidia-fp8-kv`。Prefix 共享对「同一张图多次问」有用，对每张用户图没有。

Triton 路径常是两个模型：`multimodal_encoder` 和 LLM engine，用 ensemble 串。这是显式拆阶段，形状各自固定，代价是中间 embedding 的一次设备间拷。同进程同卡省拷，scheduler 必须自己插入 encoder 阶段，不能假装只有一种 prefill kernel。

## 我怎么答取舍

延迟敏感、图少：同卡，encoder 插在请求 admit 之后、LLM prefill 之前，必要时让 decode 步退避。吞吐敏感、图大：encoder 分池，embedding 缓存按图 hash 复用。Chunk 只切 LLM 侧，page 对齐仍要遵守。别承诺「多模态 IFB 和文本一样只要把图当 token」。图在 encoder 里不是 token，进 LLM 之后才是。

## 追问

- **视觉 token 能和文本 token 做一次 FA 吗？** 进 LLM 之后可以，它们已经在同一 $D$ 上。Encoder 内部的 ViT 注意力是另一张图、另一套核。
- **无图请求和有图请求混跑？** 可以。Encoder 对无图请求是空。LLM 步里 $N_{\mathrm{vis}}=0$，ragged pack 本来就允许变长。
- **视频呢？** 帧数乘 $N_{\mathrm{patch}}$，prefill 更不齐。必须抽帧或时序压缩，否则 `max_num_tokens` 没有上限。
- **量化 encoder 吗？** TRT-LLM 备注里视觉侧常仍 FP16，和 LLM 的 W4A8 不是一把开关。质量回归先看 OCR / 细粒度定位。
