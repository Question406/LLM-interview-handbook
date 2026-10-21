---
id: dt-data-flywheel
section: panel
order: 1
level: S
title: Panel：评测失败怎么变成下一轮训练信号？
quick: "每一圈只针对一类失败：用固定评测找出失败，判断是覆盖不足、标签错误、泄漏还是奖励设计的问题，再采集或合成相关任务，质控后训练，最后看同类失败是否减少。新失败追加成金标题，旧评测标签保持冻结，不拿当前模型的判断去改。线上日志原样当 SFT 正例，模型只会重复自己的错误。"
companies:
  - apple
tags:
  - Apple
  - Data Flywheel
  - Evaluation
  - Closed Loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "Let's Verify Step by Step"
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Self-Rewarding Language Models
    url: https://arxiv.org/abs/2401.10020
    type: primary
---

飞轮要围绕具体失败转：先发现一类问题，再补对应的数据，最后检查这类问题是否真的减少。光画「收集 → 训练 → 部署」说明不了哪类问题被修好；把线上日志原样用于下一轮监督微调（SFT），可能只是让模型重复自己的错误。

## 为什么要区分模型反馈的用途

Panel 常会问：给你一个能力缺口，怎样通过数据改善它？guideline 提到的 model feedback 要分清用在哪一步。模型可以帮助发现问题、生成候选，但如果同一个模型既生成又给自己打分，没有独立验证，就有模型坍缩的风险。所以判断一次迭代是否有效，要看固定评测里这类失败有没有减少，新增了多少条标注说明不了这一点。

## 一圈怎么转

1. **观测。** 来源是冻结评测和人评。切片要能指到具体任务，比如工具第二跳、图表差值、某个 locale 的指令跟随。AFM 的人评就按 locale 分层报，单个 MMLU 分数看不出这些切片。
2. **归因。** 判断是覆盖不够、标签错了、评测泄漏、奖励被 hack，还是解码预算不足。同一个缺口，原因不同，数据干预就完全不同，诊断树见 `dt-benchmark-gap`。
3. **补模型容易失败的任务。** 可以用真人示范、难例回采、验证合成或调整 mix。能执行验证的领域（代码、数学、工具状态）优先合成；主观偏好走人标和奖励模型（RM），见 `dt-reward-pref`。
4. **质控。** 去重、污染检查、验证器（verifier）、人工抽查。合成数据要记录教师版本和代数。
5. **训练。** 只动这一圈对应的阶段：覆盖问题多半进 continued PT 或 SFT，偏好问题进基于人类反馈的强化学习（RLHF），不需要每次都从 14T 重训。阶段怎么切见 `dt-pre-mid-post`。
6. **更新评测。** 新发现的失败模式做成金标，**追加**进冻结集。禁止用当前模型的自动标注刷新旧题的标签。

最后检查两件事：固定评测中这类失败是否减少，新任务的改进有没有损害旧能力。新增 token 数不能单独说明效果。

## 模型反馈哪些能进训练

低置信度、回答前后不一致、工具报错、人和模型的分歧，这些可以触发样本采集，但不能直接当标准答案。Tesla 的数据引擎也是这个结构：影子模式触发采集，金标另走协议。

模型也可以生成 $k$ 条候选，由 verifier 或人保留正确的那些。STaR 和 rejection sampling 用的就是这种数据。工具数据可以做得更细：AFM 报告描述的标注平台让参考模型先跑轨迹，人可以在任意一步回滚、修改、再续跑，最后留下成功的主执行路径作为 SFT 数据，被放弃的尝试作为失败样本。候选由模型生成，人加上执行环境负责验证；把全部 rollout 直接拿去训练，就跳过了验证这一步。

不能闭环的情况是：同一个模型给自己打分再训练，中间没有独立 oracle。Self-Rewarding 论文把这当作研究对象，面试时要主动讲 collapse 和风格收敛的风险，见 `dt-self-improve`。

## 评测集怎么守

飞轮最容易在评测上作弊。开发集可以跟着模型一起长，用来 hill-climb；门禁集必须冻结。新失败模式另开一页，标明加入日期。训练侧所有生成器、抽取器、过滤模型的版本都写进 dataset card，否则下周的 $\Delta$ 对不上版本，这一圈就没法复盘。

评测本身也是数据。AFM 的多语评测用母语者写的输入提示（prompt），不用翻译题，因为翻译题不自然。题写歪了，回灌进飞轮就会把模型推向歪的目标。

## 追问

- **多久转一圈？** 按失败模式的验证周期，不按日历。工具类有执行环境，可以每周一圈；主观人评按抽检批次走。
- **线上用户交互能进飞轮吗？** 要先过许可和隐私这一关。能进的是聚合后的、经过许可的数据，见 `dt-privacy-feedback`。
- **失败太稀疏怎么办？** 提高触发的召回（低置信、互不一致都触发），离线再筛。稀有类别用合成和分层采样主动补。
