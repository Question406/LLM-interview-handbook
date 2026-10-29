---
id: vlm-structured-document-action
section: multimodal
order: 4
level: A
title: 表格、发票、PDF 和图表进入 Visual Agent 后，如何从视觉解析一路建立到可验证的结构化 action？
quick: >-
  分层走：先抽取带来源信息（provenance）的结构化字段，保留页码、bbox、单元格来源和置信度；通过
  schema、算术约束和原文交叉验证后，才生成写入动作。低置信度或高风险的写入转人工确认。
tags:
  - Document AI
  - VLM
  - Grounding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: DocLayNet
    url: 'https://arxiv.org/abs/2502.13923'
    type: primary
---

要分层走：先抽取带来源信息（provenance）的结构化字段，每个字段带页码、bbox 或单元格坐标、原文片段和置信度；再按字段和类型规范（schema）、算术约束和原文做交叉验证；都通过了才生成写入动作。低置信或高风险的写入转人工，Agent 最多提交一份带证据包的草稿。

文档 Agent 最危险的一步，是把流畅的自然语言直接变成财务写入。比如发票看错一行，把注释里的金额当成应付，合计对不上，生成的 JSON 格式却完全合法，直接过账就错了。解释性文字点不回像素，bbox 才能让人在 PDF 上复核，所以 provenance 比解释重要。DocLayNet 一类 layout 数据解决的是版面，离「直接过账」还差好几层。

流水线按顺序是 layout / reading order → 表格单元格或图表元素 grounding → 字段抽取 → 业务 schema 映射 → 工具调用，别端到端直接写库。没有 provenance 的数字不许进入不可逆的 action。图表要分清视觉编码（柱高、图例颜色）和读出来的数值，并保留取数位置，免得「看起来是 30%」写进去成了 3%。多页 PDF 要带页码，不然同行错位没法审计。每个字段记一个 provenance hash，抽检时能跳回原件，别光存模型生成的 JSON。

写入前检查类型、必填、币种、日期、税率和合计等式，再用独立的 OCR / 解析器或检索到的原文交叉验证。两边冲突就走人工，别挑模型更自信的那边。合计等式失败要阻塞写入、标出冲突字段，不能静默四舍五入凑平。放行可以按字段来：低置信或校验失败的字段留空转人工，其它字段先写草稿，但不许为了完成率让模型猜着填平。低置信的字段格式再合法，也不能自动过账。创建付款、改主数据、发邮件这些动作单独确认，日志记下校验器通过了哪些、哪些冲突、最终是谁批准的写入。

评测光看提交成功不够，「金额合法但张冠李戴」会被放过去。要分别衡量 layout / 单元格 grounding、字段 F1、provenance 是否指向真正的原文、schema validity、业务 action 成功率、高风险误写率。误写率按金额加权，大额错误不能被一堆正确的小字段平均掉。容易误导的做法有：合成的表结构极规整；oracle 不查合计约束；用 LLM 判断抽取文本「像不像」；负例里缺近邻行错位、页眉页脚当正文、多币种、扫描倾斜。评测集要包含合计冲突和近邻行错位，误写率单独报。

上线清单固定下来就是字段 schema、provenance 必填、合计等式、独立解析器交叉验证、高风险人工 acceptance checks、误写率。缺 provenance 的 JSON 只配当草稿，不配过账。模型读错一行时，阻止写入、回到原件复核，再生成一段解释没用。一句话总结，「读 PDF」和「写财务系统」要拆开。

## 追问

**和 GUI oracle 的差别在哪？**
文档这边的终态是结构化记录加证据链，GUI 那边更多是应用状态和副作用。

**OCR 和 VLM 谁当主抽取？**
两者交叉验证，不一致就转人工。别让同一个模型既抽取又当裁判，否则 provenance 会变成没法复核的自我证明，抽检也失去落点。
