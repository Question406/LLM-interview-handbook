---
id: msft-bing-rank
section: microsoft
order: 7
level: A
title: Microsoft：Bing / 搜索排序，LLM 重排和传统 LTR 怎么叠
quick: >-
  搜索是漏斗：召回百万、LTR 打到百、交叉编码器或 LLM 只看最顶尖。LambdaMART 一类仍扛位置偏差、新鲜度和权威性；LLM
  重排吃语义和意图，但校准差、贵、慢。不要用 LLM 替换整个索引。
tags:
  - Microsoft
  - Bing
  - Learning to Rank
  - LLM Rerank
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: From RankNet to LambdaRank to LambdaMART — An Overview
    url: https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/
    type: primary
  - title: Microsoft Learning to Rank Datasets
    url: https://www.microsoft.com/en-us/research/project/mslr/
    type: secondary
---

Bing / 搜索 / 广告排序岗不会让你从零发明检索。微软自己的家底是 RankNet → LambdaRank → LambdaMART：用梯度提升树优化 NDCG 这类 listwise 指标。LLM 进来之后，题变成 **漏斗哪一层换成大模型、哪一层绝不能换**。公开面经不一定有逐字题，但和「成本和延迟墙下的级联」口味一致。

## 漏斗：LLM 只能看顶尖

粗召回（BM25、双塔、倒排）面对的是亿级文档，单次打分必须是毫秒以下的点积或 term 统计。传统 LTR（GBDT / LambdaMART）吃的是几百个候选上的手工+统计特征：BM25、PageRank 类权威、新鲜度、点击、页面质量、匹配字段。这一层已经在优化「这个 query 下文档的相对序」，目标近似 NDCG，不是下一句 token。

交叉编码器（query 和文档拼接进 Transformer）比 GBDT 懂语义，但仍是专用排序模型，top 50-200 才用得起。生成式 LLM 重排再往上：prompt 里塞 query + 十条标题/摘要，让模型给出排列或分数。**十到五十条** 是现实数量级。对百万候选跑 GPT 是算力幻想，也打爆 Azure TPM（`msft-azure-tpm`）。

白板顺序我一定会画成：

1. 召回：$10^6$-$10^7$ → 几百。
2. LTR：$O(10^2)$ → 几十。特征可解释，freshness / spam / 权威在这里杀。
3. 可选神经网络交叉编码。
4. LLM 重排：只动 top $k$（比如 10-20），处理复杂意图、多文档比较、是否该显示生成摘要。

错法：「LLM 懂语言，把 LambdaMART 下了」。树模型在点击偏差、位置偏差、新鲜度上有二十年校准；LLM 分数和点击率不是单调对齐的，直接当最终序会把昨天的新闻压到旧百科下面，或把流畅的垃圾页排上去。

## 怎么叠：校准、特征、生成

三条叠法，面试要能选而不是全上：

- **LLM 当特征。** 离线或近线对 query-url 出相关性标签 / 嵌入，喂进 GBDT。线上仍是树，延迟可控，LLM 当教师。适合流量大、要稳。
- **LLM 当重排器。** 只在 top $k$ 调序。要校准：用验证点击或人工级把 LLM 分映射到和 LTR 同尺度，或混合 $\mathrm{final}=\alpha s_{\mathrm{ltr}}+(1-\alpha)s_{\mathrm{llm}}$。$\alpha$ 按 query 类型调：导航类（「facebook 登录」）树模型更稳；长尾自然语言 LLM 更有用。
- **LLM 当答案页。** 不只重排，还生成摘要，引用必须指向检索到的 url。这已经是 `msft-copilot-ground` 的搜索版：没有检索到的句子不能写。排序指标变成「引用可点击 + 满足」，NDCG 仍要，但不是唯一。

位置偏差：人只点第一条。LTR 用 propensity / 随机化曝光来学。LLM 重排若用有偏点击当标签，会强化已经排在前面的页。训练数据要和漏斗层级匹配：树用曝光日志，LLM 用顶层人工或弱监督，不要拿全库未点文档当负例硬训 GPT。

评测拆开：召回 recall@k、LTR NDCG@10、LLM 重排后的 NDCG 和副作用（新鲜度、权威站点是否被流畅文案挤掉）。线上还要看 p95。LLM 重排 200ms 可能吃掉整个预算，这时该缩 $k$ 或改成离线教师。

特征层我会点名几类，避免「GBDT 吃特征」太空：匹配（BM25、标题精确、锚文本）、质量（spam、页面结构）、权威（站点级、链接）、新鲜度（发布时间 × query 时效意图）、行为（点击、停留，要纠偏）。LLM 擅长改匹配和意图，不擅长偷偷替换权威和 spam 分。导航 query 上动 LLM 重排，风险是把官方登录页换成一篇写得更顺的博客。

级联还要打全每一层的候选集合日志，否则无法归因 NDCG 掉在召回、LTR 还是 LLM。成本上对 top $k=20$ 做一次 LLM 重排，QPS 一高就碰到 `msft-azure-tpm`，所以线上常见是「树模型出分 + 只对不确定的 query 开 LLM」。不确定可以用 LTR 分数熵、query 长度、或是否导航意图来门控。

校准时不要直接拿 LLM 的 1-5 分当最终序。先在验证集上看和点击 / 人工级的相关，再学一个单调映射或和 LTR 做加权。分数漂移（模型升级、prompt 一改）会让线上序垮掉，所以 LLM 层要当可开关的特征，而不是唯一排序器。

## 追问

- **为什么不端到端用 LLM 检索？** 索引规模和延迟不允许。生成式检索 / 记忆库是研究线，Bing 体量上倒排+向量召回仍是底座。
- **LambdaMART 的 lambda 是什么？** 把 NDCG 等 IR 指标的梯度推到 pairwise 上，让对指标影响大的序对权重大。不是随便一个 pairwise logistic。
- **多模态结果（图、视频、答案框）？** 仍是级联，只是特征不同。LLM 适合在答案框层做融合，不适合替换图像倒排。
- **和 Copilot 搜索的差别？** Copilot 多了 ACL 和租户索引；Bing 是开放 web、spam 和权威权重更大。重排哲学相同，权限模型不同。
