---
id: cu-executable-goal-oracle
section: computer-use
order: 1
level: S
title: 开放式 Computer-use 任务，怎样写 Goal-state 的可执行 Oracle，而不是指定唯一 trajectory 或只让 LLM 当裁判？
quick: 把正确性写成初始状态、允许的终态和副作用断言，而不是点击序列。Oracle 要允许多条正确路径，同时检查关键数据、权限、外部写入与禁止状态；再用覆盖和误判测试验证 oracle 本身。
tags:
  - Computer-use
  - Evaluation
  - Oracle
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OSWorld
    url: https://arxiv.org/abs/2404.07972
    type: primary
---

可执行 oracle 从环境初始 fixture 开始，检查最终文件、数据库、浏览器/应用状态和允许的副作用。例如“完成报销”不应要求点击固定按钮，而应断言目标条目被创建、金额正确、无重复提交、敏感数据没有外泄。

把约束分成 must-hold、must-not-hold 与可选质量项；每项都应能被脚本、API 或环境状态读取。这样 agent 可采用不同合理路径，也避免 LLM judge 因措辞、长答案或观察不全误判。

oracle 也会错。为它维护人工验证样本、故意的 near-miss 负例和不同实现路径的正例，报告 oracle 的 false accept / false reject，而不是把评测脚本当作天然真值。
