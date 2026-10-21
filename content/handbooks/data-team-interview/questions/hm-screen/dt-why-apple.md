---
id: dt-why-apple
section: hm-screen
order: 2
level: S
title: Why Apple, why now：怎么讲出你对 data-centric 的兴趣？
quick: "Why now 讲数据工作：公开报告里能力扩张越来越多写在过滤、配比、合成验证和把评测失败转成训练数据上。Why Apple 讲你为什么愿意在不使用用户私有日志训练基础模型的约束下做这些事，并用自己的经历说明。不要拿未公开的算力或团队情况作理由。"
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

Why now，我会从公开报告里的数据工作切入：端侧 2-bit QAT 和 server PT-MoE 的架构与压缩方法已经公开，这轮数据岗面试更适合讲过滤、配比、合成验证，以及怎样把评测失败转成下一轮训练数据。Why Apple，则说明你为什么愿意在不能用用户私有日志训练基础模型的约束下，从评测和产品问题里寻找改进方向。

「我喜欢生态」「苹果重视隐私」太泛，要讲清这些条件怎样影响你的数据工作。guideline 希望你理解这支团队在基础模型开发中的职责。

## Why now：公开叙事已经转到改数据

2025 更新把预训练拆成了多段。第一段最吃算力，server 从零训练用了约 13.4T 文本 token；端侧先训练 dense 模型，再通过 sparse-upcycle 得到教师模型，最后做蒸馏。能力扩张写在后面的 continued pre-training 里：提高数学、代码和多语的权重（多语从 8% 提到 30%），加入验证过的合成数据，做视觉适配，扩到 65K 长上下文。后训练进一步增加合成数据，并单独迭代改进工具调用。强化学习（RL）在异步平台上结合奖励模型（RM）和规则奖励。

这正好对应 scale-only 和 data-centric 的区别。Scale-only 的思路是「再加 token 和参数，平均 loss 就会降」。Data-centric 关心的是：同样的算力下，哪些 token 值得保留，哪些任务需要经过验证的合成数据，哪些评测失败应该转成下一轮训练数据。AFM 自己写过，过于严格的启发式规则会丢掉高价值 token，所以他们减弱了规则，更多使用模型过滤。这正是数据团队能改善的环节。

## Why Apple：约束本身就是工作内容

三家都在做基础模型。苹果公开说明的一些约束，会直接影响这个岗位怎样选数据：

- 来源边界：许可数据、公开数据集、Applebot 抓取的页面（尊重 robots.txt，不爬登录墙和付费墙），再加上合成数据。用户私有数据和交互默认不用来训练基础模型。
- 部署边界：端侧约 3B 的模型不是开放世界的 chatbot，更难的推理走 PCC。数据工作要同时服务两类需求：简短、隐私敏感、留在本地的任务，以及只上传所需部分的困难任务。
- 改进边界：全球模型靠许可、爬取和合成数据改进；「我的摘要口吻」这类需求走端上 adapter 或 few-shot，不把用户邮箱内容当作监督微调（SFT）数据。

回答时讲你怎样在这些条件下改善数据；会清洗 Common Crawl 只是基本功。隐私怎样落地，见 `dt-privacy-feedback`。

## 我会这么开口

「我过去一年的工作是把评测缺口写成可训练数据。读完 AFM 2025，我看到你们已经把核心预训练和压缩讲清楚了，能力扩张大量写在 continued pre-training、验证合成和工具轨迹标注。我想加入的是这一段：在不用用户私有数据训基础模型的约束下，把数学、工具调用和多模态任务中的失败，转成下一轮训练数据。Why now 是因为公开配方已经从堆规模转到管数据；Why Apple 是因为这条约束我认，而且我有过在类似治理下做合成和回灌的经验。」

最后一句换成你自己做过的事。没有「类似治理」的经历，就如实说你做过质控、许可或 PII 过滤，不要假装做过差分隐私生产系统。

## 哪些理由别用

别说「你们算力最大」，也别吹内部编制、未公开的参数量或「苹果要超 OpenAI」。这些内容没有公开依据，也证明不了你适合这份工作。

## 追问

- **为什么不去 OpenAI 或 Google？** 给一个和约束有关的理由，比如端云切分、不用用户日志训练 FM、按 locale 做人评，不要贬低别家。
- **data-centric 是不是反对 scaling？** 两者并存。核心预训练仍然需要规模；data-centric 关注的是新增 token 从哪里来、质量怎样验证。AFM 两方面都写了。
- **Applebot 有 opt-out，那「公开网页就能训」吗？** 公开页面仍要过 robots 检查，还要过滤 PII、脏话和低质内容。回答时要讲清这些抓取和使用条件。
