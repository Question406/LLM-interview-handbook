---
id: baichuan-query-rewrite-model-choice
section: agent
order: 112
level: A
title: 百川智能：Query 改写用了什么模型，为什么不用大模型？
quick: >-
  先把 rewrite 目标量化成检索或任务增益，别追求更像人。小模型通常在延迟、成本、稳定输出和私有部署上更合适。用
  router 把歧义、复杂多跳或低置信 query 升级给 LLM，再用 retrieval gain、p95 和失败率验证分流收益。
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

错法：编「我们用了某 7B」。原帖没给出项目模型名。rewrite 的目标是检索/任务增益，不是更像人；默认小模型，难例再升级 LLM。全量 LLM 改写会引入延迟、隐私和 query drift。接三路召回见 `baichuan-three-path-recall`，混合权重见 `ant-bm25-hybrid`。

## Rewrite 优化什么

角色是改善下游 retrieval / tool selection。因此比较：规则 + 同义表、轻量 seq2seq、embedding-aware rewrite、大模型。高 QPS、短 query、领域术语稳定时，小模型在毫秒级延迟、固定成本、私有部署和输出格式上取胜。大模型吃语义歧义、多轮上下文、复杂约束拆分。评的是 Recall@$k$ / nDCG、最终任务成功、rewrite faithful rate（没改掉关键 ID），不是改写文本的流畅度。

## 按输入特征路由

默认小模型或规则；检测到低置信、意图混杂、实体缺失或多跳时才升级 LLM。保留原 query 做 hybrid：改写路 + 原词路，避免把「合同编号写错一位」漂成语义近邻。线上同时看 p95、成本、空召回和用户再次改写率。凭「LLM 更聪明」换掉全量 rewrite，往往会把延迟和隐私问题引进检索层。

落地时把改写当可开关组件：A/B 看 retrieval gain 是否为正；负增益就回退。金融术语表应进小模型或规则，而不是每次让大模型自由发挥。

## 追问

- **为什么必须保留原 query？** 改写可能丢掉必须命中的专有名词。原词走 BM25，改写走稠密，融合后再 rerank。
- **faithful rate 怎么定义？** 关键实体、ID、否定词是否保留。改写后这些丢了就算失败，即使句子更通顺。
- **能用同一个大模型又改写又生成吗？** 可以，但检索路径会被生成延迟绑死。改写应是短、稳、可缓存的前段。
- **没有标注怎么训小模型？** 用检索增益做弱监督：改写后召回变好的 pair 当正例；再人工抽检 faithful。
