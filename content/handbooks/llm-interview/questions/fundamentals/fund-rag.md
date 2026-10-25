---
id: fund-rag
section: fundamentals
order: 13
level: A
title: BM25、Dense Retrieval、Cross-Encoder Reranker 如何组合？
quick: "通常是 hybrid 召回加精排：BM25 擅长匹配专有名词、ID 等精确词项，dense retrieval 能找到语义相近但措辞不同的文档，两路融合做召回，再用成本更高的 cross-encoder 联合编码 query 和 document，对候选精排。"
tags:
  - RAG
  - Retrieval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Dense Passage Retrieval for Open-Domain Question Answering
    url: https://arxiv.org/abs/2004.04906
    type: primary
  - title: Passage Re-ranking with BERT
    url: https://arxiv.org/abs/1901.04085
    type: secondary
---

工业上的默认组合是 hybrid 召回加贵模型精排：BM25 保住专有名词、ID 和原文片段，dense 保住同义改写，两路融合出候选，cross-encoder 只给这几十到几百个候选重新排序。三选一站队，或者让 cross-encoder 去扫全库，都不对路。

举个例子，用户贴了一个订单号来问，dense 向量很可能找不到这串字符，BM25 一下就能命中；可用户换个说法问「东西一直没收到怎么办」，文档里写的是「物流异常」，这时就得靠 dense。两路都召回之后，cross-encoder 再把 query 和每个候选放在一起细看，决定谁排第一。

## 三路各自在算什么

BM25 是词项匹配加文档长度归一，对稀有的精确字符串很强，对 paraphrase 弱。Dense / bi-encoder 把 query 和文档分开编码，文档向量可以预先算好，用内积或余弦加 ANN 从百万级文档里取 top-$K$，擅长字面不同、语义相近的情况。Cross-encoder 把每个 query-doc 对一起送进 Transformer，做 token 级 attention，准确，但文档侧没法预计算，复杂度随候选数线性涨，所以只用来 rerank 召回集。DPR 把双塔检索做成了可训练的召回器，BERT rerank 把交叉注意力放在了精排。

## 为什么是级联

第一阶段要从百万文档里快速取 top-$K$，必须能预计算或走倒排。第二阶段用 $O(K)$ 次昂贵的 forward 换精度。Hybrid 防止专有名词被 dense 漏掉，也补上 BM25 对同义句的漏召。融合可以用分数加权、RRF，或者学一个浅层学习器。起步用 RRF 或固定加权就行，再按 query 类型扫权重：含 ID、错误码、专有名词的偏 BM25，口语改写偏 dense；学权重需要有标注的 query-doc，见 `ant-bm25-hybrid`、`jd-hybrid-retrieval-weight`。ANN 索引（`fund-ann`）只加速 dense 的第一阶段，「三路如何组合」的逻辑不受它影响。

Rerank 的 $K$ 由延迟预算反推：cross-encoder 一次 forward 的成本乘 $K$ 必须落在 SLA 内，所以常见 $K\in[20,100]$，很少会到 $K=1000$。$K$ 太小，正确证据根本进不了精排；$K$ 太大，噪声文档和延迟一起涨。

常见的失败有三种：只用 dense，订单号、错误码检索失败；cross-encoder 直接打全库，延迟爆炸；chunk 切坏了，BM25 和 dense 都看不到完整证据，这时先修切块和重叠（`fund-chunking`），再谈融合。

## 怎么评

评测要拆开：召回用 Recall@$k$ / nDCG，金标是证据文档；精排用更小 $k$ 上的 nDCG；生成看忠实度和任务成功。端到端只看一个分数，会把「检索挂了」和「生成胡编」混在一起，因为检索对了，生成照样可能胡编。生成侧要不要微调是另一题（`fund-rag-ft`）：检索没拿到证据，微调生成也补不回事实。回答时说清每个阶段怎么在计算成本和准确率之间取舍：BM25 保精确词项，dense 补语义召回，cross-encoder 改善排序，生成受证据约束。

## 追问

**为什么不把 cross-encoder 当召回？**
没法为每个 query 扫全库，它也没有独立的文档向量可以建索引。

**Hybrid 一定要学权重吗？**
不一定。起步用 RRF 或固定加权就行，有标注再按 query 类型扫，见 `ant-bm25-hybrid`。

**召回很高，答案为什么还是错？**
可能是生成没受证据约束，也可能是 rerank 把对的证据挤出了窗口。要把指标拆开看。

**BM25 对中文怎么用？**
先分词，或者用字 / n-gram 建倒排。原理还是稀疏词项匹配，和 dense 互补的关系不变。

**只做 dense 行不行？**
小语料、几乎全是同义改写时可以试；线上有订单号、报错码、人名时，几乎必须 hybrid。
