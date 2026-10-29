---
id: dt-anthropic-cu-recipe
section: posttrain-data
order: 33
level: S
title: Anthropic 做电脑使用，训练环境为什么故意很少、还断网？
quick: >-
  少、简单、离线：Anthropic
  公开说训练只用了计算器、文本编辑器这类少数可重置的软件，训练期断网。重点是让模型看屏幕像素、数准坐标，用点击和键入直接操作人用的软件，不给它特制的
  click_ok API。效果有很大一部分来自模型原有的视觉和工具能力，别全归到 GUI trajectories 数量上。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Developing a computer use model
    url: 'https://www.anthropic.com/research/developing-computer-use'
    type: primary
  - title: Computer use tool
    url: >-
      https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Anthropic 的配方是少、简单、离线：挑少数几件简单、可重置的离线软件，让模型学会看屏幕、定位像素并点击。模型本身已经有较强的视觉和工具能力，训练环境不必一开始就覆盖所有真实桌面软件。出处是 Anthropic 2024-10 的 Developing a computer use model，RL 超参没公开，但环境配方写得很明确。

他们说训练只用了少数几件简单软件，点名的是计算器和文本编辑器；出于安全考虑，训练期间不让模型上网。这些数据和模型原有的视觉、工具能力结合起来，模型就能在真实桌面上分解步骤、点击按钮，卡住了重试。这对应 Yao 说的「先验 + 环境」（见 `dt-shunyu-second-half`）。公开内容只写到这些，我不会去编内部的 OSWorld 规模。

博文还单独点出了像素计数。模型不会数像素，鼠标指令就会漂，就像模型数不清 banana 里有几个 a。

博文的中心句是：以前开发者给模型特制工具和环境，电脑使用则是让模型去用人已经在用的软件。落到数据上，动作空间就是点击和键入，模型不调用 `click_ok()` 这类定制 API。checker 还是要自己写（比如 OSWorld 脚本），任务要长得像真人的工作，别写成玩具 API 序列。截图的分辨率模式也要 sampling 覆盖（见 `dt-multimodal-data`）。

成功 trajectories 也要清洗。Anthropic 自己录 demo 时，模型也会中途点停录屏、跑去看黄石公园的照片。成功 trajectories 里的这类胡点要当成被放弃的尝试来处理（见 `dt-gui-traj`）。

## 追问

**GUI 数据是不是越多越好？**
不一定。真实网页上有注入、有 gold labels leakage、有会动的广告，观测被干扰时，坐标标签也可能不再对应正确的动作。训练期断网和 Codex「容器 trajectories 开始后断网」是同一条纪律，见 `dt-codex-rl-env`。

**它和工具 JSON agent 的数据能放在一起管吗？**
要分开判断质量。JSON agent 只要改字段和类型规范（schema）就能适配，电脑使用面对的是像素和动作位置，共用一个 `quality` 字段判断不了。

**ComputerRL 那种 API 加 GUI 混合的做法怎么看？**
那是另一条追求效率的路线，面试时要和 Anthropic 这条让模型迁就人用软件的路线分开讲。

**prompt injection 算数据问题吗？**
算。截图里的恶意文字会进入 observation。训练和评测我都会放注入页，正确行为是拒绝或停下。

相关：SFT trajectories 的筛选见 `dt-gui-traj`，规模化 RL 见 `dt-gui-agent-rl`。
