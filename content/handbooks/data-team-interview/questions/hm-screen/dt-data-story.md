---
id: dt-data-story
section: hm-screen
order: 1
level: S
title: HM 30 分钟：怎么把项目讲成「数据解锁了能力」？
quick: "按数据方案讲，不按简历时间线。用 90 秒讲清模型原来做不到什么、你认为原因是什么、你改了哪些数据、对照实验是否支持这个判断，最后报一条能检验假说的指标。架构只在解释资源限制时出现，别把故事讲成换了 MoE 或 GQA。"
companies:
  - apple
tags:
  - Apple
  - Hiring Manager
  - Data Story
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Self-Instruct
    url: https://arxiv.org/abs/2212.10560
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会按数据方案讲，不按简历时间线。HM 这轮 30 分钟想听的是：你的策展或合成，有没有让模型做到原来做不到的事。guideline 也写明要 frame around data。架构可以出现，但只作为约束，比如显存不够、不能靠堆参数，所以才去挖数据。如果主线变成「我们上了 MoE、换了 GQA」，听起来就像在面架构岗。

## 90 秒里只留五件事

按这个顺序说，被打断时也能停在一句完整的话上：

1. 先说缺口：模型在哪一类任务上稳定失败。要具体，比如多跳工具调用到第二步就编造参数；图表题能读数轴，却不会算差值；某语种的指令跟随比英语低 20 个点。
2. 再说假说：失败是因为覆盖不够、标签错了、合成数据没验证，还是评测被污染了。用一句话说，而且这句话要能被数据实验推翻。
3. 接着说干预，也就是你改了什么：种子策展、难度演化、验证器（verifier）过滤、近重复去重、难例回灌或配比。只讲你亲手做的那一段。
4. 然后说对照：同一算力、同一套冻结评测集，只改数据。当时没做对照，就直说「当时没做，如果重来，我会留一份 token 数相同的旧 mix」。
5. 最后说证伪指标：哪个数涨了算赢，哪个数持平或下降说明假说错了。例如工具参数合法率上升、任务成功率持平，说明你补上的是格式，能力没有变化。

团队人数、roadmap、"we shipped v2" 都不用报。HM 追问时，可以从两个角度展开：过滤阈值和验证器怎样实现，以及它们怎样影响产品能力。看对方问什么，再决定展开哪一部分。

## 什么样的例子算「解锁」

公开的例子可以帮你校准。FineWeb-Edu 同样从 Common Crawl 出发，用教育价值分类器重新筛选，小模型在知识和推理基准上的提升，来自留下来的那部分 token 本身。Self-Instruct 面对的是人写的种子不够覆盖指令空间，于是用模型扩充任务再过滤，把 instruction following 从「几乎没有」拉了起来。AFM 2025 也写过同类做法：放松过猛的启发式、加入模型过滤，是为了少扔高价值 token；数学和代码的合成数据要通过执行或标准答案检查，才进入 continued pre-training。

你自己的项目对上其中一种就行：

- 过滤：扔掉的是噪声，留下的 token 让某项能力冒了出来。
- 合成：原来分布里几乎没有的任务，用可验证的生成补上。
- 回灌：把评测或线上失败直接变成下一轮种子。

讲合成数据时，要说明经历了几代生成、用的是哪个教师版本、怎样验证。如果来源不清、没有验证，又把多代生成结果反复送回训练，就有放大幻觉的风险，细节见 `dt-self-improve`。

## 两个容易把你带偏的问题

「你为什么不换更大的模型？」换了更大的模型，吃的还是同一份有缺口的数据。缺口在工具轨迹或某类图表上，就先补那一类可验证数据，再谈扩容。AFM 自己就是端侧约 3B 加 server，能力扩展大量写在数据和后训练上。

「这算不算你只是跑了蒸馏？」蒸馏只是生成数据的方式。数据能不能进训练，靠独立的 oracle（单测、符号检查、执行、人工抽查）把关；增益看冻结集上的目标切片，不看教师给自己打的分。

## 追问

- **没有合成项目？** 讲难例挖掘、标注协议、配比或评测隔离。策展也是数据干预。
- **项目是推荐或 CV，不是 LLM？** 闭环的形状一样：失败触发、质控、进训练、冻结评测。把标签和泄漏讲清楚就行。
- **HM 是研究出身，想听论文？** 90 秒里点一篇和你的干预同构的论文，展开留给 `dt-paper-pitch`。别把 HM 面试开成 journal club。
