---
id: company-bytedance
section: companies
order: 2
level: A
title: 字节 Seed：Post-Training / Agent 岗重点是什么？
quick: "字节 Seed 算法岗重点在 Reasoning / Agent RL，会追问 MoE 路由、rollout 长尾和过程奖励。Agent 岗重点在 Harness、Memory 和 Context Engineering，会追问压缩校验、记忆污染和 patch 回滚。"
tags:
  - ByteDance
  - Seed
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Seed 2027 大模型人才校招
    url: https://seed.bytedance.com/zh/seedearlycareer
    type: primary
  - title: 字节跳动-Agent开发实习生 一面
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
  - title: 字节AI Agent开发秋招一面面经
    url: https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887
    type: candidate-first-hand
  - title: 字节27暑期 大模型算法一面凉经分享
    url: https://www.nowcoder.com/feed/main/detail/28b254940eb940189188d795f4606c52
    type: candidate-first-hand
---

字节 Seed 的 Agent 题早就过了「会 LangGraph」这一层，公开面经已经问到 Harness、Spec、压缩有没有破坏任务、错误记忆怎么纠错。算法岗则会把 GRPO 一路问到 MoE 路由和 sampling 轨迹（rollout）工程。

比如长期记忆里写进了一条过期的摘要，后面几轮 Agent 都基于它做决定，面试官会问你怎么发现、怎么纠正。这类题要能讲到具体的检查和回滚，光说概念不够。

## 准备主线

1. 失败归因要按 model / tool / context / memory / harness / 奖励分数（reward） / data / eval 分层，并给出对照实验。
2. Harness 和调 API 的区别在权限、调度、校验和回放。
3. 记忆卫生关注过期摘要、错误结论入库和重复工具调用。
4. RL 系统要讲组内零优势、rollout 长尾，以及过程分怎么分配到 token 上。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- 字节大模型算法：SFT 和 GRPO 在优化目标上有何区别？
- 字节大模型算法：GRPO 一组全对或全错时为什么这一步不起作用？
- 字节 26 秋招：DeepSeek-R1 的奖励（规则 vs RM）以及两阶段如何开展？
- 字节大模型算法：如何搭建训练数据构造 Pipeline？
- 字节实习：一个 Agent 误判导致策略冲突时如何恢复？
- 字节 27 暑期：MoE 的 rollout / 训练专家路由为何不一致？GSPO 怎么缓解？
- 字节 AI 数据技术：Function Call 有标准答案，为什么还要 Reward Model？
- 字节 AI 数据技术：Agent 后训练的 SFT / RL 数据怎么设计，何时切 RL？
- 字节 27 暑期：GRPO rollout 长尾拖低 GPU 利用率，工程上怎么解？
- 字节 27 暑期：Agent 行为分数怎样落到 token 上？
- 字节 27 暑期：GRPO 在 Agentic RL 场景下如何设计过程打分？
- 字节 Agent 算法一面：讲讲 veRL 的结构、关键组件，怎么魔改？
- 现在做 LLM RL，面试会问哪些训练框架题？
- 你用过 veRL 和 slime，两者差在哪、什么时候换？
- slime 里 DAPO 动态 sampling 和 partial rollout 怎么配？
- slime 的异步训练怎么开？
- 字节 Agent 实习一面：什么是 Harness Engineering？和只调 LLM API 差在哪？
- 字节 Agent 一面：SDD、Spec-kit、OpenSpec 是什么，和 Harness 怎么配合？
- 字节 Agent 一面：从 ES 切到向量检索，哪些能力升、哪些会降？
- 字节 Agent 一面：三级压缩怎么做？为什么常见是按轮次切？
- 字节实习一面：长期记忆过期或写进错误结论，怎么发现和纠错？
- 字节实习一面：RAG、Memory、Context Engineering 各解决什么，Coding Agent 里怎么配合？
- 字节实习一面：错误 patch 怎么回滚、验证和再试？团队内部还要管哪些安全和审计？
- 字节 Agent：工具超时、文件不存在、权限不够时，直接报错还是恢复重试？
- 字节秋招一面：Agent Token 涨得太快，怎么定位和压？
- 字节实习一面：团队内部 Coding Agent 怎么管权限、命令和敏感信息？
- 字节实习一面：ReAct 里怎么选工具，选错了怎么纠？
- 字节秋招一面：短记忆和长记忆怎么分工？
- 字节实习一面：Recall@5 怎么算，评测 overfitting 怎么防？
- 字节实习一面：合并两个有序数组（原地 / 双指针）
