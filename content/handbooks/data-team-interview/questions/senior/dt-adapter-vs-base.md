---
id: dt-adapter-vs-base
section: senior
order: 6
level: A
title: Director：这件事该改 base model 数据，还是只训 feature adapter？
quick: >-
  看问题影响多少个功能。多个功能共有的缺口，比如工具 schema、multilingual 指令、有证据支持的拒答，补进 base model
  post-training；只属于一个功能的固定格式或口吻，训 feature adapter；用户私有偏好留在 on-device。全回 base
  model SFT 或全交给 LoRA，都说明范围没切清。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

我看这个问题影响多少个功能。工具的字段和类型规范（schema）、multilingual 指令、有实际证据支持的拒答，邮件、通知、日历都会用到，就补进 base model 的 post 或 mid 阶段。只影响一个功能、格式又很固定的，比如通知摘要的口吻、某个 App 的 guided generation schema，训 feature adapter 就够了。用户私有的偏好用 on-device adapter 或 few-shot，默认不进全球 base model，见 `dt-privacy-feedback`。

举个例子，如果邮件、通知、日历几个功能在调工具时都会把 schema 填乱，这是共性缺口，交给 LoRA 的话每个 adapter 都得各修一遍。反过来，只是通知摘要的口吻不对，为它回 base model 做 SFT，就要付一整轮 base model 迭代的成本。Director 问这题，就是想听你怎么划这条线。

base model 这边的理由是，AFM 的 Apple Intelligence 功能本来就是 base model 加 adapter 的结构，他们也发现改进通用 post-training 会把所有 feature 一起抬高。共性能力放 base model，投入一次，所有功能都受益。adapter 这边也有成本：框架暴露的是 rank-32 LoRA，每个 adapter 绑定一个基础模型版本，base model 换代就得重训，存储和分发也都要花钱。

评测跟着这个切法走。AFM 的功能评测按邮件、信息、通知分层 sampling，adapter 的数据就用对应那一层的 gold labels，结果单独报，别和 MMLU 混在一起。决定改 base model 数据的话，regression evaluation 照样要守住，见 `dt-neg-transfer`。

## 追问

**adapter 能补 mathematical reasoning 吗？**
小幅的格式问题可以。覆盖性的 reasoning capability，AFM 是放在 continued PT 里解决的，别承诺 rank-32 能补竞赛数学。

**每个功能一个 adapter，存储吃得消吗？**
公开材料说 adapter 占空间，要用 Background Assets 只下载匹配当前版本的那一个。数据岗也应少设计「一人一个 adapter」的方案。

**guided generation 的格式数据算 base model 还是 adapter？**
看范围。AFM 说 base model post-training 学过这类特殊格式，框架才能稳定工作，所以跨 App 的格式契约偏 base model，某个 App 自己的业务字段偏 adapter，见 `dt-guided-gen-data`。

**全都交给 LoRA，迭代不是更快吗？**
单个功能是快，但多个功能共有的缺口要在每个 adapter 里各修一遍，base model 一换代，这些 adapter 还得全部重训。
