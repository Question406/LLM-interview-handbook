---
id: cu-reproducible-benchmark-run
section: computer-use
order: 2
level: S
title: 云服务、网页和 GUI 都会变化：怎样发布一条可复现、可比较的 Computer-use benchmark run？
quick: 版本化的不只是模型。锁定 VM / 容器、账号与 fixture、任务资产、外部服务 mock、harness、模型快照、seed、动作/时间预算；保存 trace 和环境版本，并多次重跑报告方差。
tags:
  - Benchmark
  - Reproducibility
  - Computer-use
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OSWorld-V2
    url: https://github.com/xlang-ai/OSWorld-V2
    type: primary
---

真实 GUI 环境会因页面改版、登录态、网络、DPI、时钟和后台任务漂移。一个 benchmark run 应标出 task ID 与版本、初始 snapshot、容器/VM image digest、账户 fixture、外部 API mock、浏览器/工具版本，以及模型、prompt、tool schema、sampling seed 与完整 budget。

每次执行保存 observation、action、tool result、屏幕/DOM checkpoint、oracle 结果和失败原因。对有随机性的环境至少多次重跑，报告均值、方差和超时率；否则一个看似提升的百分点可能只是环境噪声。

线上 live benchmark 可以反映新鲜性，但不能与冻结 leaderboard 混在同一数字中。应分别报告 frozen reproducible score 与 live robustness score。
