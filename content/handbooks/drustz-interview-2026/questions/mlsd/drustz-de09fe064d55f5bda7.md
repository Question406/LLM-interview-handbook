---
id: drustz-de09fe064d55f5bda7
section: mlsd
order: 182
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  1. 面试官画像：三个关键词把题面收得很窄
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 1. 面试官画像：三个关键词把题面收得很窄
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md
    type: primary
---
## 1. 面试官画像：三个关键词把题面收得很窄

他自述的三件事，在 Exa 的产品里各有明确对应物：

| 他说的 | Exa 里的东西 | 一手来源 |
|---|---|---|
| **reranking** | 自研 reranker（"our own re-ranker"），在 Canon 里是 retrieval 之后的一个 node | [ZenML 访谈](https://www.zenml.io/llmops-database/building-a-search-engine-for-ai-agents-infrastructure-product-development-and-production-deployment)、[composing-a-search-engine](https://exa.ai/blog/composing-a-search-engine) |
| **snippet generation** | **Exa Highlights** —— 这是他领域里最独特、外部最少人准备的一块 | [highlights-for-agents](https://exa.ai/blog/highlights-for-agents)、[scaling-our-highlights-server](https://exa.ai/blog/scaling-our-highlights-server) |
| **model alignment** | 用 Dr. GRPO 训 search agent；以及 search 质量如何反过来决定 RL 的样本效率 | [rl-search-outcomes](https://exa.ai/blog/rl-search-outcomes) |
| （隐含）**production** | Canon DAG 编排、Instant 亚 200ms、exa-d 数据框架 | [exa-d](https://exa.ai/blog/exa-d)、[exa-instant](https://exa.ai/blog/exa-instant) |

**我的判断（推断，不要说成事实）**：
最可能的题是 **「设计 Exa 的 highlights / snippet 服务」** 或 **「给 agentic search 设计 reranking 这一层」**，
因为这两个是他本人在做的，他能判断你答得深不深。
第二梯队是「怎么训/评一个 web search 的 reranker」和「端到端设计一个 agentic search endpoint」。

**押注策略**：§3（highlights）和 §4（reranker）**必须能不看稿讲完**；§5、§6 能讲七成即可。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
