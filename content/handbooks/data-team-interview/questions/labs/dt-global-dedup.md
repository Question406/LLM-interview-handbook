---
id: dt-global-dedup
section: labs
order: 4
level: S
title: FineWeb：跨所有 crawl 快照做全局 MinHash，为什么可能更差？
quick: "全局近重复去重不一定更好。跨快照反复出现的优质网页被只留一份后，一次性低质页面可能占更大比例。网页可先在快照内去近重复，跨快照重点处理页脚、导航和评测指纹；具体范围用小模型下游对照确定。"
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

网页批量数据可以先按快照做近重复去重，URL 精确重复留最新或一份。跨快照优先去掉明显模板内容（boilerplate）和评测指纹，是否对所有优质网页做全局近重，要由下游对照决定。重复 token 变少，不等于模型分数一定提高。

Lee et al. 2021 说明复制内容有害，但不意味着跨年抓取的数据总应做一次全局 MinHash。FineWeb 的多快照消融发现，跨快照去重可能伤害下游；公开解释是反复出现的内容往往是被引用的优质页面。它们被只保留一次后，一次性低质页面的相对比例反而增加。

许可书籍和有标准答案的数学数据，可以精确保留一份，不能直接套用网页保留跨快照重复的策略。

## 持续抓取怎么划分

Applebot 持续抓取时，可以按时间窗分片：窗内做近重，窗间针对模板和评测指纹检查。实现仍可用 `dt-minhash-code`，差别是 LSH 的分片键是否包含 `snapshot_id`，或全部进入一个全局桶。

这与 AFM 减弱过强启发式的考虑类似：筛选也可能删掉有用 token。合理的 paraphrase 应保留，阈值按数据域验证。

## 追问

- 与行级去重冲突吗？不冲突。行级去重处理多个文档复制的页脚、导航，见 `dt-llama-extract`；文档级全局近重则可能删除整页。
- 没有快照怎么办？以时间窗作为分片单位，再验证窗间去重范围。
- 怎样保留多样性？不要默认删掉正当改写，按域调阈值，见 `dt-minhash-code`。
