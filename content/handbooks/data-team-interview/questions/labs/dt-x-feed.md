---
id: dt-x-feed
section: labs
order: 14
level: A
title: xAI：从 X 时间线灌进 Grok 的 data pipeline 怎么设计？
quick: >-
  按时间分区的流式 pipeline 来设计：摄入时删帖用墓碑记录，过滤做语言识别并去掉广告、机器人和刷屏，转发按 URL deduplication
  并保留引用计数，时效源放进 mid-training 或 annealing 阶段。来源要先过许可，公开帖子不等于能进基础模型，大规模汇聚
  personally identifiable information (PII) 的时间线要排除。实时数据值不值，用训练截止后的事件问答来证明。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: xAI Interview Questions and Hiring Process (2026)
    url: 'https://www.techinterview.org/companies/xai/'
    type: secondary
  - title: Applebot model training and individual privacy rights
    url: 'https://support.apple.com/en-us/120320'
    type: primary
  - title: Datasets used for Apple Intelligence
    url: 'https://www.apple.com/legal/ai-regulations/training-data/'
    type: primary
---

按时间分区的流式 pipeline 来设计，分摄入、过滤、deduplication、data mix 四步，每一步都要处理社交数据特有的删帖、转发和机器人。来源要先确认许可，公开帖子不等于能进基础模型；拿不到平台数据时，时效性用许可新闻和公开快照窗来补。

最能说明社交数据特殊的是转发。同一条新闻被转发一万次，文档级 MinHash 会把它当重复削成一条，事件有多热这个信号就没了。所以按 URL deduplication 转链，正文近重只留一条，附上引用计数。快照窗内做近重，窗与窗之间只去 boilerplate 和评测指纹，见 `dt-global-dedup`。

其余几步也围着社交数据的特点来。摄入按时间分区，删除和编辑都要留下记录，重建时才能排除旧版本，见 `dt-exact-dedup-code`；删帖用墓碑记录（按 URL 或帖子 id），下一次重建 mix 时拿掉。过滤做语言识别，去掉广告模板、机器人农场、短刷屏和外链农场。data mix 上，时效源放进 mid-training 或 annealing 阶段，不在 core 里按原始体积灌，见 `dt-llama-anneal`。

许可这一层绕不过去。xAI 的数据和 pre-training 面会问怎么清洗海量文本训练 Grok、怎么接入 X 平台内容，公开招聘叙事也把 X 当成独特的数据来源，但能用多少取决于许可。这和 `dt-userlog-contrast` 是同一个道理，只是来源从对话日志换成了社交时间线。

## 追问

**公开帖算不算「公开网页」？**
不能直接这么算。账号公开不代表可以把整条时间线大规模汇聚进 training set，仍按许可和 personally identifiable information (PII) 的定义处理。作为公开说明的对照，Applebot 支持页写的是只抓公开网页、遵守 robots、不爬登录墙和付费墙，并避开大规模汇聚 personally identifiable information (PII) 的站点。

**删帖为什么不用 Bloom 过滤器记？**
Bloom 过滤器做不到删除，所以用墓碑记录，下一次重建 mix 时把对应的帖子拿掉。

**社交数据能直接用网页的质量分类器吗？**
不能。社交域的质量头和网页教育分类器不是同一个，见 `dt-quality-clf-synth`。

**怎么证明实时数据有用？**
用按时间切的评测，训练截止之后的事件问答。旧百科上涨点，证明不了这类数据值这个价。
