---
id: msft-llava
section: microsoft
order: 6
level: A
title: Microsoft：LLaVA 类图文投影，视觉 token 数和上下文预算
quick: >-
  CLIP 网格投影进 LLM 词嵌入，视觉 token 数是 $(H/P)\times(W/P)$。224px 大约 256，336px 大约
  576。它们和文本抢同一条上下文。高分辨率靠切块，token 近线性涨，先算预算再谈「看清字」。
tags:
  - Microsoft
  - LLaVA
  - Multimodal
  - Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: primary
  - title: Improved Baselines with Visual Instruction Tuning (LLaVA-1.5)
    url: https://arxiv.org/abs/2310.03744
    type: primary
---

多模态 / Copilot Vision / Phi-Vision 岗会问「图是怎么进语言模型的」。LLaVA 是最干净的白板：冻结视觉编码器、一个投影、再接到 Vicuna。微软产品不一定叫 LLaVA，但 Florence / Phi-3-Vision 仍是 **视觉 token 占上下文** 这件事。评委要听 shape 和预算，不是「我们加了 cross-attn」。

## 投影：网格特征进词嵌入

图像 $H\times W$，patch $P$（CLIP ViT-L/14 里 $P=14$）。去掉 class token，网格特征

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

LLaVA-1.0 用 224px：$16\times 16=256$ 个视觉 token。LLaVA-1.5 用 336px：$24\times 24=576$。CLIP 输出大约是 $[N_{\mathrm{vis}}, 1024]$，投影（1.0 线性，1.5 两层 MLP）映到 LLM 的 $d_{\mathrm{model}}$，变成和文本 embedding 可拼接的 $[N_{\mathrm{vis}}, d]$。训练分两段：先只训投影对齐图文，再指令微调。面试别把「visual instruction tuning」说成从零训 ViT。

序列就是：视觉 token 前缀 + 文本 token。注意力是普通因果 Transformer，没有另开一条跨模态模块。代价立刻变成 **上下文长度**：

$$
N_{\mathrm{vis}}+N_{\mathrm{text}}+N_{\mathrm{out}}\le T_{\mathrm{ctx}}.
$$

4k 上下文、一张 576 token 的图，再加系统提示和检索块，文本预算很紧。多图、截图里的小字、高分辨率文档，问题不是「模型看不懂」，是 **token 先花光**。

## 高分辨率：切块会把视觉 token 打满

AnyRes / 动态切块：把大图切成 $g$ 块，每块再走一遍 336 编码器，有时再加一张全局缩略图。粗算 $g=4$ 就是 $5\times 576=2880$ 视觉 token，已经接近一个 4k 窗口的大半。文档 OCR、UI 截图、PPT 全页，不切块就看不清字；切块就把会议纪要、代码注释挤出窗口。这和 `msft-long-context` 是同一条账，只是视觉侧的「长度」由分辨率决定。

我会在白板上先问产品要看清什么：

- 自然图像问答：256-576 往往够，优先低延迟。
- 截图里的按钮文字、表格：必须切块或更高分辨率编码器，然后 **减文本、减多图、或先 OCR**。
- 多图对比：每张图一份 $N_{\mathrm{vis}}$，三张 576 就 1728，生成还没开始。

错法：把视觉 token 和文本 token 当成两个池子。在 LLaVA 类架构里它们抢同一条 KV cache，decode 带宽跟总长度走。量化、GQA 省的是 KV，减不掉已经占掉的视觉前缀。另一错法：训练用 224、推理用 4k 切块还不做适配：位置和投影统计都会漂。

Phi-3-Vision 等小模型更狠：参数少，上下文也不是无限。产品上可以「图先变成短 OCR + 少量缩略 token」，把 LLaVA 纯像素前缀当成高质量路径而不是唯一路径。Azure 上还要算这些视觉 token 进 TPM，见 `msft-azure-tpm`。

给一个具体预算：4k 窗口、系统提示 200、用户问题 100、检索块 800，剩大约 2900。一张 576 的图还宽裕；四张图加全局缩略就是 2880，文本几乎没了。面试官说「用户贴了三张截图问按钮在哪」，你要先减图、切 ROI、或走 OCR，而不是把 $T_{\mathrm{ctx}}$ 当成无限。这和 `msft-long-context` 同一条账，只是视觉侧用分辨率当长度。

训练推理分辨率不一致会直接表现为「训练能看清字、线上糊成色块」，要在评测里单开 OCR / 定位切片，不要只报综合 VQA。

## 追问

- **为什么不用 Q-Former 压成 32 个 token？** 能压，BLIP-2 那条路。省上下文，损空间细节（小字、定位）。LLaVA 用网格换简单和细节，预算换质量。
- **视频呢？** 帧数 $\times N_{\mathrm{vis}}$。1 fps 抽 16 帧 × 576 已经过万。必须抽帧、时序池化，或先字幕。
- **视觉 token 要不要 RoPE？** 它们占序列位置，要用 LLM 的位置编码。切块时块间位置怎么排（光栅、加分隔 token）要固定，训练推理一致。
- **幻觉「图里有一只猫」？** 和文本 grounding 同类：对不上区域就拒答。评测要拆开「看见了」和「说对了」，不要只报 VQA accuracy。
