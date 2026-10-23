---
id: dt-data-story
section: hm-screen
order: 1
level: S
title: HM 30 分钟：怎么把项目讲成「数据解锁了能力」？
quick: "按数据方案讲，不按简历时间线：模型原来做不到什么、我认为原因是什么、改了哪些数据、对照实验支不支持，最后报一条能推翻这个判断的指标。架构只在解释资源限制时出现，主线别变成换了 MoE 或 GQA。"
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

我会按数据方案讲，不按简历时间线。HM 这一轮只有 30 分钟，想听的是你的策展或合成有没有让模型做到原来做不到的事，guideline 里也写明了要 frame around data。架构可以出现，但只当约束用，比如显存不够、没法靠堆参数，所以才去挖数据。主线一旦变成「我们上了 MoE、换了 GQA」，听起来就像在面架构岗。

开头一句先说缺口，而且要具体，比如「模型做多跳工具调用，到第二步就开始编参数」。图表题能读数轴却不会算差值，某个语种的指令跟随比英语低 20 个点，都算这种程度的具体。接着用一句话说我当时的判断：是覆盖不够、标签错了、合成数据没验证，还是评测被污染了。这句话要能被数据实验推翻，不然后面没法讲对照。

然后讲我改了什么，只讲自己亲手做的那一段，可能是种子策展、难度演化、verifier 过滤、近重复去重，也可能是难例回灌或改配比。〔填：你的缺口、判断和干预，各一句。〕如果是合成数据，顺带交代经历了几代生成、教师是哪个版本、怎么验证的。来源不清、不验证，又把多代生成结果反复送回训练，有放大幻觉的风险，HM 很可能会追着问，细节见 `dt-self-improve`。

再说对照：同一份算力、同一套冻结评测集，只改数据。当时没做对照就直说，「当时没做，如果重来，我会留一份 token 数相同的旧 mix」。最后报一个证伪指标，哪个数涨了算赢，哪个数不动说明我判断错了。比如工具参数合法率上升、任务成功率持平，那补上的是格式，能力没变。〔填：你的指标和结果。〕

这几件事按顺序说，九十秒左右，被打断也能停在一句完整的话上。团队人数、roadmap、「we shipped v2」都不用报。HM 追问一般往两边走，一边是过滤阈值和 verifier 怎么实现，一边是它们怎么影响产品能力，看对方问哪边再展开。

## 追问

**什么样的例子算「解锁」，有没有公开的可以对一下？**
有，你的项目对上其中一种就行：过滤扔掉噪声，留下的 token 让某项能力冒出来；合成用可验证的生成补上原分布里几乎没有的任务；回灌把评测或线上失败直接变成下一轮种子。FineWeb-Edu 同样从 Common Crawl 出发，用教育价值分类器重新筛，小模型在知识和推理基准上的提升来自留下的那部分 token。Self-Instruct 面对的是人写种子覆盖不了指令空间，于是用模型扩写任务再过滤，把 instruction following 从「几乎没有」拉了起来。AFM 2025 也写过，放松过猛的启发式、加入模型过滤是为了少扔高价值 token，数学和代码的合成数据要过执行或标准答案检查，才进 continued pre-training。

**你为什么不换更大的模型？**
换了更大的模型，吃的还是同一份有缺口的数据。缺口在工具轨迹或某类图表上，就先补那一类可验证数据，再谈扩容。AFM 自己就是端侧约 3B 加 server，能力扩展大量写在数据和后训练上。

**这不就是跑了一遍蒸馏吗？**
蒸馏只是生成数据的一种方式。数据能不能进训练，靠独立的 oracle 把关，比如单测、符号检查、执行、人工抽查；增益看冻结集上的目标切片，不看教师给自己打的分。

**没有合成项目，或者项目是推荐、CV，怎么讲？**
照样能讲。难例挖掘、标注协议、配比、评测隔离都是数据干预。推荐和 CV 的闭环形状也一样：失败触发、质控、进训练、冻结评测，把标签和泄漏讲清楚就行。

**HM 是研究出身，想听论文怎么办？**
九十秒里点一篇和你的干预同构的论文就够了，展开留到 `dt-paper-pitch`，别把 HM 面试开成 journal club。
