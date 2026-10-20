---
id: dt-data-story
section: hm-screen
order: 1
level: S
title: HM 30 分钟：项目怎么讲成「数据解锁了能力」，而不是换了架构？
quick: "用 90 秒讲清模型原来做不到什么、你认为原因是什么、你改了哪些数据，以及对照实验是否支持这个判断。最后报一条能检验假说的指标。架构只在解释资源限制时出现，别把故事讲成换了 MoE 或 GQA。"
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

我会按数据方案讲，不按简历时间线。架构可以出现，但只当约束：显存不够所以不能靠堆参数，于是才去挖数据。HM 这轮 30 分钟要听的是策展或合成有没有把模型原来做不到的事做出来。

不这么选的理由：主线放在「我们上了 MoE / 换了 GQA」，像是在面架构岗。guideline 写明要 frame around data。

## 90 秒里我只留五件事

按这个顺序说，被打断也能停在完整句子上：

1. 缺口。模型在哪一类任务上稳定失败。要具体：多跳工具调用到第二步就编造参数；图表题能读数轴但不会算差值；某语种指令跟随比英语掉 20 个点。
2. 假说。失败是覆盖不够、标签错、合成无验证，还是评测被污染。一句话，能被数据实验打死。
3. 干预。你改了什么：种子策展、难度演化、验证器（verifier） 过滤、近重复去重、难例回灌、配比。说你亲手做的那一段。
4. 对照。同一算力、同一评测冻结集，只动数据。没有对照就说「当时没做，若重来我会留一条等 token 的旧 mix」。
5. 证伪指标。哪条数涨了算赢，哪条平或掉算假说错。例如工具参数合法率升、任务成功率平，就是格式数据，不是能力数据。

不要报团队人数、roadmap、"we shipped v2"。HM 追问时，可以从两个角度展开：过滤阈值和验证器如何实现，以及它们怎样影响产品能力。根据对方问的内容选择展开哪一部分。

## 什么样的例子算「解锁」

FineWeb-Edu 的公开故事好用：同样从 Common Crawl 出发，用教育价值分类器重筛，小模型在知识 / 推理基准上的增益来自留下的 文本处理单位（token），不是多训一遍。Self-Instruct 的故事是：人手种子不够覆盖指令空间，用模型扩任务再过滤，才把 instruction following 从「几乎没有」拉起来。AFM 2025 写过同类动作：放松过猛的启发式、加入模型过滤，是为了少扔高价值 token；数学 / 代码合成要过执行或标准答案，才进 continued pre-training。

你自己的项目对上其中一种即可：

- 过滤。扔掉的是噪声，留下的 token 让某一能力出头。
- 合成。原来分布里几乎没有的任务，用可验证生成补上。
- 回灌。评测或线上失败变成下一轮种子，而不是再随机抽一批。

讲合成数据时，要说明经历了几代生成、用了哪个教师版本、怎样验证。如果来源不清、没有验证，又把多代生成结果反复送回训练，就有放大幻觉的风险。细节见 `dt-self-improve`。

## 别被这两句带走

「你为什么不换更大的模型？」更大的模型也吃同一份缺口。缺口在工具轨迹或某类图表，先补那一类可验证数据，再谈扩容。AFM 自己也是端侧约 3B 加 server，能力扩展大量写在数据和后训练，而不是「再大一个数量级」。

「这算不算你只是跑了蒸馏？」蒸馏是生成器。过门靠的是独立 oracle（单测、符号、执行、人抽查），增益看冻结集上的目标切片，不看教师自己给自己打的分。

## 追问

- **没有合成项目？** 用难例挖掘、标注协议、配比或评测隔离。策展也是数据干预。
- **项目是推荐 / CV，不是 LLM？** 闭环形状一样：失败触发、质控、进训练、冻结评测。把标签和泄漏讲清楚就行。
- **HM 是研究出身，要听论文？** 90 秒里点一篇和你干预同构的论文，展开留给 `dt-paper-pitch`。别把 HM 开成 journal club。
