---
id: dt-inspect-corpus
section: good-data
order: 5
level: A
title: 还没过滤之前，怎么知道语料里到底有什么？
quick: "先对全库做计数和检索，再抽查样本。统计语言、长度、重复率、评测重叠、PII、密钥和抽取错误，才知道该过滤什么。WIMBD 用这种方法检查大规模语料；Datasheets 则把来源、用途、偏差和处理版本记录下来，方便后续复盘。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "What's In My Big Data?"
    url: https://arxiv.org/abs/2310.20707
    type: primary
  - title: Datasheets for Datasets
    url: https://arxiv.org/abs/1803.09010
    type: primary
  - title: Documenting Large Webtext Corpora (C4)
    url: https://arxiv.org/abs/2104.08758
    type: primary
---

先对全库做计数和检索，再抽查样本。既要能统计整体分布，也要能检索某一类内容。很多问题只有在全库尺度上才看得见，靠几个随机样本发现不了。

WIMBD（Elazar 等）对十个常用预训练集做了大规模计数和检索，发现 RedPajama 和 LAION-2B-en 中约一半文档是重复的；公开数据集里还有 PII、合成文本的风格，以及与 Winograd / GLUE 等评测内容的重叠。Dodge 等更早分析过 C4 的块名单和来源偏差。如果只抽查 100 条、没有检索能力，全库里反复出现的版权文案就很容易漏掉。这些数字属于对应的公开数据集；WIMBD 更值得借鉴的是方法：对 10B 文档检索某类内容、统计它出现的频率。

## 训练前要统计什么

至少统计文档数、token 数、语言分布、长度分组、精确和近重复率、评测 n-gram 命中率、PII 和密钥命中率，以及抽取结果为空的比例。实现见 `dt-countmin-code`、`dt-ngram-contam-code`、`dt-pii-luhn-code`、`dt-lid-code`。

除了这些数字，还要记下数据本身的背景。Datasheets for Datasets（Gebru 等）补的是另一类信息：谁收集的、为什么收集、可能影响谁、有哪些缺口。工程上可以写成 dataset card，记录来源、opt-out、过滤器 git 版本和已知偏差。Model card 记录的是模型，做数据工作要先把数据卡写清楚。

## 发现问题后怎么处理

- 重复内容做去重，见 `dt-lsh-cluster-code`。
- 合成文本占比很高时，检查是不是自己的教师输出混进了预训练。
- PII 和密钥进入隔离区（quarantine），见 `dt-secret-scan-code`。
- 有评测重叠时，隔离训练文档，保留评测题。
- 毒性要结合用途处理：预训练先做明确的硬性检查，需要判断语境的问题交给安全后训练，避免把整个语言的内容删掉，见 `dt-c4-side-effect`。

## 追问

- 内部语料能像 WIMBD 一样出报告吗？可以做同类分析，面试中按披露限制只讲数量级和相对变化。
- 计数用什么方法？对大量稀有 gram 做精确计数很贵。高频模板可以用 Count-Min，文档级重复可以用哈希排序。
- 找到一条问题样本，就说明全库有问题吗？要看频率和来源分组。文档网站里的一条测试卡号，和十万封含真实邮箱的内容，需要不同的处理。
