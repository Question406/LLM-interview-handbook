---
id: company-xiaohongshu
section: companies
order: 14
level: A
title: 小红书：后训练 / Agent / 全栈应重点准备什么？
quick: "小红书后训练岗会追问 MCP 与 Skill 的区别、GRPO 去掉 KL 的条件、Agentic RL 的特点、两阶段后训练和 DAPO；全栈岗会追问超时熔断怎么结合硬预算和动态降级。社区生态方向还要准备审核、价值观对齐和业务评估。"
tags:
  - Xiaohongshu
  - 真题导航
  - "2026"
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书 大模型后训练一面
    url: https://www.nowcoder.com/discuss/872533899736334336
    type: candidate-first-hand
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
  - title: 小红书Hi lab 日常实习 一面
    url: https://www.nowcoder.com/feed/main/detail/8f02e3837274408d9c94c312e8ee578d
    type: candidate-first-hand
  - title: 小红书-Ai全栈开发二面面经
    url: https://www.nowcoder.com/feed/main/detail/b0aba5ebac994002a27bf0892b8991f9
    type: candidate-first-hand
---

小红书的公开面经同时覆盖社区 Agent、后训练算法和全栈稳定性。准备时我会把「Skill 为什么省 token」和「GRPO 为什么能弱化 KL」都讲到失败模式，光报定义不够。

比如一条复杂的 Agent 任务链跑到一半，某个工具迟迟不返回，面试官会问你是按硬规则直接熔断，还是让模型动态降级，下面第四条就是为这个准备的。

## 准备主线

1. Agent 协议方面，MCP 是连接协议，Skill 提供可以按需加载的操作知识。只在需要时展开相关内容，就能减少 token 占用。
2. Reasoning RL 要讲 GRPO 原理、去掉 KL 的条件和风险，以及 DAPO 相对 GRPO 改了什么。
3. Agentic RL 和普通 RL 的区别在于动作带工具副作用，观测有噪声，奖励稀疏，还有不可逆操作。
4. 系统护栏的做法是给复杂任务链设一个不能超出的时间预算，再在预算范围内动态降级。
5. 后训练链路要讲两阶段各自的目标、多轮数据怎么拆、训推怎么保持一致。

## 本手册真题卡

下面每条点进去就能跳到对应题。

- 小红书：MCP、Skill 有何区别，Skill 为什么能省 Token
- 小红书：复杂 Agent 任务链的超时熔断，应硬规则还是动态模型降级
- 小红书：GRPO 为何可以去掉 KL，Reward 怎么设
- 小红书：Agentic RL 与普通 RL 最大的不同是什么
- 小红书 Hi lab：两阶段后训练各自学什么
- 小红书：如何面向业务设计并评估 Agent
- 小红书：Credit assignment 怎么做
- 小红书 Hi lab：DAPO 相对 GRPO 优化了什么
- 小红书：MMKG-RAG 如何分块，实体和关系怎样抽取合并
- 小红书：Deep Research 多轮检索何时停止
- 小红书：了解 ReAct 结构吗
- 小红书 Hi lab：多轮训练数据怎么切，训推如何一致
- 小红书 Hi lab：如何保证问题能对应某个事实类答案
- 小红书秋招：检索增强生成（RAG） 有哪些短板，如何保证输出一致性
- 小红书：如何判断问题简单还是复杂，要不要换模型
- 小红书秋招一面：生成内容怎么评，具体如何操作？
- 小红书秋招：hallucination 怎么抑制，提示工程能做什么、不能做什么？
- 小红书秋招：如何保证多智能体协同的效果？
- 小红书 Hi lab：如何评估训练后的收益？搜索 top-k 该固定还是由模型选？
- 小红书后训练一面：审核标准如何自适应，还要跟谁对齐价值观？
- 小红书 Agent 一面：多员工同时用如何限流降级？多租户怎么理解？
