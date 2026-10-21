---
id: dt-global-dedup
section: labs
order: 4
level: S
title: FineWeb：跨所有 crawl 快照做全局 MinHash，为什么可能更差？
quick: "因为跨快照反复出现的往往是优质网页，全局近重复去重把它们只留一份后，一次性低质页面的比例会上升。网页可先在快照内去近重复，跨快照重点处理页脚、导航和评测指纹；具体范围用小模型下游对照确定。"
companies:
  - apple
tags:
  - FineWeb
  - Dedup
  - Pre-training
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
---

全局去重删掉的不全是垃圾。跨快照反复出现的内容，往往是被反复引用的优质页面；把它们只保留一份后，一次性出现的低质页面在剩余数据里的比例就上升了。重复 token 变少，不等于模型分数一定提高。

## 证据

FineWeb 的多快照消融发现，跨快照去重可能伤害下游，公开的解释就是上面这条。Lee et al. 2021 说明复制内容有害；跨年抓取的数据要不要做一次全局 MinHash，仍要看下游对照。

## 怎么划分去重范围

1. **快照内**：按快照做近重复去重，URL 精确重复的留最新的一份。
2. **跨快照**：优先去掉明显的模板内容（boilerplate）和评测指纹。是否对所有优质网页做全局近重复，由小模型的下游对照决定。
3. **非网页数据另算**：许可书籍和有标准答案的数学数据，可以精确保留一份，不能直接套用网页保留跨快照重复的策略。
4. **保留正当改写**：合理的 paraphrase 不该被删，阈值按数据域验证。

实现上仍可以用 `dt-minhash-code`，区别只在 LSH 的分片键是否包含 `snapshot_id`，还是全部进入一个全局桶。

## 持续抓取时

持续抓取的数据没有天然的快照。可以按时间窗分片：窗内做近重复去重，窗间针对模板和评测指纹检查，再验证窗间的去重范围。道理和减弱过强的启发式规则一样，筛选本身也可能删掉有用的 token，AFM 2025 报告也减弱过过强的规则。

## 追问

- **和行级去重冲突吗？** 不冲突。行级去重处理多个文档共用的页脚、导航，见 `dt-llama-extract`；文档级的全局近重复去重则可能删掉整页。
