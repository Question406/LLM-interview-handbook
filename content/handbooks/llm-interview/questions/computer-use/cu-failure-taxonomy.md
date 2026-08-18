---
id: cu-failure-taxonomy
section: computer-use
order: 3
level: A
title: Computer-use Agent 失败后，怎样定量归因到 visual grounding、OCR / 感知、planning、action execution 或 environment，而不是笼统说模型差？
quick: 用带 checkpoint 的 trace 和能力 microbench 分层。先判断观察是否读错，再判断计划是否错、动作是否执行错或环境是否异常；记录第一个不可恢复错误及其后续传播，按类别和任务难度聚合。
tags:
  - Failure Analysis
  - GUI Agent
  - Observability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: SeeAct
    url: https://arxiv.org/abs/2401.10935
    type: primary
---

把一次 run 切成 observation、state interpretation、plan、action grounding、execution verification 五层。OCR 读错金额、看对了却选错目标、规划正确但坐标因滚动失效、工具点击成功却环境未提交，修复路径完全不同。

trace 要在每个关键 step 记录截图/DOM/可访问性树、模型观察摘要、候选 action、实际 action、执行回执和 checkpoint。标注 first failure，避免把后续连锁失败都归为根因。

再用独立 microbench 测 OCR、图标识别、元素定位、状态转换和长程规划。端到端 success rate 只适合验收，不足以指导模型、harness 或环境的改进优先级。
