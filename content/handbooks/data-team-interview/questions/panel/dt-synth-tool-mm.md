---
id: dt-synth-tool-mm
section: panel
order: 3
level: S
title: Panel：工具调用和多模态合成，你能画出哪条具体管线？
quick: "工具数据要在可重置的执行环境中生成：参考模型调用工具，人能回滚纠错，保存成功路径和放弃的尝试。视觉数据需要详细描述、代码渲染的图表与可核验问答，还要教模型拒绝回答图中没有的信息。这几条流程要分别说明。"
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

工具和视觉需要分别说明生成与验证流程，单说「生成了一些 JSON」看不出数据质量。推理数据见 `dt-synth-reasoning`。AFM 2025 两条都写了。

不这么选的理由：guideline 要一条 reasoning / tool / multimodal 的具体管线。终局字符串当唯一奖励，模型会编造「我已经加好了」。如果只保留成功路径，就没有足够示范教模型如何处理失败。

## 工具：过程监督，终局对错不够

AFM 2025 §5.3 的公开做法可以直接当白板骨架：

- 搭一个标注平台：参考模型 + 工具执行环境。环境里有有状态和无状态工具，以及人写的初始数据库。
- 标注员出用户请求，模型开始调工具，直到它决定回复用户。平台吐出整段轨迹：调用、参数、工具返回、最终回复。
- 关键能力：回滚到对话任意一轮，并重置数据库。人改错一步，再从那里续跑。
- 落盘是树：成功的主要执行路径是合法多轮 监督微调（SFT） 轨迹，其他尝试路径是放弃的错误尝试。

下面是面试中可以补充讨论的设计问题，不是报告披露的实现。

Oracle 是环境。日历是否写入、检索是否命中 id，比「最终一句听着对」重要。

被放弃的尝试有用。其他尝试路径是负例和恢复示范：参数类型错、权限拒绝、空结果之后怎么改。

要记录工具版本、schema 和数据库快照，并与轨迹一起保存。环境升级后，旧轨迹可能无法回放，后续训练也就难以复现，见 `dt-data-flywheel`。

Toolformer 是另一条更老的线：自监督决定何时插入 API 调用。产品工具数据更接近 AFM 这条「人在环上的过程监督」，因为状态和副作用没法从纯文本里猜。

现场举自己的例子，按同一骨架改名词：sandbox、回滚、成功的主要执行路径 / 被放弃的尝试、schema 版本。不要只说「我们生成了 function call」。

## 多模态：爬取对太短，合成补细节和拒答

AFM 的图像数据分层，数字都是公开的，点到为止：

- 去重后超过 10B 高质量图文对；交错文档 1.75 亿，图 5.5 亿+。
- 合成 caption 超过 50 亿对，因为网页 alt-text 太短，盖不住细节。他们还用检测器切区域、分别描述、再由 LLM 汇总成带空间关系的详细 caption，留给后面的阶段。
- 图表：LLM 先造字段，再写绘图代码，再由教师出 QA。表格从网页解析成 markdown，图和 markdown 以及合成 QA 一起用。
- SFT 用检索扩多样性：种子图 → 搜相似图 → 合成问答。另外合成对抗题：故意问图里没有的东西，配上拒答，压幻觉。

LLaVA 那条「图 + 语言模型扩写指令」是同族、更早的公开配方。AFM 多出来的是分层细节、代码渲染的图表、拒答对抗。面试把这几层分开讲，比报 50 亿有用。

端侧还有分辨率模式（高清 tiling、overview、224 的 rapid 9 文本处理单位（token））。合成数据要按模式抽样，否则模型只在 5 图 tiling 上见过细字，rapid 模式会凭空生成。产品约束见 `dt-multimodal-data`。

## 质量门不要共用一个 quality 字段

网页「教科书味」分类器会杀掉工具 JSON 和图表代码。工具桶看 schema 合法、执行成功、状态可回放。视觉桶看图文对齐、OCR 对得上、对抗拒答率。推理桶看 `dt-synth-reasoning` 的硬验证。混用一个 `quality` 字段，飞轮会把最不像网页的高价值数据扔掉。

## 追问

- **没有真实工具环境能不能纯合成？** 能做 schema 和参数类型，做不了状态副作用。至少要一个可重置的假数据库，否则回滚是空话。
- **合成 caption 会不会把教师幻觉写进预训练？** 会。所以 AFM 用检测器有实际证据支持、用 CLIP / OCR 再滤一层。教师版本进 lineage，详细 caption 放后段，不放进最脏的 core crawl mix。
- **多图推理怎么合成？** AFM 写了另收高质量多图数据。我会用「同一事件的多张图 + 必须引用跨图证据」的题，单图能答对的丢掉。
