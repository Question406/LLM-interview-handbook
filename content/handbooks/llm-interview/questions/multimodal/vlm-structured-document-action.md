---
id: vlm-structured-document-action
section: multimodal
order: 4
level: A
title: 表格、发票、PDF 和图表进入 Visual Agent 后，如何从视觉解析一路建立到可验证的结构化 action？
quick: 先抽取带 provenance 的结构化字段，而不是直接让模型写入系统。保留页码/bbox/单元格来源和置信度，用 schema、算术约束与原文交叉验证；低置信度或高风险写入必须转人工确认。
tags:
  - Document AI
  - VLM
  - Grounding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: DocLayNet
    url: https://arxiv.org/abs/2502.13923
    type: primary
---

文档任务应分层：layout / reading order，表格单元格或图表元素 grounding，字段抽取，业务 schema 映射，最后才是工具 action。每个输出字段带页码、bbox、原文片段和置信度，便于审计与人工复核。

执行前做格式、类型、合计/日期/币种等规则检查，并用独立 OCR/解析器或检索证据交叉验证。对于“写入财务系统”这类不可逆动作，字段 provenance 比流畅的自然语言解释更重要。

评测分别衡量 layout、field F1、provenance correctness、schema validity、business action success 和高风险误写率。只看最终表单提交成功会掩盖错误但格式合法的内容。
