---
id: byte-train-data-pipeline
section: data
order: 200
level: A
title: 字节大模型算法：如何搭建训练数据构造 Pipeline？
quick: >-
  按七段搭：定 Schema、多源采集、清洗去重、data quality checks、按难度分层配比、train/dev/test
  泄漏隔离、版本与实验，每段都有可观测的指标，未通过 quality checks 的样本不入库。data quality checks
  用自动验证器加人工抽检，失败样本自动送回标注与修正流程。
tags:
  - ByteDance
  - Data Pipeline
  - 2026 Campus
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 26届秋招｜字节大模型算法岗面经（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/029a292419294b4a8227acde5a00124b'
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 届别：26 届秋招；一面场景题
- 原始措辞：**“如何搭建训练数据构造 Pipeline”**

我会把 Pipeline 讲成七段，每一段都有可观测的指标和拒绝条件，坏 case 能自动回到标注队列。面试官想听的是 data quality checks、泄漏隔离和失败 feedback loop，列一份爬虫清单答不到点上。

## 七段流水线

第一段是需求和字段类型规范（schema）：prompt/ 标签 / 工具轨迹的字段，以及许可和安全级别，缺字段的样本不能入库。第二段采集，来源有公开题库、合成、业务日志、人工标注，记下来源和授权，并按来源设配额，免得单一站点占满。第三段清洗，处理语言、PII、毒性、模板重复，近重复用 hash + embedding（见 `data-minhash`、`data-semantic-dedup`）。

第四段是 data quality checks：规则验证器（verifier）在前，模型 judge 其次，最后分层人工抽检，按通过率和一致性设阈值，未通过 quality checks 的样本不进 train。第五段分层配比，按难度、领域、长度、正负比来配，并给 RL 单独留一个可验证子集。第六段防泄漏，按题面 / 答案指纹切分 train/dev/test，线上收集后重新使用的数据放进单独的命名空间，防止污染评测（`data-contamination`）。第七段是版本和实验，`dataset_version → train_run → eval` 要能追溯，坏 case 自动入队重标。

验证这条流水线有没有用，我会对照「只加爬取量」和「加上 acceptance checks」两种做法，报 holdout 增益和污染重叠率。比如数据量翻了几倍，holdout 没涨，和评测集的重叠率却升了，这就是一次失败的实验，光看条数会以为是进步。

## 没有标准答案时

没有 oracle 就别假装有。可以构造成对偏好、过程检查点，或者多模型一致性投票，报告 judge 和人工的一致率，并分切片看。Judge 只当过滤器，靠抽检来 calibration（`data-reward-calibration`）。合成数据还要查自污染（`data-synthetic-self-contamination`）。

## 追问

**没有标准答案怎么办？**
用偏好对、过程检查点加人评 calibration，不编造 oracle。

**怎么证明没有泄漏？**
拿出指纹重叠表、时间切分和 feedback-data namespace。只说「随机切的」不够。

**这套 Pipeline 和「数据越多越好」差在哪？**
每一步都有拒绝率和边际增益，通过 checks 后才计数。taxonomy 的思路见 `data-sft-pipeline`。
