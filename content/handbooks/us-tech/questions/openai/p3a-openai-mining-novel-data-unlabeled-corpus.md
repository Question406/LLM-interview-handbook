---
id: p3a-openai-mining-novel-data-unlabeled-corpus
section: openai
order: 636
level: A
title: "OpenAI：未标注语料挖掘：新信息与目标图像"
quick: "先约定新颖性的参照集，再做内容去重、表征索引、对象召回和质量重排，最后用人工抽样校准。embedding 距离远只说明表征不同，不能直接证明包含新事实。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · mining-novel-data-unlabeled-corpus"
    url: https://www.1point3acres.com/interview/problems/company/openai/mining-novel-data-unlabeled-corpus
    type: secondary
---

## 题目

从海量未标注数据里挖掘"独特"的信息，并找出包含指定对象的图片。题卡没有公开详细规格。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖，原题详细规格未公开；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

先定义「新颖」相对什么，再设计筛选流程：参照已有训练集、语义簇或事实库，方案会不同。下面练习固定为相对训练集新颖且含指定对象，流程是手册设计的方案，原题没有公开详细规格。

练习假设每天处理一千万条图片和文本，人工每天审一千条。先确认参照集和来源许可，依次做内容去重、embedding 索引、对象召回、去冗余与质量重排、人工抽样，再写入带版本的入选集。来源许可和隐私过滤贯穿全过程。

sample 记录 source、hash、`embedding_version`、cluster、`object_scores`、`novelty_score`、`selection_reason` 和 review 状态。这里把新颖性定义为到已知集合最近邻的距离，它衡量表征差异，不能证明出现新事实。

比如新爬到一张街景图，hash 没有重复，就用当前 `embedding_version` 编码，到训练集索引查最近邻，距离超阈值得到较高的 `novelty_score`。对象检测器的「自行车」分数达标后进入候选；同簇相似图已经很多时，重排就降权。入选时记录 `selection_reason`，并抽一部分给人工确认。

embedding 升级或模型分数漂移后，要建新版本索引，不同表征空间的距离不能直接比较。人工发现误报时，沿 `selection_reason` 回溯步骤，保留原分数和可追踪记录。用留出数据校准距离阈值，避免只挑到离群坏图；报告候选召回率、人审精确率、每千条新增覆盖簇数、重复率和单条成本。

## 追问

**怎样确认是真正的新知识？**
需要证据检索和验证。语义上没见过与事实上是新的需要分别判断，距离远只能支持前者。

**每天一千条人审怎么分配？**
按簇分层抽样，覆盖新簇，别只看最高分。审核结果用于校准阈值和检测器，并估计整批精确率。
