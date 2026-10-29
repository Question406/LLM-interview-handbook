---
id: drustz-ea4791fbf769cbdf2f
section: mlsd
order: 37
level: A
title: >-
  06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 十二、常见 failure
  modes 与 debug 顺序
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 十二、常见
  failure modes 与 debug 顺序
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
## 十二、常见 failure modes 与 debug 顺序

| 症状 | 首先查 | 可能根因 | 修复方向 |
|---|---|---|---|
| 答案错但 citation 看似对 | claim→span | citation 只 topic match，不 entail | atomic claim grader、human audit |
| Relevant page 从未出现 | candidate recall | index coverage、chunking、embedding、filter | 先修 crawl/index/retriever，不调 answer prompt |
| Offline nDCG 升、线上差 | slices/log policy | label leakage、click bias、query drift | temporal holdout、exploration、downstream metric |
| 搜索次数越来越多 | trajectory | SFT 冗余、reward 无 cost/stop | stop labels、budget、Pareto eval |
| 搜索次数为零但答得流畅 | search necessity | cost penalty 过大、benchmark 可背 | fresh/no-answer tasks、evidence gate |
| 只返回大站 | source mix | authority feature domination | diversity/long-tail slice、calibration |
| 新页面搜不到 | freshness funnel | recrawl/index/cache lag | 分段测 lag，event-driven updates |
| Hard-negative 训练退化 | labels | false negatives、过难、teacher bias | pooling annotation、multi-positive、curriculum |
| Latency tail 爆炸 | trace waterfall | dead host、串行 fetch、large rerank K | deadlines、bounded parallelism、early exit |
| 被网页指令劫持 | tool boundary | page text进入高权重 prompt | untrusted data channel、policy、injection eval |

Debug 顺序建议：

```text
coverage/index → candidate recall → reranking → excerpt/evidence
→ agent policy → answer synthesis → online UX/feedback
```



不要一看到最终答案错就 fine-tune generator。先找“第一个发生错误的 stage”。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。
