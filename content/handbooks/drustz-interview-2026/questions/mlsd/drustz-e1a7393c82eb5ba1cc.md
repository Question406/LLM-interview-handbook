---
id: drustz-e1a7393c82eb5ba1cc
section: mlsd
order: 23
level: A
title: 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 一、90 秒开场（建议背下来）⭐⭐⭐
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 一、90
  秒开场（建议背下来）⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md
    type: primary
---
## 一、90 秒开场（建议背下来）⭐⭐⭐

> 我会先确认产品是给人看的十条蓝链接，还是给 agent 用的 retrieval API，因为后者更关心 evidence completeness、可解析正文、freshness、citation 和每个成功任务的总成本。系统上我会做分层 cascade：query understanding → lexical/dense candidate retrieval → learned reranking → content extraction → search agent / grounded answer。训练数据由四部分组成：人工 graded relevance、经过 propensity correction 的行为日志、document-to-query synthetic pairs，以及真实 agent trajectories。Retriever 用多正例 contrastive learning 和持续 hard-negative mining；reranker 用 pairwise/listwise relevance，并显式加入 authority、freshness、duplication 等特征；agent 先用高质量 demonstrations 做 SFT，再用 preference 或 outcome-verifiable RL 优化 task success，同时对 search calls、延迟、无效引用加成本。评估必须拆成 component、trajectory、answer、system 四层，并用按时间切分的 held-out queries 防止网页和答案泄漏。上线从 shadow 和 interleaving 开始，再做小流量 A/B，guardrail 是 citation correctness、source diversity、tail latency 与成本。

如果 interviewer 只给 30 分钟，把后面所有内容压缩成这五步：

```text
1. 定义用户任务与 freshness/cost SLO
2. 建立 query × candidate × graded label 数据闭环
3. hybrid recall → learned rerank → grounded synthesis
4. SFT demonstrations → preference/RL trajectories
5. temporal offline eval → shadow/interleave → A/B + rollback
```



---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。
