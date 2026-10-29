---
id: dt-inspect-corpus
section: good-data
order: 5
level: A
title: 还没过滤之前，怎么知道 corpus 里到底有什么？
quick: >-
  先对全库做计数和检索，再 sampling 看。统计语言、长度、重复率、评测重叠、PII、密钥和抽取错误，才知道该滤什么。WIMBD 就是这样检查大规模
  corpus 的；Datasheets 把来源、用途、偏差和处理版本记下来，方便以后复盘。
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: What's In My Big Data?
    url: 'https://arxiv.org/abs/2310.20707'
    type: primary
  - title: Datasheets for Datasets
    url: 'https://arxiv.org/abs/1803.09010'
    type: primary
  - title: Documenting Large Webtext Corpora (C4)
    url: 'https://arxiv.org/abs/2104.08758'
    type: primary
---

先对全库做计数和检索，再 sampling 看。既要能统计整体分布，也要能把某一类内容检索出来，很多问题只有放到全库尺度上才看得见，几个随机样本发现不了。

比如全库里反复出现的一段版权文案，你只抽查 100 条、又没有检索能力，很容易就漏过去了。WIMBD（Elazar 等）对十个常用 pre-training 集做了大规模计数和检索，发现 RedPajama 和 LAION-2B-en 里大约一半文档是重复的，公开数据集里还有 PII、合成文本的风格，以及和 Winograd / GLUE 等评测内容的重叠。Dodge 等更早分析过 C4 的块名单和 source bias。这些数字属于对应的公开数据集，WIMBD 更值得借的是方法：对 10B 文档检索某类内容，统计它出现多少次。

## 训练前统计什么

我至少会统计文档数、token 数、语言分布、长度分组、精确和 near-duplicates 率、评测 n-gram 命中率、PII 和密钥命中率，以及抽取结果为空的比例。实现见 `dt-countmin-code`、`dt-ngram-contam-code`、`dt-pii-luhn-code`、`dt-lid-code`。

数字之外，还要记下数据本身的背景。Datasheets for Datasets（Gebru 等）补的是另一类信息：谁收集的、为什么收、可能影响谁、有哪些缺口。工程上可以写成 dataset card，记来源、opt-out、过滤器 git 版本和已知偏差。Model card 记的是模型，做数据工作要先把数据卡写清楚。

统计出问题后，按类型处理。重复内容 deduplication，见 `dt-lsh-cluster-code`；合成文本占比很高时，查一下是不是自己的 teacher 输出混进了 pre-training；PII 和密钥进隔离区（quarantine），见 `dt-secret-scan-code`；有评测重叠时，隔离训练文档，保留评测题。毒性要结合用途处理，pre-training 先做明确的硬性检查，要看语境的问题交给安全 post-training，免得把整个语言的内容删掉，见 `dt-c4-side-effect`。

## 追问

**内部 corpus 能像 WIMBD 一样出报告吗？**
可以做同类分析。面试里按披露限制，只讲数量级和相对变化。

**计数用什么方法？**
对大量稀有 gram 做精确计数很贵。高频模板可以用 Count-Min，文档级重复可以用哈希排序。

**找到一条问题样本，就说明全库有问题吗？**
要看频率和来源分组。文档网站里的一条测试卡号，和十万封含真实邮箱的内容，处理方式不一样。

**抽查和全库统计，哪个先做？**
先做全库计数和检索，知道问题大概在哪、有多少，再针对那些分组 sampling 细看。
