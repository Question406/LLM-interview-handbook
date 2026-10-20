---
id: dt-adapter-vs-base
section: senior
order: 6
level: A
title: Director：这件事该改底座数据，还是只训 feature adapter？
quick: "多种功能共同缺少的能力，优先补到底座；单一功能的固定格式或口吻，可以训练 feature adapter；用户私有偏好留在端上。先判断问题范围，不能所有问题都只靠底座 SFT 或 LoRA。"
companies:
  - apple
tags:
  - Apple
  - Adapter
  - Post-training
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

先看问题是否影响多个功能。工具 字段和类型规范（schema）、多语指令、有实际证据支持拒答，跨邮件 / 通知 / 日历，进底座 post 或 mid。只有一个功能、格式很死？通知摘要口吻、某 App 的 guided generation schema，进 adapter。用户私有偏好则用端上 adapter 或 few-shot，不能默认进入全球底座，见 `dt-privacy-feedback`。

不这么选的理由：Director 听你怎么切范围。所有产品问题都回底座 监督微调（SFT），或所有问题都回 LoRA，范围就没切。端侧 3B 不是开放 chatbot，功能数据不要灌成世界知识。

## 公开切法

AFM：Apple Intelligence 功能靠底座上的 adapter；他们也发现通用后训练会抬所有 feature。框架暴露 rank-32 LoRA，adapter 和单一基础模型版本绑定，新基础模型要重训，所以存储和分发不便宜。端侧模型擅长摘要、抽取、短对话，不是开放世界闲聊。

功能评测 AFM 按邮件 / 信息 / 通知分层样本。adapter 数据就该是那一层的金标，不要和 MMLU 混报。底座数据干预仍要守锚点，见 `dt-neg-transfer`。

## 追问

- **adapter 能不能补数学推理？** 小幅格式可以。覆盖性推理 AFM 放在 continued PT。别承诺 rank-32 能补竞赛数学。
- **每个功能一个 adapter 会不会占很多存储？** 公开说 adapter 占地，要用 Background Assets 只下匹配版本的那一个。数据岗少造「一人一个 adapter」的方案。
- **guided generation 的格式数据算底座还是 adapter？** AFM 说底座后训练过特殊格式，框架才能稳。格式契约跨 App，偏底座；某 App 的业务字段偏 adapter。见 `dt-guided-gen-data`。
