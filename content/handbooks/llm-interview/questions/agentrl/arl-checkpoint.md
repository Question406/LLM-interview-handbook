---
id: arl-checkpoint
section: agentrl
order: 14
level: A
title: Agent State Checkpoint / Restore 怎么做？
quick: >-
  快照要同时存 Agent 的逻辑状态（任务进度、记忆与上下文摘要、工具结果）和外部环境（未完成事务、文件系统或容器快照、外部资源句柄），还要记策略和
  Harness 版本。不可逆副作用存事务 ID，恢复后先重查真相；状态对不上就标 dirty，别让模型接着猜。
tags:
  - Agent State
  - Reliability
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: LangGraph Persistence
    url: 'https://langchain-ai.github.io/langgraph/concepts/persistence/'
    type: primary
---

## 可以这样回答

比如一个浏览器 Agent 下单时进程崩了，重启后对话里写着「已提交订单」，可订单到底建没建成没人知道。模型接着往下走，要么重复下单，要么在不存在的订单上改地址。看起来像「接着聊」，其实 MDP 已经换了。所以常见的误区是把 checkpoint 当成 chatbot 的 session 序列化。生产 Agent 的持久化（比如 LangGraph thread checkpoint）存的是图状态和通道，和聊天记录副本是两回事。

字段再按恢复方式分三类，别整包 pickle 了事。可回放的纯观察，比如已经拉取的检索结果、只读 API 回包，存原文或内容哈希，恢复时直接喂回上下文。版本化产物，比如代码 diff、生成的文件、中间表格，存对象存储加内容哈希，恢复时 checkout 到同一个 commit 或目录树。不可逆副作用，比如已发的邮件、已扣的款、已删的数据，靠「再执行一遍」是恢复不了的，要记 durable transaction ID，恢复后重新 query 真相，别相信内存里那句「我发过了」。超时后不知道写操作有没有落地，也归这一类，下一步是查单，别 replay，见 `arl-retry`。Checkpoint 里要留 `UNKNOWN_SIDE_EFFECT` 和查询句柄，不然恢复的进程会双发。

## 技术备查

快照要同时存两样东西：Agent 的逻辑状态和外部世界的句柄，再加上策略和 harness 的版本，写成式子就是 $(s_t, \text{handles}, \text{versions})$。只存对话文本不够，恢复后文件系统可能已经变了、网页 session 过期了、事务状态未知，Agent 会照着过时的状态继续干活。

比如一个浏览器 Agent 下单时进程崩了，重启后对话里写着「已提交订单」，可订单到底建没建成没人知道。模型接着往下走，要么重复下单，要么在不存在的订单上改地址。看起来像「接着聊」，其实 MDP 已经换了。所以常见的误区是把 checkpoint 当成 chatbot 的 session 序列化。生产 Agent 的持久化（比如 LangGraph thread checkpoint）存的是图状态和通道，和聊天记录副本是两回事。

## 同时保存逻辑状态和外部环境

逻辑状态包括任务目标与约束、当前 plan / 子目标、memory 或 context summary、已确认的 tool 结果、待澄清的问题、策略与 harness 版本。外部世界句柄包括工作目录或容器 snapshot、浏览器 cookie / tab、数据库事务或订单 ID、打开的文件锁、没完成的异步 job。缺了哪一类，restore 后 observation 都会和真实世界对不上。版本也要进快照：模型、工具的字段和类型规范（schema）、提示、权限集一变，旧轨迹里的 action 可能就不合法了。这和 `arl-environment-reset` 是同一个前提，$s_t$ 没定义清楚，后面的奖励就没有意义。

字段再按恢复方式分三类，别整包 pickle 了事。可回放的纯观察，比如已经拉取的检索结果、只读 API 回包，存原文或内容哈希，恢复时直接喂回上下文。版本化产物，比如代码 diff、生成的文件、中间表格，存对象存储加内容哈希，恢复时 checkout 到同一个 commit 或目录树。不可逆副作用，比如已发的邮件、已扣的款、已删的数据，靠「再执行一遍」是恢复不了的，要记 durable transaction ID，恢复后重新 query 真相，别相信内存里那句「我发过了」。超时后不知道写操作有没有落地，也归这一类，下一步是查单，别 replay，见 `arl-retry`。Checkpoint 里要留 `UNKNOWN_SIDE_EFFECT` 和查询句柄，不然恢复的进程会双发。

## 恢复时先核对环境，再让策略继续

我的恢复顺序是：加载 harness 版本，恢复文件系统 / 容器，用事务 ID 刷新外部真相，校验逻辑状态和观察是否一致，最后才让策略继续生成。对不上就停下来标 dirty，别让模型去猜世界还是不是原来那样，也别在不一致的状态上继续优化。长任务还要能从任意 tool boundaries 恢复，只在用户回合存一次不够，因为崩溃往往发生在工具执行中间。评测时可以注入几种情况：恢复后目录哈希变了、session 过期、事务其实已经成功了，看 Agent 是先查状态，还是盲目接着点。

## 追问

**只存 conversation 会出什么问题？**
文本里说「文件已写」，磁盘上没有，或者写的是另一份，后续动作就会改错对象。逻辑和世界要一起恢复。

**训练中要不要做 checkpoint？**
可以做。长 horizon 的 sampling 轨迹（rollout）崩了重跑很贵，可以在 tool boundaries 做可恢复快照；但脏恢复的轨迹要丢掉，别当 on-policy 样本。

**和 reset 有什么区别？**
Reset 定义 $p(s_0)$，checkpoint 保存任意 $s_t$，一个用于开局，一个用于续跑。两者都要能断言世界哈希。

**多 Agent 怎么存？**
共享黑板只存验证过的字段，各自的 scratch 分开。恢复后先对齐共享状态的版本，再让工人继续，见 `arl-multiagent`。
