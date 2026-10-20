---
id: dt-data-flywheel
section: panel
order: 1
level: S
title: Panel：评测失败怎么变成下一轮训练信号？
quick: "先用固定评测找出失败类型，判断是覆盖不足、标签错误、泄漏还是奖励设计的问题；再采集或合成相关任务，经质控后用于训练。新发现的失败可以新增金标题，但不能用当前模型的判断改掉旧评测标签。线上日志也不能原样当作 SFT 正例。"
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

这套流程要围绕具体失败展开：先发现问题，再补数据，最后检查同类问题是否减少。只画「收集 → 训练 → 部署」还不够。把线上日志原样用于下一轮监督微调（SFT），可能只是让模型重复自己的错误。

Panel 常会问：给你一个能力缺口，怎样通过数据改善它？guideline 提到的 model feedback 要区分用途。模型可以帮助发现问题、生成候选，但如果同一模型既生成又给自己打分，没有独立验证，就有模型坍缩的风险。

## 白板上画一圈

一次迭代应针对一类失败，并验证它是否改善；新增 10 万条标注本身不代表流程有效。

1. 观测。冻结评测、人评、产品 canary。切片要能指到任务：工具第二跳、图表差值、某 locale 的指令跟随。AFM 的人评按 locale、按 feature adapter 分层，不是只报一个 MMLU。
2. 归因。覆盖不够、标签错、评测泄漏、奖励在 hack、还是解码预算。同一缺口的数据干预完全不同，诊断树见 `dt-benchmark-gap`。
3. 补充模型容易失败的任务。真人示范、难例回采、验证合成、改 mix。能执行验证的（代码、数学、工具状态）优先合成；主观偏好走人和 奖励模型（RM），见 `dt-reward-pref`。
4. 质控。去重、污染检查、验证器（verifier）、抽查。合成要带教师版本和代数。
5. 训练。只动这一圈对应的阶段：覆盖问题多半进 continued PT 或 SFT，偏好问题进 基于人类反馈的强化学习（RLHF），不要每次都从 14T 重训。阶段怎么切见 `dt-pre-mid-post`。
6. 评测更新。新失败模式做成金标，**追加**进冻结集。禁止用当前模型的自动标注刷新旧题的标签。

判断迭代是否有效，要看固定评测中这类失败是否减少，以及新任务的改进有没有损害旧能力。新增 token 数不能单独说明效果。

## 模型反馈哪一段能进训练

低置信度、回答不一致、工具报错和人机分歧，可以触发样本采集，但不能直接作为标准答案。Tesla 数据引擎也是这个形状：影子模式触发采集，金标另走协议。

模型也可以生成 $k$ 条候选，由 verifier 或人保留正确的回答。STaR 和 rejection sampling 使用的就是这种数据。

不能闭环的：同一模型给自己打分再训，没有独立 oracle。Self-Rewarding 论文把这当成研究对象，面试要主动讲 collapse 和风格收敛，见 `dt-self-improve`。

AFM 的工具数据好用。标注平台让参考模型先跑轨迹，人在任意一步回滚、改、再续跑，最后留下成功的主要执行路径（合法 SFT）和被放弃的尝试（失败尝试）。模型生成了候选，人加环境才把候选变成信号。把全部 rollout 直接用于训练，就缺少了验证候选是否正确的步骤。

## 评测集怎么守

飞轮最容易在评测上作弊。

开发集可以跟着模型长，用来 hill-climb。门禁集冻结。新模式另开一页，标明加入日期。训练侧任何生成器、抽取器、过滤模型的版本写进 dataset card。下周 $\Delta$ 对不上版本，飞轮不可复盘。

AFM 多语评测用母语者写的 输入提示（prompt），不用翻译题，因为翻译题不自然。飞轮里评测本身也是数据：题写歪了，回灌会把模型推向歪的目标。

## 追问

- **多久转一圈？** 按失败模式的验证周期，不是按日历。工具类有执行环境，可以周更；主观人评按抽检批次。
- **线上用户交互能进飞轮吗？** 在苹果，默认不能进基础模型。能进的是聚合后的、许可过的、或端上 adapter。见 `dt-privacy-feedback`。
- **失败太稀怎么办？** 提高触发召回（低置信、互不一致），离线再筛。稀有类用合成和分层，不要等自然出现。
