---
id: design-mm-rag
section: design
order: 21
level: A
title: 设计：多模态 RAG——图向量、文本与 ACL
quick: >-
  文本块和图像 / 页级视觉内容分路索引，查询按模态选择编码塔，再融合检索结果。所有路径都先按
  ACL、生效状态等元数据过滤，引用指回文档、页和区域；更新时同步作废旧向量，查询图默认不进入共享索引。
tags:
  - RAG
  - Multimodal
  - Google
  - Amazon
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Learning Transferable Visual Models From Natural Language Supervision
    url: 'https://arxiv.org/abs/2103.00020'
    type: primary
  - title: ColPali — Efficient Document Retrieval with Vision Language Models
    url: 'https://arxiv.org/abs/2407.01449'
    type: primary
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: 'https://arxiv.org/abs/2005.11401'
    type: primary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

为含文字、图表、截图和扫描 PDF 的企业资料库设计检索增强问答。查询既可能描述文本事实，也可能描述图片的颜色、布局或某个区域。

### 需要满足的功能

- 接收问题、用户身份与资料范围，返回相关证据及有依据的答案。
- 证据需能够定位到文档、页码和必要的图像区域。
- 支持资料更新、扫描件文字不完整、跨模态证据和无答案情况。

### 约束与交付物

所有模态都遵守同一套权限和有效期要求，不能因图像相似而跨租户取证。需要明确召回质量、引用准确性、视觉 token、延迟和成本的评测约束。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

用户查“合同里带红色标识的那页”，结果应指出其有权查看的文档与页码；另一个租户的相似页面即使命中，也不能作为可见结果或答案证据。

## 可以这样回答

我会把文本检索和图像 / 页级视觉检索分路建索引，查询时先做 ACL 和作废过滤，再融合结果。比如用户找「红色 logo 的那页」，图像向量能补文字检索；但相似的另一租户合同即使命中，也不能进入上下文。CLIP 提供图文对齐空间，ColPali 一类方法支持页级视觉文档检索。

Google 企业搜、Amazon Bedrock 知识库、Meta 工作问答接入截屏和 PDF 扫描件时，都需要从 `design-prod-rag` 扩展到这层设计。生成侧的引用框见 `design-mm-assistant`。

## 技术备查

## 解题思路与参考答案

我会把文本检索和图像 / 页级视觉检索分路建索引，查询时先做 ACL 和作废过滤，再融合结果。比如用户找「红色 logo 的那页」，图像向量能补文字检索；但相似的另一租户合同即使命中，也不能进入上下文。CLIP 提供图文对齐空间，ColPali 一类方法支持页级视觉文档检索。

Google 企业搜、Amazon Bedrock 知识库、Meta 工作问答接入截屏和 PDF 扫描件时，都需要从 `design-prod-rag` 扩展到这层设计。生成侧的引用框见 `design-mm-assistant`。

## 切片和建索引时绑定权限

我会先问：PDF 是原生文字还是扫描、要不要区域引用、租户 / ACL、更新频率、p95。扫描件没有好文字时，纯 BM25 很难检索到有效内容。但仍按文档结构切：页、图、表，元数据绑 `doc_id`、页码、`bbox`、生效/作废、`acl_groups`。存在性泄漏同样算事故：无权限用户不该靠「图像检索有结果 vs 空」探测合同在不在。

索引建议三路，按预算裁：

1. **文本。** OCR / 原生文字 + BM25 + dense。表格保留表头副本。
2. **图级 CLIP / SigLIP。** 查询是「红色 logo 的那页」时，文字塔对不上。
3. **页级视觉检索（ColPali 一类）。** 版式、印章、手写，OCR 丢的信号在这里。

过滤必须在 ANN 之前或走支持预过滤的引擎：`acl ∩ 未作废 ∩ 语言`，再向量。把无权限页的像素打进上下文，再靠 prompt「请忽略」，等于已经泄漏。缩略图、缓存 CDN、日志里的图 URL 都要过同一 ACL。

```python
def mm_retrieve(q, user, q_image=None):
    f = {"acl": acl_groups(user), "expired": False}
    text_hits = hybrid_search(q, filters=f, k=50)
    vis_hits = image_search(q_image or text_tower(q), filters=f, k=50)
    return rrf(text_hits, vis_hits)[:20]
```

embedding 升级双写，按 `doc_id` 切流。图模型和文本模型版本都要钉在报告里，混排不可比。

## 融合、引用和 token 预算

融合用倒数排名（RRF）即可，权重用标注集扫，不要口头保证「视觉一定赢关键词」。查询带图时（以图搜页）走图像塔；纯文字走文本塔 + 用文字塔查图向量（CLIP 的对齐空间）。搜到页之后，生成不要整页高清塞进上下文：先 OCR 摘要 + 低分辨率，再把引用框对应的区域裁成高清图，见 `design-mm-assistant`。一页图可以是几千 visual token，可能挤占对话历史的上下文预算。

引用：`doc_id` + 页 + `bbox`。对不上就删句。过期页用元数据挡，不要指望向量「自己过期」。图更新（换了合同扫描件）要按版本作废旧向量，和文本同一套。

失败模式：OCR 把印章日期读错，生成信了 OCR 而没看图；视觉检索命中相似但不该看的租户水印页；ACL 漏了就是事故；把用户上传的截屏写进共享索引；审核没扫图就进库，有害图当知识，见 `align-mm-harm`、`design-moderation`。p95 拆：OCR、三路检索、重排、生成。视觉超时当该模态缺失，不许拿过期缓存图当本页。

企业场景 Amazon / Google 还会问：同一 `doc_id` 的图和文字权限必须一致；图更「好看」不能成为绕过 ACL 的理由。评测集要含：纯文能答、必须看图、图文冲突、无权限探测、扫描件无 OCR。不要用 BLEU。

## 追问

**只有 CLIP 够不够？**
图搜图、粗召回够用；版式密集的文档页往往要页级视觉检索或强 OCR。
**为什么不把每页只存一个向量？**
区域引用和表格局部对不上。页向量召回，框在生成或二次定位。
**用户图当查询会不会进别人的索引？**
查询图默认不入库。要入库必须走同一 ACL 和留存期。
**和文本 RAG 哪条绝对不能省？**
预过滤 ACL 和作废。模态再多也是检索，不是靠模型自觉。
