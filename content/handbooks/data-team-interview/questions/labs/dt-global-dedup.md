---
id: dt-global-dedup
section: labs
order: 4
level: S
title: FineWeb：跨所有 crawl 快照做全局 MinHash，为什么可能更差？
quick: >-
  因为跨快照反复出现的往往是优质网页，全局 near-duplicate deduplication
  把它们只留一份，一次性出现的低质页面比例就上去了。网页先在快照内去 near-duplicates，跨快照重点处理页脚、导航和评测指纹，范围用 small
  model 的下游对照来定。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
---

global deduplication 删掉的不全是垃圾。跨快照反复出现的内容，往往是被反复引用的优质页面；把它们只留一份，一次性出现的低质页面在剩下的数据里占比就上去了。重复 token 变少了，模型分数不一定跟着涨。

举个例子，一篇写得很好的 Python 入门教程，被十几个快照都抓到了；一个自动生成的垃圾商品页只出现过一次。global deduplication 之后两者各剩一份，教程原本靠重复得到的权重就没了。

FineWeb 的多快照 ablation study 就发现，跨快照 deduplication 可能伤害下游，公开的解释就是这一条。Lee et al. 2021 说明复制内容有害，可跨年抓取的数据要不要做一次全局 MinHash，还是要看下游对照。

我的做法是在快照内按快照去 near-duplicates，URL 精确重复的留最新一份。跨快照只优先去掉明显的模板内容（boilerplate）和评测指纹，要不要对所有优质网页做全局 near-duplicates，交给 small model 的下游对照来定。

实现上还是可以用 `dt-minhash-code`，区别只在 LSH 的分片键里带不带 `snapshot_id`，还是全部进一个全局桶。

## 追问

**持续抓取没有天然的快照，怎么办？**
按时间窗分片：窗内去 near-duplicates，窗间针对模板和评测指纹检查，再验证窗间 deduplication 的范围。道理和减弱过强的启发式规则一样，筛选本身也可能删掉有用的 token，AFM 2025 报告也减弱过过强的规则。

**书籍、数学这些非网页数据也这样 deduplication 吗？**
另算。许可书籍和有标准答案的数学数据可以精确保留一份，不套用网页那套保留跨快照重复的策略。

**改写过的内容算重复吗？**
合理的 paraphrase 不该被删，阈值按数据域验证。

**和行级 deduplication 冲突吗？**
不冲突。行级 deduplication 处理多个文档共用的页脚、导航，见 `dt-llama-extract`；文档级的全局 near-duplicate deduplication 可能删掉整页。
