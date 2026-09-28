---
id: byte-train-data-pipeline
section: data
order: 200
level: A
title: 字节大模型算法：如何搭建训练数据构造 Pipeline？
quick: >-
  按任务定义 schema，再多源采集，去污 / 去重 / 难度分层，自动 verifier 加人工抽检，train/dev/test 泄漏隔离，最后版本化与回流。场景题要讲清质量门禁和失败样本闭环，别只列爬虫步骤。
tags:
  - ByteDance
  - Data Pipeline
  - 2026 Campus
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 26届秋招｜字节大模型算法岗面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/029a292419294b4a8227acde5a00124b
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 届别：26 届秋招；一面场景题
- 原始措辞：**“如何搭建训练数据构造 Pipeline”**

错法：爬虫清单。评委要听质量门禁、泄漏隔离、失败闭环：每一步有可观测指标，坏 case 能回到标注队列。没有标准答案时，不要假装有 oracle。讲偏好对、过程检查点或多模型投票，并报告 judge 与人工一致性。

## 七段流水线，每段给指标

1. **需求与 schema**：prompt / 标签 / 工具轨迹字段、许可与安全级别。缺字段的样本不能入库。
2. **采集**：公开题库、合成、业务日志、人工标注；记录来源与授权。来源级配额，避免单一站占满。
3. **清洗**：语言、PII、毒性、模板重复；近重复用 hash + embedding（见 `data-minhash`、`data-semantic-dedup`）。
4. **质量门**：规则 verifier → 模型 judge → 分层人工抽检；按通过率与一致性设阈，不过门不进 train。
5. **分层配比**：难度、领域、长度、正负比；为 RL 另留可验证子集。
6. **泄漏防护**：按题面 / 答案指纹切分 train/dev/test；线上回流单独命名空间，防评测污染（`data-contamination`）。
7. **版本与实验**：`dataset_version → train_run → eval` 可追溯；坏 case 自动入队再标。

对照：只加爬取量 vs 加门禁，应报告 holdout 增益和污染重叠率。条数涨、重叠升，是失败实验。

## 无标准答案时的构造

构造成对偏好、过程检查点、或多模型一致性投票；报告 judge 与 human 一致率和切片。Judge 只当过滤器，抽检校准（`data-reward-calibration`）。合成数据要查自污染（`data-synthetic-self-contamination`）。

## 追问

- **没有标准答案怎么办？** 偏好对 + 过程点 + 人评校准，不编造 oracle。
- **如何证明没泄漏？** 指纹重叠表 + 时间切分 + 回流命名空间。说「随机切」不够。
- **Pipeline 和「数据越多越好」差在哪？** 每步有拒绝率和边际增益；过门才计数。见 `data-sft-pipeline` 的 taxonomy 思路。
