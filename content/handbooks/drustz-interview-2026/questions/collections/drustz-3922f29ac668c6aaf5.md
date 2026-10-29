---
id: drustz-3922f29ac668c6aaf5
section: collections
order: 43
level: A
title: OpenAI 题库（爬取全量） · ML System Design
quick: 作者文档章节 · OpenAI 题库（爬取全量） · ML System Design
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/openai.md
    type: primary
---
## ML System Design

### ML 轮新考法（2026）：噪声标注/数据质量题族（filter bad annotations、multi-annotator labels）——直接对口 post-training 数据工作
*hard · 频率: 3+ variants collected (2026) · 2026-05*

PracHub 收录三道 OpenAI MLE 变体：(1) 'Filter Bad Human Annotations'（medium）：大规模人工标注训练集中有低质/不一致标注，设计方法过滤；(2) 'Improve Training With Noisy Annotators'（hard）：Pandas DataFrame，含 feature 列和 observed label，提升训练效果；(3) 'Improve classifier with noisy multi-annotator labels'（hard）：二分类文本数据，每条样本有多个标注员的标注，如何建模/聚合/加权提升 classifier。另有 'Mine Novel Images from Unlabeled Data'（从海量无标注图库挖掘新颖图像的 ML 系统）和 'Design a RAG system with evaluation'（含评测设计的 RAG 系统）。这批题是 2026 年 Applied/Research ML 轮相对新的方向，考数据为中心的 ML 工程判断。

**解法**: 标准工具箱：annotator agreement（Cohen/Fleiss kappa）、Dawid-Skene/GLAD 类标注员能力建模、confident learning（cleanlab 思路：用模型置信度找错标）、loss-based 过滤/reweighting、soft label 聚合 vs majority vote、留出金标集calibration标注员、主动重标预算分配。答题时结合自己 post-training 数据管线经验讲 tradeoff（我的推断+经验性解法）。

来源: &lt;[来源链接](https://prachub.com/interview-questions/improve-classifier-with-noisy-multi-annotator-labels&gt;)

### OpenAI-style AI-infra design questions (DesignGurus compilation)
*hard · 频率: unknown (prep-site compilation, not first-person reports) · 2025*

(1) 'Design a large-scale AI model deployment system — e.g., how would you serve a model like GPT-4 to millions of users concurrently?' (model serving architecture, LB + GPU model servers, autoscaling, model loading/versioning, low-latency handling). (2) 'Design a real-time chatbot API for AI-driven conversations' (REST vs WebSocket, conversation context/state management, strict latency targets, safety filters, rate limiting). (3) 'Design a distributed training system for deep learning models' (data vs model parallelism, job scheduling, cluster management, parameter server vs all-reduce, failure handling/checkpointing, GPU/TPU monitoring). (4) 'Design a scalable data pipeline for machine learning applications' (Kafka/PubSub ingestion, Spark/Flink processing, storage, data quality).

来源: &lt;[来源链接](https://www.designgurus.io/blog/openai-system-design-interview-questions&gt;)

### ML 系统设计题池：RAG 检索/企业 ChatGPT/从未标注语料挖掘新数据（MLE/RE 轨）
*hard · 频率: low（各 1-2 帖） · 2025-11 ~ 2026-05-26*

官方题库三条：(1) rag-search-ml-design，low，2 帖，60min onsite SD，roles RE/MLE，2026-01-01 ~ 2026-03-22；(2) chatgpt-enterprise-rag，single，60min，MLE/RE，2025-11-01 ~ 2026-03-22；(3) mining-novel-data-unlabeled-corpus，single，MLE onsite SD，2025-11-18 ~ 2026-05-26（tags: mlsd/data-mining）——external 库 'Mining Novel Data from Large Unlabeled Corpus'（tid 7100044）。佐证：thread-1178049（2026-05-26 MLE 过经）回复区：『好像有一阵子 ML SD 没了，现在加回来了吗』——ML SD 轮 2026 春季一度取消后恢复。对 mid-training 数据管线背景候选人，(3) 几乎是本命题。

**解法**: （我的推断）mining novel data：去重（MinHash/embedding 聚类）→质量打分（分类器/perplexity过滤）→新颖性度量（与已训语料的 embedding 距离/n-gram 覆盖）→人审sampling闭环→数据配比实验；RAG：chunking/混合检索（BM25+向量）/rerank/引用与权限隔离/评测（faithfulness）。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/company/openai&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
