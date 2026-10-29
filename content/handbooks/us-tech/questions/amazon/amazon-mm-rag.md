---
id: amazon-mm-rag
section: amazon
order: 18
level: A
title: Amazon：图 / PDF RAG，OCR 和视觉检索怎么选？
quick: >-
  条款、表格和 ASIN 优先用 OCR / Textract 建文本索引；图表、版式和图标需要视觉检索。扫描页先 OCR，低置信度再走视觉，按 query
  与块类型选路。引用统一保留页码，视觉块还要带框。
tags:
  - Amazon
  - RAG
  - OCR
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Multimodal content in Amazon Bedrock Knowledge Bases
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html'
    type: primary
  - title: Amazon Textract
    url: 'https://docs.aws.amazon.com/textract/latest/dg/what-is.html'
    type: primary
  - title: What is Amazon Nova
    url: 'https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html'
    type: primary
  - title: Amazon Titan Text Embeddings V2 now available in Amazon Bedrock
    url: >-
      https://aws.amazon.com/blogs/aws/amazon-titan-text-v2-now-available-in-amazon-bedrock-optimized-for-improving-rag/
    type: secondary
---

我会按问题需要的是文字还是视觉信息选路。条款编号和表格字段优先 OCR / Textract 加文本索引；包装外观、图表和图标则用页图或多模态嵌入。比如问 `Section 4.2.1`，需要精确找字；问「这种包装算不算液体」，就需要看到像素。

公开 Knowledge Bases 有两类多模态路径：BDA / 解析器把图、音视频转成文本，Nova 多模态嵌入则保留图视频的原生表示做相似检索。Textract 适合表格和键值。Seller 政策、发票、包装图和扫描合同都可以接到 `amazon-bedrock-rag` 的检索流程里，但不能共用一种切块办法。

## 解析和检索按块类型处理

字面条款、报错码、ASIN 用 OCR、文本嵌入和 BM25。纯向量可能把 `Section 4.2.1` 匹配到另一个「第四节」，见 `amazon-kendra-hybrid`。表格尽量作为完整块保留，切碎后可能丢掉「仅危险品」这样的适用条件。表格读取优先用 Textract / 结构化结果，视觉用来校验，单靠读网格容易弄错数字。

包装或图标问题用页图检索，也可以把命中页送进 Nova，见 `amazon-nova-mm`。扫描件先 OCR，低置信度页再走视觉。BDA 的 OCR / 描述、音频转写和视频场景摘要适合「用话搜会议」，Nova 多模态嵌入适合「用图搜图」；纯视觉嵌入不能听懂语音内容。

一页上半是条款、下半是图时，可以按块拆开：文字进 BM25，图进多模态嵌入，命中后按页码拼回。只做 OCR 会丢流程图结构，只做视觉会漏编号；把 caption 当唯一索引又可能遗漏否定句。

## 引用、版本和延迟一起约束

文本块要有 `uri`、页码和文本 span，视觉块要有页码与框，生成的说法必须能指回 $E$。口播和点击打开的来源不一致就算 hallucination，这与 `apple-multimodal` 同类；Seller 控制台还应能直接打开源 PDF。

规模上，`amazon-bedrock-rag` 的 500 万 PDF 已会产生千万块，每页再加一张图嵌入会让索引翻倍。因此文本全量保留，视觉索引优先覆盖有图、扫描和无字页。两路都要带 marketplace、生效日期，过期条款依靠元数据作废，像素相似度不会处理时效。

检索含 rerank 的 p95 预算约 300 到 500ms，见 `amazon-rerank-llm`。生成只接 top 页的图或 Textract JSON，看清表格所需的信息即可，避免把 50 页 PNG 或整本 PDF 交给 Nova。身份证扫描进入 KB 要单独定策略；部分 Guardrails 对图是 text only，security constraints 见 `amazon-nova-mm`。

## 追问

**为什么不统一用多模态嵌入？**
标识符和否定条款仍然需要词法匹配。统一表示后也要保留精确检索能力。

**检索后一定需要视觉模型吗？**
命中内容是图时，生成模型要能看图，否则还需二次 OCR。模型路由见 `amazon-nova-mm`。

**PDF 更新怎么做？**
按文档 id 删除旧文本块与旧页图，再写入新内容。两路索引共用版本号，避免答案引用旧页。
