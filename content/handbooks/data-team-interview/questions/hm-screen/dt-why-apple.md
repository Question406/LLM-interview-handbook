---
id: dt-why-apple
section: hm-screen
order: 2
level: S
title: 'Why Apple, why now：怎么讲出你对 data-centric 的兴趣？'
quick: >-
  Why now 讲数据工作：公开报告里能力扩张越来越多写在过滤、data mix、合成验证，以及把评测失败转成训练数据上。Why Apple
  讲我为什么愿意在不用用户私有日志训基础模型的约束下做这件事，再拿自己的经历证明。未公开的算力、团队情况别拿来当理由。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Applebot model training and individual privacy rights
    url: 'https://support.apple.com/en-us/120320'
    type: primary
  - title: Datasets used for Apple Intelligence
    url: 'https://www.apple.com/legal/ai-regulations/training-data/'
    type: primary
---

Why now 我讲数据工作，Why Apple 我讲约束。on-device 2-bit QAT 和 server PT-MoE 的架构与压缩方法已经公开，这轮数据岗面试更适合讲过滤、data mix、合成验证，以及怎么把评测失败转成下一轮训练数据。Why Apple 则是说明我为什么愿意在不能用用户私有日志训基础模型的条件下，从评测和产品问题里找改进方向。

「我喜欢生态」「苹果重视隐私」太泛了，guideline 希望你理解这支团队在基础模型开发里负责什么，所以我会把公开报告接到自己的工作上。2025 更新把 pre-training 拆成了几段。第一段最吃算力，server 从零训了约 13.4T 文本 token；on-device 先训 dense 模型，sparse-upcycle 出 teacher，再做 distillation。能力扩张写在后面的 continued pre-training 里：提高数学、代码和 multilingual 的权重，multilingual 从 8% 提到 30%，加入验证过的 synthetic data，做视觉适配，扩到 65K long context。post-training 进一步增加 synthetic data，tool calls 单独迭代，RL 在异步平台上把 reward model 和 rule-based reward 一起用。

这正好对上 scale-only 和 data-centric 的区别。Scale-only 的想法是再加 token 和参数，平均 loss 就会降。Data-centric 关心的是同样的算力下哪些 token 值得留、哪些任务要验证过的 synthetic data、哪些评测失败该转成下一轮训练数据。AFM 自己写过，过严的启发式规则会丢掉高价值 token，所以他们减弱规则、多用模型过滤，这正是数据团队能改善的环节。

约束这边，三家都在做基础模型，Apple 公开的几条会直接影响这个岗位怎么选数据。来源上是许可数据、公开数据集、Applebot 抓的页面（尊重 robots.txt，不爬登录墙和付费墙），再加 synthetic data，用户私有数据和交互默认不训基础模型。部署上，on-device 约 3B 的模型不是开放世界的 chatbot，难的推理走 PCC，数据要同时照顾留在本地的简短、隐私敏感任务，和只上传所需部分的困难任务。改进上，全球模型靠许可、爬取和 synthetic data，「我的摘要口吻」这种需求走 on-device adapter 或 few-shot，不把用户邮箱内容当 SFT 数据。会清洗 Common Crawl 只是基本功，要讲的是在这些条件下怎么改善数据，隐私怎么落地见 `dt-privacy-feedback`。

开口大概这样：「我过去一年的工作是把评测缺口写成可训练数据。读完 AFM 2025，我看到你们已经把 core pre-training 和压缩讲清楚了，能力扩张大量写在 continued pre-training、验证合成和 tool-use trajectories 标注上。我想加入的是这一段：在不用用户私有数据训基础模型的约束下，把数学、tool calls 和 multimodal 任务里的失败转成下一轮训练数据。Why now 是因为公开配方已经从堆规模转到管数据；Why Apple 是因为这条约束我认，而且我有过在类似治理下做合成和回灌的经验。」最后一句换成〔填：你自己做过的事〕。没有「类似治理」的经历，就如实说做过 data quality checks、许可或 PII 过滤，别假装做过 differential privacy 生产系统。

## 追问

**为什么不去 OpenAI 或 Google？**
给一个和约束有关的理由，比如 on-device / server 切分、不用用户日志训 FM、按 locale 做 human evaluation，别贬低别家。

**data-centric 是不是反对 scaling？**
两者并存。core pre-training 照样需要规模，data-centric 关心的是新增 token 从哪来、质量怎么验证，AFM 两方面都写了。

**Applebot 有 opt-out，那公开网页是不是就能训？**
还要过 robots 检查，再过滤 PII、脏话和低质内容，回答时把这些抓取和使用条件讲清楚。

**能说「你们算力最大」或者「苹果要超 OpenAI」吗？**
别说。内部编制、未公开的参数量、「苹果要超 OpenAI」都没有公开依据，也证明不了你适合这份工作。
