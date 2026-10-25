---
id: baichuan-query-rewrite-model-choice
section: agent
order: 112
level: A
title: 百川智能：Query 改写用了什么模型，为什么不用大模型？
quick: "Query 改写先看能不能提高检索质量和任务成功率。小模型延迟和成本低、输出稳定、便于私有部署，所以默认用小模型或规则，用 router 把有歧义、需要多跳或难判断的 query 交给 LLM，再比较检索增益、p95 延迟和失败率，验证分流是否有效。"
tags:
  - Baichuan
  - RAG
  - Query Rewrite
  - Model Routing
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---
## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“query改写用了什么模型 为什么不用大模型”**

Query 改写默认用小模型或规则，只把有歧义、多跳、难判断的 query 路由给 LLM。改写的目标是检索和任务上的增益，改得更像人说话没有意义；小模型延迟和成本低、输出稳定、方便私有部署，全量用大模型改写会带来延迟、隐私和 query drift。原帖没给出项目用的模型名，面试时别编「我们用了某 7B」。

改写在链路里的角色是改善下游的 retrieval 和工具选择，所以候选方案要放在一起比：规则加同义表、轻量 seq2seq、embedding-aware rewrite、大模型。高 QPS、query 短、领域术语稳定时，小模型在毫秒级延迟、固定成本、私有部署和输出格式上都占优；大模型更适合处理语义歧义、多轮上下文和复杂约束拆分。评的是 Recall@$k$ / nDCG、最终任务成功，以及 rewrite faithful rate，也就是关键 ID 有没有被改掉，改写文本流不流畅不重要。

举个例子，用户输入「合同 HT-xxx 的违约条款」，大模型可能好心改成「这份合同里关于违约责任的规定」，编号没了，检索只找到语义相近的别的内容。所以要保留原 query 做 hybrid，改写走一路，原词走一路。路由规则是默认小模型或规则，检测到低置信、意图混杂、实体缺失或多跳时才升级 LLM。上线后同时看 p95、成本、空召回和用户再次改写率。只凭「LLM 更聪明」就换掉全量改写，往往会把延迟和隐私问题带进检索层。

落地时把改写做成可开关的组件，A/B 看 retrieval gain 是不是正的，负增益就回退。金融术语表放进小模型或规则里，别每次让大模型自由发挥。改写后接三路召回见 `baichuan-three-path-recall`，混合权重见 `ant-bm25-hybrid`。

## 追问

**为什么一定要保留原 query？**
改写可能丢掉必须命中的专有名词。原词走 BM25，改写走稠密，融合后再 rerank。

**faithful rate 怎么定义？**
看关键实体、ID、否定词有没有保留。丢了就算失败，哪怕句子更通顺。

**能不能用同一个大模型既改写又生成？**
可以，但检索路径会被生成延迟绑住。改写应该是短、稳、能缓存的前段。

**没有标注怎么训小模型？**
用检索增益做弱监督，改写后召回变好的 pair 当正例，再人工抽检 faithful。
