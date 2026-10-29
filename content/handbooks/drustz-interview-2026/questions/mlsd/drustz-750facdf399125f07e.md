---
id: drustz-750facdf399125f07e
section: mlsd
order: 41
level: A
title: 06 · Search / Retrieval Post-training：Exa 类 AI Web Search · 十六、延伸阅读（按面试价值排序）
quick: >-
  作者文档章节 · 06 · Search / Retrieval Post-training：Exa 类 AI Web Search ·
  十六、延伸阅读（按面试价值排序）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md
    type: primary
---
## 十六、延伸阅读（按面试价值排序）

1. [Exa Research](https://exa.ai/research)：Exa 自己训练、嵌入并服务 web-scale search index/model 的研究入口。
2. [Exa Search API](https://exa.ai/docs/reference/search) 与 [Agent API](https://exa.ai/docs/reference/agent-api/overview)：截至 2026-07 的官方产品边界；区分单次 search/content 与异步多步 research agent。
3. [Exa: web-scale vector database](https://exa.ai/blog/building-web-scale-vector-db)：Matryoshka embeddings、binary quantization 与 web-scale serving trade-off。
4. [Exa Highlights](https://exa.ai/blog/highlights-for-agents)：excerpt selection 如何在 agentic search 中同时影响 token cost 与 grounding quality。
5. [WebGPT](https://arxiv.org/abs/2112.09332)：browser demonstrations、behavior cloning、human preference/reward model 与引用。
6. [Search-R1](https://arxiv.org/abs/2503.09516)：reasoning/search interleaved RL、outcome reward 与 retrieved-token masking。
7. [MMSearch-R1](https://arxiv.org/abs/2506.20670)：search-required/search-free mixture、search penalty 与 multimodal multi-turn search。
8. [Unbiased Learning-to-Rank with Biased Feedback](https://www.ijcai.org/proceedings/2018/738)：position bias、counterfactual learning 与 propensity weighting。
9. [BEIR](https://arxiv.org/abs/2104.08663)：heterogeneous zero-shot retrieval benchmark 与 BM25/dense/rerank trade-off。
10. [ColBERT](https://arxiv.org/abs/2004.12832)：late interaction 的效果/成本位置。

阅读策略：先读 abstract、method diagram、data、objective、eval split、failure/ablation；面试不需要背论文数字，但必须能解释它解决的 construct 和代价。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/06_search_post_training.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/06_search_post_training.md)。作者整理资料；许可和第三方来源范围见阅读指南。
