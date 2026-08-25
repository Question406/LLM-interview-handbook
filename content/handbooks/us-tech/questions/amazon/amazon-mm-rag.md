---
id: amazon-mm-rag
section: amazon
order: 18
level: A
title: Amazon：图 / PDF RAG，OCR 和视觉检索怎么选？
quick: >-
  条款、表格、ASIN 用 OCR / Textract 进文本索引，词法能打中。图表、版式、商标、扫描件用多模态嵌入或页图检索。混合不是每页都跑两遍大模型：query
  类型决定走哪路，引用要带页码和框。别把整本 PDF 当一张图塞进 Nova。
tags:
  - Amazon
  - RAG
  - OCR
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Multimodal content in Amazon Bedrock Knowledge Bases
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-multimodal.html
    type: primary
  - title: Amazon Textract
    url: https://docs.aws.amazon.com/textract/latest/dg/what-is.html
    type: primary
  - title: What is Amazon Nova
    url: https://docs.aws.amazon.com/nova/latest/userguide/what-is-nova.html
    type: primary
  - title: Amazon Titan Text Embeddings V2 now available in Amazon Bedrock
    url: https://aws.amazon.com/blogs/aws/amazon-titan-text-v2-now-available-in-amazon-bedrock-optimized-for-improving-rag/
    type: secondary
---

Seller 政策、发票、包装图、扫描合同会把 `amazon-bedrock-rag` 从「切文本块」推进到图。公开 Knowledge Bases 多模态路径大致两种：BDA / 解析器把图和音视频 **转成文本**；Nova 多模态嵌入把图视频 **留在原生空间** 做相似检索。Textract 仍是表和键值的老本行。不是逐字真题。

## OCR 赢在字，视觉赢在样子

Query 先分类，不要每页双路都打满：

- **字面条款、编号、报错码、ASIN。** OCR + 文本嵌入 + BM25。向量单独很容易把 `Section 4.2.1` 吸到别的「第四节」，见 `amazon-kendra-hybrid`。表要尽量整表进一块，切碎就丢「仅危险品」。
- **「这种包装算不算液体」「图里的图标是什么」。** 文本索引没有像素。用页图 / 多模态嵌入，或把该页当图送给 Nova，见 `amazon-nova-mm`。
- **扫描件。** 先 OCR；置信度低的页再走视觉。全库当图嵌入贵，也检索不准条款编号。

BDA 公开叙事：图做 OCR / 描述，音频转写，视频出场景摘要。适合「用话搜会议」。Nova 多模态嵌入适合「用图搜图」。语音内容不要指望纯视觉嵌入听懂，文档也写了这条。

引用契约：文本块给 `uri` + 页码 + 文本 span；视觉块给页码 + 框。生成必须能指回 $E$。口播和点击不一致算幻觉，和 `apple-multimodal` 同构，Amazon 侧还要能在 Seller 控制台点开源 PDF。

## 索引和延迟

500 万 PDF 在 `amazon-bedrock-rag` 已是千万块。每页再存一张图嵌入，索引翻倍。做法：文本块全量；图嵌入只对「有图 / 扫描 / 无字」页。元数据仍要 marketplace、生效日期。过期靠元数据作废，像素相似不会自己过期。

p95 预算：检索 300–500ms 量级含 rerank，见 `amazon-rerank-llm`；生成不要塞整页像素。需要看清表时，只把 top 页的图或 Textract JSON 进 prompt，不要 50 页 PNG。

错法：只 OCR，流程图全瞎；只视觉检索，条款编号全丢；用 caption 模型给每页写一段散文当唯一索引——散文会丢否定句。安全：身份证扫描进 KB 要单独策略，Guardrails 对图可能是 text only，见 `amazon-nova-mm`。

混排页（上半条款、下半图）按块类型拆：文字进 BM25，图进多模态嵌入，检索后按页码拼回。生成只看 top 页，避免整本 PDF 像素进 Nova。路由见 `amazon-nova-mm`。引用必须带页码；视觉块还要框。口播和点击对不上算幻觉。

引用必须带页码；视觉块还要框。口播和点击对不上算幻觉。混排页按块类型拆，不要整页当一种模态。

面试收尾主动报失败模式和评测切片，不要停在架构名词。

收尾把失败案例写进评测集，不要只改 prompt。

生成侧只喂 top 页，避免整本像素进上下文。

## 追问

- **为什么不统一用多模态嵌入？** 标识符和否定条款仍是词法问题。统一空间省架构，不省 ASIN。
- **生成还要视觉模型吗？** 检索到的若是图，生成模型必须能看图，否则又要二次 OCR。路由见 `amazon-nova-mm`。
- **表格？** 优先 Textract / 结构化；视觉当校验。只视觉读网格，数字容易自信地错。
- **更新？** 日更 PDF 按文档 id 删旧文本块和旧页图再写。两路索引要同一版本号，否则引用指到旧页。
