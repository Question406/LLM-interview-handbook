---
id: msft-llava
section: microsoft
order: 6
level: A
title: Microsoft：LLaVA 类图文投影，视觉 token 数和上下文预算
quick: "LLaVA 将 CLIP patch 网格投影到 LLM 词嵌入，视觉 token 数为 $(H/P)\\times(W/P)$，与文本共享窗口和 KV cache。224px 约 256 个、336px 约 576 个；多图和切块要先算总预算，再选择 ROI、OCR 或分辨率。"
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

LLaVA 把图像网格特征投影为语言模型可读取的视觉 token，再与文本拼成一条序列。视觉 token 数 $N_{\mathrm{vis}}$ 与文字共享窗口 $T_{\mathrm{ctx}}$，所以提高分辨率、多贴几张图都会挤占文本与生成预算。比如四个 336px 切块再加全局图，就是 2880 个视觉 token，已占 4k 窗口的大半。

## 从网格到序列的形状

图像为 $H\times W$，patch 大小 $P$，CLIP ViT-L/14 取 $P=14$。去掉 class token 后，网格数为：

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

LLaVA-1.0 使用 224px，得到 $16\times 16=256$；1.5 使用 336px，得到 $24\times 24=576$。CLIP 特征约为 $[N_{\mathrm{vis}}, 1024]$，1.0 线性层或 1.5 两层 MLP 投影到 $d_{\mathrm{model}}$，输出 $[N_{\mathrm{vis}}, d]$，可以与文本 embedding 拼接。

初始连接冻结的视觉编码器与 Vicuna，先只训投影，再做指令微调。普通因果 Transformer 读取视觉前缀与文本，无需另设 cross-attn。总预算满足：

$$
N_{\mathrm{vis}}+N_{\mathrm{text}}+N_{\mathrm{out}}\le T_{\mathrm{ctx}}.
$$

视觉 token 也占位置并用 LLM 的位置编码，切块的光栅顺序和分隔 token 要固定。量化、GQA 可节省 KV，却不能消除视觉前缀，decode 带宽仍随总长度增加。

## 按要看清的内容分配预算

AnyRes / 动态切块把大图切成 $g$ 块，每块过 336 编码器，有时再加全局缩略图。$g=4$ 时约 $5\times 576=2880$。自然图问答常可先用 256-576 个 token；小按钮、表格、OCR 可能需切块或更高分辨率，再减少文本、多图，或先做 OCR。三张 576 的图已占 1728，尚未开始生成，相关长上下文问题见 `msft-long-context`。

举一个预算例子：4k 窗口，系统提示 200、问题 100、检索 800，余约 2900。一张 576 的图仍有余量，但四块加全局图的 2880 几乎用完剩余空间。用户贴三张截图问按钮时，先考虑减图、裁 ROI 或 OCR，不能只扩大输入。

Phi-3-Vision 等小模型也可先将图转成短 OCR 加少量缩略 token，把纯像素前缀留给需要细节的路径。Azure 还将视觉 token 计入 TPM，见 `msft-azure-tpm`。训练 224、推理突然用 4k 切块会让位置与投影统计漂移，评测要单列 OCR / 定位和分辨率配置，不能只看综合 VQA。

## 追问

**为什么不压成 32 个 Q-Former token？**
BLIP-2 路线能省上下文，但可能损失小字与空间定位。按目标任务比较预算与细节。

**视频 token 怎么算？**
帧数 $\times N_{\mathrm{vis}}$，1 fps 抽 16 帧、每帧 576 已过万，需要抽帧、时序池化或先字幕。

**模型说图里有猫，但没有呢？**
按 grounding 处理，论断对不上区域就拒答。评测分开感知是否正确与回答是否受支持。
