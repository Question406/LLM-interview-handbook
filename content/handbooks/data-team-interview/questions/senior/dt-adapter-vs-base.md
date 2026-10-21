---
id: dt-adapter-vs-base
section: senior
order: 6
level: A
title: Director：这件事该改底座数据，还是只训 feature adapter？
quick: "按问题影响的范围来切：多个功能共同缺的能力（工具 schema、多语指令、有证据支持的拒答）补进底座后训练；只属于一个功能的固定格式或口吻，训 feature adapter；用户私有偏好留在端上。所有问题都回底座 SFT，或都交给 LoRA，说明范围没有切清。"
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

我的判断标准是这个问题影响多少个功能。工具的字段和类型规范（schema）、多语指令、有实际证据支持的拒答，邮件、通知、日历都会用到，应该补进底座的 post 或 mid 阶段。只影响一个功能、格式又很固定的问题，例如通知摘要的口吻、某个 App 的 guided generation schema，训 feature adapter 就够了。用户私有的偏好用端上 adapter 或 few-shot 处理，不能默认进入全球底座，见 `dt-privacy-feedback`。

Director 问这题，想听你怎么划范围。所有问题都回底座监督微调（SFT），每个小格式问题都要付底座迭代的成本；所有问题都交给 LoRA，多个功能共有的缺口就要在每个 adapter 里各修一遍。

## 为什么按范围切

AFM 的 Apple Intelligence 功能就是底座加 adapter 的结构，他们也发现改进通用后训练会同时抬高所有 feature。共性能力放在底座，一次投入，所有功能都受益。

adapter 也不便宜。框架暴露的是 rank-32 LoRA，每个 adapter 和单一基础模型版本绑定，基础模型换代就要重训，存储和分发都有成本。

## 怎么评测，怎么守住旧能力

AFM 的功能评测按邮件、信息、通知分层抽样。adapter 的数据就应该是对应那一层的金标，结果单独报，不要和 MMLU 混在一起。如果决定改底座数据，仍然要守住锚点评测，见 `dt-neg-transfer`。

## 追问

- **adapter 能不能补数学推理？** 小幅的格式问题可以。覆盖性的推理能力，AFM 放在 continued PT 里解决。不要承诺 rank-32 能补竞赛数学。
- **每个功能一个 adapter，会不会占很多存储？** 公开材料说 adapter 占空间，要用 Background Assets 只下载匹配当前版本的那一个。数据岗也应少设计「一人一个 adapter」的方案。
- **guided generation 的格式数据算底座还是 adapter？** AFM 说底座后训练学过这类特殊格式，框架才能稳定工作。跨 App 的格式契约偏底座；某个 App 自己的业务字段偏 adapter，见 `dt-guided-gen-data`。
