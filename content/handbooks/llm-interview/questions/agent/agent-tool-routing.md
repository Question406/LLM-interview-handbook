---
id: agent-tool-routing
section: agent
order: 4
level: S
title: 有 1000 个 Tools，如何做 Tool Routing？
quick: >-
  多阶段路由：cheap lexical/embedding/classifier 先把 1000 收到几十，再用小模型或 reranker 选
  top-k，最后主模型按 task state 决定调不调。最终指标必须看下游成功，别只看 retrieval
  recall。
tags:
  - Tool Routing
  - Retrieval
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ToolLLM
    url: 'https://arxiv.org/abs/2307.16789'
    type: primary
---

一千个工具塞进主模型 context 既贵又吵：相近名字互相干扰，模型更容易「总要选一个」。路由是检索问题，不是把 OpenAPI 全糊进 prompt。错法：只报 Recall@K，不管下游是否调对、是否不该调。大规模工具集（ToolLLM 一类设定）已经说明：先检索再决策，比一次塞满 schema 更现实。

## 多阶段漏斗，最后一步允许不调

常见层级：先 namespace / 领域（calendar、code、finance、web、files）砍掉大类；再用 BM25 或 embedding 从描述里取 top-30；小模型或 reranker 看任务、对话状态和 schema 差异，收到 top-3～5；主模型在这小集合上决定是否调用、调哪个、参数是什么。最后一步必须保留 do-not-call / ask-user / no-tool，否则 router 有「工具总要选一个」的偏差。用户只是在闲聊或信息不足时，选任何一个都是错。

训练负例不能只随机抽。要加 semantic hard negative：名字像、能力边界不同（`search_email` vs `send_email`）。状态特征（已授权范围、已调用过的工具、缺的槽位）应进 router，纯 query-to-description 会在多轮里选错。工具描述应强调 capability 边界和 when-not-to-call，而不是同义词堆砌，否则检索更糊。见 `agent-schema-contract`。

## 指标看下游成功，不看检索虚荣

Recall@K 高仍可能差：top-k 混进危险或近义干扰工具，主模型误选率上升。要测 wrong-tool cost、任务成功率、token/延迟节省、以及 candidate 集合对主模型的干扰（加一个易混淆工具成功率掉多少）。产品上，漏召回一个只读搜索，往往轻于误召回一个付款接口。路由阈值应对高风险工具更严。

小模型 router（1B/2B）在工具多、调用频繁时值钱，但必须用 end-to-end success 验收；routing error 吃掉的成功率，可能大于省下的 token。Router 本身也是 harness 的一部分：声称模型变强时要冻结路由与候选宽度，见 `arl-model-harness-ablation`。

冷启动时先按命名空间人工切，再上 embedding；描述质量比再加一层大模型更值钱。高风险工具可以不进召回，只走显式意图 + 确认。监控按工具报：漏召回、误召回、以及「本不该调却调了」。目录涨到一千以后，最大的失败模式往往是近义工具互抢，而不是完全召不回。所以 hard negative 和 when-not-to-call，优先于把 recall 再刷高一个点。

## 追问

- **为什么 Recall@K 高还可能差？** 候选里混入语义近、权限更危险的工具，主模型误选率上升。Candidate quality 看的是干扰与风险，不是金工具是否进了 top-k。
- **Router 该不该是小模型？** 调用密、目录大时值得省主模型 token；必须用端到端成功率和误调高风险工具率验收。省下的 token 填不回一次错发邮件。
- **工具描述怎么写？** 强调 capability 边界和 when-not-to-call，少堆同义词。描述糊，检索再准也是近义互抢。见 `agent-schema-contract`。
- **高风险工具要进召回吗？** 可以不进默认召回，只走显式意图加确认，避免 top-k 里出现付款接口干扰主模型。
