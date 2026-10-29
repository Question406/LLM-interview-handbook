---
id: dt-synth-tool-mm
section: panel
order: 3
level: S
title: Panel：tool calls 和 multimodal 合成，你能画出哪条具体 pipeline？
quick: >-
  工具和视觉是两条 pipeline，要分别讲生成和验证。工具数据在可重置的执行环境里生成，reference model
  调用工具，人能回滚纠错，保存成功路径和被放弃的尝试，oracle
  是环境状态，最后一句话说得对不算数。视觉数据要补详细描述、代码渲染的图表和可核验问答，还要教模型拒绝回答图中没有的信息。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Toolformer
    url: 'https://arxiv.org/abs/2302.04761'
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: 'https://arxiv.org/abs/2304.08485'
    type: primary
---

工具和视觉是两条 pipeline，要分别讲生成和验证。工具数据在能回滚的执行环境里由人做过程监督，以环境状态为准；视觉数据用合成补上爬取 image-text pairs 缺的细节和拒答。单说「生成了一些 JSON」看不出数据质量，AFM 2025 两条都公开写了，可以直接当白板骨架。

先说工具。用户让模型「把明天下午三点的会加进日历」，模型最后回一句「我已经加好了」。如果把这句话当唯一奖励，模型就学会编造；只保留成功路径，又没有足够的示范教它怎么处理失败。guideline 要的就是这样一条 reasoning / tool / multimodal 的具体 pipeline。

## 工具：在环境里做过程监督

AFM 2025 §5.3 的公开做法是先搭一个标注平台，由 reference model 加工具执行环境组成，环境里有有状态和无状态的工具，以及人写的初始数据库。annotator 写用户请求，模型开始调工具，直到它决定回复用户，平台输出整段 trajectories：调用、参数、工具返回和最终回复。关键能力是回滚，可以回到对话的任意一轮并重置数据库，人改掉错的那一步，再从那里续跑。落盘的结果是一棵树，成功的主执行路径是合法的多轮 SFT trajectories，其他路径是被放弃的错误尝试。

下面几点是面试中可以补充讨论的设计，报告里没有披露具体实现。oracle 是环境：日历有没有真的写入、检索有没有命中对的 id，比最后一句话听着对重要得多。被放弃的尝试也有用，它们是负例，也是恢复示范，告诉模型参数类型错、权限被拒、结果为空之后该怎么改。工具版本、schema 和数据库快照要和 trajectories 一起存，环境升级后旧 trajectories 可能没法 replay，后续训练也就难以复现（`dt-data-flywheel`）。

Toolformer 是更早的另一条路线，用自监督决定何时插入 API 调用。要处理状态和副作用的工具数据更接近 AFM 这种人在环上的过程监督，因为状态和副作用没法从纯文本里猜出来。现场举自己的例子时，按同一个骨架换名词就行：sandbox、回滚、成功的主执行路径和被放弃的尝试、schema 版本。光说「我们生成了 function call」，面试官听不出你怎么验证。

## multimodal：爬取的 image-text pairs 太短，合成补细节和拒答

AFM 的图像数据是分层的，数字都公开，点到为止。deduplication 后超过 10B 高质量 image-text pairs，交错文档 1.75 亿篇，图片 5.5 亿张以上。合成 caption 超过 50 亿对，因为网页 alt-text 太短，覆盖不了细节；他们还用检测器切出区域、分别描述，再由 LLM 汇总成带空间关系的详细 caption，留给后面的训练阶段。

图表是先让 LLM 造字段，再写绘图代码，最后由 teacher 出 QA。表格从网页解析成 markdown，图、markdown 和合成 QA 一起用。SFT 阶段用检索扩多样性，从 seed 图搜相似图，再合成问答。另外合成对抗题，故意问图里没有的东西，配上拒答，用来压 hallucination。

LLaVA 那条「图片加语言模型扩写指令」的路线是同类、更早的公开配方。AFM 多出来的是分层的细节描述、代码渲染的图表和拒答对抗题，面试时把这几层分开讲，比报一个 50 亿更有用。

如果模型有多种分辨率模式，synthetic data 要按模式分别 sampling。AFM 有高清 tiling、overview，以及 224 分辨率、9 个 token 的 rapid 模式；模型只在 5 图 tiling 下见过小字，到了 rapid 模式就会凭空生成内容。图像数据的其他约束见 `dt-multimodal-data`。

## 追问

**没有真实工具环境，能不能纯合成？**
能做 schema 和参数类型，做不了状态和副作用。至少要有一个可重置的假数据库，否则回滚无从谈起。

**合成 caption 会不会把 teacher 的 hallucination 写进 pre-training？**
会。所以 AFM 用检测器提供实际证据，再用 CLIP / OCR 滤一层。teacher 版本记进 lineage，详细 caption 放到后面的阶段，不放进最脏的 core crawl mix。

**多图推理怎么合成？**
AFM 写了另外收集高质量的多图数据。我会出「同一事件的多张图，必须引用跨图证据才能答」的题，单张图就能答对的丢掉。

**工具 JSON 能和网页共用一个质量分类器吗？**
不能。网页上那种「教科书味」分类器会把工具 JSON 和图表代码杀掉，每个桶要用自己的 quality criteria：工具桶看 schema 合不合法、执行成没成功、状态能不能 replay；视觉桶看图文是否对齐、OCR 对不对得上、对抗题的拒答率；推理桶用 `dt-synth-reasoning` 里的硬验证。混用一个 `quality` 字段，飞轮会把最不像网页、价值却最高的数据扔掉。
