---
id: dt-x-feed
section: labs
order: 14
level: A
title: xAI：设计从 X 时间线灌进 Grok 的数据管线，Apple 怎么改口？
quick: "保留流式摄入、语言识别、广告和机器人过滤、去重、安全检查与时间分区的流程，把输入换成 Applebot 公开页和许可集。苹果场景不能默认使用用户时间线；时效性可以用许可新闻和公开快照补充。"
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

保留摄入和过滤流程，输入换成 Applebot 抓取的公开页、新许可数据和验证过的合成数据。不能默认拥有 X 式的用户实时动态数据。时效性用许可新闻 / 公开快照窗补，窗内近重、窗间只打 boilerplate 和评测指纹，见 `dt-global-dedup`。和 `dt-userlog-contrast` 同一句，燃料从对话日志换成了社交时间线，通道照样要换。

不这么选的理由：把「社交火管」原样搬到 AFM，或评价 xAI 该不该这么做。公开招聘叙事把 X 当成独特燃料。公开账号不等于能进基础模型。大规模汇聚个人信息的时间线，苹果口径直接拒。

接到苹果：摄入仍按时间分区，删除和编辑需要留下记录，便于重建时排除旧版本，见 `dt-exact-dedup-code`。过滤：语言、广告模板、机器人农场、短刷屏、外链农场。社交域的质量头和网页教育分类器不是同一个，见 `dt-quality-clf-synth`。近重：同一条新闻被转发一万次，文档级 MinHash 会把事件信号削掉；按 URL 去重转链，正文近重留一条加引用计数。mix：时效源给 mid / 退火，不要在 core 里按原始体积灌，见 `dt-llama-anneal`。

公开锚点：xAI 数据 / 预训练面会问清洗海量文本训 Grok，以及接入 X 平台内容；Applebot 支持页写的是公开网页、robots、不爬登录墙 / 付费墙，并避开大规模汇聚个人信息的站。

## 追问

- **公开帖是不是「公开网页」？** 苹果支持页写的是公开网页、robots、不爬登录墙 / 付费墙，并避开大规模汇聚个人信息的站。社交火管解释不成 Applebot。
- **删帖之后还在 shard 里？** 墓碑按 URL / 帖 id，下一次 mix 重建拿掉。Bloom 做不到删除。
- **实时性怎么证明有用？** 用时间切评测：训练截止之后的事件问答。旧百科涨点证明不了火管值这个价。
