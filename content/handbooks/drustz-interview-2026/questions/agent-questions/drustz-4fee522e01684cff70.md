---
id: drustz-4fee522e01684cff70
section: agent-questions
order: 4
level: A
title: A 类 · 具体应用场景设计题 · OpenAI / generic（⭐⭐：迁移备用）
quick: 作者文档章节 · A 类 · 具体应用场景设计题 · OpenAI / generic（⭐⭐：迁移备用）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Interview Questions & Solutions
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md
    type: primary
---
## OpenAI / generic（⭐⭐：迁移备用）

### [A9] ⭐⭐ Design Sora / GPU job scheduler（OpenAI 2026 最高频 SD）
- 来源: 1p3a Very High（19 帖，last asked 2026-06-29）+ hack2hire GPU Scheduling Platform（OpenAI 10/10）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 电面+onsite SD 60min · 2026-04~07
- 考察点: durable orchestration on preemptible GPUs：状态机、lease/fencing、checkpoint 恢复、两阶段放置




**题面 + 参考打法 + 高频追问**



**题面**：为 Sora 式视频生成设计后端——提交 prompt+参数，服务接受任务、调度到外部 GPU 池、跟踪进度、返回视频。约束：每 worker 同时一个视频；GPU 池**可抢占**，worker 随时可能被终止。过来人共识："别被名字唬到，本质就是 job scheduler"。NFR：创建 P95<500ms、调度 P95<30s、进度新鲜度<5s、accepted job 零丢失、抢占损失<30s。容量：100K 视频/天、峰值 20 jobs/s、单视频 ~3min → ~3600 并发、~4000 warm worker。姊妹题（hack2hire）：共享训练/批处理 GPU cluster调度平台——优先级队列+抢占、两阶段放置（DB 预留→node agent ack→commit）、desired vs actual reconciliation loop。

**参考打法**：
- 异步 API：先 durable write 再返回 202+job_id（入库前返回成功=红牌 pitfall）
- PostgreSQL source of truth + Redis 队列（可从 DB 重建）+ 对象存储放 checkpoint/成品
- worker **pull** 调度 + heartbeat lease + fencing token；lease monitor 自动 requeue；幂等完成接口防 stale worker
- 队列按 priority_tier + model_version + gpu_type 分区；checkpoint 频率自适应
- Pitfalls：假设供应商发抢占预警（心跳丢失才可靠）、无 fencing、单一 FIFO 混用所有模型

**高频追问**：push vs pull（volatile worker 选 pull）？ ｜ 网络分区 split-brain？ ｜ gang scheduling / per-team 配额（DRF）？ ｜ 供应商容量骤降的 admission control 与 ETA？





### [A10] ⭐⭐ OpenAI：企业级 RAG 聊天机器人（类 Glean）
- 来源: 1p3a 完整题解 + Qbank 两条独立行（MLE/RE 轨）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · 60min onsite ML SD（2026 春取消后恢复）· 至 2026-03
- 考察点: 超越教程级 RAG：权限、多租户、评估/hallucination检测、多轮




**题面 + 参考打法 + 高频追问**



**题面**：设计企业内部搜索问答 RAG 机器人（类比 Glean）：检索公司数据 + LLM 生成带引用回答。要求：多用户/多租户、权限控制、数据安全、答案带来源、低延迟。

**参考打法**：
- 架构解耦 ingestion/retrieval/generation；设计 API + 聊天日志 schema
- 检索：semantic vs hybrid（BM25+dense）、cross-encoder rerank、事实型 vs 开放型问题分流
- **权限过滤在检索层做**（用户只能召回有权文档），不是 prompt 层
- 质量：强制 grounding + citation 追踪、no-hit 兜底拒答、量化指标（groundedness/citation correctness）
- 性能：embedding 与热门问题缓存、批处理；RAG 细节见 [../03_gaps/rag.md](?book=drustz-interview-2026&section=agent-core&question=drustz-3ca2bc23429af23dbe)
- **失分点**（原帖）：做成教程级、忽略多轮属性、不讲评估、不考虑百万文档增长、忽略隐私

**高频追问**：如何评估 RAG 质量与检测hallucination？ ｜ 文档更新与版本？ ｜ 多轮对话历史管理？





→ **完整解答：[solutions/A10_enterprise_rag.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-5459a213c9a546aa52)**

### [A11] ⭐⭐ 企业知识库 conversational agent（含官方评分 rubric；多租户/10M 规模变体）
- 来源: PracHub 2026 GenAI SD 指南（recurring prompt + rubric）+ substack/field guide 多源 + agentswarms 变体 ｜ 置信度: ✅ ｜ 公司/轮次: generic GenAI loop · SD 轮 · 2025–2026
- 考察点: RAG 全链路 + 评分维度：framing、检索深度、成本意识、质量/安全、trade-off 主导权




**题面 + 参考打法 + 高频追问**



**题面**："Design a conversational AI agent for our enterprise knowledge base."（GenAI 面试循环 recurring prompt）。变体：cost-optimized / latency-optimized / accuracy-optimized 三种约束版本；**多租户变体**："multi-tenant RAG where each tenant's data is isolated"；**规模变体**："scale an AI search assistant for 10M+ articles"。

**参考打法**：
- 四阶段逐段讲 trade-off：摄取与 chunking（小 chunk 缺上下文/大 chunk 稀释语义）→ embedding（商用 vs BGE 成本）→ retrieve-then-rerank → 生成与流式编排
- **官方 rubric**：framing（点明概率性本质+澄清延迟/敏感度/规模）、retrieval depth、cost awareness（semantic caching、model routing）、quality/safety（evals、citations、guardrails、反馈回路）、trade-off leadership（主动挑明 precision-latency-cost 张力）
- 多租户：per-tenant namespace vs 共享索引+元数据过滤 vs 物理隔离；ACL 在检索层强制；防租户 A 文档注入影响租户 B
- 10M 规模：hybrid + 按主题 shard + 热点缓存 + precision@k 监控；换 embedding 模型的增量重建

**高频追问**：文档互相矛盾优先检索谁？ ｜ 用什么指标度量准确率？ ｜ embedding 换代如何避免全量重建？





→ **完整解答：[solutions/A10_enterprise_rag.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-5459a213c9a546aa52)**（与 [A10] 共用同一份解答）

### [A12] ⭐⭐ OpenAI：Design the OpenAI Playground（全栈：wireframe + API + schema）
- 来源: Exponent guide（reported screen 题）+ 1p3a Qbank 两条（GPT-3 Playground、Design AI Chatbot System，元数据级）｜ 置信度: ✅ ｜ 公司/轮次: OpenAI · SD screen 60min · 2025-10~2026
- 考察点: LLM 产品全栈：前端 wireframe、API 层、thread/message history schema；10x–1000x scale 压测




**题面 + 参考打法 + 高频追问**



**题面**："Design the OpenAI Playground"——前端 wireframes + API layer + thread/message history 的 DB schema，**明确期望全栈**（recruiter 会预告）。同族 Qbank 题：GPT-3 Playground（tech-screen，标签 fullstack/streaming）、Design AI Chatbot System（SSE/WebSocket/api-integration）。

**参考打法**：
- 复用 [A6] Anthropic Prompt Playground 正文（题面几乎同构），OpenAI 版加：前端组件拆解 + REST endpoint 具体化 + 消息队列语义
- 面试官套路：先验证初始设计→"what if we 10x/100x/1000x scale?"——必须点名哪个组件先崩并重设计它
- **主动问清**：model-inference/ML-infra 层要设计还是当黑盒 API
- OpenAI SD 风格：product+infra 混合、中途抛新约束/twist、背模板会翻车

**高频追问**：1000x 后哪个组件先崩？ ｜ thread history 的分页与冷热分层？ ｜ 流式失败的前端体验？





### [A13] ⭐⭐ Design GitHub Copilot / Design Perplexity（实时 LLM 搜索）
- 来源: Colin Zhou 2025 面经总结 + field guide 转引 ｜ 置信度: ✅ ｜ 公司/轮次: generic · AI SD 轮 · 2025
- 考察点: 低延迟 LLM 产品：上下文构建、缓存、实时检索+引用、成本




**题面 + 参考打法 + 高频追问**



**题面**：(1) "Design an AI co-pilot like GitHub Copilot"；(2) "Design a Perplexity.ai / real-time LLM-powered search engine"。

**参考打法**：
- Copilot：补全延迟预算 ~200ms → 小模型 + FIM（fill-in-the-middle）；context = 当前文件 + 光标邻域 + repo 级检索；请求去抖与前缀缓存；北极星指标=接受率；代码隐私
- Perplexity：实时抓取/索引 + RAG + 逐句引用、查询改写、多源冲突处理；可引 ByteByteGo 拆解（日均 2 亿查询、Vespa 上的 RAG、微调 Sonar）
- 共同点：LLM 当黑盒后拼延迟、成本、检索质量——成本模型见 [../03_gaps/cost_latency.md](?book=drustz-interview-2026&section=agent-core&question=drustz-c813e25c602cdea6a6)

**高频追问**：接受率下降怎么归因（模型 vs context vs 触发时机）？ ｜ 引用与来源冲突怎么呈现？





### [A14] ⭐⭐ PromptLayer 官方题单：白板三题 + coding 三题 + take-home 三选一
- 来源: PromptLayer CEO 官方博客（自家面试题+rubric 全公开） ｜ 置信度: ✅（官方一手） ｜ 公司/轮次: PromptLayer · 白板/live coding/take-home · 2024–2025
- 考察点: 问题分解、多步 agent 流程、每组件 prompt 结构、错误处理；take-home 强制带 eval




**题面 + 参考打法 + 高频追问**



**白板三题**：(1) 分析客服工单并自动起草回复、复杂问题升级的 agent；(2) 多 agent 协作产出带引用研究报告；(3) 读代码、理解意图、建议改进的 agent。**公开 rubric 四条**：子任务分解清晰、agent 步骤间逻辑流、错误处理与边界、每组件 prompt 结构设计。

**Live coding 三题**（允许 ChatGPT、禁 Cursor——观察你怎么写 prompt）：batch LLM API 调用、debug embeddings 处理代码、清洗文本准备 fine-tuning。**Take-home 三选一**：CSV 客户数据→个性化 email campaign（含质量 eval 指标）；文档 Q&A + citation tracking（multi-hop）；Python code review agent（含 accuracy eval）。评分三条：能跑、有意义的 eval、能阐述设计理由。

**打法要点**：所有 take-home 都强制 eval——这是 2025 后 agent take-home 共同趋势，答任何 agent 设计题都主动给 eval 段落（[../01_core/06_eval_security.md](?book=drustz-interview-2026&section=agent-core&question=drustz-4e50f8e0f483daa35c)）。





### [A15] ⭐⭐ 客服 agent：日处理 10K 工单、响应 <2s
- 来源: agentswarms 聚合站（称 Stripe/Intercom/Klarna 在问，归属未验证） ｜ 置信度: ⚠️ ｜ 公司/轮次: generic senior SD · 2025–2026
- 考察点: 意图分流、模型分层、延迟/成本预算、HITL 升级、guardrails




**题面 + 参考打法 + 高频追问**



**题面**："Design a customer-support agent that handles 10,000 tickets/day with <2s response time."（Sierra 面试的 generic 版，与 [A1]/[A2] 互补）

**参考打法**：
- 前置意图分类分流：FAQ 直答 vs 需查库 vs 直升人工
- <2s → 模型分层（小模型路由 + 大模型兜底）、semantic cache、流式输出掩盖尾延迟
- RAG 知识库 + 工具调用（订单/退款 API，写操作 HITL 审批）
- 工具失败重试降级；per-ticket 成本核算；上线前 eval harness + 回归集
- 素材：Doctolib（有向图上的专门化 agents，日均 17K 消息）、Intercom/Klarna 公开案例

**高频追问**：How would you implement a human-in-the-loop approval step for high-risk agent actions?





### [A16] ⭐⭐ 受限域三题族：银行零hallucination chatbot / AI 法律合同 / 医院语音助手
- 来源: bhavishyapandit9 substack（7 deep-cut AI SD 题） ｜ 置信度: ⚠️ ｜ 公司/轮次: generic · AI SD 轮 · 2025–2026
- 考察点: 生成边界收紧：LLM 只做界面层、模板+槽位受控组装、多约束排优先级




**题面 + 参考打法 + 高频追问**



**三题面**：(1) "Build a chatbot for a bank that must not hallucinate"；(2) "AI tool to generate legal contracts from prompts"；(3) "Voice assistant for hospital staff"。

**共同答案模式——把自由生成降级为受控组装**：
- 银行：LLM 只当界面/改写层不当知识源；账户事实路由到结构化 API；回答带来源+审计日志；置信度不够拒答；合规 disclaimer
- 法律：预审核条款模板库 + 可填槽位（当事人/金额/期限）；LLM 只做意图解析与 paraphrase；条款带 metadata（辖区/版本）；输出前强制用户批准 + 版本控制
- 医院：边缘 ASR 降延迟、医学术语微调、HIPAA 加密/匿名化、高风险操作前确认、ASR 失败回退键入——考互相冲突约束（延迟 vs 准确 vs 隐私）的排序

**高频追问**：API 数据不完整的边界？ ｜ 新辖区/新法规的治理流程？ ｜ 发音相近术语消歧？





> 高分句：企业 RAG 的权限过滤必须发生在检索层——靠 prompt 叮嘱模型"别看无权文档"在架构上不成立。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/A_scenario_design.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md)。作者整理资料；许可和第三方来源范围见阅读指南。
