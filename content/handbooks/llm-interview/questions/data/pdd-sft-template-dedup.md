---
id: pdd-sft-template-dedup
section: data
order: 104
level: A
title: 拼多多大模型算法：SFT 数据怎样避免模板化，并做 train / test 去重？
quick: >-
  先按意图、约束、领域、表达方式和答案策略控制采样，不把同一模板的改写当多样性；去重同时做 lexical、semantic 和 split leakage 检查，并人工核验「相似但需要保留」的 hard case。最终看 held-out 业务任务，不只看去重率。
tags:
  - PDD
  - SFT Data
  - Data Deduplication
  - Evaluation Leakage
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多日常实习 大模型算法一面分享（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法
- 届别 / 流程：日常实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-15
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“SFT数据如何更贴近业务：如何避免过度模板化？如何做基础的train/test去重来避免评测失真？”**

一面两问要一起答：模板化是训练信号单一，去重是评测别被同题记住。最廉价的「换个说法」会把同一决策路径抄满，holdout 总分很高只是背题。先按意图、约束、领域、表达方式、答案策略控制采样；去重同时做 lexical、semantic 和 split leakage。最终看新鲜业务 slice，不只看去重率。拼多多业务 SFT 最容易用后台字段填空冒充多样性，评测再从同一批改写里切，分数会虚高到没法上线。

## 贴近业务：覆盖缺口，不是改写工厂

把业务目标拆成 intent、输入约束、上下文、决策路径、输出格式和风险等级，按覆盖缺口主动采样。可用不同作者 / 生成器、反事实扰动和错误修复样本，但必须保留质量判定与血缘。GPT 改写（`minimax-data-quality-gpt`）只能补表达，不能当新意图。模板族要记账：同一 schema 填空超过配额就降权。语义去重（`data-semantic-dedup`）判的是同一 training signal，多解法可留 $k$ 条。

## Train/test 去重，防评测失真

split 前做 exact / normalized match、n-gram / MinHash（`data-minhash`），再对 embedding 邻居或同一 source document 做语义泄漏检查（`data-contamination`）。不能机械删除：高相似但约束、答案或工具 state 不同的样本要人工抽检。报告 cross-split nearest-neighbor、按模板族的 performance 和新鲜业务 slice。评测集构造（`pdd-offline-eval-coverage`）必须时间切分并与 train 出重叠表，否则「贴近业务」的 SFT 会把评测洗进训练。

对照：未去重、只 lexical、lexical+semantic、再加人工 hard case。看 holdout、换模板鲁棒、新 query slice。只去重率升、新鲜 slice 不升，说明你在删多样性或评测仍泄漏。

避免模板化要在采样时就卡配额：每个 intent × 输出 schema 设上限，超额的改写进「表达池」而不是「新样本池」。业务贴近看的是真实日志里的约束和失败修复，不是把后台字段名换成人话重复一百遍。train/test 去重报告给面试官看两张图就够：跨 split 最近邻相似度直方图，以及按模板族的 holdout。某族接近满分、换皮为零，就是泄漏或背模板。一面两问我会这样收：多样性来自决策路径覆盖，评测可信来自跨 split 指纹；去重率只是过程指标。

## 追问

- **改写算多样性吗？** 表达多样可以，决策路径重复不算。按答案策略分族，超配额降权。
- **相似但要留的 hard case 是什么？** 题意近、约束或工具状态不同，需要不同决策。机械删会伤边界。
- **去重率当 KPI 行吗？** 不行。KPI 是新鲜业务 slice 和换模板鲁棒；去重率只是过程量。
- **和 contamination 题怎么分？** 本题强调 SFT split 与业务贴近；contamination 是评测被预训练/语料看见。指纹可以共用。
