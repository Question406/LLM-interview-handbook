---
id: data-strong-weak
section: data
order: 12
level: A
title: Strong-to-Weak Distillation 什么时候有效？什么时候会失败？
quick: >-
  教师给的轨迹得是学生自己搜不到、但还能模仿得了的，distillation
  才有效。教师推理超出学生能力、过程太长、依赖学生没有的工具或知识，或者和部署任务分布不一致，直接模仿就会失败。办法是先量可学性，再压缩、过滤或改成
  on-policy distillation。
tags:
  - Distillation
  - Data
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: MiniLLM — knowledge distillation of large language models
    url: 'https://arxiv.org/abs/2306.08543'
    type: primary
---

Strong-to-weak distillation 有效的前提是教师的轨迹落在学生可模仿的 capability range 内：学生自己搜不到这条路，但看了能学会。推理太长、依赖学生没有的隐含知识或工具，直接做 SFT 就会失败，学生可能只学到了措辞，复现不了决策。「教师越强、数据越好」这个说法不成立。

举个例子，教师在做题时调了代码解释器，最终答案很漂亮，可学生线上没有这个工具。把这条轨迹拿来 SFT，学生学到的是「这里应该冒出一个精确数字」，这是不可见工具泄漏，并没有学到能力。所以教师最终答案好，也不代表每个 token 都适合当学生的监督。这和 teacher model（teacher）偏差（`data-teacher-bias`）是连着的：就算可学，也可能把风格上的 shortcut 一起蒸进去。

## 先量可学性，再决定怎么喂

可学性可以这样量：学生在这条轨迹上的 likelihood、teacher-forced 成功率，或者学生自己 sampling $k$ 次能不能碰到等价答案。学生完全复现不了的超长推理，先压缩 rationale、拆子任务或者做 curriculum，别整段塞进 SFT。具体手段有 simplification 或长度截断、difficulty filtering、student-aware rejection sampling（只留学生能部分复现的轨迹），还有 on-policy distillation，用学生自己的分布做提议，教师只负责打分或改写。分布也要和部署对齐。

可学性过滤本身也要做成实验：按学生 likelihood 的分位切成易、中、难三档，各训一小步，看哪一档的边际收益最高。全难档掉点，说明超了容量；全易档不涨，说明没有新信息。过滤后条数变少不等于质量下降，目标是 token 效率。

## 失败怎么用实验拆开

对照至少四组：原始教师轨迹、压缩后的轨迹、学生自 sampling 加过滤、人类或弱教师混合。看学生的 holdout、长度、格式服从，以及 out-of-distribution 数据（OOD，即与训练数据明显不同的数据）有没有回退。如果只有原样 imitation 在涨、压缩版不涨，说明蒸的是风格，决策没学到；如果压缩版涨、原样版掉，说明超了容量。比的时候 token budget 要对齐，否则长的教师轨迹会靠长度赢。

失败原因常见的就四种：超出容量；风格太长，占满了梯度；依赖不可见的工具或私有知识；教师和线上 query 的分布不匹配。弱模型教弱模型，或者未经验证就重新用于训练，会滑向自污染（`data-synthetic-self-contamination`）。在 SFT pipeline（`data-sft-pipeline`）里，教师只是候选生成器，能不能进训练靠验证器（verifier）和学生的边际增益来决定。说到底，有效的 distillation 是把教师轨迹推回到学生的 learnability limits 上，最强模型的 chain of thought 原样粘过去是不行的。

## 追问

**答案对、过程学不会，怎么办？**
只监督 final answer、重写一段短 rationale，或者拆成可验证的子题。整段 CoT 进损失（loss），会蒸进去假推理。

**一定要用最强的教师吗？**
不必。中等强度、能复现、带 verifier 的轨迹，往往比超长的闭源 chain of thought 更适合小模型。

**和 Weak-to-Strong 是什么关系？**
那是用弱监督训强模型，这题是用强轨迹教弱模型。两者都怕学不会的信号，只是容量瓶颈的方向相反。

**怎么证明 distillation 有效？**
同等 token 下对比「可学子集」和「全量 imitation」，看 holdout 和 OOD。教师自己的分说明不了问题。
