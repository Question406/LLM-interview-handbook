---
id: msft-bing-rank
section: microsoft
order: 7
level: A
title: Microsoft：Bing / 搜索排序，LLM 重排和传统 LTR 怎么叠
quick: >-
  保留倒排 / 双塔召回和传统 LTR，让交叉编码器或 LLM 只重排前几十条。LTR 综合点击、新鲜度、权威性等特征，LLM 补复杂意图与语义；两者分数先
  calibration，再按 query 类型融合。逐层记录候选，分别验证 NDCG、时效和 p95。
tags:
  - Microsoft
  - Bing
  - Learning to Rank
  - LLM Rerank
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: From RankNet to LambdaRank to LambdaMART — An Overview
    url: >-
      https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/
    type: primary
  - title: Microsoft Learning to Rank Datasets
    url: 'https://www.microsoft.com/en-us/research/project/mslr/'
    type: secondary
---

## 可以这样回答

我会把 LLM 放在检索漏斗的末端，或离线当教师，保留传统召回与 LTR。比如「facebook 登录」要找到官方入口，一篇写得流畅的博客不能因为 LLM 喜欢它就排到官网前面。LLM 理解语义的优势，需要与权威、新鲜度和行为信号一起使用。

粗召回用 BM25、双塔、倒排处理亿级文档，依赖毫秒以下的点积或 term 统计。白板上可以画 $10^6$-$10^7$ 到几百，再由 LTR 把 $O(10^2)$ 缩到几十。树模型使用 BM25、PageRank 类权威、新鲜度、点击、页面质量和匹配字段，学习 query 下的相对次序。

## 技术备查

我会把 LLM 放在检索漏斗的末端，或离线当教师，保留传统召回与 LTR。比如「facebook 登录」要找到官方入口，一篇写得流畅的博客不能因为 LLM 喜欢它就排到官网前面。LLM 理解语义的优势，需要与权威、新鲜度和行为信号一起使用。

## 先缩小候选，再用昂贵模型

公开技术线从 RankNet、LambdaRank 到 LambdaMART，用 GBDT 优化 NDCG 等排序指标。本卡据公开工作讨论级联。

粗召回用 BM25、双塔、倒排处理亿级文档，依赖毫秒以下的点积或 term 统计。白板上可以画 $10^6$-$10^7$ 到几百，再由 LTR 把 $O(10^2)$ 缩到几十。树模型使用 BM25、PageRank 类权威、新鲜度、点击、页面质量和匹配字段，学习 query 下的相对次序。

交叉编码器把 query 和文档拼接，通常只处理 top 50-200；生成式 LLM 再比较十到五十条标题 / 摘要，实际可只动 top $k$，如 10-20，处理复杂意图、多文档比较和生成摘要选择。对百万候选调用 GPT 会超出延迟与 `msft-azure-tpm` 配额。

树模型长期处理点击、位置、新鲜度等信号，LLM 分数与点击率并不天然单调。直接替换可能把旧百科压过昨天新闻，或抬高流畅垃圾页，因此要分别验证这些副作用。

## 按流量和预算选择叠法

流量大、延迟紧时，可离线 / 近线让 LLM 对 query-url 产相关性标签或嵌入，作为 GBDT 特征，线上仍运行树。需要在线理解时，只对 top $k$ 重排，用验证点击或人工等级 calibration 到 LTR 尺度，也可混合 $\mathrm{final}=\alpha s_{\mathrm{ltr}}+(1-\alpha)s_{\mathrm{llm}}$。$\alpha$ 按 query 类型调，导航类 query 可提高传统排序权重，长尾自然语言更多利用 LLM。

生成答案页是另一层：摘要的引用必须指向实际检索 url，不能加入证据外论断，见 `msft-copilot-ground`。这时还要评引用可点击和用户满足度，NDCG 保留但不能覆盖全部质量。

点击有 position bias，LTR 可以用 propensity / 随机化曝光纠偏；LLM 若直接学习有偏点击，也会继续抬高原来靠前页面。树使用曝光日志，LLM 使用顶层人工或弱监督，别把全库未点文档都当负例。

特征要具体到匹配（BM25、标题精确、锚文本）、质量（spam、页面结构）、权威（站点与链接）、新鲜度（发布时间与 query 时效意图）、纠偏后的行为（点击、停留）。LLM 可改进匹配与意图判断，其他信号仍需验证。每层候选都留日志，才能定位 NDCG 掉在召回、LTR 还是 LLM。

离线分别看 recall@k、LTR NDCG@10、LLM 后 NDCG，以及新鲜度和权威站点变化，线上看 p95。额外 200ms 已用满预算时，缩 $k$ 或转离线教师。top $k=20$ 在高 QPS 下也可能撞 TPM，可以用 LTR 分数熵、query 长度、导航意图 gating，只对不确定请求开 LLM。

calibration 要用验证集学单调映射或加权，不能直接把 1-5 分作为最终序。模型或 prompt 改动会造成漂移，因此 LLM 层应可开关。

## 追问

**为什么不端到端让 LLM 检索？**
Bing 规模下要满足索引和延迟约束，倒排与向量仍是底座，生成式检索是另一个研究方向。

**LambdaMART 的 lambda 是什么？**
将 NDCG 等 IR 指标的变化传到 pairwise 梯度，让影响指标更大的序对获得更高权重。

**图、视频、答案框怎么处理？**
继续级联，使用各自特征。LLM 可以在答案框层融合，不适合替换图像倒排。

**与 Copilot 搜索有何不同？**
Copilot 多租户索引和 ACL，Bing 面向开放 web，更关注 spam 与权威；重排思路可复用，权限模型不同。
