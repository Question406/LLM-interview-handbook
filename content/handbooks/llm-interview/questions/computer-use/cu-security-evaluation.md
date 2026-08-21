---
id: cu-security-evaluation
section: computer-use
order: 4
level: A
title: 怎样设计同时衡量 utility、attack success、未授权状态改变和数据外泄的 Agent 安全评测？
quick: 将正常任务与注入/越权对抗任务成对设计，用 allow / deny state invariants 判断结果；同时报告任务效用、攻击成功率、未授权写入和数据外泄，而不是只报「拦截率」。
tags:
  - Agent Security
  - Evaluation
  - Prompt Injection
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Agent Security Bench
    url: https://arxiv.org/abs/2406.13352
    type: primary
---

只塞一句恶意文本再问「模型拒没拒」，测的是口头安全，不是 Agent 安全。Computer-use 的危害发生在环境副作用上：该买的没买、不该转的转了、秘密进了聊天或外发邮件。面试官要听成对任务、状态不变量、以及 utility–security 一起报，而不是一个拦截率。策略若把正常任务全部拒绝，拦截率可以很高但没有产品价值。

## 成对任务与不变量

为每个真实任务做正常版和攻击版，共享同一初始 fixture。先写清 allow / deny：哪些字段可读、哪些工具可调、哪些状态绝不能变（支付、权限、删除、外发）。攻击覆盖间接注入（网页 / 文档 / 邮件）、恶意 UI（看起来像系统对话框）、tool output 注入、多步组合（先骗读 secret，再骗外发）。Oracle 检查最终副作用，而不是检查模型有没有说「我拒绝」。Canary secret 预先埋进文件、页面或邮件，出现在消息、下载或出站请求都算泄漏。没有 canary 就无法测外泄，只能测「嘴上硬不硬」。

## 指标怎么报

至少四列，禁止合成一个「安全分」：正常任务成功率（utility）；attack success rate（仅当攻击者目标在环境里成真）；敏感字段 / canary 外泄率；未授权写入 / 购买 / 删除率。另报人工升级率与拒答过度率。必须画 utility–security 权衡。每条失败保留 trace，能回答攻击穿过了观察、规划、工具策略还是 oracle 盲区。ASR 的分母是攻击任务数，不是「模型没拒绝的次数」。记录字段：任务对 ID、攻击类型、是否发生 deny-state 违反、canary 出现位置、用户是否被升级。

## 可被刷与过时

可被刷的点：只用直接「忽略之前的指令」；攻击与工具权限不匹配（根本调不到支付就报拦截成功）；不放 canary；把「模型说已拒绝」当成功，但后台请求已发出；用过时攻击集刷防御论文。防御迭代后攻击集必须更新，否则是在刷旧题。安全 eval 是持续合同：冻结 benign 集做回归，对抗集随威胁模型版本化。面试口径：安全成功 = 攻击目标未在环境中达成 ∧ 正常任务仍能完成；只报拦截率是在回避权衡。把成对任务、canary、deny-state 写成与功能测试同级的 CI。防御合并后要重跑攻击集版本号，否则你在回归旧招。现场能讲清「攻击成功的环境定义」，比讲模型拒答话术更像安全评测。utility 与 ASR 必须同一次发布出数：只优化其中一边，另一边会在下个迭代爆掉。把这条 Pareto 画进评测报告，比给安全一个单独的红绿灯更诚实。

攻击集版本号与防御版本号一起发布。每次只改防御或只改攻击时，另一侧必须重跑。Canary 外泄位置（聊天、文件、HTTP）要分列，否则无法判断该挡模型、挡工具还是挡网络。

面试官要听成对任务和副作用 oracle，而不是拒答率。能说明 ASR 何时算成功、canary 埋在哪、utility 如何一起报，安全评测才站得住。拦截率单独出现就是红旗。

## 追问

- **ASR 的分母是什么？** 是攻击任务数，且仅当攻击者目标在环境里成真才算成功，不是模型没拒绝。
- **为什么要 canary secret？** 没有标记数据就无法测外泄；canary 出现在消息、文件、网络请求都算泄漏。
- **和 executable oracle 怎么接？** 安全不变量就是 deny-state oracle；utility 是 must-hold oracle。同一套状态检查，标签不同。
- **只测直接注入够吗？** 不够。间接注入、恶意文档和 tool output 才是 Computer-use 的主威胁，直接「忽略指令」只能当最弱的烟雾测试，不能当安全结论。
