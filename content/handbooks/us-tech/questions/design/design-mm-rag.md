---
id: design-mm-rag
section: design
order: 21
level: A
title: 设计：多模态 RAG——图向量、文本与 ACL
quick: >-
  图和文字进同一问答，权限仍走元数据过滤，不能靠「模型别看无权限像素」。索引至少两路：文本块 + 图像
  / 页级向量，查询侧按模态选塔再融合。引用要指回页和区域，新鲜度与作废和文本 RAG 同一纪律。
tags:
  - RAG
  - Multimodal
  - Google
  - Amazon
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Learning Transferable Visual Models From Natural Language Supervision
    url: https://arxiv.org/abs/2103.00020
    type: primary
  - title: ColPali — Efficient Document Retrieval with Vision Language Models
    url: https://arxiv.org/abs/2407.01449
    type: primary
  - title: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
    url: https://arxiv.org/abs/2005.11401
    type: primary
---

Google 企业搜、Amazon Bedrock 知识库、Meta 工作问答一旦接截屏和 PDF 扫描件，就会从 `design-prod-rag` 追到「图怎么索引、权限怎么漏」。CLIP 给图文对齐向量；ColPali 一类把页当视觉文档检索。不是某次现场逐字题。生成侧引用框见 `design-mm-assistant`。本题收检索层：双路索引、ACL、融合、泄漏。

## 切片仍先于 embedding，像素也有租户

我会先问：PDF 是原生文字还是扫描、要不要区域引用、租户 / ACL、更新频率、p95。扫描件没有好文字时，纯 BM25 会瞎。但仍按文档结构切：页、图、表，元数据绑 `doc_id`、页码、`bbox`、生效/作废、`acl_groups`。存在性泄漏同样算事故：无权限用户不该靠「图像检索有结果 vs 空」探测合同在不在。

索引建议三路，按预算裁：

1. **文本。** OCR / 原生文字 + BM25 + dense。表格保留表头副本。
2. **图级 CLIP / SigLIP。** 查询是「红色 logo 的那页」时，文字塔对不上。
3. **页级视觉检索（ColPali 一类）。** 版式、印章、手写，OCR 丢的信号在这里。

过滤必须在 ANN 之前或走支持预过滤的引擎：`acl ∩ 未作废 ∩ 语言`，**再**向量。把无权限页的像素打进上下文，再靠 prompt「请忽略」，等于已经泄漏。缩略图、缓存 CDN、日志里的图 URL 都要过同一 ACL。

```python
def mm_retrieve(q, user, q_image=None):
    f = {"acl": acl_groups(user), "expired": False}
    text_hits = hybrid_search(q, filters=f, k=50)
    vis_hits = image_search(q_image or text_tower(q), filters=f, k=50)
    return rrf(text_hits, vis_hits)[:20]
```

embedding 升级双写，按 `doc_id` 切流。图模型和文本模型版本都要钉在报告里，混排不可比。

## 融合、引用、token

融合用倒数排名（RRF）即可，权重用标注集扫，不要口头保证「视觉一定赢关键词」。查询带图时（以图搜页）走图像塔；纯文字走文本塔 + 用文字塔查图向量（CLIP 的对齐空间）。搜到页之后，生成不要整页高清塞进上下文：先 OCR 摘要 + 低分辨率，引用框再裁高清作物，见 `design-mm-assistant`。一页图可以是几千 visual token，会把对话历史挤爆。

引用：`doc_id` + 页 + `bbox`。对不上就删句。过期页用元数据挡，不要指望向量「自己过期」。图更新（换了合同扫描件）要按版本作废旧向量，和文本同一套。

失败模式：OCR 把印章日期读错，生成信了 OCR 而没看图；视觉检索命中相似但不该看的租户水印页——若 ACL 漏了就是事故；把用户上传的截屏写进共享索引；审核没扫图就进库，有害图当知识，见 `align-mm-harm`、`design-moderation`。p95 拆：OCR、三路检索、重排、生成。视觉超时当该模态缺失，不许拿过期缓存图当本页。

企业场景 Amazon / Google 还会问：同一 `doc_id` 的图和文字权限必须一致；图更「好看」不能成为绕过 ACL 的理由。评测集要含：纯文能答、必须看图、图文冲突、无权限探测、扫描件无 OCR。不要用 BLEU。

## 追问

- **只有 CLIP 够不够？** 图搜图、粗召回够用；版式密集的文档页往往要页级视觉检索或强 OCR。
- **为什么不把每页只存一个向量？** 区域引用和表格局部对不上。页向量召回，框在生成或二次定位。
- **用户图当查询会不会进别人的索引？** 查询图默认不入库。要入库必须走同一 ACL 和留存期。
- **和文本 RAG 哪条绝对不能省？** 预过滤 ACL 和作废。模态再多也是检索，不是靠模型自觉。
