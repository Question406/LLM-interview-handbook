---
id: amazon-titan-embed
section: amazon
order: 13
level: A
title: Amazon：Titan embedding 怎么评（MTEB 坑、领域），和 RAG 是什么关系？
quick: >-
  MTEB 是八类任务的公开榜，没有一个模型全赢；RAG 只关心检索切片和你的语料，不关心 STS 平均分。Titan V2 公开可出 1024 /
  512 / 256 维，短维在检索上能保住大部分分数。索引和查询必须同一模型、同一维。领域要自己做金标，不要把英文维基榜当 Seller
  政策。
tags:
  - Amazon
  - Titan
  - Embeddings
  - RAG
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon Titan Text Embeddings models
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/titan-embedding-models.html
    type: primary
  - title: Amazon Titan Text Embeddings V2 now available in Amazon Bedrock
    url: https://aws.amazon.com/blogs/aws/amazon-titan-text-v2-now-available-in-amazon-bedrock-optimized-for-improving-rag/
    type: primary
  - title: "MTEB: Massive Text Embedding Benchmark"
    url: https://arxiv.org/abs/2210.07316
    type: primary
  - title: Titan Text Embeddings — AWS Responsible AI
    url: https://docs.aws.amazon.com/ai/responsible-ai/titan-text-embeddings/overview.html
    type: primary
---

RAG / Knowledge Bases 岗会把 embedding 问成「是不是 MTEB 第一」。Muennighoff 等人的 MTEB 论文核心结论正好相反：**没有一种嵌入方法在所有任务上称王**。STS 强不代表检索强。Titan V2 的公开卖点是 RAG：默认 1024 维，可选 512 / 256，AWS 写 512 维大约留住 99% 检索分、256 维大约 97%，用来换存储和延迟。生成侧怎么评见 `amazon-titan-eval`；本题只评向量。

## MTEB 能看什么，不能当门禁

MTEB 把分类、聚类、对分类、重排、检索、STS、摘要等任务放在一张表里。有用之处：防止你只在自己的 50 条相似度集上自嗨；看模型有没有明显短板（比如聚类崩）。不能当门禁的原因：

1. **任务不是你的任务。** RAG 要的是检索：nDCG@$k$、Recall@$k$、MRR。把八类分数平均，会让 STS 把检索的洞填平。论文里就举过 STS 强、检索弱的例子。
2. **测试集公开。** 榜上的题会进预训练爬取，分会虚高。2025 以后更要用领域私有集或更新的 retrieval 评测，不能靠 0.3 分榜差选模型。
3. **语言和领域。** 早期 MTEB 偏英文、偏通用网页。Seller 政策、ASIN 属性、工单缩写、多 marketplace 语言，分布都不一样。标识符 query 本来就该走词法，见 `amazon-kendra-hybrid`。
4. **实现细节。** 是否归一化、query 要不要指令前缀、截断长度、是否对文档和 query 用同一编码器。Titan V2 默认 `normalize=true`，文档写这对 RAG 合适。换模型时这些旋钮要锁死，否则你在比预处理。

AWS 自己的 responsible AI 卡也用 MTEB 讲稳健性，并单独报检索 nDCG@10。面试可以引用这张卡，但要马上补一句：这是通用检索，不是你的条款库。

## 和 RAG 的关系：embedding 只负责召回

向量模型 **不生成答案**。它把 query 和块打到同一空间，ANN 取邻居，生成模型再读这些块。所以：

- 索引侧用吞吐：Bedrock 对 embedding 常按 RPM 限流，语料用 batch，见 `amazon-batch-infer`。
- 查询侧用延迟：在线 `InvokeModel`，维数越短，ANN 越轻。512 维几乎够用就不要撑满 1024。
- **同一模型、同一维、同一归一化** 编库和查库。中途换 Titan V1 → V2 或 1024 → 256，必须全量重嵌。混用余弦空间是静默事故。
- 切块质量 > 再刷 1 个 MTEB 点。表格和条款边界切丢了，最好的 embedding 也救不回来，见 `amazon-bedrock-rag`。
- 生成幻觉不是 embedding 的锅，除非召回根本没拿到金标块。先看 Recall@$k$，再看忠实度。

领域评测我会做一份「应用 MTEB」：正例是该返回的条款 / 商品 / FAQ，负例是易混的过期条款和邻类目。报 Recall@5、nDCG@10，再切标识符 vs 语义 vs 多语言。冷启动目录没有行为信号时，embedding 更重要，见 `amazon-cold-start`、`amazon-two-tower`（双塔是另一套检索，别和 Titan 句向量混为一个塔）。

错法：只报 MTEB average；query 用指令型模型、文档用 Titan；用生成模型的 BLEU 证明 embedding 好；把 256 维当免费午餐却不在自己的集上复测那 97%。

```python
body = json.dumps({
    "inputText": query,
    "dimensions": 512,
    "normalize": True,
})
# 编库和查询同一 dimensions；换维即重索引
```

## 追问

- **为什么 V2 还提供 256 维？** 存储和 ANN 延迟。公开数字是通用检索上的保留比例；你的领域可能掉得更多，要自己画曲线。
- **二值化 embedding？** 卡上写二值加全精度 query 重排可留很高检索分。那是再一刀压缩，先把 float 维数选对。
- **MTEB 第一但 RAG 变差？** 很常见。切块、过滤、过期元数据、混合检索没了。先查召回切片，别先换更大生成模型。
- **要不要微调 Titan？** 文档写 V2 不支持微调。领域适配靠切块、混合检索、重排模型，或换可微调的嵌入方案。不要承诺「我们 LoRA 一下 Titan Embed」。
