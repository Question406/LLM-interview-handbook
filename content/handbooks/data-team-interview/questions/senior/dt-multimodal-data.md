---
id: dt-multimodal-data
section: senior
order: 3
level: A
title: Director：多模态数据举一个你能讲到底的例子
quick: "挑一个任务讲到底，比如从海报、文档截图里抽字段：图片从哪来、真数据缺什么、合成补哪一层、进哪个训练阶段、怎么评测。只报一个 LAION 的名字，听的人看不出你做过什么。AFM 2025 报告公开的 text-rich / OCR 数据可以当骨架，换成自己的模态时七项照填。"
companies:
  - apple
tags:
  - Apple
  - Multimodal
  - Synthetic Data
  - Vision
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "CLIP: Learning Transferable Visual Models From Natural Language Supervision"
    url: https://arxiv.org/abs/2103.00020
    type: primary
  - title: "Visual Instruction Tuning (LLaVA)"
    url: https://arxiv.org/abs/2304.08485
    type: primary
---

我会挑一个文字密集图像的理解任务从头讲到尾：模型看一张海报、菜单或文档截图，把里面的字段抽出来。图片从哪来、真数据缺什么、合成补哪一层、进哪个训练阶段、怎么评测，一路讲下来。只报一句「我们用了 LAION」，听的人看不出你做过什么。骨架我借 AFM 2025 报告公开的 text-rich / OCR 数据，因为它把每一步的数字都写出来了。没有视觉项目，换成音频、视频或屏幕任务也是这套骨架，但别硬编一段 50 亿 caption 的经历。

先说为什么只靠爬来的图文对不够。比如一张菜单，网页上的 alt-text 往往只有一句很短的描述，菜名和价格都不在里面。Alt-text 通常很短，也未必对应图里的文字，去重后的 10B 图文对能帮模型理解一般图像，印刷字和表格理解要专门的数据来训。真数据从三处补：许可和爬取的 PDF、文档、信息图；用图表代码渲染出图，再生成 QA；真实 OCR 数据，印刷和手写都有，场景包括海报、菜单、店招、笔记本，并覆盖要支持的语言。合成数据各补一个缺口：50 亿条分层 caption 补细节，用检测器切出区域再汇总描述补空间关系，对抗题补拒答。教师生成的内容先过 CLIP / OCR 过滤，详细 caption 放在训练后段。

然后讲每批数据进哪个阶段。视觉编码器先做 CLIP 训练，公开写的是 6B+ 图文对、448 分辨率、FLIP 掩码，再和一个小 decoder 对齐到 672。LLM 的视觉能力在 continued PT 阶段获得，mix 是 60 / 10 / 28.5 / 1.5。SFT 再把分辨率提到 $1344$，用 $2\times 2$ tiling。RL 阶段可以更新视觉编码器，但前提是先把数据分布摆对。推理时的视觉 token 预算也会影响合成数据怎么抽：推理会用低分辨率、少量视觉 token 的设置，训练数据就要按这些设置分别抽样，否则模型会在没看清字的时候编一个答案出来。

评测我报字段级抽取准确率、抽出来的字段下游能不能直接用、图里没有的字段模型会不会拒答。COCO caption 的 CIDEr 反映不了这些。

换成自己的项目时，把「海报」换成做过的任务，UI 截图、病理切片、监控帧、语音转写都行，七项照填：任务定义、真数据缺什么、合成补哪一层、进 pre / mid / post 哪段、推理预算、评什么、哪些数据不能用于训练。合成 DAG 的细节见 `dt-synth-tool-mm`。

## 追问

**音频和视频有什么不一样？**
时间对齐和切段是头等问题，切错 10 秒比 caption 写错更伤。视频要先说清 fps 和分辨率决定的 token 预算，再谈合成对白。

**交错文档和成对 caption 差在哪？**
交错文档保留图片在原文中的位置，有利于文档理解；成对 caption 有利于短对齐。AFM 两种都保留，mid mix 里交错占 10%、caption 占 28.5%。

**图表为什么要用代码渲染？**
真实图表的标签贵，也不齐。代码渲染自带精确的数据表，可以做可验证的 QA。但它的分布有偏，所以还要配网页上的真实表格。

**没有视觉论文怎么办？**
讲清楚你做过哪些模态、没做过哪些。可以借公开报告的骨架说明你会怎么设计，但别说成自己训过 50 亿对。
