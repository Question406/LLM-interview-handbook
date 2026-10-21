---
id: dt-frontier-ctx-mm
section: frontier-release
order: 5
level: S
title: MRCR、MMMU、多语榜怎么造，发版里的长上下文和多模态在测什么？
quick: "长上下文要看模型在长输入里能否找对信息，「支持 1M」只说明能接收这么长的输入。MRCR v2 在长文中放入多个相似目标，要求按指令取回指定内容；同一模型在 128k 与 1M 下可能差很多。MMMU-Pro 尽量减少不看图也能答对的题，多语榜则要检查题目是否只是英语翻译。"
companies:
  - google
  - meta
  - openai
  - anthropic
tags:
  - Evaluation
  - Long context
  - Multimodal
  - Multilingual
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Gemini 3.1 Pro Model Card
    url: https://deepmind.google/models/model-cards/gemini-3-1-pro/
    type: primary
  - title: "Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities"
    url: https://arxiv.org/abs/2507.06261
    type: primary
  - title: MMMU
    url: https://arxiv.org/abs/2311.16502
    type: primary
  - title: Llama 4 model card
    url: https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
    type: primary
  - title: Introducing GPT-5
    url: https://openai.com/index/introducing-gpt-5/
    type: primary
  - title: The Llama 4 herd
    url: https://ai.meta.com/blog/llama-4-multimodal-intelligence/
    type: primary
---

「支持 1M 上下文」只说明模型能接收这么长的输入，能不能在里面找对指定信息，要看 MRCR 在 1M 下的结果。多模态也要区分任务：OCR 能读对图表里的数字，不代表模型能根据学科图片推理，MMMU-Pro 测的是后者。多语榜则要先检查题目是不是从英语翻译过来的。

## MRCR

Gemini 技术报告把 MRCR 放在长上下文那一行，卡上的名字是 MRCR v2（8-needle）。做法是在长文里放入多段相似的材料，称为「针」，模型要按指令取回指定的那一段，找到任意一段不算完成。8 根针比单针难得多，取错一段或顺序错了，整道题就判错。只在文末放一句「密码是香蕉」属于单针检索，不能代表 MRCR 的多针任务。

Gemini 3.1 Pro 模型卡（2026-02）把长度拆开报：

| 模型 | 128k，平均 | 1M，点估计 |
| --- | --- | --- |
| Gemini 3.1 Pro Thinking High | 84.9% | 26.3% |
| Gemini 3 Pro | 77.0% | 26.3% |
| Sonnet 4.6 / Opus 4.6 / GPT-5.2 | 84.9% / 84.0% / 83.8% | 卡上写不支持 |

在 128k 长度下，几家模型的结果很接近；1M 只有 Gemini 报了分，3.1 Pro 和 3 Pro 都是 26.3%。只报窗口长度，读者无法判断长文检索的质量。

Gemini 2.5 报告里还有 LOFT（hard retrieval）和更早的 MRCR-V2 数字，协议和 3.1 这张卡不一定相同，引用时要带上报告名。

## MMMU 和 MMMU-Pro

MMMU 收的是大学考试式的题目，图和文本都有，学科从理工到人文。它想评估必须结合图片的学科推理，但题干和选项有时已经足够让语言模型选对，所以高分不一定体现读图能力。数据组应另外报告去掉图片后的纯文本基线，见 us-tech 的多模态评测卡。

MMMU-Pro 为了减少这种情况，增加了更难的选项，并加入更侧重视觉理解的题。Llama 4 指令模型卡写明，他们报的 MMMU Pro 是 Standard 和 Vision 的平均。

| 材料 | 模型 | 数据集 | 数 |
| --- | --- | --- | --- |
| Google 卡，2026-02，无工具 | Gemini 3.1 Pro | MMMU-Pro | 80.5% |
| 同一张卡 | Gemini 3 Pro | MMMU-Pro | 81.0% |
| 同一张卡 | GPT-5.2 / Sonnet 4.6 / Opus 4.6 | MMMU-Pro | 79.5% / 74.5% / 73.9% |
| Llama 4 指令模型卡，2025-04 | Maverick | MMMU | 73.4% |
| 同一张卡 | Maverick | MMMU Pro（Standard 与 Vision 平均） | 59.6% |
| 同一张卡 | Scout | MMMU / MMMU Pro | 69.4% / 52.2% |
| OpenAI GPT-5 博文 | GPT-5 | MMMU | 84.2% |

3.1 Pro 的 MMMU-Pro 80.5% 低于 3 Pro 的 81.0%，而卡上别的推理项 3.1 是涨的。这一行没有一起涨，所以不要说「多模态全面超过上一代」。GPT-5 的 84.2% 是 MMMU，不是 MMMU-Pro。

Llama 4 还报了更接近「读懂文档和图表」的榜。指令模型 Maverick：ChartQA relaxed accuracy 90.0，DocVQA test ANLS 94.4，MathVista 73.7。这些榜卡的是版面和图表理解，不是大学考试推理。基座表和指令表的 shot 数、指标不同，模型卡分成了两张表，引用时要说明是哪一张。

## 多语

Gemini 3.1 卡报 MMMLU：3.1 Pro 92.6%，3 Pro 91.8%，Opus 4.6 91.1%，GPT-5.2 89.6%。这是多语问答准确率。如果题目由英语翻译而来，测到的多半是翻译腔，反映不了该语言的母语分布。AFM 公开弃用这类题，见 `dt-benchmark-gap`。

Llama 4 指令模型报的是 MGSM（多语小学数学）和 MTOB（一本低资源语言的书，分半本和整本，chrF，两个翻译方向）。Maverick 的 MGSM 是 92.3；MTOB 半本 54.0/46.4，整本 50.8/46.7。MGSM 高分说明模型会解多种语言的小学算术题，但不足以代表整体语言能力。MTOB 则要求模型借助上下文中的书，处理预训练里很少见的语言。

## 事实题还在不在主表

Gemini 2.5 技术报告把 SimpleQA 和 FACTS Grounding 放在事实性那一行，并写当时在对照模型里他们最高。Gemini 3.1 Pro 模型卡我读到的主表没有这两行。主表换了轴之后，如果事实性结果只出现在旧报告里，引用时要说明年份。

SimpleQA 是短事实题，答案唯一；FACTS Grounding 卡的是回答是否被给定材料支持。BrowseComp 主要检查能否找到事实，Grounding 检查回答里的陈述是否有给定材料支持。两者一起评测，才能分别了解检索能力和回答是否忠实于材料。

## 追问

- **窗口支持 1M，但 MRCR 1M 只有 26%，该准备什么数据？** 这说明模型在这个长度下仍然经常取错信息。训练样本要达到相应长度，包含多个相似的目标材料和干扰项，并带顺序约束，要求模型取回指定的第几段，见 `dt-longctx-data`。只增加预训练上下文长度，模型并没有练习这个任务。
- **图文对越多，MMMU-Pro 就越高吗？** 不一定。网页 alt-text 更接近图片描述（Caption）和部分 OCR 任务。如果学科题靠题干就能作答，训练主要学到的是文本线索，未必改善看图推理。
