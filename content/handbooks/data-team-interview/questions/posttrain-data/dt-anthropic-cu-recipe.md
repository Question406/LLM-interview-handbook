---
id: dt-anthropic-cu-recipe
section: posttrain-data
order: 33
level: S
title: Anthropic 做电脑使用，训练环境为什么故意很少、还断网？
quick: "少、简单、离线：Anthropic 公开说训练只用了计算器、文本编辑器这类少量可重置的软件，训练期断网。重点是让模型看屏幕像素、数准坐标，用点击和键入直接操作人用的软件，不给它特制 click_ok API。模型原有的视觉和工具能力也很关键，效果不能全归因于 GUI 轨迹数量。"
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

先选少量简单、可重置的离线软件，让模型学会看屏幕、定位像素并点击。模型本身已经有较强的视觉和工具能力，训练环境不必一开始就覆盖所有真实桌面软件。公开出处是 Anthropic 2024-10 的 Developing a computer use model：RL 超参没公开，但环境配方写得很明确。

## 为什么少而简单就够

他们说训练只用了少数几件简单软件，点名的是计算器和文本编辑器；出于安全考虑，训练期间不让模型上网。这些数据和模型原有的视觉、工具能力结合起来，模型就能在真实桌面上分解步骤、点击按钮，卡住时重试。这对应 Yao 说的「先验 + 环境」，见 `dt-shunyu-second-half`。公开内容只写到这些，我不会去编内部的 OSWorld 规模。

GUI 数据也不是越多越好。真实网页上有注入、有金标泄漏、有会动的广告，观测被干扰时，坐标标签也可能不再对应正确的动作。断网和 Codex「容器轨迹开始后断网」是同一条纪律，见 `dt-codex-rl-env`。

博文还单独点出了像素计数：模型不会数像素，鼠标指令就会漂，就像模型数不清 banana 里有几个 a。

## 让模型去迁就工具

博文的中心句是：以前开发者给模型特制工具和环境，电脑使用则是让模型去用人已经在用的软件。落到数据上，动作空间就是点击和键入，模型不调用 `click_ok()` 这类定制 API。检查器仍然要自己写（比如 OSWorld 脚本），任务则要长得像真人的工作，别写成玩具 API 序列。截图的分辨率模式也要抽样覆盖，见 `dt-multimodal-data`。ComputerRL 后来做了 API 和 GUI 混合，是另一条追求效率的路线，面试时要分开讲。

这也是它和工具 JSON agent 的区别：JSON agent 只要改字段和类型规范（schema）就能适配，电脑使用面对的是像素和动作位置，两套数据要分开判断质量，共用一个 `quality` 字段判断不了。

## 成功轨迹也要清洗

Anthropic 自己录 demo 时，模型也会中途点停录屏、跑去看黄石公园照片。成功轨迹里的这类胡点要当作被放弃的尝试处理，见 `dt-gui-traj`。

## 追问

- **prompt injection 算数据问题吗？** 算。截图里的恶意文字会进入观测结果（observation）。训练和评测我都会放注入页，正确行为是拒绝或停下。

相关：监督微调（SFT）轨迹的筛选见 `dt-gui-traj`，规模化强化学习（RL）见 `dt-gui-agent-rl`。
