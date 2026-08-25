---
id: anthropic-citations
section: anthropic
order: 22
level: A
title: Anthropic：引用接地怎么做，文档块和 span 对不上时该不该拒答？
quick: >-
  Citations 把文档切成可引用单元，回答里每个论断带指向你提供文档的 span。指针保证落在给定资料里，不保证论断为真。事实必须接地时：没有
  citation 就拒答或标「资料未覆盖」。不要用模型编一个看起来像的页码。
tags:
  - Anthropic
  - Citations
  - Grounding
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Citations (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/citations
    type: primary
  - title: Introducing Citations on the Anthropic API
    url: https://www.anthropic.com/news/introducing-citations-api
    type: primary
---

企业检索岗会问：怎么让 Claude 的答案能点回原文，而不是 prompt 里求「请列出出处」然后自己编页码。官方 Citations：在 document 块上开 `citations.enabled`，模型在文本块上附 span。Cookbook 写过：API 不会返回指向未提供文档的引用；`cited_text` 不计入输出 token。题是产品接地，不是隐藏面经。

## 块和 span 是什么

资料以 document 进上下文，不是糊进一段 user 散文。三种切法：

| 类型 | 怎么切 | 引用长什么样 |
| --- | --- | --- |
| 纯文本 | 默认按句切 | 字符下标区间 |
| PDF | 抽文本再按句切 | 页码 + 句 |
| 自定义 content | 你给的块不再切 | 块下标 |

粒度是产品选择：按句引用适合合同条款；RAG 已经按段切好，就用 custom content，避免再切碎。同一请求里 citations 必须全开或全关。图片目前不能引。`title` / `context` 会进模型但**不能被引**——适合放元数据或「不要当原文引用的说明」。

返回形状：一个回答拆成多个 text 块，每块可选带 `citations`。每条 citation 有 document 下标和位置。`cited_text` 是方便字段，回传入下一轮时也不计入输入 token。这比让模型在输出里抄整段原文便宜，也少一层「引文是不是模型编的」。

指针保证：落在你提供的 document 里。不保证：论断被这段话真正支持（断章取义）、也没有未引用的幻觉句。所以接地政策是产品的，不是 API 的。

## 无法引用时该拒答

我会把回答里的句子分成三类：

1. **有 citation 的经验句。** 可以展示，UI 链回原文。上线前建议抽查：span 文本是否真支持该句。
2. **无 citation 的推理 / 寒暄。** 「根据以上，风险在于…」若仍依赖资料事实，要么补引，要么删。
3. **资料覆盖不了的事实问题。** 明确说「提供的文档里没有」，不要补互联网记忆，也不要伪造 span。

产品开关：合规 / 客服 / 法律 RAG 用「无引则不说」；头脑风暴可以允许无引，但 UI 要区分「来自文档」和「模型发挥」。评测诚实性时，针不在文档里却仍自信作答，算失败，见 `anthropic-eval-honesty` 和 `anthropic-needle`。

Prompt 求引用的老办法：模型会编页码、把两段拼成一句假引文。API 路径至少堵死「指向不存在的位置」。仍要自己挡：未引论断、错配 span。检索层没召回相关段，citations 救不了——那是 RAG 召回问题。

## 和 XML、缓存、批处理

长资料仍可用 `anthropic-xml-prompt` 那种 documents 边界减少串角色；citations 是额外的结构化接地，不是标签的替代。Document 很大、跨请求复用，前缀打 `anthropic-prompt-cache`。离线对账用 `anthropic-batch-api`。不要把网页全文当已授权资料：注入见 `anthropic-prompt-injection`，外部文档零信任。

错法：只开 citations 却把无引句子原样给用户；用 `context` 塞进真正要引的条款（引不到）；扫描件 PDF 无文本还指望页码引用。

官方博文给过内部评测：内置 citations 比多数自建 prompt 引用召回更高，且摘录文本不计输出价。这仍不是「论断为真」的证明。合规场景我会加一层：无 citation 的事实句丢掉或改写成「文档未覆盖」。

官方博文给过内部评测：内置 citations 比多数自建 prompt 引用召回更高，且 `cited_text` 不计输出价。这仍不是「论断为真」的证明。合规场景我会加一层：无 citation 的事实句直接丢掉或改写为「文档未覆盖」。

## 追问

- **citation 能否证明没幻觉？** 不能。只能证明「这段字来自你给的文件」。支持关系要另评或抽查。
- **多文档打架怎么办？** 让模型引双方并说冲突，不要静默挑一段。评测要有矛盾文档集。
- **自定义块切太大？** 一块整章，引用粒度变成「见第 3 章」，用户没法核。块要接近你希望高亮的单位。
- **和 tool 检索怎么接？** 先检索再把命中段当 document 打开 citations。不要让模型既搜又自由发挥还不标哪句来自 tool 结果。
