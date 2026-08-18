---
id: cu-security-evaluation
section: computer-use
order: 4
level: A
title: 怎样设计同时衡量 utility、attack success、未授权状态改变和数据外泄的 Agent 安全评测？
quick: 将正常任务与注入/越权对抗任务成对设计，用 allow / deny state invariants 判断结果；同时报告任务效用、攻击成功率、未授权写入和数据外泄，而不是只报“拦截率”。
tags:
  - Agent Security
  - Evaluation
  - Prompt Injection
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Agent Security Bench
    url: https://arxiv.org/abs/2406.13352
    type: primary
---

安全 eval 不能只放恶意文本并问“模型有没有拒绝”。为每个真实任务建立正常版本和攻击版本，明确哪些数据允许读取、哪些工具允许调用、哪些状态绝不能改变，并用环境 oracle 检查最终副作用。

核心指标至少包括正常任务成功率、attack success rate、敏感字段/秘密外泄率、未经授权的写入/购买/删除率和人工升级率。安全策略若把正常任务全部拒绝，拦截率高也没有价值，因此要画 utility–security Pareto。

攻击应覆盖间接注入、恶意网页/文档、tool output 注入和多步骤组合，并随 agent 的防御迭代更新。最终需保留 trace，能回答“攻击穿透了哪个边界”。
