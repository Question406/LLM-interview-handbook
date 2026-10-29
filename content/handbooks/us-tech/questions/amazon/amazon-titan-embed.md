---
id: amazon-titan-embed
section: amazon
order: 13
level: A
title: Amazon：Titan embedding 怎么评（MTEB 坑、领域），和 RAG 是什么关系？
quick: >-
  Titan embedding 要用领域检索集评，重点看 Recall 和 nDCG，MTEB 总均分只作背景。V2 提供 1024 / 512 / 256
  维，需要用存储、延迟和本域检索损失做选择。编库与查询固定同一模型、维数和 normalization 规则，再检查切块与 RAG 的最终效果。
tags:
  - Amazon
  - Titan
  - Embeddings
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Amazon Titan Text Embeddings models
    url: >-
      https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
    type: primary
  - title: Amazon Titan Text Embeddings V2 now available in Amazon Bedrock
    url: >-
      https://aws.amazon.com/blogs/aws/amazon-titan-text-v2-now-available-in-amazon-bedrock-optimized-for-improving-rag/
    type: primary
  - title: 'MTEB: Massive Text Embedding Benchmark'
    url: 'https://arxiv.org/abs/2210.07316'
    type: primary
  - title: Titan Text Embeddings — AWS Responsible AI
    url: >-
      https://docs.aws.amazon.com/ai/responsible-ai/titan-text-embeddings/overview.html
    type: primary
---

Titan embedding 要先看它能否把应用所需的条款或商品找回来，再参考 MTEB。比如 STS 相似度得分很高，却把过期条款排在有效条款前面，RAG 仍然会失败。Muennighoff 等人的 MTEB 论文也说明，没有一种嵌入方法在所有任务上都赢。

Titan V2 默认 1024 维，可选 512 / 256。AWS 报告 512 维保留约 99% 检索分、256 维约 97%，可以节省存储和 ANN 时间；这些通用检索比例仍需在自己的语料复测。生成侧评测另见 `amazon-titan-eval`。

## 先把公开成绩转成应用测试

MTEB 覆盖分类、聚类、对分类、重排、检索、STS、摘要等八类任务，能帮助发现短板，也比自己仅有的 50 条相似度测试更广。但 RAG 更关心 nDCG@$k$、Recall@$k$ 和 MRR，把八类平均可能掩盖检索不足。AWS responsible AI 卡也单独给检索 nDCG@10，仍属于通用检索。

公开测试可能进入预训练爬取，2025 以后更应补领域私有集或更新的 retrieval 评测，0.3 分榜差未必有意义。早期 MTEB 偏英文通用网页，Seller 政策、ASIN 属性、工单缩写和多 marketplace 语言都可能换分布；标识符 query 仍需要词法路径，见 `amazon-kendra-hybrid`。

比较模型时固定 normalization、query 指令前缀、截断长度和编码器使用方式。Titan V2 默认 `normalize=true`，文档推荐用于 RAG。query 用别的指令模型、文档用 Titan，会破坏两端空间一致性。

领域集的正例是该返回的条款、商品或 FAQ，难负例可以是过期条款和相近类目。报告 Recall@5、nDCG@10，并切标识符、语义和多语言。冷启动目录没有行为信号时，embedding 更重要，见 `amazon-cold-start`、`amazon-two-tower`；商品双塔与 Titan 句向量仍是不同检索系统。

## 在 RAG 中检查召回这一段

Embedding 把 query 和文本块编码到同一空间，ANN 找邻居，生成模型才读取这些块作答。先看 Recall@$k$ 是否命中金标块，再看忠实度，可以分开检索失败与生成 hallucination。

编库偏 throughput，Bedrock embedding 常按 RPM 限流，可走 batch，见 `amazon-batch-infer`。在线 query 用 `InvokeModel`，维数短则 ANN 负担小，512 维足够时就不必坚持 1024。编库和查询要用同一模型、维数与 normalization；Titan V1 → V2 或 1024 → 256 都需要全量重嵌。

切块也影响上限。表格或 section boundaries 丢了，再提高 1 个 MTEB 点也找不回缺失信息，见 `amazon-bedrock-rag`。MTEB 第一但 RAG 变差时，先查切块、过滤、过期元数据和混合检索，再考虑生成模型。

```python
body = json.dumps(
    {
        "inputText": query,
        "dimensions": 512,
        "normalize": True,
    }
)
# 编库和查询同一 dimensions；换维即重索引
```

这段请求固定了 512 维并 normalization，编库端也要采用同一配置。生成模型的 BLEU 无法用来证明 embedding 质量。

## 追问

**256 维值得用吗？**
可以节约存储和 ANN 延迟，但要画本域的质量与维数曲线，复核公开的 97% 保留比例。

**还能二值化吗？**
模型卡提到二值表示加全精度 query 重排能保留较高检索分。这是另一层压缩，先验证 float 维数的选择。

**能微调 Titan V2 吗？**
所引文档写明 V2 不支持微调。领域适配可先用切块、混合检索、重排，或更换可微调嵌入方案，不能直接承诺对 Titan Embed 做 LoRA。
