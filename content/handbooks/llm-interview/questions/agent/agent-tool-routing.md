---
id: agent-tool-routing
section: agent
order: 4
level: S
title: 有 1000 个 Tools，如何做 Tool Routing？
quick: >-
  分阶段把工具缩小：先按命名空间砍大类，再用 BM25 或 embedding 取几十个候选，小模型或 reranker
  收到三到五个，主模型在小集合上决定调不调、调哪个，并保留不调用的出口。验收看端到端任务成功率和误调率，相关工具被检索到只是第一步。
tags:
  - Tool Routing
  - Retrieval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ToolLLM
    url: 'https://arxiv.org/abs/2307.16789'
    type: primary
---

一千个工具我会用多阶段漏斗来路由，最后一步一定允许「不调」。全塞进主模型上下文，成本高，名字相近的工具还会互相干扰，模型容易勉强挑一个。ToolLLM 一类大规模工具集的设定也说明，先检索再决策，比一次塞满字段和类型规范（schema）现实得多。

漏斗大概这样走。先按命名空间或领域砍掉大类，比如 calendar、code、finance、web、files；再用 BM25 或 embedding 在描述里取 top-30；然后小模型或 reranker 看任务、对话状态和 schema 差异，收到 top-3～5；最后主模型在这个小集合上决定要不要调、调哪个、参数怎么填。这一步必须保留 do-not-call、ask-user、no-tool 这些出口，否则 router 会带着「总得选一个」的偏差，用户只是在闲聊或者信息不够时，选哪个都是错。

router 的训练有两点要讲。负例要加容易混淆的工具，名字相近、capability limits 不同，比如 `search_email` 和 `send_email`。状态特征也要进 router，已授权范围、已经调过的工具、还缺的槽位，纯 query 对描述的匹配在多轮里会选错。工具描述本身要写 capability scope 和 when-not-to-call，堆同义词只会让检索更糊，见 `agent-schema-contract`。

指标我会看下游。只报 Recall@K，不管下游有没有调对、该不该调，是最常见的误区。要测 wrong-tool cost、任务成功率、token 和延迟省了多少，以及候选集对主模型的干扰，比如多放一个易混淆工具成功率掉多少。产品上，漏召回一个只读搜索，往往比误召回一个付款接口轻得多，所以高风险工具的路由阈值要更严。

工程上，冷启动先按命名空间人工切，再上 embedding，把描述写好比再加一层大模型更值钱。Router 也是 harness 的一部分，声称模型变强时要冻结路由和候选宽度，见 `arl-model-harness-ablation`。上线后按工具报漏召回、误召回和「本不该调却调了」。目录涨到一千以后，最常见的失败是近义工具互抢，完全召不回的情况少得多，所以 hard negative 和 when-not-to-call 比把 recall 再刷高一个点更优先。

## 追问

**为什么 Recall@K 高还可能差？**
候选里混进了语义相近、权限更危险的工具，主模型误选率会上升。候选质量要看干扰和风险，金工具进了 top-k 只说明了一半。

**Router 该用小模型吗？**
调用密、目录大时值得，小模型 router（1B/2B）能省主模型的 token。但必须用端到端成功率和高风险工具误调率验收，routing error 吃掉的成功率可能比省下的 token 更多，省下的 token 也抵不过一次发错的邮件。

**高风险工具要进召回吗？**
可以不进默认召回，只走显式意图加确认，免得付款接口出现在 top-k 里干扰主模型。
