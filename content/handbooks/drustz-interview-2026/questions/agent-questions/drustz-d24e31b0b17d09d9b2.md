---
id: drustz-d24e31b0b17d09d9b2
section: agent-questions
order: 3
level: A
title: A 类 · 具体应用场景设计题 · Anthropic（7/22）
quick: 作者文档章节 · A 类 · 具体应用场景设计题 · Anthropic（7/22）
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
## Anthropic（7/22）

### [A5] ⭐⭐⭐ Anthropic 最高频 SD：LLM Inference Batch API（含 batchstring 变体与 100K RPS 变体）
- 来源: 1p3a 题库 Very High（16+ 讨论）+ Exponent 完整题面 + OfferEngineering 2026-07 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · 50–55min 店面/onsite SD（含 Google Doc 书面形式）· 2025–2026-07 持续
- 考察点: batching 双触发、continuous batching/KV cache、响应路由、背压限流、GPU 容量与故障恢复




**题面 + 参考打法 + 高频追问**



**题面（Exponent 版原文）**："You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users." **batchstring 变体**：给定固定后端 `batchstring(inputs: list[str]) -> list[str]`，每批 1–100 条、固定 ~100ms 延迟（与批大小无关）、每 GPU 一次一批；要求 1000+ RPS、P95<500ms、GPU 利用率 70–80%。**完整需求版**（2026-07）：+ 优先级、流式、重试/幂等、排队/背压/限流/按优先级丢弃、KV-cache 显存、突发流量、worker 崩溃安全重试、可观测性。

**参考打法**：
- 请求队列 + 双触发 batch 调度器（凑满 OR 超时 10–50ms）；correlation ID/future 把结果路由回等待的 HTTP handler
- 有界队列 + 429 背压；付费用户多队列加权调度
- 改进层：continuous batching（vLLM 式）、prefill/decode 分离；KV per-token bytes $= 2 \cdot n_{layers} \cdot n_{kv} \cdot d_{head} \cdot \text{dtype}$
- 多 GPU：least-loaded / 一致性哈希（sticky 命中 prefix cache）
- **100K RPS 变体**（"Handle 100,000 req/s for an LLM token-generation service"）：按 tokens/sec 而非 RPS 定容；评分标准=剥掉 AI 皮找核心 infra 问题 + 主动 failure-mode 分析
- 深挖：[../03_gaps/scaling.md](?book=drustz-interview-2026&section=agent-core&question=drustz-2689044041125af3f2)、[../03_gaps/cost_latency.md](?book=drustz-interview-2026&section=agent-core&question=drustz-c813e25c602cdea6a6)

**高频追问**（原帖清单）：10K RPS 需要几块 GPU？ ｜ 新 GPU 启动 5 分钟怎么办（warm pool + 预测扩容）？ ｜ 一半 GPU 挂掉如何自动限流？ ｜ 500ms 里排队 vs 计算各占多少？ ｜ batch 中单条失败怎么办？ ｜ 重复请求要不要缓存？





→ **完整解答：[solutions/A5_batch_api.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-511499f433f1ec6716)**

### [A6] ⭐⭐⭐ Anthropic：Prompt Playground 全栈设计
- 来源: 1p3a 题库 high（完整题解）+ hack2hire 变体（freq 9/10）+ 多个 onsite 报告 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · onsite SD（**纯 Google Doc 书面讨论，不画图**）· 2026-04~06
- 考察点: 大文本编辑与存储、版本管理、异步 run+流式、LLM API 成本控制




**题面 + 参考打法 + 高频追问**



**题面**：设计类 OpenAI Playground / Anthropic Console 的 prompt 工程平台——写 prompt→迭代→运行→保存最佳版本。**不是 chatbot**：每次 Run 无会话记忆、one-shot；单用户项目（单写者简化版本管理）；prompt 可达 10MB/100K tokens；外部 LLM 慢但界面必须"感觉即时"；每次迭代持久化版本不丢好 prompt。

**参考打法**：
- **核心考点**（原帖标注）：10MB ≈ 250 万 token 远超模型上限——"可存储可编辑"与"可运行"必须分开讲
- 版本：append-only 版本链 + snapshot+diff（1000 次保存追问）；autosave draft vs committed version
- 内容：S3/content-addressed 放大文件，DB 放元数据；服务端 token 计数
- 运行：异步 run job + 流式 partial + idempotency key；run 历史关联 prompt-version+params+输出+成本/延迟
- 成本：估算给到高端模型 &#36;450/天——相同 prompt 结果缓存；读写流量低不需分片，贵的是 LLM 调用
- 每个取舍说 "可以 X 或 Y，我选 X 因为…"；书面轮要练打字表达（[../02_playbook.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d48438e1a63e68f6a5)）

**高频追问**：10MB 文件怎么处理？ ｜ 1000 次保存的版本追踪？ ｜ 如何防 LLM API 花费失控？ ｜ 大文档怎么搜索？





→ **完整解答：[solutions/A6_prompt_playground.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-a3f95a672539bfe129)**

### [A7] ⭐⭐⭐ Design ChatGPT：多轮对话后端 + SSE token streaming
- 来源: hack2hire（Anthropic 6/10、OpenAI 9/10）+ hellointerview 官方 guide + 多面经交叉 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic/OpenAI/generic · onsite SD · 2026 持续
- 考察点: 会话持久化、context 组装 token 预算、GPU 推理调度、SSE 流式与断线恢复




**题面 + 参考打法 + 高频追问**



**题面**：设计 ChatGPT 类服务后端——多轮对话、持久化历史（数天后续聊携带上下文）、context assembly、GPU cluster推理分发、SSE token 流式返回。指标：TTFT ≤500ms p50 / 2s p95；200M+ DAU；GPU 稀缺。Out of scope（hellointerview 版）：消息编辑、多模态、custom GPTs。

**参考打法**：
- 主线：API gateway → conversation service（持久存储）→ context assembler（system prompt + 摘要历史 + 最近轮次，token 预算）→ continuous batching 推理调度 → SSE streamer（可恢复 event id）
- 流式快路径与持久化写路径分离；TTFT 预算拆解（排队/prefill/首 token）
- 四个 deep dive：token streaming、GPU 调度、公平资源分配（防重度用户垄断 + 付费优先）、长会话截断/摘要控成本
- SSE vs WebSocket、断线用 Last-Event-ID 续传：[../03_gaps/streaming.md](?book=drustz-interview-2026&section=agent-core&question=drustz-306f658b7cd85b430e)

**高频追问**：safety guardrails 管线的延迟预算？ ｜ 多模型路由与灰度？ ｜ 会话摘要何时触发、存哪？





→ **完整解答：[solutions/A7_design_chatgpt.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-b6f2567ca90d9516d4)**

### [A8] ⭐⭐⭐ Anthropic：500GB 模型权重分发到 100–1000 GPU worker
- 来源: 1p3a 题库 medium（完整题解，SD 五题 portal 成员） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · 店面/onsite SD 55min · 至 2026-06
- 考察点: 带宽数学、链式 pipeline 分发、chunk 化、容错协调




**题面 + 参考打法 + 高频追问**



**题面**：把 500GB 模型权重分发到数据中心内 100–1000 台 GPU worker，总时间最短、容忍故障。约束：云端下载 10Gbps；每 worker 全双工 10Gbps。目标：100 台约 8 分钟、1–5% 故障率、支持增量更新与回滚。

**参考打法**：
- **要求当场算数学**：逐台串行 $N \cdot F/B$；树形广播上行带宽被 fan-out 均分 → $\sim \log_2 N \cdot F/B$；链式 pipeline chunk 化（收到即转发）$\approx F/B + (N-1) \cdot c/B \approx F/B$（chunk $c \ll F$）。$F/B = 500\text{GB}/1.25\text{GB/s} = 400s \approx 6.7$ 分钟——正好对上 8 分钟目标
- 中央 coordinator 定链序 + 追踪 chunk 位置；heartbeat 探活，节点挂了绕开重接链路
- chunk 大小权衡：太小协调开销大，太大流水线气泡大；SHA256 校验 chunk 与整文件
- 10K worker：分层（region → rack chain）或 BitTorrent 式 swarm

**高频追问**：为什么 pipeline 优于树形（数学证明）？ ｜ 链中间 worker 挂了？ ｜ 扩到 10,000 台还成立吗？





→ **完整解答：[solutions/A8_weights_distribution.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-a128f631d8dab91fc6)**

> 高分句：Anthropic 的 SD 题都是"AI 皮、分布式系统骨"——先剥掉 AI 包装说出核心 infra 问题，再用 tokens/sec 而不是 RPS 做容量推理。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/A_scenario_design.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/A_scenario_design.md)。作者整理资料；许可和第三方来源范围见阅读指南。
