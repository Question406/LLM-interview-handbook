---
id: dt-why-apple
section: hm-screen
order: 2
level: S
title: Why Apple, why now：怎么讲 data-centric，而不是「我想做大模型」？
quick: "Why now 可以讲数据工作：过滤、训练配比、合成数据验证，以及根据评测失败补数据，都需要持续改进。Why Apple 则讲你为什么愿意在不使用用户私有日志训练基础模型的约束下做这些事，并用自己的经历说明。不要拿未公开的算力或团队情况作理由。"
companies:
  - apple
tags:
  - Apple
  - Why Apple
  - Data-centric AI
  - Privacy
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

回答 Why now 时，可以从公开报告里的数据工作切入。端侧 2-bit QAT 和 server PT-MoE 的架构与压缩方法已经公开；这轮数据岗面试更适合讲过滤、配比、合成验证，以及如何把评测失败转成下一轮训练数据。回答 Why Apple 时，再说明你为什么愿意在不能使用用户私有日志训练基础模型的约束下，从评测和产品问题中寻找改进方向。

只说「我喜欢生态」或「苹果重视隐私」还不够，要解释这些条件如何影响你的数据工作。guideline 希望你理解这支团队在基础模型开发中的职责。别说「你们算力最大」，也别吹内部编制或未公开参数量。

## Why now：公开叙事已经转到改数据

2025 更新把预训练拆成多段。第一段最吃算力，server 从零训练使用约 13.4T 文本 token；端侧先训练 dense 模型，再通过 sparse-upcycle 得到教师模型，最后进行蒸馏。能力扩张写在后面的 continued pre-training：提高数学 / 代码 / 多语权重（多语从 8% 提到 30%）、验证过的合成、视觉适配、65K 长上下文。后训练进一步增加合成数据，并单独迭代改进工具调用。强化学习（RL）在异步平台上结合奖励模型（RM）和规则奖励。

Scale-only 是「再加 token 和参数，平均 loss 会掉」。Data-centric 是：同样算力下，哪些 token 值得保留，哪些任务需要经过验证的合成数据，以及哪些评测失败应转成下一轮训练数据。AFM 自己写过：过于严格的启发式规则会丢掉高价值 token，所以他们减弱规则，更多使用模型过滤。这正是数据团队可以改善的环节。

## Why Apple：约束本身是工作内容

三家都做基础模型。苹果公开说明的一些约束，会直接影响这个岗位的数据选择：

- 来源边界。许可、公开集、Applebot（尊重 robots.txt，不爬登录墙 / 付费墙），加合成。用户私有数据和交互默认不训基础模型。
- 部署边界。端侧约 3B 不是开放世界 chatbot；更难的推理走 PCC。数据工作要同时服务「简短、隐私敏感、留在本地」和「困难任务只上传所需部分」。
- 改进边界。全球模型走许可 / 爬取 / 合成；「我的摘要口吻」走端上 adapter 或 few-shot，不把用户邮箱内容作为监督微调（SFT）数据。

回答时要说明你怎样在这些条件下改善数据，不能只说自己会清洗 Common Crawl。隐私怎么落地见 `dt-privacy-feedback`。

不要吹内部编制、未公开的参数量或「苹果要超 OpenAI」。这些内容没有公开依据，也不能证明你适合这份工作。

## 口播

「我过去一年的工作是把评测缺口写成可训练数据，而不是改模型宽度。读完 AFM 2025，我看到你们已经把核心预训练和压缩讲清楚了，能力扩张大量写在 continued pre-training、验证合成和工具轨迹标注。我想加入的是这一段：在不用用户私有数据训基础模型的约束下，把数学、工具调用和多模态任务中的失败，转成下一轮训练数据。Why now 是因为公开配方已经从堆规模转到管数据；Why Apple 是因为这条约束我认，而且我有过在类似治理下做合成和回灌的经验。」

把最后一句换成你自己做过的事。没有「类似治理」就老实说你做过质控 / 许可 / PII 过滤，不要假装做过差分隐私生产系统。

## 追问

- **为什么不去 OpenAI / Google？** 给一个和约束有关的理由（端云切分、不用用户日志训 FM、locale 人评），不要贬别家。
- **data-centric 是不是反对 scaling？** 不是。核心预训练仍然需要规模；data-centric 关注新增 token 来自哪里、质量如何验证。AFM 两边都写了。
- **Applebot opt-out 和「公开网页就能训」？** 公开页仍要过 robots、过滤 PII / 脏话 / 低质。回答时要说明这些抓取和使用条件。
