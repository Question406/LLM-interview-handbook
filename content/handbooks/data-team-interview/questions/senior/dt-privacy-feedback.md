---
id: dt-privacy-feedback
section: senior
order: 4
level: S
title: Director：真实世界反馈怎么用，还不把用户数据喂进基础模型？
quick: "先问这条反馈要改进什么：基础模型训练、当前请求的处理，还是端上个性化。基础模型使用许可、公开和合成数据；私人偏好留在设备上，用检索或 adapter 改善；需要上传的聚合统计再设计 $\\varepsilon$-DP。PCC、数据不落盘和训练许可是不同问题，不能把点踩原文直接送入下一轮 SFT。"
companies:
  - apple
tags:
  - Apple
  - Privacy
  - Differential Privacy
  - Feedback
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Learning with Privacy at Scale
    url: https://machinelearning.apple.com/research/learning-with-privacy-at-scale
    type: primary
  - title: Private Cloud Compute
    url: https://security.apple.com/blog/private-cloud-compute/
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

先问这条反馈要改进的是什么：全球基础模型、当前这次请求的处理，还是这台设备上的个性化。三个答案对应三条数据通道，各有各的许可。点赞日志不能默认成为 SFT 数据；PCC 对当前请求的处理承诺，也不等于拿到了训练许可。

岗位 guideline 写明 Apple cares deeply about governance。把 PCC、本地存储和差分隐私说成一件事，或者设计一个「用户点踩进下一周 SFT」的飞轮，治理上就已经错了。

## 三条通道

全球基础模型的数据来自许可内容、公开集、Applebot 抓取和合成。支持页的原话是：私有个人数据和交互从不用于训练基础模型，除非用户明确选择帮助改进。训练前还要过滤 PII，避开大规模汇聚个人信息的网站。这一条管的是训练许可。

当前这一轮推理：短且敏感的请求留在端侧；更难的请求只把这一轮需要的最小切片送到 PCC。PCC 的公开承诺是请求用完即丢，不拿这一轮的明文训练基础模型。PCC 和 DP 是两回事，它也不提供收集反馈的许可。

个性化：「我的摘要口吻」这类偏好走端上检索、adapter 或 few-shot。开发者 LoRA toolkit 也是在开发者侧训练，并和基础模型版本绑定。邮件、消息、屏幕内容默认不出设备，不当下一版 AFM 的 SFT 数据。

把三条通道混在一起，就是治理事故。

## 反馈还能怎么用

反馈仍然可以用来改进系统，只是要按用途选合法的数据来源和处理方式：

- 用户研究和许可研究数据。法律页写明 user studies 是数据来源之一。这是知情同意下的标注。
- 聚合失败模式。设备上先把失败归成粗类型（工具写入失败、OCR 字段为空），再考虑是否用本地 DP 上传计数。2017 年的 Learning with Privacy at Scale 讲的是频率统计：$\varepsilon$ 花在计数上，邮件原文不参与。
- 合成复现。从聚合的失败类型出发，在许可范围内造同类题，不复述用户原文。飞轮的补洞走合成和内部标注，见 `dt-data-flywheel`。
- 明确 opt-in。支持页留了「用户选择帮助改进」的口子。设计上要默认关闭，打开时说清数据进哪条通道、能不能撤回。
- 端上 adapter。反馈留在设备上，改进的是这台手机的行为，不更新全球权重。

关于 DP，这里只守一句：没有 $\varepsilon$ 的「我们匿名化了」不是 DP。差分隐私的定义和 $\varepsilon$ 怎么报，us-tech 的 Apple 章写过。邻居数据集、组合、每日条数上限讲不清，就不要主动拿 DP 当挡箭牌。

## 例题：通知摘要有人点踩，怎么改进模型？

默认做法是点踩留在端上，作为这条通知的负反馈，调整的是本地排序或 few-shot，不回传原文。

如果要改进全球的摘要能力，就用 opt-in 研究集和内部许可的邮件语料，或者合成「关键限定词被删」的对抗题。不要把点踩原文送进 SFT。

如果只想知道哪类摘要在变差，就在设备上分类计数，用本地 DP 上传。上传的只是「删了限定词 / 剧透 / 太长」这样的类别。

评测时也要报隐私事故：这一轮的证据有没有离开设备，日志里有没有原文。任务分涨了、隐私事故也涨了，就不满足上线条件。

## 追问

- **PCC 里能不能记日志做飞轮？** 按公开承诺，不能把用户请求当训练语料。即使存在调试日志，也不是基础模型的数据源。
- **开源同行都在用用户对话训下一代，苹果以后会不会也这样？** 以当前公开口径为准，面试里的设计仍按「默认不用」。口径如果变，变的是 opt-in 和治理方式，不会变成「日志很好用就直接用」。
- **合成会不会间接泄漏用户信息？** 如果种子是用户原文，会。种子必须来自许可、公开或内部研究集。聚合类型可以指导「造哪类题」，不能直接当题面。
