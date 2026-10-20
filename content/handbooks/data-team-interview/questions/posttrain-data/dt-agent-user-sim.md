---
id: dt-agent-user-sim
section: posttrain-data
order: 15
level: A
title: Agent 多轮数据里的「用户」用 LLM 模拟，坑在哪？
quick: "模拟器只生成用户话，不能看到隐藏数据库或完整内部政策。成功由真实状态和政策 grader 判断。检查过度配合、泄密、单一文风和无法结束等问题，评测换种子或教师，再人工抽查，避免 agent 只适应模拟用户。"
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

模拟器只负责生成用户话，是否成功由环境状态和政策 grader 判断。多轮 agent 数据常需要模拟用户，但模拟器的满意反馈不能作为 oracle。公开锚点是 τ-bench：任务要在多轮对话里改库，用户由语言模型扮演。

常见误区是：训练跟着模拟器转。它会一次把所有槽位给齐、把订单号主动说出来、或一直聊到没有合法停。换成真人后，成功率就可能明显下降。

## 模拟器会干什么坏事

过度合作。真人会改主意、给错邮箱、中途不确认。模拟器常一次把所有槽位给齐。训出来的 agent 不会追问，见 `dt-tool-write-confirm`。

泄露。模拟器 输入提示里若有数据库真相，它会把订单号主动说出来，agent 没调工具也对。看起来 $\mathrm{pass}^{k}$ 很高。

风格单一。同一教师扮用户，agent 只适应这种说话方式。换真人就掉。和教师偏差同构。

永不结束。模拟器一直聊，轨迹没有合法停。要给模拟器停条件：目标达成、用户放弃、轮次上限。

## 合同

模拟器：只出用户话。看不到隐藏库，看不到政策全文（最多看到它作为用户该知道的）。

grader：库状态 + 政策规则。用户是否「满意」不当金标。

人工检查可以抽 100 段模拟对话，标记是否像真人、是否泄露隐藏信息。$\kappa$ 低先改模拟器说明书，见 `dt-kappa-code`。

苹果：AFM 的人在环平台是更贵的正解，真人当用户、模型当 agent。规模不够时才上模拟器，模拟器版本进 lineage。用户日志默认不进基础模型；许可研究集另说。

## 追问

- **训练和评测用同一个模拟器？** 会过拟合模拟器。评测我会换种子、换教师、加人抽检。
- **$\mathrm{pass}^{k}$ 低是 agent 差还是模拟器吵？** 先看模拟器是否在同一任务上自己前后矛盾。用户侧不稳定，agent 再稳也过不了 $k$ 次，见 `dt-tau-passk`。
- **用户日志代替模拟器？** 苹果基础模型默认不行。许可研究集另说。
