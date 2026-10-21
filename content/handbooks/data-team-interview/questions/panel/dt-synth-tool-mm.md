---
id: dt-synth-tool-mm
section: panel
order: 3
level: S
title: Panel：工具调用和多模态合成，你能画出哪条具体管线？
quick: "工具和视觉是两条管线，要分别讲生成和验证。工具数据在可重置的执行环境里生成：参考模型调用工具，人能回滚纠错，保存成功路径和被放弃的尝试，oracle 是环境状态，最后一句话说得对不算数。视觉数据要补详细描述、代码渲染的图表和可核验问答，还要教模型拒绝回答图中没有的信息。"
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Tool Use
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Toolformer
    url: https://arxiv.org/abs/2302.04761
    type: primary
  - title: "Visual Instruction Tuning (LLaVA)"
    url: https://arxiv.org/abs/2304.08485
    type: primary
---

工具和视觉要分别说明生成与验证流程，单说「生成了一些 JSON」看不出数据质量。AFM 2025 两条都公开写了，可以直接当白板骨架。

guideline 要的是一条 reasoning / tool / multimodal 的具体管线。工具这边的关键是：把最终那句话当唯一奖励，模型会编造「我已经加好了」；只保留成功路径，又没有足够示范教模型怎么处理失败。

## 工具：在环境里做过程监督

AFM 2025 §5.3 的公开做法是这样的：

1. 搭一个标注平台：参考模型加工具执行环境。环境里有有状态和无状态的工具，以及人写的初始数据库。
2. 标注员写用户请求，模型开始调工具，直到它决定回复用户。平台输出整段轨迹：调用、参数、工具返回和最终回复。
3. 关键能力是回滚：可以回到对话的任意一轮，并重置数据库。人改掉错的那一步，再从那里续跑。
4. 落盘的结果是一棵树：成功的主执行路径是合法的多轮监督微调（SFT）轨迹，其他路径是被放弃的错误尝试。

下面几点是面试中可以补充讨论的设计，报告里没有披露具体实现。

- **oracle 是环境。** 日历是否真的写入、检索是否命中了对的 id，比最终一句话听着对重要得多。
- **被放弃的尝试有用。** 它们是负例，也是恢复示范：参数类型错、权限被拒、结果为空之后该怎么改。
- **版本要和轨迹一起存。** 记录工具版本、schema 和数据库快照。环境升级后，旧轨迹可能没法回放，后续训练也就难以复现，见 `dt-data-flywheel`。

Toolformer 是另一条更早的路线：用自监督决定何时插入 API 调用。要处理状态和副作用的工具数据更接近 AFM 这种「人在环上的过程监督」，因为状态和副作用没法从纯文本里猜出来。

现场举自己的例子时，按同一个骨架换名词就行：sandbox、回滚、成功的主执行路径和被放弃的尝试、schema 版本。光说「我们生成了 function call」，面试官听不出你怎么验证。

## 多模态：爬取的图文对太短，合成补细节和拒答

AFM 的图像数据是分层的，数字都是公开的，点到为止：

- 去重后超过 10B 高质量图文对；交错文档 1.75 亿篇，图片 5.5 亿张以上。
- 合成 caption 超过 50 亿对，因为网页 alt-text 太短，覆盖不了细节。他们还用检测器切出区域、分别描述，再由 LLM 汇总成带空间关系的详细 caption，留给后面的训练阶段。
- 图表：先让 LLM 造字段，再写绘图代码，最后由教师出 QA。表格从网页解析成 markdown，图、markdown 和合成 QA 一起用。
- SFT 阶段用检索扩多样性：种子图 → 搜相似图 → 合成问答。另外合成对抗题：故意问图里没有的东西，配上拒答，用来压幻觉。

LLaVA 那条「图片加语言模型扩写指令」的路线是同类、更早的公开配方。AFM 多出来的是分层的细节描述、代码渲染的图表和拒答对抗题。面试时把这几层分开讲，比报一个 50 亿更有用。

如果模型有多种分辨率模式，合成数据要按模式分别抽样。AFM 有高清 tiling、overview，以及 224 分辨率、9 个文本处理单位（token）的 rapid 模式；模型只在 5 图 tiling 下见过小字，到了 rapid 模式就会凭空生成内容。图像数据的其他约束见 `dt-multimodal-data`。

## 每个桶用自己的质量门

网页上那种「教科书味」分类器会把工具 JSON 和图表代码杀掉。所以每个桶要用自己的门：工具桶看 schema 是否合法、执行是否成功、状态能否回放；视觉桶看图文是否对齐、OCR 是否对得上、对抗题的拒答率；推理桶用 `dt-synth-reasoning` 里的硬验证。混用一个 `quality` 字段，飞轮会把最不像网页、价值却最高的数据扔掉。

## 追问

- **没有真实工具环境，能不能纯合成？** 能做 schema 和参数类型，做不了状态和副作用。至少要有一个可重置的假数据库，否则回滚无从谈起。
- **合成 caption 会不会把教师的幻觉写进预训练？** 会。所以 AFM 用检测器提供实际证据，再用 CLIP / OCR 滤一层。教师版本记进 lineage，详细 caption 放到后面的阶段，不放进最脏的 core crawl mix。
- **多图推理怎么合成？** AFM 写了另外收集高质量的多图数据。我会出「同一事件的多张图，必须引用跨图证据才能答」的题，单张图就能答对的丢掉。
