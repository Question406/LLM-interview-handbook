---
id: dt-multimodal-data
section: senior
order: 3
level: A
title: Director：多模态数据举一个你能讲到底的例子
quick: "选一个完整产品任务，说明图片来源、对齐方式、合成补充、训练阶段、评测和隐私限制。可以参考 AFM 从海报抽事件再写日历的流程。报一个 LAION 名字不够，也不能把 Image Playground 图像生成与 AFM 图文理解当成同一模型。"
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

我会选一条产品路径讲完，不报「我们用了 LAION」。没有视觉项目就用音频 / 视频 / 屏幕，骨架相同。不要硬编 50 亿 caption。

不这么选的理由：guideline 写有具体多模态例子会加分。把 Image Playground 的扩散模型和 AFM 的图文理解说成同一个 checkpoint，产品契约就乱了。

## 一个能讲 4 分钟的例子：text-rich 图

先明确产品任务：用户把 iPhone 对着海报，模型需要抽取事件名、时间和地点。公开来源是 AFM 2025 的 text-rich / OCR 段。

只有爬取图文对还不够。Alt-text 通常很短，未必对应图里的文字。去重后的 10B 图文对有助于模型理解一般图像，但仍需要专门数据训练印刷字和表格理解。

所以补三层。许可和爬取的 PDF / 文档 / 信息图；从图表代码渲染再出 QA；OCR 真数据（印刷和手写，海报、菜单、店招、笔记本），覆盖要支持的语言。

合成各管一层。50 亿分层 caption 补细节；检测器切区域再汇总，补空间关系；对抗题补拒答。教师要过 CLIP / OCR 过滤，详细 caption 放后段。

训练落点也要说清。视觉编码器先 CLIP（公开写了 6B+ 图文对，448，FLIP 掩码），再和小 decoder 对齐到 672。LLM 的视觉能力在 continued PT：60 / 10 / 28.5 / 1.5 的 mix。监督微调（SFT） 再把分辨率拉到 $1344$ 的 $2\times 2$ tiling。强化学习（RL） 可以更新视觉编码器，但先把数据剖面摆对。

端侧还有预算。高清 5 图（overview + 4 tile）、balanced 只 overlay、rapid 224 只有 9 个视觉 文本处理单位（token）。合成必须按模式抽样，否则 rapid 会在没看清字的时候编时间。

评测我报字段级抽取、时间是否能进日历、图里没有的字段是否拒。不要只报 COCO caption CIDEr。

隐私最后钉：用户海报照片默认不是下一版基础模型的 SFT。屏幕截图更不能当训练日志。全球模型走许可 / 爬取 / 合成；个人相册走端上。

## 你自己的项目怎么套这副骨架

把「海报」换成你做过的：UI 截图、病理切片、监控帧、语音转写。按七行填：产品契约、真数据缺什么、合成补哪一层、进 pre / mid / post 哪段、推理预算、评什么、什么不能回灌。合成 DAG 细节见 `dt-synth-tool-mm`。

音频 / 视频多一句：时间对齐和切段是一等公民。错切的 10 秒比错 caption 更伤。视频 token 预算要先说 fps 和分辨率，再谈合成对白。

## 追问

- **交错文档和成对 caption 差在哪？** 交错保留图在原文中的位置，利于文档理解；成对 caption 利于短对齐。AFM 两种都留，mid mix 里交错 10%、caption 28.5%。
- **图表为什么要代码渲染？** 真图标签贵且不齐。代码渲染自带精确数据表，能做可验证 QA。分布偏，所以还要网页真表。
- **没有视觉论文怎么办？** 讲清楚你做过的模态和你没做过的。用 AFM 骨架证明你能设计，不要假装训过 50 亿对。
