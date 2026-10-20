---
id: apple-vision-edge
section: apple
order: 17
level: S
title: Apple：端侧视觉 token 预算和 ANE 静态 shape 怎么卡？
quick: "视觉 token 数 $(H/P)\\times(W/P)$ 进同一条上下文和 KV。ANE 要预编译分辨率档，不能 AnyRes 现场切。先算 $N_{\\mathrm{vis}}$ 占了多少 $S_{\\max}$，再决定缩略、切 ROI 还是上云。动态 padding 掉出 ANE 比看不清字更常见。"
tags:
  - Apple
  - Neural Engine
  - Vision
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Deploying Transformers on the Apple Neural Engine
    url: https://machinelearning.apple.com/research/neural-engine-transformers
    type: primary
  - title: MM1 — Methods, Analysis and Insights from Multimodal LLM Pre-training
    url: https://machinelearning.apple.com/research/mm1-methods-analysis-insights
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Improved Baselines with Visual Instruction Tuning (LLaVA-1.5)
    url: https://arxiv.org/abs/2310.03744
    type: secondary
---

屏幕理解、Visual Intelligence、端侧 AFM 多模态都会问「一张图要几个 token」。云端 AnyRes 把大图切成 $g$ 块再加全局缩略，token 数近线性增长，见 `msft-llava`。手机上的限制是 ANE 静态 shape、SRAM 和已经预分配的 $S_{\max}$，见 `apple-ane`、`apple-ondevice-kv`。MM1 说分辨率和 token 数主导质量。按这些公开约束收。

## 先写预算，再谈切图

图像 $H\times W$、patch $P$：

$$
N_{\mathrm{vis}}=\frac{H}{P}\times\frac{W}{P}.
$$

336px、$P=14$ 是 $24\times 24=576$。端侧若再加系统提示、工具 JSON、用户话，不等式是

$$
N_{\mathrm{vis}}+N_{\mathrm{text}}+N_{\mathrm{out}}\le S_{\max}.
$$

$S_{\max}$ 在导出时就定死。视觉前缀写入 KV 之后，逐 token 生成（decode） 每步都要扫它，字节账仍是 $2 L H_{\mathrm{kv}} d_h S b$，见 `apple-ondevice-kv`。减不掉已经占住的图。

ANE 额外约束：

1. 分辨率是档位，不是连续量。编译 `(224, 336, 448)` 一类入口。来图 pad / 缩放到最近档，不要运行时 `interpolate` 出新 $H$。
2. $N_{\mathrm{vis}}$ 必须静态。切块数 $g$ 一变，序列长度变，整段掉 CPU。要切块就预编译 $g\in\{1,2,4\}$ 三张图，或先在 CPU 上裁 ROI 再送固定编码器。
3. 布局。视觉塔若走 ANE，激活靠近 $[B,C,1,S]$ / Conv 友好格式，和语言塔同一套痛，见 `apple-ane`。随手 `reshape` 会把整网切出 NPU。

例子：端侧 $S_{\max}=4096$，系统加用户 300，工具证据 400，生成预留 200，视觉只剩大约 3196。一张 576 很宽裕；四张截图加全局就是 2880，文本证据开始被挤。产品决策是减图、裁按钮周围，或把高分辨率文档送给 PCC，而不是把 $S_{\max}$ 口头加长。

## 质量和时延的切法

看清小字要高 $R$；高 $R$ 要更多 $N_{\mathrm{vis}}$ 或切块。端上正确顺序：

- 自然图问答、相册描述：单档 224/336，冻塔，见 `apple-mm-train`。
- 屏幕、表格：先 UI 树 / OCR，像素模型只补充模型容易失败的任务，见 `apple-multimodal`。不要整屏 1344 进 3B。
- 多图：硬顶张数。超出就问「你指哪一张」。

Prefill 复杂度按 $(N_{\mathrm{vis}}+N_{\mathrm{text}})^2$ 估。图一进，首 token 被视觉编码器加 输入预填充（prefill，即处理输入并建立缓存） 吃掉，和 `apple-siri-latency` 的 0.6 ms/prompt-token 不是同一段。验收看 Instruments：视觉塔和 LLM 是否都留在 Neural Engine，以及 greedy 与 CPU 参考一致。

常见误区是：把动态 AnyRes 当端侧默认；视觉 token 另开一条不占 KV 的「旁路」；训练用 224、线上 pad 到 448 还不做分辨率适配。剪枝若让 $N_{\mathrm{vis}}$ 变成数据依赖长度，会直接掉 ANE，见 `apple-token-prune`。

## 追问

- **为什么不把图压成 32 个 query？** 能压，BLIP-2 那条。省 $S$，损定位和小字。端侧屏幕任务通常不能。
- **视频？** 帧数乘 $N_{\mathrm{vis}}$。必须抽帧或先字幕，不要 1 fps $\times$ 576 往静态 cache 里塞。
- **和 PCC 怎么切？** 私有屏幕默认端上低 $R$；要高 $R$ 文档理解再上 PCC，仍不是把原图拿去训下一版。
- **padding 会不会让模型看见黑边？** 会。训练要含同样档位的 pad，mask 掉 pad 位置，mask 用有限大负数，见 `apple-ondevice-quant`。
