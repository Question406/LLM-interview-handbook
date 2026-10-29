---
id: drustz-66dc77dddae3378598
section: collections
order: 15
level: A
title: Anthropic 题库（爬取全量） · System Design
quick: 作者文档章节 · Anthropic 题库（爬取全量） · System Design
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md
    type: primary
---
## System Design

### System Design：Prompt Playground（onsite 高频）
*medium · 频率: high (5+ reports) · 2026-04*

设计一个类 ChatGPT Playground / Anthropic Console 的 prompt 工程平台。1p3a 题解页结构：需求定义→规模成本估算→API 定义→DB schema→架构总览→组件深挖→性能问题修复→方案对比（正文需登录）。多个 onsite 报告：SWE onsite 'Prompt Playground + Coding Q6' 组合（interview thread 1152158）；Telegram 镜像两例：一人 VO 四轮之一考 Prompt Playground，另一人店面挂在 image processing system design + Prompt Playground。

**解法**: 考点（我的推断）：prompt 版本管理与 diff、多模型/多参数并行试验、流式 SSE 输出、API key 与配额、prompt/completion 存储 schema（含大文本）、评估集与 A/B、成本追踪；性能部分常问长 prompt 渲染与缓存。HelloInterview 有公开同题讨论：[来源链接](https://www.hellointerview.com/community/questions/prompt-playground/cmjd4xmkg04nf08adwd3m0bvs)

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/post/7100017&gt;)

### System Design Q5：Data Infrastructure（数据平台题，与候选人数据管线背景对口）
*medium · 频率: single report · 2026-03*

55 min，medium 难度，单一报告，last asked 2026-03-07。题面（公开部分）：设计一个系统，ingest 大规模数据、处理后 serve 给多个 stakeholder，各方 access needs 和数据敏感度不同。标签：data-engineering/ingestion/ETL/access-control。Roles: SWE/DS/Infra。完整题面需登录。

**解法**: 我的推断：分层 lake/warehouse 架构（raw→cleaned→curated）、批流双路 ingest、schema registry、行/列级 ACL 与 PII 脱敏、audit log、数据血缘；对 Anthropic 场景可映射到训练数据管线+安全分级。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q5-data-infrastructure&gt;)

### 其他 onsite 设计/分析题：image processing system design、dataset analysis (cloud capacity)、Bootloader 新 coding 题
*unknown · 频率: single reports each · 2026-05*

Telegram 镜像（1p3a 转载）三条 2026 onsite 新信息：(1) 店面/onsite 设计轮考 image processing system design（一人挂在此轮）；(2) onsite 有 dataset analysis 轮：给云容量管理（cloud capacity management）数据集做分析，配合 'why Anthropic' 和 project presentation；(3) VO coding 出现新题 'Bootloader'（与 Prompt Playground SD、project deep dive、culture 同一 loop）。

**解法**: dataset analysis 轮类似 take-home 现场版：EDA→假设→容量预测/异常检测→建议，重讲清 reasoning。Bootloader 题无公开细节（我的推断：实现分阶段加载/依赖解析的模拟器类题）。

来源: &lt;[来源链接](https://t.me/s/usinterview?q=%23anthropic&gt;)

### System Design: Slack-like Chat System (DMs to 100K-member channels)
*hard · 频率: Anthropic freq 7/10 (shared: OpenAI 9, Snapchat 10, Meta 9, +9 more companies); last reported 2026-07-09 · 2026-03 (published)*

LOCKED (long preview captured). Stage: Onsite. Core messaging layer: DMs and group channels from 2 to 100K members. Preview clarifying Q&A gives the constraints: both small and announcement-scale channels in scope; delivery latency budgets differ - <=200ms for small conversations, <=500ms for large channels; central tension is eager per-member push for small channels vs pull/fan-out-on-read for huge channels (channel size becomes a first-class input to delivery strategy). Full solution paywalled.

**解法**: My inference: hybrid fan-out - write-time fan-out to per-user inboxes/connections below a membership threshold; read-time pull + lightweight 'channel updated' signal above it; per-channel message log (ordered, partitioned by channel id) as source of truth; WebSocket gateway layer with connection registry; unread counts via async counters; follow-ups usually cover ordering, presence, typing indicators, and hot-channel partitioning.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69c9fe5dff3ebde766ced6f4&gt;)

### System Design: Facebook Messenger (durable ordered history + realtime layers)
*medium · 频率: Anthropic freq 4/10 (Uber/Meta 7, Google/Microsoft 6); last reported 2026-07-08 · 2026-04 (published)*

LOCKED (long preview captured). Stage: Onsite. 1:1 and small-group realtime chat across devices. Preview clarifying Q&A pins scope: groups capped ~250 members (personal communication, not broadcast - keeps synchronous-path fan-out manageable); new group members can read FULL prior history by default (membership semantics = full shared history); durable ordered conversation history is the single source of truth, while presence/read-receipts/notifications are fast lossy layers around it. Full solution paywalled.

**解法**: My inference: per-conversation ordered log with server-assigned sequence numbers; multi-device sync via per-device cursors; push notifications + WebSocket delivery as best-effort layers reconciled against the durable log on reconnect; small-group fan-out done synchronously on send path; idempotent sends with client message ids.

来源: &lt;[来源链接](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d2bf7307421ca06eb8e38c&gt;)

### Anthropic classic-infra system design set: P2P file distribution, file cache, KV store, web crawler
*medium · 频率: multiple reports each · 2026-01*

Reported Anthropic onsite/phone-screen questions: (1) Peer-to-peer file distribution — distribute a large file to thousands of bandwidth-constrained machines; core tension: sequential transfers maximize per-transfer speed but force waiting vs simultaneous distribution splitting bandwidth (BitTorrent-style chunking is the expected insight). (2) File cache system — caching strategies, eviction, consistency. (3) Key-value store — storage engines, replication, partitioning, consistency models. (4) Web crawler — follow-ups on multi-threading, deduplication, crawl politeness. Guidance: 'abstract AI terminology immediately'; toolkit patterns = queuing, batching, consistent hashing, P2P distribution; address failure modes automatically for every component. Problems are often novel with no predetermined optimal solution.

**解法**: P2P: chunk the file, tree/swarm topology so each recipient becomes a seeder — total time O(log N) rounds instead of O(N); discuss rarest-first chunk selection and stragglers.

来源: &lt;[来源链接](https://www.tryexponent.com/blog/anthropic-system-design-interview&gt;)

### System design 真题：1B 文档 1M QPS 分布式搜索系统
*hard · 频率: single report（主题目）；变体各 1 报告 · 2025*

Medium 上 2025 年 SWE 候选人面经：system design 轮为设计 distributed search system，规格 1B documents、1M QPS，需要处理 sharding、caching、LLM inference scaling；面试官重点追问避免 hotspot 和 GPU 显存优化。其他被报告的 system design 题（jobright 聚合）：分布式 job queue（类 Kafka + workers）、"Implement a GPU Scheduling System Using Credits"（抢占逻辑、防资源垄断、容错）、"Design a 1-on-1 Chat System"（SQL vs Cassandra、离线投递、消息顺序、WebSocket 扩展）、为开发者设计访问 Anthropic 模型的 API。

**解法**: 倒排索引分片（doc-sharding）+ 多副本读扩展；两层缓存（query result cache + posting list cache）；热 term 用 replication+随机路由避免 hotspot；若含语义检索：ANN 索引（HNSW/IVF）分片 + embedding 服务批量化；GPU 显存：embedding 模型量化、动态 batching。（我的推断）

来源: &lt;[来源链接](https://medium.com/@anqi.silvia/my-2025-anthropic-software-engineer-interview-experience-9fc15cd81a99&gt;)

### Anthropic Staff/Sr Staff Infra onsite 系统设计真题 1：Model Downloader（模型分发）
*hard · 频率: 2 reports (Jun 2026) · 2026-06*

两份 2026-06/07 onsite 面经（同一候选人两处发帖+社区确认为常考题）：设计把大模型权重分发到大量机器的 Model Downloader。考生用 chunk-based pipeline 设计；讨论了 chunk size 如何影响 pipeline 式 vs tree 式分发的差异；先用 coordinator 分配 chunk 和做恢复，follow-up：没有 coordinator 时如何恢复（去中心化）。该轮被认为通过。这是 Anthropic 真实基础设施场景（把 checkpoint 快速分发到推理/训练cluster）。

**解法**: 类 BitTorrent/HDFS 混合：源分 chunk + 校验和，节点间 P2P 传播（tree 减少源带宽，pipeline 利用全双工），无 coordinator 用 gossip + 一致性哈希决定 chunk 归属 + 本地清单对账拉取缺失 chunk。讨论小 chunk=更好流水线但元数据开销大。

来源: &lt;[来源链接](https://www.reddit.com/r/OfferEngineering/comments/1udgir6/anthropic_sr_staff_infra_swe_onsite_model/&gt;)

### Anthropic 近期系统设计题库汇总（辅导教练整理）：Claude chat service、分布式/混合搜索、p95 延迟排查、1B 文档爬虫管线
*hard · 频率: aggregated from multiple loops (coach-reported) · 2026-03*

InterviewCoderHQ 'Targeting Anthropic' 帖（drCounterIntuitive，面试教练，2026-03）汇总近期 loop 真题：(1) Design a Claude chat service；(2) Design a distributed search system；(3) Design a hybrid search system（关键词+向量）；(4) Debug performance degradation：p95 延迟从 100ms 飙到 2000ms，如何排查、建监控、排序修复优先级；(5) Design data pipeline with concurrent web crawler for ~1B documents。风格提醒：interviewer-driven、time-box、中途 pivot，可能不让你按'需求→估算→API→高层→深挖'模板走；另确认 reference check 可能在流程走完前就开始；并发题常态化；表现好也可能不发 offer（决策不透明）。senior 还有 technical presentation 轮（讲自己项目）。

**解法**: p95 排查题按层讲：先定位（USE/RED 指标、tracing 分段）→常见根因（GC/连接池耗尽/热分区/缓存击穿/重试风暴）→监控（p50/p95/p99 分位 + burn-rate 告警）→修复排序按影响面。

来源: &lt;[来源链接](https://www.reddit.com/r/InterviewCoderHQ/comments/1rxinyi/targeting_anthropic_insights_from_recent/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
