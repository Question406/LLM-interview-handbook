---
id: drustz-46f2acb483e2bf060f
section: research
order: 173
level: A
title: >-
  ML 理论/推导考点（2026-05 Blind 多 lab 对比帖）：手写 MHA 是 table stakes、backprop 推导刷掉
  80%、log-sum-exp 是隐形过滤器
quick: >-
  supplemental-research-note · ML 理论/推导考点（2026-05 Blind 多 lab 对比帖）：手写 MHA 是
  table stakes、backprop 推导刷掉 80%、log-sum-exp 是隐形过滤器
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.teamblind.com/post/recent-ml-interview-loops-at-openai-anthropic-databricks-mercor-what-i-learned-xl3yizf4
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Blind 'Recent ML interview loops at OpenAI/Anthropic/Databricks/Mercor'（2026-05-03，Apple 员工发帖，面完 7 家）：(1) 手写 Transformer/MHA（不用库）已是所有 AI lab 的 table stakes；(2) backprop 推导（chain rule 落地、softmax+cross-entropy 梯度）淘汰约 80% 候选人，senior 也大量挂；(3) softmax 数值稳定性/log-sum-exp 是隐形筛子，会被要求实现并解释；(4) infra 向岗位要求 Megatron-LM 源码级理解（TP/PP/SP）、ZeRO、FlashAttention——'只读 paper 已经不够'；(5) quant firm 重 latency/确定性/统计，AI lab 重 scaling/分布式/模型行为。注：评论区质疑发帖人夹带私货（卖题），核心观察与其他来源一致可采信。PracHub 对应收录：'Implement Backprop for a Tiny Network'、'Derive Backpropagation for Matrix-Product Layers'、'Compute Matrix Prefix Products and Gradients'（N 个 D×D 矩阵的前缀积及其梯度）、'Explain KV cache in Transformer inference'。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.teamblind.com/post/recent-ml-interview-loops-at-openai-anthropic-databricks-mercor-what-i-learned-xl3yizf4)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
