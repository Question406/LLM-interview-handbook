---
id: dt-x-feed
section: labs
order: 14
level: A
title: xAI：从 X 时间线灌进 Grok 的数据管线怎么设计？
quick: "按时间分区的流式管线来设计：摄入时删帖用墓碑记录，过滤做语言识别并去掉广告、机器人和刷屏，转发按 URL 去重并保留引用计数，时效源放进 mid-training 或退火阶段。数据来源要先过许可：公开帖子不等于能进基础模型，大规模汇聚个人信息的时间线要排除。实时数据值不值，用训练截止后的事件问答来证明。"
companies:
  - apple
tags:
  - xAI
  - Data Pipeline
  - Privacy
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: xAI Interview Questions and Hiring Process (2026)
    url: https://www.techinterview.org/companies/xai/
    type: secondary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

按时间分区的流式管线来设计，分摄入、过滤、去重、配比四步，每步都要处理社交数据特有的删帖、转发和机器人。数据来源要先确认许可：公开帖子不等于能进基础模型。拿不到平台数据时，时效性用许可新闻和公开快照窗来补。

## 来源先过许可

xAI 的数据和预训练面会问怎么清洗海量文本训练 Grok，以及怎么接入 X 平台内容；公开招聘叙事也把 X 当成独特的数据来源。能用多少取决于许可。作为公开口径的对照，Applebot 支持页写的是只抓公开网页、遵守 robots、不爬登录墙和付费墙，并避开大规模汇聚个人信息的站点。账号公开不等于可以把整条时间线汇聚进训练集。

这和 `dt-userlog-contrast` 是同一个道理，只是来源从对话日志换成了社交时间线。

## 管线怎么搭

1. 摄入：按时间分区。删除和编辑都要留下记录，重建时才能排除旧版本，见 `dt-exact-dedup-code`。删帖用墓碑记录（按 URL 或帖子 id），下一次重建 mix 时拿掉；Bloom 过滤器做不到删除。
2. 过滤：语言识别，去掉广告模板、机器人农场、短刷屏和外链农场。社交域的质量头和网页教育分类器不是同一个，见 `dt-quality-clf-synth`。
3. 去重：同一条新闻被转发一万次，文档级 MinHash 会把事件信号削掉。做法是按 URL 去重转链，正文近重只留一条并附引用计数。快照窗内做近重，窗与窗之间只去 boilerplate 和评测指纹，见 `dt-global-dedup`。
4. 配比：时效源放进 mid-training 或退火阶段，不要在 core 里按原始体积灌，见 `dt-llama-anneal`。

## 追问

- **公开帖算不算「公开网页」？** 不能直接这么算。账号公开不代表可以大规模汇聚，仍按许可和个人信息的口径处理。
- **怎么证明实时数据有用？** 用按时间切的评测：训练截止之后的事件问答。旧百科上涨点证明不了这类数据值这个价。
