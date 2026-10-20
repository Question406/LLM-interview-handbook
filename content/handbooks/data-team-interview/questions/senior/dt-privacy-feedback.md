---
id: dt-privacy-feedback
section: senior
order: 4
level: S
title: Director：真实世界反馈怎么用，还不把用户数据喂进基础模型？
quick: "先区分基础模型训练、当前请求处理和端上个性化。基础模型使用许可、公开和合成数据；私人偏好可留在设备，用检索或 adapter 改善；需要上传的聚合统计再设计 $\\varepsilon$-DP。PCC、数据不落盘和训练许可是不同问题，不能把点踩原文直接送入下一轮 SFT。"
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

先画出数据用于训练、处理当前请求和个性化的路径。点赞日志不能默认成为 SFT 数据。PCC 对当前请求的处理承诺，也不等于获得了训练许可。

不这么选的理由：guideline 写 Apple cares deeply about governance。把 PCC、本地存储和差分隐私说成一件事，或设计一道「用户点踩进下一周 SFT」的飞轮，治理已经错了。

## 三条通道，现场先画

全球基础模型吃许可、公开集、Applebot、合成。支持页原句：私有个人数据和交互从不用于训练基础模型，除非用户明确选择帮助改进。过滤 PII，避开大规模汇聚个人信息的站。这是训练许可，不是部署通道。

这一轮推理：短且敏感的留端侧；更难的把这一轮需要的最小切片送到 PCC。PCC 的公开承诺是请求用完丢、不拿这轮明文训基础模型。PCC 不是 DP，也不是「可以收集反馈了」。

个性化。「我的摘要口吻」走端上检索 / adapter / few-shot。开发者 LoRA toolkit 也在开发者侧训，并和基础模型版本绑定。邮箱、消息、屏幕默认不出设备，不当下一版 AFM 的 SFT。

真实世界反馈要先问：它要改进的是全球模型、这一轮路由，还是这台设备上的 adapter。三个答案对应三条通道。混在一起就是治理事故。

## 反馈还能怎么用

仍然可以利用反馈改进系统，但要根据用途选择合法的数据来源与处理方式。

用户研究 / 许可研究数据。法律页写了 user studies 是来源之一。这是知情同意的标注，不是静默日志。

聚合失败模式。设备上先把失败打成粗类型（工具写失败、OCR 字段空），再考虑是否用本地 DP 上传计数。2017 的 Learning with Privacy at Scale 讲的是频率统计，不是把邮件原文加噪后当 SFT。$\varepsilon$ 花在计数上，不花在文本上。

合成复现。从聚合类型出发，在许可域里造同类题，不复述用户原文。飞轮的「补洞」走合成和内部标注，见 `dt-data-flywheel`。

明确 opt-in。支持页留了「用户选择帮助改进」的口子。设计上要默认关，打开时说清进哪一条通道、能不能撤回。

端上 adapter。反馈留在设备，改进的是这台手机的行为，不更新全球权重。

差分隐私的定义和 $\varepsilon$ 怎么报，us-tech 的 Apple 章写过。这里只守一句：没有 $\varepsilon$ 的「我们匿名化了」不是 DP。邻居数据集、组合、每日条数上限，讲不清就不要主动用 DP 当挡箭牌。

## 一道会被问的设计

「通知摘要有人点踩，怎么改进模型？」

默认：点踩留在端上，当这条通知的负反馈，调的是本地排序或 few-shot，不回传原文。

若要改进全球摘要能力：看 opt-in 研究集和内部许可邮件语料，或合成「关键限定词被删」的对抗题。不要把点踩原文送进 SFT。

若只想知道「哪类摘要在跌」：设备上分类计数，本地 DP 上传。类别是「删了限定词 / 剧透 / 太长」，不是句子。

评测也要报隐私事故：这一轮证据有没有离设备、日志有没有原文。任务分涨、隐私事故也涨，未满足上线条件。

## 追问

- **PCC 里能不能记日志做飞轮？** 按公开承诺，不能把用户请求当训练语料。调试日志若存在，也不是 foundation model 数据源。
- **开源同行都在用用户对话训下一代，苹果会不会以后也这样？** 以当前公开口径为准。面试里设计仍按「默认不」。口径若变，变的是 opt-in 和治理，不是「日志很好用」。
- **合成会不会间接泄漏用户？** 会，如果种子是用户原文。种子必须来自许可 / 公开 / 内部研究集。聚合类型可以指导「造哪类题」，不能当题面。
