---
id: drustz-74dc68b5600adb792f
section: openai
order: 43
level: A
title: Rag Search Ml Design
quick: original-structured-preparation-guide · Rag Search Ml Design
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/rag-search-ml-design
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# RAG Search ML Design：训练检索器、混合召回与排序

## 证据边界

公开摘要已明确这是口头 ML Design 轮，面试官常有搜索背景，会深挖 embedding training、contrastive learning、retrieval flow、hybrid retrieval 和 ranking。它与上一题“企业上传私有数据并做 ChatGPT”不同：这里的主角是搜索相关性模型、训练数据和评测，而不是多租户权限产品。锁定正文不可见，因此下面把任务表述为可直接练习的合理版本：给定文档语料、查询日志以及部分相关性标签，设计一个为 RAG 提供候选证据的搜索系统；既要召回精确关键词，也要覆盖语义改写，并在延迟预算内返回排序后的 top-K。开场应确认语言范围、语料规模与更新频率、标签来自人工还是点击、最终目标是文档搜索还是答案质量、是否已有 BM25 baseline。训练方法、K 值和延迟数字均需根据面试官回答调整，不能当作已知会员题面。

## 示例查询与在线检索流程

假设内部技术语料含“GPU project quota reset”文档，用户问“怎样恢复被用完的算力额度？”纯 lexical search 可能因没有出现 quota/reset 而漏召回，纯 dense search 又可能把“恢复 GPU 驱动”排得很高。在线流程先做规范化、拼写/语言识别与必要的 query rewrite；并行执行 BM25 倒排召回和 dual-encoder ANN 向量召回，各取候选及原始分数；用 reciprocal rank fusion 或经验证的轻量融合模型合并并去重；补充 freshness、文档类型等特征后，由 cross-encoder 对 query-document pair 重排，最后返回 top-K chunk 及分数、来源和调试 trace 给 RAG。对含错误代码、专有名词、数字的查询提高 lexical 权重，对自然语言意图可提高 dense 权重，但路由规则必须由离线分桶实验验证。若第一阶段没有足够候选，reranker 再强也无法救回，因此要分别评估召回与排序。

## 训练数据、损失与索引

dual encoder 分别编码 query 与 document，使用点积或余弦相似度；对一个正例和一组负例做 softmax contrastive loss，使正例分数高于负例。batch 内其他文档可作 in-batch negatives，throughput高但可能包含“其实也相关”的假负例；应结合人工判断、点击去偏标签、BM25 高分但不相关的 lexical hard negatives，以及当前 dense 模型近邻中的 semantic hard negatives。负例过难或被错误标注会使训练不稳，要做去重、规则过滤与少量人审。数据切分按时间和 query/document group，避免同一文档片段泄漏到训练与测试。索引侧离线/增量生成文档 embedding，按语料规模选择 HNSW、IVF 等 ANN 结构并调节 recall、内存、构建时间与查询延迟；文档版本更新要先写新向量，再原子切换可见版本，删除要传播到 lexical 与 vector 两套索引。cross-encoder 更准但成本高，只对数十或数百候选运行。

## 复杂度、评测与失败模式

倒排检索成本与命中 posting 长度相关，ANN 不是严格的 `O(log N)` 保证，其访问量取决于索引和搜索参数；融合去重约 `O(K_b+K_d)`，对 R 个候选重排的主要成本是 R 次 pair inference，可通过 batching、distillation或两级 rerank 降低。离线先测第一阶段 recall@K，再测完整排序的 MRR、NDCG@K、precision@K，并按短查询、错误码、长尾、时效、多语言分桶；RAG 场景还需测 context relevance、最终答案 faithfulness 与 citation correctness。点击率不能直接当真值，因为position bias和旧排序器决定曝光，可用随机化小流量、inverse propensity weighting、人工标注和时间切分校正；上线用 A/B 观察任务成功、无结果率、改写率、延迟与成本。故障测试包括语料突增、热门 query cache 击穿、embedding 模型升级导致新旧向量空间不兼容、索引只更新一半、重复 chunk、超长/空/对抗查询、罕见实体、流行度偏置和概念漂移。监控检索分数分布、ANN recall 抽检、索引年龄、各阶段 p95/p99 以及线上反事实样本，才能判断问题出在召回、融合、排序还是生成。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/rag-search-ml-design)
- [相关来源](https://www.1point3acres.com/bbs/thread-1158070-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
