---
id: dt-agent-user-sim
section: posttrain-data
order: 15
level: A
title: Agent 多轮数据里的「用户」用 LLM 模拟，坑在哪？
quick: "模拟器只生成用户的话，看不到隐藏数据库和完整内部政策；成功由真实环境状态和政策 grader 判断，模拟器的满意反馈不能当 oracle。要检查过度配合、泄密、单一文风和无法结束这几类问题，评测时换种子或教师并人工抽查，避免 agent 只学会适应模拟用户。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - Evaluation
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "τ-bench: A Benchmark for Tool-Agent-User Interaction"
    url: https://arxiv.org/abs/2406.12045
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "FireAct: Toward Language Agent Fine-tuning"
    url: https://arxiv.org/abs/2310.05915
    type: primary
---

模拟器只负责生成用户说的话，任务是否成功由环境状态和政策 grader 判断。多轮 agent 数据经常需要模拟用户，但模拟器表示「满意」不能当 oracle。公开的参照是 τ-bench：任务要在多轮对话里修改数据库，用户由语言模型扮演。

## 模拟器会把 agent 带偏

如果训练跟着模拟器转，agent 学到的是适应这个模拟器，换成真人后成功率可能明显下降。常见的几种偏差：

- **过度配合。** 真人会改主意、给错邮箱、中途不确认；模拟器常常一次把所有槽位给齐。这样训出来的 agent 不会追问，见 `dt-tool-write-confirm`。
- **泄露。** 模拟器的输入提示里如果有数据库真相，它会主动报出订单号，agent 没调工具也能答对，$\mathrm{pass}^{k}$ 看起来很高。
- **风格单一。** 一直由同一个教师扮演用户，agent 只适应这一种说话方式，换真人就掉。这和教师偏差是同一类问题。
- **永不结束。** 模拟器会一直聊下去，轨迹没有合法的终点。要给模拟器设停止条件：目标达成、用户放弃、轮次上限。

## 怎么划分职责

模拟器只输出用户的话。它看不到隐藏的数据库，也看不到政策全文，最多只知道一个用户本该知道的部分。

grader 根据数据库状态和政策规则判定成败，用户是否「满意」不当金标。

人工检查可以抽 100 段模拟对话，标注是否像真人、是否泄露了隐藏信息。如果标注一致性 $\kappa$ 低，先改模拟器的说明书，见 `dt-kappa-code`。

训练和评测不要用同一个模拟器，否则会过拟合它。评测时换种子、换教师，再加人工抽检。

真人当用户、模型当 agent 的人在环平台更贵，但更接近真实分布，AFM 2025 报告的工具平台就是这种形式。规模不够时再上模拟器，模拟器版本要进 lineage。

## 追问

- **$\mathrm{pass}^{k}$ 低，是 agent 差还是模拟器太吵？** 先看模拟器在同一任务上是否自己前后矛盾。用户侧不稳定，agent 再稳也过不了 $k$ 次，见 `dt-tau-passk`。
