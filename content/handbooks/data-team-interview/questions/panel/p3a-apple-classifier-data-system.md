---
id: p3a-apple-classifier-data-system
section: panel
order: 72
level: S
title: 一亩三分地 Apple MLE：从简单分类器讲到完整数据系统
quick: >-
  先定义标签与误判代价，建立简单分类器，再把标注、分组切分、阈值、部署与反馈串起来。系统质量取决于标签是否稳定、输入是否一致和错误是否被监测，不是只看模型复杂度。
companies:
  - apple
tags:
  - AFM 专项 2026-10
  - Apple
  - 一亩三分地原帖核对
  - Siri
  - ML System Design
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: 非ML专业人士的果子家MLE 虚拟昂赛（2021）
    url: 'https://www.1point3acres.com/bbs/thread-789348-1-1.html'
    type: interview
  - title: 果子MLE店面（2026）
    url: 'https://www.1point3acres.com/bbs/thread-1165265-1-1.html'
    type: interview
  - title: Google ML Crash Course — Classification metrics
    url: >-
      https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
    type: primary
  - title: scikit-learn — Common pitfalls and recommended practices
    url: 'https://scikit-learn.org/stable/common_pitfalls.html'
    type: primary
---

## 题目描述

**原帖核对范围：**2026-10-26 通过 Chrome 查看两帖主帖及评论。2021-08-17 的 Apple MLE onsite 报告明确提到“基于简单分类模型构建 ML 系统”；作者后续评论表示所属 Siri 团队。2026-02-15 11:42:04 的技术电面报告描述：给应用场景，讨论数据类型与挑战，设计从预处理到模型选择和训练方法的系统；作者当日回复是 Siri。两帖均未披露实际业务、数据集或模型细节，不能推断为 AFM 原题。

**手册扩展练习：**设计一个筛选公开训练文档的二分类系统，标签为“适合保留”与“需要进一步审核”。每天新增 100 万篇文档，人工每天只能审核 2,000 篇。要求减少人工负担，同时避免大量误丢 low-resource 语言和少见但有价值的内容。规模、标签与约束均为练习约定。

请说明数据定义、标注、切分、模型 baseline、阈值策略、评测、部署及持续改进。不要直接回答“调用一个 LLM 打分”。

## 可以这样回答

先承认“适合保留”不是天然客观标签。把标签拆成可核验的维度，例如正文抽取是否完整、是否重复、是否具备可理解内容，再说明授权与来源约束单独检查，不能用高质量分覆盖来源限制。

先让 annotator 对同一小批文档独立评分，讨论分歧和 edge cases，再形成版本化规则。low-resource 语言需要合适语言能力的审核人员，不能只因通用模型分数低就标成坏样本。

## 技术备查

## 解题思路与参考答案

先承认“适合保留”不是天然客观标签。把标签拆成可核验的维度，例如正文抽取是否完整、是否重复、是否具备可理解内容，再说明授权与来源约束单独检查，不能用高质量分覆盖来源限制。

### 标签与简单模型

先让 annotator 对同一小批文档独立评分，讨论分歧和 edge cases，再形成版本化规则。low-resource 语言需要合适语言能力的审核人员，不能只因通用模型分数低就标成坏样本。

baseline 可用可解释的长度、重复度、语言与文本特征配合逻辑回归或小型分类器。只在 training set 拟合 vocabulary、standardization 等预处理，再把同一流程用于开发、测试与生产；先用简单模型判断数据和标签是否有有效信号，再比较更强模型的增益与成本。

### 数据切分和评估

同源站点、near-duplicates cluster 与同一文档修订版不能随机分到不同集合。按来源与时间留出评测，分别测已知来源与新来源，避免模型只是记住“这个域名一般好”。留一批人工审计样本估计误丢率，审核队列里的标签不能代表整个流量。

单一 accuracy 不适合决定上线。假设 95% 文档都可保留，“全部保留”就有 95% 准确率，却没有节省多少审核资源。需要报告误丢有效文档的比例、审核队列精度、每千篇审核收益，以及语言、长度与来源 evaluation slices。

### 阈值、预算与反馈

设置直接保留、人工审核和明确拒收的决策区域，但阈值必须以误判代价和审核能力为依据。本题只有每日 2,000 条审核预算，不能承诺所有不确定样本都被审核；在队列中结合不确定性、分布变化和来源覆盖分配预算，并为直接保留与拒收区域保留随机审计额度。

新标签会受之前的筛选策略影响，必须记录 sampling 概率或审核选择规则，评估时避免把被选择的 hard examples 当成全量分布。定期检查被拒收区域，发现系统性误丢时修规则、阈值或覆盖，再从冻结 baseline 做数据干预对照。

## 面试追问

**为什么不一开始就上 large model？** 可能值得，但先验证标签、切分和指标。复杂模型不会自动修复标注标准冲突与训练测试 leakage，还会增加 inference cost 和 calibration 负担。

**审核准确率越来越高是不是好事？** 可能只是队列越来越集中于容易判断的样本。必须固定审计分布并检查覆盖，否则只提高了被选中人群的指标。

**训练和生产输入不同怎么办？** 固定解析器、特征提取与分词版本，监测缺失率和分布变化。先复现差异，再判断是 pipeline 缺陷还是需要新的训练数据。

**这题与 AFM 的联系是什么？** 可练习数据过滤器的完整生命周期；这只是把历史 Apple MLE 设计主题迁移到数据岗，不能声称原面试要求设计训练 corpus 过滤器。
