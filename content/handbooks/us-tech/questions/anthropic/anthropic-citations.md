---
id: anthropic-citations
section: anthropic
order: 22
level: A
title: Anthropic：引用接地怎么做，文档块和 span 对不上时该不该拒答？
quick: >-
  Citations 把回答关联到提供文档中的 span，但指针有效仍不代表论断被支持。合规 / 客服 RAG 应逐句检查事实与证据：缺引用或 span
  对不上时删去、补引，资料没有覆盖就明确拒答。文档块粒度按用户需要高亮的位置设置。
tags:
  - Anthropic
  - Citations
  - Grounding
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Citations (Claude Docs)
    url: 'https://platform.claude.com/docs/en/build-with-claude/citations'
    type: primary
  - title: Introducing Citations on the Anthropic API
    url: 'https://www.anthropic.com/news/introducing-citations-api'
    type: primary
---

需要事实有证据支持时，文档块和论断对不上就不应照常展示：能补正确引用就补，资料没有覆盖就说没有。Citations 保证引用落在提供的文档内，但「引用存在」和「这段原文支持这句话」仍是两件需要分别检查的事。

官方 API 在 document 上开启 `citations.enabled`，模型再给回答的 text 块附 span。它不会返回指向未提供文档的引用，`cited_text` 不计输出 token，也不计回传下一轮时的输入 token。相比让模型按 prompt 自由写页码，这减少了伪造位置与整段抄原文的开销。

## 把文档切到能核对的粒度

资料用 document 块送入，引用位置取决于内容类型：

| 类型 | 怎么切 | 引用长什么样 |
| --- | --- | --- |
| 纯文本 | 默认按句切 | 字符下标区间 |
| PDF | 抽文本再按句切 | 页码 + 句 |
| 自定义 content | 你给的块不再切 | 块下标 |

合同条款可按句引用；RAG 已按段切好时，可用 custom content 保留原块。若一块就是整章，用户只能看到「见第 3 章」，核验会很困难。扫描 PDF 没有文本时，也不能指望自动得到有效的页码引用。

同一请求中 citations 要全开或全关，图片目前不能引用。`title` / `context` 会进入模型却不能被引用，因此适合元数据和说明，需要作为证据的条款则放正文。

返回答案由多个 text 块组成，每块可以带 `citations`，每条记录 document 下标与位置。UI 可以按这些位置跳转，但还要抽查 span 是否支持相应事实，避免断章取义和夹带未引论断。

## 逐句决定展示还是拒答

有 citation 的事实句可以展示并链接原文，但仍要验证支持关系。没有 citation 的推理或「根据以上，风险在于……」，如果依赖资料事实，也应补引或删掉。资料外的事实问题则回答「提供的文档里没有」，避免用互联网记忆补齐或伪造 span。

合规、客服和法律 RAG 可以要求事实句无引不展示；头脑风暴可以允许发挥，但 UI 区分文档证据与模型生成。针不在文档里还自信回答属于诚实性失败，见 `anthropic-eval-honesty`、`anthropic-needle`。检索根本没召回相关段时，引用功能无法补救召回。

长资料可用 `anthropic-xml-prompt` 的 delimiters 减少 role confusion，citations 另外提供结构化引用。跨请求重复的大文档用 `anthropic-prompt-cache`，离线对账用 `anthropic-batch-api`。外部网页和文件仍是不可信数据，注入问题见 `anthropic-prompt-injection`。

官方内部评测称内置 citations 的引用召回高于多数自建 prompt 方案，仍需应用检查未引事实与错配 span。引用机制提供了可核验的位置，最终展示政策由产品定义。

## 追问

**citation 能证明没有 hallucination 吗？**
不能。它证明引用文字来自提供的文件，论断是否受支持还要另评。

**多份文档冲突呢？**
引用双方并明确指出冲突，评测加入矛盾文档，避免静默选一份。

**tool 检索怎么接？**
先检索，再把命中段作为 document 并开启 citations，让用户能分辨哪句话来自 tool 证据。
