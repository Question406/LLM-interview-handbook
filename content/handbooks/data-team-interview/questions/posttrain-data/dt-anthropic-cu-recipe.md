---
id: dt-anthropic-cu-recipe
section: posttrain-data
order: 33
level: S
title: Anthropic 做电脑使用，训练环境为什么故意很少、还断网？
quick: "Anthropic 公开介绍的训练环境只包含少量简单、可重置的软件，并在训练期断网。重点是让模型根据屏幕像素操作人用的软件，而不是提供专门的 click_ok API。已有视觉和工具能力也很重要，不能把效果全归因于 GUI 轨迹数量。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Anthropic
  - GUI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Developing a computer use model
    url: https://www.anthropic.com/research/developing-computer-use
    type: primary
  - title: Computer use tool
    url: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先选择少量简单、可重置的离线软件，让模型学会看屏幕、确定像素位置并点击。模型已有较强的视觉和工具能力，训练环境不必一开始就覆盖所有真实桌面软件。监督微调（SFT） 轨迹门在 `dt-gui-traj`，规模化 强化学习（RL） 在 `dt-gui-agent-rl`。公开锚点是 2024-10 Anthropic 的 Developing a computer use model：没公开 RL 超参，环境配方写得很死。

常见误区是：GUI 数据越多越好，或给模型特制 `click_ok()` API。网上有注入、有金标、有会动的广告；观测内容受到干扰时，坐标标签也可能不再对应正确动作。

## 少、简单、离线

他们说训练只用了少数几件简单软件，点名计算器和文本编辑器。安全原因：训练期不让模型上网。这些训练数据结合原有视觉和工具能力后，模型能在真实桌面上分解步骤、点击按钮，并在卡住时重试。Yao 的先验 + 环境，见 `dt-shunyu-second-half`。像素计数被单独点出来：不会数，鼠标指令就漂，像模型不会数 banana 里有几个 a。

断网和 Codex 容器轨迹开始后断网是同一纪律，见 `dt-codex-rl-env`。

## 模型去迁就工具

博文的中心句：以前开发者给模型特制工具和环境；电脑使用是让模型去用人已经在用的软件。数据含义：动作空间是点击、键入，不是定制 API。检查器仍要你写（OSWorld 脚本），但任务应该长得像真人工作，不像玩具 API 序列。ComputerRL 后来加 API-GUI 混合，是另一条效率路线，现场分开讲。

他们自己录 demo 也会点停录屏、中途去看黄石公园照片。成功轨迹里的胡点要当被放弃的尝试，见 `dt-gui-traj`。

苹果：用户屏幕默认不进基础模型。研究用合成 UI、许可演示、隔离桌面。端侧分辨率模式要抽样，见 `dt-multimodal-data`。

## 追问

- **真的只靠计算器和编辑器？** 公开只写到这些。我不会发明内部 OSWorld 规模。能讲的是：简单可重置环境 + 坐标技能 + 断网。
- **输入提示（prompt） injection 算数据问题吗？** 算。截图里的恶意字会进 观测结果（observation）。训练和评测我都会放注入页，奖励是拒或停，不是点下去。
- **和工具 JSON agent？** JSON agent 改 字段和类型规范（schema） 就能用。电脑使用面对的是像素和动作位置。两套数据不能只用同一个 `quality` 字段判断质量。
