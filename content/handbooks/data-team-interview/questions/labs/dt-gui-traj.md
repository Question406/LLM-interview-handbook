---
id: dt-gui-traj
section: labs
order: 31
level: A
title: OSWorld / AndroidWorld：屏幕轨迹哪一段能进 SFT？
quick: "只训练与当时屏幕元素对应、能够回放的动作，丢掉依据过期截图做出的操作。任务成功与否由环境状态验证。OSWorld 的分析中，文本操作历史有帮助，增加历史截图未见同样收益。轨迹来源应是研究集、合成界面或许可演示。"
companies:
  - apple
tags:
  - OSWorld
  - Agent
  - Multimodal
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks"
    url: https://arxiv.org/abs/2404.07972
    type: primary
  - title: AndroidWorld
    url: https://arxiv.org/abs/2405.14573
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

每个动作要对应执行当时无障碍树中的元素，不能依据 800ms 前的旧截图。每一步记录一个能回放的原子动作，最后由环境状态判断任务是否完成。截图作为输入上下文，坐标或手势作为训练目标；截图像素本身不计算交叉熵损失。训练数据也要覆盖不同分辨率模式。AFM 端侧有 tiling / overview / rapid，只在高清上见过细按钮，rapid 会瞎点，见 `dt-multimodal-data`。成功轨迹里的犹豫点击当被放弃的尝试或 mask 掉，别当正例，见 `dt-swe-success-noise`。

不这么选的理由：把「我们标了点击轨迹」整段进 监督微调（SFT）。终局任务过了仍可能点偏、对着过期帧点。只要截图、不要树，点会更飘。树是对齐用的，产品可以不展示。

接到苹果：没有公开 OSWorld 配方。能对上的是屏幕感知 + 工具。用户屏幕默认不进全球 FM，见 `dt-privacy-feedback`。研究集、合成 UI、许可 demo 才能当轨迹源。Android 动态出题的参数随机化是为了抗背题，种子模板仍要和门禁去重。

公开锚点：OSWorld 真实电脑，截图（含鼠标）加 无障碍信息 树；AndroidWorld 116 个人写的任务、20 个应用，参数随机化能变出大量变体，奖励看状态。OSWorld 的分析：分辨率高一点通常更好；多轮文本历史有用，把历史截图越堆越多帮不上；VLM 点不准、会重复点。

## 追问

- **只要截图、不要树？** 能训，点会更飘。树是对齐用的，产品可以不展示。
- **成功轨迹里的犹豫点击？** 当被放弃的尝试或 mask 掉，别当正例，见 `dt-swe-success-noise`。
- **Android 动态出题会不会脏评测？** 参数随机化是为了抗背题。种子模板仍要和门禁去重。
