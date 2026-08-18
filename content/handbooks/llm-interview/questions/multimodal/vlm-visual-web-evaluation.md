---
id: vlm-visual-web-evaluation
section: multimodal
order: 3
level: A
title: 怎样把视觉 Web Agent 的评测拆为 OCR、icon / layout、visual reference、image matching 与端到端 web execution，避免一个 success rate 掩盖能力缺口？
quick: 用能力分桶和逐层指标：感知正确率、元素 grounding、动作有效率、任务成功率；再按是否依赖视觉信息做文本/视觉消融。端到端失败必须能回溯到具体视觉能力，而非只报总分。
tags:
  - VisualWebArena
  - Evaluation
  - VLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: VisualWebArena
    url: https://arxiv.org/abs/2401.13649
    type: primary
---

先按任务的视觉依赖分桶：文字 OCR、图标/布局理解、图片属性匹配、视觉 referential grounding、跨页面状态判断。每个桶配独立 oracle，例如文本读取准确率、目标元素定位、图片匹配准确率与 action validity。

做文本观察、截图观察、二者结合的消融。若加视觉后端到端分数不涨，要看是视觉编码器没有读到关键信息、planner 没有使用它，还是执行器没有把 visual target 转为正确 action。

不要让自动 judge 只看最终自然语言说明。网页任务应检查实际状态与副作用，并报告每层指标与跨域泛化，才能知道应该修数据、视觉模型还是 Agent loop。
