---
id: drustz-2f5e775d8b9dcb8349
section: agent-questions
order: 7
level: A
title: C 类 · Live Coding / AI-assisted Coding 实操题 · Anthropic（7/22）
quick: 作者文档章节 · C 类 · Live Coding / AI-assisted Coding 实操题 · Anthropic（7/22）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md
    type: primary
---
## Anthropic（7/22）

### [C1] ⭐⭐⭐ Anthropic Agent Coding 轮：手搭 Claude agent loop（tool use 回答股票价格）
- 来源: 1p3a 三帖交叉 + Telegram 镜像 + Qbank "Agents Coding: LLM Tool Use"（medium 频率，last 2026-06-29） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · SWE/RE 技术店面（四选一 track）55min Colab · 2026 Q2 频率上升
- 考察点: tool schema 定义、tool_use/tool_result 协议、while 循环与终止、错误处理与防hallucination




**题面 + 参考打法 + 高频追问**



**题面**：实现 Claude agent loop——定义 tools、解析模型 tool call、执行工具回传结果、循环到最终回答。具体版本：给一个股票价格查询工具（`get_stock_price(symbol)`），让 agent 多步调用回答用户问题。环境：Google Colab + Anthropic API，共享屏幕，**可查语言文档和网页、禁 AI 助手**。官方 blurb："写出能编译运行的代码，并根据测试失败迭代"。

**参考打法**：
- 协议肌肉记忆：`stop_reason == "tool_use"` 分支 → 保留完整 assistant content → 追加匹配 `tool_use_id` 的 `tool_result` → 循环；同轮多个 tool_use 必须**一次性**全部回传
- while 循环 + max_steps + token 预算保护；工具异常转 `is_error: true` 回传让模型自修复，不泄异常栈
- 只读工具可并行（有界线程池）；副作用工具禁自动并行
- 防hallucination：system prompt 强制引用 tool 结果、final answer 校验有 tool 调用发生
- 手写模板先背熟：[../01_core/01_loop_and_tools.md](?book=drustz-interview-2026&section=agent-core&question=drustz-78ebf691851b815a7d)

**变体**：同菜单另有 "Prompting/Engineering with LLMs"（Colab，prompt 迭代 + 为输出建简单 evaluation，不含 tool-use）——同一套准备覆盖。

**高频追问**：prompt 设计 ｜ 防hallucination（强制引用 tool 结果） ｜ 并行 tool call 怎么做

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-anthropic-stock-agent`





→ **完整解答：[solutions/C1_stock_agent_loop.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-316f3c2c38b3a50173)**

### [C2] ⭐⭐⭐ Anthropic：Durable Function Call Cache（确定性 key + WAL 崩溃恢复）
- 来源: hack2hire 完整题面（freq 8/10，2026-07 活跃）+ 1p3a Qbank "Coding Q2 LRU Cache Durability" 独立收录 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · onsite coding 60min · 2026-06~07
- 考察点: 规范化序列化与哈希 key、append-only WAL replay、LRU recency 重建、容错反序列化




**题面 + 参考打法 + 高频追问**



**题面**：给部分实现的 Python `FunctionCallCache`（LRU 已写好）。**Part 1** `create_cache_key`：确定性可哈希 key——排序 kwargs、递归规范化嵌套 dict、函数名+args+规范化 kwargs 组成不可变容器。**Part 2**（durability）：cache 操作写 append-only WAL；重启 replay 同时重建值和 LRU recency（已有 key 的位置更新要显式 delete-and-reinsert——标准 replay 常漏）；优雅跳过尾部损坏/截断记录，不让启动失败。

**参考打法**：
- key 等价性：`inspect.signature.bind` + `apply_defaults` 让 positional/keyword/default 同一 key
- WAL record：version + operation + payload + checksum；replay 在第一条坏记录停止（官方提示：try/except 跳过畸形尾部）
- put 和 hit（touch）都追加记录，否则 recency 恢复不完整
- 官方 follow-up 全清单：不可 JSON 序列化参数（自定义类）｜ 序列化字符串 vs 值元组 key ｜ 函数签名/源码变化的失效 ｜ 线程安全 ｜ 多进程并发 ｜ 批量写降 I/O ｜ checkpoint 加速恢复 ｜ log compaction

**高频追问**：pickle 为什么不适合不可信文件？ ｜ 如何演进 key encoding 不静默错误命中？

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-anthropic-durable-cache`





→ **完整解答：[solutions/C2_durable_cache.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-f1e2141227ee03a6bc)**

### [C3] ⭐⭐⭐ Anthropic 2026 新增 onsite AI-assisted coding 轮（提供 Claude Code CLI）
- 来源: 1p3a VO 结构帖（5+ 报告）+ Telegram 镜像多例 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · VO coding 轮（部分 loop）· 2026 新增
- 考察点: 驾驭 AI agent 的工作流：任务拆解、给 Claude Code 写 spec、review 生成代码、验证




**题面 + 参考打法 + 高频追问**



**形式**：2026 年 Anthropic SWE/RE VO 四轮（coding/SD/project deep dive/culture）中新增的 coding 轮，明确允许并要求"使用 AI 工具编写和审查代码"，现场提供 Claude Code CLI。**对照规则**：店面禁 AI 工具（但可抄网上正当搜到的代码）。VO coding 题为题库题（tokenizer/Bootloader/dedupe 3-part 等），SD 轮为 Prompt Playground / inference API 等。流程硬 gate：技术轮挂了静默取消后续。

**参考打法**：
- 评的不是裸算法，是工作流：先自己读题拆解 → 给 Claude Code 清晰 spec（验收条件、边界）→ review diff → 跑测试验证
- 全程 narration："我让它做 X，因为…；这段我要自己验证，因为…"
- 平时用 Claude Code 做真实项目即最好准备；现场脚本见 [../02_playbook.md](?book=drustz-interview-2026&section=agent-core&question=drustz-d48438e1a63e68f6a5)

**高频追问**：为什么接受/拒绝这段 AI 生成的代码？ ｜ 怎么确认它没破坏别处？





### [C4] ⭐⭐⭐ Anthropic FDE/Applied AI 店面：55 分钟 CodeSignal "build an agent"
- 来源: 多帖交叉 2026-01~07（含 2026-06 FDE 面经） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · FDE/SA-Applied AI/Product Engineer 轨店面 · 2026
- 考察点: 现场从零搭 agent：prompt 优化到特定输出、debug 输出不稳定、边缘案例改进




**题面 + 参考打法 + 高频追问**



**形式**：55 分钟 CodeSignal "build an agent"——可能可用 Claude SDK 但**禁 AI 辅助**。实际包含：优化 prompt 达到特定输出、理解模型局限、debug 为什么某些 prompt 输出不稳定、改进 chatbot 边缘案例响应。该轨 OA 是较短的 prompt engineering 测试（非 SWE 4-part ICA）。后续 onsite：dataset analysis（云容量场景：利用率/瓶颈/成本-延迟-可靠性权衡）、project presentation、XFN 协作（含 SQL）、HM（research→生产系统）。

**参考打法**：练"从空白到能跑的 agent"55 分钟节奏：先最小 loop 跑通 → 加 tool → 再调 prompt；输出不稳定的排查顺序 = temperature/sampling → prompt 歧义 → few-shot 锚定 → 结构化输出约束。

**高频追问**：为什么这个 prompt 不稳定？ ｜ 模型做不到 X 时你怎么绕？





→ **完整解答：[solutions/C4_build_an_agent.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-cebf765a31b8312976)**

### [C5] ⭐⭐⭐ Anthropic：为 tool-calling agent 的 API 实现线程安全 rate limiter
- 来源: 多来源报告（reyzharkov 面经 + Glassdoor 风格总结） ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · live coding · 2025
- 考察点: 限流算法 + 并发安全 + 分布式扩展 + 降载




**题面 + 参考打法 + 高频追问**



**题面**：实现 rate limiter，follow-up 递进：(1) 线程安全（场景：agent 并发高频调外部 API）；(2) 多机分布式限流；(3) sliding window 实现；(4) load shedding。

**参考打法**：token bucket 单机 + lock/原子操作 → 分布式用 Redis Lua 原子脚本或一致性哈希分片 → sliding window log（精确、内存 O(n)）vs sliding window counter（近似、O(1)）的 tradeoff → 降载按优先级丢弃 + 429 with Retry-After。

**相邻题族**（同来源报告）：实时流数据处理（去重/排名/聚合/故障检测）、sequence packing for LLM training（变长序列打包 max_length，first-fit decreasing 贪心）、tokenization 引擎、duplicate file finder、log processing。Glassdoor 总结 Anthropic coding 风格："software development assignment with a bit of leetcode baked in"。

**高频追问**：突发流量 vs 平均速率怎么同时限？ ｜ 时钟漂移对分布式窗口的影响？





→ **完整解答：[solutions/C5_rate_limiter.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-67e47e8dac3ab7adb8)**

### [C6] ⭐⭐⭐ Anthropic RL Fundamentals 轮：debug GRPO training loop（3 个埋点 bug）
- 来源: 1p3a 三帖（2026-05，3+ 报告）+ prachub 评分维度页 ｜ 置信度: ✅ ｜ 公司/轮次: Anthropic · RE 店面四选一 track · 2026 Q2 新增
- 考察点: GRPO 实现级理解、系统性 debug、区分"设计内偏差"与真 bug 的实验设计




**题面 + 参考打法 + 高频追问**



**题面**：给简化 GRPO 训练 step 实现，含 3 个埋好的 bug，每个要求给出**检测方法+具体修复**（不能只点名）。常见 bug 池：log-prob 未对齐 autoregressive shift、loss/KL 的 token masking 错、advantage normalization（组内奖励全相同→除零/无信号）、rollout 与 update 的 policy 混用。

**核心追问**：严格 on-policy 下为什么 importance ratio $\exp(\log\pi_\theta - \log\pi_{old}) \neq 1$？要求设计判别实验区分设计内偏差（推理引擎与训练器 forward 路径不同、bf16/fp32 精度、每 rollout batch 多次 optimizer step）与真 bug。

**参考打法**：
- 应主动澄清：reward 类型、每 batch optimizer 步数、生成与打分是否同一 forward 路径、sampling温度/top-p、KL 实现、数值精度
- Follow-ups：clipped surrogate 如何防崩、组内奖励全同怎么办、engine-to-trainer log-prob 修正、process vs outcome supervision、KL 放 reward 还是 loss
- 手写练习：`../../online_resource/drills/04_grpo_ppo.py`；概念梳理 [../03_gaps/agentic_rl.md](?book=drustz-interview-2026&section=agent-core&question=drustz-ecc62e136df467a25f)；tool-return masking 见 [D 类 D20](?book=drustz-interview-2026&section=agent-questions&question=drustz-9d5b52c44f5252c7ab)





→ **完整解答：[solutions/C6_grpo_debug.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-a23b472ed3ba1b5d1e)**

### [C7] ⭐⭐⭐ Anthropic Applied AI 轨题族：retrieval scorer / token-budget allocator / customer-brief take-home
- 来源: getperspective.ai 博客（单源二手；tool-use orchestrator 部分与 1p3a 印证） ｜ 置信度: ⚠️ ｜ 公司/轮次: Anthropic · Applied AI 60min 店面 + 3–4h take-home · 2025H2–2026H1
- 考察点: LLM 周边实用 Python：检索评估指标、context/token 预算、API hygiene、模糊需求自主决策




**题面 + 参考打法 + 高频追问**



**店面三类实作（LLM-adjacent Python）**：(1) retrieval scorer——给 query-document 对和相关性标注，实现打分/排序 + 评估指标（MRR/NDCG，追问平局与缺失标注）；(2) token-budget allocator——多个消息/文档/工具结果竞争有限 context window，按优先级+截断策略分配 token 预算（追问截断对下游影响、缓存友好性）；(3) tool-use orchestrator——与 [C1](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md#c1) 同型。

**Take-home**：按虚构企业客户 brief，3–4h 用 Claude API 构建能跑的应用。评分＝"shipped behavior, API hygiene"（Messages API/tool use/prompt caching/重试）+ 模糊需求下独立做合理假设。后接 60–90min customer-conversation simulation（discovery 而非 demo——问买家现有评估标准、过去失败的 AI 部署），博文称该轮与 offer 相关性最强；SD 轮 "increasingly focuses on evaluation harnesses, not RAG architecture"。

**打法**：NDCG 手写公式过一遍；token allocator 用贪心+优先级桶；take-home 必带最小 eval 脚本。





### [C8] ⭐⭐⭐ Anthropic：Weighted DataBatcher with Deterministic Checkpointing
- 来源: 1p3a 研究岗面经转述（v1 练习版题面） ｜ 置信度: ⚠️ ｜ 公司/轮次: Anthropic · ML 岗 coding-design 55min · 2025–2026
- 考察点: 加权sampling、checkpoint/resume 确定性、iterator 状态模型




**题面 + 参考打法 + 高频追问**



**题面**：实现 `DataBatcher(registry, weights, seed)`：`next_batch(k)` 按权重选数据源取样；`checkpoint()` 返回可序列化 state；新实例 `resume(state)` 后必须产生与未中断运行**完全相同**的后续样本流。说明动态增删数据源和 multi-worker 语义。

**参考打法**：registry version + 规范化 weights 写进 checkpoint → seeded RNG state 或 counter-based choice 保证随机流可续 → 每 source 存 cursor/epoch，batch commit 后原子推进 → registry 变化默认拒绝恢复（要兼容需显式 migration policy）→ 测试 uninterrupted 与 split-run 序列完全相等。

**高频追问**：checkpoint 正好在 batch 一半？ ｜ 百万数据源的高效 weighted choice（alias table / 树状累积权重）？ ｜ worker 扩缩容 shard 稳定性？

完整 rubric: [../../agentic/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic/data/questions.json) → `q-anthropic-weighted-batcher`





→ **完整解答：[solutions/C8_weighted_batcher.md](?book=drustz-interview-2026&section=agent-questions&question=drustz-6997781bde8be3ca8d)**

> 高分句：Anthropic 全程可查文档、禁 AI——把 tool_use/tool_result 协议写成肌肉记忆，现场时间花在错误处理和终止条件上。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/05_questions/C_live_ai_coding.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/05_questions/C_live_ai_coding.md)。作者整理资料；许可和第三方来源范围见阅读指南。
