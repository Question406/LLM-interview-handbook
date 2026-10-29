---
id: p3a-openai-design-chess-game
section: openai
order: 633
level: A
title: "OpenAI：在线国际象棋：匹配、走子和权威时钟"
quick: "每盘棋由服务端一个权威状态机串行处理走子和棋钟，成功提交后递增版本，并向两端推送。比如断线重连带 last_seen_version 补事件；重复走子按 client_move_id 去重，处理器切换靠租约和 fencing epoch 防止双写。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · design-chess-game"
    url: https://www.1point3acres.com/interview/problems/company/openai/design-chess-game
    type: secondary
---

我会给每盘棋一个服务端权威状态机，让走子合法性、棋钟和终局都在那里裁决。比如白方在 version 12 走 e4，服务端验证、扣时并提交 version 13 后再推给双方，两端就有同一个局面和计时起点。

这道题按一百万在线连接、同时十万局设计，需要实时对弈、评级匹配、断线恢复和权威棋钟。开始时确认是否观战、悔棋和支持哪些时间规则。网关维持 WebSocket，按 game id 路由权威处理器；匹配池按评级找对手，等待越久，允许的评级范围越大。事件日志与定期快照用于故障恢复。

game 保存 FEN、`side_to_move`、version、双方剩余时长和上次确认走子的服务端时间，move 保存 game、version 和 `client_move_id`。客户端发送 `(game, version=12, client_move_id, e2e4)` 后，处理器确认轮次和着法，用单调时钟算白方用时，扣掉后写日志、推进版本并推送；黑方从这次提交的服务端时间开始计时。

同一 version 只接收一次合法走子，重复 `client_move_id` 返回原结果。进程崩溃后从快照加日志重放，重连先补 `last_seen_version` 之后的事件，再恢复推送。棋钟只记录事件间的时间差，走子和超时才落库，不必每秒写数据库。容量按连接数和每局平均走子频率估算，监控权威提交时延、重连成功率和超时争议数。

## 追问

**两台服务器都认为自己管理同一盘棋怎么办？**
用租约加 fencing epoch。接管拿更大 epoch，存储只接受当前 epoch 的写入，负载均衡本身无法保证单权威。

**最后一秒走子和超时同时发生，听谁的？**
听权威处理器的服务端时钟。到达时已耗尽就判超时，否则接受；两种事件在同一状态机串行处理，不会同时成立。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。
