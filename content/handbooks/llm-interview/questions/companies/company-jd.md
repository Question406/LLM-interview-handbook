---
id: company-jd
section: companies
order: 12
level: A
title: 京东：大模型 / Agent 研发应重点准备什么？
quick: >-
  Agent 工程题密度高：工具目录治理、MCP / Skill 分层、Reflection 归因、工具权限和 AI IDE
  隔离、RAG 幻觉兜底。电商场景还要把导购以外的用例，以及 Redis、压测讲清楚。
tags:
  - JD
  - 真题导航
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 秋招面经-京东大模型算法一面
    url: https://www.nowcoder.com/feed/main/detail/3f02a8e652fa414c819de810452a2b2a
    type: candidate-first-hand
  - title: 京东科技 AI 全栈 agent 研发一面面经
    url: https://www.nowcoder.com/feed/main/detail/e80b257b1c064970a72c9679c2177585
    type: candidate-first-hand
  - title: 京东大模型算法 实习面经
    url: https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46
    type: candidate-first-hand
  - title: 27暑期实习-京东Agent开发二面分享
    url: https://www.nowcoder.com/feed/main/detail/6af1c8611e434bbe8ba9cfa2bd0eaf18
    type: candidate-first-hand
  - title: 京东后端-一面
    url: https://www.nowcoder.com/feed/main/detail/ad9b86d7b29b4b5583840d0169458b0a
    type: candidate-first-hand
  - title: 京东零售平台产品与研发中心二面
    url: https://www.nowcoder.com/feed/main/detail/6a94272eee68460d9e8f90c72ddb8dab
    type: candidate-first-hand
  - title: 京东大模型应用开发 实习面经
    url: https://www.nowcoder.com/feed/main/detail/904555611d13461da9288d4147b7550b
    type: candidate-first-hand
---

京东相关岗分两条线。大模型算法会追 Toolformer、Reflection、PPO/GRPO 和复读机；Agent 研发会追工具目录、RAG 幻觉、意图识别评测和电商场景。准备时我不会把「会调工具」当成终点。

## 准备主线

1. **工具、协议与隔离**：MCP 只解决连接；Skill 解决流程；执行权在 Host。AI IDE / 工作区要防「幻读」式过期快照。
2. **训练范式**：Toolformer 自监督 vs RLHF；什么时候 PPO、什么时候 GRPO。
3. **生成病态**：复读机、重复解码怎么从数据、解码和训练三侧处理。
4. **RAG 生产**：幻觉不能只靠 prompt，要有检索归因、拒答和人工兜底。

## 本手册真题卡

点击下面每条即可跳到对应题。

- 京东：Reflection 如何归因知识缺失还是工具调用错误
- 京东：Toolformer 自监督 tool-call 数据与 RLHF 有何不同
- 京东科技：工具上下文太长、工具列表太多时如何治理
- 京东：什么时候用 PPO，什么时候用 GRPO
- 京东：如何解决复读机问题
- 京东 Agent：RAG 出现幻觉时如何设计兜底
- 京东：意图识别用什么模型，准确率怎么测
- 京东：向量检索里 IVF / HNSW 和暴力有何差异
- 京东：输入不标准时，混合检索权重怎么配
- 京东：SFT 和 PEFT 训练有哪些实用 trick
- 京东：Agent 为什么不能只看问答准确率，还要评什么
- 京东：如何评测 RAG 系统的准确率
- 京东：什么时候加缓存，为什么不能只用 MySQL
- 京东：除了导购，电商还有哪些场景适合 Agent
- 京东：Agent 和 RAG 的原理有何不同
- 京东后端一面：MCP 底层协议是什么，它解决权限问题吗？
- 京东后端一面：Skills 的本质是什么？和 MCP 差在哪一层？
- 京东一面：设计 AI IDE 时怎么定位，如何防止类似数据库的幻读？
- 京东零售二面：Agent 的长期记忆系统是什么？Prompt 过长怎么处理？
- 京东 Agent 二面：Redis 单线程为什么还能高并发？向量检索内部用什么算法？
- 京东 Agent 二面：JMeter 压测参数具体怎么设？
- 京东大模型算法实习：最长公共子序列和环形链表怎么写？
- 京东零售二面：二叉树中序遍历如何非递归写？
- 京东应用开发：对 RAG 和 Multi-Agent 的认知应怎么迭代？
- 京东应用开发：ES 和向量库具体怎么用？准召率如何保障？
- 京东应用开发：Transformer 的优劣和「哲学」怎么讲，还关注过别的架构吗？
